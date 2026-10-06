# Namma Jothidam

A personal Vedic astrology birth chart (jathakam) calculator, with an English/Tamil toggle.

- **Birth details**: place-name search (Open-Meteo geocoding) fills in latitude, longitude and
  time zone; 12-hour time picker.
- **Charts**: South Indian style rasi chart (D1) with retrograde marking and Gulika/Mandi placed
  in the grid, plus divisional charts D2, D3, D7, D9, D10, D12 and D60.
- **Under the chart**: Indu Lagna, Pranapada, Tithi/Thithi Soonyam, Mudakku Rasi, Upasana
  Deivam and Kaala Pakai each sit in a collapsed box; click a title to open it.
- **Special lagnas**: Indu Lagna and Pranapada Lagna.
- **Tithi and Thithi Soonyam**: birth tithi, its void (soonya) rasis with their lords, houses
  and occupants, hatched in the D1 grid.
- **Mudakku Rasi**: from the Sun's nakshatra pada, with its rasi and star lords, house and
  occupants, tagged in the D1 grid; flags when it is the lagna, which is said to weaken it.
- **Graha details**: rasi and nakshatra lords, absolute and in-sign degrees, a Pushkara
  Navamsa column naming the pada (and whether it is vargottama), and a Kaala Pakai column with a
  summary line above the table.
- **Kaala Pakai**: grahas sitting in their Kaala Pakai rasi in the D1 chart, with the rasi,
  house and effect; a planet picker shows any graha's Kaala Pakai rasis.
- **Ucham / Neecham**: planets in exaltation or debilitation, with distance from the deep
  exaltation/debilitation degree.
- **Dasa**: Vimshottari dasa down to Prana level, with the current period highlighted.
- **Tara Balam** from the birth star.
- **Yogas and doshas**: Mangal Dosha, Gaja Kesari, Budhaditya, Chandra-Mangal, Kemadruma
  (simplified), Soorya Chandraadhi, Jeevanam (naming the planets that show the source of
  earnings) and the five Pancha Mahapurusha yogas, each marked Present or Not present.
- **Upasana Deivam**: the 11th rasi from Jupiter (for a man) or Venus (for a woman), with its
  temple and deity; any other rasi can be looked up too.
- **Moorthy (Moorthi Nirnayam)**: every rasi change of Saturn, Jupiter and Rahu/Ketu from
  2026 to 2031 (plus the one already running on 1 Jan 2026), with the date and time, the Moon's
  rasi then and the Moorthi (Swarna, Rajatha, Thamira or Loha) counted from the janma rasi;
  the running transits are highlighted, and the table can be filtered by planet.
- **Drekkana Lords Aathipathyam**: for all nine planets, the drekkana lord (controller) picked
  by the planet's degree, where it sits, and whether it is 6th or 8th from the planet, which
  weakens the planet; when any planet is weakened, the pariharam (Vakkarakali Amman) is shown.
- **Navamsa Sashtashtagam**: each of the nine planets' D9 rasi counted from its D1 rasi; a planet
  6th or 8th is flagged with the houses it rules in D1 (its aathipathyam) and what they stand for,
  plus the Vakkarakali Amman pariharam, and every period from 2026 to 2031 when the planet in
  transit is in the nakshatra pada of its navamsa position, when the issue is said to show. None
  flagged is a huge plus in the jathakam.
- **Reading**: side-nav pages explaining the method, tables and sources for Pushkara Navamsa,
  Pancha Mahapurusha yogas, Ucham/Neecham, Pranapada, Thithi Soonyam, Mudakku, Soorya Chandraadhi
  Yoga, Jeevanam Yoga, Kaala Pakai, Moorthi Nirnayam, Drekkana Lords Aathipathyam
  and Navamsa Sashtashtagam.
- **Pariharam**: a tab at the top, next to the language picker, with its own side nav of
  pariharams that do not need a chart. The first, Richness and Selvam, lists seven names from the
  Lalitha Sahasranamam given by Maha Periyavar, each in English and Tamil together. More are
  added to `PARIHARAMS` in `static/labels.js` and appear in the side nav.
- **Prasannam**: a tab at the top that casts the chart for this moment where you are (the
  browser's location, or a place you type if location is not allowed), draws it, and gives the
  Chandra Nadi: the Moon's star, pada, exact degree and the rasi it is crossing. Nothing is saved.
- **Saved charts**: stored locally, recomputed on load, and deletable.

## Setup

Requires Python 3.11 (pyswisseph has no prebuilt wheel for newer Python versions yet).

```bash
brew install python@3.11
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Without Homebrew, [uv](https://docs.astral.sh/uv/) can fetch Python 3.11 into your home directory:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

### Ephemeris data

Download the Swiss Ephemeris files into `ephe/` (one-time, ~1.8MB, not committed to git):

```bash
curl -sfL -o ephe/sepl_18.se1 https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/sepl_18.se1
curl -sfL -o ephe/semo_18.se1 https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/semo_18.se1
```

## Run

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in a browser.

## Test

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## Notes

- Ayanamsa: Lahiri. Node: Mean Node (not True Node).
- Houses: whole-sign, from the lagna.
- Gulika is cast from the start of Saturn's day/night segment and Mandi from its middle;
  both are shown because traditions differ on which to use.
- Pranapada uses the BPHS method: Sun + ishta kala from sunrise, plus a correction for the
  Sun's sign type (movable +0°, dual +120°, fixed +240°).
- Thithi Soonyam uses the South Indian panchanga table, the same for both pakshas; sources
  cite no classical text for it.
- Mudakku counts padas from the Sun's pada to the same pada of Moolam, then the same again
  from there; the landing pada's rasi is the Mudakku rasi. Some versions count whole stars from
  Pooradam instead.
- Upasana Deivam: the rasi-to-temple/deity list is the author's own, not from a published
  source. Charts with gender "Other" get no computed rasi; the lookup still works.
- Classical cancellation conditions (for example, Neecha Bhanga and Mangal Dosha
  cancellations) are not modeled. Each yoga's description in the app says what is checked.
- Tara Balam is computed from the birth star only (not two-person compatibility).
- Data is stored locally in `jathakam.db` (SQLite), gitignored.
- Kaala Pakai: the planet-to-rasi table and its effects come from a video, not a written
  source. D1 only, and the whole rasi counts regardless of degree. Ketu has no Kaala Pakai rasi.
  The table is kept in both `app/constants.py` and `static/labels.js`, so change both together.
- Soorya Chandraadhi Yoga: the Sun's house from the lagna (lagna = 1), counted that many rasis
  from Mesha (Mesha = 1), must hold the Moon. D1 only; the rule is the author's own, with no
  written source.
- Jeevanam Yoga: the Moon's rasi numbered from Mesha (Mesha = 1) gives a house count from the
  lagna; any of the nine grahas there, the Moon included, forms the yoga and shows the source of
  earnings. Always present for a Mesha lagna. D1 only; the author's own rule.
- Moorthi Nirnayam follows [Astroshala's Moorti Nirnaya article](https://astroshala.com/moorti-nirnaya-a-traditional-and-authentic-approach-to-check-planetary-transit-results/):
  count from the janma rasi to the Moon's rasi at the moment of each peyarchi (1/6/11 Swarna,
  2/5/9 Rajatha, 3/7/10 Thamira, 4/8/12 Loha). Peyarchi times come from the Swiss Ephemeris with
  Lahiri ayanamsa and the mean node (Thirukanitha); Vakya panchangam dates can differ. A retrograde
  slip back into the previous rasi, and the re-entry after it, are listed with their own Moorthi.
  The window is set by `PEYARCHI_START_YEAR` and `PEYARCHI_END_YEAR` in `app/constants.py`.
- Drekkana Lords Aathipathyam: up to 10° the controller is the planet's rasi lord, over 10° up to 20° the
  5th rasi's lord, over 20° the 9th rasi's lord (degrees to the hundredth, so exactly 10° and
  20° stay in the earlier drekkana, unlike the usual convention and the app's D3 chart). A
  controller 6th or 8th from the planet weakens it. All nine planets are checked; Rahu and Ketu are
  never controllers, as they rule no rasi. The author's own rule.
- Navamsa Sashtashtagam: counted from each planet's D1 rasi (= 1) to its D9 rasi; 6th or 8th is
  flagged. The house meanings shown are a common short list, not from a single source. Rahu and
  Ketu rule no house, so the house they sit in is shown instead. The author's own rule.
  The timing point is the pada holding the planet's navamsa longitude (its longitude times 9),
  e.g. a Sun at Dhanus 5°35' has its navamsa at Rishabam 20°18', Rohini pada 4; the transit
  periods are found with the Swiss Ephemeris and include each retrograde pass separately.
- Pushkara Navamsa follows Dr. N. G. Kumaran, "Pushkara Navamsa", IJATET 8(1), 2023: 24 of the
  108 padas, two per rasi (fire signs the 7th and 9th navamsa, earth the 3rd and 5th, air the 6th
  and 8th, water the 1st and 3rd). The stars of the Sun and Jupiter hold 6 each; Venus, Saturn,
  the Moon and Rahu 3 each; Mars, Mercury and Ketu none. The paper's table prints Uttara
  Phalguni 3 and Uttara Bhadrapada 3; its own rule gives 4 and 2, which the app uses.
