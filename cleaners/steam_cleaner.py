"""
steam_cleaner.py

Clean the raw Steam CSV into a modeling-friendly format,
sharing as many fields as possible with Loaded and InstantGaming.
"""

import re
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd


# ---------------------------
# Paths
# ---------------------------

RAW_CANDIDATES = [
    Path("data/raw/steam.csv"),
    Path("steam.csv"),
    Path("/mnt/data/steam.csv"),  # for local testing
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_steam.csv"

# ---------------------------
# Currency
# ---------------------------

# Same rate you used for InstantGaming:
# EUR → USD
EUR_TO_USD_RATE = 1.08
USD_TO_EUR_RATE = 1.0 / EUR_TO_USD_RATE


# ---------------------------
# Parsing helpers
# ---------------------------

def parse_price_usd(text):
    """
    Convert price strings like '$39.99' or 'Free' to float USD.
    - 'Free' / 'Free to Play' -> 0.0
    - NaN or weird strings -> NaN
    """
    if pd.isna(text):
        return np.nan
    s = str(text).strip()

    # Free games
    if "free" in s.lower():
        return 0.0

    # Remove currency symbols and extraneous chars
    # (handles '$39.99', 'US$39.99', etc.)
    s_clean = re.sub(r"[^\d.,\-]", "", s)

    if not s_clean:
        return np.nan

    # Simple: assume dot decimal, commas as thousands
    # e.g. "1,299.99" -> "1299.99"
    if s_clean.count(".") == 1 and s_clean.count(",") >= 1:
        s_clean = s_clean.replace(",", "")
    else:
        # If only comma appears, treat it as decimal
        if s_clean.count(",") == 1 and s_clean.count(".") == 0:
            s_clean = s_clean.replace(",", ".")

    try:
        return float(s_clean)
    except ValueError:
        return np.nan


def parse_discount_pct(text):
    """
    Convert strings like '-15%' or '15%' to a positive float (15.0).
    If missing, return 0.0.
    """
    if pd.isna(text):
        return 0.0
    s = str(text)
    m = re.search(r"(-?\d+)", s)
    if not m:
        return 0.0
    val = float(m.group(1))
    return abs(val)


def compute_original_price(price, discount_pct):
    """
    Estimate original price from current price and discount percentage.
    If discount_pct <= 0, just return price.
    """
    if pd.isna(price):
        return np.nan
    if discount_pct is None or discount_pct <= 0:
        return price
    try:
        orig = price / (1 - discount_pct / 100.0)
        return round(orig, 2)
    except ZeroDivisionError:
        return price


def infer_is_preorder(release_date_str: str) -> bool:
    """
    Infer if a Steam title is a preorder:
    - If release date is a valid future date -> True
    - If it contains 'coming soon' / 'tba' -> True
    - Else -> False
    """
    if pd.isna(release_date_str):
        return False

    s = str(release_date_str).strip().lower()

    # Text-based hints
    if "coming soon" in s or "tba" in s or "to be announced" in s:
        return True

    # Try to parse e.g. '21 Aug, 2012'
    try:
        dt = datetime.strptime(str(release_date_str), "%d %b, %Y")
    except ValueError:
        return False

    today = datetime.today()
    return dt.date() > today.date()


# ---------------------------
# Main cleaning logic
# ---------------------------

def load_raw_csv():
    for p in RAW_CANDIDATES:
        if p.exists():
            print(f"📥 Loading raw Steam data from: {p}")
            return pd.read_csv(p)
    raise FileNotFoundError(
        "steam.csv not found in any of: "
        + ", ".join(str(p) for p in RAW_CANDIDATES)
    )


def main():
    df = load_raw_csv()
    print(f"🔹 Raw shape: {df.shape}")
    print(f"🔹 Columns: {list(df.columns)}")

    # Expected columns from your scraper
    expected_cols = [
        "source",       # 'steam'
        "category",     # top_sellers / specials / trending / ...
        "title",
        "release_date",
        "price_raw",
        "discount_raw",
        "product_url",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in raw Steam CSV: {missing}")

    # Drop duplicate URLs
    before = len(df)
    df = df.drop_duplicates(subset=["product_url"]).copy()
    after = len(df)
    print(f"🧹 Removed {before - after} duplicate rows based on product_url")

    # Price + discount
    df["price_usd"] = df["price_raw"].apply(parse_price_usd)
    df["discount_pct"] = df["discount_raw"].apply(parse_discount_pct)

    # Convert to EUR for cross-site consistency
    df["price_eur"] = (df["price_usd"] * USD_TO_EUR_RATE).round(2)

    # Original price in EUR (back-calculated from discount)
    df["original_price_eur"] = df.apply(
        lambda row: compute_original_price(row["price_eur"], row["discount_pct"]),
        axis=1,
    )

    # Platform & storefront (fixed for Steam)
    df["platform"] = "PC"
    df["storefront"] = "Steam"

    # Preorder flag
    df["is_preorder"] = df["release_date"].apply(infer_is_preorder)

    # Drop rows without usable price or URL
    before = len(df)
    df = df.dropna(subset=["price_usd", "product_url"])
    after = len(df)
    print(f"🧹 Dropped {before - after} rows with missing price/url")

    # Final column order — matching other sites as much as possible
    cleaned = df[
        [
            "source",                # 'steam'
            "title",                 # game title
            "platform",              # PC
            "storefront",            # Steam
            "is_preorder",           # True/False
            "price_eur",             # normalized EUR
            "price_usd",             # native Steam USD
            "original_price_eur",    # estimated original EUR price
            "discount_pct",          # numeric discount percentage
            "product_url",           # link to game page

            # Extra useful fields (Steam-specific but nice to keep)
            "category",              # top_sellers / specials / trending / ...
            "release_date",          # raw text date
        ]
    ].copy()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"✅ Saved cleaned Steam data to: {OUTPUT_PATH}")
    print(f"✅ Final shape: {cleaned.shape}")
    print("\n🔎 Preview:")
    print(cleaned.head())


if __name__ == "__main__":
    main()
