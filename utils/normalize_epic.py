"""
Normalize Epic Games dataset to match schema of other sources
"""
import pandas as pd
from pathlib import Path

# Load Epic Games data
epic_path = Path("data/cleaned/cleaned_epicgames.csv")
df_epic = pd.read_csv(epic_path)

print(f"Original Epic Games shape: {df_epic.shape}")
print(f"Original columns: {list(df_epic.columns)}")

# Normalize to match other datasets
df_epic_normalized = df_epic.copy()

# Rename columns
df_epic_normalized = df_epic_normalized.rename(columns={
    'store': 'source',
    'price': 'price_usd'
})

# Add missing columns with standardized values
df_epic_normalized['platform'] = df_epic_normalized['platform'].fillna('PC')  # All Epic games are PC
df_epic_normalized['storefront'] = 'Epic Games Store'
df_epic_normalized['is_preorder'] = False  # Assume all are released
df_epic_normalized['source'] = 'epic_games'  # Standardize source name

# Convert USD to EUR (approximate 1.08 rate)
USD_TO_EUR = 0.926
df_epic_normalized['price_eur'] = (df_epic_normalized['price_usd'] * USD_TO_EUR).round(2)

# Add missing financial columns
df_epic_normalized['original_price_eur'] = df_epic_normalized['price_eur']  # No discount info
df_epic_normalized['discount_pct'] = 0.0  # No discount data available

# Add missing metadata columns
df_epic_normalized['product_url'] = ''  # Not available in Epic dataset
df_epic_normalized['category'] = 'all_games'  # Default category

# Reorder columns to match other datasets
columns_order = [
    'source', 'title', 'platform', 'storefront', 'is_preorder',
    'price_eur', 'price_usd', 'original_price_eur', 'discount_pct',
    'product_url', 'category', 'release_date'
]

df_epic_normalized = df_epic_normalized[columns_order]

print(f"\nNormalized Epic Games shape: {df_epic_normalized.shape}")
print(f"Normalized columns: {list(df_epic_normalized.columns)}")

# Save normalized version
output_path = Path("data/cleaned/cleaned_epicgames.csv")
df_epic_normalized.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n✅ Epic Games dataset normalized and saved!")
print(f"📝 Preview:")
print(df_epic_normalized.head(10))

print(f"\n📊 Dataset Info:")
print(f"  • Total games: {len(df_epic_normalized)}")
print(f"  • Price range (USD): ${df_epic_normalized['price_usd'].min():.2f} - ${df_epic_normalized['price_usd'].max():.2f}")
print(f"  • Price range (EUR): €{df_epic_normalized['price_eur'].min():.2f} - €{df_epic_normalized['price_eur'].max():.2f}")
print(f"  • Free games: {len(df_epic_normalized[df_epic_normalized['price_usd'] == 0.0])}")
