import streamlit as st
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import date


import streamlit as st
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import date


def renderScheduleCalendar(schedule_data=None, selected_date: date | None = None):
    """
    Renders a unified calendar listing for both ESPN and PCS events.
    Finished games show their score in place of “vs”; upcoming games still show “vs”.
    """
    st.subheader("Sports Schedule Calendar")

    if schedule_data is None:
        st.info("Please select a league in the sidebar to view the schedule.")
        return

    if selected_date is None:
        selected_date = date.today()

    st.write(f"### Schedule for {selected_date:%Y-%m-%d}")

    found = False
    tz_local = tzlocal()

    for ev in schedule_data:
        ev_dt = ev.get("start_datetime")
        if not ev_dt:
            continue

        # Parse and convert to local timezone
        if isinstance(ev_dt, str):
            ev_dt = parser.parse(ev_dt)
        if ev_dt.tzinfo:
            ev_dt = ev_dt.astimezone(tz_local)
        ev_dt = ev_dt.replace(tzinfo=None)

        # Filter to the selected day
        if ev_dt.date() != selected_date:
            continue

        found = True
        title = ev.get("title")
        home = ev.get("home_team")
        away = ev.get("away_team")
        result = ev.get("result", "")
        venue = ev.get("venue", "")
        league = ev.get("league_name", "")
        network = ev.get("network", "")

        date_str = ev_dt.strftime("%-m/%-d")
        time_str = ev_dt.strftime("%I:%M %p")

        # Single-title events (e.g. races)
        if title and not home and not away:
            st.markdown(f"## {title}")
            meta = f"*Date:* {date_str}  •  *Time:* {time_str}"
            if league:
                meta += f"  •  *League:* {league}"
            if network:
                meta += f"  •  *TV:* {network}"
            st.markdown(meta)
            st.divider()
            continue

        # Four-column layout: Home | Score/vs | Away | Date/Time
        c1, c2, c3, c4 = st.columns([3, 1, 3, 2])
        with c1:
            st.markdown(f"**{home or 'TBD'}**")
        with c2:
            if result:
                st.markdown(f"**{result}**")
            else:
                st.markdown("vs")
        with c3:
            st.markdown(f"**{away or 'TBD'}**")
        with c4:
            st.markdown(f"{date_str} at {time_str}")

        # Meta line below
        meta_parts = []
        if venue:
            meta_parts.append(f"*Venue:* {venue}")
        if league:
            meta_parts.append(f"*League:* {league}")
        if network:
            meta_parts.append(f"*TV:* {network}")
        if meta_parts:
            st.markdown("  •  ".join(meta_parts))

        st.divider()

    if not found:
        st.warning("No games scheduled for this date.")
