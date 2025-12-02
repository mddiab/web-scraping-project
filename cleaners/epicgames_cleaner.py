import math
from pathlib import Path

import pandas as pd


# ---------------------------
# Paths (adjust if needed)
# ---------------------------
RAW_PATH = Path("data/raw/epicgames.csv")
CLEAN_PATH = Path("data/cleaned/cleaned_epicgames.csv")


# ---------------------------
# Helper functions
# ---------------------------

# Rough INR -> USD conversion rate
INR_TO_USD = 0.012  # tweak if you want a more up-to-date rate


def parse_price(x):
    """
    Take a price string like '₹3,249' and return (3249.0, '₹').
    Handle 'Free' as 0.0.
    If missing, returns (nan, None).
    """
    if pd.isna(x):
        return (math.nan, None)

    s = str(x).strip()
    if not s:
        return (math.nan, None)

    # Handle free games
    if s.lower().startswith("free"):
        return (0.0, None)

    # currency chars: everything that is NOT digit / comma / dot / space
    currency_chars = "".join(
        ch for ch in s if not ch.isdigit() and ch not in {",", ".", " "}
    )
    currency = currency_chars or None

    # numeric part: digits + dot
    number = "".join(ch for ch in s if ch.isdigit() or ch == ".")
    value = float(number) if number else math.nan
    return value, currency


def parse_percent(x):
    """
    Take a percent string like '92%' and return 92.0.
    If missing, returns nan.
    """
    if pd.isna(x):
        return math.nan

    s = str(x).strip().replace("%", "")
    return float(s) if s else math.nan


def convert_to_usd(value, currency):
    """
    Convert numeric price + currency to USD.
    For this dataset, prices are in INR (₹), so we map to USD.
    If currency is unknown/None, we leave as-is.
    """
    if pd.isna(value):
        return math.nan

    if not currency:
        # Assume it's already in USD or no currency symbol
        return value

    # Handle INR (₹) explicitly
    if currency == "₹" or str(currency).upper() == "INR":
        return value * INR_TO_USD

    # Fallback: no conversion
    return value


def map_single_platform(raw: str) -> str | None:
    """
    Map a raw platform string to a normalized category:
    PC, PlayStation, Xbox, Nintendo Switch, Mac, Linux, Android, iOS, Other
    """
    if raw is None:
        return None

    s = str(raw).strip().lower()
    if not s or s in {"nan", "none"}:
        return None

    if any(k in s for k in ["windows", "win", "pc"]):
        return "PC"
    if "xbox" in s:
        return "Xbox"
    if any(k in s for k in ["playstation", "ps1", "ps2", "ps3", "ps4", "ps5", "ps vita"]):
        return "PlayStation"
    if "switch" in s or "nintendo" in s:
        return "Nintendo Switch"
    if "mac" in s or "macos" in s:
        return "Mac"
    if "linux" in s or "steamos" in s:
        return "Linux"
    if "android" in s:
        return "Android"
    if any(k in s for k in ["ios", "iphone", "ipad"]):
        return "iOS"

    return "Other"


def normalize_platform(value):
    """
    Handle multiple platforms like 'Windows, MacOS, Linux' by mapping each
    and joining unique normalized labels with ' / '.
    """
    if pd.isna(value):
        return "Other"

    text = str(value)
    # Treat commas and slashes as separators
    parts = [p.strip() for p in text.replace("/", ",").split(",") if p.strip()]
    mapped = []
    for p in parts:
        m = map_single_platform(p)
        if m and m not in mapped:
            mapped.append(m)

    if not mapped:
        return "Other"
    return " / ".join(mapped)


def clean_epic_games(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Epic Games Store dataset.
    """

    df = df_raw.copy()

    # --- Price & currency ---
    price_tuples = df["price of game"].apply(parse_price)
    df["price_numeric"], df["currency"] = zip(*price_tuples)

    # Convert to USD
    df["price_usd"] = [
        convert_to_usd(v, c) for v, c in zip(df["price_numeric"], df["currency"])
    ]
    # Round to 2 decimal places
    df["price_usd"] = df["price_usd"].round(2)

    # --- Release date to proper datetime / date ---
    # Your file uses MM/DD/YY like 09/03/20
    df["release_date_parsed"] = pd.to_datetime(
        df["date release"], errors="coerce", format="%m/%d/%y"
    )
    # Save as ISO string so it shows clearly in CSV
    df["release_date_str"] = df["release_date_parsed"].dt.strftime("%Y-%m-%d")

    # --- Critics recommend to numeric percent (kept for later use if needed) ---
    df["critics_recommend_percent"] = df["Critics Recommend"].apply(parse_percent)

    # --- Normalize platform labels ---
    df["platform_normalized"] = df["platform"].apply(normalize_platform)

    # --- Build a cleaned dataframe with unified columns ---
    df_clean = pd.DataFrame(
        {
            "store": "epic_games_store",  # constant
            "title": df["name"].astype(str).str.strip(),
            "platform": df["platform_normalized"],
            # final price column is now in USD (rounded to 2 decimals)
            "price": df["price_usd"],
            "release_date": df["release_date_str"],
        }
    )

    # Optional: drop rows with completely missing title
    df_clean = df_clean.dropna(subset=["title"]).reset_index(drop=True)

    return df_clean


# ---------------------------
# Main
# ---------------------------
def main():
    print("=======================================")
    print("🎮  Epic Games CLEANER STARTED")
    print("=======================================")

    print(f"📥 Loading raw data from: {RAW_PATH}")
    df_raw = pd.read_csv(RAW_PATH)
    print(f"   ➜ Raw shape: {df_raw.shape}")

    df_clean = clean_epic_games(df_raw)
    print(f"✅ Cleaned shape: {df_clean.shape}")

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(CLEAN_PATH, index=False, encoding="utf-8")
    print(f"💾 Saved cleaned data to: {CLEAN_PATH}")
    print("✅ Done.")


if __name__ == "__main__":
    main()
