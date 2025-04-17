from pyespn import PYESPN
from dateutil import parser

# Initialize the client for NBA
client = PYESPN("nba", load_teams=False)

# What URLs is it using under the hood?
print("schedule_list URLs:", client.schedule.schedule_list)

# How many weeks did it load?
sched = client.schedule
print("weeks loaded:", len(sched.weeks))

# If there are weeks, pull events from the first one
if sched.weeks:
    w = sched.weeks[0].number
    evs = sched.get_events(w)
    print(f"events in week {w}:", len(evs))
    if evs:
        print("sample event keys:", evs[0].__dict__.keys())
else:
    print("No weeks loaded at all.")
