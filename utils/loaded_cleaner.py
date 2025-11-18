"""
loaded_cleaner.py

Clean the raw Loaded.com games data.

- Reads:  data/raw/loaded.csv   (fallback: ./loaded.csv)
- Writes: data/cleaned/cleaned_loaded.csv

Notes:
- Original prices on Loaded.com are in GBP (£).
- We convert them to USD ($) using a fixed rate (GBP_TO_USD).
  Change GBP_TO_USD below if you want a different rate.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------
# Config
# ---------------------------

RAW_CANDIDATES = [
    Path("data/raw/loaded.csv"),
    Path("loaded.csv"),
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_loaded.csv"

# Approximate conversion rate — adjust if you want
GBP_TO_USD = 1.25


# ---------------------------
# Helpers
# ---------------------------

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

    # Remove common currency symbols
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

    # Xbox first (catches Xbox One, Xbox Series X|S, etc.)
    if "xbox" in padded:
        return "Xbox"

    # PlayStation family
    if any(x in padded for x in [" ps5 ", " ps4 ", " ps3 ", " playstation ", " ps vita ", " ps vr "]):
        return "PlayStation"

    # Switch / Nintendo
    if "switch" in padded or " nintendo " in padded:
        return "Nintendo Switch"

    # PC keywords
    if " pc " in padded or padded.strip().endswith(" pc") or " (pc" in padded:
        return "PC"

    # Titles that mention Steam usually mean PC as well
    if "steam" in padded:
        return "PC"

    return "Unknown"


def clean_loaded(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning steps to the Loaded dataset."""
    df = df_raw.copy()

    # Fix the source column: the scraper stored literally "source"
    df["source"] = "loaded.com"

    # Strip whitespace / normalize text
    df["title"] = df["title"].astype(str).str.strip()
    df["product_url"] = df["product_url"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip().str.lower()

    # --- Price cleaning ---

    # Step 1: numeric price in GBP (from price_raw)
    df["price_gbp"] = df["price_raw"].map(clean_price_gbp)

    before = len(df)
    df = df[df["price_gbp"].notna() & (df["price_gbp"] > 0)]
    after_price = len(df)

    # Step 2: convert to USD (this will be our main 'price' column)
    df["price"] = (df["price_gbp"] * GBP_TO_USD).round(2)

    # --- Platform inference ---

    df["platform"] = df["title"].map(infer_platform)

    # --- Timestamps ---

    df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce", utc=True)
    df["scraped_date"] = df["scraped_at"].dt.date

    # Drop exact duplicates by product_url (if future runs append)
    before_dup = len(df)
    df = df.drop_duplicates(subset=["product_url"])
    after_dup = len(df)

    # Reorder columns
    cols = [
        "source",
        "title",
        "platform",     # NEW
        "price",        # numeric price in USD ($)
        "price_gbp",    # numeric price in GBP (£)
        "price_raw",    # original raw price string
        "category",
        "product_url",
        "scraped_at",
        "scraped_date",
    ]
    df = df[cols]

    print(f"   🔹 Dropped {before - after_price} rows with invalid price.")
    print(f"   🔹 Dropped {before_dup - after_dup} duplicate product_url rows.")
    return df


# ---------------------------
# Main
# ---------------------------

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
    df_clean.to_csv(OUTPUT_PATH, index=False)

    print(f"\n✅ Cleaned data saved to: {OUTPUT_PATH}")
    print(f"   ➜ Cleaned shape: {df_clean.shape}")
    print("=======================================")
    print("✅ DONE")
    print("=======================================")


if __name__ == "__main__":
    main()
