const DASA_LEVEL_ORDER = ["mahadasa", "antardasa", "antaram", "sookshma", "prana"];

const GRID_POSITIONS = [
  { rasi: 11, row: 1, col: 1 }, { rasi: 0, row: 1, col: 2 }, { rasi: 1, row: 1, col: 3 }, { rasi: 2, row: 1, col: 4 },
  { rasi: 10, row: 2, col: 1 }, { rasi: 3, row: 2, col: 4 },
  { rasi: 9, row: 3, col: 1 }, { rasi: 4, row: 3, col: 4 },
  { rasi: 8, row: 4, col: 1 }, { rasi: 7, row: 4, col: 2 }, { rasi: 6, row: 4, col: 3 }, { rasi: 5, row: 4, col: 4 },
];

// Rahu/Ketu (nodes) are essentially always retrograde by nature (Mean Node),
// so marking them "(R)" would be noise, not information — classical charts
// only mark it for the 5 planets where it's a noteworthy, temporary state.
const NODES_NOT_MARKED_RETROGRADE = new Set(["Rahu", "Ketu"]);
const UPAGRAHA_NAMES = new Set(["Gulika", "Mandi"]);
// Inauspicious combinations: shown in a warning colour when present, not the green used for yogas.
const INAUSPICIOUS_YOGAS = new Set(["Mangal Dosha", "Kemadruma Yoga (simplified)"]);

let state = {
  lang: "en",
  chart: null,
  varga: "D1",
  selectedPlace: null, // { label, latitude, longitude, timezone }
  readingTopic: "pushkaraNavamsa",
  upasanaRasi: "", // rasi index picked in the Upasana Deivam box, as a string
  kaalaPakaiPlanet: "", // planet picked in the Kaala Pakai box
  pariharamTopic: 0, // index into PARIHARAMS shown on the Pariharam page
  prasannam: { place: null, chart: null }, // place: { latitude, longitude, timezone, label }; label null = device location
  peyarchiPlanet: "", // planet filter on the Peyarchi tab; "" = all
};

function L() {
  return LABELS[state.lang];
}

function nextDasaLevel(level) {
  const idx = DASA_LEVEL_ORDER.indexOf(level);
  return idx >= 0 && idx < DASA_LEVEL_ORDER.length - 1 ? DASA_LEVEL_ORDER[idx + 1] : null;
}

function fmtDate(iso) {
  return iso.slice(0, 10);
}

function formatDMS(deg) {
  let d = Math.floor(deg);
  let mFull = (deg - d) * 60;
  let m = Math.floor(mFull);
  let s = Math.round((mFull - m) * 60);
  if (s === 60) { s = 0; m += 1; }
  if (m === 60) { m = 0; d += 1; }
  return `${d}°${String(m).padStart(2, "0")}'${String(s).padStart(2, "0")}"`;
}

function readTob24Hour() {
  const hour12 = parseInt(document.getElementById("tobHour").value, 10);
  const minute = parseInt(document.getElementById("tobMinute").value, 10);
  const ampm = document.getElementById("tobAmPm").value;
  let hour24 = hour12 % 12;
  if (ampm === "PM") hour24 += 12;
  return `${String(hour24).padStart(2, "0")}:${String(minute).padStart(2, "0")}:00`;
}

function populateTobMinutes() {
  const select = document.getElementById("tobMinute");
  for (let m = 0; m < 60; m++) {
    const opt = document.createElement("option");
    opt.value = String(m);
    opt.textContent = String(m).padStart(2, "0");
    select.appendChild(opt);
  }
}

// --- Language ---

function applyLanguage() {
  const labels = L();
  document.getElementById("pageTitle").textContent = labels.ui.title;
  document.getElementById("pageTagline").textContent = labels.ui.tagline;
  document.getElementById("lblFormTitle").textContent = labels.ui.newChart;
  document.getElementById("lblName").textContent = labels.ui.name;
  document.getElementById("lblGender").textContent = labels.ui.gender;
  document.getElementById("optMale").textContent = labels.ui.male;
  document.getElementById("optFemale").textContent = labels.ui.female;
  document.getElementById("optOther").textContent = labels.ui.other;
  document.getElementById("lblDob").textContent = labels.ui.dob;
  document.getElementById("lblTob").textContent = labels.ui.tob;
  document.getElementById("lblPob").textContent = labels.ui.pob;
  document.getElementById("pob").placeholder = labels.ui.pobPlaceholder;
  document.getElementById("btnCalculate").textContent = labels.ui.calculate;
  document.getElementById("lblSavedCharts").textContent = labels.ui.savedCharts;
  document.getElementById("lblChartTab").textContent = labels.ui.chartTab;
  document.getElementById("lblDasaTab").textContent = labels.ui.dasaTab;
  document.getElementById("lblYogaTab").textContent = labels.ui.yogaTab;
  document.getElementById("lblTaraTab").textContent = labels.ui.taraTab;
  document.getElementById("lblDetailsTab").textContent = labels.ui.detailsTab;
  document.getElementById("thPlanet").textContent = labels.ui.colPlanet;
  document.getElementById("thRasi").textContent = labels.ui.colRasi;
  document.getElementById("thRasiLord").textContent = labels.ui.colRasiLord;
  document.getElementById("thAbsDeg").textContent = labels.ui.colAbsDeg;
  document.getElementById("thDegInSign").textContent = labels.ui.colDegInSign;
  document.getElementById("thStar").textContent = labels.ui.colStar;
  document.getElementById("thPada").textContent = labels.ui.colPada;
  document.getElementById("thStarLord").textContent = labels.ui.colStarLord;
  document.getElementById("thPushkara").textContent = labels.ui.colPushkara;
  document.getElementById("lblPranapada").textContent = labels.ui.pranapada;
  document.getElementById("pranapadaHint").textContent = labels.ui.pranapadaHint;
  document.getElementById("lblDignityTab").textContent = labels.ui.dignityTab;
  document.getElementById("thDgPlanet").textContent = labels.ui.colPlanet;
  document.getElementById("thDgState").textContent = labels.ui.colState;
  document.getElementById("thDgRasi").textContent = labels.ui.colRasi;
  document.getElementById("thDgDeg").textContent = labels.ui.colDegInSign;
  document.getElementById("thDgDeep").textContent = labels.ui.colDeep;
  document.getElementById("thDgDist").textContent = labels.ui.colDistance;
  document.getElementById("dignityNote").textContent = labels.ui.dignityNote;
  document.getElementById("lblInduLagna").textContent = labels.ui.induLagna;
  document.getElementById("lblTithi").textContent = labels.ui.tithi;
  document.getElementById("lblTithiBox").textContent = labels.ui.tithiBox;
  document.getElementById("lblSoonyam").textContent = labels.ui.soonyam;
  document.getElementById("soonyamHint").textContent = labels.ui.soonyamHint;
  document.getElementById("soonyamLegendText").textContent = labels.ui.soonyamLegend;
  document.getElementById("lblMudakku").textContent = labels.ui.mudakku;
  document.getElementById("mudakkuHint").textContent = labels.ui.mudakkuHint;
  document.getElementById("lblUpasana").textContent = labels.ui.upasana;
  document.getElementById("lblUpasanaRasi").textContent = labels.ui.colRasi;
  document.getElementById("lblKaalaPakai").textContent = labels.ui.kaalaPakai;
  document.getElementById("lblKaalaPakaiPlanet").textContent = labels.ui.colPlanet;
  document.getElementById("kaalaPakaiHint").textContent = labels.ui.kaalaPakaiHint;
  document.getElementById("thKaalaPakai").textContent = labels.ui.colKaalaPakai;
  document.getElementById("lblPeyarchiTab").textContent = labels.ui.peyarchiTab;
  document.getElementById("lblPeyarchiFilter").textContent = labels.ui.colPlanet;
  document.getElementById("thPyPlanet").textContent = labels.ui.colPlanet;
  document.getElementById("thPyEnters").textContent = labels.ui.colEnters;
  document.getElementById("thPyWhen").textContent = labels.ui.colWhen;
  document.getElementById("thPyMoon").textContent = labels.ui.colMoonThen;
  document.getElementById("thPyCount").textContent = labels.ui.colCount;
  document.getElementById("thPyMoorthi").textContent = labels.ui.colMoorthi;
  document.getElementById("lblDrekkanaTab").textContent = labels.ui.drekkanaTab;
  document.getElementById("thDkPlanet").textContent = labels.ui.colPlanet;
  document.getElementById("thDkRasi").textContent = labels.ui.colRasi;
  document.getElementById("thDkDeg").textContent = labels.ui.colDegInSign;
  document.getElementById("thDkDrekkana").textContent = labels.ui.colDrekkana;
  document.getElementById("thDkController").textContent = labels.ui.colController;
  document.getElementById("thDkControllerIn").textContent = labels.ui.colControllerIn;
  document.getElementById("thDkCount").textContent = labels.ui.colFromPlanet;
  document.getElementById("thDkResult").textContent = labels.ui.colResult;
  document.getElementById("drekkanaNote").textContent = labels.ui.drekkanaNote;
  document.getElementById("lblSashtashtagamTab").textContent = labels.ui.sashtashtagamTab;
  document.getElementById("thSsPlanet").textContent = labels.ui.colPlanet;
  document.getElementById("thSsD1Rasi").textContent = labels.ui.colD1Rasi;
  document.getElementById("thSsD1House").textContent = labels.ui.colD1House;
  document.getElementById("thSsD9Rasi").textContent = labels.ui.colD9Rasi;
  document.getElementById("thSsCount").textContent = labels.ui.colCount;
  document.getElementById("thSsRules").textContent = labels.ui.colAathipathyam;
  document.getElementById("thSsResult").textContent = labels.ui.colResult;
  document.getElementById("sashtashtagamNote").textContent = labels.ui.sashtashtagamNote;
  document.getElementById("induLagnaHint").textContent = labels.ui.induLagnaHint;
  document.getElementById("lblReading").textContent = labels.ui.reading;
  document.getElementById("lblBack").textContent = labels.ui.back;
  document.getElementById("lblTopHome").textContent = labels.ui.topHome;
  const topJathakam = document.getElementById("lblTopJathakam");
  if (topJathakam) topJathakam.textContent = labels.ui.topJathakam;
  document.getElementById("lblTopPariharam").textContent = labels.ui.topPariharam;
  document.getElementById("lblPariharamNav").textContent = labels.ui.topPariharam;
  if (!document.getElementById("pariharamSection").classList.contains("hidden")) renderPariharam();
  document.getElementById("lblTopPrasannam").textContent = labels.ui.topPrasannam;
  const topReading = document.getElementById("lblTopReading");
  if (topReading) topReading.textContent = labels.ui.topReading;
  document.getElementById("lblPrasannamTitle").textContent = labels.ui.topPrasannam;
  document.getElementById("lblPrasTime").textContent = labels.ui.prasTime;
  document.getElementById("lblPrasPlace").textContent = labels.ui.prasPlace;
  document.getElementById("prasNow").textContent = labels.ui.prasNow;
  document.getElementById("prasUseLocation").textContent = labels.ui.prasUseLocation;
  document.getElementById("prasChangePlace").textContent = labels.ui.prasChangePlace;
  document.getElementById("prasPlaceInput").placeholder = labels.ui.prasPlaceholder;
  document.getElementById("lblChandraNadi").textContent = labels.ui.chandraNadi;
  document.getElementById("thPrPlanet").textContent = labels.ui.colPlanet;
  document.getElementById("thPrRasi").textContent = labels.ui.colRasi;
  document.getElementById("thPrDeg").textContent = labels.ui.colDegInSign;
  document.getElementById("thPrStar").textContent = labels.ui.colStar;
  document.getElementById("thPrPada").textContent = labels.ui.colPada;
  if (state.prasannam.chart) renderPrasannam();
  document.querySelectorAll(".side-nav-topic").forEach((btn) => {
    btn.textContent = READING_TOPICS[btn.dataset.topic].title[state.lang];
  });
  if (!document.getElementById("readingSection").classList.contains("hidden")) {
    renderReadingPage(state.readingTopic);
  }

  const heroKicker = document.getElementById("heroKicker");
  if (heroKicker && labels.ui.heroKicker) heroKicker.textContent = labels.ui.heroKicker;
  const heroWelcome = document.getElementById("heroWelcome");
  if (heroWelcome && labels.ui.heroWelcome) heroWelcome.textContent = labels.ui.heroWelcome;
  const heroTitleWorld = document.getElementById("heroTitleWorld");
  if (heroTitleWorld && labels.ui.heroTitleWorld) heroTitleWorld.textContent = labels.ui.heroTitleWorld;
  const heroTitleAstrology = document.getElementById("heroTitleAstrology");
  if (heroTitleAstrology && labels.ui.heroTitleAstrology) heroTitleAstrology.textContent = labels.ui.heroTitleAstrology;
  const heroDesc = document.getElementById("heroDesc");
  if (heroDesc && labels.ui.heroDesc) heroDesc.textContent = labels.ui.heroDesc;

  const c1t = document.getElementById("lblCard1Title"); if (c1t && labels.ui.heroCard1Title) c1t.textContent = labels.ui.heroCard1Title;
  const c1a = document.getElementById("lblCard1Action"); if (c1a && labels.ui.heroCard1Action) c1a.textContent = labels.ui.heroCard1Action;
  const c2t = document.getElementById("lblCard2Title"); if (c2t && labels.ui.heroCard2Title) c2t.textContent = labels.ui.heroCard2Title;
  const c2a = document.getElementById("lblCard2Action"); if (c2a && labels.ui.heroCard2Action) c2a.textContent = labels.ui.heroCard2Action;
  const c3t = document.getElementById("lblCard3Title"); if (c3t && labels.ui.heroCard3Title) c3t.textContent = labels.ui.heroCard3Title;
  const c3a = document.getElementById("lblCard3Action"); if (c3a && labels.ui.heroCard3Action) c3a.textContent = labels.ui.heroCard3Action;
  const c4t = document.getElementById("lblCard4Title"); if (c4t && labels.ui.heroCard4Title) c4t.textContent = labels.ui.heroCard4Title;
  const c4a = document.getElementById("lblCard4Action"); if (c4a && labels.ui.heroCard4Action) c4a.textContent = labels.ui.heroCard4Action;

  const wwdTag = document.getElementById("lblWwdTag"); if (wwdTag && labels.ui.wwdTag) wwdTag.textContent = labels.ui.wwdTag;
  const wwdHeading = document.getElementById("lblWwdHeading"); if (wwdHeading && labels.ui.wwdHeading) wwdHeading.textContent = labels.ui.wwdHeading;
  const wwdDesc = document.getElementById("lblWwdDesc"); if (wwdDesc && labels.ui.wwdDesc) wwdDesc.textContent = labels.ui.wwdDesc;
  const wwdBtn = document.getElementById("lblWwdBtn"); if (wwdBtn && labels.ui.wwdBtn) wwdBtn.textContent = labels.ui.wwdBtn;

  const f1t = document.getElementById("lblWwdFeat1Title"); if (f1t && labels.ui.wwdFeat1Title) f1t.textContent = labels.ui.wwdFeat1Title;
  const f1d = document.getElementById("lblWwdFeat1Desc"); if (f1d && labels.ui.wwdFeat1Desc) f1d.textContent = labels.ui.wwdFeat1Desc;
  const f2t = document.getElementById("lblWwdFeat2Title"); if (f2t && labels.ui.wwdFeat2Title) f2t.textContent = labels.ui.wwdFeat2Title;
  const f2d = document.getElementById("lblWwdFeat2Desc"); if (f2d && labels.ui.wwdFeat2Desc) f2d.textContent = labels.ui.wwdFeat2Desc;
  const f3t = document.getElementById("lblWwdFeat3Title"); if (f3t && labels.ui.wwdFeat3Title) f3t.textContent = labels.ui.wwdFeat3Title;
  const f3d = document.getElementById("lblWwdFeat3Desc"); if (f3d && labels.ui.wwdFeat3Desc) f3d.textContent = labels.ui.wwdFeat3Desc;
  const f4t = document.getElementById("lblWwdFeat4Title"); if (f4t && labels.ui.wwdFeat4Title) f4t.textContent = labels.ui.wwdFeat4Title;
  const f4d = document.getElementById("lblWwdFeat4Desc"); if (f4d && labels.ui.wwdFeat4Desc) f4d.textContent = labels.ui.wwdFeat4Desc;

  const s1 = document.getElementById("lblWwdStat1"); if (s1 && labels.ui.wwdStat1) s1.textContent = labels.ui.wwdStat1;
  const s2 = document.getElementById("lblWwdStat2"); if (s2 && labels.ui.wwdStat2) s2.textContent = labels.ui.wwdStat2;
  const s3 = document.getElementById("lblWwdStat3"); if (s3 && labels.ui.wwdStat3) s3.textContent = labels.ui.wwdStat3;

  const mTag = document.getElementById("lblModTag"); if (mTag && labels.ui.modTag) mTag.textContent = labels.ui.modTag;
  const mHeading = document.getElementById("lblModHeading"); if (mHeading && labels.ui.modHeading) mHeading.textContent = labels.ui.modHeading;
  const mDesc = document.getElementById("lblModDesc"); if (mDesc && labels.ui.modDesc) mDesc.textContent = labels.ui.modDesc;

  const mChip1 = document.getElementById("lblModChip1"); if (mChip1 && labels.ui.modChip1) mChip1.textContent = labels.ui.modChip1;
  const mC1t = document.getElementById("lblModCard1Title"); if (mC1t && labels.ui.modCard1Title) mC1t.textContent = labels.ui.modCard1Title;
  const mC1d = document.getElementById("lblModCard1Desc"); if (mC1d && labels.ui.modCard1Desc) mC1d.textContent = labels.ui.modCard1Desc;
  const mC1a = document.getElementById("lblModCard1Action"); if (mC1a && labels.ui.modCard1Action) mC1a.textContent = labels.ui.modCard1Action;

  const mChip2 = document.getElementById("lblModChip2"); if (mChip2 && labels.ui.modChip2) mChip2.textContent = labels.ui.modChip2;
  const mC2t = document.getElementById("lblModCard2Title"); if (mC2t && labels.ui.modCard2Title) mC2t.textContent = labels.ui.modCard2Title;
  const mC2d = document.getElementById("lblModCard2Desc"); if (mC2d && labels.ui.modCard2Desc) mC2d.textContent = labels.ui.modCard2Desc;
  const mC2a = document.getElementById("lblModCard2Action"); if (mC2a && labels.ui.modCard2Action) mC2a.textContent = labels.ui.modCard2Action;

  const mChip3 = document.getElementById("lblModChip3"); if (mChip3 && labels.ui.modChip3) mChip3.textContent = labels.ui.modChip3;
  const mC3t = document.getElementById("lblModCard3Title"); if (mC3t && labels.ui.modCard3Title) mC3t.textContent = labels.ui.modCard3Title;
  const mC3d = document.getElementById("lblModCard3Desc"); if (mC3d && labels.ui.modCard3Desc) mC3d.textContent = labels.ui.modCard3Desc;
  const mC3a = document.getElementById("lblModCard3Action"); if (mC3a && labels.ui.modCard3Action) mC3a.textContent = labels.ui.modCard3Action;

  const mChip4 = document.getElementById("lblModChip4"); if (mChip4 && labels.ui.modChip4) mChip4.textContent = labels.ui.modChip4;
  const mC4t = document.getElementById("lblModCard4Title"); if (mC4t && labels.ui.modCard4Title) mC4t.textContent = labels.ui.modCard4Title;
  const mC4d = document.getElementById("lblModCard4Desc"); if (mC4d && labels.ui.modCard4Desc) mC4d.textContent = labels.ui.modCard4Desc;
  const mC4a = document.getElementById("lblModCard4Action"); if (mC4a && labels.ui.modCard4Action) mC4a.textContent = labels.ui.modCard4Action;

  const mChip5 = document.getElementById("lblModChip5"); if (mChip5 && labels.ui.modChip5) mChip5.textContent = labels.ui.modChip5;
  const mC5t = document.getElementById("lblModCard5Title"); if (mC5t && labels.ui.modCard5Title) mC5t.textContent = labels.ui.modCard5Title;
  const mC5d = document.getElementById("lblModCard5Desc"); if (mC5d && labels.ui.modCard5Desc) mC5d.textContent = labels.ui.modCard5Desc;
  const mC5a = document.getElementById("lblModCard5Action"); if (mC5a && labels.ui.modCard5Action) mC5a.textContent = labels.ui.modCard5Action;

  const mChip6 = document.getElementById("lblModChip6"); if (mChip6 && labels.ui.modChip6) mChip6.textContent = labels.ui.modChip6;
  const mC6t = document.getElementById("lblModCard6Title"); if (mC6t && labels.ui.modCard6Title) mC6t.textContent = labels.ui.modCard6Title;
  const mC6d = document.getElementById("lblModCard6Desc"); if (mC6d && labels.ui.modCard6Desc) mC6d.textContent = labels.ui.modCard6Desc;
  const mC6a = document.getElementById("lblModCard6Action"); if (mC6a && labels.ui.modCard6Action) mC6a.textContent = labels.ui.modCard6Action;

  renderSavedList(state.savedCharts || []);
  if (state.chart) renderAll();
}

// --- Saved charts ---

async function loadSavedCharts() {
  const res = await fetch("/api/charts");
  state.savedCharts = await res.json();
  renderSavedList(state.savedCharts);
}

function showLoading(text) {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    if (text) {
      const title = overlay.querySelector(".loading-title");
      if (title) title.textContent = text;
    }
    overlay.classList.remove("hidden");
  }
}

function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.classList.add("hidden");
}

function renderSavedList(list) {
  const ul = document.getElementById("savedList");
  ul.innerHTML = "";
  if (!list || list.length === 0) {
    const emptyLi = document.createElement("li");
    emptyLi.className = "saved-empty-msg";
    emptyLi.textContent = "No saved horoscopes yet. Calculate a chart above to save it.";
    ul.appendChild(emptyLi);
    return;
  }
  for (const c of list) {
    const li = document.createElement("li");
    li.className = "saved-chart-item";
    
    const initial = (c.name || "A").trim().charAt(0).toUpperCase();
    const avatar = document.createElement("div");
    avatar.className = "saved-avatar";
    avatar.textContent = initial;

    const info = document.createElement("div");
    info.className = "saved-info";
    const nameSpan = document.createElement("strong");
    nameSpan.className = "saved-name";
    nameSpan.textContent = c.name;
    const dateSpan = document.createElement("span");
    dateSpan.className = "saved-dob";
    dateSpan.textContent = `📅 ${c.dob}`;
    info.append(nameSpan, dateSpan);

    const actions = document.createElement("div");
    actions.className = "saved-actions";

    const btn = document.createElement("button");
    btn.className = "saved-load-btn";
    btn.innerHTML = `<span class="btn-icon">⚡</span> ${L().ui.loadChart}`;
    btn.onclick = () => loadChart(c.id);

    const del = document.createElement("button");
    del.className = "delete-btn";
    del.innerHTML = `✕`;
    del.title = L().ui.deleteChart;
    del.onclick = () => deleteSavedChart(c);

    actions.append(btn, del);
    li.append(avatar, info, actions);
    ul.appendChild(li);
  }
}

async function deleteSavedChart(c) {
  if (!window.confirm(`${c.name} \u2014 ${c.dob}\n\n${L().ui.deleteConfirm}`)) return;
  const res = await fetch(`/api/charts/${c.id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 404) {
    alert("Could not delete chart: " + (await res.text()));
    return;
  }
  if (state.chart && state.chart.id === c.id) {
    state.chart = null;
    document.getElementById("resultSection").classList.add("hidden");
  }
  await loadSavedCharts();
}

async function loadChart(id) {
  showLoading("Loading Chart...");
  try {
    const res = await fetch(`/api/charts/${id}`);
    if (!res.ok) throw new Error(await res.text());
    state.chart = await res.json();
    state.varga = "D1";
    state.upasanaRasi = state.chart.upasana ? String(state.chart.upasana.rasi) : "";
    state.kaalaPakaiPlanet = state.chart.kaala_pakai.length ? state.chart.kaala_pakai[0].planet : "";
    showPage("jathakam");
    renderAll();
    const resSection = document.getElementById("resultSection");
    if (resSection) resSection.scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    alert("Error loading chart: " + err.message);
  } finally {
    hideLoading();
  }
}

// --- Place of Birth search ---

let pobSearchTimer = null;

const pobInput = document.getElementById("pob");
const pobResultsEl = document.getElementById("pobResults");

pobInput.addEventListener("input", () => {
  state.selectedPlace = null; // typing invalidates any prior selection
  const query = pobInput.value.trim();
  clearTimeout(pobSearchTimer);
  if (query.length < 2) {
    pobResultsEl.classList.add("hidden");
    pobResultsEl.innerHTML = "";
    return;
  }
  pobSearchTimer = setTimeout(() => runPobSearch(query), 300);
});

document.addEventListener("click", (e) => {
  if (!e.target.closest(".pob-field")) {
    pobResultsEl.classList.add("hidden");
  }
});

async function runPobSearch(query) {
  const res = await fetch(`/api/geocode?query=${encodeURIComponent(query)}`);
  const places = await res.json();
  pobResultsEl.innerHTML = "";
  if (places.length === 0) {
    const li = document.createElement("li");
    li.className = "pob-no-results";
    li.textContent = L().ui.pobNoResults;
    pobResultsEl.appendChild(li);
  } else {
    for (const place of places) {
      const li = document.createElement("li");
      li.textContent = place.label;
      li.addEventListener("click", () => {
        state.selectedPlace = place;
        pobInput.value = place.label;
        pobResultsEl.classList.add("hidden");
      });
      pobResultsEl.appendChild(li);
    }
  }
  pobResultsEl.classList.remove("hidden");
}

// --- Form ---

document.getElementById("birthForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!state.selectedPlace) {
    alert(L().ui.pobSelectPrompt);
    return;
  }
  const btn = document.getElementById("btnCalculate");
  btn.disabled = true;
  showLoading("Calculating Chart...");
  try {
    const body = {
      name: document.getElementById("name").value,
      gender: document.getElementById("gender").value,
      dob: document.getElementById("dob").value,
      tob: readTob24Hour(),
      pob_label: state.selectedPlace.label,
      latitude: state.selectedPlace.latitude,
      longitude: state.selectedPlace.longitude,
      timezone: state.selectedPlace.timezone,
    };
    const res = await fetch("/api/chart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      alert("Error computing chart: " + (await res.text()));
      return;
    }
    state.chart = await res.json();
    state.varga = "D1";
    state.upasanaRasi = state.chart.upasana ? String(state.chart.upasana.rasi) : "";
    state.kaalaPakaiPlanet = state.chart.kaala_pakai.length ? state.chart.kaala_pakai[0].planet : "";
    showPage("jathakam");
    renderAll();
    loadSavedCharts();
    const resSection = document.getElementById("resultSection");
    if (resSection) resSection.scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    alert("Error computing chart: " + err.message);
  } finally {
    btn.disabled = false;
    hideLoading();
  }
});


document.getElementById("langToggle").addEventListener("change", (e) => {
  state.lang = e.target.value;
  applyLanguage();
});

// --- Reading / side nav ---
// The side nav is just a compact row list; clicking a row opens that topic as
// its own full-width page in the main content area, replacing the chart/form
// view (not squeezed into the narrow sidebar).

for (const key of Object.keys(READING_TOPICS)) {
  const li = document.createElement("li");
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "side-nav-topic";
  btn.dataset.topic = key;
  btn.addEventListener("click", () => {
    document.querySelectorAll(".side-nav-topic").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.readingTopic = key;
    showReadingPage(key);
  });
  li.appendChild(btn);
  document.getElementById("sideNavList").appendChild(li);
}

document.getElementById("readingBack").addEventListener("click", hideReadingPage);

function showReadingPage(topicKey) {
  state.readingTopic = topicKey;
  setTopTab("reading");
  for (const id of PAGE_SECTIONS) {
    const el = document.getElementById(id);
    if (el) el.classList.add("hidden");
  }
  document.getElementById("sideNav").classList.remove("hidden");
  document.getElementById("pariharamNav").classList.add("hidden");
  document.querySelectorAll(".side-nav-topic").forEach((b) => b.classList.toggle("active", b.dataset.topic === topicKey));
  document.getElementById("readingSection").classList.remove("hidden");
  renderReadingPage(topicKey);
}

function hideReadingPage() {
  showPage("home");
}

// --- Top tabs & Navigation ---

function setTopTab(page) {
  document.querySelectorAll(".top-tab").forEach((b) => b.classList.toggle("active", b.dataset.page === page));
}

document.querySelectorAll(".top-tab").forEach((btn) => {
  btn.addEventListener("click", () => showPage(btn.dataset.page));
});

const heroJathakamBtn = document.getElementById("heroJathakamBtn");
if (heroJathakamBtn) heroJathakamBtn.addEventListener("click", () => showPage("jathakam"));
const heroPrasBtn = document.getElementById("heroPrasBtn");
if (heroPrasBtn) heroPrasBtn.addEventListener("click", () => showPage("prasannam"));
const heroPariharamBtn = document.getElementById("heroPariharamBtn");
if (heroPariharamBtn) heroPariharamBtn.addEventListener("click", () => showPage("pariharam"));
const heroReadingBtn = document.getElementById("heroReadingBtn");
if (heroReadingBtn) heroReadingBtn.addEventListener("click", () => showPage("reading"));
const wwdGetStartedBtn = document.getElementById("wwdGetStartedBtn");
if (wwdGetStartedBtn) wwdGetStartedBtn.addEventListener("click", () => showPage("jathakam"));

const modCardVargas = document.getElementById("modCardVargas");
if (modCardVargas) modCardVargas.addEventListener("click", () => showPage("jathakam"));
const modCardDasas = document.getElementById("modCardDasas");
if (modCardDasas) modCardDasas.addEventListener("click", () => showPage("jathakam"));
const modCardYogas = document.getElementById("modCardYogas");
if (modCardYogas) modCardYogas.addEventListener("click", () => showPage("jathakam"));
const modCardPrasannam = document.getElementById("modCardPrasannam");
if (modCardPrasannam) modCardPrasannam.addEventListener("click", () => showPage("prasannam"));
const modCardBlocks = document.getElementById("modCardBlocks");
if (modCardBlocks) modCardBlocks.addEventListener("click", () => showPage("jathakam"));
const modCardPariharam = document.getElementById("modCardPariharam");
if (modCardPariharam) modCardPariharam.addEventListener("click", () => showPage("pariharam"));

// Footer navigation links
const footerLinkHome = document.getElementById("footerLinkHome");
if (footerLinkHome) footerLinkHome.addEventListener("click", () => { showPage("home"); window.scrollTo({ top: 0, behavior: "smooth" }); });
const footerLinkJathakam = document.getElementById("footerLinkJathakam");
if (footerLinkJathakam) footerLinkJathakam.addEventListener("click", () => showPage("jathakam"));
const footerLinkPrasannam = document.getElementById("footerLinkPrasannam");
if (footerLinkPrasannam) footerLinkPrasannam.addEventListener("click", () => showPage("prasannam"));
const footerLinkPariharam = document.getElementById("footerLinkPariharam");
if (footerLinkPariharam) footerLinkPariharam.addEventListener("click", () => showPage("pariharam"));
const footerLinkNavagraha = document.getElementById("footerLinkNavagraha");
if (footerLinkNavagraha) footerLinkNavagraha.addEventListener("click", () => {
  showPage("home");
  const el = document.getElementById("homeNavagrahaSection");
  if (el) el.scrollIntoView({ behavior: "smooth" });
});
const footerLinkRasi = document.getElementById("footerLinkRasi");
if (footerLinkRasi) footerLinkRasi.addEventListener("click", () => {
  showPage("home");
  const el = document.getElementById("homeRasiSection");
  if (el) el.scrollIntoView({ behavior: "smooth" });
});
const footerLinkDasa = document.getElementById("footerLinkDasa");
if (footerLinkDasa) footerLinkDasa.addEventListener("click", () => showPage("jathakam"));
const footerLinkSoonyam = document.getElementById("footerLinkSoonyam");
if (footerLinkSoonyam) footerLinkSoonyam.addEventListener("click", () => showPage("jathakam"));

const PAGE_SECTIONS = ["homeHeroSection", "homeWhatWeDoSection", "homeModulesSection", "homeNavagrahaSection", "homeRasiSection", "formSection", "savedSection", "resultSection", "readingSection", "pariharamSection", "prasannamSection"];

function showPage(page) {
  setTopTab(page);
  // Hide all sections initially
  for (const id of PAGE_SECTIONS) {
    const el = document.getElementById(id);
    if (el) el.classList.add("hidden");
  }
  document.querySelectorAll(".side-nav-topic").forEach((b) => b.classList.remove("active"));
  
  // App body visibility (hide on home page so there is zero gap before footer)
  const appBody = document.querySelector(".app-body");
  if (appBody) appBody.classList.toggle("hidden", page === "home");

  // Sidebar visibility
  document.getElementById("sideNav").classList.toggle("hidden", page !== "reading");
  document.getElementById("pariharamNav").classList.toggle("hidden", page !== "pariharam");

  if (page === "home") {
    const hero = document.getElementById("homeHeroSection");
    if (hero) hero.classList.remove("hidden");
    const wwd = document.getElementById("homeWhatWeDoSection");
    if (wwd) wwd.classList.remove("hidden");
    const mods = document.getElementById("homeModulesSection");
    if (mods) mods.classList.remove("hidden");
    const nava = document.getElementById("homeNavagrahaSection");
    if (nava) nava.classList.remove("hidden");
    const rasi = document.getElementById("homeRasiSection");
    if (rasi) rasi.classList.remove("hidden");
  } else if (page === "jathakam") {
    document.getElementById("formSection").classList.remove("hidden");
    document.getElementById("savedSection").classList.remove("hidden");
    if (state.chart) document.getElementById("resultSection").classList.remove("hidden");
  } else if (page === "pariharam") {
    document.getElementById("pariharamSection").classList.remove("hidden");
    renderPariharam();
  } else if (page === "prasannam") {
    document.getElementById("prasannamSection").classList.remove("hidden");
    startPrasannam();
  } else if (page === "reading") {
    document.getElementById("readingSection").classList.remove("hidden");
    renderReadingPage(state.readingTopic || "pushkaraNavamsa");
  }
}

// --- Sacred Navagrahas 4th Home Section Data & Logic ---
const NAVAGRAHA_DATA = {
  Sun: {
    key: "Sun",
    name: "Surya (The Sun)",
    sanskrit: "SURYA BHAGAVAN • ஆத்மகாரகன்",
    tagline: "Lord of Vitality, Soul (Atma), Father & Sovereign Power",
    avatar: "☀️",
    color: "#f59e0b",
    desc: "Surya represents divine consciousness, inner illumination, life force (Prana), willpower, and leadership. As the King of the celestial cabinet, Sun governs royal favor, authority, government recognition, courage, and core vitality.",
    rasi: "Leo (Simha)",
    exalt: "Aries (Mesha 10°)",
    debil: "Libra (Thulam 10°)",
    gem: "Ruby (மாணிக்கம்)",
    day: "Sunday (ஞாயிறு)",
    deity: "Lord Shiva / Agni",
    mantra: "ॐ ஹ்ராம் ஹ்ரீம் ஹ்ரௌம் ஸஹ சூர்யாய நமஹ ॥",
    cta: "Analyze Your Sun's House & Strength"
  },
  Moon: {
    key: "Moon",
    name: "Chandra (The Moon)",
    sanskrit: "CHANDRA BHAGAVAN • மனோகாரகன்",
    tagline: "Ruler of Mind, Emotions, Mother & Liquid Radiance",
    avatar: "🌙",
    color: "#60a5fa",
    desc: "Chandra governs inner feelings, mental serenity, imagination, intuition, maternal love, and memory. The Moon's placement determines your Janma Rasi and Nakshatra, shaping your emotional responses and daily cosmic rhythm.",
    rasi: "Cancer (Kataka)",
    exalt: "Taurus (Rishabha 3°)",
    debil: "Scorpio (Vrischikam 3°)",
    gem: "Natural Pearl (முத்து)",
    day: "Monday (திங்கள்)",
    deity: "Goddess Parvati / Water",
    mantra: "ॐ ஷ்ராம் ஷ்ரீம் ஷ்ரௌம் ஸஹ சந்திராய நமஹ ॥",
    cta: "Check Your Moon Sign & Dasa Balance"
  },
  Mars: {
    key: "Mars",
    name: "Sevvai / Mangal (Mars)",
    sanskrit: "SEVVAI BHAGAVAN • பூமி / தைரியகாரகன்",
    tagline: "Commander of Valor, Ambition, Land & Vital Energy",
    avatar: "🔴",
    color: "#ef4444",
    desc: "Sevvai is the celestial commander representing physical vigor, courage, brotherly bonds, land assets, technical engineering, and decisive drive. A harmonious Mars bestows fearlessness and triumphant victory over obstacles.",
    rasi: "Aries & Scorpio (மேஷம், விருச்சிகம்)",
    exalt: "Capricorn (Makara 28°)",
    debil: "Cancer (Kataka 28°)",
    gem: "Red Coral (பவளம்)",
    day: "Tuesday (செவ்வாய்)",
    deity: "Lord Murugan (Kartikeya)",
    mantra: "ॐ க்ராம் க்ரீம் க்ரௌம் ஸஹ பௌமாய நமஹ ॥",
    cta: "Check Mangal Dosha & Mars Energy"
  },
  Mercury: {
    key: "Mercury",
    name: "Budhan (Mercury)",
    sanskrit: "BUDHA BHAGAVAN • வித்யாகாரகன்",
    tagline: "Prince of Intellect, Logic, Trade & Eloquent Speech",
    avatar: "🟢",
    color: "#10b981",
    desc: "Budhan governs analytical intellect, mathematics, commerce, communication, wit, and learning agility. A strong Mercury grants sharp business acumen, diplomatic speech, and mastery in sciences and arts.",
    rasi: "Gemini & Virgo (மிதுனம், கன்னி)",
    exalt: "Virgo (Kanya 15°)",
    debil: "Pisces (Meena 15°)",
    gem: "Emerald (மரகதம்)",
    day: "Wednesday (புதன்)",
    deity: "Lord Vishnu / Saraswati",
    mantra: "ॐ ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ புதாய நமஹ ॥",
    cta: "Explore Budhaditya Yoga & Intellect"
  },
  Jupiter: {
    key: "Jupiter",
    name: "Guru / Brihaspati (Jupiter)",
    sanskrit: "GURU BHAGAVAN • புத்திர / தனகாரகன்",
    tagline: "Supreme Preceptor of Wisdom, Wealth, Children & Dharma",
    avatar: "🟡",
    color: "#eab308",
    desc: "Guru is the prime benefic representing divine blessings, spiritual wisdom, progeny, wealth, and righteousness (Dharma). Jupiter's auspicious Drishti (gaze) possesses the power to neutralize thousands of afflictions in a horoscope.",
    rasi: "Sagittarius & Pisces (தனுசு, மீனம்)",
    exalt: "Cancer (Kataka 5°)",
    debil: "Capricorn (Makara 5°)",
    gem: "Yellow Sapphire (புஷ்பராகம்)",
    day: "Thursday (வியாழன்)",
    deity: "Lord Dakshinamurthy / Shiva",
    mantra: "ॐ கிராம் க்ரீம் க்ரௌம் ஸஹ குரவே நமஹ ॥",
    cta: "Examine Gaja Kesari Yoga & Guru Blessings"
  },
  Venus: {
    key: "Venus",
    name: "Shukran (Venus)",
    sanskrit: "SHUKRA BHAGAVAN • களத்திரகாரகன்",
    tagline: "Architect of Romance, Luxury, Arts, Beauty & Marital Harmony",
    avatar: "⚪",
    color: "#ec4899",
    desc: "Shukran presides over refined aesthetics, beauty, artistic talents, luxury, vehicles, and matrimonial bliss. A well-placed Venus bestows magnetic charisma, joyous relationships, and material affluence.",
    rasi: "Taurus & Libra (ரிஷபம், துலாம்)",
    exalt: "Pisces (Meena 27°)",
    debil: "Virgo (Kanya 27°)",
    gem: "Diamond / Zircon (வைரம்)",
    day: "Friday (வெள்ளி)",
    deity: "Goddess Mahalakshmi",
    mantra: "ॐ த்ராம் த்ரீம் த்ரௌம் ஸஹ சுக்ராய நமஹ ॥",
    cta: "Discover Malavya Yoga & Venus Placement"
  },
  Saturn: {
    key: "Saturn",
    name: "Sani (Saturn)",
    sanskrit: "SANI BHAGAVAN • ஆயுள் / கர்மகாரகன்",
    tagline: "Dispenser of Cosmic Justice, Longevity, Humility & Discipline",
    avatar: "🪐",
    color: "#3b82f6",
    desc: "Sani is the eternal dispenser of Karma, testing patience, endurance, humility, and dedication. Saturn strips away superficial illusions to build lasting spiritual resilience, wisdom, and enduring monumental success.",
    rasi: "Capricorn & Aquarius (மகரம், கும்பம்)",
    exalt: "Libra (Thulam 20°)",
    debil: "Aries (Mesha 20°)",
    gem: "Blue Sapphire (நீலக்கல்)",
    day: "Saturday (சனி)",
    deity: "Lord Sastha / Hanuman / Yama",
    mantra: "ॐ ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ சனைச்சராய நமஹ ॥",
    cta: "Check Saturn Sade Sati & Karma"
  },
  Rahu: {
    key: "Rahu",
    name: "Rahu (North Lunar Node)",
    sanskrit: "RAHU BHAGAVAN • நிழல் கிரகம் / போககாரகன்",
    tagline: "Shadow Titan of Ambition, Worldly Maya, Technology & Foreign Travel",
    avatar: "🟣",
    color: "#a855f7",
    desc: "Rahu represents boundless ambition, technological brilliance, sudden breakthroughs, unconventional mastery, and foreign accomplishments. It accelerates worldly achievements while teaching discernment over illusion.",
    rasi: "Co-lord Aquarius (கும்பம்)",
    exalt: "Taurus (Rishabha 20°)",
    debil: "Scorpio (Vrischikam 20°)",
    gem: "Hessonite / Gomed (கோமேதகம்)",
    day: "Saturday / Rahu Kalam",
    deity: "Goddess Durga / Sarpa Deivam",
    mantra: "ॐ ப்ராம் ப்ரீம் ப்ரௌம் ஸஹ ராஹவே நமஹ ॥",
    cta: "Examine Rahu Dasa & Foreign Prospects"
  },
  Ketu: {
    key: "Ketu",
    name: "Ketu (South Lunar Node)",
    sanskrit: "KETU BHAGAVAN • ஞான / மோக்ஷகாரகன்",
    tagline: "Mystic Master of Liberation (Moksha), Intuition & Occult Wisdom",
    avatar: "🟤",
    color: "#d97706",
    desc: "Ketu represents detachment, deep meditative intuition, occult sciences, healing prowess, and spiritual liberation (Moksha). Ketu dissolves worldly bondages to unveil transcendental truth and inner enlightenment.",
    rasi: "Co-lord Scorpio (விருச்சிகம்)",
    exalt: "Sagittarius (Dhanus 20°)",
    debil: "Gemini (Mithuna 20°)",
    gem: "Cat's Eye (வைடூரியம்)",
    day: "Tuesday / Special Hours",
    deity: "Lord Ganesha / Chitragupta",
    mantra: "ॐ ஸ்ராம் ஸ்ரீம் ஸ்ரௌம் ஸஹ கேதவே நமஹ ॥",
    cta: "Analyze Ketu Moksha & Spiritual Gifts"
  }
};

let currentSelectedGraha = "Sun";

function selectGraha(grahaKey) {
  const data = NAVAGRAHA_DATA[grahaKey];
  if (!data) return;
  currentSelectedGraha = grahaKey;

  // Update spotlight card elements
  const avatarEl = document.getElementById("spotlightAvatar");
  const sanskritEl = document.getElementById("spotlightSanskrit");
  const nameEl = document.getElementById("spotlightName");
  const taglineEl = document.getElementById("spotlightTagline");
  const descEl = document.getElementById("spotlightDesc");
  const rasiEl = document.getElementById("spotlightRasi");
  const exaltEl = document.getElementById("spotlightExalt");
  const debilEl = document.getElementById("spotlightDebil");
  const gemEl = document.getElementById("spotlightGem");
  const dayEl = document.getElementById("spotlightDay");
  const deityEl = document.getElementById("spotlightDeity");
  const mantraEl = document.getElementById("spotlightMantra");
  const ctaTextEl = document.getElementById("spotlightCtaText");
  const cardEl = document.getElementById("grahaSpotlightCard");

  if (avatarEl) avatarEl.textContent = data.avatar;
  if (sanskritEl) sanskritEl.textContent = data.sanskrit;
  if (nameEl) nameEl.textContent = data.name;
  if (taglineEl) taglineEl.textContent = data.tagline;
  if (descEl) descEl.textContent = data.desc;
  if (rasiEl) rasiEl.textContent = data.rasi;
  if (exaltEl) exaltEl.textContent = data.exalt;
  if (debilEl) debilEl.textContent = data.debil;
  if (gemEl) gemEl.textContent = data.gem;
  if (dayEl) dayEl.textContent = data.day;
  if (deityEl) deityEl.textContent = data.deity;
  if (mantraEl) mantraEl.textContent = data.mantra;
  if (ctaTextEl) ctaTextEl.textContent = data.cta;

  // Card theme glow effect
  if (cardEl) {
    cardEl.style.setProperty("--graha-accent", data.color);
    cardEl.classList.add("spotlight-pulse");
    setTimeout(() => cardEl.classList.remove("spotlight-pulse"), 400);
  }

  // Update active state in orbital nodes
  document.querySelectorAll(".graha-interactive-node").forEach(node => {
    node.classList.toggle("active-graha-node", node.dataset.graha === grahaKey);
  });

  // Update active state in mini cards
  document.querySelectorAll(".graha-mini-card").forEach(card => {
    card.classList.toggle("active-mini-card", card.dataset.graha === grahaKey);
  });
}

function initNavagrahaSection() {
  // Render quick selector grid
  const gridEl = document.getElementById("navagrahaQuickGrid");
  if (gridEl) {
    gridEl.innerHTML = Object.values(NAVAGRAHA_DATA).map(g => `
      <div class="graha-mini-card ${g.key === 'Sun' ? 'active-mini-card' : ''}" data-graha="${g.key}">
        <div class="mini-card-icon" style="background: ${g.color}22; color: ${g.color}; border: 1px solid ${g.color}55;">${g.avatar}</div>
        <div class="mini-card-info">
          <div class="mini-card-name">${g.name.split(' ')[0]}</div>
          <div class="mini-card-sub">${g.gem.split(' ')[0]}</div>
        </div>
        <div class="mini-card-pill" style="color: ${g.color};">&#9679;</div>
      </div>
    `).join("");
  }

  // Setup click listeners for interactive orbital nodes
  document.querySelectorAll(".graha-interactive-node").forEach(node => {
    node.addEventListener("click", () => {
      const g = node.dataset.graha;
      if (g) selectGraha(g);
    });
  });

  // Setup click listeners for mini cards
  if (gridEl) {
    gridEl.addEventListener("click", (e) => {
      const card = e.target.closest(".graha-mini-card");
      if (card && card.dataset.graha) {
        selectGraha(card.dataset.graha);
      }
    });
  }

  // Setup CTA button
  const ctaBtn = document.getElementById("btnSpotlightToChart");
  if (ctaBtn) {
    ctaBtn.addEventListener("click", () => {
      showPage("jathakam");
      const form = document.getElementById("formSection");
      if (form) form.scrollIntoView({ behavior: "smooth" });
    });
  }
}

// Call initNavagrahaSection on page load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initNavagrahaSection);
} else {
  initNavagrahaSection();
}

// --- Sacred 12 Vedic Rasis (Zodiac Signs) Section Data & Logic ---
const RASI_DATA = [
  {
    id: "Mesha",
    num: 1,
    name: "Aries (மேஷம்)",
    sanskrit: "MESHA RASI • அக்னி தத்துவம்",
    symbol: "♈",
    element: "Fire",
    elementLabel: "Fire (அக்னி)",
    mobility: "Chara / Cardinal (சரம்)",
    lord: "Mars (Sevvai / செவ்வாய்)",
    body: "Head, Brain & Forehead (தலை)",
    direction: "East (கிழக்கு)",
    gem: "Red Coral / Crimson (பவளம்)",
    dignities: "Sun Exalted (10°) • Saturn Debilitated (20°)",
    tagline: "The Cardinal Fire Pioneer • Leadership, Valor & Initiative",
    desc: "Mesha is the first sign of the zodiac representing boundless initiative, primal courage, vital life force, and enterprise. Governed by Sevvai, individuals with strong Aries energy are courageous trailblazers, bold decision-makers, and energetic pioneers.",
    nakshatrasDetail: [
      { star: "Ashwini", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Ketu" },
      { star: "Bharani", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Venus" },
      { star: "Krittika", padas: "Pada 1 (First Quarter)", lord: "Sun" }
    ],
    color: "#EF4444"
  },
  {
    id: "Vrishabha",
    num: 2,
    name: "Taurus (ரிஷபம்)",
    sanskrit: "VRISHABHA RASI • பூமி தத்துவம்",
    symbol: "♉",
    element: "Earth",
    elementLabel: "Earth (பூமி)",
    mobility: "Sthira / Fixed (ஸ்திரம்)",
    lord: "Venus (Shukran / சுக்ரன்)",
    body: "Face, Neck, Throat & Voice (முகம்/தொண்டை)",
    direction: "South (தெற்கு)",
    gem: "Diamond / White (வைரம்)",
    dignities: "Moon Exalted (3°) • Rahu Exalted",
    tagline: "The Fixed Earth Sanctuary • Wealth, Perseverance & Harmony",
    desc: "Vrishabha embodies grounded stability, material wealth, culinary arts, beauty, and unwavering perseverance. Governed by Shukran, it grants aesthetic grace, enduring loyalty, financial acumen, and steadfast practical determination.",
    nakshatrasDetail: [
      { star: "Krittika", padas: "Pada 2, 3, 4", lord: "Sun" },
      { star: "Rohini", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Moon" },
      { star: "Mrigashira", padas: "Pada 1, 2", lord: "Mars" }
    ],
    color: "#10B981"
  },
  {
    id: "Mithuna",
    num: 3,
    name: "Gemini (மிதுனம்)",
    sanskrit: "MITHUNA RASI • காற்று தத்துவம்",
    symbol: "♊",
    element: "Air",
    elementLabel: "Air (காற்று)",
    mobility: "Dwiswabhava / Dual (உபயம்)",
    lord: "Mercury (Budhan / புதன்)",
    body: "Shoulders, Arms, Hands & Lungs (தோள்பட்டை/கைகள்)",
    direction: "West (மேற்கு)",
    gem: "Emerald / Green (மரகதம்)",
    dignities: "Rahu Exalted / Friendly • Mercury Own House",
    tagline: "The Dual Air Communicator • Wit, Intellect & Versatility",
    desc: "Mithuna represents intellectual agility, communication, commerce, wit, and adaptable curiosity. Governed by Budhan, it excels in diplomacy, literature, media, networking, trade, and creative analytical thinking.",
    nakshatrasDetail: [
      { star: "Mrigashira", padas: "Pada 3, 4", lord: "Mars" },
      { star: "Ardra", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Rahu" },
      { star: "Punarvasu", padas: "Pada 1, 2, 3", lord: "Jupiter" }
    ],
    color: "#38BDF8"
  },
  {
    id: "Kataka",
    num: 4,
    name: "Cancer (கடகம்)",
    sanskrit: "KATAKA RASI • நீர் தத்துவம்",
    symbol: "♋",
    element: "Water",
    elementLabel: "Water (நீர்)",
    mobility: "Chara / Cardinal (சரம்)",
    lord: "Moon (Chandra / சந்திரன்)",
    body: "Chest, Breasts, Heart & Stomach (மார்பு/இதயம்)",
    direction: "North (வடக்கு)",
    gem: "Natural Pearl / Silver (முத்து)",
    dignities: "Jupiter Exalted (5°) • Mars Debilitated (28°)",
    tagline: "The Cardinal Water Sanctuary • Empathy, Nurturing & Intuition",
    desc: "Kataka represents deep emotional intuition, maternal empathy, domestic sanctuary, and imaginative sensitivity. Governed by Chandra, it rules subconscious feelings, psychic empathy, and protective caring for loved ones.",
    nakshatrasDetail: [
      { star: "Punarvasu", padas: "Pada 4", lord: "Jupiter" },
      { star: "Pushya", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Saturn" },
      { star: "Ashlesha", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Mercury" }
    ],
    color: "#60A5FA"
  },
  {
    id: "Simha",
    num: 5,
    name: "Leo (சிம்மம்)",
    sanskrit: "SIMHA RASI • அக்னி தத்துவம்",
    symbol: "♌",
    element: "Fire",
    elementLabel: "Fire (அக்னி)",
    mobility: "Sthira / Fixed (ஸ்திரம்)",
    lord: "Sun (Surya / சூரியன்)",
    body: "Heart, Spine, Upper Back & Solar Plexus (இதயம்)",
    direction: "East (கிழக்கு)",
    gem: "Ruby / Gold & Orange (மாணிக்கம்)",
    dignities: "Sun Moolatrikona • Mars Friendly",
    tagline: "The Royal Fire Sovereign • Majesty, Nobility & Executive Will",
    desc: "Simha is the royal celestial throne governed by Surya, representing majesty, executive leadership, honor, generosity, and creative self-expression. It inspires sovereign dignity, heroic confidence, and high social standing.",
    nakshatrasDetail: [
      { star: "Magha", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Ketu" },
      { star: "Purva Phalguni", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Venus" },
      { star: "Uttara Phalguni", padas: "Pada 1", lord: "Sun" }
    ],
    color: "#F59E0B"
  },
  {
    id: "Kanya",
    num: 6,
    name: "Virgo (கன்னி)",
    sanskrit: "KANYA RASI • பூமி தத்துவம்",
    symbol: "♍",
    element: "Earth",
    elementLabel: "Earth (பூமி)",
    mobility: "Dwiswabhava / Dual (உபயம்)",
    lord: "Mercury (Budhan / புதன்)",
    body: "Abdomen, Intestines & Digestive Tract (வயிறு)",
    direction: "South (தெற்கு)",
    gem: "Emerald / Dark Green (மரகதம்)",
    dignities: "Mercury Exalted (15°) • Venus Debilitated (27°)",
    tagline: "The Dual Earth Craftsman • Precision, Service & Healing",
    desc: "Kanya governs analytical precision, healing crafts, dedicated service, bookkeeping, and organizational mastery. Governed by Budhan, it seeks perfection, purity, research depth, and practical wisdom.",
    nakshatrasDetail: [
      { star: "Uttara Phalguni", padas: "Pada 2, 3, 4", lord: "Sun" },
      { star: "Hasta", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Moon" },
      { star: "Chitra", padas: "Pada 1, 2", lord: "Mars" }
    ],
    color: "#059669"
  },
  {
    id: "Thula",
    num: 7,
    name: "Libra (துலாம்)",
    sanskrit: "THULA RASI • காற்று தத்துவம்",
    symbol: "♎",
    element: "Air",
    elementLabel: "Air (காற்று)",
    mobility: "Chara / Cardinal (சரம்)",
    lord: "Venus (Shukran / சுக்ரன்)",
    body: "Lower Abdomen, Kidneys & Pelvis (சிறுநீரகம்)",
    direction: "West (மேற்கு)",
    gem: "Diamond / Pastel White (வைரம்)",
    dignities: "Saturn Exalted (20°) • Sun Debilitated (10°)",
    tagline: "The Cardinal Air Balance • Harmony, Justice & Partnership",
    desc: "Thula represents the cosmic scales of balance, justice, matrimonial partnership, diplomacy, and elegance. Governed by Shukran, it seeks social harmony, grace, balanced judgment, and refined artistic aesthetics.",
    nakshatrasDetail: [
      { star: "Chitra", padas: "Pada 3, 4", lord: "Mars" },
      { star: "Swati", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Rahu" },
      { star: "Vishakha", padas: "Pada 1, 2, 3", lord: "Jupiter" }
    ],
    color: "#EC4899"
  },
  {
    id: "Vrischika",
    num: 8,
    name: "Scorpio (விருச்சிகம்)",
    sanskrit: "VRISCHIKA RASI • நீர் தத்துவம்",
    symbol: "♏",
    element: "Water",
    elementLabel: "Water (நீர்)",
    mobility: "Sthira / Fixed (ஸ்திரம்)",
    lord: "Mars & Ketu (செவ்வாய் / கேது)",
    body: "Pelvic Region & Excretory System (இடைப்பகுதி)",
    direction: "North (வடக்கு)",
    gem: "Red Coral / Deep Crimson (பவளம்)",
    dignities: "Ketu Exalted • Moon Debilitated (3°)",
    tagline: "The Fixed Water Mystic • Transformation, Occult & Resilience",
    desc: "Vrischikam rules mystical transformation, research depth, occult sciences, emotional resilience, and unyielding will. Governed by Mars and Ketu, it penetrates deep into cosmic mysteries and spiritual alchemy.",
    nakshatrasDetail: [
      { star: "Vishakha", padas: "Pada 4", lord: "Jupiter" },
      { star: "Anuradha", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Saturn" },
      { star: "Jyeshtha", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Mercury" }
    ],
    color: "#DC2626"
  },
  {
    id: "Dhanus",
    num: 9,
    name: "Sagittarius (தனுசு)",
    sanskrit: "DHANUS RASI • அக்னி தத்துவம்",
    symbol: "♐",
    element: "Fire",
    elementLabel: "Fire (அக்னி)",
    mobility: "Dwiswabhava / Dual (உபயம்)",
    lord: "Jupiter (Guru / குரு)",
    body: "Thighs, Hips & Arterial System (தொடைகள்)",
    direction: "East (கிழக்கு)",
    gem: "Yellow Sapphire / Royal Yellow (புஷ்பராகம்)",
    dignities: "Ketu Exalted • Jupiter Moolatrikona",
    tagline: "The Dual Fire Seeker • Dharma, Higher Wisdom & Optimism",
    desc: "Dhanus represents higher philosophy, divine dharma, righteous optimism, pilgrimage, and supreme spiritual wisdom. Governed by Guru, it strives for universal truth, moral ethics, teaching, and expansive horizons.",
    nakshatrasDetail: [
      { star: "Mula", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Ketu" },
      { star: "Purva Ashadha", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Venus" },
      { star: "Uttara Ashadha", padas: "Pada 1", lord: "Sun" }
    ],
    color: "#D97706"
  },
  {
    id: "Makara",
    num: 10,
    name: "Capricorn (மகரம்)",
    sanskrit: "MAKARA RASI • பூமி தத்துவம்",
    symbol: "♑",
    element: "Earth",
    elementLabel: "Earth (பூமி)",
    mobility: "Chara / Cardinal (சரம்)",
    lord: "Saturn (Sani / சனி)",
    body: "Knees, Joints & Skeletal System (முழங்கால்கள்)",
    direction: "South (தெற்கு)",
    gem: "Blue Sapphire / Dark Navy (நீலக்கல்)",
    dignities: "Mars Exalted (28°) • Jupiter Debilitated (5°)",
    tagline: "The Cardinal Earth Architect • Mastery, Ambition & Endurance",
    desc: "Makara embodies steadfast discipline, monumental endurance, career ambition, and pragmatic governance. Governed by Sani, it scales the highest peaks of worldly mastery through patient resilience and organizational leadership.",
    nakshatrasDetail: [
      { star: "Uttara Ashadha", padas: "Pada 2, 3, 4", lord: "Sun" },
      { star: "Shravana", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Moon" },
      { star: "Dhanishta", padas: "Pada 1, 2", lord: "Mars" }
    ],
    color: "#475569"
  },
  {
    id: "Kumbha",
    num: 11,
    name: "Aquarius (கும்பம்)",
    sanskrit: "KUMBHA RASI • காற்று தத்துவம்",
    symbol: "♒",
    element: "Air",
    elementLabel: "Air (காற்று)",
    mobility: "Sthira / Fixed (ஸ்திரம்)",
    lord: "Saturn & Rahu (சனி / ராகு)",
    body: "Calves, Shins & Ankles (கணுக்கால்)",
    direction: "West (மேற்கு)",
    gem: "Blue Sapphire / Indigo (நீலம்)",
    dignities: "Saturn Moolatrikona • Rahu Co-ruler",
    tagline: "The Fixed Air Visionary • Innovation, Humanity & Occult Intuition",
    desc: "Kumbha symbolizes universal humanitarianism, scientific innovation, intuition, and collective consciousness. Governed by Sani and Rahu, it envisions futuristic horizons, philosophical reform, and unconventional mastery.",
    nakshatrasDetail: [
      { star: "Dhanishta", padas: "Pada 3, 4", lord: "Mars" },
      { star: "Shatabhisha", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Rahu" },
      { star: "Purva Bhadrapada", padas: "Pada 1, 2, 3", lord: "Jupiter" }
    ],
    color: "#8B5CF6"
  },
  {
    id: "Meena",
    num: 12,
    name: "Pisces (மீனம்)",
    sanskrit: "MEENA RASI • நீர் தத்துவம்",
    symbol: "♓",
    element: "Water",
    elementLabel: "Water (நீர்)",
    mobility: "Dwiswabhava / Dual (உபயம்)",
    lord: "Jupiter (Guru / குரு)",
    body: "Feet, Soles & Lymphatic System (பாதங்கள்)",
    direction: "North (வடக்கு)",
    gem: "Yellow Sapphire / Sea Gold (புஷ்பராகம்)",
    dignities: "Venus Exalted (27°) • Mercury Debilitated (15°)",
    tagline: "The Dual Water Transcendence • Moksha, Dreams & Cosmic Empathy",
    desc: "Meena represents the ocean of cosmic consciousness, empathy, dreams, spiritual imagination, and ultimate Moksha (spiritual liberation). Governed by Guru, it dissolves worldly illusion into divine transcendental bliss.",
    nakshatrasDetail: [
      { star: "Purva Bhadrapada", padas: "Pada 4", lord: "Jupiter" },
      { star: "Uttara Bhadrapada", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Saturn" },
      { star: "Revati", padas: "Pada 1, 2, 3, 4 (Complete)", lord: "Mercury" }
    ],
    color: "#3B82F6"
  }
];

let selectedRasiId = "Mesha";

function selectRasi(rasiId) {
  const rasi = RASI_DATA.find(r => r.id === rasiId);
  if (!rasi) return;
  selectedRasiId = rasiId;

  const symbolEl = document.getElementById("rasiSpotlightSymbol");
  const numEl = document.getElementById("rasiSpotlightNum");
  const nameEl = document.getElementById("rasiSpotlightName");
  const descEl = document.getElementById("rasiSpotlightDesc");
  const lordEl = document.getElementById("rasiSpotlightLord");
  const elementEl = document.getElementById("rasiSpotlightElement");
  const mobilityEl = document.getElementById("rasiSpotlightMobility");
  const bodyEl = document.getElementById("rasiSpotlightBody");
  const directionEl = document.getElementById("rasiSpotlightDirection");
  const gemEl = document.getElementById("rasiSpotlightGem");
  const dignitiesEl = document.getElementById("rasiSpotlightDignities");
  const nakshatrasEl = document.getElementById("rasiSpotlightNakshatras");
  const cardEl = document.getElementById("rasiSpotlightCard");

  if (symbolEl) symbolEl.textContent = rasi.symbol;
  if (numEl) numEl.textContent = `SIGN ${rasi.num} • ${rasi.mobility.toUpperCase()} • ${rasi.element.toUpperCase()}`;
  if (nameEl) nameEl.textContent = rasi.name;
  if (descEl) descEl.textContent = rasi.desc;
  if (lordEl) lordEl.textContent = `Lord: ${rasi.lord}`;
  if (elementEl) elementEl.textContent = rasi.elementLabel;
  if (mobilityEl) mobilityEl.textContent = rasi.mobility;
  if (bodyEl) bodyEl.textContent = rasi.body;
  if (directionEl) directionEl.textContent = rasi.direction;
  if (gemEl) gemEl.textContent = rasi.gem;
  if (dignitiesEl) dignitiesEl.textContent = rasi.dignities;

  if (nakshatrasEl && rasi.nakshatrasDetail) {
    nakshatrasEl.innerHTML = rasi.nakshatrasDetail.map((n, i) => `
      <div class="nakshatra-quarter-card">
        <div class="nak-card-head">
          <span class="nak-star-name">✨ ${n.star}</span>
          <span class="nak-lord-tag">Lord: ${n.lord}</span>
        </div>
        <div class="nak-padas-text">${n.padas}</div>
      </div>
    `).join("");
  }

  if (cardEl) {
    cardEl.style.setProperty("--rasi-accent", rasi.color);
    cardEl.classList.add("rasi-pulse");
    setTimeout(() => cardEl.classList.remove("rasi-pulse"), 350);
  }

  document.querySelectorAll(".rasi-compact-card").forEach(c => {
    c.classList.toggle("active-rasi-card", c.dataset.rasi === rasiId);
  });
}

function renderRasiGrid(filterElement = "all") {
  const grid = document.getElementById("rasiCardsGrid");
  if (!grid) return;

  const filtered = filterElement === "all" 
    ? RASI_DATA 
    : RASI_DATA.filter(r => r.element === filterElement);

  grid.innerHTML = filtered.map(r => `
    <div class="rasi-compact-card ${r.id === selectedRasiId ? 'active-rasi-card' : ''}" data-rasi="${r.id}" style="--rasi-item-color: ${r.color};">
      <div class="compact-symbol-circle">${r.symbol}</div>
      <div class="compact-card-body">
        <div class="compact-name-row">
          <span class="compact-name">${r.name.split(' ')[0]}</span>
          <span class="compact-tamil">${r.name.includes('(') ? r.name.match(/\\((.*?)\\)/)?.[1] || '' : ''}</span>
        </div>
        <div class="compact-sub-row">
          <span class="compact-lord">${r.lord.split(' ')[0]}</span>
          <span class="compact-dot">•</span>
          <span class="compact-elem">${r.element}</span>
        </div>
      </div>
      <span class="compact-order">#${r.num}</span>
    </div>
  `).join("");
}

function initRasiSection() {
  renderRasiGrid("all");
  selectRasi("Mesha");

  // Element filter pills
  const filterPills = document.getElementById("rasiFilterPills");
  if (filterPills) {
    filterPills.addEventListener("click", (e) => {
      const btn = e.target.closest(".filter-pill");
      if (btn && btn.dataset.element) {
        filterPills.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        renderRasiGrid(btn.dataset.element);
      }
    });
  }

  // Card click event delegation
  const grid = document.getElementById("rasiCardsGrid");
  if (grid) {
    grid.addEventListener("click", (e) => {
      const card = e.target.closest(".rasi-compact-card");
      if (card && card.dataset.rasi) {
        selectRasi(card.dataset.rasi);
        const inspector = document.getElementById("rasiSpotlightCard");
        if (inspector && window.innerWidth <= 768) {
          inspector.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }
    });
  }

  // CTA button
  const cta = document.getElementById("btnRasiToChart");
  if (cta) {
    cta.addEventListener("click", () => {
      showPage("jathakam");
      const form = document.getElementById("formSection");
      if (form) form.scrollIntoView({ behavior: "smooth" });
    });
  }
}

// Call initRasiSection on page load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initRasiSection);
} else {
  initRasiSection();
}

// --- Prasannam: the chart for this moment where you are, and the Moon's position (Chandra Nadi) ---

function setPrasStatus(text) {
  document.getElementById("prasStatus").textContent = text;
}

function startPrasannam() {
  if (state.prasannam.place) castPrasannam();
  else locatePrasannam();
}

function locatePrasannam() {
  const labels = L();
  if (!navigator.geolocation) {
    showPrasSearch();
    return;
  }
  setPrasStatus(labels.ui.prasLocating);
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      state.prasannam.place = {
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        label: null,
      };
      document.getElementById("prasSearch").classList.add("hidden");
      castPrasannam();
    },
    () => showPrasSearch(),
    { timeout: 15000, maximumAge: 10 * 60 * 1000 }
  );
}

function showPrasSearch() {
  setPrasStatus(state.prasannam.place ? "" : L().ui.prasDenied);
  document.getElementById("prasSearch").classList.remove("hidden");
  document.getElementById("prasPlaceInput").focus();
}

async function castPrasannam() {
  const labels = L();
  const place = state.prasannam.place;
  setPrasStatus(labels.ui.prasCasting);
  const params = new URLSearchParams({ latitude: place.latitude, longitude: place.longitude, timezone: place.timezone });
  const res = await fetch(`/api/prasannam?${params}`);
  if (!res.ok) {
    setPrasStatus(labels.ui.prasError + (await res.text()));
    return;
  }
  state.prasannam.chart = await res.json();
  setPrasStatus("");
  renderPrasannam();
}

function renderPrasannam() {
  const labels = L();
  const chart = state.prasannam.chart;
  const place = state.prasannam.place;
  document.getElementById("prasResult").classList.remove("hidden");
  document.getElementById("prasTime").textContent = `${fmtDateTime(chart.when)}:${chart.when.slice(17, 19)} (UTC${chart.when.slice(19)})`;
  document.getElementById("prasPlace").textContent =
    place.label ||
    labels.ui.prasMyLocation.replace("{lat}", place.latitude.toFixed(4)).replace("{lon}", place.longitude.toFixed(4));

  const moon = chart.d1.grahas.Moon;
  document.getElementById("chandraNadiMain").textContent =
    `${labels.nakshatra[moon.nakshatra]} ${labels.ui.padaWord} ${moon.pada} \u00B7 ${labels.rasi[moon.rasi]} ${formatDMS(moon.degree_in_sign)}`;
  const rows = [
    [labels.ui.prasMoonRasi, `${labels.rasi[moon.rasi]} (${labels.planets[moon.rasi_lord]})`],
    [labels.ui.prasMoonStar, `${labels.nakshatra[moon.nakshatra]} (${labels.planets[moon.star_lord]})`],
    [labels.ui.prasMoonPada, String(moon.pada)],
    [labels.ui.prasMoonDegree, formatDMS(moon.degree_in_sign)],
    [labels.ui.prasMoonAbs, formatDMS(moon.longitude)],
    [labels.ui.lagna, `${labels.rasi[chart.d1.lagna_rasi]} ${formatDMS(chart.lagna_longitude % 30)}`],
  ];
  const body = document.getElementById("chandraNadiBody");
  body.innerHTML = "";
  for (const [k, v] of rows) {
    const tr = document.createElement("tr");
    for (const text of [k, v]) {
      const td = document.createElement("td");
      td.textContent = text;
      tr.appendChild(td);
    }
    body.appendChild(tr);
  }

  drawGrid(document.getElementById("prasGrid"), chart.d1, { centerLabel: labels.ui.topPrasannam });

  const tbody = document.getElementById("prasBody");
  tbody.innerHTML = "";
  for (const g of Object.values(chart.d1.grahas)) {
    const tr = document.createElement("tr");
    const isRetrogradeEligible = g.retrograde && !NODES_NOT_MARKED_RETROGRADE.has(g.name);
    for (const text of [
      labels.planets[g.name] + (isRetrogradeEligible ? " (R)" : ""),
      labels.rasi[g.rasi],
      formatDMS(g.degree_in_sign),
      labels.nakshatra[g.nakshatra],
      String(g.pada),
    ]) {
      const td = document.createElement("td");
      td.textContent = text;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
}

document.getElementById("prasNow").addEventListener("click", () => startPrasannam());
document.getElementById("prasUseLocation").addEventListener("click", () => {
  state.prasannam.place = null;
  locatePrasannam();
});
document.getElementById("prasChangePlace").addEventListener("click", showPrasSearch);

let prasSearchTimer = null;
document.getElementById("prasPlaceInput").addEventListener("input", (e) => {
  clearTimeout(prasSearchTimer);
  const query = e.target.value.trim();
  const list = document.getElementById("prasPlaceResults");
  if (query.length < 2) {
    list.classList.add("hidden");
    return;
  }
  prasSearchTimer = setTimeout(async () => {
    const res = await fetch(`/api/geocode?query=${encodeURIComponent(query)}`);
    const places = res.ok ? await res.json() : [];
    list.innerHTML = "";
    if (places.length === 0) {
      const li = document.createElement("li");
      li.className = "pob-no-results";
      li.textContent = L().ui.pobNoResults;
      list.appendChild(li);
    }
    for (const p of places) {
      const li = document.createElement("li");
      li.textContent = p.label;
      li.addEventListener("click", () => {
        state.prasannam.place = { latitude: p.latitude, longitude: p.longitude, timezone: p.timezone, label: p.label };
        list.classList.add("hidden");
        document.getElementById("prasSearch").classList.add("hidden");
        e.target.value = "";
        castPrasannam();
      });
      list.appendChild(li);
    }
    list.classList.remove("hidden");
  }, 300);
});

// The Pariharam page: its own side nav of pariharams, and the one picked. The names to
// recite are shown in English and Tamil together, whatever the language setting.
function renderPariharam() {
  const nav = document.getElementById("pariharamNavList");
  nav.innerHTML = "";
  PARIHARAMS.forEach((p, i) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "pariharam-topic" + (i === state.pariharamTopic ? " active" : "");
    btn.textContent = p.title[state.lang];
    btn.addEventListener("click", () => {
      state.pariharamTopic = i;
      renderPariharam();
    });
    li.appendChild(btn);
    nav.appendChild(li);
  });

  const p = PARIHARAMS[state.pariharamTopic];
  document.getElementById("lblPariharamTitle").textContent = p.title[state.lang];
  const container = document.getElementById("pariharamContent");
  container.innerHTML = "";
  const intro = document.createElement("p");
  intro.className = "pariharam-intro";
  intro.textContent = p.intro[state.lang];
  const ol = document.createElement("ol");
  ol.className = "pariharam-names";
  for (const name of p.names) {
    const li = document.createElement("li");
    const en = document.createElement("span");
    en.className = "pariharam-name-en";
    en.textContent = name.en;
    const ta = document.createElement("span");
    ta.className = "pariharam-name-ta";
    ta.lang = "ta";
    ta.textContent = name.ta;
    li.append(en, ta);
    ol.appendChild(li);
  }
  container.append(intro, ol);
}

function readingTable(header, rows) {
  const table = document.createElement("table");
  table.className = "reading-table";
  if (header) {
    const headRow = document.createElement("tr");
    for (const col of header) {
      const th = document.createElement("th");
      th.textContent = col[state.lang];
      headRow.appendChild(th);
    }
    table.appendChild(headRow);
  }
  for (const row of rows) {
    const tr = document.createElement("tr");
    for (const col of row) {
      const td = document.createElement("td");
      td.textContent = col[state.lang];
      tr.appendChild(td);
    }
    table.appendChild(tr);
  }
  return table;
}

function renderReadingPage(topicKey) {
  const topic = READING_TOPICS[topicKey];
  const container = document.getElementById("readingContent");
  container.innerHTML = "";
  if (!topic) return;

  document.getElementById("readingTitle").textContent = topic.title[state.lang];

  const intro = document.createElement("p");
  intro.textContent = topic.intro[state.lang];
  container.appendChild(intro);

  if (topic.table) container.appendChild(readingTable(topic.tableHeader, topic.table));

  // Optional further sections, each with a heading, text and its own table.
  for (const section of topic.sections || []) {
    const heading = document.createElement("h3");
    heading.className = "reading-subhead";
    heading.textContent = section.heading[state.lang];
    container.appendChild(heading);
    if (section.text) {
      const p = document.createElement("p");
      p.textContent = section.text[state.lang];
      container.appendChild(p);
    }
    if (section.table) container.appendChild(readingTable(section.tableHeader, section.table));
  }

  if (topic.note) {
    const note = document.createElement("p");
    note.className = "reading-note";
    note.textContent = topic.note[state.lang];
    container.appendChild(note);
  }

  if (topic.sources && topic.sources.length) {
    const sourcesLabel = document.createElement("div");
    sourcesLabel.className = "reading-sources-label";
    sourcesLabel.textContent = L().ui.sources;
    container.appendChild(sourcesLabel);

    const ul = document.createElement("ul");
    ul.className = "reading-sources";
    for (const src of topic.sources) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = src.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = src.title;
      li.appendChild(a);
      ul.appendChild(li);
    }
    container.appendChild(ul);
  }
}

// --- Tabs ---

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// --- Rendering ---

function renderAll() {
  renderProfileSummary();
  renderVargaSelect();
  renderGrid();
  renderInduLagna();
  renderPranapada();
  renderTithi();
  renderMudakku();
  renderUpasana();
  renderKaalaPakai();
  renderDasaTable();
  renderYogas();
  renderTaraBalam();
  renderGrahaDetails();
  renderDignity();
  renderPeyarchi();
  renderDrekkanaLords();
  renderSashtashtagam();
}

function renderProfileSummary() {
  if (!state.chart || !state.chart.d1) return;
  const labels = L();
  const c = state.chart;
  
  const nameEl = document.getElementById("profileName");
  if (nameEl) nameEl.textContent = c.name || "Vedic Horoscope";

  const avatarEl = document.getElementById("profileAvatar");
  if (avatarEl && typeof c.d1.lagna_rasi === "number") {
    const zodiacSymbols = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];
    avatarEl.textContent = zodiacSymbols[c.d1.lagna_rasi] || "✨";
  }

  const detailsEl = document.getElementById("profileBirthDetails");
  if (detailsEl) {
    detailsEl.textContent = `📅 ${c.dob || ""}  ·  ⏰ ${c.tob || ""}  ·  📍 ${c.pob_label || "Location"}`;
  }

  const lagnaEl = document.getElementById("badgeLagna");
  if (lagnaEl && typeof c.d1.lagna_rasi === "number") {
    const lagnaRasiName = labels.rasi?.[c.d1.lagna_rasi] || "";
    const lagnaLabel = labels.ui?.lagna || "Lagna";
    lagnaEl.textContent = `${lagnaLabel}: ${lagnaRasiName}`;
  }

  const moon = c.d1?.grahas?.Moon;
  const moonEl = document.getElementById("badgeMoon");
  if (moonEl && moon && typeof moon.rasi === "number") {
    moonEl.textContent = `${labels.rasi?.[moon.rasi] || ""}`;
  }

  const starEl = document.getElementById("badgeStar");
  if (starEl && moon && typeof moon.nakshatra === "number") {
    const starName = labels.nakshatra?.[moon.nakshatra] || "";
    starEl.textContent = `${starName} (${moon.pada || 1})`;
  }

  const dasaEl = document.getElementById("badgeDasa");
  if (dasaEl && c.mahadasas && c.mahadasas.length) {
    const now = new Date();
    const curr = c.mahadasas.find(d => new Date(d.start) <= now && now <= new Date(d.end)) || c.mahadasas[0];
    const lordName = labels.planets?.[curr.lord] || curr.lord;
    const dasaWord = labels.ui?.dasaTab || "Dasa";
    dasaEl.textContent = `${lordName} ${dasaWord}`;
  }
}



function renderPranapada() {
  const labels = L();
  const p = state.chart.pranapada;
  document.getElementById("pranapadaBox").classList.toggle("hidden", !p);
  if (!p) return;
  document.getElementById("pranapadaValue").textContent =
    `${labels.rasi[p.rasi]} ${formatDMS(p.degree_in_sign)} \u00B7 ${labels.nakshatra[p.nakshatra]} \u00B7 ${labels.ui.houseWord} ${p.house}`;
}

function tithiName(t) {
  const labels = L();
  if (t.paksha_tithi === 15) return t.paksha === "shukla" ? labels.pournami : labels.amavasai;
  return `${labels.paksha[t.paksha]} ${labels.tithiNames[t.paksha_tithi - 1]}`;
}

function renderTithi() {
  const labels = L();
  const t = state.chart.tithi;
  document.getElementById("tithiBox").classList.toggle("hidden", !t);
  if (!t) return;
  document.getElementById("tithiValue").textContent = tithiName(t);
  document.getElementById("soonyamValue").textContent = t.soonya_rasis.length
    ? t.soonya_rasis
        .map((r) => {
          const lord = labels.planets[r.lord] || r.lord;
          const planets = r.planets.map((p) => labels.planets[p] || p).join(", ");
          return `${labels.rasi[r.rasi]} (${lord}) \u00B7 ${labels.ui.houseWord} ${r.house}` + (planets ? ` \u00B7 ${planets}` : "");
        })
        .join("; ")
    : labels.ui.soonyamNone;
}

function renderMudakku() {
  const labels = L();
  const m = state.chart.mudakku;
  document.getElementById("mudakkuBox").classList.toggle("hidden", !m);
  if (!m) return;
  const planet = (p) => labels.planets[p] || p;
  const planets = m.planets.map(planet).join(", ");
  document.getElementById("mudakkuValue").textContent =
    `${labels.rasi[m.rasi]} (${planet(m.rasi_lord)}) \u00B7 ${labels.nakshatra[m.nakshatra]} ${labels.ui.padaWord} ${m.pada} (${labels.ui.starLordWord} ${planet(m.star_lord)}) \u00B7 ${labels.ui.houseWord} ${m.house}` +
    (planets ? ` \u00B7 ${planets}` : "");
  document.getElementById("mudakkuLagnaNote").textContent = m.is_lagna ? labels.ui.mudakkuLagna : "";
}

function renderUpasana() {
  const labels = L();
  const select = document.getElementById("upasanaRasi");
  select.innerHTML = "";
  const blank = document.createElement("option");
  blank.value = "";
  blank.textContent = labels.ui.upasanaPick;
  select.appendChild(blank);
  labels.rasi.forEach((name, i) => {
    const opt = document.createElement("option");
    opt.value = String(i);
    opt.textContent = name;
    select.appendChild(opt);
  });
  select.value = state.upasanaRasi;

  const u = state.chart.upasana;
  document.getElementById("upasanaCalc").textContent = u
    ? labels.ui.upasanaCalc
        .replace("{planet}", labels.planets[u.planet])
        .replace("{from}", labels.rasi[u.planet_rasi])
        .replace("{rasi}", labels.rasi[u.rasi])
    : labels.ui.upasanaNoGender;
  document.getElementById("upasanaHint").textContent = labels.ui.upasanaHint;

  const show = () => {
    document.getElementById("upasanaValue").textContent =
      state.upasanaRasi === "" ? "" : UPASANA_DEIVAM[Number(state.upasanaRasi)][state.lang];
  };
  select.onchange = () => {
    state.upasanaRasi = select.value;
    show();
  };
  show();
}

function renderKaalaPakai() {
  const labels = L();
  const value = document.getElementById("kaalaPakaiValue");
  value.innerHTML = "";
  const entries = state.chart.kaala_pakai;
  if (entries.length === 0) value.textContent = labels.ui.kaalaPakaiNone;
  for (const e of entries) {
    const div = document.createElement("div");
    div.className = "kaala-pakai-entry";
    const head = document.createElement("span");
    head.className = "info-label";
    head.textContent = `${labels.planets[e.planet]}: ${labels.rasi[e.rasi]} \u00B7 ${labels.ui.houseWord} ${e.house}`;
    const effect = document.createElement("div");
    effect.className = "info-hint";
    effect.textContent = KAALA_PAKAI[e.planet].effect[state.lang];
    div.append(head, effect);
    value.appendChild(div);
  }

  const select = document.getElementById("kaalaPakaiPlanet");
  select.innerHTML = "";
  const blank = document.createElement("option");
  blank.value = "";
  blank.textContent = labels.ui.kaalaPakaiPick;
  select.appendChild(blank);
  for (const planet of Object.keys(KAALA_PAKAI)) {
    const opt = document.createElement("option");
    opt.value = planet;
    opt.textContent = labels.planets[planet];
    select.appendChild(opt);
  }
  select.value = state.kaalaPakaiPlanet;

  const show = () => {
    const k = KAALA_PAKAI[state.kaalaPakaiPlanet];
    document.getElementById("kaalaPakaiLookup").textContent = k
      ? `${labels.ui.kaalaPakaiRasis}: ${k.rasis.map((r) => labels.rasi[r]).join(", ")}`
      : "";
    document.getElementById("kaalaPakaiEffect").textContent = k ? k.effect[state.lang] : "";
  };
  select.onchange = () => {
    state.kaalaPakaiPlanet = select.value;
    show();
  };
  show();
}

function renderInduLagna() {
  const labels = L();
  const rasiName = labels.rasi[state.chart.indu_lagna_rasi];
  const lordName = labels.planets[state.chart.indu_lagna_lord] || state.chart.indu_lagna_lord;
  document.getElementById("induLagnaValue").textContent = `${rasiName} (${lordName})`;
}

function renderVargaSelect() {
  const select = document.getElementById("vargaSelect");
  select.innerHTML = "";
  const options = ["D1", ...Object.keys(state.chart.vargas)];
  for (const v of options) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = L().vargas[v] || v;
    select.appendChild(opt);
  }
  select.value = state.varga;
  select.onchange = () => {
    state.varga = select.value;
    renderGrid();
  };
}

function chartOutFor(varga) {
  return varga === "D1" ? state.chart.d1 : state.chart.vargas[varga];
}

function renderGrid() {
  const chart = chartOutFor(state.varga);
  const isD1 = state.varga === "D1";
  // Thithi Soonyam is sign-based and read from the D1 chart only
  const soonyaRasis = new Set(isD1 && state.chart.tithi ? state.chart.tithi.soonya_rasis.map((r) => r.rasi) : []);
  document.getElementById("soonyamLegend").classList.toggle("hidden", soonyaRasis.size === 0);
  drawGrid(document.getElementById("chartGrid"), chart, {
    // Gulika/Mandi are only computed for D1, not per-varga
    extraPlanets: isD1 ? [state.chart.gulika, state.chart.mandi] : [],
    soonyaRasis,
    mudakkuRasi: isD1 && state.chart.mudakku ? state.chart.mudakku.rasi : null,
    centerLabel: L().vargas[state.varga] || state.varga,
  });
}

// Draws a South Indian chart into `grid`: used for the birth chart and the Prasannam chart.
function drawGrid(grid, chart, { extraPlanets = [], soonyaRasis = new Set(), mudakkuRasi = null, centerLabel = "" } = {}) {
  grid.innerHTML = "";
  const labels = L();

  const rasiToPlanets = {};
  for (const g of [...Object.values(chart.grahas), ...extraPlanets]) {
    (rasiToPlanets[g.rasi] = rasiToPlanets[g.rasi] || []).push(g);
  }

  for (const pos of GRID_POSITIONS) {
    const cell = document.createElement("div");
    cell.className = "grid-cell";
    if (pos.rasi === chart.lagna_rasi) cell.classList.add("lagna");
    if (soonyaRasis.has(pos.rasi)) cell.classList.add("soonyam");
    cell.style.gridRow = pos.row;
    cell.style.gridColumn = pos.col;

    const nameDiv = document.createElement("div");
    nameDiv.className = "rasi-name";
    nameDiv.textContent = labels.rasi[pos.rasi];
    cell.appendChild(nameDiv);
    if (mudakkuRasi === pos.rasi) {
      const tag = document.createElement("div");
      tag.className = "mudakku-tag";
      tag.textContent = labels.ui.mudakkuTag;
      cell.appendChild(tag);
    }

    const planetsDiv = document.createElement("div");
    planetsDiv.className = "planets";
    for (const g of rasiToPlanets[pos.rasi] || []) {
      const span = document.createElement("span");
      const isRetrogradeEligible = g.retrograde && !NODES_NOT_MARKED_RETROGRADE.has(g.name);
      span.textContent = (labels.planetAbbr[g.name] || g.name) + (isRetrogradeEligible ? " (R)" : "");
      if (UPAGRAHA_NAMES.has(g.name)) span.classList.add("upagraha");
      planetsDiv.appendChild(span);
    }
    cell.appendChild(planetsDiv);
    grid.appendChild(cell);
  }

  const center = document.createElement("div");
  center.className = "grid-center";
  const ganeshaImg = document.createElement("img");
  ganeshaImg.src = "ganesha.svg";
  ganeshaImg.alt = "";
  ganeshaImg.className = "ganesha-icon";
  const label = document.createElement("div");
  label.textContent = centerLabel;
  center.append(ganeshaImg, label);
  grid.appendChild(center);
}

function isCurrentPeriod(period) {
  const now = new Date();
  return now >= new Date(period.start) && now < new Date(period.end);
}

async function fetchDasaChildren(period, nextLevel) {
  const res = await fetch("/api/dasa/expand", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lord: period.lord, start: period.start, end: period.end, next_level: nextLevel }),
  });
  return res.json();
}

async function expandRow(tr, period, depth) {
  const next = nextDasaLevel(period.level);
  if (!next || tr.dataset.expanded === "true") return [];
  const children = await fetchDasaChildren(period, next);
  let anchor = tr;
  const childRows = [];
  for (const child of children) {
    const childRow = makeDasaRow(child, depth + 1);
    childRow.dataset.parentDepth = depth;
    anchor.after(childRow);
    anchor = childRow;
    childRows.push({ row: childRow, period: child });
  }
  tr.dataset.expanded = "true";
  return childRows;
}

function renderDasaTable() {
  const tbody = document.getElementById("dasaBody");
  tbody.innerHTML = "";
  const rows = [];
  for (const period of state.chart.mahadasas) {
    const tr = makeDasaRow(period, 0);
    tbody.appendChild(tr);
    rows.push({ row: tr, period });
  }
  autoExpandCurrentChain(rows, 0);
}

// Reveals the currently-active Mahadasa -> Antardasa -> Antaram (Pratyantardasa)
// chain automatically, so the periods that matter right now don't require clicking.
async function autoExpandCurrentChain(rows, depth) {
  if (depth >= 2) return; // stop after Antaram (mahadasa=0, antardasa=1, antaram=2)
  const current = rows.find(({ period }) => isCurrentPeriod(period));
  if (!current) return;
  current.row.classList.add("current-period");
  const childRows = await expandRow(current.row, current.period, depth);
  await autoExpandCurrentChain(childRows, depth + 1);
}

function makeDasaRow(period, depth) {
  const tr = document.createElement("tr");
  tr.className = depth === 0 ? "expandable" : `expandable child-row depth-${depth}`;
  tr.dataset.expanded = "false";
  if (depth > 0) tr.style.setProperty("--dasa-depth", depth);
  if (isCurrentPeriod(period)) tr.classList.add("current-period");

  const lordTd = document.createElement("td");
  const lordSpan = document.createElement("span");
  lordSpan.textContent = L().dasaLords[period.lord] || period.lord;
  const levelSpan = document.createElement("span");
  levelSpan.className = "dasa-level-tag";
  levelSpan.textContent = L().dasaLevels[period.level] || period.level;
  lordTd.append(lordSpan, levelSpan);
  const startTd = document.createElement("td");
  startTd.textContent = fmtDate(period.start);
  const endTd = document.createElement("td");
  endTd.textContent = fmtDate(period.end);
  tr.append(lordTd, startTd, endTd);

  const next = nextDasaLevel(period.level);
  if (next) {
    tr.addEventListener("click", async () => {
      if (tr.dataset.expanded === "true") {
        collapseChildren(tr);
        tr.dataset.expanded = "false";
        return;
      }
      await expandRow(tr, period, depth);
    });
  }
  return tr;
}

function collapseChildren(parentRow) {
  let next = parentRow.nextElementSibling;
  while (next && Number(next.className.match(/depth-(\d+)/)?.[1] || 0) > 0) {
    const toRemove = next;
    next = next.nextElementSibling;
    toRemove.remove();
  }
}

// The worked count shown under yogas whose rule is a count, so it can be checked by eye.
function yogaWorking(name, triggered) {
  const labels = L();
  const d1 = state.chart.d1;
  if (name === "Soorya Chandraadhi Yoga") {
    const sunHouse = d1.grahas.Sun.house;
    return [
      labels.ui.sooryaChandraadhiCalc
        .replaceAll("{house}", sunHouse)
        .replace("{target}", labels.rasi[sunHouse - 1])
        .replace("{moon}", labels.rasi[d1.grahas.Moon.rasi]),
    ];
  }
  if (name === "Jeevanam Yoga") {
    const n = d1.grahas.Moon.rasi + 1;
    const planets = d1.houses[n].map((p) => labels.planets[p]).join(", ");
    const lines = [
      labels.ui.jeevanamCalc
        .replaceAll("{n}", n)
        .replace("{moon}", labels.rasi[d1.grahas.Moon.rasi])
        .replace("{target}", labels.rasi[(d1.lagna_rasi + n - 1) % 12])
        .replace("{planets}", planets || labels.ui.noneWord),
    ];
    if (triggered) lines.push(labels.ui.jeevanamEarning.replace("{planets}", planets));
    return lines;
  }
  return [];
}

function renderYogas() {
  const ul = document.getElementById("yogaList");
  ul.innerHTML = "";
  const labels = L();
  const present = [];
  for (const y of state.chart.yogas) {
    const displayName = labels.yogas[y.name] || y.name;
    const li = document.createElement("li");
    if (y.triggered) {
      li.classList.add(INAUSPICIOUS_YOGAS.has(y.name) ? "triggered-warning" : "triggered");
      present.push(displayName);
    }
    const head = document.createElement("div");
    head.className = "yoga-head";
    const title = document.createElement("strong");
    title.textContent = displayName;
    const tag = document.createElement("span");
    tag.className = "yoga-tag " + (y.triggered ? "yoga-tag-present" : "yoga-tag-absent");
    tag.textContent = y.triggered ? labels.ui.yogaPresent : labels.ui.yogaAbsent;
    head.append(title, tag);
    const desc = document.createElement("div");
    desc.className = "yoga-desc";
    desc.textContent = y.description;
    li.append(head, desc);
    for (const line of yogaWorking(y.name, y.triggered)) {
      const calc = document.createElement("div");
      calc.className = "yoga-moon-note";
      calc.textContent = line;
      li.appendChild(calc);
    }
    if (y.from_moon) {
      const moonNote = document.createElement("div");
      moonNote.className = "yoga-moon-note";
      moonNote.textContent = labels.ui.yogaFromMoon;
      li.appendChild(moonNote);
    }
    ul.appendChild(li);
  }
  document.getElementById("yogaSummary").textContent = present.length
    ? `${labels.ui.yogaSummary}: ${present.join(", ")}`
    : labels.ui.noYogas;
}

function renderTaraBalam() {
  const tbody = document.getElementById("taraBody");
  tbody.innerHTML = "";
  const labels = L();
  for (const t of state.chart.tara_balam) {
    const tr = document.createElement("tr");
    const c1 = document.createElement("td");
    c1.textContent = t.count;
    const c2 = document.createElement("td");
    c2.textContent = labels.nakshatra[t.nakshatra];
    const c3 = document.createElement("td");
    c3.textContent = labels.taraCategories[t.category];
    const c4 = document.createElement("td");
    c4.textContent = t.quality;
    c4.className = "quality-" + t.quality;
    tr.append(c1, c2, c3, c4);
    tbody.appendChild(tr);
  }
}

function renderGrahaDetails() {
  const tbody = document.getElementById("detailsBody");
  tbody.innerHTML = "";
  const labels = L();

  const kaalaPakai = state.chart.kaala_pakai;
  document.getElementById("kaalaPakaiSummary").textContent = kaalaPakai.length
    ? `${labels.ui.kaalaPakai}: ` +
      kaalaPakai.map((e) => `${labels.planets[e.planet]} (${labels.rasi[e.rasi]})`).join("  \u00B7  ")
    : labels.ui.kaalaPakaiNone;
  const inKaalaPakai = new Set(kaalaPakai.map((e) => e.planet));

  const rows = [...Object.values(state.chart.d1.grahas), state.chart.gulika, state.chart.mandi];
  for (const g of rows) {
    const tr = document.createElement("tr");
    if (inKaalaPakai.has(g.name)) tr.className = "kaala-pakai";
    const isRetrogradeEligible = g.retrograde && !NODES_NOT_MARKED_RETROGRADE.has(g.name);
    const cells = [
      (labels.planets[g.name] || g.name) + (isRetrogradeEligible ? " (R)" : ""),
      labels.rasi[g.rasi],
      labels.planets[g.rasi_lord] || g.rasi_lord,
      formatDMS(g.longitude),
      formatDMS(g.degree_in_sign),
      labels.nakshatra[g.nakshatra],
      g.pada,
      labels.planets[g.star_lord] || g.star_lord,
      g.pushkara_navamsa
        ? `\u2713 ${labels.nakshatra[g.nakshatra]} ${g.pada}` +
          (isVargottamaPada([g.nakshatra, g.pada]) ? ` (${labels.ui.vargottamaWord})` : "")
        : "–",
      inKaalaPakai.has(g.name) ? labels.ui.kaalaPakaiYes : "–",
    ];
    for (const value of cells) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
}

function renderDignity() {
  const labels = L();
  const entries = state.chart.dignities || [];
  const table = document.getElementById("dignityTable");
  const tbody = document.getElementById("dignityBody");
  tbody.innerHTML = "";
  const summary = document.getElementById("dignitySummary");
  if (entries.length === 0) {
    summary.textContent = labels.ui.dignityNone;
    table.classList.add("hidden");
    return;
  }
  summary.textContent = entries
    .map((e) => `${labels.planets[e.planet] || e.planet}: ${e.state === "ucham" ? labels.ui.dignityUcham : labels.ui.dignityNeecham}`)
    .join("  \u00B7  ");
  table.classList.remove("hidden");
  for (const e of entries) {
    const tr = document.createElement("tr");
    tr.className = e.state === "ucham" ? "dignity-ucham" : "dignity-neecham";
    const cells = [
      labels.planets[e.planet] || e.planet,
      e.state === "ucham" ? labels.ui.dignityUcham : labels.ui.dignityNeecham,
      labels.rasi[e.rasi],
      formatDMS(e.degree_in_sign),
      e.deep_degree === null ? "\u2013" : formatDMS(e.deep_degree),
      e.degrees_from_deep === null ? "\u2013" : formatDMS(e.degrees_from_deep),
    ];
    for (const value of cells) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
}

// Rahu and Ketu change rasi together, so a Rahu peyarchi is shown as both.
function peyarchiPlanetName(planet) {
  return planet === "Rahu" ? L().ui.rahuKetu : L().planets[planet];
}

function peyarchiRasiName(p) {
  const rasi = L().rasi;
  return p.planet === "Rahu" ? `${rasi[p.rasi]} / ${rasi[(p.rasi + 6) % 12]}` : rasi[p.rasi];
}

// The peyarchi of each planet that is running now: its latest one that has started.
function currentPeyarchis() {
  const now = new Date();
  const current = new Map();
  for (const p of state.chart.peyarchis) {
    if (new Date(p.when) <= now) current.set(p.planet, p);
  }
  return current;
}

function renderPeyarchi() {
  const labels = L();
  const peyarchis = state.chart.peyarchis;
  const current = currentPeyarchis();

  document.getElementById("peyarchiSummary").textContent = current.size
    ? `${labels.ui.peyarchiNow}: ` +
      [...current.values()].map((p) => `${peyarchiPlanetName(p.planet)} ${peyarchiRasiName(p)} \u2013 ${labels.moorthi[p.moorthi]}`).join("  \u00B7  ")
    : "";
  document.getElementById("peyarchiNote").textContent =
    labels.ui.peyarchiNote.replace("{janma}", labels.rasi[state.chart.d1.grahas.Moon.rasi]);

  const select = document.getElementById("peyarchiFilter");
  select.innerHTML = "";
  for (const planet of ["", "Saturn", "Jupiter", "Rahu"]) {
    const opt = document.createElement("option");
    opt.value = planet;
    opt.textContent = planet ? peyarchiPlanetName(planet) : labels.ui.peyarchiAll;
    select.appendChild(opt);
  }
  select.value = state.peyarchiPlanet;
  select.onchange = () => {
    state.peyarchiPlanet = select.value;
    renderPeyarchi();
  };

  const tbody = document.getElementById("peyarchiBody");
  tbody.innerHTML = "";
  const currentSet = new Set(current.values());
  for (const p of peyarchis) {
    if (state.peyarchiPlanet && p.planet !== state.peyarchiPlanet) continue;
    const tr = document.createElement("tr");
    if (currentSet.has(p)) tr.className = "current-period";
    const kind = p.kind === "retrograde" ? ` ${labels.ui.peyarchiRetro}` : p.kind === "re-entry" ? ` ${labels.ui.peyarchiReentry}` : "";
    const cells = [
      [peyarchiPlanetName(p.planet)],
      [peyarchiRasiName(p) + kind],
      [p.when.slice(0, 16).replace("T", " "), p.in_effect_at_start ? labels.ui.peyarchiCarried : ""],
      [labels.rasi[p.moon_rasi]],
      [String(p.count)],
      [labels.moorthi[p.moorthi], labels.moorthiResult[p.moorthi]],
    ];
    cells.forEach(([main, sub], i) => {
      const td = document.createElement("td");
      td.textContent = main;
      if (sub) {
        const span = document.createElement("span");
        span.className = "peyarchi-sub";
        span.textContent = sub;
        td.appendChild(span);
      }
      if (i === 5) td.className = `moorthi-${p.moorthi}`;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  }
}

function renderDrekkanaLords() {
  const labels = L();
  const entries = state.chart.drekkana_lords;
  const weak = entries.filter((e) => e.weakened);
  document.getElementById("drekkanaSummary").textContent = weak.length
    ? `${labels.ui.drekkanaSummary}: ` +
      weak.map((e) => `${labels.planets[e.planet]} (${labels.planets[e.controller]} ${e.count})`).join("  \u00B7  ")
    : labels.ui.drekkanaNone;
  const pariharam = document.getElementById("drekkanaPariharam");
  pariharam.textContent = labels.ui.drekkanaPariharam;
  pariharam.classList.toggle("hidden", weak.length === 0);

  const tbody = document.getElementById("drekkanaBody");
  tbody.innerHTML = "";
  for (const e of entries) {
    const tr = document.createElement("tr");
    if (e.weakened) tr.className = "drekkana-weak";
    const result = e.weakened
      ? labels.ui.drekkanaWeak.replace("{n}", e.count)
      : e.controller === e.planet ? labels.ui.drekkanaOwn : labels.ui.drekkanaOk;
    const cells = [
      labels.planets[e.planet],
      labels.rasi[e.rasi],
      formatDMS(e.degree_in_sign),
      `${labels.ui.drekkanaOrdinal[e.drekkana - 1]} (${labels.rasi[e.drekkana_rasi]})`,
      labels.planets[e.controller],
      labels.rasi[e.controller_rasi],
      String(e.count),
      result,
    ];
    for (const value of cells) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
}

// "9: father, fortune, dharma" for each house a planet rules; Rahu and Ketu get the house they sit in.
function aathipathyamLines(e) {
  const labels = L();
  if (!e.houses_ruled || e.houses_ruled.length === 0) {
    const template = labels.ui?.sashtashtagamNoLordship || "{house} (sits here; rules no sign)";
    return [template.replace("{house}", e.d1_house)];
  }
  const meanings = labels.ui?.houseMeanings || [];
  return e.houses_ruled.map((h) => `${h}: ${meanings[h - 1] || ""}`);
}

function renderSashtashtagam() {
  const labels = L();
  const entries = state.chart.navamsa_sashtashtagam;
  const flagged = entries.filter((e) => e.flagged);
  document.getElementById("sashtashtagamSummary").textContent = flagged.length
    ? `${labels.ui.sashtashtagamSummary}: ` +
      flagged
        .map((e) => {
          const next = upcomingWindows(e)[0];
          const nextText = next
            ? ` \u2013 ${pointText(e, labels.ui.sashtashtagamNextShort).replace("{when}", fmtWindow(next))}`
            : "";
          return `${labels.planets[e.planet]} (${aathipathyamLines(e).join("; ")})${nextText}`;
        })
        .join("  \u00B7  ")
    : labels.ui.sashtashtagamNone;
  const pariharam = document.getElementById("sashtashtagamPariharam");
  pariharam.textContent = labels.ui.drekkanaPariharam;
  pariharam.classList.toggle("hidden", flagged.length === 0);

  const tbody = document.getElementById("sashtashtagamBody");
  tbody.innerHTML = "";
  for (const e of entries) {
    const tr = document.createElement("tr");
    if (e.flagged) tr.className = "sashtashtagam-flag";
    const cells = [
      labels.planets[e.planet],
      labels.rasi[e.d1_rasi],
      String(e.d1_house),
      labels.rasi[e.d9_rasi],
      String(e.count),
      aathipathyamLines(e),
      e.flagged ? labels.ui.sashtashtagamWeak.replace("{n}", e.count) : labels.ui.sashtashtagamOk,
    ];
    for (const value of cells) {
      const td = document.createElement("td");
      if (Array.isArray(value)) {
        for (const line of value) {
          const span = document.createElement("span");
          span.className = "house-line";
          span.textContent = line;
          td.appendChild(span);
        }
      } else {
        td.textContent = value;
      }
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  renderSashtashtagamTiming(flagged);
}

function fmtDateTime(iso) {
  return iso.slice(0, 16).replace("T", " ");
}

function fmtWindow(w) {
  return `${fmtDateTime(w.start)} \u2192 ${fmtDateTime(w.end)}`;
}

function fmtDegMin(deg) {
  const whole = Math.floor(deg + 1e-9);
  const minutes = Math.round((deg - whole) * 60);
  return `${whole}\u00B0${String(minutes).padStart(2, "0")}'`;
}

// Fills {planet} {star} {pada} {rasi} {from} {to} for a flagged planet's navamsa point.
function pointText(e, template) {
  const labels = L();
  const p = e.point;
  const rasi = Math.floor(p.start / 30);
  return template
    .replaceAll("{planet}", labels.planets[e.planet])
    .replace("{star}", labels.nakshatra[p.nakshatra])
    .replace("{pada}", p.pada)
    .replace("{rasi}", labels.rasi[rasi])
    .replace("{from}", fmtDegMin(p.start - rasi * 30))
    .replace("{to}", fmtDegMin(p.end - rasi * 30));
}

// Periods not yet over, soonest first.
function upcomingWindows(e) {
  const now = new Date();
  return e.transits.filter((w) => new Date(w.end) >= now);
}

function renderSashtashtagamTiming(flagged) {
  const labels = L();
  const container = document.getElementById("sashtashtagamTiming");
  container.innerHTML = "";
  if (flagged.length === 0) return;

  const title = document.createElement("h3");
  title.className = "timing-title";
  title.textContent = labels.ui.sashtashtagamTimingTitle;
  container.appendChild(title);

  const now = new Date();
  const windowLine = (w) => {
    const li = document.createElement("li");
    const running = new Date(w.start) <= now && now <= new Date(w.end);
    li.textContent = fmtWindow(w) + (running ? ` (${labels.ui.sashtashtagamNowTag})` : "");
    if (running) li.className = "timing-now";
    return li;
  };

  for (const e of flagged) {
    const block = document.createElement("div");
    block.className = "timing-block";
    const intro = document.createElement("div");
    intro.className = "timing-intro";
    if (e.transits.length === 0) {
      intro.textContent = pointText(e, labels.ui.sashtashtagamNoTransit);
      block.appendChild(intro);
      container.appendChild(block);
      continue;
    }
    intro.textContent = pointText(e, labels.ui.sashtashtagamTimingIntro);
    block.appendChild(intro);

    const upcoming = upcomingWindows(e);
    const next = document.createElement("div");
    next.className = "info-label";
    next.textContent = labels.ui.sashtashtagamUpcoming;
    block.appendChild(next);
    const ul = document.createElement("ul");
    ul.className = "timing-list";
    if (upcoming.length === 0) {
      const li = document.createElement("li");
      li.textContent = labels.ui.sashtashtagamNoneLeft;
      ul.appendChild(li);
    }
    for (const w of upcoming.slice(0, 3)) ul.appendChild(windowLine(w));
    block.appendChild(ul);

    const all = document.createElement("details");
    all.className = "timing-all";
    const summary = document.createElement("summary");
    summary.textContent = labels.ui.sashtashtagamAllPeriods.replace("{n}", e.transits.length);
    all.appendChild(summary);
    const allList = document.createElement("ul");
    allList.className = "timing-list";
    for (const w of e.transits) allList.appendChild(windowLine(w));
    all.appendChild(allList);
    block.appendChild(all);
    container.appendChild(block);
  }
}

// --- Init ---

populateTobMinutes();
applyLanguage();
loadSavedCharts();
showPage("home");
