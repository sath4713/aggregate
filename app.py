# app.py

import streamlit as st
from datetime import date, timedelta
import datetime as _dt
import os, json
from dateutil.tz import tzlocal

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
# Next Event Up Helper
# ——————————————
# Dynamically searches forward from `start` up to 365 days for the next event in the given league.
def get_next_event(league: str, start: date) -> dict | None:
    for offset in range(100):
        day = start + timedelta(days=offset)
        if league in PCS_LEAGUES:
            evs = get_pcs_events_by_day(day, PCS_LEAGUES[league])
        elif league in ESPN_LEAGUES_FLAT:
            sport, slug = ESPN_LEAGUES_FLAT[league]
            evs = get_espn_scoreboard(sport, slug, day)
        elif league == "Diamond League":
            evs = get_diamond_league_events_by_day(day)
        elif league == "World Marathon Majors":
            evs = get_marathon_majors_by_day(day)
        elif league == "World Athletics Championships":
            evs = get_wa_champs_by_day(day)
        else:
            evs = []
        if evs:
            # return the earliest event of that day
            evs.sort(key=lambda e: e.get("start_datetime") or _dt.datetime.min)
            return evs[0]
    return None


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

# near the top of app.py, alongside PCS_LEAGUES…
GRAND_TOUR_SLUGS = {
    "Giro d’Italia": "giro-d-italia",
    "Tour de France": "tour-de-france",
    "Vuelta a España": "vuelta-a-espana",
}

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
st.title("🏟️ Sports")

# initialize or load session_state
if "selected_leagues" not in st.session_state:
    st.session_state.selected_leagues = load_profile()
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# top‐level tabs
tabs = st.tabs(["📰 News Feed", "📅 Schedules", "👤 Profile"])
news_tab, sched_tab, profile_tab = tabs


# ——————————————
# 1) NEWS FEED TAB
# ——————————————
with news_tab:

    if st.button("🔄 Reload News"):
        st.cache_data.clear()
        st.rerun()

    sel = st.session_state.selected_leagues
    if not sel:
        st.info("Select leagues in Profile to see news.")
    else:
        # build your URL list exactly as before
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

        renderMultipleNewsFeeds(urls, max_items_per_feed=4)

# ——————————————
# 2) SCHEDULES TAB
# ——————————————
with sched_tab:

    # ← Prev • Today • Next →
    c1, c2, c3 = st.columns(3)
    if c1.button("← Prev"):
        st.session_state.selected_date -= timedelta(days=1)
    if c2.button("Today"):
        st.session_state.selected_date = date.today()
    if c3.button("Next →"):
        st.session_state.selected_date += timedelta(days=1)

    # — Sidebar controls (only on Schedules tab) —
    with st.sidebar:
        sel_date = st.date_input("Jump to date", value=st.session_state.selected_date)
        sel = st.session_state.selected_leagues
        if sel:
            view_choice = st.radio("View:", ["All"] + sel)
        else:
            st.write("No leagues selected yet.")
            view_choice = "All"

    # — Main pane —
    if not sel:
        st.warning("Select leagues in Profile to see schedules.")
    else:
        # Fetch & normalize day's events
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

        # Convert all to naive local datetimes
        local_tz = _dt.datetime.now().astimezone().tzinfo
        for e in day_events:
            dt = e.get("start_datetime")
            if dt:
                if dt.tzinfo:
                    dt = dt.astimezone(local_tz)
                else:
                    dt = dt.replace(tzinfo=local_tz)
                e["start_datetime"] = dt.replace(tzinfo=None)

        # Sort & filter by view_choice
        day_events.sort(
            key=lambda e: (
                e.get("start_datetime").timestamp() if e.get("start_datetime") else 0
            )
        )
        subset = (
            day_events
            if view_choice == "All"
            else [e for e in day_events if e["league_name"] == view_choice]
        )

        # Render calendar
        renderScheduleCalendar(subset, sel_date)

        # Next Event Up (in-tab)
        next_ev = get_next_event(view_choice, date.today())
        if next_ev:
            ev_dt = next_ev["start_datetime"]
            if ev_dt.tzinfo:
                ev_dt = ev_dt.astimezone(tzlocal())
            else:
                ev_dt = ev_dt.replace(tzinfo=tzlocal())
            ev_dt = ev_dt.replace(tzinfo=None)

            date_str = ev_dt.strftime("%-m/%-d")
            time_str = ev_dt.strftime("%I:%M %p")
            name = (
                next_ev.get("title")
                or f"{next_ev.get('away_team','')} at {next_ev.get('home_team','')}"
            )

            st.markdown("### Next Event Up")
            st.write(f"**{name}** — {date_str} – {time_str}")
            if url := next_ev.get("url"):
                st.write(f"[More info]({url})")


# ——————————————
# 3) PROFILE TAB
# ——————————————
with profile_tab:
    st.header("👤 Your Profile")
    if st.button("🔄 Reset Profile"):
        reset_profile()

    st.write("Select the leagues you follow:")

    # Existing sports expanders
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

    # PCS-specific cycling leagues
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
