# import streamlit as st
# from datetime import date
# from components.available_feeds import available_feeds
# from components.newsFeed import renderMultipleNewsFeeds
# from components.calendarView import renderScheduleCalendar
# from components.api_client import get_espn_scoreboard, get_tsdb_schedule_by_season

# # --- Mapping of sports to their supported ESPN leagues/slugs ---
# LEAGUES_BY_SPORT = {
#     "Basketball": {
#         "NBA":                          ("basketball", "nba"),
#         "WNBA":                         ("basketball", "wnba"),
#         "NCAAM (Men's College BBall)":  ("basketball", "mens-college-basketball"),
#         "NCAAW (Women's College BBall)":("basketball", "womens-college-basketball"),
#     },
#     "Football": {
#         "NFL":                          ("football",   "nfl"),
#         "NCAAF (College Football)":     ("football",   "college-football"),
#     },
#     "Baseball": {
#         "MLB":                          ("baseball",   "mlb"),
#     },
#     "Hockey": {
#         "NHL":                          ("hockey",     "nhl"),
#     },
#     "Soccer": {
#         "MLS":                          ("soccer",     "usa.1"),
#         "Premier League":               ("soccer",     "eng.1"),
#         "La Liga":                      ("soccer",     "esp.1"),
#         "Bundesliga":                   ("soccer",     "ger.1"),
#         "Serie A":                      ("soccer",     "ita.1"),
#         "Ligue 1":                      ("soccer",     "fra.1"),
#         "Liga MX":                      ("soccer",     "mex.1"),
#         "Champions League":             ("soccer",     "uefa.champions"),
#         "Europa League":                ("soccer",     "uefa.europa"),
#     },
#     "Motorsports": {
#         "Formula 1":                    ("racing",     "f1"),
#         "NASCAR Cup Series":            ("racing",     "nascar.cup"),
#     },
#     "Golf": {
#         "The Masters":                  ("golf",       "masters"),
#         "PGA Championship":             ("golf",       "pga"),
#         "US Open (Golf)":               ("golf",       "usopen"),
#         "The Open Championship":        ("golf",       "britishopen"),
#     },
#     "Tennis": {
#         "Wimbledon":                    ("tennis",     "wimbledon"),
#         "US Open (Tennis)":             ("tennis",     "usopen"),
#         "Australian Open":              ("tennis",     "australianopen"),
#         "French Open":                  ("tennis",     "frenchopen"),
#     },
# }

# # --- TSDB‐only leagues (free tier, ≤100 events/season) ---
# TSDB_LEAGUES_BY_SPORT = {
#     "Cycling": {
#         "UCI World Tour": "4465",
#         "UCI ProSeries":  "5330",
#     },
#     # add more TSDB‐only sports here as needed…
# }

# # --- Streamlit page config ---
# st.set_page_config(layout="wide")
# st.title("🏟️ Sports Hub")

# # --- Session state for user profile ---
# if 'selected_leagues' not in st.session_state:
#     st.session_state.selected_leagues = []

# # --- Sidebar navigation ---
# mode = st.sidebar.radio("Navigate to:", ["Profile", "News Feed", "Schedules"])

# if mode == "Profile":
#     st.header("👤 Your Profile: Choose Leagues")
#     st.write("Check the leagues you follow:")

#     # ESPN‐backed leagues
#     for sport, leagues in LEAGUES_BY_SPORT.items():
#         with st.expander(sport, expanded=False):
#             for league_name in leagues:
#                 key = f"profile_{league_name}"
#                 checked = league_name in st.session_state.selected_leagues
#                 new_val = st.checkbox(league_name, value=checked, key=key)
#                 if new_val and league_name not in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.append(league_name)
#                 if not new_val and league_name in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.remove(league_name)

#     # TSDB‐only leagues
#     for sport, leagues in TSDB_LEAGUES_BY_SPORT.items():
#         with st.expander(f"{sport} (via TheSportsDB)", expanded=False):
#             for league_name in leagues:
#                 key = f"profile_{league_name}"
#                 checked = league_name in st.session_state.selected_leagues
#                 new_val = st.checkbox(league_name, value=checked, key=key)
#                 if new_val and league_name not in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.append(league_name)
#                 if not new_val and league_name in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.remove(league_name)

#     st.markdown("**Selected Leagues:**")
#     st.write(st.session_state.selected_leagues)

# elif mode == "News Feed":
#     st.header("📰 Your Custom News Feed")
#     sel_leagues = st.session_state.selected_leagues
#     if not sel_leagues:
#         st.warning("Select some leagues in your Profile first to see news.")
#     else:
#         # Map selected leagues → sports
#         selected_sports = {
#             sport
#             for sport, leagues in LEAGUES_BY_SPORT.items()
#             if any(l in sel_leagues for l in leagues)
#         } | {
#             sport
#             for sport, leagues in TSDB_LEAGUES_BY_SPORT.items()
#             if any(l in sel_leagues for l in leagues)
#         }

#         # Gather RSS URLs for those sports
#         urls = []
#         for sport in selected_sports:
#             feeds = available_feeds.get(sport, {})
#             if isinstance(feeds, list):
#                 urls.extend(f['url'] for f in feeds)
#             else:
#                 for lst in feeds.values():
#                     urls.extend(f['url'] for f in lst)

#         renderMultipleNewsFeeds(urls, max_items_per_feed=10)

# else:  # Schedules
#     st.header("📅 Sports Schedules")
#     sel_leagues = st.session_state.selected_leagues
#     if not sel_leagues:
#         st.warning("Select some leagues in your Profile first to see schedules.")
#     else:
#         # Build lookups
#         espn_lookup = {
#             name: slugs
#             for leagues in LEAGUES_BY_SPORT.values()
#             for name, slugs in leagues.items()
#         }
#         tsdb_lookup = {
#             name: lid
#             for leagues in TSDB_LEAGUES_BY_SPORT.values()
#             for name, lid in leagues.items()
#         }

#         selected_date = st.sidebar.date_input("Select a date", value=date.today())
#         year_str = str(selected_date.year)

#         all_events = []
#         with st.spinner(f"Loading games for {selected_date}…"):
#             for league_name in sel_leagues:
#                 if league_name in espn_lookup:
#         # ESPN events
#                     s_slug, l_slug = espn_lookup[league_name]
#                     evs = get_espn_scoreboard(s_slug, l_slug, selected_date)
#                     for ev in evs:
#                         ev["league_name"] = league_name
#                         ev["league_id"]   = f"{s_slug}/{l_slug}"
#                     all_events.extend(evs)

#                 elif league_name in tsdb_lookup:
#         # TSDB events by season
#                     lid = tsdb_lookup[league_name]
#                     evs = get_tsdb_schedule_by_season(lid, year_str)
#                     for ev in evs:
#                         ev["league_name"] = league_name
#                         ev["league_id"]   = lid
#                     all_events.extend(evs)


#         # Sort and render
#         import datetime

# # old:
# # all_events.sort(key=lambda e: e.get("start_datetime") or datetime.datetime.min)

# # new:
#         def _event_ts(ev):
#             dt = ev.get("start_datetime")
#             if not dt:
#                 return float("-inf")
#     # if timezone‑aware, convert to UTC
#             if dt.tzinfo is not None:
#                 dt = dt.astimezone(datetime.timezone.utc)
#     # timestamp works for both naive and aware
#             return dt.timestamp()

#         all_events.sort(key=_event_ts)

#         if all_events:
#             st.sidebar.success(f"Fetched {len(all_events)} games across selected leagues")
#         else:
#             st.sidebar.warning("No games on this date for any selected league.")

#         renderScheduleCalendar(all_events, selected_date)


# app.py
import streamlit as st
from datetime import date, timedelta
from components.available_feeds import available_feeds
from components.newsFeed import renderMultipleNewsFeeds
from components.calendarView import renderScheduleCalendar
from components.api_client import get_espn_scoreboard, get_tsdb_schedule_by_season

# --- Mapping of sports to their supported ESPN leagues/slugs ---
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
    "Baseball": {
        "MLB": ("baseball", "mlb"),
    },
    "Hockey": {
        "NHL": ("hockey", "nhl"),
    },
    "Soccer": {
        "MLS": ("soccer", "usa.1"),
        "Premier League": ("soccer", "eng.1"),
        "La Liga": ("soccer", "esp.1"),
        "Bundesliga": ("soccer", "ger.1"),
        "Serie A": ("soccer", "ita.1"),
        "Ligue 1": ("soccer", "fra.1"),
        "Liga MX": ("soccer", "mex.1"),
        "Champions League": ("soccer", "uefa.champions"),
        "Europa League": ("soccer", "uefa.europa"),
    },
    "Motorsports": {
        "Formula 1": ("racing", "f1"),
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

# --- TSDB‐only leagues (free tier, ≤100 events/season) ---
TSDB_LEAGUES_BY_SPORT = {
    "Cycling": {
        "UCI World Tour": "4465",
        "UCI ProSeries": "5330",
    },
    # add more TSDB‐only sports here as needed…
}

# --- Streamlit page config ---
st.set_page_config(layout="wide")
st.title("🏟️ Sports Hub")

# --- Session state defaults ---
if "selected_leagues" not in st.session_state:
    st.session_state.selected_leagues = []
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# --- Sidebar navigation ---
mode = st.sidebar.radio("Navigate to:", ["Profile", "News Feed", "Schedules"])

# ————————————— PROFILE —————————————
if mode == "Profile":
    st.header("👤 Your Profile: Choose Leagues")
    st.write("Check the leagues you follow:")

    # ESPN-backed leagues
    for sport, leagues in LEAGUES_BY_SPORT.items():
        with st.expander(sport, expanded=False):
            for league_name in leagues:
                key = f"profile_{league_name}"
                checked = league_name in st.session_state.selected_leagues
                new_val = st.checkbox(league_name, value=checked, key=key)
                if new_val and league_name not in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.append(league_name)
                if not new_val and league_name in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.remove(league_name)

    # TSDB-only leagues
    for sport, leagues in TSDB_LEAGUES_BY_SPORT.items():
        with st.expander(f"{sport} (via TheSportsDB)", expanded=False):
            for league_name in leagues:
                key = f"profile_{league_name}"
                checked = league_name in st.session_state.selected_leagues
                new_val = st.checkbox(league_name, value=checked, key=key)
                if new_val and league_name not in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.append(league_name)
                if not new_val and league_name in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.remove(league_name)

    st.markdown("**Selected Leagues:**")
    st.write(st.session_state.selected_leagues)

# ————————————— NEWS FEED —————————————
elif mode == "News Feed":
    st.header("📰 Your Custom News Feed")

    # Reload button
    if st.sidebar.button("🔄 Reload News"):
        st.cache_data.clear()
        try:
            st.experimental_rerun()
        except AttributeError:
            st.sidebar.info("Cache cleared. Refresh your browser to reload.")

    sel_leagues = st.session_state.selected_leagues
    if not sel_leagues:
        st.warning("Select some leagues in your Profile first to see news.")
    else:
        # Derive sports from selected leagues
        selected_sports = {
            sport
            for sport, leagues in LEAGUES_BY_SPORT.items()
            if any(l in sel_leagues for l in leagues)
        } | {
            sport
            for sport, leagues in TSDB_LEAGUES_BY_SPORT.items()
            if any(l in sel_leagues for l in leagues)
        }

        # Gather RSS URLs
        urls = []
        for sport in selected_sports:
            feeds = available_feeds.get(sport, {})
            if isinstance(feeds, list):
                urls.extend(f["url"] for f in feeds)
            else:
                for lst in feeds.values():
                    urls.extend(f["url"] for f in lst)

        renderMultipleNewsFeeds(urls, max_items_per_feed=10)

# ————————————— SCHEDULES —————————————
else:
    st.header("📅 Sports Schedules")

    # Prev/Today/Next buttons
    prev_col, today_col, next_col = st.sidebar.columns([1, 1, 1])
    if prev_col.button("← Prev"):
        st.session_state.selected_date -= timedelta(days=1)
    if today_col.button("• Today"):
        st.session_state.selected_date = date.today()
    if next_col.button("Next →"):
        st.session_state.selected_date += timedelta(days=1)

    # Date picker for far‑future jumps
    st.sidebar.date_input(
        "Jump to date:", value=st.session_state.selected_date, key="selected_date"
    )

    sel_leagues = st.session_state.selected_leagues
    if not sel_leagues:
        st.warning("Select some leagues in your Profile first to see schedules.")
    else:
        # Build lookups
        espn_lookup = {
            name: slugs
            for leagues in LEAGUES_BY_SPORT.values()
            for name, slugs in leagues.items()
        }
        tsdb_lookup = {
            name: lid
            for leagues in TSDB_LEAGUES_BY_SPORT.values()
            for name, lid in leagues.items()
        }

        # Fetch and merge events
        all_events = []
        with st.spinner(f"Loading games for {st.session_state.selected_date}…"):
            year_str = str(st.session_state.selected_date.year)
            for league_name in sel_leagues:
                if league_name in espn_lookup:
                    s_slug, l_slug = espn_lookup[league_name]
                    evs = get_espn_scoreboard(
                        s_slug, l_slug, st.session_state.selected_date
                    )
                    for ev in evs:
                        ev["league_name"] = league_name
                    all_events.extend(evs)
                elif league_name in tsdb_lookup:
                    lid = tsdb_lookup[league_name]
                    evs = get_tsdb_schedule_by_season(lid, year_str)
                    for ev in evs:
                        ev["league_name"] = league_name
                    all_events.extend(evs)

        # Sort by timestamp to avoid tz-naive/aware issues
        import datetime as _dt

        def _event_ts(ev):
            dt = ev.get("start_datetime")
            if not dt:
                return float("-inf")
            if hasattr(dt, "tzinfo") and dt.tzinfo:
                dt = dt.astimezone(_dt.timezone.utc).replace(tzinfo=None)
            return dt.timestamp() if isinstance(dt, _dt.datetime) else float("-inf")

        all_events.sort(key=_event_ts)

        # Sidebar status
        if all_events:
            st.sidebar.success(
                f"Fetched {len(all_events)} games across selected leagues"
            )
        else:
            st.sidebar.warning("No games on this date for any selected league.")

        # Render calendar
        renderScheduleCalendar(all_events, st.session_state.selected_date)
