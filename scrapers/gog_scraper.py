import csv
import json
import time
import os
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import requests

class GOGScraper:
    def __init__(self, headless=True):
        self.base_url = "https://www.gog.com"
        self.games_url = "https://www.gog.com/games"
        self.api_url = "https://www.gog.com/games/ajax/filtered"
        self.scraped_products = set()
        self.load_scraped_ids()
        self.driver = self.setup_driver(headless)

    def setup_driver(self, headless):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            raise

    def load_scraped_ids(self):
        if os.path.exists("gog_products.csv"):
            try:
                with open("gog_products.csv", "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("product_id"):
                            self.scraped_products.add(row["product_id"])
            except:
                pass

    def get_products_from_api(self, page=1, limit=48):
        params = {
            "page": page,
            "limit": limit,
            "sort": "popularity",
            "order": "desc",
            "mediaType": "game"
        }

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.gog.com/games",
                "Origin": "https://www.gog.com"
            }
            response = requests.get(self.api_url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
        return None

    def discover_products_selenium(self, max_scrolls=20):
        products = []
        try:
            self.driver.get(self.games_url)
            time.sleep(5)

            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0

            while scroll_count < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = self.driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    time.sleep(2)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break

                last_height = new_height
                scroll_count += 1

            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "product-tile, .product-tile, [data-product-id]")

            for elem in product_elements:
                try:
                    product_id = elem.get_attribute("data-product-id") or elem.get_attribute("data-id")
                    if not product_id:
                        continue

                    if product_id in self.scraped_products:
                        continue

                    try:
                        title_elem = elem.find_element(By.CSS_SELECTOR, ".product-tile__title, .product-title, h3, h4")
                        title = title_elem.text.strip()
                    except:
                        title = "N/A"

                    try:
                        link_elem = elem.find_element(By.CSS_SELECTOR, "a")
                        url = link_elem.get_attribute("href")
                    except:
                        url = f"{self.base_url}/en/game/{product_id}"

                    try:
                        price_elem = elem.find_element(By.CSS_SELECTOR, ".product-tile__price, .price, [data-price]")
                        price_final = price_elem.text.strip()
                    except:
                        price_final = "N/A"

                    try:
                        cover_elem = elem.find_element(By.CSS_SELECTOR, "img")
                        cover_image = cover_elem.get_attribute("src") or cover_elem.get_attribute("data-src")
                    except:
                        cover_image = "N/A"

                    product_data = {
                        "product_id": product_id,
                        "slug": url.split("/")[-1] if "/" in url else product_id,
                        "title": title,
                        "url": url,
                        "price_base": "N/A",
                        "price_final": price_final,
                        "price_currency": "USD",
                        "discount_percentage": 0,
                        "review_score": "N/A",
                        "release_date": "N/A",
                        "tags": "N/A",
                        "genres": "N/A",
                        "platforms": "N/A",
                        "cover_image": cover_image,
                        "is_discounted": False
                    }
                    products.append(product_data)
                    self.scraped_products.add(product_id)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Selenium discovery failed: {e}")

        return products

    def discover_products(self, max_pages=10, use_api=True):
        products = []

        if use_api:
            page = 1
            while page <= max_pages:
                print(f"Fetching page {page} via API...")
                data = self.get_products_from_api(page)

                if not data or not data.get("products"):
                    print("API returned no products, trying Selenium...")
                    break

                for product in data["products"]:
                    product_id = str(product.get("id", ""))
                    slug = product.get("slug", "")

                    if product_id and product_id not in self.scraped_products:
                        price_info = product.get("price", {}) if isinstance(product.get("price"), dict) else {}

                        tags_list = []
                        for tag in product.get("tags", []):
                            if isinstance(tag, dict):
                                tag_name = tag.get("name", "")
                            else:
                                tag_name = str(tag)
                            if tag_name:
                                tags_list.append(tag_name)

                        genres_list = []
                        for genre in product.get("genres", []):
                            if isinstance(genre, dict):
                                genre_name = genre.get("name", "")
                            else:
                                genre_name = str(genre)
                            if genre_name:
                                genres_list.append(genre_name)

                        works_on = product.get("worksOn", {})
                        platforms_list = []
                        if isinstance(works_on, dict):
                            platforms_list = [k for k, v in works_on.items() if v]
                        elif isinstance(works_on, list):
                            platforms_list = [str(p) for p in works_on]

                        product_data = {
                            "product_id": product_id,
                            "slug": slug,
                            "title": product.get("title", "N/A"),
                            "url": f"{self.base_url}/en/game/{slug}" if slug else "N/A",
                            "price_base": price_info.get("baseAmount", "N/A") if price_info else "N/A",
                            "price_final": price_info.get("finalAmount", "N/A") if price_info else "N/A",
                            "price_currency": price_info.get("currency", "USD") if price_info else "USD",
                            "discount_percentage": price_info.get("discountPercentage", 0) if price_info else 0,
                            "review_score": product.get("rating", "N/A"),
                            "release_date": product.get("releaseDate", "N/A"),
                            "tags": ", ".join(tags_list),
                            "genres": ", ".join(genres_list),
                            "platforms": ", ".join(platforms_list),
                            "cover_image": product.get("image", "N/A"),
                            "is_discounted": price_info.get("isDiscounted", False) if price_info else False
                        }
                        products.append(product_data)
                        self.scraped_products.add(product_id)

                if len(data.get("products", [])) < 48:
                    break

                page += 1
                time.sleep(2)

        if len(products) == 0:
            print("Using Selenium fallback for product discovery...")
            products = self.discover_products_selenium(max_scrolls=15)

        return products

    def extract_detail_data(self, product_url):
        detail_data = {
            "description_html": "N/A",
            "description_text": "N/A",
            "system_requirements": "N/A",
            "screenshots": "N/A",
            "trailer_url": "N/A",
            "extras": "N/A",
            "supported_languages": "N/A",
            "publisher": "N/A",
            "developer": "N/A",
            "age_rating": "N/A",
            "changelog": "N/A",
            "dlc": "N/A",
            "series": "N/A",
            "related_games": "N/A"
        }

        try:
            self.driver.get(product_url)
            time.sleep(4)

            description_selectors = [
                ".description",
                ".product-description",
                "[data-testid='description']",
                ".product-tabs__content",
                ".product-description__text"
            ]
            for selector in description_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data["description_html"] = elem.get_attribute("innerHTML") or "N/A"
                    detail_data["description_text"] = elem.text.strip() or "N/A"
                    break
                except:
                    continue

            req_selectors = [
                ".product-requirements",
                ".system-requirements",
                "[data-testid='system-requirements']",
                ".requirements"
            ]
            req_text = []
            for selector in req_selectors:
                try:
                    reqs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for req in reqs:
                        text = req.text.strip()
                        if text:
                            req_text.append(text)
                    if req_text:
                        break
                except:
                    continue
            if req_text:
                detail_data["system_requirements"] = " | ".join(req_text[:3])

            screenshot_selectors = [
                ".product-gallery img",
                ".screenshot img",
                ".product-screenshots img",
                "[data-testid='screenshot'] img",
                ".gallery img"
            ]
            screenshots = []
            for selector in screenshot_selectors:
                try:
                    imgs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for img in imgs[:20]:
                        src = img.get_attribute("src") or img.get_attribute("data-src") or img.get_attribute("data-full")
                        if src and ("http" in src or "//" in src):
                            if "//" in src and "http" not in src:
                                src = "https:" + src
                            screenshots.append(src)
                    if screenshots:
                        break
                except:
                    continue
            if screenshots:
                detail_data["screenshots"] = " | ".join(screenshots[:20])

            video_selectors = [
                ".product-video iframe",
                "video source",
                "[data-testid='trailer'] iframe",
                ".trailer iframe"
            ]
            for selector in video_selectors:
                try:
                    video_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data["trailer_url"] = video_elem.get_attribute("src") or video_elem.get_attribute("data-src") or "N/A"
                    if detail_data["trailer_url"] != "N/A":
                        break
                except:
                    continue

            extras_selectors = [
                ".product-extras .extra-item",
                ".extras .extra",
                "[data-testid='extras'] .item"
            ]
            for selector in extras_selectors:
                try:
                    extras = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    extras_list = [extra.text.strip() for extra in extras if extra.text.strip()]
                    if extras_list:
                        detail_data["extras"] = " | ".join(extras_list)
                        break
                except:
                    continue

            lang_selectors = [
                ".product-languages .language-item",
                ".languages .language",
                "[data-testid='languages'] .item"
            ]
            for selector in lang_selectors:
                try:
                    languages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    lang_list = [lang.text.strip() for lang in languages if lang.text.strip()]
                    if lang_list:
                        detail_data["supported_languages"] = " | ".join(lang_list)
                        break
                except:
                    continue

            publisher_selectors = [
                ".product-publisher",
                "[data-testid='publisher']",
                ".publisher",
                ".product-details__publisher"
            ]
            for selector in publisher_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data["publisher"] = elem.text.strip() or "N/A"
                    if detail_data["publisher"] != "N/A":
                        break
                except:
                    continue

            developer_selectors = [
                ".product-developer",
                "[data-testid='developer']",
                ".developer",
                ".product-details__developer"
            ]
            for selector in developer_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data["developer"] = elem.text.strip() or "N/A"
                    if detail_data["developer"] != "N/A":
                        break
                except:
                    continue

            rating_selectors = [
                ".product-rating",
                "[data-testid='age-rating']",
                ".age-rating",
                ".rating"
            ]
            for selector in rating_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data["age_rating"] = elem.text.strip() or "N/A"
                    if detail_data["age_rating"] != "N/A":
                        break
                except:
                    continue

            changelog_selectors = [
                ".product-changelog",
                ".changelog",
                "[data-testid='changelog']"
            ]
            for selector in changelog_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data["changelog"] = elem.text.strip() or "N/A"
                    if detail_data["changelog"] != "N/A":
                        break
                except:
                    continue

            dlc_selectors = [
                ".product-dlc .dlc-item",
                "[data-testid='dlc-item']",
                ".dlc .item"
            ]
            dlc_list = []
            for selector in dlc_selectors:
                try:
                    dlc_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for dlc in dlc_elems:
                        try:
                            dlc_title = dlc.find_element(By.CSS_SELECTOR, ".dlc-title, h3, h4, .title").text.strip()
                            if dlc_title:
                                dlc_list.append(dlc_title)
                        except:
                            pass
                    if dlc_list:
                        break
                except:
                    continue
            if dlc_list:
                detail_data["dlc"] = " | ".join(dlc_list[:10])

            series_selectors = [
                ".product-series",
                "[data-testid='series']",
                ".series"
            ]
            for selector in series_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    detail_data["series"] = elem.text.strip() or "N/A"
                    if detail_data["series"] != "N/A":
                        break
                except:
                    continue

            related_selectors = [
                ".related-games .game-item",
                "[data-testid='related-game']",
                ".related .game"
            ]
            related_games = []
            for selector in related_selectors:
                try:
                    related_elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for game in related_elems[:10]:
                        try:
                            game_title = game.text.strip()
                            if game_title:
                                related_games.append(game_title)
                        except:
                            pass
                    if related_games:
                        break
                except:
                    continue
            if related_games:
                detail_data["related_games"] = " | ".join(related_games)

        except Exception as e:
            print(f"Error extracting detail data from {product_url}: {e}")

        return detail_data

    def scrape(self, max_products=100, scrape_details=True):
        print("Starting GOG.com scraper...")

        products = self.discover_products(max_pages=50)
        print(f"Discovered {len(products)} new products")

        if len(products) == 0:
            print("No new products to scrape")
            return

        file_exists = os.path.exists("gog_products.csv")

        with open("gog_products.csv", "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "timestamp", "product_id", "slug", "title", "url", "price_base", "price_final",
                "price_currency", "discount_percentage", "review_score", "release_date", "tags",
                "genres", "platforms", "cover_image", "is_discounted", "description_html",
                "description_text", "system_requirements", "screenshots", "trailer_url", "extras",
                "supported_languages", "publisher", "developer", "age_rating", "changelog",
                "dlc", "series", "related_games"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            scraped_count = 0
            for i, product in enumerate(products[:max_products]):
                if scrape_details and product.get("url") != "N/A":
                    print(f"Scraping details for {product['title']} ({i+1}/{min(len(products), max_products)})...")
                    detail_data = self.extract_detail_data(product["url"])
                    product.update(detail_data)
                    time.sleep(2)

                product["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow(product)
                scraped_count += 1

            print(f"Successfully scraped {scraped_count} products")

    def close(self):
        if self.driver:
            self.driver.quit()

def main():
    import argparse

    parser = argparse.ArgumentParser(description="GOG.com Product Scraper")
    parser.add_argument("--max-products", type=int, default=50, help="Maximum products to scrape")
    parser.add_argument("--no-details", action="store_true", help="Skip detail page scraping")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")

    args = parser.parse_args()

    scraper = GOGScraper(headless=args.headless)
    try:
        scraper.scrape(max_products=args.max_products, scrape_details=not args.no_details)
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
