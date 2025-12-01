# Dataset Overview & Analysis

## Cleaned Datasets Summary

### 1. **Steam** (`cleaned_steam.csv`)
- **Rows:** 3,533 games
- **Columns:** 12
  - `source`, `title`, `platform`, `storefront`, `is_preorder`
  - `price_eur`, `price_usd`, `original_price_eur`, `discount_pct`
  - `product_url`, `category`, `release_date`
- **Platforms:** PC (all Steam games)
- **Storefront:** Steam
- **Price Range:** €0.00 - varies
- **Categories:** top_sellers, specials, trending
- **Key Insight:** Large dataset with diverse pricing and discount information

---

### 2. **Epic Games Store** (`cleaned_epicgames.csv`)
- **Rows:** 901 games
- **Columns:** 5 ⚠️ **DIFFERENT SCHEMA**
  - `store`, `title`, `platform`, `price`, `release_date`
- **Platforms:** PC (all Epic games)
- **Note:** Missing critical fields like:
  - `storefront` (assumed Epic Games Store)
  - `is_preorder`, `discount_pct`, `original_price_eur`
  - `product_url` (not included)
- **Action Required:** Schema needs normalization to match other sources

---

### 3. **Instant Gaming** (`cleaned_instantgaming.csv`)
- **Rows:** 1,000 games
- **Columns:** 10
  - `source`, `title`, `platform`, `storefront`, `is_preorder`
  - `price_eur`, `price_usd`, `original_price_eur`, `discount_pct`, `product_url`
- **Platforms:** PC, Xbox, PlayStation, Nintendo Switch, Unknown
- **Storefronts:** Steam, EA App, Microsoft Store, PlayStation Store, etc.
- **Price Currency:** EUR
- **Discount Info:** Present (calculated from original vs current price)
- **Sample Prices:** €55.49 - €80.42 range observed

---

### 4. **Loaded/CDKeys** (`cleaned_loaded.csv`)
- **Rows:** 132 games
- **Columns:** 12
  - `source`, `title`, `platform`, `storefront`, `is_preorder`
  - `price_eur`, `price_usd`, `original_price_eur`, `discount_pct`
  - `product_url`, `category`, `scraped_at_utc`
- **Platforms:** PC, Xbox, PlayStation
- **Storefront:** Loaded/CDKeys
- **Price Currency:** EUR (converted from GBP)
- **Note:** Smallest dataset, limited game coverage
- **Timestamps:** Available (2025-11-17)

---

### 5. **Xbox Store** (`cleaned_xbox.csv`)
- **Rows:** 1,502 games
- **Columns:** 12
  - `source`, `title`, `platform`, `storefront`, `is_preorder`
  - `price_eur`, `price_usd`, `original_price_eur`, `discount_pct`
  - `product_url`, `category`, `scraped_at_utc`
- **Platforms:** Xbox (Microsoft Store games)
- **Storefront:** Microsoft Store
- **Price Currency:** USD (converted to EUR)
- **Timestamps:** Available (2025-11-17)
- **Note:** Many games at 0.0 price (Game Pass items)

---

## Combined Dataset Statistics

### Total Coverage
| Metric | Value |
|--------|-------|
| **Total Games** | ~7,068 (if combined) |
| **Unique Sources** | 5 |
| **Unique Platforms** | 5 (PC, Xbox, PlayStation, Switch, Unknown) |
| **Unique Storefronts** | 6+ |
| **Price Range (EUR)** | €0.00 - €99.99+ |
| **Average Records/Source** | ~1,414 |

### Source Breakdown
```
Steam:              3,533 games (50.0%)
Xbox:               1,502 games (21.3%)
Instant Gaming:     1,000 games (14.2%)
Epic Games:           901 games (12.7%)
Loaded/CDKeys:        132 games (1.9%)
```

---

## Data Quality Issues & Recommendations

### ⚠️ Critical Issues

1. **Epic Games Schema Mismatch**
   - Missing: `storefront`, `is_preorder`, `discount_pct`, `original_price_eur`, `product_url`
   - **Action:** Normalize Epic dataset to match others or create separate processing
   - **Impact:** Cannot be directly merged with other datasets

2. **Missing Product URLs**
   - Epic Games: No `product_url` field
   - **Impact:** Cannot link back to store pages

3. **Free vs Paid Games**
   - Xbox: Many games at €0.00 (Game Pass items)
   - Steam: Some free-to-play games
   - **Impact:** May skew pricing analysis

### ⚠️ Data Consistency Notes

| Dataset | Price Currency | Discount Info | URLs | Timestamps |
|---------|----------------|---------------|------|-----------|
| Steam | EUR & USD | ✅ Yes | ✅ Yes | ❌ No |
| Epic | USD only | ❌ No | ❌ No | ❌ No |
| Instant Gaming | EUR & USD | ✅ Yes | ✅ Yes | ❌ No |
| Loaded | EUR & USD | ✅ Yes | ✅ Yes | ✅ Yes |
| Xbox | EUR & USD | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Recommendations for EDA

### 1. **Data Validation**
- [ ] Check for duplicates across sources
- [ ] Validate price ranges (outliers)
- [ ] Verify discount calculations
- [ ] Check for missing critical fields

### 2. **Normalization**
- [ ] Epic Games dataset needs schema alignment
- [ ] Standardize platform names across sources
- [ ] Unify storefront naming conventions

### 3. **Analysis Opportunities**
- ✅ Price comparison across sources
- ✅ Discount trends by platform
- ✅ Preorder vs released games analysis
- ✅ Best deals across all platforms
- ❌ Temporal trends (limited timestamp data)

### 4. **Data Enrichment**
- Consider adding genre/category information
- Track scraping timestamps consistently
- Include conversion rates used (EUR/USD/GBP)

---

## File Locations

```
data/
├── raw/
│   ├── steam.csv
│   ├── instantgaming.csv
│   ├── loaded.csv
│   └── xbox.csv
│
└── cleaned/
    ├── cleaned_steam.csv (3,533 rows)
    ├── cleaned_epicgames.csv (901 rows) ⚠️ Schema differs
    ├── cleaned_instantgaming.csv (1,000 rows)
    ├── cleaned_loaded.csv (132 rows)
    └── cleaned_xbox.csv (1,502 rows)
```

---

## Next Steps

1. **Fix Epic Games dataset** to match schema
2. **Run comprehensive EDA** on combined dataset
3. **Create price comparison dashboard**
4. **Identify best deals** across all platforms
5. **Analyze discount patterns** by source

