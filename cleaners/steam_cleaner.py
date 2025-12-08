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






RAW_CANDIDATES = [
    Path("data/raw/steam.csv"),
    Path("steam.csv"),
    Path("/mnt/data/steam.csv"),  
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_steam.csv"







EUR_TO_USD_RATE = 1.08
USD_TO_EUR_RATE = 1.0 / EUR_TO_USD_RATE






def parse_price_usd(text):
    """
    Convert price strings like '$39.99' or 'Free' to float USD.
    - 'Free' / 'Free to Play' -> 0.0
    - NaN or weird strings -> NaN
    """
    if pd.isna(text):
        return np.nan
    s = str(text).strip()

    
    if "free" in s.lower():
        return 0.0

    
    
    s_clean = re.sub(r"[^\d.,\-]", "", s)

    if not s_clean:
        return np.nan

    
    
    if s_clean.count(".") == 1 and s_clean.count(",") >= 1:
        s_clean = s_clean.replace(",", "")
    else:
        
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

    
    if "coming soon" in s or "tba" in s or "to be announced" in s:
        return True

    
    try:
        dt = datetime.strptime(str(release_date_str), "%d %b, %Y")
    except ValueError:
        return False

    today = datetime.today()
    return dt.date() > today.date()






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

    
    expected_cols = [
        "source",       
        "category",     
        "title",
        "release_date",
        "price_raw",
        "discount_raw",
        "product_url",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in raw Steam CSV: {missing}")

    
    before = len(df)
    df = df.drop_duplicates(subset=["product_url"]).copy()
    after = len(df)
    print(f"🧹 Removed {before - after} duplicate rows based on product_url")

    
    df["price_usd"] = df["price_raw"].apply(parse_price_usd)
    df["discount_pct"] = df["discount_raw"].apply(parse_discount_pct)

    
    df["price_eur"] = (df["price_usd"] * USD_TO_EUR_RATE).round(2)

    
    df["original_price_eur"] = df.apply(
        lambda row: compute_original_price(row["price_eur"], row["discount_pct"]),
        axis=1,
    )

    
    df["platform"] = "PC"
    df["storefront"] = "Steam"

    
    df["is_preorder"] = df["release_date"].apply(infer_is_preorder)

    
    before = len(df)
    df = df.dropna(subset=["price_usd", "product_url"])
    after = len(df)
    print(f"🧹 Dropped {before - after} rows with missing price/url")

    
    cleaned = df[
        [
            "source",                
            "title",                 
            "platform",              
            "storefront",            
            "is_preorder",           
            "price_eur",             
            "price_usd",             
            "original_price_eur",    
            "discount_pct",          
            "product_url",           

            
            "category",              
            "release_date",          
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
