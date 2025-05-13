import streamlit as st
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import date


def renderScheduleCalendar(schedule_data=None, selected_date: date | None = None):
    """
    Renders a unified calendar listing for both ESPN and PCS events as styled cards,
    now with per-event “More info” links.
    """
    # Inject card CSS once per session
    if not st.session_state.get("_schedule_css_loaded", False):
        st.markdown(
            """
            <style>
            .schedule-card {
                padding: 1rem;
                margin-bottom: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                background-color: #F9F9F9;
            }
            .schedule-title {
                font-size: 1.25rem;
                margin-bottom: 0.5rem;
            }
            .more-info {
                margin-top: 0.5rem;
                font-size: 0.9rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["_schedule_css_loaded"] = True

    if schedule_data is None:
        st.info("Please select a league in the sidebar to view the schedule.")
        return

    if selected_date is None:
        selected_date = date.today()

    st.markdown(f"### Schedule for {selected_date:%A, %b %-d %Y}")

    found = False
    tz_local = tzlocal()

    for ev in schedule_data:
        ev_dt = ev.get("start_datetime")
        if not ev_dt:
            continue

        # Normalize to local naive datetime
        if isinstance(ev_dt, str):
            ev_dt = parser.parse(ev_dt)
        if ev_dt.tzinfo:
            ev_dt = ev_dt.astimezone(tz_local)
        ev_dt = ev_dt.replace(tzinfo=None)

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
        info_url = ev.get("url")

        date_str = ev_dt.strftime("%-m/%-d")
        time_str = ev_dt.strftime("%I:%M %p").lstrip("0")

        st.markdown('<div class="schedule-card">', unsafe_allow_html=True)

        # --- Single-title events (races, specials) ---
        if title and not home and not away:
            st.markdown(
                f'<div class="schedule-title">{title}</div>', unsafe_allow_html=True
            )
            meta = f"**Date:** {date_str}  •  **Time:** {time_str}"
            if league:
                meta += f"  •  **League:** {league}"
            if network:
                meta += f"  •  **TV:** {network}"
            st.markdown(meta)
        else:
            # --- Four-column layout for head-to-head events ---
            c1, c2, c3, c4 = st.columns([3, 1, 3, 2])
            with c1:
                if ev.get("home_logo"):
                    st.image(ev["home_logo"], width=32)
                st.markdown(f"**{ev['home_team'] or 'TBD'}**")
            with c2:
                st.markdown(f"**{result or 'vs'}**")
            with c3:
                if ev.get("away_logo"):
                    st.image(ev["away_logo"], width=32)
                st.markdown(f"**{ev['away_team'] or 'TBD'}**")
            with c4:
                st.markdown(f"{date_str} at {time_str}")

            meta_parts = []
            if venue:
                meta_parts.append(f"**Venue:** {venue}")
            if league:
                meta_parts.append(f"**League:** {league}")
            if network:
                meta_parts.append(f"**TV:** {network}")
            if meta_parts:
                st.markdown("  •  ".join(meta_parts))

        # --- More info link ---
        # … inside your renderScheduleCalendar loop, after rendering the card’s main content …

# --- More info link (HTML anchor instead of Markdown) ---
            if info_url:
                st.markdown(
                    f'''
                    <div class="more-info">
                        <a href="{info_url}" target="_blank">More info</a>
                    </div>
                    ''',
                unsafe_allow_html=True
    )


        st.markdown("</div>", unsafe_allow_html=True)

    if not found:
        st.warning("No games scheduled for this date.")
