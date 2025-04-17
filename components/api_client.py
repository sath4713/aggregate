# import streamlit as st
# import requests
# import logging
# import datetime
# from dateutil import parser

# # ————————————————————————————————
# # ESPN Scoreboard Fetcher (per-date), now with TV network info
# # ————————————————————————————————
# @st.cache_data(ttl=300)
# def get_espn_scoreboard(sport: str, league: str, dt: datetime.date) -> list[dict]:
#     """
#     Fetches games on a specific date from ESPN's V2 scoreboard endpoint,
#     and normalizes them, including the primary broadcast network.
#     """
#     date_str = dt.strftime("%Y%m%d")
#     url = (
#         f"https://site.api.espn.com/apis/site/v2/sports/"
#         f"{sport}/{league}/scoreboard?dates={date_str}"
#     )
#     try:
#         resp = requests.get(url, timeout=5)
#         resp.raise_for_status()
#         data = resp.json()
#     except Exception as e:
#         logging.error(f"ESPN scoreboard fetch failed: {e}", exc_info=True)
#         return []

#     events = data.get("events", [])
#     out = []
#     for ev in events:
#         comp = ev.get("competitions", [{}])[0]

#         # parse UTC datetime
#         try:
#             dt_obj = parser.parse(ev.get("date"))
#         except Exception:
#             dt_obj = None

#         # teams
#         competitors = comp.get("competitors", [])
#         home = next((c for c in competitors if c.get("homeAway") == "home"), {})
#         away = next((c for c in competitors if c.get("homeAway") == "away"), {})

#         # status & result
#         stype = comp.get("status", {}).get("type", {})
#         status = stype.get("shortDetail", "Scheduled")
#         result = None
#         if "Final" in status or stype.get("completed"):
#             hs = home.get("score"); as_ = away.get("score")
#             if hs is not None and as_ is not None:
#                 result = f"{hs} – {as_}"

#         # venue
#         venue = comp.get("venue", {}).get("fullName", "")

#         # primary broadcast network
#         broadcasts = comp.get("broadcasts", [])
#         network = None
#         if broadcasts:
#             bc = broadcasts[0]
#             network = (
#                 bc.get("callLetters")
#                 or bc.get("media", {}).get("callLetters")
#                 or bc.get("name")
#                 or bc.get("shortName")
#             )

#         # link
#         link = (ev.get("links") or [{}])[0].get("href", "")

#         out.append({
#             "id":             ev.get("id"),
#             "home_team":      home.get("team", {}).get("displayName", "TBD"),
#             "away_team":      away.get("team", {}).get("displayName", "TBD"),
#             "start_datetime": dt_obj,
#             "venue":          venue,
#             "status":         status,
#             "result":         result,
#             "network":        network,
#             "league_name":    league.upper(),
#             "league_id":      f"{sport}/{league}",
#             "url":            link,
#         })

#     # sort chronologically
#     out.sort(key=lambda x: x["start_datetime"] or datetime.datetime.min)
#     return out


# # ————————————————————————————————
# # TheSportsDB Season Fetcher (≤100 events/season)
# # ————————————————————————————————
# @st.cache_data(ttl=1800)
# def get_tsdb_schedule_by_season(league_id: str, season: str) -> list[dict]:
#     """
#     Fetches every event for a TSDB league-season via /eventsseason.php (free tier).
#     Falls back to the test key "3" if no secret is provided.
#     """
#     try:
#         api_key = st.secrets["THESPORTSDB_API_KEY"]
#     except Exception:
#         api_key = "3"

#     url = (
#         f"https://www.thesportsdb.com/api/v1/json/{api_key}"
#         f"/eventsseason.php?id={league_id}&s={season}"
#     )
#     try:
#         resp = requests.get(url, timeout=10)
#         resp.raise_for_status()
#         data = resp.json() or {}
#     except Exception as e:
#         logging.error(f"TSDB season fetch failed for {league_id}/{season}: {e}", exc_info=True)
#         return []

#     out = []
#     for ev in data.get("events") or []:
#         # parse date + time
#         dt_obj = None
#         date_str = ev.get("dateEvent")
#         time_str = ev.get("strTime") or "00:00:00"
#         if date_str:
#             try:
#                 dt_obj = parser.parse(f"{date_str} {time_str}")
#             except Exception:
#                 pass

#         title = ev.get("strEvent")
#         home  = ev.get("strHomeTeam")
#         away  = ev.get("strAwayTeam")
#         # for single-event leagues, clear home/away
#         if not home and not away:
#             home = away = None

#         hs = ev.get("intHomeScore"); as_ = ev.get("intAwayScore")
#         result = f"{hs} – {as_}" if hs is not None and as_ is not None else None
#         venue = ev.get("strVenue", "")

#         out.append({
#             "id":             ev.get("idEvent"),
#             "title":          title,
#             "home_team":      home,
#             "away_team":      away,
#             "start_datetime": dt_obj,
#             "venue":          venue,
#             "status":         ev.get("strStatus", "Scheduled"),
#             "result":         result,
#             "network":        None,               # TSDB has no broadcast info
#             "league_name":    None,               # added later in app.py
#             "league_id":      league_id,          # TSDB league ID
#             "url":            ev.get("strVideo", ""),
#         })

#     # sort by kickoff
#     out.sort(key=lambda x: x["start_datetime"] or datetime.datetime.min)
#     return out


# components/api_client.py

import streamlit as st
import requests
import logging
import datetime as _dt
from dateutil import parser

# ————————————————————————————————
# Try to import the WorldAthletics GraphQL wrapper
# ————————————————————————————————

try:
    from worldathletics import WorldAthletics

    WA_AVAILABLE = True
    _wa_client = WorldAthletics()
except ImportError:
    WA_AVAILABLE = False


# ————————————————————————————————
# ESPN Scoreboard Fetcher
# ————————————————————————————————
@st.cache_data(ttl=300)
def get_espn_scoreboard(sport: str, league: str, dt: _dt.date) -> list[dict]:
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
        if "Final" in status or stype.get("completed"):
            hs = home.get("score")
            as_ = away.get("score")
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
# TheSportsDB Season Fetcher
# ————————————————————————————————
@st.cache_data(ttl=1800)
def get_tsdb_schedule_by_season(league_id: str, season: str) -> list[dict]:
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
        logging.error(
            f"TSDB season fetch failed for {league_id}/{season}: {e}", exc_info=True
        )
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
        home = ev.get("strHomeTeam")
        away = ev.get("strAwayTeam")
        if not home and not away:
            home = away = None

        hs = ev.get("intHomeScore")
        as_ = ev.get("intAwayScore")
        result = f"{hs} – {as_}" if hs is not None and as_ is not None else None
        venue = ev.get("strVenue", "")

        out.append(
            {
                "id": ev.get("idEvent"),
                "title": title,
                "home_team": home,
                "away_team": away,
                "start_datetime": dt_obj,
                "venue": venue,
                "status": ev.get("strStatus", "Scheduled"),
                "result": result,
                "network": None,
                "league_name": None,
                "league_id": league_id,
                "url": ev.get("strVideo", ""),
            }
        )

    out.sort(key=lambda x: x["start_datetime"] or datetime.datetime.min)
    return out


# ————————————————————————————————
# World Athletics GraphQL Fetcher
# ————————————————————————————————
# In components/api_client.py, replace your existing get_wa_competition_events(...) with:


@st.cache_data(ttl=1800)
def get_wa_competition_events(competition_id: int) -> list[dict]:
    """
    Fetches upcoming events for a World Athletics competition via GraphQL,
    using the get_calendar_events(...) wrapper and the generated Pydantic models.
    """
    if not WA_AVAILABLE:
        st.error("worldathletics package not installed.")
        return []

    try:
        # this returns a GetCalendarEvents Pydantic model
        gql_response = _wa_client.get_calendar_events(competition_id)
    except Exception as e:
        st.error(f"WA fetch failed for competition {competition_id}: {e}")
        return []

    # gql_response.get_calendar_events is the inner model
    cal = getattr(gql_response, "get_calendar_events", None)
    if not cal or not getattr(cal, "results", None):
        # no results field or empty
        return []

    out = []
    for item in cal.results or []:
        if item is None:
            continue

        # item is a GetCalendarEventsGetCalendarEventsResults
        # its fields: id, name, venue, start_date, etc.
        start_dt = None
        if item.start_date:
            try:
                start_dt = _dt.datetime.fromisoformat(item.start_date)
            except Exception:
                pass

        out.append(
            {
                "id": item.id,
                "title": item.name,
                "home_team": None,
                "away_team": None,
                "start_datetime": start_dt,
                "venue": item.venue or "",
                "status": "Scheduled",
                "result": None,
                "network": None,
                "league_name": None,  # set later in app.py
                "league_id": competition_id,
                "url": item.was_url or "",
            }
        )

    # sort by start_datetime
    out.sort(key=lambda x: x["start_datetime"] or _dt.datetime.min)
    return out
