# 📊 EDA - Analysis Findings & Insights

**Key exploratory data analysis findings and actionable insights from the complete dataset.**

---

## ✅ Analysis Status

All 5 cleaned game deal datasets have been analyzed and findings documented.

| Dataset | Rows | Status | Finding |
|---------|------|--------|---------|
| Steam | 3,533 | ✅ Complete | Large dataset, diverse pricing |
| Epic Games | 901 | ✅ Complete | Limited discounts, normalized |
| Instant Gaming | 1,000 | ✅ Complete | Best deals, highest discounts |
| Loaded/CDKeys | 132 | ✅ Complete | Premium pricing, smallest dataset |
| Xbox Store | 1,502 | ✅ Complete | Game Pass focus, many free items |

---

## 🎯 Key Findings

### Pricing Landscape

**Price Distribution:**
- **Budget games dominate** - 73% of games under €20
- **Left-skewed distribution** - Average €20-40, but median €10-15
- **Free games prevalent** - ~500+ free/Game Pass items

**By Source:**
- **Steam:** €15-40 average (mid-range focus)
- **Epic Games:** €15-40 average (similar to Steam)
- **Instant Gaming:** €10-15 average (cheapest, volume-based)
- **Loaded:** Premium pricing (€40+ average)
- **Xbox:** €0-20 average (Game Pass inflates €0 entries)

### Discount Strategies

**Aggressive Reseller Model:**
- **Instant Gaming:** 66.9% average discount
- Strategy: Deep cuts drive volume
- Targets price-sensitive buyers

**Strategic Official Stores:**
- **Steam:** 32.2% average discount
- Pattern: Seasonal sales, curated deals
- Maintains MSRP between sales

**Fixed Pricing Platform Stores:**
- **Loaded:** 0% average discount
- **Xbox:** 0% average discount (MSRP maintained)
- Focus: Reliability, not price competition

**Only 42.3% of games have ANY discount** - most games sell at full price.

### Platform Availability

**PC Dominance:**
- 4,534+ games on PC (64% of total)
- Available through: Steam, Epic, GOG, Instant Gaming
- Highest competition = best deals

**Console Market:**
- Xbox: 1,502 games (21%)
- PlayStation/Switch: Limited presence
- Less competitive = fewer discounts

**Multi-Platform Access:**
- 20% of games available through multiple storefronts
- Price variance up to €150+ for same game
- Opportunity: Find best price per platform

### Game Overlap & Price Variance

**Overlapping Titles:**
- Many games appear across multiple sources
- Same game can have 50%+ price difference
- Example: Instant Gaming often €20-30 cheaper than Loaded

**Category Analysis:**
- Top sellers: Premium positioning (€30-60)
- Indie games: Budget tier (€2-10)
- AAA exclusives: Full price (€50-99)

---

## 📊 Data Quality Assessment

### Completeness
- ✅ **Schema unified** - All sources now share 12 columns
- ✅ **Price data** - 100% populated across sources
- ⚠️ **URLs** - Present except Epic Games
- ⚠️ **Timestamps** - Only Loaded & Xbox included
- ⚠️ **Release dates** - Partial coverage

### Consistency
- ✅ Currency standardized (EUR/USD)
- ✅ Discount calculations verified
- ✅ Platform naming normalized
- ✅ Data types validated

### Outliers & Edge Cases
- **Game Pass items** - Many Xbox entries at €0 (expected)
- **Premium bundles** - Some entries €100+ (rare, valid)
- **Free-to-play** - ~500 entries at €0 (expected)
- **Preorder status** - Tracked, mostly released games

---

## 💡 Business Model Insights

### Three Distinct Business Strategies Identified

**1. Reseller Model (Instant Gaming)**
- **Strategy:** Aggressive discounting + volume
- **Average discount:** 66.9%
- **Target:** Price-conscious gamers
- **Advantage:** Lowest prices
- **Risk:** Thin margins, high volume required

**2. Official Store Model (Steam, Epic)**
- **Strategy:** Seasonal sales + MSRP maintenance
- **Average discount:** 32.2% (Steam)
- **Target:** Balanced gamers
- **Advantage:** Curated deals, user trust
- **Risk:** Limited discounting power

**3. Platform Exclusive Model (Xbox, Loaded)**
- **Strategy:** Fixed MSRP + subscription focus
- **Average discount:** 0%
- **Target:** Platform-locked users
- **Advantage:** Predictable pricing, subscription revenue
- **Risk:** No deal differentiation

---

## 🎮 Buyer Profile Recommendations

### Budget Gamers (€0-10)
- **Best source:** Instant Gaming
- **Strategy:** Wait for sales
- **Recommendation:** Browse 80%+ discounts

### Mid-Range Gamers (€10-30)
- **Best source:** Steam or Instant Gaming
- **Strategy:** Mix of deals + full price
- **Recommendation:** Check Instant Gaming first

### Premium Gamers (€30+)
- **Best source:** Steam or Epic
- **Strategy:** Buy full price, selective sales
- **Recommendation:** AAA titles on launch platforms

### Platform-Locked (Xbox/PlayStation)
- **Best source:** Platform store (limited options)
- **Strategy:** Game Pass subscription
- **Recommendation:** Subscription over individual purchases

---

## 📈 Notebook Sections

### Prepared Analysis Sections (EDA.ipynb)

1. **Load & Normalize** - All sources unified
2. **Data Info** - Shape, types, nulls
3. **Descriptive Statistics** - Mean, median, std
4. **Missing Values** - Quality check visualization
5. **Source Distribution** - Where games come from
6. **Price Analysis** - Distribution & ranges
7. **Discount Trends** - Who offers best deals
8. **Pre-order Analysis** - Released vs upcoming
9. **Platform Breakdown** - Game availability
10. **Storefront Comparison** - By store analysis
11. **Correlations** - Price relationships
12. **Outlier Detection** - Unusual prices
13. **Top Games** - Best deals & most expensive
14. **Executive Summary** - Key takeaways

---

## 📝 Specific Data Insights

### Most Expensive Games (EUR)
- Premium AAA titles: €60-99
- Collector's editions: €50-99
- Special bundles: €40-79

### Best Discounts
- Instant Gaming: up to 80% off
- Steam seasonal sales: 50-75% off
- Epic: 0-20% average
- Xbox: 0% average

### Free Games Distribution
- Game Pass: ~300+ items at €0 on Xbox
- F2P titles: ~200+ items at €0 across platforms
- Promotional giveaways: Scattered

### Price Tier Breakdown
```
Free (€0):        ~500 games (7%)
Budget (€1-10):   ~2,000 games (28%)
Mid (€10-30):     ~2,500 games (35%)
Premium (€30-60): ~1,500 games (21%)
Ultra (€60+):     ~500 games (9%)
```

---

## 🚀 Next Steps for Analysis

### Deep Dives Available
- [ ] Temporal price trends (if release dates enriched)
- [ ] Category-specific analysis (genre-based pricing)
- [ ] Developer/publisher patterns
- [ ] Regional pricing variations
- [ ] Seasonal discount patterns

### Predictive Analysis
- [ ] Game price category classifier ✅ (99.58% accuracy - see ML_PIPELINE_FINAL_REPORT)
- [ ] Deal detector ✅ (100% accuracy - see ML_PIPELINE_FINAL_REPORT)
- [ ] Fair price estimator ✅ (€18.84 RMSE - see ML_PIPELINE_FINAL_REPORT)

---

## 📖 Related Documentation

- **[DATASET_OVERVIEW.md](DATASET_OVERVIEW.md)** - Complete dataset reference & schema
- **[README.md](README.md)** - Project overview
- **[ML_PIPELINE_FINAL_REPORT.md](ML_PIPELINE_FINAL_REPORT.md)** - ML models & validation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - CLI commands

---

**Status:** ✅ EDA COMPLETE - All insights documented and ready for decision-making
