# debug_pyespn.py
from pyespn import PYESPN
from dateutil import parser

client = PYESPN("nba", load_teams=False)
print("schedule_list URLs:", client.schedule.schedule_list)

sched = client.schedule
print("weeks loaded:", len(sched.weeks))

if sched.weeks:
    w = sched.weeks[0].number
    evs = sched.get_events(w)
    print(f"events in week {w}:", len(evs))
    if evs:
        print("sample event keys:", evs[0].__dict__.keys())
else:
    print("No weeks loaded at all.")
