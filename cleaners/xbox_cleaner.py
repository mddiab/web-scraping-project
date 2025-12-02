"""
xbox_cleaner.py

Clean the raw Xbox Store CSV into a modeling-friendly format,
sharing as many fields as possible with Loaded, InstantGaming, and Steam.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------
# Paths
# ---------------------------

RAW_CANDIDATES = [
    Path("data/raw/xbox.csv"),
    Path("xbox.csv"),
    Path("/mnt/data/xbox.csv"),  # for local testing
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_xbox.csv"

# ---------------------------
# Currency
# ---------------------------

# Same rate you used elsewhere
EUR_TO_USD_RATE = 1.08
USD_TO_EUR_RATE = 1.0 / EUR_TO_USD_RATE


# ---------------------------
# Helpers
# ---------------------------

def parse_price_usd(text):
    """
    Convert Xbox price strings like '$39.99', 'Free', 'Free+' to float USD.
    - 'Free' / 'Free+' -> 0.0
    - NaN or weird strings -> NaN
    """
    if pd.isna(text):
        return np.nan
    s = str(text).strip()

    # Free variants
    if "free" in s.lower():
        return 0.0

    # Remove currency symbols and extras, keep digits/.,,
    s_clean = re.sub(r"[^\d.,\-]", "", s)

    if not s_clean:
        return np.nan

    # Assume US style (dot decimal). If comma present, treat as thousands or decimal.
    if s_clean.count(".") == 1 and s_clean.count(",") >= 1:
        # "1,299.99" -> "1299.99"
        s_clean = s_clean.replace(",", "")
    else:
        # "19,99" -> "19.99"
        if s_clean.count(",") == 1 and s_clean.count(".") == 0:
            s_clean = s_clean.replace(",", ".")

    try:
        return float(s_clean)
    except ValueError:
        return np.nan


def compute_original_price(price, discount_pct):
    """
    Estimate original price from current price and discount percentage.
    If discount_pct <= 0, just return price.
    (For Xbox we don't have discounts, so discount_pct will be 0.)
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


def infer_is_preorder_from_title(title: str) -> bool:
    """
    Rough heuristic: mark as preorder if title mentions 'pre-order' / 'pre order'.
    """
    if pd.isna(title):
        return False
    s = str(title).lower()
    return ("pre-order" in s) or ("pre order" in s)


# ---------------------------
# Main cleaning logic
# ---------------------------

def load_raw_csv():
    for p in RAW_CANDIDATES:
        if p.exists():
            print(f"📥 Loading raw Xbox data from: {p}")
            return pd.read_csv(p)
    raise FileNotFoundError(
        "xbox.csv not found in any of: "
        + ", ".join(str(p) for p in RAW_CANDIDATES)
    )


def main():
    df = load_raw_csv()
    print(f"🔹 Raw shape: {df.shape}")
    print(f"🔹 Columns: {list(df.columns)}")

    # Expected columns from your scraper
    expected_cols = [
        "store",           # 'xbox'
        "category",        # e.g. 'all_games'
        "title",
        "price_text",
        "product_url",
        "scraped_at_utc",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in raw Xbox CSV: {missing}")

    # Rename store -> source to match other cleaners
    df = df.rename(columns={"store": "source"})

    # Drop duplicate URLs
    before = len(df)
    df = df.drop_duplicates(subset=["product_url"]).copy()
    after = len(df)
    print(f"🧹 Removed {before - after} duplicate rows based on product_url")

    # Price in USD
    df["price_usd"] = df["price_text"].apply(parse_price_usd)

    # Convert to EUR for consistency with other sites
    df["price_eur"] = (df["price_usd"] * USD_TO_EUR_RATE).round(2)

    # No discount info in this scrape → set discount_pct = 0
    df["discount_pct"] = 0.0

    # Original price (same as current since no discount info)
    df["original_price_eur"] = df.apply(
        lambda row: compute_original_price(row["price_eur"], row["discount_pct"]),
        axis=1,
    )

    # Platform & storefront
    df["platform"] = "Xbox"
    df["storefront"] = "Microsoft Store"

    # Preorder flag from title
    df["is_preorder"] = df["title"].apply(infer_is_preorder_from_title)

    # Drop rows without usable price or URL
    before = len(df)
    df = df.dropna(subset=["price_usd", "product_url"])
    after = len(df)
    print(f"🧹 Dropped {before - after} rows with missing price/url")

    # Final column order — aligned with other cleaners
    cleaned = df[
        [
            "source",                # 'xbox'
            "title",                 # game title
            "platform",              # Xbox
            "storefront",            # Microsoft Store
            "is_preorder",           # True/False
            "price_eur",             # normalized EUR
            "price_usd",             # native USD
            "original_price_eur",    # same as price_eur here
            "discount_pct",          # 0.0 for now
            "product_url",           # link

            # Xbox-specific extras (nice to keep)
            "category",
            "scraped_at_utc",
        ]
    ].copy()

    # Ensure output dir (NOTE: data/cleaned/)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"✅ Saved cleaned Xbox data to: {OUTPUT_PATH}")
    print(f"✅ Final shape: {cleaned.shape}")
    print("\n🔎 Preview:")
    print(cleaned.head())


if __name__ == "__main__":
    main()
