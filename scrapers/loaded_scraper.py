import time
import random
import pandas as pd
from datetime import datetime, timezone
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def human_wait(min_s=1.0, max_s=2.5):
    """Wait a random small delay to look human."""
    time.sleep(random.uniform(min_s, max_s))


def accept_cookies():
    """Try a list of XPaths to find a clickable element and click the first that works."""
    
    cookie_xpaths = [
            "//button[contains(., 'Accept all') or contains(., 'Accept All') or contains(., 'Accept cookies')]",
            "//button[contains(., 'Accept') and contains(., 'cookies')]",
            "//button[contains(., 'I agree') or contains(., 'Agree')]",
            "//button[contains(@id, 'onetrust-accept-btn-handler')]",
        ]

    for xp in cookie_xpaths:
        try:
            el = WebDriverWait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            el.click()
            return True
        except Exception:
            continue
    return False


def scroll_to_bottom(driver):
    while True:
        y_offset = driver.execute_script("return window.pageYOffset;")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_y_offset = driver.execute_script("return window.pageYOffset;")
        if new_y_offset == y_offset:
            break



def scrape_games(driver, already_scraped):
    """
    Scrape all currently visible product cards.
    Returns a list of dicts for newly found products.
    """
    new_items = []
    cards = driver.find_elements(By.CSS_SELECTOR,"a.product-tile, div.product-item, div.product, article.product, .product-listing a")

    for card in cards:
        
        #Title
        try:
            title = card.find_element(By.CSS_SELECTOR, "h3, .title, .product-title").text
        except Exception:
            title = card.get_attribute("aria-label") or card.get_attribute("title") or ""

        # Price
        try:
            price = card.find_element(By.CSS_SELECTOR, ".price, .product-price, .now-price, .sale-price").text
        except Exception:
            try:
                price = card.find_element(By.XPATH, ".//span[contains(@class,'price')]").text
            except Exception:
                price = ""

        new_items.append({
            "title": title.strip(),
            "price_raw": price.strip(),
            "scraped_at": datetime.now(timezone.utc).isoformat()
        })

    return new_items


def scrape_cdkeys(max_items=50):
    base_url = "https://www.cdkeys.com/latest-games"

    print("\n==============================")
    print(f"🎮  CDKeys SCRAPER STARTED (LIMIT: {max_items} ITEMS)")
    print("==============================\n")

    # --- Chrome setup ---
    options = Options()
    # options.add_argument("--headless")  # Keep visible while testing
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")

    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🌍 Opening Loaded homepage...")
        driver.get(base_url)
        human_wait(2.5, 4.5)

        # Accept cookies if any
        accept_cookies()
        
        # Scroll to bottom of the page
        scroll_to_bottom(driver)
        
        WebDriverWait.until(EC.presence_of_all_elements_located(By.CSS_SELECTOR, "a.product-tile, div.product-item, div.product, article"))
        print("✅ Product grid loaded.")

        # --- Main loop ---
        scraped_items = []

        print("\n🖱️ Starting scroll & scrape...\n")
        
        scrape_games()

        # --- Save results ---
        print("\n🧹 Done scrolling. Closing browser...")
        driver.quit()

        df = pd.DataFrame(scraped_items)
        filename = "loaded.csv"
        df.to_csv(f"{filename}", index=False)

        print("\n==============================")
        print(f"✅ SCRAPING COMPLETE — {len(df)} items saved to '{filename}'")
        print("==============================\n")

        return df

    except Exception as e:
        print("❗ Unexpected error:", e)
        driver.quit()
        return None


if __name__ == "__main__":
    scrape_cdkeys(max_items=50)
