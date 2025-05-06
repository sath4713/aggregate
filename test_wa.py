# debug_profiles.py

import json
from first_cycling_api import RaceEdition
from components.api_client import FC_RACE_IDS

# Choose one Grand Tour
race_name = "Giro d’Italia"
race_id = FC_RACE_IDS[race_name]
year = 2025

# Instantiate the wrapper
ed = RaceEdition(race_id=race_id, year=year)

# 1) Fetch the stage-profiles JSON
profiles = ed.stage_profiles().get()

print(f"\n=== Raw stage_profiles JSON for {race_name} {year} ===")
print(json.dumps(profiles, indent=2)[:500])  # print first 500 chars for brevity

# 2) Inspect the keys & structure
print("\nKeys at the top level of profiles JSON:", list(profiles.keys()))

# 3) Fetch the full results for Stage 1 to see a winner record
res1 = ed.results(stage=1).get()

print(f"\n=== Raw results JSON for {race_name} Stage 1 ({year}) ===")
print(json.dumps(res1, indent=2)[:500])
print("\nKeys at the top level of results JSON:", list(res1.keys()))
