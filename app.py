# import streamlit as st
# from datetime import date, timedelta
# import datetime as _dt
# import os, json

# from components.available_feeds import available_feeds
# from components.newsFeed import renderMultipleNewsFeeds
# from components.calendarView import renderScheduleCalendar
# from components.api_client import (
#     get_espn_scoreboard,
#     get_pcs_events_by_day,
#     get_marathon_majors_by_day,
#     get_wa_champs_by_day,
#     get_world_athletics_by_day,
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


# def reset_profile():
#     if os.path.exists(PROFILE_PATH):
#         os.remove(PROFILE_PATH)
#     st.session_state.selected_leagues = []
#     for key in list(st.session_state.keys()):
#         if key.startswith("profile_"):
#             del st.session_state[key]
#     st.rerun()


# # ——————————————
# # League mappings
# # ——————————————
# # ESPN: map display name → (api_sport, api_league)
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
#     "Baseball": {"MLB": ("baseball", "mlb")},
#     "Hockey": {"NHL": ("hockey", "nhl")},
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
#     "Running": {
#         "World Marathon Majors": ("running", "marathon"),
#         "World Athletics Championships": ("running", "wachamps"),
#         "World Athletics Calendar": ("None", None),
#     },
# }

# # PCS: map display name → PCS classification code
# PCS_LEAGUES = {
#     "UCI WorldTour": "1.uwt",
#     "UCI ProSeries": "2.pro",
# }

# # Flatten ESPN lookup: league_name → (api_sport, api_league)
# ESPN_LEAGUES_FLAT = {
#     league: (api_sport, api_slug)
#     for _, leagues in LEAGUES_BY_SPORT.items()
#     for league, (api_sport, api_slug) in leagues.items()
# }

# # ——————————————
# # Streamlit setup
# # ——————————————
# st.set_page_config(layout="wide")
# st.title("🏟️ Sports Hub")

# if "selected_leagues" not in st.session_state:
#     st.session_state.selected_leagues = load_profile()
# if "selected_date" not in st.session_state:
#     st.session_state.selected_date = date.today()

# tabs = st.tabs(["📰 News Feed", "📅 Schedules", "👤 Profile"])
# news_tab, sched_tab, profile_tab = tabs

# # ——————————————
# # 1) NEWS FEED TAB
# # ——————————————
# with news_tab:
#     st.header("📰 Your Custom News Feed")
#     if st.button("🔄 Reload News"):
#         st.cache_data.clear()
#         st.rerun()

#     sel = st.session_state.selected_leagues
#     if not sel:
#         st.info("Select leagues in Profile to see news.")
#     else:
#         # collect the sports (keys in available_feeds) that correspond
#         # to any selected ESPN league, plus Cycling if any PCS league selected
#         sports_to_show = {
#             sport_name
#             for sport_name, leagues in LEAGUES_BY_SPORT.items()
#             if any(l in sel for l in leagues)
#         }
#         if any(l in PCS_LEAGUES for l in sel):
#             sports_to_show.add("Cycling")

#         urls = []
#         for sport_name in sports_to_show:
#             feeds = available_feeds.get(sport_name)
#             if not feeds:
#                 continue
#             if isinstance(feeds, list):
#                 urls += [f["url"] for f in feeds]
#             else:
#                 for lst in feeds.values():
#                     urls += [f["url"] for f in lst]

#         renderMultipleNewsFeeds(urls, max_items_per_feed=10)


# # ——————————————
# # 2) SCHEDULES TAB
# # ——————————————
# with sched_tab:
#     st.header("📅 Sports Schedules")

#     prev_c, today_c, next_c = st.columns(3)
#     if prev_c.button("← Prev"):
#         st.session_state.selected_date -= timedelta(days=1)
#     if today_c.button("• Today"):
#         st.session_state.selected_date = date.today()
#     if next_c.button("Next →"):
#         st.session_state.selected_date += timedelta(days=1)

#     sel_date = st.sidebar.date_input(
#         "Jump to date", value=st.session_state.selected_date
#     )
#     sel = st.session_state.selected_leagues

#     if not sel:
#         st.warning("Select leagues in Profile to see schedules.")
#     else:
#         view_opts = ["All"] + sel
#         view_choice = st.sidebar.radio("View:", view_opts, index=0)

#         # fetch everything for that day
#         day_events: list[dict] = []
#         with st.spinner(f"Loading events for {sel_date}…"):
#             for league in sel:
#                 # PCS
#                 if league in PCS_LEAGUES:
#                     code = PCS_LEAGUES[league]
#                     evs = get_pcs_events_by_day(sel_date, code)
#                 # ESPN
#                 elif league in ESPN_LEAGUES_FLAT:
#                     api_sport, api_slug = ESPN_LEAGUES_FLAT[league]
#                     evs = get_espn_scoreboard(api_sport, api_slug, sel_date)
#                 else:
#                     evs = []

#                 for e in evs:
#                     e["league_name"] = league
#                 day_events.extend(evs)

#         # sort by datetime
#         day_events.sort(
#             key=lambda e: (
#                 e.get("start_datetime").timestamp() if e.get("start_datetime") else -1
#             )
#         )

#         # render calendar
#         if view_choice == "All":
#             renderScheduleCalendar(day_events, sel_date)
#         else:
#             subset = [e for e in day_events if e["league_name"] == view_choice]
#             renderScheduleCalendar(subset, sel_date)


# # ——————————————
# # 3) PROFILE TAB
# # ——————————————
# with profile_tab:
#     st.header("👤 Your Profile")
#     if st.button("🔄 Reset Profile"):
#         reset_profile()

#     st.write("Select the leagues you follow:")

#     for sport_name, leagues in LEAGUES_BY_SPORT.items():
#         with st.expander(sport_name, expanded=True):
#             for league in leagues:
#                 key = f"profile_{league}"
#                 checked = league in st.session_state.selected_leagues
#                 new = st.checkbox(league, value=checked, key=key)
#                 if new and league not in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.append(league)
#                 if not new and league in st.session_state.selected_leagues:
#                     st.session_state.selected_leagues.remove(league)

#     with st.expander("Cycling (PCS)", expanded=True):
#         for league in PCS_LEAGUES:
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
#         st.success("Profile saved for next time!")


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
    get_diamond_league_events_by_day,
    get_marathon_majors_by_day,
    get_wa_champs_by_day,
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
    except:
        return []


def save_profile(leagues: list[str]):
    os.makedirs(PROFILE_DIR, exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        json.dump(leagues, f)


def reset_profile():
    if os.path.exists(PROFILE_PATH):
        os.remove(PROFILE_PATH)
    st.session_state.selected_leagues = []
    for key in list(st.session_state.keys()):
        if key.startswith("profile_"):
            del st.session_state[key]
    st.rerun()


# ——————————————
# League mappings
# ——————————————
LEAGUES_BY_SPORT = {
    "Basketball": {
        "NBA": ("basketball", "nba"),
        "WNBA": ("basketball", "wnba"),
        "NCAAM": ("basketball", "mens-college-basketball"),
        "NCAAW": ("basketball", "womens-college-basketball"),
    },
    "Football": {
        "NFL": ("football", "nfl"),
        "NCAAF": ("football", "college-football"),
    },
    "Baseball": {"MLB": ("baseball", "mlb")},
    "Hockey": {"NHL": ("hockey", "nhl")},
    "Soccer": {
        "MLS": ("soccer", "usa.1"),
        "Premier League": ("soccer", "eng.1"),
        # ... other soccer ...
    },
    "Motorsports": {
        "Formula 1": ("racing", "f1"),
        "NASCAR Cup Series": ("racing", "nascar.cup"),
    },
    "Tennis": {
        "Wimbledon": ("tennis", "wimbledon"),
        "US Open": ("tennis", "usopen"),
        # ... other tennis ...
    },
    # ——— ADD ATHLETICS SECTION ———
    "Athletics": {
        "Diamond League": (None, None),
        "World Marathon Majors": (None, None),
        "World Athletics Championships": (None, None),
    },
}

PCS_LEAGUES = {
    "UCI WorldTour": "1.uwt",
    "UCI ProSeries": "2.pro",
}

# flatten ESPN lookups
ESPN_LEAGUES_FLAT = {
    league: (api_sport, api_slug)
    for _, leagues in LEAGUES_BY_SPORT.items()
    for league, (api_sport, api_slug) in leagues.items()
    if api_sport
}

# ——————————————
# Streamlit setup
# ——————————————
st.set_page_config(layout="wide")
st.title("🏟️ Sports Hub")

if "selected_leagues" not in st.session_state:
    st.session_state.selected_leagues = load_profile()
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

tabs = st.tabs(["📰 News Feed", "📅 Schedules", "👤 Profile"])
news_tab, sched_tab, profile_tab = tabs

# ——————————————
# 1) NEWS FEED TAB
# ——————————————
with news_tab:
    st.header("📰 Your Custom News Feed")
    if st.button("🔄 Reload News"):
        st.cache_data.clear()
        st.rerun()

    sel = st.session_state.selected_leagues
    if not sel:
        st.info("Select leagues in Profile to see news.")
    else:
        sports_to_show = {
            sport_name
            for sport_name, leagues in LEAGUES_BY_SPORT.items()
            if any(l in sel for l in leagues)
        }
        if any(l in PCS_LEAGUES for l in sel):
            sports_to_show.add("Cycling")

        urls = []
        for sport_name in sports_to_show:
            feeds = available_feeds.get(sport_name)
            if not feeds:
                continue
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

    prev_c, today_c, next_c = st.columns(3)
    if prev_c.button("← Prev"):
        st.session_state.selected_date -= timedelta(days=1)
    if today_c.button("• Today"):
        st.session_state.selected_date = date.today()
    if next_c.button("Next →"):
        st.session_state.selected_date += timedelta(days=1)

    sel_date = st.sidebar.date_input(
        "Jump to date", value=st.session_state.selected_date
    )
    sel = st.session_state.selected_leagues

    if not sel:
        st.warning("Select leagues in Profile to see schedules.")
    else:
        view_opts = ["All"] + sel
        view_choice = st.sidebar.radio("View:", view_opts, index=0)

        day_events: list[dict] = []
        with st.spinner(f"Loading events for {sel_date}…"):
            for league in sel:
                if league in PCS_LEAGUES:
                    evs = get_pcs_events_by_day(sel_date, PCS_LEAGUES[league])
                elif league in ESPN_LEAGUES_FLAT:
                    sport, slug = ESPN_LEAGUES_FLAT[league]
                    evs = get_espn_scoreboard(sport, slug, sel_date)
                elif league == "Diamond League":
                    evs = get_diamond_league_events_by_day(sel_date)
                elif league == "World Marathon Majors":
                    evs = get_marathon_majors_by_day(sel_date)
                elif league == "World Athletics Championships":
                    evs = get_wa_champs_by_day(sel_date)
                else:
                    evs = []

                for e in evs:
                    e["league_name"] = league
                day_events.extend(evs)

        day_events.sort(
            key=lambda e: (
                e.get("start_datetime").timestamp() if e.get("start_datetime") else -1
            )
        )

        if view_choice == "All":
            renderScheduleCalendar(day_events, sel_date)
        else:
            subset = [e for e in day_events if e["league_name"] == view_choice]
            renderScheduleCalendar(subset, sel_date)

# ——————————————
# 3) PROFILE TAB
# ——————————————
with profile_tab:
    st.header("👤 Your Profile")
    if st.button("🔄 Reset Profile"):
        reset_profile()

    st.write("Select the leagues you follow:")
    for sport_name, leagues in LEAGUES_BY_SPORT.items():
        with st.expander(sport_name, expanded=True):
            for league in leagues:
                key = f"profile_{league}"
                checked = league in st.session_state.selected_leagues
                new = st.checkbox(league, value=checked, key=key)
                if new and league not in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.append(league)
                if not new and league in st.session_state.selected_leagues:
                    st.session_state.selected_leagues.remove(league)
    with st.expander("Cycling (PCS)", expanded=True):
        for league in PCS_LEAGUES:
            key = f"profile_{league}"
            checked = league in st.session_state.selected_leagues
            new = st.checkbox(league, value=checked, key=key)
            if new and league not in st.session_state.selected_leagues:
                st.session_state.selected_leagues.append(league)
            if not new and league in st.session_state.selected_leagues:
                st.session_state.selected_leagues.remove(league)

    st.markdown("**Your Selected Leagues:**")
    st.write(st.session_state.selected_leagues)

    if st.button("💾 Save Profile"):
        save_profile(st.session_state.selected_leagues)
        st.success("Profile saved for next time!")
