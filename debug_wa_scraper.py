# debug_wa_scraper.py

"""
Combined debug scraper for:
- Diamond League (official site)
- World Marathon Majors (Wikipedia)
- World Athletics Championships (Wikipedia)
- World Athletics Calendar (embedded JSON)
"""
import json
import re
import requests
import certifi
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_diamond_league_events(year: int) -> list[dict]:
    """
    Scrape the Diamond League calendar from diamondleague.com.
    """
    base_url = "https://www.diamondleague.com"
    resp = requests.get(f"{base_url}/calendar/")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    heading = next(
        (
            h2
            for h2 in soup.find_all("h2")
            if h2.get_text(strip=True) == f"Calendar {year}"
        ),
        None,
    )
    if not heading:
        return []

    events = []
    for sib in heading.find_next_siblings():
        if sib.name == "h2":
            break
        for a in sib.find_all("a", href=True):
            text = a.get_text(" ", strip=True)
            if not re.match(r"\d{1,2}\s\w+", text):
                continue
            dates = list(re.finditer(r"\d{1,2}\s\w+", text))
            if len(dates) < 2:
                continue
            date_str = f"{dates[1].group(0)} {year}"
            m = re.search(r"(.+?)\s*\((\w{3})\)", text[dates[1].end() :])
            if not m:
                continue
            name, country = m.groups()
            try:
                dt = datetime.strptime(date_str, "%d %B %Y").date()
            except ValueError:
                continue
            href = a["href"]
            url = href if href.startswith("http") else base_url + href
            events.append(
                {
                    "league": "Diamond League",
                    "date": dt,
                    "name": name.strip(),
                    "country": country,
                    "url": url,
                }
            )
    return events


def get_marathon_majors(year: int) -> list[dict]:
    """
    Scrape World Marathon Majors dates from Wikipedia.
    """
    url = "https://en.wikipedia.org/wiki/World_Marathon_Majors"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table", {"class": "wikitable"})
    if not table:
        return []

    headers = [th.get_text(strip=True) for th in table.find("tr").find_all("th")]
    row = next(
        (
            r
            for r in table.find_all("tr")[1:]
            if (td := r.find("td")) and td.get_text(strip=True) == str(year)
        ),
        None,
    )
    if not row:
        return []

    events = []
    cells = row.find_all("td")
    for city, cell in zip(headers[1:7], cells[1:7]):
        date_text = cell.get_text(strip=True)
        try:
            dt = datetime.strptime(f"{date_text} {year}", "%d %B %Y").date()
        except ValueError:
            dt = None
        events.append(
            {
                "league": "World Marathon Majors",
                "date": dt,
                "name": city,
                "url": None,
            }
        )
    return events


def get_wa_champs(year: int) -> list[dict]:
    """
    Scrape World Athletics Championships dates from Wikipedia.
    """
    url = f"https://en.wikipedia.org/wiki/{year}_World_Athletics_Championships"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    date_text = None
    for tr in soup.select("table.infobox tr"):
        if tr.th and tr.th.get_text(strip=True) == "Dates":
            date_text = tr.td.get_text(strip=True)
            break
    if not date_text:
        return []

    m = re.match(r"(\d{1,2})[–-](\d{1,2})\s+(\w+)\s+(\d{4})", date_text)
    if not m:
        return []
    start_d, end_d, month, y = m.groups()
    start = datetime.strptime(f"{start_d} {month} {y}", "%d %B %Y").date()
    end = datetime.strptime(f"{end_d} {month} {y}", "%d %B %Y").date()

    return [
        {
            "league": "World Athletics Championships",
            "date": start + timedelta(days=i),
            "name": f"World Athletics Championships ({year})",
            "url": url,
        }
        for i in range((end - start).days + 1)
    ]




if __name__ == "__main__":
    year = 2025

    # Optional: list Wikipedia athletics page headings

    scrapers = [
        get_diamond_league_events,
        get_marathon_majors,
        get_wa_champs,
    ]

    total = []
    for fn in scrapers:
        evs = fn(year)
        print(f"\n>> {fn.__name__}: found {len(evs)} events")
        for e in evs:
            info = e.get("date") or e.get("date_str", "")
            print(f" • [{e['league']}] {info} — {e['name']} {e.get('url','')}")
        total.extend(evs)

    print(f"\nTotal across all leagues: {len(total)} events")
