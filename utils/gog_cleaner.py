#!/usr/bin/env python3
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

# ---------------------------
# Paths
# ---------------------------

RAW_CANDIDATES = [
    Path("data/raw/gog.csv"),
    Path("data/raw/gog_products.csv"),
    Path("gog_products.csv"),
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_gog.csv"

# ---------------------------
# Parsing helpers
# ---------------------------

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
    
    # Remove 'N/A'
    if s.upper() == 'N/A':
        return np.nan

    # Remove currency symbols and extraneous chars
    s_clean = re.sub(r"[^\d.,\-]", "", s)

    if not s_clean:
        return np.nan

    # Handle comma/dot decimal separators
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
    
    # GOG dates are often ISO format already (YYYY-MM-DD)
    # or full timestamps
    s = str(date_str).strip()
    try:
        # Try taking just the date part if it's a timestamp
        if 'T' in s:
            s = s.split('T')[0]
        elif ' ' in s:
            s = s.split(' ')[0]
            
        # Validate format
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        return None

# ---------------------------
# Main cleaning logic
# ---------------------------

def load_raw_csv():
    for p in RAW_CANDIDATES:
        if p.exists():
            print(f"📥 Loading raw GOG data from: {p}")
            return pd.read_csv(p)
    
    # If we are in utils/, try looking up one level
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
    
    # Drop duplicates based on product_id or url
    if "product_id" in df.columns:
        df = df.drop_duplicates(subset=["product_id"])
    elif "url" in df.columns:
        df = df.drop_duplicates(subset=["url"])
    
    print(f"🔹 Shape after deduplication: {df.shape}")

    # Normalize columns
    # Map GOG scraper columns to standard schema
    # Expected GOG columns: title, price_final, price_base, discount_percentage, url, release_date
    
    # Price parsing
    if "price_final" in df.columns:
        df["price_usd"] = df["price_final"].apply(parse_price)
    else:
        df["price_usd"] = np.nan

    if "price_base" in df.columns:
        df["original_price_usd"] = df["price_base"].apply(parse_price)
    else:
        df["original_price_usd"] = np.nan

    # Discount parsing
    if "discount_percentage" in df.columns:
        df["discount_pct"] = df["discount_percentage"].apply(parse_discount_pct)
    else:
        df["discount_pct"] = 0.0

    # Date parsing
    if "release_date" in df.columns:
        df["release_date"] = df["release_date"].apply(parse_date)

    # Add metadata
    df["source"] = "gog"
    df["storefront"] = "GOG"
    df["platform"] = "PC" # GOG is PC only
    
    # Rename URL column if needed
    if "url" in df.columns:
        df = df.rename(columns={"url": "product_url"})

    # Select and reorder columns
    keep_cols = [
        "source", "storefront", "platform", "title", 
        "price_usd", "original_price_usd", "discount_pct",
        "product_url", "release_date"
    ]
    
    # Add any other useful columns that exist
    optional_cols = ["review_score", "genres", "tags"]
    for col in optional_cols:
        if col in df.columns:
            keep_cols.append(col)

    # Filter to available columns
    final_cols = [c for c in keep_cols if c in df.columns]
    cleaned = df[final_cols].copy()

    # Drop rows with no price AND no title (useless data)
    cleaned = cleaned.dropna(subset=["title"])

    # Ensure output directory exists
    # If running from utils/, output might need to be adjusted relative to project root
    # But we defined OUTPUT_DIR as relative to CWD. 
    # Assuming script is run from project root.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    cleaned.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"✅ Saved cleaned GOG data to: {OUTPUT_PATH}")
    print(f"✅ Final shape: {cleaned.shape}")
    print("\n🔎 Preview:")
    print(cleaned.head())

if __name__ == "__main__":
    main()
