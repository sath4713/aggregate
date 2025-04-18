# components/api_client.py

import streamlit as st
import requests
import logging
import datetime as _dt
from dateutil import parser
from bs4 import BeautifulSoup
import re


# ————————————————————————————————
# ESPN Scoreboard Fetcher
# ————————————————————————————————
@st.cache_data(ttl=300)
def get_espn_scoreboard(sport: str, league: str, dt_date: _dt.date) -> list[dict]:
    """
    Fetches schedule/scoreboard data from ESPN's V2 API for a given date.
    """
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
        competitors = comp.get("competitors", [])
        home = next((c for c in competitors if c.get("homeAway") == "home"), {})
        away = next((c for c in competitors if c.get("homeAway") == "away"), {})

        # status & result
        stype = comp.get("status", {}).get("type", {})
        status = stype.get("shortDetail", "Scheduled")
        result = None
        if stype.get("completed") or "Final" in status:
            hs = home.get("score")
            as_ = away.get("score")
            if hs is not None and as_ is not None:
                result = f"{hs} – {as_}"

        # venue
        venue = comp.get("venue", {}).get("fullName", "")

        # primary broadcast network
        network = None
        broadcasts = comp.get("broadcasts", [])
        if broadcasts:
            bc = broadcasts[0]
            network = (
                bc.get("callLetters")
                or bc.get("media", {}).get("callLetters")
                or bc.get("name")
                or bc.get("shortName")
            )

        # link
        link = (ev.get("links") or [{}])[0].get("href", "")

        out.append(
            {
                "id": ev.get("id"),
                "home_team": home.get("team", {}).get("displayName", "TBD"),
                "away_team": away.get("team", {}).get("displayName", "TBD"),
                "start_datetime": dt_obj,
                "venue": venue,
                "status": status,
                "result": result,
                "network": network,
                "league_name": league.upper(),
                "league_id": f"{sport}/{league}",
                "url": link,
            }
        )

    out.sort(key=lambda x: x["start_datetime"] or _dt.datetime.min)
    return out


# ————————————————————————————————
# ProCyclingStats Helpers & Scrapers
# ————————————————————————————————

PCS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Safari/537.36"
    )
}


def _parse_pcs_date(cell_text: str, year: int) -> _dt.date | None:
    """
    Extract first DD.MM from 'DD.MM – DD.MM' or 'DD.MM' and return date(year, month, day).
    """
    part = re.split(r"[–-]", cell_text)[0].strip()
    m = re.match(r"^(\d{1,2})\.(\d{1,2})$", part)
    if not m:
        return None
    d, mth = int(m.group(1)), int(m.group(2))
    try:
        return _dt.date(year, mth, d)
    except ValueError:
        return None


def _find_pcs_races_table(soup: BeautifulSoup) -> BeautifulSoup | None:
    """
    Locate the PCS races table by matching the header row: th texts include 'Date' + 'Race'.
    """
    for tbl in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in tbl.select("thead th")]
        if "date" in headers and ("race" in headers or "name" in headers):
            return tbl
    return None


@st.cache_data(ttl=300)
def get_pcs_events_by_day(day: _dt.date, classification: str) -> list[dict]:
    """
    Scrapes PCS for UCI events of a given class on a specific day.
    """
    url = f"https://www.procyclingstats.com/races.php?class={classification}&year={day.year}"
    try:
        resp = requests.get(url, headers=PCS_HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(
            f"PCS day fetch failed ({classification} {day.year}): {e}", exc_info=True
        )
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = _find_pcs_races_table(soup)
    if not table:
        logging.warning("PCS: couldn't find races table by header-match")
        return []

    events = []
    for row in table.select("tbody tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        race_date = _parse_pcs_date(cols[0].get_text(strip=True), day.year)
        if race_date != day:
            continue

        link_tag = cols[2].find("a")
        if not link_tag:
            continue
        title = link_tag.get_text(strip=True)
        href = link_tag["href"]

        events.append(
            {
                "id": None,
                "title": title,
                "home_team": None,
                "away_team": None,
                "start_datetime": _dt.datetime.combine(day, _dt.time.min),
                "venue": "",
                "status": "Scheduled",
                "result": None,
                "network": None,
                "league_name": classification.upper(),
                "league_id": classification,
                "url": f"https://www.procyclingstats.com{href}",
            }
        )

    return events


@st.cache_data(ttl=1800)
def get_pcs_season_events(classification: str, year: int) -> list[dict]:
    """
    Scrapes the full PCS calendar for the given UCI classification & year.
    """
    url = (
        f"https://www.procyclingstats.com/races.php?class={classification}&year={year}"
    )
    try:
        resp = requests.get(url, headers=PCS_HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logging.error(
            f"PCS season fetch failed ({classification} {year}): {e}", exc_info=True
        )
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    table = _find_pcs_races_table(soup)
    if not table:
        logging.warning("PCS: couldn't find races table by header-match")
        return []

    events = []
    for row in table.select("tbody tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        race_date = _parse_pcs_date(cols[0].get_text(strip=True), year)
        if not race_date:
            continue

        link_tag = cols[2].find("a")
        if not link_tag:
            continue
        title = link_tag.get_text(strip=True)
        href = link_tag["href"]

        events.append(
            {
                "id": None,
                "title": title,
                "home_team": None,
                "away_team": None,
                "start_datetime": _dt.datetime.combine(race_date, _dt.time.min),
                "venue": "",
                "status": "Scheduled",
                "result": None,
                "network": None,
                "league_name": classification.upper(),
                "league_id": classification,
                "url": f"https://www.procyclingstats.com{href}",
            }
        )

    # sort by date
    events.sort(key=lambda e: e["start_datetime"])
    return events
