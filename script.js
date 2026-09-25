// TerpBites: reads real UMD dining data from data/dining.js (built by scripts/update_data.py).
(function () {
  const D = window.TERPBITES_DATA;
  const $ = (id) => document.getElementById(id);

  if (!D) {
    $("demo-summary").textContent = "Dining data didn't load. Run scripts/update_data.py to create data/dining.js.";
    return;
  }

  // ---------- helpers ----------
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pad = (n) => String(n).padStart(2, "0");
  const isoOf = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const dateOf = (iso) => { const [y, m, d] = iso.split("-").map(Number); return new Date(y, m - 1, d); };
  const addDays = (iso, n) => { const d = dateOf(iso); d.setDate(d.getDate() + n); return isoOf(d); };
  const money = (n) => `$${n.toFixed(2)}`;

  function clock(mins) {
    mins = ((mins % 1440) + 1440) % 1440;
    const h = Math.floor(mins / 60), m = mins % 60;
    const h12 = h % 12 === 0 ? 12 : h % 12;
    return `${h12}${m ? ":" + pad(m) : ""} ${h < 12 ? "AM" : "PM"}`;
  }

  function dayLabel(iso, todayIso) {
    if (iso === todayIso) return "Today";
    if (iso === addDays(todayIso, 1)) return "Tomorrow";
    return dateOf(iso).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  }

  // Walking time between two points: straight-line distance, padded for paths, at ~80 m/min.
  function walkMinutes(a, b) {
    const R = 6371000, rad = Math.PI / 180;
    const dLat = (b.lat - a.lat) * rad, dLng = (b.lng - a.lng) * rad;
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLng / 2) ** 2;
    const meters = 2 * R * Math.asin(Math.sqrt(h));
    return Math.max(1, Math.ceil((meters * 1.3) / 80));
  }

  // Rough wait estimates by type of place (to be replaced with research data).
  const WAIT = { "Dining hall": 5, "Café": 4, "Fast food": 7, "Fast casual": 8, "Grill": 8, "Market": 2, "Ice cream": 4 };
  const QUICK = new Set(["Fast food", "Fast casual", "Grill", "Ice cream"]);

  const ICON_BY_ID = {
    "union-pizza": "🍕", "north-market-pizza": "🍕", "taco-bell": "🌮", "stamp-subway": "🥪", "kirwan-subway": "🥪",
    qdoba: "🌯", panera: "🥖", samovar: "🍜", "maryland-dairy": "🍦", "chick-fil-a": "🍗", breakpoint: "🥗", sneakers: "🥤",
  };
  const ICON_BY_KIND = { "Dining hall": "🍽️", "Café": "☕", "Fast food": "🍔", "Fast casual": "🌯", "Grill": "🍔", "Market": "🛒", "Ice cream": "🍦" };
  const TINT_BY_KIND = { "Dining hall": "var(--mango-soft)", "Café": "var(--berry-soft)", "Market": "var(--mint-soft)" };
  const iconFor = (v) => ICON_BY_ID[v.id] || ICON_BY_KIND[v.kind] || "🍴";
  const tintFor = (v) => TINT_BY_KIND[v.kind] || "var(--wash)";

  // ---------- hours ----------
  // Returns the range covering minute t on `iso`, including late-night ranges from the day before.
  function rangeAt(v, iso, t) {
    const today = v.hours[iso] || [];
    for (const r of today) if (t >= r.open && t < r.close) return { ...r, closeAt: r.close };
    const prev = v.hours[addDays(iso, -1)] || [];
    for (const r of prev) if (t + 1440 >= r.open && t + 1440 < r.close) return { ...r, closeAt: r.close - 1440 };
    return null;
  }

  function nextOpening(v, iso, t) {
    const today = v.hours[iso];
    if (today === null) return { tbd: true };
    for (const r of today || []) if (r.open > t) return { at: r.open, meal: r.meal };
    return null;
  }

  function doorPrice(meal) {
    return meal && D.doorPrices[meal] ? `${money(D.doorPrices[meal])} at the door` : "";
  }

  const todayIso = isoOf(new Date());
  const hourDates = [...new Set(D.venues.flatMap((v) => Object.keys(v.hours)))].sort();
  const hasToday = hourDates.includes(todayIso);
  const updated = new Date(D.updated);
  const updatedLabel = updated.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });

  $("footer-updated").textContent = `Last updated ${updatedLabel}.`;
  $("data-note").textContent = hasToday
    ? `Live data: hours and menus from UMD Dining Services, updated ${updatedLabel}.`
    : `Showing UMD Dining data from ${updatedLabel}. Run scripts/update_data.py for today's hours.`;
  document.querySelectorAll("[data-door]").forEach((el) => {
    const p = D.doorPrices[el.dataset.door];
    if (p) el.textContent = money(p);
  });

  // ---------- hero phone ----------
  const MALL = { lat: 38.98599, lng: -76.94227 };

  function renderPhone() {
    const now = new Date();
    const t = now.getHours() * 60 + now.getMinutes();
    $("phone-clock").textContent = clock(t).replace(" AM", "").replace(" PM", "");

    const open = D.venues
      .map((v) => ({ v, r: rangeAt(v, todayIso, t), walk: walkMinutes(MALL, v) }))
      .filter((x) => x.r)
      .sort((a, b) => a.walk - b.walk);

    const total = D.venues.length;
    $("phone-open-count").innerHTML = `${open.length}<small>open</small>`;
    document.querySelector(".ring-fill").style.setProperty("--ring-to", 119.4 * (1 - open.length / total));
    $("float-open").textContent = open.length ? `${open.length} places open right now` : "Everything's closed right now";

    const items = Object.values(D.menus).reduce((n, days) => n + (days[todayIso] || []).reduce((m, meal) => m + meal.stations.reduce((k, s) => k + s.items.length, 0), 0), 0);
    $("float-items").textContent = items ? `${items.toLocaleString()} items` : "Today's";

    if (!open.length) {
      $("phone-spots").innerHTML = `<li><span class="spot-icon" style="--c: var(--wash)">🌙</span><span class="spot-name">Nothing open nearby<small>Check back in the morning</small></span><span class="spot-time">–</span></li>`;
      return;
    }
    $("phone-spots").innerHTML = open.slice(0, 3).map(({ v, r, walk }) => {
      const left = r.closeAt - t;
      const soon = left <= 30;
      const meta = soon ? `Closes in ${left} min` : `Open until ${clock(r.closeAt)}`;
      return `<li class="${soon ? "spot-warn" : ""}">
        <span class="spot-icon" style="--c: ${tintFor(v)}">${iconFor(v)}</span>
        <span class="spot-name">${esc(v.name)}<small>${meta}</small></span>
        <span class="spot-time">${walk} min</span>
      </li>`;
    }).join("");
  }

  // ---------- finder ----------
  const fromSel = $("from"), toSel = $("to"), startIn = $("start"), daySel = $("day"), range = $("break");
  const buildings = D.buildings;

  const optionHtml = buildings.map((b, i) => `<option value="${i}">${esc(b.name)}${b.code ? ` (${esc(b.code)})` : ""}</option>`).join("");
  fromSel.innerHTML = optionHtml;
  toSel.innerHTML = optionHtml;
  const findBuilding = (re) => Math.max(0, buildings.findIndex((b) => re.test(b.name)));
  fromSel.value = findBuilding(/^McKeldin Library/);
  toSel.value = findBuilding(/^Brendan Iribe/);

  daySel.innerHTML = hourDates.map((iso) => `<option value="${iso}">${dayLabel(iso, todayIso)}</option>`).join("");
  daySel.value = hasToday ? todayIso : hourDates[0];

  const now = new Date();
  const nowRounded = Math.ceil((now.getHours() * 60 + now.getMinutes()) / 5) * 5;
  startIn.value = `${pad(Math.floor(nowRounded / 60) % 24)}:${pad(nowRounded % 60)}`;

  let showAll = false;

  function evaluate(v, from, to, iso, t, mins) {
    const there = walkMinutes(from, v);
    const back = walkMinutes(v, to);
    const wait = WAIT[v.kind] ?? 5;
    const need = there + wait + back;
    const arrive = t + there;
    const r = rangeAt(v, iso, arrive);
    const base = { v, there, back, wait, need };

    if (!r) {
      const next = nextOpening(v, iso, arrive);
      if (next && next.tbd) return { ...base, state: "closed", note: "Hours not posted yet" };
      if (next) return { ...base, state: "closed", note: `Opens at ${clock(next.at)}${next.meal ? ` for ${next.meal.toLowerCase()}` : ""}` };
      return { ...base, state: "closed", note: "Closed for the rest of the day" };
    }
    if (arrive + wait > r.closeAt) return { ...base, state: "closing", r, note: `Closes at ${clock(r.closeAt)}, before you'd get served` };
    if (need > mins) return { ...base, state: "far", r, note: `Needs ${need} min round trip` };
    return { ...base, state: "fits", r, spare: mins - need };
  }

  function renderFinder() {
    const mins = Number(range.value);
    $("break-out").textContent = `${mins} min`;
    const from = buildings[fromSel.value], to = buildings[toSel.value];
    const iso = daySel.value;
    const [hh, mm] = (startIn.value || "12:00").split(":").map(Number);
    const t = hh * 60 + mm;
    const kind = document.querySelector('input[name="kind"]:checked').value;

    const rows = D.venues
      .filter((v) => kind === "all" || (kind === "quick" ? QUICK.has(v.kind) : v.kind === kind))
      .map((v) => evaluate(v, from, to, iso, t, mins));

    const order = { fits: 0, far: 1, closing: 2, closed: 3 };
    rows.sort((a, b) => order[a.state] - order[b.state] || a.need - b.need);
    const fits = rows.filter((r) => r.state === "fits");
    const rest = rows.filter((r) => r.state !== "fits");

    const when = `${dayLabel(iso, todayIso).toLowerCase()} at ${clock(t)}`;
    $("demo-summary").innerHTML = fits.length
      ? `<strong>${fits.length} of ${rows.length}</strong> places fit a ${mins}-minute break ${esc(when)}.`
      : `Nothing fits a ${mins}-minute break ${esc(when)}. Try a longer break or a different time.`;

    const visible = showAll ? rows : fits.length ? fits : rest.slice(0, 4);
    $("demo-list").innerHTML = visible.map(rowHtml).join("");

    const hidden = rows.length - visible.length;
    const btn = $("show-closed");
    btn.hidden = hidden <= 0 && !showAll;
    btn.textContent = showAll ? "Only show places that fit" : `Show ${hidden} more that don't fit`;
  }

  function rowHtml(x) {
    const { v } = x;
    let meta = `${esc(v.kind)} in ${esc(v.building)}`;
    let badge;
    if (x.state === "fits") {
      const extra = x.r.meal ? ` · ${esc(x.r.meal)}${doorPrice(x.r.meal) ? `, ${doorPrice(x.r.meal)}` : ""}` : "";
      meta += `<br>Open until ${clock(x.r.closeAt)}${extra}`;
      badge = `<span class="d-badge">${x.spare} min to spare</span>`;
    } else {
      meta += `<br>${esc(x.note)}`;
      badge = `<span class="d-badge">${x.state === "far" ? "Too far" : "Closed"}</span>`;
    }
    return `<li class="${x.state === "fits" ? "" : "out"}">
      <span class="d-icon" style="background:${tintFor(v)}" aria-hidden="true">${iconFor(v)}</span>
      <span class="d-name">${esc(v.name)}
        <span class="d-meta">${meta}</span>
        <span class="d-trip">${x.there} min walk · ~${x.wait} min wait · ${x.back} min to class</span>
      </span>
      ${badge}
    </li>`;
  }

  [fromSel, toSel, startIn, daySel].forEach((el) => el.addEventListener("change", renderFinder));
  range.addEventListener("input", renderFinder);
  document.querySelectorAll('input[name="kind"]').forEach((el) => el.addEventListener("change", () => { showAll = false; renderFinder(); }));
  $("show-closed").addEventListener("click", () => { showAll = !showAll; renderFinder(); });

  // ---------- menus ----------
  const halls = D.venues.filter((v) => v.hasMenu && D.menus[v.id]);
  const state = { 
    hall: halls[0]?.id, 
    day: null, 
    meal: null, 
    diet: "all", 
    expanded: new Set(),
    openStations: new Set()};
  const menuDates = [...new Set(halls.flatMap((h) => Object.keys(D.menus[h.id])))].sort();
  state.day = menuDates.includes(todayIso) ? todayIso : menuDates[0];

  $("menu-day").innerHTML = menuDates.map((iso) => `<option value="${iso}">${dayLabel(iso, todayIso)}</option>`).join("");
  $("menu-day").value = state.day;

  function segHtml(items, active, attr) {
    return items.map((it) => `<button type="button" role="tab" aria-selected="${it.value === active}" data-${attr}="${esc(it.value)}">${esc(it.label)}</button>`).join("");
  }

  function currentMeal(hall, iso, meals) {
    if (iso !== todayIso) return meals[0];
    const now = new Date();
    const t = now.getHours() * 60 + now.getMinutes();
    const ranges = hall.hours[iso] || [];
    const live = ranges.find((r) => t >= r.open && t < r.close) || ranges.find((r) => r.open > t);
    return (live && meals.find((m) => m === live.meal)) || meals[meals.length - 1];
  }

  function renderMenus() {
    const hall = halls.find((h) => h.id === state.hall);
    $("hall-tabs").innerHTML = segHtml(halls.map((h) => ({ value: h.id, label: h.name.replace(" Dining Hall", "") })), state.hall, "hall");

    const day = (D.menus[hall.id][state.day] || []);
    const meals = day.map((m) => m.meal);
    if (!meals.includes(state.meal)) state.meal = currentMeal(hall, state.day, meals);
    $("meal-tabs").innerHTML = segHtml(meals.map((m) => ({ value: m, label: m })), state.meal, "meal");

    const range = (hall.hours[state.day] || []).find((r) => r.meal === state.meal);
    const bits = [];
    if (range) bits.push(`<strong>${esc(state.meal)}</strong> ${clock(range.open)} to ${clock(range.close)}`);
    if (doorPrice(state.meal)) bits.push(doorPrice(state.meal));
    bits.push(esc(hall.building));
    if (state.day === todayIso && range) {
      const n = new Date(); const t = n.getHours() * 60 + n.getMinutes();
      bits.push(t >= range.open && t < range.close ? `<span class="live">Serving now</span>` : t < range.open ? `Starts in ${range.open - t} min` : "Over for today");
    }
    $("menu-meta").innerHTML = bits.map((b) => `<span>${b}</span>`).join('<span class="sep" aria-hidden="true"></span>');

    const meal = day.find((m) => m.meal === state.meal);
    if (!meal) {
      $("stations").innerHTML = `<p class="empty">No menu posted for this day yet.</p>`;
      return;
    }

    const match = (item) => state.diet === "all" || item.tags.includes(state.diet) || (state.diet === "vegetarian" && item.tags.includes("vegan"));
    const cards = meal.stations
      .map((s) => ({ ...s, items: s.items.filter(match) }))
      .filter((s) => s.items.length);

    if (!cards.length) {
      $("stations").innerHTML = `<p class="empty">Nothing matches that filter for ${esc(state.meal.toLowerCase())}.</p>`;
      return;
    }

    const LIMIT = 6;

    $("stations").innerHTML = cards.map((s) => {
      const key = `${state.hall}|${state.day}|${state.meal}|${s.station}`;

      // if all items are shown, the station is considered "open" (expanded)
      const stationOpen = state.openStations.has(key);

      // whether to show all food items
      const itemsExpanded = state.expanded.has(key);

      const shown = itemsExpanded
        ? s.items
        : s.items.slice(0, LIMIT);

      const more = s.items.length - LIMIT;

      return `
        <article class="station ${stationOpen ? "station-open" : ""}">

          <button
            type="button"
            class="station-toggle"
            data-toggle-station="${esc(key)}"
            aria-expanded="${stationOpen}"
          >
            <span class="station-arrow">▶</span>
            <span class="station-name">${esc(s.station)}</span>
            <span class="station-count">${s.items.length}</span>
          </button>

          ${
            stationOpen
              ? `
                <div class="station-body">
                  <ul>
                    ${shown
                      .map(
                        (it) =>
                          `<li>${esc(it.name)}${tagHtml(it.tags)}</li>`
                      )
                      .join("")}
                  </ul>

                  ${
                    more > 0
                      ? `
                        <button
                          type="button"
                          class="station-more"
                          data-station="${esc(key)}"
                        >
                          ${
                            itemsExpanded
                              ? "Show less"
                              : `Show ${more} more`
                          }
                        </button>
                      `
                      : ""
                  }
                </div>
              `
              : ""
          }

        </article>
      `;
    }).join("");
  }

  function tagHtml(tags) {
    const out = [];
    if (tags.includes("vegan")) out.push('<span class="diet diet-vegan" title="Vegan">Vegan</span>');
    else if (tags.includes("vegetarian")) out.push('<span class="diet diet-veg" title="Vegetarian">Veg</span>');
    if (tags.includes("halal")) out.push('<span class="diet diet-halal" title="Halal-friendly">Halal</span>');
    return out.join("");
  }

  $("hall-tabs").addEventListener("click", (e) => { const b = e.target.closest("[data-hall]"); if (b) { state.hall = b.dataset.hall; state.meal = null; renderMenus(); } });
  $("meal-tabs").addEventListener("click", (e) => { const b = e.target.closest("[data-meal]"); if (b) { state.meal = b.dataset.meal; renderMenus(); } });
  $("menu-day").addEventListener("change", (e) => { state.day = e.target.value; state.meal = null; renderMenus(); });
  document.querySelectorAll('input[name="diet"]').forEach((el) => el.addEventListener("change", () => { state.diet = el.value; renderMenus(); }));
  $("stations").addEventListener("click", (e) => {

  // Fold / Expand 整个 station
  const toggle = e.target.closest("[data-toggle-station]");

  if (toggle) {
    const key = toggle.dataset.toggleStation;

    if (state.openStations.has(key)) {
      state.openStations.delete(key);
    } else {
      state.openStations.add(key);
    }

    renderMenus();
    return;
  }


  // 原来的 Show more / Show less
  const moreButton = e.target.closest("[data-station]");

  if (moreButton) {
    const key = moreButton.dataset.station;

    if (state.expanded.has(key)) {
      state.expanded.delete(key);
    } else {
      state.expanded.add(key);
    }

    renderMenus();
  }
});

  renderPhone();
  renderFinder();
  if (halls.length) renderMenus();
  setInterval(renderPhone, 60 * 1000);
})();

// Persona tabs (works even if dining data fails to load)
(function () {
  const tabs = [...document.querySelectorAll(".persona-tabs [role=tab]")];
  if (!tabs.length) return;

  function select(tab, focus) {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute("aria-selected", on);
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
    });
    if (focus) tab.focus();
  }

  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => select(tab));
    tab.addEventListener("keydown", (e) => {
      const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (step) select(tabs[(i + step + tabs.length) % tabs.length], true);
    });
  });

  document.querySelectorAll("[data-persona]").forEach((link) => {
    link.addEventListener("click", () => select(document.getElementById(`tab-${link.dataset.persona}`)));
  });
})();
