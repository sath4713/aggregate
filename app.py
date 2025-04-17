# # app.py
# import streamlit as st
# import logging

# # Import the new components
# from components.feedSelector import renderFeedSelector
# from components.newsFeed import renderMultipleNewsFeeds
# # available_feeds is used implicitly by feedSelector now

# # --- Basic Logging Configuration --- (Optional but recommended)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Streamlit App Layout ---
# st.set_page_config(layout="wide") # Use wide layout for better news display

# st.title("📰 Your Custom Sports News Feed")
# st.caption("Select your favorite feeds from the sidebar to build your personalized news stream.")

# # --- Sidebar for feed selection ---
# # The selector now manages its state via session_state and returns the selected list
# selected_urls = renderFeedSelector()

# # --- Main Area for Displaying Feeds ---
# # Pass the list of selected URLs to the rendering function
# renderMultipleNewsFeeds(selected_urls, max_items_per_feed=10) # Adjust max items per feed if needed

# --- Optional: Footer or other info ---
# st.sidebar.info("Your selections are saved for this session.")

# app.py
# import streamlit as st
# import logging
# import datetime

# # Import components
# from components.calendarView import renderScheduleCalendar
# # Import API client functions
# from components.api_client import get_schedule_by_league, get_espn_schedule, get_pyespn_schedule, PYESPN_AVAILABLE # Import new func and availability flag

# # --- Basic Logging Configuration ---
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # --- Streamlit App Layout ---
# st.set_page_config(layout="wide")
# st.title("📅 Sports Schedules")

# # --- Sidebar ---
# st.sidebar.header("Schedule Options")

# # --- Data Source Selection ---
# # Add 'pyespn Library' as an option if available
# source_options = ["ESPN Direct API", "TheSportsDB"]
# if PYESPN_AVAILABLE:
#     source_options.insert(0, "ESPN (pyespn Library)") # Add pyespn as first option if installed

# data_source = st.sidebar.radio("Select Data Source:", source_options, index=0)

# # --- League/Schedule Selection ---
# schedule_data = None

# if data_source == "ESPN (pyespn Library)":
#     st.sidebar.subheader("ESPN Leagues (via pyespn)")
#     # Use the league codes supported by pyespn from the docs
#     pyespn_league_codes = {
#         "NFL": "nfl",
#         "NBA": "nba",
#         "WNBA": "wnba",
#         "Men's College BBall": "mcbb",
#         "College Football": "cfb",
#         "College Baseball": "cbb",
#         "College Softball": "csb",
#         "Formula 1": "f1",
#         "NASCAR": "nascar",
#     }
#     selected_pyespn_league_name = st.sidebar.selectbox(
#         "Choose ESPN League:",
#         options=list(pyespn_league_codes.keys())
#     )
#     if selected_pyespn_league_name:
#          selected_code = pyespn_league_codes[selected_pyespn_league_name]
#          # Call the new pyespn API function
#          schedule_data = get_pyespn_schedule(selected_code)

# elif data_source == "ESPN Direct API":
#     st.sidebar.subheader("ESPN Leagues (via Direct API)")
#     # Use sport/league slugs for direct V2 API
#     espn_direct_options = {
#         "NFL": ("football", "nfl"),
#         "NBA": ("basketball", "nba"),
#         "WNBA": ("basketball", "wnba"),
#         "MLB": ("baseball", "mlb"),
#         "NHL": ("hockey", "nhl"),
#         "NCAAF": ("football", "ncaaf"),
#         "NCAAB": ("basketball", "mens-college-basketball"),
#         "WNBA": ("basketball", "wnba"),
#         "MLS (Soccer)": ("soccer", "usa.1"),
#         "Premier League (Soccer)": ("soccer", "eng.1"),
#         "La Liga (Soccer)": ("soccer", "esp.1"),
#         "Bundesliga (Soccer)": ("soccer", "ger.1"),
#         "Serie A (Soccer)": ("soccer", "ita.1"),
#         "Ligue 1 (Soccer)": ("soccer", "fra.1"),
#         "Liga MX (Soccer)": ("soccer", "mex.1"),
#         "Champions League (Soccer)": ("soccer", "uefa.champions"),
#         "Europa League (Soccer)": ("soccer", "uefa.europa"),
#         "Formula 1": ("racing", "f1"),
#         "NASCAR": ("racing", "nascar.cup"),
#         "Wimbledon (Tennis)": ("tennis", "wimbledon"),
#         "US Open (Tennis)": ("tennis", "usopen"),
#         "Australian Open (Tennis)": ("tennis", "australianopen"),
#         "French Open (Tennis)": ("tennis", "frenchopen"),
#         "Masters (Golf)": ("golf", "masters"),
#         "PGA Championship (Golf)": ("golf", "pga"),
#         "US Open (Golf)": ("golf", "usopen"),
#         "The Open Championship (Golf)": ("golf", "britishopen"),
#     }
#     selected_direct_league_name = st.sidebar.selectbox(
#         "Choose ESPN League:",
#         options=list(espn_direct_options.keys())
#     )
#     if selected_direct_league_name:
#          selected_sport_slug, selected_league_slug = espn_direct_options[selected_direct_league_name]
#          schedule_data = get_espn_schedule(selected_sport_slug, selected_league_slug) # Calls the direct API func

# elif data_source == "TheSportsDB":
#     st.sidebar.subheader("TheSportsDB Leagues")
#     # ... (TheSportsDB selection logic remains the same) ...
#     tsdb_league_options = { "NFL (USA)": "4391", "Premier League (Soccer)": "4328", "NBA (USA)": "4387", "MLB (USA)": "4424", "NHL (USA)": "4380" }
#     selected_tsdb_league_name = st.sidebar.selectbox( "Choose TheSportsDB League:", options=list(tsdb_league_options.keys()) )
#     selected_league_id = tsdb_league_options[selected_tsdb_league_name]
#     current_year = datetime.date.today().year
#     selected_season = st.sidebar.text_input("Enter Season (e.g., 2024):", value=str(current_year))
#     if selected_league_id:
#         if st.secrets.get("THESPORTSDB_API_KEY"): schedule_data = get_schedule_by_league(selected_league_id, selected_season)
#         else: st.sidebar.error("API Key for TheSportsDB is missing in secrets.")


# # --- Main Area - Display Schedule Calendar ---
# renderScheduleCalendar(schedule_data)

# app.py
# app.py
# app.py
# app.py
import streamlit as st
from datetime import date
from components.available_feeds import available_feeds
from components.newsFeed import renderMultipleNewsFeeds
from components.calendarView import renderScheduleCalendar
from components.api_client import get_espn_scoreboard

# --- Mapping of sports to their supported schedule leagues/slugs ---
LEAGUES_BY_SPORT = {
    "Basketball": {
        "NBA":                          ("basketball", "nba"),
        "WNBA":                         ("basketball", "wnba"),
        "NCAAM (Men's College BBall)":  ("basketball", "mens-college-basketball"),
        "NCAAW (Women's College BBall)":("basketball", "womens-college-basketball"),
    },
    "Football": {
        "NFL":                          ("football",   "nfl"),
        "NCAAF (College Football)":     ("football",   "college-football"),
    },
    "Baseball": {
        "MLB":                          ("baseball",   "mlb"),
    },
    "Hockey": {
        "NHL":                          ("hockey",     "nhl"),
    },
    "Soccer": {
        "MLS":                          ("soccer",     "usa.1"),
        "Premier League":               ("soccer",     "eng.1"),
        "La Liga":                      ("soccer",     "esp.1"),
        "Bundesliga":                   ("soccer",     "ger.1"),
        "Serie A":                      ("soccer",     "ita.1"),
        "Ligue 1":                      ("soccer",     "fra.1"),
        "Liga MX":                      ("soccer",     "mex.1"),
        "Champions League":             ("soccer",     "uefa.champions"),
        "Europa League":                ("soccer",     "uefa.europa"),
    },
    "Motorsports": {
        "Formula 1":                    ("racing",     "f1"),
        "NASCAR Cup Series":            ("racing",     "nascar.cup"),
    },
    "Golf": {
        "The Masters":                  ("golf",       "masters"),
        "PGA Championship":             ("golf",       "pga"),
        "US Open (Golf)":               ("golf",       "usopen"),
        "The Open Championship":        ("golf",       "britishopen"),
    },
    "Tennis": {
        "Wimbledon":                    ("tennis",     "wimbledon"),
        "US Open (Tennis)":             ("tennis",     "usopen"),
        "Australian Open":              ("tennis",     "australianopen"),
        "French Open":                  ("tennis",     "frenchopen"),
    },
}

# --- Streamlit page config ---
st.set_page_config(layout="wide")
st.title("🏟️ Sports Hub")

# --- Session state for profile ---
if 'selected_leagues' not in st.session_state:
    st.session_state.selected_leagues = []

# --- Sidebar navigation ---
mode = st.sidebar.radio("Navigate to:", ["Profile", "News Feed", "Schedules"])

if mode == "Profile":
    st.header("👤 Your Profile: Choose Leagues")
    st.write("Check the leagues you follow:")
    # Group by sport
    for sport, leagues in LEAGUES_BY_SPORT.items():
        with st.expander(sport, expanded=True):
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

elif mode == "News Feed":
    st.header("📰 Your Custom News Feed")

    sel_leagues = st.session_state.selected_leagues
    if not sel_leagues:
        st.warning("Select some leagues in your Profile first to see news.")
    else:
        # Map selected leagues back to sports
        selected_sports = {
            sport
            for sport, leagues in LEAGUES_BY_SPORT.items()
            if any(l in sel_leagues for l in leagues)
        }

        # Gather all RSS URLs for those sports
        urls = []
        for sport in selected_sports:
            feeds = available_feeds.get(sport, {})
            if isinstance(feeds, list):
                urls.extend(feed['url'] for feed in feeds)
            elif isinstance(feeds, dict):
                for league_feeds in feeds.values():
                    urls.extend(feed['url'] for feed in league_feeds)

        renderMultipleNewsFeeds(urls, max_items_per_feed=10)

else:  # Schedules
    st.header("📅 Sports Schedules")

    sel_leagues = st.session_state.selected_leagues
    if not sel_leagues:
        st.warning("Select some leagues in your Profile first to see schedules.")
    else:
        # Flatten league → slug lookup
        league_lookup = {
            name: slugs
            for leagues in LEAGUES_BY_SPORT.values()
            for name, slugs in leagues.items()
        }

        selected_date = st.sidebar.date_input("Select a date", value=date.today())

        schedule_data = []
        with st.spinner(f"Loading games for {selected_date}…"):
            for league_name in sel_leagues:
                sport_slug, league_slug = league_lookup[league_name]
                games = get_espn_scoreboard(sport_slug, league_slug, selected_date)
                for ev in games:
                    ev["league_name"] = league_name
                schedule_data.extend(games)

        # Sort by kickoff
        import datetime
        schedule_data.sort(key=lambda x: x.get("start_datetime") or datetime.datetime.min)

        if schedule_data:
            st.sidebar.success(f"Fetched {len(schedule_data)} games across {len(sel_leagues)} leagues")
        else:
            st.sidebar.warning("No games on this date for any selected league.")

        renderScheduleCalendar(schedule_data, selected_date)
