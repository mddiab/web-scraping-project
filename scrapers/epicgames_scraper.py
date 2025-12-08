import time
import csv
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def human_delay(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))

def human_mouse_move(driver):
    try:
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(20, 80), random.randint(20, 80)).perform()
        actions.move_by_offset(-random.randint(20, 80), random.randint(20, 80)).perform()
    except:
        pass

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    driver = uc.Chrome(options=options)
    return driver

def handle_age_verification(driver):
    """
    Epic Games Age Gate Handler (Fixed for popper-based dropdown menus)
    """

    time.sleep(1)

    try:
        popup = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='AgeSelect'], div[data-testid='age-gate-wrapper']")
        if not popup:
            return
        print("[AGE-GATE] Detected popup, solving...")

        wait = WebDriverWait(driver, 10)

        def select_from_dropdown(toggle_selector, desired_text):
            """
            toggle_selector = css for the dropdown toggle button
            desired_text = '1990', '01', '12', etc.
            """

            toggle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, toggle_selector)))
            toggle.click()
            time.sleep(0.6)

            menu_items = wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                "div[data-popper-placement] ul[role='menu'] li button[data-testid='MenuItemButton']"
            )))

            for item in menu_items:
                if item.text.strip() == desired_text:
                    item.click()
                    time.sleep(0.5)
                    return True

            print(f"[AGE-GATE] Could not find: {desired_text}")
            return False

        select_from_dropdown("button#year_toggle", "1990")

        select_from_dropdown("button#month_toggle", "01")

        select_from_dropdown("button#day_toggle", "01")

        time.sleep(0.4)

        try:
            btn = wait.until(EC.element_to_be_clickable((By.ID, "btn_age_continue")))
            driver.execute_script("arguments[0].removeAttribute('disabled');", btn)
            btn.click()
            print("[AGE-GATE] Continue clicked successfully")
        except:
            print("[AGE-GATE] Could not click Continue — trying fallback")
            try:
                driver.find_element(By.XPATH, "//button[span[text()='Continue']]").click()
            except:
                print("[AGE-GATE] Continue button failed")

        time.sleep(1)
        print("[AGE-GATE] Done ✔")

    except Exception as e:
        print(f"[AGE-GATE ERROR] {e}")

def scrape_game_detail_page(driver, base):
    game = base.copy()
    wait = WebDriverWait(driver, 20)

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "main")))
    except:
        return game

    human_delay()
    human_mouse_move(driver)

    try:
        game["title"] = driver.find_element(
            By.CSS_SELECTOR, "span[data-testid='pdp-title']"
        ).text.strip()
    except:
        game["title"] = game.get("title", "")

    try:
        game["description"] = driver.find_element(
            By.CSS_SELECTOR, "div.css-1myreog"
        ).text.strip()
    except:
        game["description"] = ""

    try:
        tag_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/en-US/browse?tag=')]")
        tag_texts = [t.text.strip() for t in tag_links if t.text.strip()]
        joined = "|".join(tag_texts)
        game["genres"] = joined
        game["tags"] = joined
    except:
        game["genres"] = ""
        game["tags"] = ""

    try:
        plat_items = driver.find_elements(By.CSS_SELECTOR, "li[data-testid^='metadata-platform-']")
        plats = [p.text.strip() for p in plat_items if p.text.strip()]
        game["platforms"] = "|".join(plats)
    except:
        game["platforms"] = ""

    try:
        game["developer"] = driver.find_element(
            By.CSS_SELECTOR, "span[data-testid='metadata-developer-single']"
        ).text.strip()
    except:
        game["developer"] = ""

    try:
        pub_span = driver.find_element(
            By.XPATH, "//span[normalize-space()='Publisher']/following::span[1]"
        )
        game["publisher"] = pub_span.text.strip()
    except:
        game["publisher"] = ""

    try:
        time_elem = driver.find_element(
            By.XPATH, "//span[normalize-space()='Initial Release']/following::time[1]"
        )
        game["release_date"] = time_elem.text.strip()
    except:
        try:
            time_elem = driver.find_element(
                By.XPATH, "//span[normalize-space()='Release Date']/following::time[1]"
            )
            game["release_date"] = time_elem.text.strip()
        except:
            game["release_date"] = ""

    try:
        age = ""
        descs = []

        try:
            age = driver.find_element(
                By.CSS_SELECTOR, "div[data-testid='ratings-title'] strong"
            ).text.strip()
        except:
            pass

        try:
            desc_spans = driver.find_elements(
                By.CSS_SELECTOR, "div[data-testid='ratings-descriptions'] span"
            )
            descs = [d.text.strip() for d in desc_spans]
        except:
            pass

        if age or descs:
            if descs:
                game["rating"] = f"{age} ({'; '.join(descs)})" if age else "; ".join(descs)
            else:
                game["rating"] = age
        else:
            game["rating"] = ""
    except:
        game["rating"] = ""

    try:
        req_block = driver.find_element(By.CSS_SELECTOR, "div[data-component='SystemRequirements']")
        game["system_requirements"] = req_block.text.strip()
    except:
        game["system_requirements"] = ""

    return game

def scrape_page(page_url):
    driver = init_driver()
    print(f"[PAGE] {page_url}")

    driver.get(page_url)
    human_delay()
    human_mouse_move(driver)

    wait = WebDriverWait(driver, 25)

    try:
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[data-component='BrowseOfferCard']")
        ))
    except:
        print("[ERROR] No game cards found")
        driver.quit()
        return []

    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component='BrowseOfferCard']")
    print(f"[INFO] {len(cards)} cards")

    listing = []

    for card in cards:
        g = {}

        try:
            link = card.find_element(By.CSS_SELECTOR, "a[href*='/en-US/']")
            g["url"] = link.get_attribute("href")
        except:
            continue

        try:
            g["title"] = card.text.strip()
        except:
            g["title"] = ""

        try:
            disc_elem = card.find_element(By.XPATH, ".//span[contains(text(),'%')]")
            g["discount_percent"] = disc_elem.text.strip()
        except:
            g["discount_percent"] = ""

        try:
            price_spans = card.find_elements(By.XPATH, ".//span[contains(text(),'$')]")
        except:
            price_spans = []

        if price_spans:
            g["discount_price"] = price_spans[0].text.strip()
        else:
            g["discount_price"] = ""

        try:
            full_elem = card.find_element(By.XPATH, ".//strong[contains(text(),'$')]")
            g["full_price"] = full_elem.text.strip()
        except:
            try:
                g["full_price"] = price_spans[0].text.strip() if price_spans else ""
            except:
                g["full_price"] = ""

        g["is_discounted"] = "yes" if g["discount_percent"] else "no"

        def to_numeric(v):
            if not v:
                return ""
            if v.lower() == "free":
                return "Free"
            clean = v.replace("$", "").replace(",", "")
            try:
                return float(clean)
            except:
                return ""

        g["full_price"] = to_numeric(g["full_price"])
        g["discount_price"] = to_numeric(g["discount_price"])

        listing.append(g)

    results = []

    for g in listing:
        try:
            driver.get(g["url"])
            human_delay()
            handle_age_verification(driver)
            full = scrape_game_detail_page(driver, g)
            results.append(full)
        except Exception as e:
            print("[ERROR] detail:", e)
            results.append(g)

    driver.quit()
    return results

def scrape_all_pages(page_urls, max_workers=2):
    all_games = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_page, url): url for url in page_urls}
        for future in as_completed(futures):
            try:
                all_games.extend(future.result())
            except Exception as e:
                print("[THREAD ERROR]", e)
    return all_games

def save_to_csv(data, filename="epic_games_full.csv"):
    fields = [
        "title", "url",
        "full_price", "discount_price", "discount_percent", "is_discounted",
        "genres", "tags", "platforms",
        "developer", "publisher", "release_date",
        "rating", "system_requirements",
        "description",
    ]

    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k, "") for k in fields})

    print(f"[DONE] Saved {len(data)} games → {filename}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Epic Games Scraper")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum number of items to scrape")
    parser.add_argument("--max-workers", type=int, default=2, help="Number of worker threads")
    args = parser.parse_args()

    num_pages = (args.limit + 39) // 40

    num_pages = min(num_pages, 149)

    print(f"Scraping {num_pages} pages to get approx {args.limit} items...")

    page_urls = [
        f"https://store.epicgames.com/en-US/browse?"
        f"sortBy=relevancy&sortDir=DESC&count=40&start={(p-1)*40}"
        for p in range(1, num_pages + 1)
    ]

    all_data = scrape_all_pages(page_urls, max_workers=args.max_workers)

    if len(all_data) > args.limit:
        all_data = all_data[:args.limit]

    save_to_csv(all_data)

if __name__ == "__main__":
    main()
