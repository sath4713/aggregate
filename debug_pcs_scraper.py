# #!/usr/bin/env python3
# """
# Quick test script to verify that Tour of the Alps appears on each day of its ProSeries date range.
# """
# from components.api_client import get_pcs_season_events


# def main():
#     # Fetch all UCI ProSeries races for 2025
#     events = get_pcs_season_events("2.pro", 2025)

#     # Filter for Tour of the Alps
#     alps = [e for e in events if "Alps" in e.get("title", "")]

#     print(f"Found {len(alps)} entries for Tour of the Alps:\n")
#     for e in alps:
#         dt = e.get("start_datetime")
#         # dt should be a datetime.datetime
#         date_only = dt.strftime("%Y-%m-%d") if dt else "None"
#         print(f"  • {e.get('title')} — {date_only} ({dt})")


# if __name__ == "__main__":
#     main()

from components.api_client import get_pcs_events_by_day
from datetime import date

evs = get_pcs_events_by_day(date(2025, 4, 22), "2.pro")
for e in evs:
    if "Alps" in e["title"]:
        print(e["start_datetime"], e["title"])
