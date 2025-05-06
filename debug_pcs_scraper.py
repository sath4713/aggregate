# debug_rest_days.py

import requests, re
from bs4 import BeautifulSoup
import datetime


def get_rest_days_for_tour(slug: str, year: int) -> list[datetime.date]:
    url = f"https://www.procyclingstats.com/race/{slug}/{year}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"ERROR fetching {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    # look for the “Stages” header (h2 or h3)
    header = soup.find(
        lambda tag: tag.name in ("h2", "h3") and "Stages" in tag.get_text()
    )
    if not header:
        print("❌ Couldn't find Stages header")
        return []

    block = header.find_next_sibling()
    if not block:
        print("❌ No content after Stages header")
        return []

    rest_days = []
    for line in block.get_text("\n", strip=True).splitlines():
        if "Restday" not in line:
            continue
        m = re.search(r"(\d{1,2}/\d{1,2})", line)
        if not m:
            continue
        d, mth = map(int, m.group(1).split("/"))
        rest_days.append(datetime.date(year, mth, d))

    return rest_days


if __name__ == "__main__":
    for slug in ("giro-d-italia", "tour-de-france", "vuelta-a-espana"):
        days = get_rest_days_for_tour(slug, 2025)
        print(f"{slug} rest days → {days}")
