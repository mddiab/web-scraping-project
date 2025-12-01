import time
import random
import re
from urllib.parse import urljoin
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ---------------------------
# Helpers
# ---------------------------

def human_wait(min_s=1.0, max_s=2.5):
    """Wait a random small delay to look human."""
    time.sleep(random.uniform(min_s, max_s))


def accept_cookies(driver, timeout=10):
    """
    Try a list of XPaths to find a clickable cookie button and click the first that works.
    """
    cookie_xpaths = [
        "//button[contains(., 'Accept all') or contains(., 'Accept All') or contains(., 'Accept cookies')]",
        "//button[contains(., 'Accept') and contains(., 'cookies')]",
        "//button[contains(., 'I agree') or contains(., 'Agree')]",
        "//button[contains(@id, 'onetrust-accept-btn-handler')]",
    ]

    for xp in cookie_xpaths:
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            el.click()
            print("✅ Cookies popup accepted.")
            human_wait()
            return True
        except Exception:
            continue

    print("ℹ️ No cookies popup clicked (maybe none appeared).")
    return False


def scroll_to_bottom(driver):
    """Scroll to the bottom of the page to load all products."""
    print("⬇️  Scrolling to bottom to load all products...")
    while True:
        y_offset = driver.execute_script("return window.pageYOffset;")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        new_y_offset = driver.execute_script("return window.pageYOffset;")
        if new_y_offset == y_offset:
            break
    print("✅ Reached bottom of page.")


def create_driver():
    """Create and return a configured Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")

    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    return driver


# ---------------------------
# BeautifulSoup parsing
# ---------------------------

TITLE_KEYWORDS_RE = re.compile(
    r"\b(PC|Xbox|PlayStation|Nintendo|Switch|Steam)\b",
    re.IGNORECASE,
)

PRICE_RE = re.compile(
    r"^[^\d]*\d[\d,]*\.\d{2}\s*[A-Za-z$€£]*$"   # e.g. $34.99, 34.99 USD, €34.99
)


def parse_loaded_latest_games(html, base_url, max_items=None):
    """
    Parse a Loaded/CDKeys category page using BeautifulSoup.

    Strategy:
      1. Find all <a> tags whose text looks like a product title
         (contains PC/Xbox/PlayStation/Nintendo/Switch/Steam).
      2. For each title link, walk forward in the DOM and pick the first
         text that looks like a price (e.g. 34.99, $34.99) before we hit:
            - another title-like <a>, or
            - an "Add"/"Buy"/"Notify" button.
    """
    soup = BeautifulSoup(html, "html.parser")

    title_links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if not text:
            continue
        if TITLE_KEYWORDS_RE.search(text):
            title_links.append(a)

    print(f"🔍 Found {len(title_links)} candidate title links.")

    items = []
    seen_keys = set()

    for a in title_links:
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not href or not title:
            continue

        full_url = urljoin(base_url, href)

        # Walk forward after this title to find price
        price_text = None

        steps = 0
        for node in a.next_elements:
            if steps > 150:  # safety cap
                break
            steps += 1

            # If we see another title-like link, stop (probably next product)
            if isinstance(node, Tag) and node.name == "a":
                other_text = node.get_text(strip=True)
                if other_text and TITLE_KEYWORDS_RE.search(other_text) and other_text != title:
                    break

            # Stop at obvious action buttons
            if isinstance(node, Tag) and node.name in ("button", "a"):
                btn_txt = node.get_text(strip=True)
                if any(x in btn_txt for x in ("Add", "Buy", "Notify", "Pre-order", "Pre-Order")):
                    break

            # Look for a price-looking text node
            if isinstance(node, NavigableString):
                txt = node.strip()
                if not txt:
                    continue
                if PRICE_RE.match(txt):
                    price_text = txt
                    break

        if not price_text:
            continue

        key = (title, full_url)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        items.append(
            {
                "source": "loaded",
                "title": title,
                "price_raw": price_text,
                "product_url": full_url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        if max_items is not None and len(items) >= max_items:
            break

    print(f"✅ Parsed {len(items)} unique products from HTML.")
    return items


# ---------------------------
# Per-category scraper
# ---------------------------

def scrape_single_category(label, url, max_items_per_category, loaded_base):
    """
    Scrape a single category (given by URL) and tag all rows with `category=label`.
    """
    print(f"\n🌍 Opening category '{label}' → {url}")
    driver = create_driver()

    try:
        driver.get(url)
        human_wait(2.5, 4.5)

        # Accept cookies if any
        accept_cookies(driver)

        # We *could* wait on a specific heading if we know it, but to keep it generic,
        # just scroll to bottom and parse page source.
        scroll_to_bottom(driver)

        html = driver.page_source
        items = parse_loaded_latest_games(
            html, base_url=loaded_base, max_items=max_items_per_category
        )

        # Add category column
        for item in items:
            item["category"] = label

        print(f"📦 Category '{label}' → {len(items)} items scraped.")
        return items

    except Exception as e:
        print(f"❗ Error while scraping category '{label}': {repr(e)}")
        return []

    finally:
        print(f"🧹 Closing browser for category '{label}'...")
        driver.quit()


# ---------------------------
# Main multi-category scraper
# ---------------------------

def scrape_cdkeys(category_urls, max_items_per_category=50, use_threads=True):
    """
    Scrape multiple CDKeys/Loaded categories.

    Parameters
    ----------
    category_urls : dict
        Mapping from category label → category URL, e.g.:
        {
            "latest-games": "https://www.cdkeys.com/latest-games",
            "xbox": "https://www.cdkeys.com/xbox-live",
        }

    max_items_per_category : int
        Maximum number of items to parse per category page (after scrolling).

    use_threads : bool
        If True and you have multiple categories, each category will be scraped
        in its own thread (i.e. its own Chrome driver) to speed things up.
    """
    loaded_base = "https://www.loaded.com"

    print("\n==============================")
    print("🎮  CDKeys/Loaded MULTI-CATEGORY SCRAPER STARTED")
    print("==============================\n")

    all_items = []

    if use_threads and len(category_urls) > 1:
        max_workers = min(len(category_urls), 4)  # don't spawn *too* many drivers
        print(f"🧵 Using multithreading with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    scrape_single_category,
                    label,
                    url,
                    max_items_per_category,
                    loaded_base,
                ): label
                for label, url in category_urls.items()
            }

            for future in as_completed(futures):
                label = futures[future]
                try:
                    items = future.result()
                    all_items.extend(items)
                except Exception as e:
                    print(f"❗ Category '{label}' failed with error: {repr(e)}")
    else:
        # Sequential mode (default if 0 or 1 categories, or use_threads=False)
        for label, url in category_urls.items():
            items = scrape_single_category(
                label, url, max_items_per_category, loaded_base
            )
            all_items.extend(items)

    # ---------------- Save to data/raw/ ----------------
    df = pd.DataFrame(all_items)

    BASE_DIR = Path(__file__).resolve().parent.parent  # project root
    raw_dir = BASE_DIR / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    filename = raw_dir / "loaded.csv"
    df.to_csv(filename, index=False)

    print("\n==============================")
    print(f"✅ SCRAPING COMPLETE — {len(df)} items saved to '{filename}'")
    print("==============================\n")

    return df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Loaded/CDKeys Scraper")
    parser.add_argument("--limit", type=int, default=500, help="Maximum number of items to scrape per category")
    parser.add_argument("--no-threads", action="store_true", help="Disable multithreading")
    args = parser.parse_args()

    # 🔧 Define the categories you want to scrape here.
    # Keys = label that will appear in the 'category' column.
    # Values = full URLs of the category pages.
    CATEGORY_URLS = {
        "latest-games": "https://www.cdkeys.com/latest-games",
        "deals": "https://www.loaded.com/cdkeys-deals",
        "gift-cards": "https://www.loaded.com/gift-cards"
    }

    # Example: scrape all categories with multithreading enabled
    scrape_cdkeys(
        category_urls=CATEGORY_URLS,
        max_items_per_category=args.limit,
        use_threads=not args.no_threads,
    )
