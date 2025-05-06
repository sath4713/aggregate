# debug_profiles.py

import json
from first_cycling_api import RaceEdition
from components.api_client import FC_RACE_IDS

# 1) Pick a Grand Tour and year
race_name = "Giro d’Italia"
race_id = FC_RACE_IDS[race_name]
year = 2025

ed = RaceEdition(race_id=race_id, year=year)

# 2) Fetch and inspect stage_profiles JSON
profiles_json = ed.stage_profiles().get_json()
print(f"\n=== Raw stage_profiles JSON for {race_name} {year} ===")
# dump just the top‐level keys and the first few entries
print("Top‐level keys:", list(profiles_json.keys()))
print("Sample stages list (first 3):")
print(json.dumps(profiles_json.get("stages", [])[:3], indent=2))

# 3) Fetch and inspect the JSON for stage=1 results
res1_json = ed.results(stage_num=1).get_json()
print(f"\n=== Raw results JSON for {race_name} Stage 1 ({year}) ===")
print("Top‐level keys:", list(res1_json.keys()))
# presumably the finishers will live under res1_json['results'] or similar:
print("Sample results list (first 3):")
print(json.dumps(res1_json.get("results", [])[:3], indent=2))
