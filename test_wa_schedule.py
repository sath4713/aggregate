import asyncio
import json
from worldathletics import WorldAthletics

async def main():
    wa = WorldAthletics()
    try:
        sched = await wa.get_schedule(5282)    # await the async method
        print("get_schedule output:")
        print(json.dumps(sched, indent=2))
    except Exception as e:
        print("Error calling get_schedule:", e)

if __name__ == "__main__":
    asyncio.run(main())
