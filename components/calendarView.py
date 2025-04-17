
# import streamlit as st
# from dateutil import parser
# from dateutil.tz import tzlocal
# from datetime import date

# def renderScheduleCalendar(schedule_data=None, selected_date: date | None = None):
#     st.subheader("Sports Schedule Calendar")

#     if schedule_data is None:
#         st.info("Please select a league in the sidebar to view the schedule.")
#         return

#     if selected_date is None:
#         selected_date = date.today()

#     st.write(f"### Schedule for {selected_date.strftime('%Y-%m-%d')}")

#     found = False
#     for ev in schedule_data:
#         ev_dt = ev.get("start_datetime")
#         if not ev_dt:
#             continue

#         # Normalize & convert to local
#         if isinstance(ev_dt, str):
#             ev_dt = parser.parse(ev_dt)
#         if ev_dt.tzinfo:
#             ev_dt = ev_dt.astimezone(tzlocal())
#         if ev_dt.date() != selected_date:
#             continue

#         found = True
#         title  = ev.get("title")           # TSDB single‑event name
#         home   = ev.get("home_team")
#         away   = ev.get("away_team")
#         status = ev.get("status", "")
#         result = ev.get("result", "")
#         venue  = ev.get("venue", "")
#         league = ev.get("league_name", "")
#         time_str = ev_dt.strftime("%I:%M %p")

#         # If it's a title‑only event (no home/away), render full‑width
#         if title and not home and not away:
#             st.markdown(f"## {title}")
#             meta = f"*Time:* {time_str}"
#             if league:
#                 meta += f"  •  *League:* {league}"
#             st.markdown(meta)
#             st.divider()
#             continue

#         # Otherwise, render the standard 4‑column layout
#         c1, c2, c3, c4 = st.columns([3, 1, 3, 2])
#         with c1:
#             st.markdown(f"**{away or 'TBD'}**")
#         with c2:
#             st.markdown("vs")
#         with c3:
#             st.markdown(f"**{home or 'TBD'}**")
#         with c4:
#             st.markdown(result or status or "")

#         # Build the meta line
#         meta = f"*Time:* {time_str}"
#         if venue:
#             meta += f"  •  *Venue:* {venue}"
#         if league:
#             meta += f"  •  *League:* {league}"
#         if ev.get("network"):
#             meta += f"  •  *TV:* {ev['network']}"
#         st.markdown(meta)
#         st.divider()

#     if not found:
#         st.warning("No games scheduled for this date.")


# components/calendarView.py

import streamlit as st
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import date

def renderScheduleCalendar(schedule_data=None, selected_date: date | None = None):
    """
    Renders a unified calendar listing for both ESPN and TSDB events.
    Title‑only events (like Paris–Roubaix) show as a full-width header.
    Home/away events use the 4-column layout.
    """
    st.subheader("Sports Schedule Calendar")

    if schedule_data is None:
        st.info("Please select a league in the sidebar to view the schedule.")
        return

    if selected_date is None:
        selected_date = date.today()

    st.write(f"### Schedule for {selected_date.strftime('%Y-%m-%d')}")

    found = False
    for ev in schedule_data:
        ev_dt = ev.get("start_datetime")
        if not ev_dt:
            continue

        # Normalize and convert to local tz
        if isinstance(ev_dt, str):
            ev_dt = parser.parse(ev_dt)
        if ev_dt.tzinfo:
            ev_dt = ev_dt.astimezone(tzlocal())
        if ev_dt.date() != selected_date:
            continue

        found = True
        title  = ev.get("title")           # TSDB single-event name
        home   = ev.get("home_team")
        away   = ev.get("away_team")
        status = ev.get("status", "")
        result = ev.get("result", "")
        venue  = ev.get("venue", "")
        league = ev.get("league_name", "")
        network = ev.get("network", "")
        time_str = ev_dt.strftime("%I:%M %p")

        # Title‑only (e.g. Paris–Roubaix): full-width header
        if title and not home and not away:
            st.markdown(f"## {title}")
            meta = f"*Time:* {time_str}"
            if league:
                meta += f"  •  *League:* {league}"
            if network:
                meta += f"  •  *TV:* {network}"
            st.markdown(meta)
            st.divider()
            continue

        # Standard 4-column layout
        c1, c2, c3, c4 = st.columns([3,1,3,2])
        with c1:
            st.markdown(f"**{away or 'TBD'}**")
        with c2:
            st.markdown("vs")
        with c3:
            st.markdown(f"**{home or 'TBD'}**")
        with c4:
            st.markdown(result or status or "")

        # Meta line
        meta = f"*Time:* {time_str}"
        if venue:
            meta += f"  •  *Venue:* {venue}"
        if league:
            meta += f"  •  *League:* {league}"
        if network:
            meta += f"  •  *TV:* {network}"
        st.markdown(meta)
        st.divider()

    if not found:
        st.warning("No games scheduled for this date.")
