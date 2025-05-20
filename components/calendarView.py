import streamlit as st
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import date, time


def renderScheduleCalendar(schedule_data=None, selected_date: date | None = None):
    
    if schedule_data is None:
        st.info("Please select a league in the sidebar to view the schedule.")
        return

    if selected_date is None:
        selected_date = date.today()

    st.markdown(f"### Schedule for {selected_date:%A, %b %-d %Y}")
    tz_local = tzlocal()
    found = False

    # leagues for which 00:00 should be hidden
    hide_midnight = {
        "UCI WorldTour",
        "UCI ProSeries",
        "Diamond League",
        "World Marathon Majors",
        "World Athletics Championships",
    }

    for ev in schedule_data:
        ev_dt = ev.get("start_datetime")
        if not ev_dt:
            continue

        # parse & normalize
        if isinstance(ev_dt, str):
            ev_dt = parser.parse(ev_dt)
        if ev_dt.tzinfo:
            ev_dt = ev_dt.astimezone(tz_local)
        ev_dt = ev_dt.replace(tzinfo=None)

        if ev_dt.date() != selected_date:
            continue
        found = True

        league = ev.get("league_name", "")
        title = ev.get("title")
        home = ev.get("home_team")
        away = ev.get("away_team")
        result = ev.get("result", "")
        venue = ev.get("venue", "")
        network = ev.get("network", "")
        info_url = ev.get("url")

        # build date & time strings
        date_str = ev_dt.strftime("%-m/%-d")
        # only show time if not exactly midnight _or_ league not in hide_midnight
        if not (ev_dt.time() == time(0, 0) and league in hide_midnight):
            time_str = ev_dt.strftime("%I:%M %p").lstrip("0")
        else:
            time_str = ""  # drop it

        # open card
        st.markdown('<div class="schedule-card">', unsafe_allow_html=True)

        # single-title events (e.g. races)
        if title and not home and not away:
            st.markdown(
                f'<div class="schedule-title">{title}</div>', unsafe_allow_html=True
            )
            meta = f"**Date:** {date_str}"
            if time_str:
                meta += f"  •  **Time:** {time_str}"
            if league:
                meta += f"  •  **League:** {league}"
            if network:
                meta += f"  •  **TV:** {network}"
            st.markdown(meta)

        # head-to-head events
        else:
            c1, c2, c3, c4 = st.columns([3, 1, 3, 2])
            with c1:
                if ev.get("home_logo"):
                    st.image(ev["home_logo"], width=32)
                st.markdown(f"**{home or 'TBD'}**")
            with c2:
                st.markdown(f"**{result or 'vs'}**")
            with c3:
                if ev.get("away_logo"):
                    st.image(ev["away_logo"], width=32)
                st.markdown(f"**{away or 'TBD'}**")
            with c4:
                label = date_str + (f" at {time_str}" if time_str else "")
                st.markdown(label)

            meta_parts = []
            if venue:
                meta_parts.append(f"**Venue:** {venue}")
            if league:
                meta_parts.append(f"**League:** {league}")
            if network:
                meta_parts.append(f"**TV:** {network}")
            if meta_parts:
                st.markdown("  •  ".join(meta_parts))

        # more-info link
        if info_url:
            st.markdown(
                f"""<div class="more-info">
                        <a href="{info_url}" target="_blank">More info</a>
                    </div>""",
                unsafe_allow_html=True,
            )

        # close card
        st.markdown("</div>", unsafe_allow_html=True)

    if not found:
        st.warning("No games scheduled for this date.")
