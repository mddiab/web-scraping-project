import time
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)
from webdriver_manager.chrome import ChromeDriverManager


# ---------------------------
# Config
# ---------------------------

# "All games" listing (console + PC, no filters)
BASE_URL = "https://www.xbox.com/en-US/games/browse"

MAX_ITEMS = 1000          # hard cap
MAX_SHOW_MORE_CLICKS = 80 # safety for "Show more" loops

PRICE_REGEX = re.compile(r"([€$£])\s?\d[\d.,]*|Free\+?", re.IGNORECASE)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV = DATA_DIR / "xbox.csv"


# ---------------------------
# Helpers
# ---------------------------

def human_wait(min_s=1.0, max_s=2.5):
    time.sleep(random.uniform(min_s, max_s))


def make_driver() -> webdriver.Chrome:
    ua = UserAgent()
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def accept_cookies_if_any(driver, timeout=10):
    """
    Best-effort cookie banner accept. Safe to fail silently.
    """
    selectors = [
        (By.XPATH, "//button[contains(., 'Accept all')]"),
        (By.XPATH, "//button[contains(., 'Accept')]"),
        (By.XPATH, "//button[contains(., 'I agree')]"),
        (By.XPATH, "//button[contains(., 'Got it')]"),
    ]
    for by, xp in selectors:
        try:
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, xp))
            )
            btn.click()
            human_wait(1.0, 2.0)
            print("ℹ️  Cookies popup accepted.")
            return
        except (TimeoutException, ElementClickInterceptedException):
            continue

    print("ℹ️  No cookies popup clicked (maybe none appeared).")


def scroll_slowly(driver, steps=6, pause=1.0):
    """
    Slow scroll down to trigger lazy loading on the current "page".
    """
    for i in range(steps):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight * arguments[0]);",
            (i + 1) / steps,
        )
        time.sleep(pause)


def click_show_more_if_any(driver, timeout=8) -> bool:
    """
    Try to click a 'Show more' / 'Show more results' button.
    Returns True if clicked, False otherwise.
    """
    xpaths = [
        "//button[contains(., 'Show more')]",
        "//button[contains(., 'Load more')]",
        "//button[contains(., 'Load More')]",
        "//button[contains(., 'Show More')]",
        "//button[contains(., 'Show more results')]",
    ]
    for xp in xpaths:
        try:
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            btn.click()
            print("⬇️  Clicked 'Show more'.")
            human_wait(1.5, 3.0)
            return True
        except (TimeoutException, ElementClickInterceptedException):
            continue
    return False


# ---------------------------
# Parsing logic
# ---------------------------

def extract_games_from_html(html: str, base_url: str, already_seen: set):
    """
    Generic parser for Xbox listing pages:
    - Find <a> whose href contains '/games/store/'
    - Use anchor text as title
    - Try to extract a price string from surrounding text
    """
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.find_all("a", href=True)

    rows = []

    for a in anchors:
        href = a["href"]
        if "/games/store/" not in href:
            continue

        full_url = urljoin(base_url, href.split("?")[0])

        if full_url in already_seen:
            continue

        title = " ".join(a.stripped_strings)
        if not title:
            continue

        # Try to find price in parent containers
        price_text = None

        for parent in a.parents:
            if parent.name in ("body", "html"):
                break

            text_blob = " ".join(parent.stripped_strings)
            m = PRICE_REGEX.search(text_blob)
            if m:
                price_text = m.group(0)
                break

        # Fallback: look in the anchor's parent
        if price_text is None and a.parent is not None:
            siblings_text = " ".join(a.parent.stripped_strings)
            m2 = PRICE_REGEX.search(siblings_text)
            if m2:
                price_text = m2.group(0)

        rows.append(
            {
                "store": "xbox",
                "category": "all_games",
                "title": title,
                "price_text": price_text,
                "product_url": full_url,
            }
        )
        already_seen.add(full_url)

    return rows


# ---------------------------
# Main scrape function
# ---------------------------

def scrape_xbox_all_games(max_items: int = MAX_ITEMS):
    print("==============================")
    print(f"🎮  Xbox ALL GAMES SCRAPER STARTED (MAX_ITEMS: {max_items})")
    print("==============================")

    driver = make_driver()

    try:
        print(f"🌍 Opening All Games page: {BASE_URL}")
        driver.get(BASE_URL)
        human_wait(3.0, 5.0)

        accept_cookies_if_any(driver)

        all_rows = []
        seen_urls = set()
        show_more_clicks = 0

        while len(all_rows) < max_items:
            scroll_slowly(driver, steps=5, pause=1.0)

            html = driver.page_source
            new_rows = extract_games_from_html(html, BASE_URL, seen_urls)

            if new_rows:
                all_rows.extend(new_rows)
                print(
                    f"➕ Parsed {len(new_rows)} new items on this view "
                    f"(total unique: {len(all_rows)})"
                )
            else:
                print("ℹ️  No new items found on this view.")

            if len(all_rows) >= max_items:
                break

            if show_more_clicks >= MAX_SHOW_MORE_CLICKS:
                print("ℹ️  Reached max 'Show more' clicks, stopping.")
                break

            clicked = click_show_more_if_any(driver)
            if not clicked:
                print("ℹ️  No 'Show more' button found, stopping.")
                break

            show_more_clicks += 1

        # Trim to max_items
        all_rows = all_rows[:max_items]

        if not all_rows:
            print("⚠️  No items scraped — CSV will not be written.")
            return

        scraped_at = datetime.now(timezone.utc).isoformat()
        for row in all_rows:
            row["scraped_at_utc"] = scraped_at

        df = pd.DataFrame(all_rows)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

        print("==============================")
        print(f"✅ SCRAPING COMPLETE — {len(df)} items saved to '{OUTPUT_CSV.name}'")
        print("==============================")

    finally:
        print("🧹 Done. Closing browser...")
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    scrape_xbox_all_games(max_items=1500)
