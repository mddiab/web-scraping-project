# Exploratory Data Analysis (EDA) — Canonical

This single-file EDA consolidates the project's exploratory analysis, data-quality findings, dataset counts, and actionable recommendations. It is the canonical EDA for the repository (derived from `notebooks/EDA.ipynb`).

## Executive Summary
- **Total games (combined):** 7,058
- **Complete dataset (excl. Epic):** ~4,372
- **Epic Games (separate):** ~899 (discounts missing / normalized)
- **Primary sources:** Steam, Instant Gaming, Loaded/CDKeys, Xbox, Epic Games, GOG

## Key Analysis Flags
- `INCLUDE_EPIC_DISCOUNT = False` → Epic discount_pct is unreliable (normalized 0.0) and excluded from cross-source discount comparisons and discount-based ML features.
- `INCLUDE_EPIC_PRICING = True` → Epic pricing values are used for price-level comparisons only.

## Data Ingestion & Normalization
- Raw scrapers: `scrapers/<store>_scraper.py` write raw CSVs to `data/raw/`.
- Cleaners: `cleaners/<store>_cleaner.py` normalize each store to a canonical schema and write to `data/cleaned/cleaned_<store>.csv`.
- Canonical schema (examples): `source, title, platform, storefront, is_preorder, price_usd, price_eur, original_price_eur, discount_pct, product_url, category, release_date, scraped_at_utc`.
- Currency normalization applied (e.g., Epic USD → EUR via multiplier).

## Data Quality Findings
- Epic Games discount data missing: all `discount_pct == 0.0` after normalization → flagged as placeholder.
- Release dates and timestamps are partially missing (limits temporal analyses).
- Some category/platform values are missing (notably in Xbox data).
- Small number of duplicate rows (title + source) were detected.

## Analytical Steps Performed
1. Load & normalize all cleaned datasets into `df_combined`.
2. Data quality assessment (missing values, duplicates, schema issues).
3. Split datasets: `df_complete` (excl. Epic) and `df_epic` (Epic-only). Create clean subsets with valid prices.
4. Price tiering: Free, Budget (<€5), Mid (€5–20), Premium (€20–50), Ultra (>€50).
5. Discount strategy comparison per source and cross-source overlap analysis to find savings opportunities.
6. Executive summary and recommendations based on observed distributions and sample analyses.

## Key Findings
- **Discount strategies:** Instant Gaming shows the largest average discounts (reseller model). Steam shows selective, seasonal discounts. Loaded and Xbox generally maintain MSRP (near 0% discounts).
- **Market composition:** ~73% of games under €20 (budget/mid dominated).
- **Overlap & savings:** Many titles appear across multiple sources; price variance can yield tens of euros in savings on the same title.
- **ML implications:** Epic's placeholder discounts would bias models if included; exclude Epic discounts from training and use `df_complete` for ML features driven by discount behavior.

## Visuals & Tables (notebook)
- The notebook contains: price histograms, boxplots by source, stacked price-tier by source bars, discount heatmaps, and top-overlap variance tables. See `notebooks/EDA.ipynb` for visuals.

## Recommended Next Steps
- Add `scraped_at_utc` and a `run_id` to scraper outputs for provenance and freshness checks.
- Persist raw HTML/JSON snapshots for debugging scraper regressions.
- Add unit/smoke tests for cleaners to assert schema stability.
- Re-run the EDA notebook when cleaned CSVs change and regenerate any exported figures/tables used in reports.
- Validate ML models for leakage and class imbalance; add explainability (SHAP) before productionizing.

## How to re-run the notebook (quick)
```
& .venv\Scripts\Activate.ps1
jupyter nbconvert --to notebook --inplace --execute notebooks\EDA.ipynb
```

## Files referenced
- `notebooks/EDA.ipynb`  — source notebook for EDA
- `data/raw/`            — raw scraper outputs
- `data/cleaned/`        — normalized CSVs used for analysis
- `EDA.md` (this file)   — canonical EDA
