"""
loaded_cleaner.py

Clean the raw Loaded.com games data.

- Reads:  data/raw/loaded.csv   (fallback: ./loaded.csv)
- Writes: data/cleaned/cleaned_loaded.csv

Output columns (aligned with other stores):
    source, title, platform, storefront, is_preorder,
    price_eur, price_usd, original_price_eur, discount_pct,
    product_url, category, scraped_at_utc
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

RAW_CANDIDATES = [
    Path("data/raw/loaded.csv"),
    Path("loaded.csv"),
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_loaded.csv"

GBP_TO_EUR = 1.17
EUR_TO_USD = 1.08

def find_raw_path(candidates=RAW_CANDIDATES) -> Path:
    """Return the first existing path from the candidates list, or raise if none exist."""
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"❌ Could not find raw Loaded data. Tried: {[str(p) for p in candidates]}"
    )

def clean_price_gbp(value):
    """
    Convert a price string like '£25.99' into a float 25.99 (GBP).
    Returns NaN if parsing fails.
    """
    if pd.isna(value):
        return np.nan

    text = str(value).strip()

    for sym in ["£", "$", "€"]:
        text = text.replace(sym, "")

    match = re.findall(r"[0-9]+(?:\.[0-9]+)?", text)
    if not match:
        return np.nan

    try:
        return float(match[0])
    except ValueError:
        return np.nan

def infer_platform(title: str) -> str:
    """
    Guess platform from the game title text.

    Returns one of: 'PC', 'Xbox', 'PlayStation', 'Nintendo Switch', 'Unknown'
    """
    if not isinstance(title, str):
        return "Unknown"

    t = title.lower()
    padded = f" {t} "

    if "xbox" in padded:
        return "Xbox"

    if any(x in padded for x in [" ps5 ", " ps4 ", " ps3 ", " playstation ", " ps vita ", " ps vr "]):
        return "PlayStation"

    if "switch" in padded or " nintendo " in padded:
        return "Nintendo Switch"

    if " pc " in padded or padded.strip().endswith(" pc") or " (pc" in padded:
        return "PC"

    if "steam" in padded:
        return "PC"

    return "Unknown"

def infer_is_preorder(title: str) -> bool:
    """True if title mentions pre-order / preorder / pre order."""
    if not isinstance(title, str):
        return False
    t = title.lower()
    return ("pre-order" in t) or ("preorder" in t) or ("pre order" in t)

def clean_loaded(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning steps to the Loaded dataset and return unified columns."""
    df = df_raw.copy()

    df["source"] = "loaded.com"

    df["title"] = df["title"].astype(str).str.strip()
    df["product_url"] = df["product_url"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip().str.lower()

    df["price_gbp"] = df["price_raw"].map(clean_price_gbp)

    before = len(df)
    df = df[df["price_gbp"].notna() & (df["price_gbp"] > 0)]
    after_price = len(df)

    df["price_eur"] = (df["price_gbp"] * GBP_TO_EUR).round(2)
    df["price_usd"] = (df["price_eur"] * EUR_TO_USD).round(2)

    df["discount_pct"] = 0.0
    df["original_price_eur"] = df["price_eur"]

    df["platform"] = df["title"].map(infer_platform)
    df["storefront"] = "Loaded/CDKeys"
    df["is_preorder"] = df["title"].map(infer_is_preorder)

    df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce", utc=True)

    df["scraped_at_utc"] = df["scraped_at"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    before_dup = len(df)
    df = df.drop_duplicates(subset=["product_url"])
    after_dup = len(df)

    cols = [
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
        "scraped_at_utc",       
    ]
    df = df[cols]

    print(f"   🔹 Dropped {before - after_price} rows with invalid price.")
    print(f"   🔹 Dropped {before_dup - after_dup} duplicate product_url rows.")
    return df

def main():
    raw_path = find_raw_path()
    print("=======================================")
    print("🎮  Loaded.com CLEANER STARTED")
    print("=======================================")
    print(f"📥 Loading raw data from: {raw_path}")

    df_raw = pd.read_csv(raw_path)
    print(f"   ➜ Raw shape: {df_raw.shape}")

    df_clean = clean_loaded(df_raw)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n✅ Cleaned data saved to: {OUTPUT_PATH}")
    print(f"   ➜ Cleaned shape: {df_clean.shape}")
    print("=======================================")
    print("✅ DONE")
    print("=======================================")

if __name__ == "__main__":
    main()
