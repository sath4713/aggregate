
# import streamlit as st
# import requests, logging
# import datetime
# from dateutil import parser

# @st.cache_data(ttl=300)
# def get_espn_scoreboard(sport: str, league: str, dt: datetime.date) -> list[dict]:
#     """
#     Fetches games on a specific date from ESPN's V2 scoreboard endpoint,
#     and returns a list of normalized event dicts.
#     """
#     # ESPN wants YYYYMMDD
#     date_str = dt.strftime("%Y%m%d")
#     url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard?dates={date_str}"
#     try:
#         resp = requests.get(url, timeout=5)
#         resp.raise_for_status()
#         data = resp.json()
#     except Exception as e:
#         logging.error(f"Scoreboard fetch failed: {e}", exc_info=True)
#         return []

#     events = data.get("events", [])
#     out = []
#     for ev in events:
#         comp = ev.get("competitions", [{}])[0]
#         # parse time
#         try:
#             dt_obj = parser.parse(ev.get("date"))
#         except:
#             dt_obj = None

#         # find home/away
#         comps = comp.get("competitors", [])
#         home = next((c for c in comps if c.get("homeAway")=="home"), {})
#         away = next((c for c in comps if c.get("homeAway")=="away"), {})

#         # status/result
#         stype = comp.get("status",{}).get("type",{})
#         status = stype.get("shortDetail","Scheduled")
#         result = None
#         if "Final" in status or stype.get("completed"):
#             hs = home.get("score"); as_ = away.get("score")
#             if hs is not None and as_ is not None:
#                 result = f"{hs} – {as_}"

#         venue = comp.get("venue",{}).get("fullName","")

#         out.append({
#             "id":             ev.get("id"),
#             "home_team":      home.get("team",{}).get("displayName","TBD"),
#             "away_team":      away.get("team",{}).get("displayName","TBD"),
#             "start_datetime": dt_obj,
#             "venue":          venue,
#             "status":         status,
#             "result":         result,
#             "url":            (ev.get("links") or [{}])[0].get("href"),
#         })

#     return out

# components/api_client.py

import streamlit as st
import requests
import logging
import datetime
from dateutil import parser

# ————————————————————————————————
# ESPN Scoreboard Fetcher (per-date), now with TV network info
# ————————————————————————————————
@st.cache_data(ttl=300)
def get_espn_scoreboard(sport: str, league: str, dt: datetime.date) -> list[dict]:
    """
    Fetches games on a specific date from ESPN's V2 scoreboard endpoint,
    and normalizes them, including the primary broadcast network.
    """
    date_str = dt.strftime("%Y%m%d")
    url = (
        f"https://site.api.espn.com/apis/site/v2/sports/"
        f"{sport}/{league}/scoreboard?dates={date_str}"
    )
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logging.error(f"ESPN scoreboard fetch failed: {e}", exc_info=True)
        return []

    events = data.get("events", [])
    out = []
    for ev in events:
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
        if "Final" in status or stype.get("completed"):
            hs = home.get("score"); as_ = away.get("score")
            if hs is not None and as_ is not None:
                result = f"{hs} – {as_}"

        # venue
        venue = comp.get("venue", {}).get("fullName", "")

        # primary broadcast network
        broadcasts = comp.get("broadcasts", [])
        network = None
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

        out.append({
            "id":             ev.get("id"),
            "home_team":      home.get("team", {}).get("displayName", "TBD"),
            "away_team":      away.get("team", {}).get("displayName", "TBD"),
            "start_datetime": dt_obj,
            "venue":          venue,
            "status":         status,
            "result":         result,
            "network":        network,
            "league_name":    league.upper(),
            "league_id":      f"{sport}/{league}",
            "url":            link,
        })

    # sort chronologically
    out.sort(key=lambda x: x["start_datetime"] or datetime.datetime.min)
    return out


# ————————————————————————————————
# TheSportsDB Season Fetcher (≤100 events/season)
# ————————————————————————————————
@st.cache_data(ttl=1800)
def get_tsdb_schedule_by_season(league_id: str, season: str) -> list[dict]:
    """
    Fetches every event for a TSDB league-season via /eventsseason.php (free tier).
    Falls back to the test key "3" if no secret is provided.
    """
    try:
        api_key = st.secrets["THESPORTSDB_API_KEY"]
    except Exception:
        api_key = "3"

    url = (
        f"https://www.thesportsdb.com/api/v1/json/{api_key}"
        f"/eventsseason.php?id={league_id}&s={season}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json() or {}
    except Exception as e:
        logging.error(f"TSDB season fetch failed for {league_id}/{season}: {e}", exc_info=True)
        return []

    out = []
    for ev in data.get("events") or []:
        # parse date + time
        dt_obj = None
        date_str = ev.get("dateEvent")
        time_str = ev.get("strTime") or "00:00:00"
        if date_str:
            try:
                dt_obj = parser.parse(f"{date_str} {time_str}")
            except Exception:
                pass

        title = ev.get("strEvent")
        home  = ev.get("strHomeTeam")
        away  = ev.get("strAwayTeam")
        # for single-event leagues, clear home/away
        if not home and not away:
            home = away = None

        hs = ev.get("intHomeScore"); as_ = ev.get("intAwayScore")
        result = f"{hs} – {as_}" if hs is not None and as_ is not None else None
        venue = ev.get("strVenue", "")

        out.append({
            "id":             ev.get("idEvent"),
            "title":          title,
            "home_team":      home,
            "away_team":      away,
            "start_datetime": dt_obj,
            "venue":          venue,
            "status":         ev.get("strStatus", "Scheduled"),
            "result":         result,
            "network":        None,               # TSDB has no broadcast info
            "league_name":    None,               # added later in app.py
            "league_id":      league_id,          # TSDB league ID
            "url":            ev.get("strVideo", ""),
        })

    # sort by kickoff
    out.sort(key=lambda x: x["start_datetime"] or datetime.datetime.min)
    return out
