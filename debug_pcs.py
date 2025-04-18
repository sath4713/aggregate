# debug_pcs_verbose.py

import requests
from bs4 import BeautifulSoup
from dateutil import parser
import datetime as dt

# Real‑browser UA so PCS doesn’t block us
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Safari/537.36"
    )
}


def find_table(soup):
    t = soup.find("table", class_="basic")
    if t:
        print("→ Using <table class='basic'>")
        return t
    for t in soup.find_all("table"):
        # we’ll pick the first table with at least one parseable date in its first <td>
        rows = t.select("tbody tr")
        for row in rows:
            td = row.select_one("td")
            if not td:
                continue
            text = td.get_text(strip=True)
            try:
                parser.parse(text, dayfirst=True)
                print("→ Found table by heuristic match on date text:", repr(text))
                return t
            except Exception:
                continue
    print("❌ No table found by any method")
    return None


def verbose_season(classification: str, year: int):
    url = (
        f"https://www.procyclingstats.com/races.php?class={classification}&year={year}"
    )
    print(f"[DEBUG] Fetching URL: {url}\n")
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = find_table(soup)
    if not table:
        print("[ERROR] No table to scrape—check your selector.")
        return []

    rows = table.select("tbody tr")
    print(f"[DEBUG] Total rows found in <tbody>: {len(rows)}\n")

    # Show the first few rows' raw text
    for idx, row in enumerate(rows[:10]):
        cols = row.find_all("td")
        raw_date = cols[0].get_text(strip=True) if cols else "<no cols>"
        raw_name = cols[1].get_text(strip=True) if len(cols) > 1 else "<no link>"
        print(f"Row {idx:02d}: date_cell={raw_date!r}, name_cell={raw_name!r}")

    # Now attempt to parse every row and collect events
    events = []
    for idx, row in enumerate(rows):
        cols = row.find_all("td")
        if len(cols) < 2:
            print(f" Skipping row {idx}: fewer than 2 <td> elements.")
            continue

        date_text = cols[0].get_text(strip=True)
        try:
            race_date = parser.parse(date_text, dayfirst=True).date()
        except Exception as parse_err:
            print(f"  [!] Row {idx} date parse failed ({date_text!r}): {parse_err}")
            continue

        link_tag = cols[1].find("a")
        if not link_tag:
            print(f"  [!] Row {idx} missing <a> tag in second <td>.")
            continue

        title = link_tag.get_text(strip=True)
        events.append((race_date, title))

    print(f"\n[RESULT] Parsed {len(events)} events from season table.\n")
    return events


def verbose_day(classification: str, test_date: dt.date):
    all_events = verbose_season(classification, test_date.year)
    today_events = [t for (d, t) in all_events if d == test_date]
    print(f"[RESULT] Found {len(today_events)} events on {test_date}\n")
    for t in today_events:
        print("  •", t)
    return today_events


if __name__ == "__main__":
    raw = input("UCI class (e.g. 1.pro): ").strip() or "1.pro"
    cls = raw.lower()  # keep the query lowercase to match PCS URLs
    yr = input("Year (e.g. 2025): ").strip() or str(dt.date.today().year)
    ds = input("Test date (YYYY-MM-DD): ").strip() or dt.date.today().isoformat()

    year = int(yr)
    test_date = dt.date.fromisoformat(ds)

    print(f"\n=== SEASON SCRAPE for class={cls}, year={year} ===\n")
    verbose_season(cls, year)

    print(f"\n=== DAY‑OF SCRAPE for {test_date} (class={cls}) ===\n")
    verbose_day(cls, test_date)
