import time
import random
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# ---------------------------
# Helpers
# ---------------------------

def human_wait(min_s=1.0, max_s=2.5):
    """Wait a random small delay to look human."""
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


def scroll_steam_results(
    driver,
    desired_count: int | None = None,
    pause_range=(1.0, 2.0),
    max_scrolls: int = 150,
):
    """
    Scroll Steam search results.

    Stops when:
      - We have at least `desired_count` items (if provided), OR
      - Page height stops increasing, OR
      - We hit `max_scrolls` to avoid infinite loops.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    same_height_rounds = 0

    for i in range(max_scrolls):
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_wait(*pause_range)

        # Check how many items are currently loaded
        if desired_count is not None:
            cards = driver.find_elements(By.CSS_SELECTOR, "a.search_result_row")
            count = len(cards)
            print(f"   🔍 Scroll #{i+1}: currently {count} items loaded...")
            if count >= desired_count:
                print(f"   ⏹ Reached desired count ({desired_count}); stopping scroll.")
                return

        # Check if we've reached the real bottom (height not changing)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            same_height_rounds += 1
            if same_height_rounds >= 2:
                print("   ⏹ Page height stopped increasing; probably at bottom.")
                return
        else:
            same_height_rounds = 0
            last_height = new_height

    print(f"   ⏹ Reached max scrolls ({max_scrolls}); stopping to avoid infinite loop.")


# ---------------------------
# Main Scraper
# ---------------------------

STEAM_LISTING_URLS = {
    "top_sellers": "https://store.steampowered.com/search/?filter=topsellers",
    "specials": "https://store.steampowered.com/search/?specials=1",
    "new_and_trending": "https://store.steampowered.com/search/?filter=popularnew",
}


def parse_steam_search_html(html: str, category: str):
    """
    Parse Steam search HTML into a list of product dicts.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    for a in soup.select("a.search_result_row"):
        title_el = a.select_one(".title")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        release_date = a.select_one(".search_released")
        release_date = release_date.get_text(strip=True) if release_date else None

        # --------- PRICE / DISCOUNT (FIXED) ----------
        # Steam usually uses .discount_pct like "-50%"
        discount_el = a.select_one(".discount_pct")
        if not discount_el:
            # Fallback in case markup is slightly different
            discount_el = a.select_one(".search_discount span")

        discount_raw = discount_el.get_text(strip=True) if discount_el else None
        if discount_raw == "":
            discount_raw = None

        price_el = a.select_one(".discount_final_price")
        if not price_el:
            # Some entries only have .search_price
            price_el = a.select_one(".search_price")
        price_raw = price_el.get_text(strip=True) if price_el else None
        # ---------------------------------------------

        url = a.get("href", "").split("?")[0]

        rows.append(
            {
                "source": "steam",
                "category": category,
                "title": title,
                "release_date": release_date,
                "price_raw": price_raw,
                "discount_raw": discount_raw,
                "product_url": url,
            }
        )

    return rows


def main(limit_per_category: int | None = None):
    print("==============================")
    print("🟦  STEAM SCRAPER STARTED")
    print("==============================")

    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "steam.csv"

    driver = make_driver()

    all_rows = []

    try:
        for cat_name, url in STEAM_LISTING_URLS.items():
            print(f"\n🌍 Category: {cat_name} → {url}")
            driver.get(url)
            human_wait()

            print("⬇️  Scrolling to load items...")
            # Only scroll until we have at least `limit_per_category` items (if provided)
            scroll_steam_results(driver, desired_count=limit_per_category)

            html = driver.page_source
            rows = parse_steam_search_html(html, category=cat_name)

            if limit_per_category is not None:
                rows = rows[:limit_per_category]

            print(f"✅ Parsed {len(rows)} items in '{cat_name}'")
            all_rows.extend(rows)

        if not all_rows:
            print("⚠️ No products found; nothing to save.")
            return

        df = pd.DataFrame(all_rows)

        # Drop obvious duplicates (same title & URL)
        df.drop_duplicates(subset=["title", "product_url"], inplace=True)

        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print("\n==============================")
        print(f"✅ SCRAPING COMPLETE — {len(df)} items saved to '{output_path}'")
        print("==============================")

    finally:
        print("🧹 Closing browser...")
        driver.quit()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Steam Scraper")
    parser.add_argument("--limit", type=int, default=2000, help="Maximum number of items to scrape per category")
    args = parser.parse_args()
    
    main(limit_per_category=args.limit)
