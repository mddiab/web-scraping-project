
"""
gog_cleaner.py

Clean the raw GOG CSV into a modeling-friendly format,
sharing as many fields as possible with other scrapers.
"""

import re
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

RAW_CANDIDATES = [
    Path("data/raw/gog.csv"),
    Path("data/raw/gog_products.csv"),
    Path("gog_products.csv"),
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_gog.csv"

def parse_price(text):
    """
    Convert price strings to float.
    Handles 'Free', currency symbols, and standard number formats.
    """
    if pd.isna(text):
        return np.nan
    s = str(text).strip()

    if "free" in s.lower():
        return 0.0

    if s.upper() == 'N/A':
        return np.nan

    s_clean = re.sub(r"[^\d.,\-]", "", s)

    if not s_clean:
        return np.nan

    if s_clean.count(".") == 1 and s_clean.count(",") >= 1:
        s_clean = s_clean.replace(",", "")
    elif s_clean.count(",") == 1 and s_clean.count(".") == 0:
        s_clean = s_clean.replace(",", ".")

    try:
        return float(s_clean)
    except ValueError:
        return np.nan

def parse_discount_pct(val):
    """
    Convert discount to positive float percentage.
    """
    if pd.isna(val):
        return 0.0

    if isinstance(val, (int, float)):
        return float(abs(val))

    s = str(val).strip()
    if not s or s.upper() == 'N/A':
        return 0.0

    m = re.search(r"(-?\d+)", s)
    if not m:
        return 0.0
    return float(abs(float(m.group(1))))

def parse_date(date_str):
    """
    Attempt to parse date string to YYYY-MM-DD.
    """
    if pd.isna(date_str) or str(date_str).strip().upper() == 'N/A':
        return None

    s = str(date_str).strip()
    try:

        if 'T' in s:
            s = s.split('T')[0]
        elif ' ' in s:
            s = s.split(' ')[0]

        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        return None

def load_raw_csv():
    for p in RAW_CANDIDATES:
        if p.exists():
            print(f"📥 Loading raw GOG data from: {p}")
            return pd.read_csv(p)

    parent_candidates = [Path("../") / p for p in RAW_CANDIDATES]
    for p in parent_candidates:
        if p.exists():
            print(f"📥 Loading raw GOG data from: {p}")
            return pd.read_csv(p)

    raise FileNotFoundError(
        "GOG data file not found in expected locations."
    )

def main():
    try:
        df = load_raw_csv()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    print(f"🔹 Raw shape: {df.shape}")

    if "product_id" in df.columns:
        df = df.drop_duplicates(subset=["product_id"])
    elif "url" in df.columns:
        df = df.drop_duplicates(subset=["url"])

    print(f"🔹 Shape after deduplication: {df.shape}")

    if "price_final" in df.columns:
        df["price_usd"] = df["price_final"].apply(parse_price)
    else:
        df["price_usd"] = np.nan

    if "price_base" in df.columns:
        df["original_price_usd"] = df["price_base"].apply(parse_price)
    else:
        df["original_price_usd"] = np.nan

    if "discount_percentage" in df.columns:
        df["discount_pct"] = df["discount_percentage"].apply(parse_discount_pct)
    else:
        df["discount_pct"] = 0.0

    if "release_date" in df.columns:
        df["release_date"] = df["release_date"].apply(parse_date)

    df["source"] = "gog"
    df["storefront"] = "GOG"
    df["platform"] = "PC" 

    if "url" in df.columns:
        df = df.rename(columns={"url": "product_url"})

    keep_cols = [
        "source", "storefront", "platform", "title", 
        "price_usd", "original_price_usd", "discount_pct",
        "product_url", "release_date"
    ]

    optional_cols = ["review_score", "genres", "tags"]
    for col in optional_cols:
        if col in df.columns:
            keep_cols.append(col)

    final_cols = [c for c in keep_cols if c in df.columns]
    cleaned = df[final_cols].copy()

    cleaned = cleaned.dropna(subset=["title"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"✅ Saved cleaned GOG data to: {OUTPUT_PATH}")
    print(f"✅ Final shape: {cleaned.shape}")
    print("\n🔎 Preview:")
    print(cleaned.head())

if __name__ == "__main__":
    main()
