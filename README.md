# Game Deals Scraper  
Web Scraping Project – Loaded.com | Steam | Epic Games

## Overview
This project automates the extraction of game data and deals from multiple online platforms — currently Loaded.com, Steam, and Epic Games. The goal is to collect, clean, and analyze information about game prices, discounts, and availability to help us compare offers across stores and detect trends in game sales.

## Objectives
1. Scrape real-time data about games (titles, prices, discounts, ratings, etc.)  
2. Clean and store the data in structured CSV files or a local database.  
3. Compare deals across different platforms.  
4. Visualize trends and pricing insights in Jupyter Notebooks (EDA phase).  
5. Automate the scraping process using scheduled GitHub Actions or cron jobs.

## Target Websites
Loaded.com – Game title, current price, discount, release date  
Steam Store – Game title, price, discount, review score, tags  
Epic Games Store – Game title, sale price, original price, release info  

(More sources may be added later, such as GOG or PlayStation Store.)

## Project Structure
game-deals-scraper/
│
├── data/
│   ├── raw/                     # Unprocessed scraped data
│   ├── cleaned/                 # Cleaned and formatted CSVs
│
├── notebooks/
│   └── EDA.ipynb                # Data analysis and visualizations
│
├── scrapers/
│   ├── loaded_scraper.py        # Scraper for Loaded.com
│   ├── steam_scraper.py         # Scraper for Steam Store
│   ├── epicgames_scraper.py     # Scraper for Epic Games
│   ├── gog_scraper.py           # Scraper for GOG
│   ├── instantgaming_scraper.py # Scraper for Instant Gaming
│   ├── xbox_scraper.py          # Scraper for Xbox
│
├── utils/
│   ├── *_cleaner.py             # Data cleaning scripts per platform
│
├── utils/
│   ├── helpers.py               # Common scraping utilities
│   ├── user_agents.py           # Randomized user-agent generator
│
├── .github/
│   └── workflows/
│       └── scrape.yml           # GitHub Actions automation
│
├── requirements.txt             # Project dependencies
├── README.md                    # Project overview (this file)
└── LICENSE

## Technologies Used
- Python 3.11+
- Selenium / BeautifulSoup4
- Pandas
- Requests / LXML
- GitHub Actions (for automation)
- Jupyter Notebook (for EDA & visualization)

## How It Works
1. Each scraper navigates its respective site and collects structured data (title, price, discount, etc.).  
2. Data is exported to /data/raw/ as CSV files.  
3. clean_data.py standardizes the format (e.g., removes symbols, converts prices, normalizes currency).  
4. Cleaned CSVs are saved to /data/cleaned/.  
5. EDA.ipynb uses Pandas and Matplotlib to analyze pricing trends, best discounts, and popular titles.  
6. GitHub Actions can automatically run the scrapers on a schedule (e.g., every 6 hours).

## Example Data Columns
title – Game name  
original_price – Price before discount  
discounted_price – Current sale price  
discount_percentage – % off the original price  
release_date – Original release date  
rating – Steam or Epic user rating  
platform – Source website (Steam / Epic / Loaded)  
timestamp – When data was scraped

## Data Cleaning
The cleaning stage ensures all data is consistent:
- Converts prices to float values (removes currency symbols like $ or €).  
- Ensures date formats are ISO-standard (YYYY-MM-DD).  
- Removes duplicates and empty rows.  
- Calculates discount percentages if missing.

## Next Steps
- Add more platforms (e.g., GOG, Ubisoft Connect)  
- Integrate a database (SQLite or PostgreSQL) for better storage  
- Build a web dashboard (e.g., Flask + Chart.js or Svelte frontend)  
- Add deal alerts for major price drops  
- Perform time-series analysis on discount frequency

## Contributors
Mohamad Diab - 20220584
Mohamad Chehade -
Sahar Sabbagh - 
