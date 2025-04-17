# # components/api_client.py
# import streamlit as st
# import requests
# import logging
# import datetime
# from dateutil import parser
# # Import the new library
# try:
#     from pyespn import PYESPN
#     PYESPN_AVAILABLE = True
# except ImportError:
#     PYESPN_AVAILABLE = False
#     logging.warning("pyespn library not found. ESPN schedule fetching via pyespn will be unavailable.")

# # Keep get_schedule_by_league (TheSportsDB) function...
# # Keep get_espn_schedule (direct V2 API call) function...


# # --- NEW Function using pyespn library ---
# @st.cache_data(ttl=1800) # Cache for 30 minutes
# def get_pyespn_schedule(sport_league_code: str) -> list | None:
#     """
#     Fetches schedule data for a specific league using the pyespn library.

#     Args:
#         sport_league_code (str): The league code supported by pyespn
#                                  (e.g., 'nfl', 'nba', 'cfb', 'mcbb').

#     Returns:
#         list | None: A list of event dictionaries in our standard format, or None on error.
#     """
#     if not PYESPN_AVAILABLE:
#         st.error("The 'pyespn' library is not installed. Cannot fetch ESPN schedules with this method.")
#         return None

#     logging.info(f"Fetching schedule using pyespn for: {sport_league_code}")
#     all_events_transformed = []

#     try:
#         # 1. Initialize the client
#         client = PYESPN(sport_league=sport_league_code)

#         # 2. Access the schedule
#         # --- !!! IMPORTANT !!! ---
#         # How to get the Schedule object is not explicit in the provided docs.
#         # We need to *assume* how it's accessed. Common patterns:
#         # Option A: client.schedule
#         # Option B: client.get_schedule()
#         # Option C: client.league.schedule (less likely based on attributes)
#         # Let's *try* Option A, but this might need adjustment after testing.
#         try:
#              schedule_obj = client.schedule # <<<< ASSUMPTION HERE
#              if schedule_obj is None:
#                  # Maybe it needs to be explicitly loaded?
#                  # schedule_obj = client.load_schedule() # <<<< Alternative Assumption
#                  # Or maybe it's under league?
#                  # schedule_obj = client.league.schedule # <<<< Another Assumption
#                  # If none work, we cannot proceed with this library easily.
#                  raise AttributeError("Could not find schedule object via assumed attributes (.schedule, .league.schedule)")

#         except AttributeError as e:
#              logging.error(f"Could not access schedule object from PYESPN client: {e}. The library structure might differ from assumptions.")
#              st.error(f"Error accessing schedule data structure within pyespn for {sport_league_code}.")
#              return None
#         except Exception as e: # Catch other potential init/load errors
#             logging.error(f"Error initializing or loading schedule in pyespn for {sport_league_code}: {e}")
#             st.error(f"Failed to load schedule via pyespn: {e}")
#             return None


#         # 3. Iterate through weeks and events
#         if not hasattr(schedule_obj, 'weeks') or not hasattr(schedule_obj, 'get_events'):
#              logging.error("The retrieved schedule object lacks expected 'weeks' or 'get_events' method.")
#              st.error("Schedule data format from pyespn is not as expected.")
#              return None

#         for week in schedule_obj.weeks:
#             try:
#                 # Assuming week object has a 'number' attribute or similar
#                 week_num = week.number # <<<< ASSUMPTION
#                 events_this_week = schedule_obj.get_events(week_num)

#                 for event in events_this_week:
#                     # 4. Extract data from the Event object
#                     # --- !!! MORE ASSUMPTIONS !!! ---
#                     # We need to guess the attributes of the Event object.
#                     # Common names will be tried. This NEEDS verification.
#                     try:
#                         event_id = getattr(event, 'id', None) or getattr(event, 'event_id', None)
#                         event_name = getattr(event, 'name', 'Unknown Event')
#                         event_date_raw = getattr(event, 'date', None) or getattr(event, 'event_date', None)
#                         status_obj = getattr(event, 'status', None) # Might be an object or string
#                         competitors = getattr(event, 'competitors', []) # Expecting list/dict
#                         venue_obj = getattr(event, 'venue', None) # Might be an object or string

#                         # Parse date robustly
#                         event_datetime_utc = None
#                         if isinstance(event_date_raw, datetime.datetime):
#                             event_datetime_utc = event_date_raw # Assume timezone aware if datetime obj
#                         elif isinstance(event_date_raw, str):
#                              try:
#                                  event_datetime_utc = parser.parse(event_date_raw) # Use parser for flexibility
#                              except ValueError:
#                                  logging.warning(f"Could not parse date string: {event_date_raw} for event {event_id}")
#                                  continue # Skip event if date is unusable
#                         else:
#                              logging.warning(f"Unknown date format: {event_date_raw} for event {event_id}")
#                              continue # Skip event

#                         # Process status (needs inspection of actual status_obj)
#                         status = "STATUS_SCHEDULED" # Default
#                         status_detail = ""
#                         if isinstance(status_obj, str):
#                            status_detail = status_obj # Assume simple string status?
#                            # Might need mapping: if 'Final' in status_obj: status = 'STATUS_FINAL'
#                         elif hasattr(status_obj, 'type') and hasattr(status_obj.type, 'short_detail'):
#                            status = getattr(status_obj.type, 'name', status) # e.g., STATUS_FINAL
#                            status_detail = getattr(status_obj.type, 'short_detail', status)


#                         # Process competitors (needs inspection of actual competitors structure)
#                         home_team_name = "TBD"
#                         away_team_name = "TBD"
#                         home_score = None
#                         away_score = None
#                         if isinstance(competitors, list) and len(competitors) == 2:
#                             # Assuming list of competitor objects/dicts
#                             c1 = competitors[0]
#                             c2 = competitors[1]
#                             # Assuming they have 'homeAway' and 'team' attributes
#                             if getattr(c1, 'homeAway', '') == 'home' or getattr(c1, 'home_away', '') == 'home':
#                                 home_team_name = getattr(c1.team, 'name', 'TBD') if hasattr(c1, 'team') else 'TBD'
#                                 home_score = getattr(c1, 'score', None)
#                                 away_team_name = getattr(c2.team, 'name', 'TBD') if hasattr(c2, 'team') else 'TBD'
#                                 away_score = getattr(c2, 'score', None)
#                             else: # Assume c2 is home
#                                 home_team_name = getattr(c2.team, 'name', 'TBD') if hasattr(c2, 'team') else 'TBD'
#                                 home_score = getattr(c2, 'score', None)
#                                 away_team_name = getattr(c1.team, 'name', 'TBD') if hasattr(c1, 'team') else 'TBD'
#                                 away_score = getattr(c1, 'score', None)

#                         # Process venue
#                         venue_name = None
#                         if isinstance(venue_obj, str):
#                             venue_name = venue_obj
#                         elif hasattr(venue_obj, 'name'):
#                             venue_name = getattr(venue_obj, 'name', None)


#                         result_str = None
#                         if status == 'STATUS_FINAL' or 'Final' in status_detail:
#                             result_str = f"{home_score} - {away_score}" if home_score and away_score else "Final"


#                         # 5. Transform into standard dictionary
#                         all_events_transformed.append({
#                             'id': event_id,
#                             'title': event_name,
#                             'league': client.league.name if hasattr(client, 'league') else sport_league_code.upper(), # Get league name from client if possible
#                             'home_team': home_team_name,
#                             'away_team': away_team_name,
#                             'start_datetime': event_datetime_utc,
#                             'venue': venue_name,
#                             'status': status_detail or status,
#                             'result': result_str,
#                             'url': getattr(event, 'url', None) # Guessing attribute name for URL
#                         })

#                     except Exception as parse_err:
#                         logging.warning(f"Failed to parse details for an event in week {week_num} for {sport_league_code}: {parse_err}")
#                         continue # Skip this event

#             except StopIteration:
#                  logging.info(f"No Week object found for week number {week_num} (StopIteration).")
#                  # This might happen if week numbers are not sequential or get_events expects something else
#                  continue
#             except Exception as week_err:
#                 logging.error(f"Error processing week {getattr(week, 'number', '?')} for {sport_league_code}: {week_err}")
#                 continue # Skip week on error

#         # 6. Sort by date
#         all_events_transformed.sort(key=lambda x: x['start_datetime'] if x['start_datetime'] else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc))

#         return all_events_transformed

#     except Exception as e:
#         st.error(f"Failed to get schedule via pyespn for {sport_league_code}: {e}")
#         logging.error(f"Pyespn schedule fetch failed for {sport_league_code}: {e}", exc_info=True)
#         return None

import streamlit as st
import requests, logging
import datetime
from dateutil import parser

@st.cache_data(ttl=300)
def get_espn_scoreboard(sport: str, league: str, dt: datetime.date) -> list[dict]:
    """
    Fetches games on a specific date from ESPN's V2 scoreboard endpoint,
    and returns a list of normalized event dicts.
    """
    # ESPN wants YYYYMMDD
    date_str = dt.strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard?dates={date_str}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logging.error(f"Scoreboard fetch failed: {e}", exc_info=True)
        return []

    events = data.get("events", [])
    out = []
    for ev in events:
        comp = ev.get("competitions", [{}])[0]
        # parse time
        try:
            dt_obj = parser.parse(ev.get("date"))
        except:
            dt_obj = None

        # find home/away
        comps = comp.get("competitors", [])
        home = next((c for c in comps if c.get("homeAway")=="home"), {})
        away = next((c for c in comps if c.get("homeAway")=="away"), {})

        # status/result
        stype = comp.get("status",{}).get("type",{})
        status = stype.get("shortDetail","Scheduled")
        result = None
        if "Final" in status or stype.get("completed"):
            hs = home.get("score"); as_ = away.get("score")
            if hs is not None and as_ is not None:
                result = f"{hs} – {as_}"

        venue = comp.get("venue",{}).get("fullName","")

        out.append({
            "id":             ev.get("id"),
            "home_team":      home.get("team",{}).get("displayName","TBD"),
            "away_team":      away.get("team",{}).get("displayName","TBD"),
            "start_datetime": dt_obj,
            "venue":          venue,
            "status":         status,
            "result":         result,
            "url":            (ev.get("links") or [{}])[0].get("href"),
        })

    return out
