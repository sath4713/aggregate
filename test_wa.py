import asyncio
import json
from worldathletics import WorldAthletics


async def main():
    wa = WorldAthletics()
    query = """
    query getCalendarEvents($competitionId: Int!) {
      getCalendarEvents(competitionId: $competitionId) {
        results {
          id
          name
          startDate
          venue
          wasUrl
        }
      }
    }
    """
    variables = {"competitionId": 5282}
    resp = await wa.execute(query, variables=variables)
    print(json.dumps(resp, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
