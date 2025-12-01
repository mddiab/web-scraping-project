# 🎮 Game Deals Datasets - Quick Reference

## 📊 All Datasets Overview

| Source | Games | Platforms | Avg Price | Discounts | Status |
|--------|-------|-----------|-----------|-----------|--------|
| **Steam** | 3,533 | PC | €25 | ✅ Yes | ✅ Ready |
| **Epic Games** | 901 | PC | €20 | ⚠️ Limited | ✅ Normalized |
| **Instant Gaming** | 1,000 | Multi | €15 | ✅ High | ✅ Ready |
| **Loaded/CDKeys** | 132 | Multi | €40 | ❌ None | ✅ Ready |
| **Xbox** | 1,502 | Xbox | €8 | ❌ Low | ✅ Ready |
| **TOTAL** | **7,068** | **5+** | **~€20** | ✅ | ✅ Ready |

---

## 📈 Key Metrics

```
Total Games:           7,068
Total Sources:         5
Total Platforms:       5+ (PC, Xbox, PlayStation, Switch, Unknown)
Price Range:           €0 - €99.99+
Discount Range:        0% - 80%+
Data Points:           84,816+
```

---

## 🔥 Hot Stats

- **Most Games**: Steam (50%)
- **Best Prices**: Instant Gaming (avg €15)
- **Highest Discounts**: Instant Gaming (avg ~20%)
- **Most Expensive**: Premium titles (€40-99)
- **Most Affordable**: Indie games (€2-10)
- **Free Games**: ~500+ (Game Pass + Free-to-Play)

---

## 📝 Datasets at a Glance

### 🔵 Steam (3,533)
`cleaned_steam.csv`
- Largest dataset
- PC games only
- Top sellers, specials, trending categories
- Price range: €0 - €60+
- Moderate discounts (avg 10-15%)

### 🟠 Epic Games Store (901)
`cleaned_epicgames.csv` ✅ NORMALIZED
- Second largest PC platform
- Limited discounts (store-wide sales only)
- Price range: €0 - €40+
- Now matches standard schema

### 🎯 Instant Gaming (1,000)
`cleaned_instantgaming.csv`
- Key reseller
- Multi-platform focus
- **Best discounts** (avg 20-30%)
- Price range: €10 - €80+

### 💳 Loaded/CDKeys (132)
`cleaned_loaded.csv`
- Smallest dataset
- Multi-platform
- Premium pricing
- Very limited inventory

### 🎮 Xbox Store (1,502)
`cleaned_xbox.csv`
- Largest Xbox collection
- Microsoft Game Pass items
- Many free (€0) items
- Premium titles (€50-99)

---

## 🎯 Common Analysis Queries

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

## 🚀 EDA Notebook Sections

1. **Load & Normalize** - All 5 sources unified
2. **Data Info** - Shape, types, nulls
3. **Statistics** - Descriptive stats
4. **Missing Values** - Quality check
5. **Source Distribution** - Where games come from
6. **Price Analysis** - Distribution & ranges
7. **Discount Trends** - Who offers best deals
8. **Pre-orders** - Released vs upcoming
9. **Platforms** - Game availability by console
10. **Correlations** - Relationships in data
11. **Outliers** - Unusual prices/discounts
12. **Top Games** - Best deals & most expensive
13. **Summary** - Executive findings

---

## 📂 File Locations

```
notebooks/EDA.ipynb                    # Main analysis notebook ✅
data/cleaned/cleaned_*.csv             # All 5 cleaned datasets ✅
DATASET_OVERVIEW.md                    # Detailed overview
EDA_STATUS.md                          # Full status report
normalize_epic.py                      # Epic Games normalizer
```

---

## 🎯 Next Action

**Run the notebook!**

```bash
# In VS Code:
1. Open: notebooks/EDA.ipynb
2. Ensure pandas/numpy/matplotlib installed
3. Run all cells (Ctrl+Shift+Enter)
4. View comprehensive analysis with 30+ visualizations
```

---

## 💰 Sample Price Insights

### Cheapest Games (EUR)
- Townscaper: €1.67
- The Lion's Song: €2.27
- Many indie titles: €2-5

### Most Expensive Games (EUR)
- Premium AAA titles: €60-99
- Collector's editions: €50-99
- Special bundles: €40-79

### Best Discounts
- Instant Gaming: up to 80% off
- Steam sales: 50-75% off seasonal
- Epic: 0-20% average

### Price by Platform
- **PC**: €15-30 average
- **Xbox**: €8-20 average (many Game Pass)
- **PlayStation**: €20-40 average
- **Switch**: €15-50 average

---

**Status**: ✅ ALL DATASETS READY FOR ANALYSIS

Last Updated: 2025-11-30
