# # app.py
# import streamlit as st
# from datetime import date, timedelta
# import datetime as _dt
# import os, json

# from components.available_feeds import available_feeds
# from components.newsFeed import renderMultipleNewsFeeds
# from components.calendarView import renderScheduleCalendar
# from components.api_client import (
#     get_espn_scoreboard,
#     get_tsdb_schedule_by_season,
#     get_wa_competition_events,
# )

# # ——————————————
# # Profile persistence
# # ——————————————
# PROFILE_DIR = os.path.join(os.getcwd(), ".streamlit")
# PROFILE_PATH = os.path.join(PROFILE_DIR, "user_profile.json")


# def load_profile() -> list[str]:
#     try:
#         with open(PROFILE_PATH, "r") as f:
#             return json.load(f)
#     except Exception:
#         return []


# def save_profile(leagues: list[str]):
#     os.makedirs(PROFILE_DIR, exist_ok=True)
#     with open(PROFILE_PATH, "w") as f:
#         json.dump(leagues, f)


# # ——————————————
# # League mappings
# # ——————————————
# LEAGUES_BY_SPORT = {
#     "Basketball": {
#         "NBA": ("basketball", "nba"),
#         "WNBA": ("basketball", "wnba"),
#         "NCAAM (Men's College BBall)": ("basketball", "mens-college-basketball"),
#         "NCAAW (Women's College BBall)": ("basketball", "womens-college-basketball"),
#     },
#     "Football": {
#         "NFL": ("football", "nfl"),
#         "NCAAF (College Football)": ("football", "college-football"),
#     },
#     "Baseball": {
#         "MLB": ("baseball", "mlb"),
#     },
#     "Hockey": {
#         "NHL": ("hockey", "nhl"),
#     },
#     "Soccer": {
#         "MLS": ("soccer", "usa.1"),
#         "Premier League": ("soccer", "eng.1"),
#         "La Liga": ("soccer", "esp.1"),
#         "Bundesliga": ("soccer", "ger.1"),
#         "Serie A": ("soccer", "ita.1"),
#         "Ligue 1": ("soccer", "fra.1"),
#         "Liga MX": ("soccer", "mex.1"),
#         "Champions League": ("soccer", "uefa.champions"),
#         "Europa League": ("soccer", "uefa.europa"),
#     },
#     "Motorsports": {
#         "Formula 1": ("racing", "f1"),
#         "NASCAR Cup Series": ("racing", "nascar.cup"),
#     },
#     "Golf": {
#         "The Masters": ("golf", "masters"),
#         "PGA Championship": ("golf", "pga"),
#         "US Open (Golf)": ("golf", "usopen"),
#         "The Open Championship": ("golf", "britishopen"),
#     },
#     "Tennis": {
#         "Wimbledon": ("tennis", "wimbledon"),
#         "US Open (Tennis)": ("tennis", "usopen"),
#         "Australian Open": ("tennis", "australianopen"),
#         "French Open": ("tennis", "frenchopen"),
#     },
# }

# # TSDB-only leagues (free tier, ≤100 events/season)
# TSDB_LEAGUES_BY_SPORT = {
#     "Cycling": {
#         "UCI World Tour": "4465",
#         "UCI ProSeries": "5330",
#     },
#     # other non-ESPN sports…
# }

# # World Athletics competitions (via GraphQL wrapper)
# WA_COMPETITIONS = {
#     "Diamond League": 5282,
#     "World Athletics Championships": 5007,
#     "World Athletics Indoor Championships": 5283,
#     "Olympics Athletics": 4994,
#     "World Athletics Relays": 5305,
# }

# # ——————————————
# # Streamlit setup
# # ——————————————
# st.set_page_config(layout="wide")
# st.title("🏟️ Sports Hub")

# # session state defaults
# if "selected_leagues" not in st.session_state:
#     st.session_state.selected_leagues = load_profile()
# if "selected_date" not in st.session_state:
#     st.session_state.selected_date = date.today()

# # top tabs
# tabs = st.tabs(["📰 News Feed", "📅 Schedules", "👤 Profile"])
# news_tab, sched_tab, profile_tab = tabs

# # ——————————————
# # NEWS FEED TAB
# # ——————————————
# with news_tab:
#     st.header("📰 Your Custom News Feed")
#     if st.sidebar.button("🔄 Reload News"):
#         st.cache_data.clear()
#         try:
#             st.experimental_rerun()
#         except AttributeError:
#             st.sidebar.info("Cache cleared – please refresh the page.")

#     sel = st.session_state.selected_leagues
#     if not sel:
#         st.warning("Select leagues in Profile to see news.")
#     else:
#         sports = (
#             {
#                 sport
#                 for sport, leagues in LEAGUES_BY_SPORT.items()
#                 if any(l in sel for l in leagues)
#             }
#             | {
#                 sport
#                 for sport, leagues in TSDB_LEAGUES_BY_SPORT.items()
#                 if any(l in sel for l in leagues)
#             }
#             | {sport for sport in WA_COMPETITIONS if sport in sel}
#         )
#         urls = []
#         for sport in sports:
#             feeds = available_feeds.get(sport, {})
#             if isinstance(feeds, list):
#                 urls += [f["url"] for f in feeds]
#             else:
#                 for lst in feeds.values():
#                     urls += [f["url"] for f in lst]
#         renderMultipleNewsFeeds(urls, max_items_per_feed=10)

# # ——————————————
# # SCHEDULES TAB
# # ——————————————
# with sched_tab:
#     st.header("📅 Sports Schedules")

#     # Prev/Today/Next buttons
#     p, t, n = st.columns([1, 1, 1])
#     if p.button("← Prev"):
#         st.session_state.selected_date -= timedelta(days=1)
#     if t.button("• Today"):
#         st.session_state.selected_date = date.today()
#     if n.button("Next →"):
#         st.session_state.selected_date += timedelta(days=1)

#     # sidebar date picker
#     st.sidebar.date_input(
#         "Jump to date:", value=st.session_state.selected_date, key="selected_date"
#     )

#     sel_leagues = st.session_state.selected_leagues
#     if not sel_leagues:
#         st.warning("Select leagues in Profile to see schedules.")
#     else:
#         # build lookup tables
#         espn_map = {
#             name: slugs
#             for leagues in LEAGUES_BY_SPORT.values()
#             for name, slugs in leagues.items()
#         }
#         tsdb_map = {
#             name: lid
#             for leagues in TSDB_LEAGUES_BY_SPORT.values()
#             for name, lid in leagues.items()
#         }

#         # view selector
#         view_opts = ["All"] + sel_leagues
#         view_choice = st.sidebar.radio("View:", view_opts, index=0)

#         # fetch events
#         all_events = []
#         with st.spinner(f"Loading games for {st.session_state.selected_date}…"):
#             yr = str(st.session_state.selected_date.year)
#             for league in sel_leagues:
#                 if league in espn_map:
#                     s, l = espn_map[league]
#                     evs = get_espn_scoreboard(s, l, st.session_state.selected_date)
#                 elif league in WA_COMPETITIONS:
#                     cid = WA_COMPETITIONS[league]
#                     evs = get_wa_competition_events(cid)
#                 elif league in tsdb_map:
#                     evs = get_tsdb_schedule_by_season(tsdb_map[league], yr)
#                 else:
#                     st.sidebar.warning(f"Skipping unknown league: {league}")
#                     continue

#                 for e in evs:
#                     e["league_name"] = league
#                 all_events += evs

#         # sort by timestamp
#         def _ts(ev):
#             dt = ev.get("start_datetime")
#             if not dt:
#                 return float("-inf")
#             if hasattr(dt, "tzinfo") and dt.tzinfo:
#                 dt = dt.astimezone(_dt.timezone.utc).replace(tzinfo=None)
#             return dt.timestamp()

#         all_events.sort(key=_ts)

#         # per-league view
#         if view_choice != "All":
#             le_events = [e for e in all_events if e["league_name"] == view_choice]
#             now_ts = _dt.datetime.now().timestamp()
#             upcoming = [e for e in le_events if _ts(e) >= now_ts]
#             if upcoming:
#                 ne = upcoming[0]
#                 st.subheader(f"Next {view_choice} Event")
#                 dt_obj = ne.get("start_datetime")
#                 time_str = dt_obj.strftime("%Y-%m-%d %I:%M %p") if dt_obj else "TBD"
#                 title = (
#                     ne.get("title") or f"{ne.get('away_team')} vs {ne.get('home_team')}"
#                 )
#                 st.markdown(f"### {title}")
#                 st.write(f"**Time:** {time_str}")
#                 if ne.get("venue"):
#                     st.write(f"**Venue:** {ne['venue']}")
#                 if ne.get("status"):
#                     st.write(f"**Status:** {ne['status']}")
#                 st.divider()
#             else:
#                 st.info(f"No upcoming {view_choice} events found.")
#             renderScheduleCalendar(le_events, st.session_state.selected_date)
#         else:
#             renderScheduleCalendar(all_events, st.session_state.selected_date)

# # ——————————————
# # PROFILE TAB
# # ——————————————
# with profile_tab:
#     st.header("👤 Your Profile")
#     st.write("Select the leagues you follow:")

#     # ESPN-backed leagues
#     for sport, leagues in LEAGUES_BY_SPORT.items():
#         with st.expander(sport):
#             for league in leagues:
#                 key = f"profile_{league}"
#                 checked = league in st.session_state.selected_leagues
#                 new = st.checkbox(league, value=checked, key=key)
#                 if new and league not in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.append(league)
#                 if not new and league in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.remove(league)

#     # TSDB-only leagues
#     for sport, leagues in TSDB_LEAGUES_BY_SPORT.items():
#         with st.expander(f"{sport} (via TheSportsDB)"):
#             for league in leagues:
#                 key = f"profile_{league}"
#                 checked = league in st.session_state.selected_leagues
#                 new = st.checkbox(league, value=checked, key=key)
#                 if new and league not in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.append(league)
#                 if not new and league in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.remove(league)

#     # World Athletics competitions
#     with st.expander("Track & Field (World Athletics)"):
#         for league in WA_COMPETITIONS:
#             key = f"profile_{league}"
#             checked = league in st.session_state.selected_leagues
#             new = st.checkbox(league, value=checked, key=key)
#             if new and league not in st.session_state.selected_leagues:
#                 st.session_state.selected_leagues.append(league)
#             if not new and league in st.session_state.selected_leagues:
#                 st.session_state.selected_leagues.remove(league)

#     st.markdown("**Your Selected Leagues:**")
#     st.write(st.session_state.selected_leagues)

#     if st.button("💾 Save Profile"):
#         save_profile(st.session_state.selected_leagues)
#         st.success("Profile saved and will load next time.")


# app.py

import streamlit as st
from datetime import date, timedelta
import datetime as _dt
import os, json

from components.available_feeds import available_feeds
from components.newsFeed import renderMultipleNewsFeeds
from components.calendarView import renderScheduleCalendar
from components.api_client import (
    get_espn_scoreboard,
    get_pcs_events_by_day,
    get_pcs_season_events,
)

# ——————————————
# Profile persistence
# ——————————————
PROFILE_DIR = os.path.join(os.getcwd(), ".streamlit")
PROFILE_PATH = os.path.join(PROFILE_DIR, "user_profile.json")


def load_profile() -> list[str]:
    try:
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_profile(leagues: list[str]):
    os.makedirs(PROFILE_DIR, exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        json.dump(leagues, f)


# ——————————————
# League mappings
# ——————————————
LEAGUES_BY_SPORT = {
    "Basketball": {
        "NBA": ("basketball", "nba"),
        "WNBA": ("basketball", "wnba"),
        "NCAAM (Men's College BBall)": ("basketball", "mens-college-basketball"),
        "NCAAW (Women's College BBall)": ("basketball", "womens-college-basketball"),
    },
    "Football": {
        "NFL": ("football", "nfl"),
        "NCAAF (College Football)": ("football", "college-football"),
    },
    "Baseball": {"MLB": ("baseball", "mlb")},
    "Hockey": {"NHL": ("hockey", "nhl")},
    "Soccer": {
        "MLS": ("soccer", "usa.1"),
        "Premier League": ("soccer", "eng.1"),
        "La Liga": ("soccer", "esp.1"),
        "Bundesliga": ("soccer", "ger.1"),
        "Serie A": ("soccer", "ita.1"),
        "Ligue 1": ("soccer", "fra.1"),
        "Liga MX": ("soccer", "mex.1"),
        "Champions League": ("soccer", "uefa.champions"),
        "Europa League": ("soccer", "uefa.europa"),
    },
    "Motorsports": {
        "Formula 1": ("racing", "f1"),
        "NASCAR Cup Series": ("racing", "nascar.cup"),
    },
    "Golf": {
        "The Masters": ("golf", "masters"),
        "PGA Championship": ("golf", "pga"),
        "US Open (Golf)": ("golf", "usopen"),
        "The Open Championship": ("golf", "britishopen"),
    },
    "Tennis": {
        "Wimbledon": ("tennis", "wimbledon"),
        "US Open (Tennis)": ("tennis", "usopen"),
        "Australian Open": ("tennis", "australianopen"),
        "French Open": ("tennis", "frenchopen"),
    },
}

PCS_LEAGUES_BY_SPORT = {
    "Cycling (ProCyclingStats)": {
        "UCI ProSeries One‑Day (1.PRO)": "1.pro",
        "UCI ProSeries Stage Race (2.PRO)": "2.pro",
        "UCI WorldTour One‑Day (1.UWT)": "1.uwt",
        "UCI WorldTour Stage Race (2.UWT)": "2.uwt",
    }
}

# ——————————————
# Streamlit setup
# ——————————————
st.set_page_config(layout="wide")
st.title("🏟️ Sports Hub")

# Session state defaults
if "selected_leagues" not in st.session_state:
    st.session_state.selected_leagues = load_profile()
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# Top navigation tabs
tabs = st.tabs(["📰 News Feed", "📅 Schedules", "👤 Profile"])
news_tab, sched_tab, profile_tab = tabs

# ——————————————
# 1) NEWS FEED TAB
# ——————————————
with news_tab:
    st.header("📰 Your Custom News Feed")
    if st.sidebar.button("🔄 Reload News"):
        st.cache_data.clear()
        try:
            st.experimental_rerun()
        except AttributeError:
            st.sidebar.info("Cache cleared. Refresh page manually.")

    sel = st.session_state.selected_leagues
    if not sel:
        st.warning("Select leagues in Profile to see news.")
    else:
        # gather RSS URLs for chosen sports
        sports = {
            sport
            for sport, leagues in LEAGUES_BY_SPORT.items()
            if any(l in sel for l in leagues)
        } | {sport for sport in PCS_LEAGUES_BY_SPORT if sport in sel}
        urls = []
        for sport in sports:
            feeds = available_feeds.get(sport, {})
            if isinstance(feeds, list):
                urls += [f["url"] for f in feeds]
            else:
                for lst in feeds.values():
                    urls += [f["url"] for f in lst]
        renderMultipleNewsFeeds(urls, max_items_per_feed=10)

# ——————————————
# 2) SCHEDULES TAB
# ——————————————
with sched_tab:
    st.header("📅 Sports Schedules")

    # ← Prev • Today → buttons
    prev_col, today_col, next_col = st.columns(3)
    if prev_col.button("← Prev"):
        st.session_state.selected_date -= timedelta(days=1)
    if today_col.button("• Today"):
        st.session_state.selected_date = date.today()
    if next_col.button("Next →"):
        st.session_state.selected_date += timedelta(days=1)

    sel_date = st.sidebar.date_input(
        "Jump to date",
        value=st.session_state.selected_date,
        key="selected_date",
    )

    sel_leagues = st.session_state.selected_leagues
    if not sel_leagues:
        st.warning("Select some leagues in Profile to see schedules.")
        st.stop()

    view_opts = ["All"] + sel_leagues
    view_choice = st.sidebar.radio("View:", view_opts, index=0)

    espn_map = {
        name: slugs
        for leagues in LEAGUES_BY_SPORT.values()
        for name, slugs in leagues.items()
    }
    pcs_map = {
        name: code
        for leagues in PCS_LEAGUES_BY_SPORT.values()
        for name, code in leagues.items()
    }

    if "pcs_season_cache" not in st.session_state:
        st.session_state.pcs_season_cache = {}

    # 1) Fetch all day‑of events
    day_events: list[dict] = []
    with st.spinner(f"Loading events for {sel_date}…"):
        for league in sel_leagues:
            if league in espn_map:
                s, l = espn_map[league]
                evs = get_espn_scoreboard(s, l, sel_date)
            elif league in pcs_map:
                evs = get_pcs_events_by_day(sel_date, pcs_map[league])
            else:
                evs = []

            for e in evs:
                e["league_name"] = league
            day_events.extend(evs)

    # 2) Prime PCS season cache
    for league in sel_leagues:
        if league in pcs_map:
            code = pcs_map[league]
            cache_key = (code, sel_date.year)
            if cache_key not in st.session_state.pcs_season_cache:
                st.session_state.pcs_season_cache[cache_key] = get_pcs_season_events(
                    code, sel_date.year
                )

    # Sort helper
    def _ts(e):
        dt_obj = e.get("start_datetime")
        if not dt_obj:
            return float("-inf")
        if hasattr(dt_obj, "tzinfo") and dt_obj.tzinfo:
            dt_obj = dt_obj.astimezone(_dt.timezone.utc).replace(tzinfo=None)
        return dt_obj.timestamp()

    day_events.sort(key=_ts)

    # ————————————————————————————————
    # DEBUG: show exactly what was pulled
    # ————————————————————————————————
    st.markdown("### 🔍 Debug Info")

    st.write("**Day‑of Events**")
    for e in day_events:
        st.write(
            {
                "league": e.get("league_name"),
                "title": e.get("title")
                or f"{e.get('away_team')} vs {e.get('home_team')}",
                "time": e.get("start_datetime"),
                "status": e.get("status"),
                "url": e.get("url"),
            }
        )

    st.write("**PCS Season Cache**")
    for league_name, code in pcs_map.items():
        key = (code, sel_date.year)
        events = st.session_state.pcs_season_cache.get(key, [])
        st.write(f"- {league_name}: {len(events)} events")
        for ev in events[:5]:
            st.write(
                {
                    "date": (
                        ev["start_datetime"].date()
                        if ev.get("start_datetime")
                        else None
                    ),
                    "title": ev.get("title"),
                }
            )
        if len(events) > 5:
            st.write("  …")
    st.divider()

    # 3) If viewing single league, show Next Event...
    if view_choice != "All":
        league = view_choice
        now_ts = _dt.datetime.now().timestamp()
        if league in pcs_map:
            season = st.session_state.pcs_season_cache[(pcs_map[league], sel_date.year)]
            upcoming = [e for e in season if _ts(e) >= now_ts]
        else:
            upcoming = [
                e for e in day_events if e["league_name"] == league and _ts(e) >= now_ts
            ]
        if upcoming:
            ne = upcoming[0]
            st.subheader(f"Next {league} Event")
            title = ne.get("title") or f"{ne.get('away_team')} vs {ne.get('home_team')}"
            st.markdown(f"### {title}")
            if ne.get("start_datetime"):
                st.write(f"**Time:** {ne['start_datetime']:%Y-%m-%d %I:%M %p}")
            if ne.get("venue"):
                st.write(f"**Venue:** {ne['venue']}")
            if ne.get("status"):
                st.write(f"**Status:** {ne['status']}")
            st.divider()
        else:
            st.info(f"No upcoming {league} events found.")

        subset = [e for e in day_events if e["league_name"] == league]
        renderScheduleCalendar(subset, sel_date)

    else:
        renderScheduleCalendar(day_events, sel_date)

# ——————————————
# 3) PROFILE TAB
# ——————————————
with profile_tab:
    st.header("👤 Your Profile")
    st.write("Select the leagues you follow:")

    # ESPN-backed
    for sport, leagues in LEAGUES_BY_SPORT.items():
        with st.expander(sport):
            for league in leagues:
                key = f"profile_{league}"
                chk = league in st.session_state.selected_leagues
                new = st.checkbox(league, value=chk, key=key)
                if new and league not in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.append(league)
                if not new and league in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.remove(league)

    # ProCyclingStats
    with st.expander("Cycling (ProCyclingStats)"):
        for league, cls in PCS_LEAGUES_BY_SPORT["Cycling (ProCyclingStats)"].items():
            key = f"profile_{league}"
            chk = league in st.session_state.selected_leagues
            new = st.checkbox(league, value=chk, key=key)
            if new and league not in st.session_state.selected_leagues:
                st.session_state.selected_leagues.append(league)
            if not new and league in st.session_state.selected_leagues:
                st.session_state.selected_leagues.remove(league)

    st.markdown("**Your Selected Leagues:**")
    st.write(st.session_state.selected_leagues)

    if st.button("💾 Save Profile"):
        save_profile(st.session_state.selected_leagues)
        st.success("Profile saved for next time!")
