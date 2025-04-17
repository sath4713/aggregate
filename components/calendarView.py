import streamlit as st
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import date

def renderScheduleCalendar(schedule_data=None, selected_date: date | None = None):
    """
    Renders a calendar view for the given schedule_data on the given selected_date.
    Converts each event time to the local timezone before comparing dates.
    """
    st.subheader("Sports Schedule Calendar")

    # 1) No league chosen yet?
    if schedule_data is None:
        st.info("Please select a league in the sidebar to view the schedule.")
        return

    # 2) Use passed-in date or default to today
    if selected_date is None:
        selected_date = date.today()

    st.write(f"### Schedule for {selected_date.strftime('%Y-%m-%d')}")

    found = False
    for ev in schedule_data:
        ev_dt = ev.get("start_datetime")

        # 3) Normalize string → datetime
        if isinstance(ev_dt, str):
            try:
                ev_dt = parser.parse(ev_dt)
            except:
                ev_dt = None

        if not ev_dt:
            continue

        # 4) Convert UTC→local before matching
        if ev_dt.tzinfo is not None:
            ev_dt_local = ev_dt.astimezone(tzlocal())
        else:
            ev_dt_local = ev_dt  # assume already local

        # 5) Only render events matching our selected local date
        if ev_dt_local.date() != selected_date:
            continue

        found = True
        home      = ev.get("home_team", "TBD")
        away      = ev.get("away_team", "TBD")
        status    = ev.get("status", "Scheduled")
        result    = ev.get("result", "")
        venue     = ev.get("venue", "N/A")
        time_str  = ev_dt_local.strftime("%I:%M %p")  # now in local tz

        # Layout columns
        c1, c2, c3, c4 = st.columns([2,1,2,2])
        with c1: st.markdown(f"**{away}**")
        with c2: st.markdown("vs")
        with c3: st.markdown(f"**{home}**")
        with c4: st.markdown(f"{result or status}")

        st.markdown(f"*Time:* {time_str}  •  *Venue:* {venue}")
        st.divider()

    if not found:
        st.warning("No games scheduled for this date.")
