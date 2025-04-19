import streamlit as st
import requests
import logging
import datetime as _dt
from dateutil import parser
from bs4 import BeautifulSoup
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
        # parse UTC datetime
        try:
            dt_obj = parser.parse(ev.get("date"))
        except Exception:
            dt_obj = None

        # teams
        comps = comp.get("competitors", [])
        home = next((c for c in comps if c.get("homeAway") == "home"), {})
        away = next((c for c in comps if c.get("homeAway") == "away"), {})

        # status & result
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
# ProCyclingStats via Playwright (season cache + day filter)
# ——————————————
CIRCUIT_IDS = {
    "1.uwt": 1,  # UCI WorldTour
    "2.pro": 26,  # UCI ProSeries
}


def _parse_pcs_date(cell_text: str, year: int) -> _dt.date | None:
    # take first “DD.MM” from “DD.MM – DD.MM”
    part = cell_text.split("–", 1)[0].strip()
    try:
        d, m = map(int, part.split("."))
        return _dt.date(year, m, d)
    except:
        return None


@st.cache_data(ttl=24 * 3600)
def get_pcs_season_events(classification: str, year: int) -> list[dict]:
    """
    Scrape the full season for a given PCS classification (e.g. "1.uwt")
    and cache it for 24h.
    """
    circuit = CIRCUIT_IDS.get(classification)
    if circuit is None:
        logging.error("Unknown PCS classification %r", classification)
        return []

    url = f"https://www.procyclingstats.com/races.php?year={year}&circuit={circuit}&class=&filter=Filter"
    logging.debug("PCS season scrape → %s", url)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/100.0.4896.127 Safari/537.36"
            )
        )
        # only wait for table BASIC to appear
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
        race_date = _parse_pcs_date(cols[0].get_text(strip=True), year)
        name_cell = cols[2]
        link = name_cell.find("a")
        title = link.get_text(strip=True) if link else name_cell.get_text(strip=True)
        href = link["href"] if link else ""
        # build a datetime at midnight UTC
        dt_obj = _dt.datetime.combine(race_date, _dt.time.min) if race_date else None

        events.append(
            {
                "id": None,
                "title": title,
                "home_team": None,
                "away_team": None,
                "start_datetime": dt_obj,
                "venue": "",
                "status": "Scheduled",
                "result": None,
                "network": None,
                "league_name": classification.upper(),
                "league_id": classification,
                "url": f"https://www.procyclingstats.com{href}",
            }
        )

    # already sorted by appearance, but let's be sure:
    events.sort(key=lambda e: e["start_datetime"] or _dt.datetime.min)
    return events


@st.cache_data(ttl=3600)
def get_pcs_events_by_day(day: _dt.date, classification: str) -> list[dict]:
    """
    Return only those season events whose date == `day`.
    """
    season = get_pcs_season_events(classification, day.year)
    out = []
    for e in season:
        dt_obj = e.get("start_datetime")
        if dt_obj and dt_obj.date() == day:
            out.append(e.copy())
    return out
