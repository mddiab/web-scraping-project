# 📊 Dataset Overview & Complete Reference

**Single authoritative source for all dataset information, schema details, and data quality metrics.**

---

## 📈 Combined Coverage

| Metric | Value |
|--------|-------|
| **Total Games** | 7,058 |
| **Data Sources** | 6 major gaming retailers |
| **Unique Platforms** | 5 (PC, Xbox, PlayStation, Switch, Unknown) |
| **Unique Storefronts** | 6+ |
| **Price Range** | €0.00 - €249.99 |
| **Data Points** | 84,816+ |

### Source Distribution
```
Steam:            3,531 games
Xbox:             1,502 games
Instant Gaming:   998 games
Epic Games:         899 games (analyzed separately; discount data normalized)
Loaded/CDKeys:      128 games
```

---

## 📝 Unified Data Schema

All datasets share this **standard schema** (12 columns):

```
source              # steam, epic_games, instantgaming, loaded, xbox
title               # Game title
platform            # PC, Xbox, PlayStation, Switch, Unknown
storefront          # Steam, Epic Games Store, Microsoft Store, etc.
is_preorder         # Boolean
price_eur           # Current price in EUR
price_usd           # Current price in USD
original_price_eur  # Price before discount
discount_pct        # Discount percentage
product_url         # Link to game page
category            # top_sellers, all_games, trending, etc.
release_date        # Release date (format varies)
```

---

## 🗂️ Cleaned Datasets Details

### 1. **Steam** (`cleaned_steam.csv`)
- **Rows:** 3,533 games
- **Platforms:** PC only
- **Storefront:** Steam
- **Price Range:** €0.00 - €60+
- **Discounts:** Yes (avg 10-15%)
- **Categories:** top_sellers, specials, trending
- **Schema:** ✅ Standard (12 columns)

### 2. **Epic Games Store** (`cleaned_epicgames.csv`)
- **Rows:** 901 games
- **Platforms:** PC only
- **Storefront:** Epic Games Store
- **Price Range:** €0.00 - €40+
- **Discounts:** Limited (store-wide sales only)
- **Schema:** ✅ Standard (12 columns, normalized)

### 3. **Instant Gaming** (`cleaned_instantgaming.csv`)
- **Rows:** 1,000 games
- **Platforms:** PC, Xbox, PlayStation, Nintendo Switch, Unknown
- **Storefronts:** Steam, EA App, Microsoft Store, PlayStation Store, etc.
- **Price Range:** €10 - €80+
- **Discounts:** Yes (avg 20-30%, highest across sources)
- **Schema:** ✅ Standard (12 columns)

### 4. **Loaded/CDKeys** (`cleaned_loaded.csv`)
- **Rows:** 132 games (smallest dataset)
- **Platforms:** PC, Xbox, PlayStation
- **Storefront:** Loaded/CDKeys
- **Price Range:** Variable premium pricing
- **Discounts:** None (0% average)
- **Schema:** ✅ Standard (12 columns)
- **Note:** Limited inventory, premium reseller

### 5. **Xbox Store** (`cleaned_xbox.csv`)
- **Rows:** 1,502 games
- **Platforms:** Xbox/Microsoft Store games
- **Storefront:** Microsoft Store
- **Price Range:** €0.00 - €99.99 (many Game Pass items at €0)
- **Discounts:** Minimal (0% average)
- **Schema:** ✅ Standard (12 columns)

### 6. **GOG** (`cleaned_gog.csv`)
- **Rows:** Varies
- **Platforms:** PC (DRM-free)
- **Storefront:** GOG
- **Schema:** ✅ Standard (12 columns)

---

## 📊 Price Statistics

### By Source (EUR)
| Source | Min | Max | Average | Median |
|--------|-----|-----|---------|--------|
| Steam | €0.00 | €60+ | €25 | €10-15 |
| Epic Games | €0.00 | €40+ | €20 | €10-15 |
| Instant Gaming | €10 | €80+ | €15 | €12 |
| Loaded | Varies | Premium | €40+ | - |
| Xbox | €0.00 | €99+ | €8 | €0-5 |

### Discount Coverage
- **Games with discounts:** ~2,500+ (35%+)
- **Max discount observed:** 80%+
- **Average discount:** 15-25%
- **Best source:** Instant Gaming (avg 20-30%)
- **No discounts:** Loaded, Xbox (mostly)

### Platform Distribution
```
PC              4,534+ games (64%)
Xbox            1,502+ games (21%)
PlayStation     Multiple games
Nintendo Switch Multiple games
Multi-platform  Across sources
```

---

## ⚠️ Data Quality & Issues

### Quality Checklist
| Issue | Status | Impact |
|-------|--------|--------|
| Schema normalized | ✅ Complete | All sources unified |
| Missing URLs | ⚠️ Epic Games | Cannot link back to Epic store |
| Free vs paid | ✅ Handled | Xbox has many €0 Game Pass items |
| Timestamps | ⚠️ Partial | Only Loaded & Xbox have timestamps |
| Discount info | ✅ Available | Present in all except Loaded |
| Price currency | ✅ Unified | All standardized to EUR/USD |

### Data Consistency Notes
| Dataset | Price Currency | Discount Info | URLs | Timestamps |
|---------|----------------|---------------|------|-----------|
| Steam | EUR & USD | ✅ Yes | ✅ Yes | ❌ No |
| Epic | EUR & USD | ✅ Yes | ❌ No | ❌ No |
| Instant Gaming | EUR & USD | ✅ Yes | ✅ Yes | ❌ No |
| Loaded | EUR & USD | ✅ Yes | ✅ Yes | ✅ Yes |
| Xbox | EUR & USD | ✅ Yes | ✅ Yes | ✅ Yes |

---

## 📂 File Locations

```
data/
├── raw/                              # Original scraped data
│   ├── steam.csv
│   ├── epicgames.csv
│   ├── instantgaming.csv
│   ├── loaded.csv
│   └── xbox.csv
│
└── cleaned/                          # Normalized datasets
    ├── cleaned_steam.csv             (3,533 rows)
    ├── cleaned_epicgames.csv         (901 rows)
    ├── cleaned_instantgaming.csv     (1,000 rows)
    ├── cleaned_loaded.csv            (132 rows)
    └── cleaned_xbox.csv              (1,502 rows)
```

---

## 🔄 Common Analysis Queries

### Find Best Deals
```python
df_combined[df_combined['discount_pct'] > 50].nlargest(10, 'discount_pct')
```

### Compare Sources
```python
df_combined.groupby('source')['price_eur'].agg(['mean', 'min', 'max', 'count'])
```

### Platform Breakdown
```python
df_combined['platform'].value_counts()
```

### Free Games
```python
free_games = df_combined[df_combined['price_eur'] == 0.0]
len(free_games)  # Count of free games
```

### Most Expensive
```python
df_combined.nlargest(10, 'price_eur')[['title', 'source', 'price_eur']]
```

### Price by Platform
```python
df_combined.groupby('platform')['price_eur'].describe()
```

---

## 🚀 Getting Started

### Load All Cleaned Data
```python
import pandas as pd

# Load individual datasets
steam = pd.read_csv('data/cleaned/cleaned_steam.csv')
epic = pd.read_csv('data/cleaned/cleaned_epicgames.csv')
instant = pd.read_csv('data/cleaned/cleaned_instantgaming.csv')
loaded = pd.read_csv('data/cleaned/cleaned_loaded.csv')
xbox = pd.read_csv('data/cleaned/cleaned_xbox.csv')

# Combine all
df_combined = pd.concat([steam, epic, instant, loaded, xbox], ignore_index=True)
print(f"Total games: {len(df_combined)}")
```

---

## 📊 Key Insights

### Pricing
- **Average Game Price:** €20-40 across sources
- **Budget games:** 73% of games under €20
- **Most affordable:** Instant Gaming (avg €15)
- **Most expensive:** Loaded/Premium titles (€40-99)
- **Free games:** ~500+ (Game Pass + F2P)

### Discounts
- **Instant Gaming:** 66.9% avg (aggressive reseller model)
- **Steam:** 32.2% avg (strategic seasonal sales)
- **Epic/Xbox:** 0-20% (limited or no discounts)
- **Only 42.3% of games have any discount**

### Business Models
1. **Reseller** (Instant Gaming) → Max profit via volume + deep cuts
2. **Official Store** (Steam/Epic) → Curated sales + MSRP
3. **Platform Exclusive** (Xbox/Loaded) → Fixed pricing

---

## 📖 Related Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[EDA_STATUS.md](EDA_STATUS.md)** - Exploratory data analysis findings
 - **[EDA.md](EDA.md)** - Exploratory data analysis findings
- **[ML_PIPELINE_FINAL_REPORT.md](ML_PIPELINE_FINAL_REPORT.md)** - ML model details
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - CLI commands and quick links

---

**Last Updated:** December 3, 2025  
**Status:** ✅ Complete & Ready for Analysis
