from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.astrology import (
    ChartData,
    VARGA_FUNCTIONS,
    build_chart,
    build_varga_chart,
    compute_indu_lagna,
    longitude_to_rasi,
    make_graha_position,
)
from app.constants import PEYARCHI_END_YEAR, PEYARCHI_START_YEAR, RASI_LORDS
from app.dasa import compute_mahadasas, compute_sub_periods
from app.db import SavedChart, delete_chart, get_chart, init_db, list_charts, save_chart
from app.dignity import compute_dignities
from app.drekkana_lords import compute_drekkana_lords
from app.ephemeris import (
    compute_ascendant,
    compute_graha_positions,
    init_ephemeris,
    jd_from_datetime,
    to_julian_day_ut,
)
from app.geocode import search_places
from app.models import (
    BirthRequest,
    ChartOut,
    ChartResponse,
    ChartSummary,
    DasaExpandRequest,
    DasaPeriodOut,
    DignityOut,
    DrekkanaLordOut,
    GrahaOut,
    KaalaPakaiOut,
    MudakkuOut,
    PeyarchiOut,
    PrasannamResponse,
    PlaceResult,
    SashtashtagamOut,
    SoonyaRasiOut,
    TaraEntryOut,
    TithiOut,
    TransitWindowOut,
    UpasanaOut,
    YogaOut,
)
from app.kaala_pakai import compute_kaala_pakai
from app.mudakku import compute_mudakku
from app.navamsa_sashtashtagam import compute_navamsa_sashtashtagam
from app.peyarchi import compute_peyarchis
from app.pranapada import compute_pranapada_longitude
from app.tara import compute_tara_balam
from app.tithi import compute_tithi
from app.timezone_utils import compute_utc_offset
from app.upasana import compute_upasana
from app.upagraha import compute_gulika_longitude, compute_mandi_longitude
from app.yogas import detect_all_yogas

app = FastAPI(title="Namma Jothidam")


@app.on_event("startup")
def startup() -> None:
    init_ephemeris()
    init_db()


@app.middleware("http")
async def no_cache_static_files(request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/api"):
        # Forces the browser to revalidate (ETag/Last-Modified) instead of silently
        # reusing a stale cached copy of index.html/chart.js/labels.js/style.css.
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _to_chart_out(chart: ChartData) -> ChartOut:
    return ChartOut(
        lagna_rasi=chart.lagna_rasi,
        grahas={name: GrahaOut(**vars(g)) for name, g in chart.grahas.items()},
        houses=chart.houses,
    )


@app.get("/api/geocode", response_model=list[PlaceResult])
async def geocode(query: str) -> list[PlaceResult]:
    if len(query.strip()) < 2:
        return []
    results = await search_places(query)
    return [PlaceResult(**r) for r in results]


def _build_chart_response(
    chart_id: int, name: str, gender: str, dob, tob, pob_label: str, latitude: float, longitude: float, timezone: str
) -> ChartResponse:
    """Everything shown for a chart, computed from birth details alone. Saved charts
    are recomputed on load (not read back from stored results), so they always
    include every feature added since they were saved."""
    utc_offset = compute_utc_offset(timezone, dob, tob)
    jd_ut = to_julian_day_ut(dob, tob, utc_offset)
    graha_positions = compute_graha_positions(jd_ut)
    graha_longitudes = {n: lon for n, (lon, _speed) in graha_positions.items()}
    graha_speeds = {n: speed for n, (_lon, speed) in graha_positions.items()}
    lagna_longitude = compute_ascendant(jd_ut, latitude, longitude)

    d1 = build_chart(lagna_longitude, graha_longitudes, graha_speeds)
    vargas = {
        varga: build_varga_chart(varga, lagna_longitude, graha_longitudes, graha_speeds)
        for varga in VARGA_FUNCTIONS
    }

    gulika_longitude = compute_gulika_longitude(dob, tob, utc_offset, latitude, longitude)
    gulika = make_graha_position("Gulika", gulika_longitude, longitude_to_rasi(gulika_longitude), d1.lagna_rasi)
    mandi_longitude = compute_mandi_longitude(dob, tob, utc_offset, latitude, longitude)
    mandi = make_graha_position("Mandi", mandi_longitude, longitude_to_rasi(mandi_longitude), d1.lagna_rasi)

    pranapada_longitude = compute_pranapada_longitude(
        dob, tob, utc_offset, latitude, longitude, graha_longitudes["Sun"]
    )
    pranapada = make_graha_position(
        "Pranapada", pranapada_longitude, longitude_to_rasi(pranapada_longitude), d1.lagna_rasi
    )

    indu_lagna_rasi = compute_indu_lagna(d1.lagna_rasi, d1.grahas["Moon"].rasi)
    mahadasas = compute_mahadasas(datetime.combine(dob, tob), graha_longitudes["Moon"])
    tara_entries = compute_tara_balam(d1.grahas["Moon"].nakshatra)
    tithi = compute_tithi(d1)
    mudakku = compute_mudakku(d1)
    upasana = compute_upasana(d1, gender)

    return ChartResponse(
        id=chart_id,
        name=name,
        gender=gender,
        dob=dob,
        tob=tob,
        pob_label=pob_label,
        d1=_to_chart_out(d1),
        vargas={varga: _to_chart_out(c) for varga, c in vargas.items()},
        gulika=GrahaOut(**vars(gulika)),
        mandi=GrahaOut(**vars(mandi)),
        indu_lagna_rasi=indu_lagna_rasi,
        indu_lagna_lord=RASI_LORDS[indu_lagna_rasi],
        mahadasas=[DasaPeriodOut(lord=p.lord, start=p.start, end=p.end, level=p.level) for p in mahadasas],
        tara_balam=[
            TaraEntryOut(nakshatra=e.nakshatra, count=e.count, category=e.category, quality=e.quality)
            for e in tara_entries
        ],
        yogas=[
            YogaOut(name=y.name, description=y.description, triggered=y.triggered, from_moon=y.from_moon)
            for y in detect_all_yogas(d1)
        ],
        dignities=[DignityOut(**vars(e)) for e in compute_dignities(d1)],
        pranapada=GrahaOut(**vars(pranapada)),
        tithi=TithiOut(
            number=tithi.number,
            paksha=tithi.paksha,
            paksha_tithi=tithi.paksha_tithi,
            progress=tithi.progress,
            soonya_rasis=[SoonyaRasiOut(**vars(r)) for r in tithi.soonya_rasis],
        ),
        mudakku=MudakkuOut(**vars(mudakku)),
        upasana=UpasanaOut(**vars(upasana)) if upasana else None,
        kaala_pakai=[KaalaPakaiOut(**vars(e)) for e in compute_kaala_pakai(d1)],
        peyarchis=_peyarchis_out(d1.grahas["Moon"].rasi, timezone),
        drekkana_lords=[DrekkanaLordOut(**vars(e)) for e in compute_drekkana_lords(d1)],
        navamsa_sashtashtagam=_sashtashtagam_out(d1, vargas["D9"], timezone),
    )


def _transit_window(timezone_name: str) -> tuple[datetime, datetime]:
    """The years the Moorthy and Sashtashtagam timings cover, in the chart's time zone."""
    tz = ZoneInfo(timezone_name)
    return datetime(PEYARCHI_START_YEAR, 1, 1, tzinfo=tz), datetime(PEYARCHI_END_YEAR + 1, 1, 1, tzinfo=tz)


def _sashtashtagam_out(d1: ChartData, d9: ChartData, timezone_name: str) -> list[SashtashtagamOut]:
    tz = ZoneInfo(timezone_name)
    out = []
    for e in compute_navamsa_sashtashtagam(d1, d9, *_transit_window(timezone_name)):
        fields = {**vars(e), "point": vars(e.point) if e.point else None}
        fields["transits"] = [TransitWindowOut(start=w.start.astimezone(tz), end=w.end.astimezone(tz)) for w in e.transits]
        out.append(SashtashtagamOut(**fields))
    return out


def _peyarchis_out(janma_rasi: int, timezone_name: str) -> list[PeyarchiOut]:
    tz = ZoneInfo(timezone_name)
    start, end = _transit_window(timezone_name)
    return [
        PeyarchiOut(**{**vars(e), "when": e.when.astimezone(tz)})
        for e in compute_peyarchis(janma_rasi, start, end)
    ]


@app.post("/api/chart", response_model=ChartResponse)
async def create_chart(req: BirthRequest) -> ChartResponse:
    # Call Navamsha Cloud API for live Kundali calculation
    payload = build_navamsha_payload(req.dob, req.tob, req.latitude, req.longitude, req.timezone)
    try:
        await call_navamsha_api("/api/v1/kundali/basic", payload)
    except Exception as exc:
        print(f"Navamsha API call: {exc}")

    response = _build_chart_response(
        0, req.name, req.gender, req.dob, req.tob, req.pob_label, req.latitude, req.longitude, req.timezone
    )
    record = save_chart(
        SavedChart(
            name=req.name,
            gender=req.gender,
            dob=req.dob,
            tob=req.tob,
            pob_label=req.pob_label,
            latitude=req.latitude,
            longitude=req.longitude,
            tz_name=req.timezone,
            utc_offset=compute_utc_offset(req.timezone, req.dob, req.tob),
            chart_json="{}",  # results are recomputed on load; kept only because the column is required
        )
    )
    response.id = record.id
    return response


@app.get("/api/charts", response_model=list[ChartSummary])
def get_charts() -> list[ChartSummary]:
    return [ChartSummary(id=c.id, name=c.name, dob=c.dob, created_at=c.created_at) for c in list_charts()]


@app.get("/api/charts/{chart_id}", response_model=ChartResponse)
def get_chart_by_id(chart_id: int) -> ChartResponse:
    record = get_chart(chart_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Chart not found")
    return _build_chart_response(
        record.id, record.name, record.gender, record.dob, record.tob, record.pob_label,
        record.latitude, record.longitude, record.tz_name,
    )


@app.delete("/api/charts/{chart_id}", status_code=204)
def remove_chart(chart_id: int) -> None:
    if not delete_chart(chart_id):
        raise HTTPException(status_code=404, detail="Chart not found")


@app.get("/api/prasannam", response_model=PrasannamResponse)
def prasannam(latitude: float, longitude: float, timezone: str, at: datetime | None = None) -> PrasannamResponse:
    """The chart for this moment (or `at`, used by tests) at the given place. Not saved."""
    try:
        tz = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=400, detail="Unknown time zone")
    when = datetime.now(tz) if at is None else (at if at.tzinfo else at.replace(tzinfo=tz)).astimezone(tz)
    jd_ut = jd_from_datetime(when)
    positions = compute_graha_positions(jd_ut)
    lagna_longitude = compute_ascendant(jd_ut, latitude, longitude)
    d1 = build_chart(
        lagna_longitude,
        {n: lon for n, (lon, _speed) in positions.items()},
        {n: speed for n, (_lon, speed) in positions.items()},
    )
    return PrasannamResponse(
        when=when.replace(microsecond=0),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        lagna_longitude=lagna_longitude,
        d1=_to_chart_out(d1),
    )


@app.post("/api/dasa/expand", response_model=list[DasaPeriodOut])
def expand_dasa(req: DasaExpandRequest) -> list[DasaPeriodOut]:
    children = compute_sub_periods(req.lord, req.start, req.end, req.next_level)
    return [DasaPeriodOut(lord=p.lord, start=p.start, end=p.end, level=p.level) for p in children]


from app.navamsha import build_navamsha_payload, call_navamsha_api


@app.post("/api/navamsha/kundali")
async def navamsha_kundali(req: BirthRequest, detailed: bool = False):
    """Fetch Kundali chart (basic or complete) from Navamsha API."""
    payload = build_navamsha_payload(req.dob, req.tob, req.latitude, req.longitude, req.timezone)
    endpoint = "/api/v1/kundali/complete" if detailed else "/api/v1/kundali/basic"
    return await call_navamsha_api(endpoint, payload)


@app.post("/api/navamsha/birth-details")
async def navamsha_birth_details(req: BirthRequest):
    """Fetch astrological birth details (Nakshatra, Tithi, Yoga, Karana) from Navamsha API."""
    payload = build_navamsha_payload(req.dob, req.tob, req.latitude, req.longitude, req.timezone)
    return await call_navamsha_api("/api/v1/astrology/birth-details", payload)


@app.post("/api/navamsha/chart-svg/{chart_type}")
async def navamsha_chart_svg(chart_type: str, req: BirthRequest):
    """Fetch rendered SVG chart graphic code (e.g. d1, d9, d10, etc.) from Navamsha API."""
    chart_key = chart_type.lower().strip()
    payload = build_navamsha_payload(req.dob, req.tob, req.latitude, req.longitude, req.timezone)
    endpoint = f"/api/v1/{chart_key}-chart-svg-code"
    return await call_navamsha_api(endpoint, payload)


@app.post("/api/navamsha/dasha")
async def navamsha_dasha_periods(req: BirthRequest):
    """Fetch Vimshottari Dasha periods from Navamsha API."""
    payload = build_navamsha_payload(req.dob, req.tob, req.latitude, req.longitude, req.timezone)
    return await call_navamsha_api("/api/v1/astrology/dasha-periods", payload)


@app.post("/api/navamsha/panchang")
async def navamsha_panchang(req: BirthRequest):
    """Fetch Panchang details for the birth moment from Navamsha API."""
    payload = build_navamsha_payload(req.dob, req.tob, req.latitude, req.longitude, req.timezone)
    return await call_navamsha_api("/api/v1/astrology/panchang", payload)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
