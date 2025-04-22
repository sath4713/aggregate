import streamlit as st
import requests
import logging
import datetime as _dt
import re
from bs4 import BeautifulSoup
from dateutil import parser
from playwright.sync_api import sync_playwright


# ——————————————
# ESPN Scoreboard Fetcher (unchanged)
# ——————————————
@st.cache_data(ttl=300)
def get_espn_scoreboard(sport: str, league: str, dt_date: _dt.date) -> list[dict]:
    date_str = dt_date.strftime("%Y%m%d")
    url = (
        f"https://site.api.espn.com/apis/site/v2/sports/"
        f"{sport}/{league}/scoreboard?dates={date_str}"
    )
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logging.error(
            f"ESPN fetch failed ({sport}/{league}@{date_str}): {e}", exc_info=True
        )
        return []
    out = []
    for ev in data.get("events", []):
        comp = ev.get("competitions", [{}])[0]
        try:
            dt_obj = parser.parse(ev.get("date"))
        except Exception:
            dt_obj = None
        comps = comp.get("competitors", [])
        home = next((c for c in comps if c.get("homeAway") == "home"), {})
        away = next((c for c in comps if c.get("homeAway") == "away"), {})
        stype = comp.get("status", {}).get("type", {})
        status = stype.get("shortDetail", "Scheduled")
        result = None
        if stype.get("completed") or "Final" in status:
            hs, as_ = home.get("score"), away.get("score")
            if hs is not None and as_ is not None:
                result = f"{hs} – {as_}"
        out.append(
            {
                "id": ev.get("id"),
                "home_team": home.get("team", {}).get("displayName", "TBD"),
                "away_team": away.get("team", {}).get("displayName", "TBD"),
                "start_datetime": dt_obj,
                "venue": comp.get("venue", {}).get("fullName", ""),
                "status": status,
                "result": result,
                "network": (comp.get("broadcasts") or [{}])[0].get("callLetters"),
                "league_name": league.upper(),
                "league_id": f"{sport}/{league}",
                "url": (ev.get("links") or [{}])[0].get("href", ""),
            }
        )
    out.sort(key=lambda x: x["start_datetime"] or _dt.datetime.min)
    return out


# ——————————————
# ProCyclingStats via Playwright
# ——————————————
CIRCUIT_IDS = {"1.uwt": 1, "2.pro": 26}


def _parse_pcs_date_range(
    cell_text: str, year: int
) -> tuple[_dt.date, _dt.date] | None:
    """
    Parse a date or date-range string like "21.04 – 25.04" into (start_date, end_date)
    """
    parts = [p.strip() for p in re.split(r"–|-", cell_text) if p.strip()]
    try:

        def to_date(part: str):
            d, m = map(int, part.split("."))
            return _dt.date(year, m, d)

        if len(parts) == 2:
            start = to_date(parts[0])
            end = to_date(parts[1])
        else:
            start = end = to_date(parts[0])
        return start, end
    except Exception:
        logging.warning(f"Could not parse PCS date range: '{cell_text}'")
        return None


@st.cache_data(ttl=24 * 3600)
def get_pcs_season_events(classification: str, year: int) -> list[dict]:
    circuit = CIRCUIT_IDS.get(classification)
    if circuit is None:
        logging.error("Unknown PCS classification %r", classification)
        return []
    url = (
        f"https://www.procyclingstats.com/races.php?"
        f"year={year}&circuit={circuit}&class=&filter=Filter"
    )
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0")
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_selector("table.basic tbody tr", timeout=30000)
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.basic")
    if not table:
        logging.error("PCS: cannot find races table on %s", url)
        return []
    events = []
    for row in table.tbody.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        date_cell = cols[0].get_text(strip=True)
        date_range = _parse_pcs_date_range(date_cell, year)
        if not date_range:
            continue
        start_date, end_date = date_range
        link = cols[2].find("a")
        title = link.get_text(strip=True) if link else cols[2].get_text(strip=True)
        href = link["href"] if link and link.has_attr("href") else None
        # Emit one entry per day of the race
        day = start_date
        while day <= end_date:
            dt_obj = _dt.datetime.combine(day, _dt.time.min)
            events.append(
                {
                    "id": None,
                    "title": title,
                    "start_datetime": dt_obj,
                    "league_name": classification.upper(),
                    "league_id": classification,
                    "url": f"https://www.procyclingstats.com{href}" if href else None,
                }
            )
            day += _dt.timedelta(days=1)
    # Sort chronologically
    events.sort(key=lambda e: e["start_datetime"] or _dt.datetime.min)
    return events


@st.cache_data(ttl=3600)
def get_pcs_events_by_day(day: _dt.date, classification: str) -> list[dict]:
    return [
        e
        for e in get_pcs_season_events(classification, day.year)
        if e["start_datetime"] and e["start_datetime"].date() == day
    ]


# ——————————————
# Diamond League by‑day (PCS‑style)
# ——————————————
@st.cache_data(ttl=24 * 3600)
def get_diamond_league_events_by_day(day: _dt.date) -> list[dict]:
    base_url = "https://www.diamondleague.com"
    resp = requests.get(f"{base_url}/calendar/", timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    heading = next(
        (
            h2
            for h2 in soup.find_all("h2")
            if h2.get_text(strip=True) == f"Calendar {day.year}"
        ),
        None,
    )
    if not heading:
        return []

    out = []
    for sib in heading.find_next_siblings():
        if sib.name == "h2":
            break
        for a in sib.find_all("a", href=True):
            text = a.get_text(" ", strip=True)
            date_matches = list(re.finditer(r"\d{1,2}\s\w+", text))
            if len(date_matches) < 2:
                continue
            second = date_matches[1]
            try:
                ev_date = _dt.datetime.strptime(
                    f"{second.group(0)} {day.year}", "%d %B %Y"
                ).date()
            except ValueError:
                continue
            if ev_date != day:
                continue
            rest = text[second.end() :]
            m = re.match(r"\s*([^(]+)", rest)
            title = m.group(1).strip() if m else text
            href = a["href"]
            url = href if href.startswith("http") else base_url + href
            out.append(
                {
                    "id": None,
                    "title": title,
                    "start_datetime": _dt.datetime.combine(day, _dt.time.min),
                    "league_name": "Diamond League",
                    "league_id": "diamond-league",
                    "url": url,
                }
            )
    return out


# ——————————————
# World Marathon Majors by‑day (PCS‑style)
# ——————————————
@st.cache_data(ttl=3600)
def get_marathon_majors_by_day(day: _dt.date) -> list[dict]:
    url = "https://en.wikipedia.org/wiki/World_Marathon_Majors"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table", {"class": "wikitable"})
    if not table:
        return []

    headers = [th.get_text(strip=True) for th in table.find("tr").find_all("th")]
    row = next(
        (
            r
            for r in table.find_all("tr")[1:]
            if (td := r.find("td")) and td.get_text(strip=True) == str(day.year)
        ),
        None,
    )
    if not row:
        return []

    out = []
    cells = row.find_all("td")
    for city, cell in zip(headers[1:7], cells[1:7]):
        date_txt = cell.get_text(strip=True)
        try:
            ev_date = _dt.datetime.strptime(f"{date_txt} {day.year}", "%d %B %Y").date()
        except ValueError:
            continue
        if ev_date != day:
            continue
        out.append(
            {
                "id": None,
                "title": f"{city} Marathon",
                "start_datetime": _dt.datetime.combine(day, _dt.time.min),
                "league_name": "World Marathon Majors",
                "league_id": "world-marathon-majors",
                "url": None,
            }
        )
    return out


# ——————————————
# World Athletics Championships by‑day (PCS‑style)
# ——————————————
@st.cache_data(ttl=3600)
def get_wa_champs_by_day(day: _dt.date) -> list[dict]:
    url = f"https://en.wikipedia.org/wiki/{day.year}_World_Athletics_Championships"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")

    date_text = None
    for tr in soup.select("table.infobox tr"):
        if tr.th and tr.th.get_text(strip=True) == "Dates":
            date_text = tr.td.get_text(strip=True)
            break
    if not date_text:
        return []

    m = re.match(r"(\d{1,2})[–-](\d{1,2})\s+(\w+)\s+(\d{4})", date_text)
    if not m:
        return []
    sd, ed, mon, yr = m.groups()
    start = _dt.datetime.strptime(f"{sd} {mon} {yr}", "%d %B %Y").date()
    end = _dt.datetime.strptime(f"{ed} {mon} {yr}", "%d %B %Y").date()

    if not (start <= day <= end):
        return []

    return [
        {
            "id": None,
            "title": f"World Athletics Championships ({yr})",
            "start_datetime": _dt.datetime.combine(day, _dt.time.min),
            "league_name": "World Athletics Championships",
            "league_id": "world-athletics-championships",
            "url": url,
        }
    ]


