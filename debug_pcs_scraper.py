from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s — %(message)s"
)

BASE_URL = "https://www.procyclingstats.com/races.php"


def fetch_events(year: int, circuit: int) -> list:
    """
    Fetch all races for a given year & circuit‑ID by rendering the page with Playwright
      • circuit=1  → UCI WorldTour
      • circuit=26 → UCI ProSeries
    """
    url = f"{BASE_URL}" f"?year={year}&circuit={circuit}&class=&filter=Filter"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/100.0.4896.127 Safari/537.36"
            )
        )
        logging.debug(f"→ Navigating to {url}")
        page.goto(url)
        # wait for that <table class="basic"> to appear
        page.wait_for_selector("table.basic", timeout=15_000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="basic")
    if not table:
        # dump a snippet so you can debug if it ever changes again
        snippet = html[:500].replace("\n", " ")
        raise RuntimeError(
            f'No <table class="basic"> found! Page snippet:\n{snippet!r}'
        )

    events = []
    for row in table.tbody.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        date_cell = cols[0].get_text(strip=True)
        name_cell = cols[2]
        link_tag = name_cell.find("a")
        category = cols[4].get_text(strip=True)

        events.append(
            {
                "date": date_cell,
                "name": (
                    link_tag.get_text(strip=True)
                    if link_tag
                    else name_cell.get_text(strip=True)
                ),
                "link": link_tag["href"] if link_tag else None,
                "category": category,
            }
        )

    return events


if __name__ == "__main__":
    YEAR = 2025
    CIRCUITS = {"WorldTour": 1, "ProSeries": 26}

    all_events = {}
    for label, cid in CIRCUITS.items():
        evs = fetch_events(YEAR, cid)
        logging.info(f"→ Fetched {len(evs)} {label} races")
        all_events[label] = evs

    for label, evs in all_events.items():
        print(f"\n{label} races ({len(evs)}):")
        for e in evs:
            print(f" • {e['date']} — {e['name']} ({e['category']})")
