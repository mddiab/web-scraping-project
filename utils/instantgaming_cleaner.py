"""
instantgaming_cleaner.py

Clean the raw Instant Gaming CSV into a modeling-friendly format,
similar in structure to the cleaned Loaded/CDKeys CSV.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------
# Paths
# ---------------------------

RAW_CANDIDATES = [
    Path("data/raw/instantgaming.csv"),
    Path("instantgaming.csv"),
    Path("/mnt/data/instantgaming.csv"),  # for local testing
]

OUTPUT_DIR = Path("data/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_instantgaming.csv"

# ---------------------------
# Currency
# ---------------------------

# Approx EUR → USD rate. Adjust if you want a more up-to-date value.
EUR_TO_USD_RATE = 1.08


# ---------------------------
# Parsing helpers
# ---------------------------

def parse_price_eur(text):
    """Convert a price string like '55.49 €' or '55,49 €' to float euros."""
    if pd.isna(text):
        return np.nan
    s = str(text).replace("\xa0", " ").strip()
    # keep digits, comma, dot, minus
    s_clean = re.sub(r"[^\d,.\-]", "", s)

    if not s_clean:
        return np.nan

    # If we have exactly one comma and no dot, treat comma as decimal
    if s_clean.count(",") == 1 and s_clean.count(".") == 0:
        s_clean = s_clean.replace(",", ".")

    # If both comma and dot appear, assume dot is decimal and commas are thousands
    if s_clean.count(".") == 1 and s_clean.count(",") >= 1:
        s_clean = s_clean.replace(",", "")

    try:
        return float(s_clean)
    except ValueError:
        return np.nan


def parse_discount_pct(text):
    """
    Convert strings like '-31%' or '31%' to a positive float (31.0).
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


def extract_platform_and_storefront(title: str):
    """
    Try to infer platform (PC/PS/Xbox/Switch/Unknown)
    and storefront (Steam, EA App, Microsoft Store, etc.)
    from the game title.
    """
    s = str(title)

    # Storefront: last (...) at end of title
    storefront = None
    m = re.search(r"\(([^)]+)\)\s*$", s)
    if m:
        storefront = m.group(1).strip()

    # Platform via simple keyword checks
    platform = None
    patterns = {
        "PC": ["- PC", " PC ", "PC -"],
        "PS5": ["PS5", "PlayStation 5"],
        "PS4": ["PS4", "PlayStation 4"],
        "Xbox One/Series": ["Xbox One/Series X|S", "Xbox Series X|S", "Xbox One"],
        "Xbox 360": ["Xbox 360"],
        "Switch": ["Nintendo Switch", "Switch"],
    }

    for plat, needles in patterns.items():
        for n in needles:
            if n in s:
                platform = plat
                break
        if platform:
            break

    # Fallbacks
    if platform is None:
        if "PC" in s:
            platform = "PC"
        else:
            platform = "Unknown"

    return platform, storefront


# ---------------------------
# Main cleaning logic
# ---------------------------

def load_raw_csv():
    for p in RAW_CANDIDATES:
        if p.exists():
            print(f"📥 Loading raw Instant Gaming data from: {p}")
            return pd.read_csv(p)
    raise FileNotFoundError(
        "instantgaming.csv not found in any of: "
        + ", ".join(str(p) for p in RAW_CANDIDATES)
    )


def main():
    df = load_raw_csv()
    print(f"🔹 Raw shape: {df.shape}")

    # Basic sanity: keep only expected columns if they exist
    expected_cols = ["source", "title", "discount", "price_raw", "preorder_info", "product_url"]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in raw CSV: {missing}")

    # Drop exact duplicate product URLs
    before = len(df)
    df = df.drop_duplicates(subset=["product_url"]).copy()
    after = len(df)
    print(f"🧹 Removed {before - after} duplicate rows based on product_url")

    # Parse price and discount
    df["price_eur"] = df["price_raw"].apply(parse_price_eur)
    df["discount_pct"] = df["discount"].apply(parse_discount_pct)

    # Estimate original price from discount
    df["original_price_eur"] = df.apply(
        lambda row: compute_original_price(row["price_eur"], row["discount_pct"]),
        axis=1,
    )

    # NEW: price in USD
    df["price_usd"] = (df["price_eur"] * EUR_TO_USD_RATE).round(2)

    # Pre-order flag
    df["is_preorder"] = df["preorder_info"].str.contains(
        "pre-order", case=False, na=False
    )

    # Platform + storefront
    plat_store = df["title"].apply(extract_platform_and_storefront)
    df["platform"] = plat_store.apply(lambda x: x[0])
    df["storefront"] = plat_store.apply(lambda x: x[1])

    # Drop rows without a valid price or URL
    before = len(df)
    df = df.dropna(subset=["price_eur", "product_url"])
    after = len(df)
    print(f"🧹 Dropped {before - after} rows with missing price/url")

    # Final column order (similar style to Loaded cleaned CSV)
    cleaned = df[
        [
            "source",                # 'instantgaming'
            "title",                 # game title
            "platform",              # PC / PS / Xbox / Switch / Unknown
            "storefront",            # Steam, EA App, Microsoft Store, ...
            "is_preorder",           # True/False
            "price_eur",             # current discounted price (EUR)
            "price_usd",             # current discounted price (USD)
            "original_price_eur",    # estimated original price (EUR)
            "discount_pct",          # numeric discount percentage
            "product_url",           # link to game page
        ]
    ].copy()

    # Make sure output folder exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"✅ Saved cleaned Instant Gaming data to: {OUTPUT_PATH}")
    print(f"✅ Final shape: {cleaned.shape}")
    print("\n🔎 Preview:")
    print(cleaned.head())


if __name__ == "__main__":
    main()
