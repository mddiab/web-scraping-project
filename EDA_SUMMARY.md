# EDA v2 — Executive Summary (Canonical)

This file contains the canonical executive summary produced by the rebuilt EDA v2 (analysis snapshot: December 3, 2025). All project documentation and the Streamlit dashboard reference these numbers and findings.

## Dataset Overview
- Total games (combined): 7,058
- Complete dataset (excl. Epic Games): 4,372
- Epic Games (analyzed separately): 899
- Primary sources analyzed: Steam, Instant Gaming, Loaded/CDKeys, Xbox, Epic Games

## Key Analysis Flags
- `INCLUDE_EPIC_DISCOUNT = False`  — Epic discount data is missing/normalized (all zeros), so discount comparisons exclude Epic.
- `INCLUDE_EPIC_PRICING = True`    — Epic pricing values are used where available (pricing is valid).

## Top Findings
- Instant Gaming consistently offers the deepest discounts (best source for budget-conscious buyers).
- Steam shows selective but meaningful discounts (seasonal sales pattern).
- Xbox & Loaded maintain MSRP (discounts ~0%; many Game Pass items appear as €0).
- Game overlap across sources creates measurable savings opportunities (same title price variance can be €30+ on some items).
- Market composition: ~73% of games are under €20 (budget/mid-range dominated).

## Dataset Health Summary
- Price fields: largely complete (usable for ML and analytics)
- Discount fields: complete for all sources except Epic (normalized to 0)
- Release dates & timestamps: partially missing; temporal analyses are limited

## Actionable Recommendations
- Exclude Epic discounts from cross-source discount comparisons; include Epic pricing for price-level insights only.
- Use `df_complete` (excl. Epic) for ML training to avoid noisy/placeholder discount values.
- Prioritize Instant Gaming + Steam when surfacing recommended purchase sources in the dashboard.

## Next Steps
1. Ensure `README.md` and `DATASET_OVERVIEW.md` reference EDA v2 as canonical (done).
2. If you want exact per-source counts re-derived, run the `notebooks/EDA.ipynb` cells for a fresh snapshot and commit outputs.

---
**Reference:** `notebooks/EDA.ipynb` (rebuilt EDA v2)
