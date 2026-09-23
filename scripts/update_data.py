#!/usr/bin/env python3
"""Pull real UMD dining data into data/dining.js for the TerpBites site.

Sources (all public):
  - Hours: the Google Sheet that dining.umd.edu reads its hours from
  - Menus: nutrition.umd.edu (South Campus, Yahentamitsi, 251 North)
  - Building locations: api.umd.io/v1/map/buildings

Run from the project root:  python3 scripts/update_data.py
Standard library only. Re-run whenever you want fresh hours and menus.
"""

import csv
import io
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "dining.js"
DAYS_OF_HOURS = 21
DAYS_OF_MENUS = 3

SHEET = "https://docs.google.com/spreadsheets/d/1vdWskGO2-aJfKLSW8-3zMaj_nx4SBJHF3OvMEy4-ZNo/gviz/tq?tqx=out:csv&gid={}"
TABS = {
    "hall": 479022338,
    "cafe": 2021515491,
    "stamp": 57096019,
    "kirwan": 1473105230,
    "market": 1618091201,
}
MENU_URL = "https://nutrition.umd.edu/?locationNum={}&dtdate={}"
BUILDINGS_URL = "https://api.umd.io/v1/map/buildings"

# Buildings that umd.io is missing or names differently: id -> override
BUILDING_OVERRIDES = {
    "PSC": {"name": "Physical Sciences Complex", "lat": 38.99085, "lng": -76.94015},
}

# Venue metadata taken from dining.umd.edu hours pages.
# key: (sheet tab, venue name in sheet) -> details
VENUES = [
    # Dining halls (hours come as one row per meal)
    dict(id="south-campus", tab="hall", sheet="South Campus", name="South Campus Dining Hall", kind="Dining hall",
         building="026", menu=16, blurb="All-you-care-to-eat dining hall on South Hill."),
    dict(id="yahentamitsi", tab="hall", sheet="Yahentamitsi", name="Yahentamitsi Dining Hall", kind="Dining hall",
         building="436", menu=19, blurb="All-you-care-to-eat dining hall in the Heritage Community."),
    dict(id="251-north", tab="hall", sheet="251 North", name="251 North", kind="Dining hall",
         building="251", menu=51, blurb="All-you-care-to-eat dining hall in the Denton Community."),
    # Stamp Student Union
    dict(id="chick-fil-a", tab="stamp", sheet="Chick-fil-A", name="Chick-fil-A", kind="Fast food", building="163",
         blurb="Stamp food court."),
    dict(id="panera", tab="stamp", sheet="Panera Bread", name="Panera Bread", kind="Fast casual", building="163",
         blurb="First floor of the Stamp."),
    dict(id="stamp-subway", tab="stamp", sheet="Subway", name="Subway (Stamp)", kind="Fast food", building="163",
         blurb="Stamp food court."),
    dict(id="qdoba", tab="stamp", sheet="Qdoba", name="Qdoba", kind="Fast casual", building="163",
         blurb="Stamp food court."),
    dict(id="union-pizza", tab="stamp", sheet="Union Pizza", name="Union Pizza", kind="Fast food", building="163",
         blurb="Stamp food court."),
    dict(id="maryland-dairy", tab="stamp", sheet="Maryland Dairy", name="Maryland Dairy", kind="Ice cream", building="163",
         blurb="Ice cream made on campus, in the Baltimore Room."),
    dict(id="coffee-bar", tab="stamp", sheet="The Coffee Bar", name="The Coffee Bar", kind="Café", building="163",
         blurb="Starbucks coffee, donuts, bagels, and muffins."),
    # Kirwan Food Court
    dict(id="kirwan-subway", tab="kirwan", sheet="Subway", name="Subway (Kirwan)", kind="Fast food", building="084",
         blurb="Smaller Subway menu in Kirwan Hall."),
    dict(id="taco-bell", tab="kirwan", sheet="Taco Bell Express", name="Taco Bell Express", kind="Fast food", building="084",
         blurb="Kirwan Hall food court."),
    dict(id="em-cafe", tab="kirwan", sheet="E+M Cafe", name="E+M Cafe", kind="Café", building="084",
         blurb="Donuts, bagels, muffins, chips, and snacks."),
    # Cafes
    dict(id="applause", tab="cafe", sheet="Applause", name="Applause", kind="Café", building="386",
         blurb="Starbucks coffee and quick bites in The Clarice."),
    dict(id="breakpoint", tab="cafe", sheet="Breakpoint", name="Breakpoint", kind="Café", building="432",
         blurb="Omelet burritos, bowls, and made-to-order salads in Iribe."),
    dict(id="creative-commons", tab="cafe", sheet="Creative Commons", name="Creative Commons", kind="Café", building="141",
         blurb="Sandwiches, salads, and fruit in Tawes Hall."),
    dict(id="idea-central", tab="cafe", sheet="IDEA Central", name="IDEA Central", kind="Café", building="228",
         blurb="Breakfast sandwiches and wraps in the IDEA Factory."),
    dict(id="food-for-thought", tab="cafe", sheet="Food for Thought", name="Food for Thought", kind="Café", building="226",
         blurb="Sandwiches, salads, and fruit in ESJ."),
    dict(id="footnotes", tab="cafe", sheet="Footnotes", name="Footnotes", kind="Café", building="035",
         blurb="Sandwiches, salads, and snacks in McKeldin Library."),
    dict(id="quantum", tab="cafe", sheet="Quantum", name="Quantum", kind="Café", building="PSC",
         blurb="Pastries, sandwiches, and salads in the Physical Sciences Complex."),
    dict(id="rudys", tab="cafe", sheet="Rudy’s", name="Rudy's", kind="Café", building="039",
         blurb="Hot entrees, pizza, salad bar, and soup in Van Munching."),
    dict(id="samovar", tab="cafe", sheet="Samovar", name="Samovar", kind="Café", building="073",
         blurb="Noodle bowls in H.J. Patterson Hall."),
    dict(id="sneakers", tab="cafe", sheet="Sneaker’s", name="Sneaker's", kind="Café", building="068",
         blurb="Smoothies, sandwiches, and snacks in Eppley Rec Center."),
    # Markets
    dict(id="north-market-grill", tab="market", sheet="North Campus Market | Grill", name="North Campus Grill",
         kind="Grill", building="256", blurb="Late-night grill in the Ellicott Community."),
    dict(id="north-market-pizza", tab="market", sheet="North Campus Market | Pizza", name="North Campus Pizza",
         kind="Fast food", building="256", blurb="Late-night pizza in the Ellicott Community."),
    dict(id="north-market-cafe", tab="market", sheet="North Campus Market | Cafe", name="North Campus Cafe",
         kind="Café", building="256", blurb="Starbucks coffee and boba tea."),
    dict(id="north-market-shop", tab="market", sheet="North Campus Market | Shop", name="North Campus Market",
         kind="Market", building="256", blurb="Convenience store, open late."),
    dict(id="south-market-grill", tab="market", sheet="South Campus Market | Grill", name="South Campus Grill",
         kind="Grill", building="026", blurb="Grill on South Hill."),
    dict(id="south-market-cafe", tab="market", sheet="South Campus Market | Cafe", name="South Campus Cafe",
         kind="Café", building="026", blurb="Starbucks coffee and baked goods."),
    dict(id="south-market-shop", tab="market", sheet="South Campus Market | Shop", name="South Campus Market",
         kind="Market", building="026", blurb="Convenience store, open late."),
    dict(id="union-shop", tab="market", sheet="Union Shop", name="Union Shop", kind="Market", building="163",
         blurb="Grab-and-go sandwiches, salads, and coffee in the Stamp."),
    dict(id="engage", tab="market", sheet="Engage", name="Engage", kind="Market", building="226",
         blurb="Small grab-and-go shop in ESJ."),
]

DOOR_PRICES = {"Breakfast": 9.50, "Brunch": 16.25, "Lunch": 16.25, "Dinner": 20.25}
DOOR_PRICES_NOTE = "Dining hall door prices listed by UMD Dining for Fall 2025."


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TerpBites class project (INST362)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


# ---------- hours ----------

TIME_RE = re.compile(r"^\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*$", re.I)


def parse_time(s, fallback_meridiem=None):
    m = TIME_RE.match(s)
    if not m:
        return None, None
    h, mins, mer = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or fallback_meridiem or "").lower()
    if mer == "pm" and h != 12:
        h += 12
    if mer == "am" and h == 12:
        h = 0
    return h * 60 + mins, mer


def parse_range(cell):
    """'7:30am-1am' -> [450, 1500]. Returns None for Closed/TBD/blank."""
    cell = cell.strip()
    if "-" not in cell:
        return None
    a, b = cell.split("-", 1)
    end, end_mer = parse_time(b)
    start, _ = parse_time(a, fallback_meridiem=end_mer)
    if start is None or end is None:
        return None
    if end <= start:
        end += 24 * 60
    return [start, end]


def load_hours():
    """Return {tab: {row_name: {iso_date: cell}}}"""
    today = date.today()
    wanted = {(today + timedelta(days=i)) for i in range(DAYS_OF_HOURS)}
    tabs = {}
    for tab, gid in TABS.items():
        rows = list(csv.reader(io.StringIO(fetch(SHEET.format(gid)))))
        header = rows[1]
        cols = {}
        for i, h in enumerate(header):
            try:
                d = datetime.strptime(h.strip(), "%m/%d/%Y").date()
            except ValueError:
                continue
            if d in wanted:
                cols[i] = d.isoformat()
        table = {}
        for r in rows[2:]:
            if not r or not r[0].strip():
                continue
            table[r[0].strip()] = {iso: r[i].strip() for i, iso in cols.items() if i < len(r)}
        tabs[tab] = table
    return tabs


def venue_hours(v, tabs):
    table = tabs[v["tab"]]
    out = {}
    if v["tab"] == "hall":
        meals = [k for k in table if k.startswith(v["sheet"] + " |")]
        dates = sorted({d for k in meals for d in table[k]})
        for d in dates:
            ranges = []
            for k in meals:
                meal = k.split("|", 1)[1].strip()
                cell = table[k].get(d, "")
                rng = parse_range(cell)
                if rng:
                    ranges.append({"meal": meal, "open": rng[0], "close": rng[1], "label": cell})
            out[d] = sorted(ranges, key=lambda x: x["open"])
    else:
        row = table.get(v["sheet"])
        if row is None:
            print(f"  ! no hours row for {v['sheet']!r} in {v['tab']}", file=sys.stderr)
            return {}
        for d, cell in row.items():
            rng = parse_range(cell)
            out[d] = [{"open": rng[0], "close": rng[1], "label": cell}] if rng else []
            if not rng and cell.upper() == "TBD":
                out[d] = None  # unknown
    return out


# ---------- menus ----------

class MenuParser(HTMLParser):
    """Pulls meal tabs -> station cards -> items (with diet icons) from nutrition.umd.edu."""

    def __init__(self):
        super().__init__()
        self.tabs = {}        # pane id -> meal name
        self.meals = {}       # pane id -> [ {station, items} ]
        self._tab_for = None
        self._pane = None
        self._in_title = False
        self._in_item = False
        self._station = None
        self._item = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        if tag == "a" and "nav-link" in cls and a.get("href", "").startswith("#pane-"):
            self._tab_for = a["href"][1:]
        elif tag == "div" and "tab-pane" in cls and a.get("id", "").startswith("pane-"):
            self._pane = a["id"]
            self.meals.setdefault(self._pane, [])
        elif tag == "h3" and "card-title" in cls and self._pane:
            self._in_title = True
            self._station = {"station": "", "items": []}
            self.meals[self._pane].append(self._station)
        elif tag == "a" and "menu-item-name" in cls and self._station is not None:
            self._in_item = True
            self._item = {"name": "", "tags": []}
            self._station["items"].append(self._item)
        elif tag == "img" and "nutri-icon" in cls and self._item is not None:
            alt = (a.get("alt") or "").lower()
            tag_name = {"vegan": "vegan", "vegetarian": "vegetarian", "halalfriendly": "halal"}.get(alt)
            if tag_name and tag_name not in self._item["tags"]:
                self._item["tags"].append(tag_name)

    def handle_endtag(self, tag):
        if tag == "a":
            self._tab_for = None
            self._in_item = False
        if tag == "h3":
            self._in_title = False

    def handle_data(self, data):
        if self._tab_for:
            self.tabs[self._tab_for] = (self.tabs.get(self._tab_for, "") + data).strip()
        elif self._in_title:
            self._station["station"] += data.strip()
        elif self._in_item:
            self._item["name"] += data.strip()


def load_menu(location, d):
    p = MenuParser()
    p.feed(fetch(MENU_URL.format(location, f"{d.month}/{d.day}/{d.year}")))
    meals = []
    for pane, stations in p.meals.items():
        stations = [s for s in stations if s["items"]]
        if stations:
            meals.append({"meal": p.tabs.get(pane, pane), "stations": stations})
    return meals


# ---------- buildings ----------

def load_buildings():
    raw = json.loads(fetch(BUILDINGS_URL))
    by_id = {}
    for b in raw:
        if b.get("lat") is None or b.get("long") is None:
            continue
        by_id[b["id"]] = {"id": b["id"], "code": b.get("code") or "", "name": b["name"],
                          "lat": round(float(b["lat"]), 6), "lng": round(float(b["long"]), 6)}
    for k, v in BUILDING_OVERRIDES.items():
        by_id[k] = {"id": k, "code": k, **v}
    return by_id


def main():
    print("Fetching buildings from umd.io…")
    buildings = load_buildings()

    print("Fetching hours from UMD Dining…")
    tabs = load_hours()

    venues = []
    for v in VENUES:
        b = buildings.get(v["building"])
        if not b:
            print(f"  ! missing building {v['building']} for {v['name']}", file=sys.stderr)
            continue
        venues.append({
            "id": v["id"], "name": v["name"], "kind": v["kind"], "blurb": v["blurb"],
            "building": b["name"], "lat": b["lat"], "lng": b["lng"],
            "hasMenu": "menu" in v,
            "hours": venue_hours(v, tabs),
        })

    print("Fetching dining hall menus from nutrition.umd.edu…")
    menus = {}
    today = date.today()
    for v in VENUES:
        if "menu" not in v:
            continue
        menus[v["id"]] = {}
        for i in range(DAYS_OF_MENUS):
            d = today + timedelta(days=i)
            try:
                menus[v["id"]][d.isoformat()] = load_menu(v["menu"], d)
            except Exception as e:  # keep going if one page fails
                print(f"  ! menu failed for {v['name']} {d}: {e}", file=sys.stderr)

    # Buildings people might be coming from / going to: anything with a course code, plus venue buildings.
    venue_building_ids = {v["building"] for v in VENUES}
    places = sorted(
        (b for b in buildings.values() if b["code"] or b["id"] in venue_building_ids),
        key=lambda b: b["name"],
    )

    data = {
        "updated": datetime.now().isoformat(timespec="minutes"),
        "sources": {
            "hours": "https://dining.umd.edu/hours-locations",
            "menus": "https://nutrition.umd.edu/",
            "buildings": "https://api.umd.io/v1/map/buildings",
        },
        "doorPrices": DOOR_PRICES,
        "doorPricesNote": DOOR_PRICES_NOTE,
        "venues": venues,
        "menus": menus,
        "buildings": [{"name": b["name"], "code": b["code"], "lat": b["lat"], "lng": b["lng"]} for b in places],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "// Generated by scripts/update_data.py. Do not edit by hand.\n"
        "window.TERPBITES_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    n_items = sum(len(s["items"]) for m in menus.values() for day in m.values() for meal in day for s in meal["stations"])
    print(f"Wrote {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}: "
          f"{len(venues)} venues, {len(places)} buildings, {n_items} menu items.")


if __name__ == "__main__":
    main()
