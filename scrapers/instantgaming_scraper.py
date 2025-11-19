import time
import random
import re
from pathlib import Path
from urllib.parse import urljoin

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
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchWindowException,
    InvalidSessionIdException,
)
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "https://www.instant-gaming.com/en/pc/trending/"
OUTPUT_CSV = Path("data/raw/instantgaming.csv")


# ---------------------------
# Helpers
# ---------------------------

def human_wait(min_s: float = 1.0, max_s: float = 2.5):
    """Wait a random small delay to look human."""
    time.sleep(random.uniform(min_s, max_s))


def make_driver() -> webdriver.Chrome:
    """Create and configure a Chrome WebDriver."""
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


def accept_cookies(driver: webdriver.Chrome, timeout: int = 10):
    """
    Try a list of 'Accept cookies' / 'Agree' buttons and click the first that works.
    If nothing is found, just continue.
    """
    candidates = [
        "//button[contains(., 'Accept all')]",
        "//button[contains(., 'Accept All')]",
        "//button[contains(., 'Accept')]",
        "//button[contains(., 'I agree')]",
        "//button[contains(., 'Agree')]",
        "//button[contains(., 'OK')]",
    ]

    wait = WebDriverWait(driver, timeout)
    for xp in candidates:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            print("🍪 Clicked cookies button:", xp)
            human_wait(0.5, 1.0)
            return
        except TimeoutException:
            continue
        except Exception:
            continue

    print("ℹ️ No cookies popup clicked (maybe none appeared).")


def wait_for_results(driver: webdriver.Chrome, timeout: int = 20):
    """
    Wait until the product list is present (any discount badge).
    """
    wait = WebDriverWait(driver, timeout)
    wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//a[contains(normalize-space(.), '%')]")
        )
    )


# ---------------------------
# Parsing
# ---------------------------

def parse_trending_page(
    html: str,
    max_items_page: int,
    seen_urls: set[str],
) -> list[dict]:
    """
    Parse one Trending page HTML and extract up to max_items_page products.

    Two passes:

      1) Discount items:
         • Find all <a> where text looks like "-25%" etc.
         • From each, walk forward and grab:
              title        = first non-empty text
              preorder     = "Pre-order..." line (optional)
              price_raw    = first currency-like text

      2) No-discount items:
         • Find title-like text (" - PC", " - PC (Steam)", etc.)
         • Skip titles already captured.
         • Walk forward until a price-like text is found.
         • Find a nearby <a> to use as URL.
    """
    soup = BeautifulSoup(html, "html.parser")

    discount_re = re.compile(r"^-\d+%$")
    discount_any_re = re.compile(r"-\d+%")
    currency_re = re.compile(r"(\$|€|£|R\$|zł|kr|₪|₺|руб|PLN|BRL)")
    title_hint_re = re.compile(r" - PC")  # catches " - PC", " - PC (Steam)", etc.

    rows: list[dict] = []
    titles_captured: set[str] = set()

    # ----- Pass 1: Items WITH discounts -----
    discount_anchors = []
    for a in soup.find_all("a"):
        txt = a.get_text(strip=True)
        if discount_re.match(txt):
            discount_anchors.append(a)

    print(f"   🔍 Found {len(discount_anchors)} discount anchors on this page.")

    for a in discount_anchors:
        href = a.get("href")
        if not href:
            continue

        full_url = urljoin("https://www.instant-gaming.com", href)
        if full_url in seen_urls:
            # already seen on some page
            continue

        discount_text = a.get_text(strip=True)
        title = None
        price_raw = None
        preorder = None

        # Walk forward until next discount anchor -> that's next product
        for node in a.next_elements:
            if isinstance(node, Tag) and node.name == "a":
                # If this is another discount badge, stop (next game)
                txt = node.get_text(strip=True)
                if discount_any_re.search(txt) and node is not a:
                    break

            if isinstance(node, NavigableString):
                txt = node.strip()
                if not txt:
                    continue

                # Skip the discount itself
                if discount_any_re.search(txt):
                    continue

                # Title = first non-empty string after discount
                if title is None:
                    title = txt
                    continue

                # Optional preorder line
                if preorder is None and txt.lower().startswith("pre-order"):
                    preorder = txt
                    continue

                # Price = first currency-like thing
                if price_raw is None and currency_re.search(txt):
                    price_raw = txt
                    # after we got price, we can stop for this item
                    break

        rows.append(
            {
                "source": "instantgaming",
                "title": title,
                "discount": discount_text,
                "price_raw": price_raw,
                "preorder_info": preorder,
                "product_url": full_url,
            }
        )
        titles_captured.add(title or "")
        seen_urls.add(full_url)

        if len(rows) >= max_items_page:
            return rows

    # ----- Pass 2: Items WITHOUT discounts -----
    # Look for lines that look like "Game Name - PC (Steam)" but were not captured.
    extra_rows = 0
    title_nodes = soup.find_all(string=title_hint_re)

    for text_node in title_nodes:
        title = text_node.strip()
        if not title or title in titles_captured:
            continue

        # Try to find a price after this title
        price_raw = None

        for node in text_node.next_elements:
            # Stop if we hit a new discount -> likely next product block
            if isinstance(node, Tag) and node.name == "a":
                t = node.get_text(strip=True)
                if discount_any_re.search(t):
                    break

            if isinstance(node, NavigableString):
                txt = node.strip()
                if not txt:
                    continue
                if currency_re.search(txt):
                    price_raw = txt
                    break

        if price_raw is None:
            continue

        # Try to find a nearby <a> with href as product URL
        a = text_node.find_parent("a")
        if a is None:
            # Fallback: walk backwards a bit to find a link
            prev = text_node.previous_element
            steps = 0
            while prev is not None and steps < 40:
                if isinstance(prev, Tag) and prev.name == "a" and prev.get("href"):
                    a = prev
                    break
                prev = prev.previous_element
                steps += 1

        if a is None:
            continue

        href = a.get("href")
        if not href:
            continue

        full_url = urljoin("https://www.instant-gaming.com", href)
        if full_url in seen_urls:
            continue

        rows.append(
            {
                "source": "instantgaming",
                "title": title,
                "discount": None,
                "price_raw": price_raw,
                "preorder_info": None,
                "product_url": full_url,
            }
        )
        titles_captured.add(title)
        seen_urls.add(full_url)
        extra_rows += 1

        if len(rows) >= max_items_page:
            break

    if extra_rows:
        print(f"   ➕ Added {extra_rows} extra no-discount items.")

    return rows


def click_next_page_by_number(
    driver: webdriver.Chrome,
    current_page: int,
    timeout: int = 15,
) -> bool:
    """
    Click the next page using its number (2, 3, 4, ...) at the bottom of the page.

    Returns True if it clicked something, False if there is no next page.
    """
    next_page_num = current_page + 1
    wait = WebDriverWait(driver, timeout)

    try:
        next_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, str(next_page_num)))
        )
    except TimeoutException:
        print(f"ℹ️ No page {next_page_num} link found — assuming last page.")
        return False

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});", next_link
    )
    human_wait(0.8, 1.6)
    next_link.click()
    print(f"➡️  Moved to page {next_page_num}")
    human_wait(1.0, 2.5)
    return True


# ---------------------------
# Main scraping function
# ---------------------------

def scrape_instantgaming_trending(max_items: int = 200):
    """
    Scrape the PC Trending page on Instant Gaming and save up to `max_items`
    products into data/raw/instantgaming.csv.
    """
    print("\n==============================")
    print(f"🎮  Instant Gaming TRENDING SCRAPER STARTED (LIMIT: {max_items} ITEMS)")
    print("==============================\n")

    driver = make_driver()
    driver_alive = True
    all_rows: list[dict] = []
    seen_urls: set[str] = set()

    try:
        print(f"🌍 Opening Trending page: {BASE_URL}")
        driver.get(BASE_URL)
        accept_cookies(driver)
        wait_for_results(driver)

        current_page = 1

        while len(all_rows) < max_items and driver_alive:
            print(f"\n📄 Scraping page {current_page} ...")

            try:
                html = driver.page_source
            except (NoSuchWindowException, InvalidSessionIdException):
                print("⚠️ Browser window closed / session invalid. Stopping.")
                driver_alive = False
                break

            remaining = max_items - len(all_rows)
            page_rows = parse_trending_page(html, remaining, seen_urls)

            print(f"   ➕ Parsed {len(page_rows)} items on this page.")
            all_rows.extend(page_rows)

            if len(all_rows) >= max_items:
                print(f"✅ Reached max_items limit ({max_items}).")
                break

            if not click_next_page_by_number(driver, current_page):
                break

            current_page += 1

        if not all_rows:
            print("⚠️ No products were scraped — nothing to save.")
            return

        df = pd.DataFrame(all_rows)
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

        # Optionally de-duplicate by URL
        df = df.drop_duplicates(subset=["product_url"])

        df.to_csv(OUTPUT_CSV, index=False)

        print("\n🧾 Sample of scraped data:")
        print(df.head())

        print("\n==============================")
        print(
            f"✅ SCRAPING COMPLETE — {len(df)} unique items saved to '{OUTPUT_CSV.as_posix()}'"
        )
        print("==============================\n")

    finally:
        print("🧹 Done. Closing browser...")
        if driver_alive:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    # Change the limit here when you run the script
    scrape_instantgaming_trending(max_items=1000)
