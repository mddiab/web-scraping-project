import time
import random
import re
from urllib.parse import urljoin
from datetime import datetime, timezone

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


# ---------------------------
# BeautifulSoup parsing
# ---------------------------

TITLE_KEYWORDS_RE = re.compile(
    r"\b(PC|Xbox|PlayStation|Nintendo|Switch|Steam)\b",
    re.IGNORECASE,
)

PRICE_RE = re.compile(
    r"^[^\d]*\d[\d,]*\.\d{2}\s*[A-Za-z$€£]*$"   # something like: $34.99, 34.99 USD, €34.99
)


def parse_loaded_latest_games(html, base_url, max_items=None):
    """
    Parse the Loaded (formerly CDKeys) 'Latest Games' page using BeautifulSoup.

    Strategy:
      1. Find all <a> tags whose text looks like a product title
         (contains PC/Xbox/PlayStation/Nintendo/Switch/Steam).
      2. For each title link, walk forward in the DOM and pick the first
         text that looks like a price (e.g. 34.99, $34.99) before we hit:
            - another title-like <a>, or
            - the "Add"/"Buy"/"Notify" button.
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

        # We limit how far we scan to avoid going into the next big section
        steps = 0
        for node in a.next_elements:
            if steps > 150:  # safety cap so we don't scan the whole page for one item
                break
            steps += 1

            # If we see another title-like link, stop (we've probably reached the next product)
            if isinstance(node, Tag) and node.name == "a":
                other_text = node.get_text(strip=True)
                if other_text and TITLE_KEYWORDS_RE.search(other_text) and other_text != title:
                    break

            # Stop at obvious action buttons
            if isinstance(node, Tag) and node.name in ("button", "a"):
                btn_txt = node.get_text(strip=True)
                if any(x in btn_txt for x in ("Add", "Buy", "Notify", "Pre-order", "Pre-Order")):
                    # If we didn't catch a price before an action button, there's likely no valid price here
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
            # If no price found near this title, skip it
            continue

        key = (title, full_url)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        items.append(
            {
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
# Main scraper
# ---------------------------

def scrape_cdkeys(max_items=50):
    base_url = "https://www.cdkeys.com/latest-games"
    loaded_base = "https://www.loaded.com"

    print("\n==============================")
    print(f"🎮  CDKeys/Loaded SCRAPER STARTED (LIMIT: {max_items} ITEMS)")
    print("==============================\n")

    # --- Chrome setup ---
    options = Options()
    # options.add_argument("--headless")  # uncomment in CI/server
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

    try:
        print("🌍 Opening Latest Games page...")
        driver.get(base_url)
        human_wait(2.5, 4.5)

        # Accept cookies if any
        accept_cookies(driver)

        # Wait until the "Latest Games" heading is present (just to be sure page loaded)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Latest Games')]")
                )
            )
            print("✅ Page header loaded.")
        except Exception:
            print("⚠️ Could not explicitly detect header, continuing...")

        # Scroll to load everything
        scroll_to_bottom(driver)

        # Get final HTML and parse with BeautifulSoup
        html = driver.page_source
        scraped_items = parse_loaded_latest_games(
            html, base_url=loaded_base, max_items=max_items
        )

        df = pd.DataFrame(scraped_items)
        filename = "cdkeys_latest_games.csv"
        df.to_csv(filename, index=False)

        print("\n🧹 Done. Closing browser...")
        print("\n==============================")
        print(f"✅ SCRAPING COMPLETE — {len(df)} items saved to '{filename}'")
        print("==============================\n")

        return df

    except Exception as e:
        print("❗ Unexpected error:", repr(e))
        return None

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_cdkeys(max_items=50)
