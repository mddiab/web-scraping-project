# 🚀 Quick Reference Guide

**Fast access to documentation and common commands.**

---

## 📚 Documentation Map

| Document | Purpose | When to Use |
|----------|---------|-----------|
| **[README.md](README.md)** | Overview & setup | Getting started |
| **[DATASET_OVERVIEW.md](DATASET_OVERVIEW.md)** | Dataset details & schema | Understanding data |
| **[EDA.md](EDA.md)** | Analysis findings | Key insights |
| **[ML_PIPELINE_FINAL_REPORT.md](ML_PIPELINE_FINAL_REPORT.md)** | Model details & validation | ML implementation |

---

## 🚀 Quick Commands

### Setup

```bash
# Clone repository
git clone https://github.com/mddiab/web-scraping-project.git
cd web-scraping-project

# Virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Dashboard

```bash
# Launch interactive dashboard
streamlit run dashboard.py

# Dashboard URL: http://localhost:8501
```

### Notebooks

```bash
# Run EDA notebook
jupyter notebook notebooks/EDA.ipynb

# Run ML Pipeline notebook
jupyter notebook notebooks/ML_Pipeline.ipynb
```

### Scrapers

```bash
# Individual scrapers
python scrapers/steam_scraper.py
python scrapers/epicgames_scraper.py
python scrapers/gog_scraper.py
python scrapers/instantgaming_scraper.py
python scrapers/loaded_scraper.py
python scrapers/xbox_scraper.py

# Data cleaning
python cleaners/steam_cleaner.py
python cleaners/epicgames_cleaner.py
```

---

## 📊 Quick Data Access

### Load All Datasets

```python
import pandas as pd

# Load individual datasets
steam = pd.read_csv('data/cleaned/cleaned_steam.csv')
epic = pd.read_csv('data/cleaned/cleaned_epicgames.csv')
instant = pd.read_csv('data/cleaned/cleaned_instantgaming.csv')
loaded = pd.read_csv('data/cleaned/cleaned_loaded.csv')
xbox = pd.read_csv('data/cleaned/cleaned_xbox.csv')

# Combine all
df = pd.concat([steam, epic, instant, loaded, xbox], ignore_index=True)
```

### Common Queries

```python
# Best deals
df[df['discount_pct'] > 50].sort_values('discount_pct', ascending=False).head(10)

# Average price by source
df.groupby('source')['price_eur'].mean()

# Platform distribution
df['platform'].value_counts()

# Free games
df[df['price_eur'] == 0.0].shape[0]

# Most expensive
df.nlargest(10, 'price_eur')[['title', 'source', 'price_eur']]
```

---

## 🤖 Quick ML Usage

### Load Deal Classifier

```python
import pickle
import numpy as np

model = pickle.load(open('models/best_model_deal_classifier_Gradient_Boosting.pkl', 'rb'))
scaler = pickle.load(open('models/scaler_deal_classifier.pkl', 'rb'))

# Prepare features (9 features)
X = np.array([[50, 59.99, 1, 1, 0, 0, 0, 0, 0]])  # discount%, price, etc.
X_scaled = scaler.transform(X)
prediction = model.predict(X_scaled)  # 'Good Deal' or 'Not a Deal'
```

### Load Price Regressor

```python
model = pickle.load(open('models/best_model_price_regression_clean.pkl', 'rb'))
scaler = pickle.load(open('models/scaler_price_regression_clean.pkl', 'rb'))

# 8 features (NO original_price)
X = np.array([[25, 1, 0, 0, 0, 0, 0, 0]])
X_scaled = scaler.transform(X)
predicted_price = model.predict(X_scaled)[0]
```

---

## 📁 Key File Locations

```
data/cleaned/
  ├── cleaned_steam.csv           (3,533 games)
  ├── cleaned_epicgames.csv       (901 games)
  ├── cleaned_instantgaming.csv   (1,000 games)
  ├── cleaned_loaded.csv          (132 games)
  └── cleaned_xbox.csv            (1,502 games)

models/
  ├── best_model_price_category_Random_Forest.pkl
  ├── best_model_deal_classifier_Gradient_Boosting.pkl
  ├── best_model_price_regression_clean.pkl
  └── *_scaler.pkl & label_encoders.pkl

notebooks/
  ├── EDA.ipynb
  └── ML_Pipeline.ipynb
```

---

## ⚡ Quick Stats

| Metric | Value |
|--------|-------|
| Total Games | 7,068 |
| Data Sources | 6 |
| Price Range | €0 - €249.99 |
| Best Discounts | Instant Gaming (66.9% avg) |
| Deal Classifier Accuracy | 100% |
| Price Regressor RMSE | €18.84 |

---

## 🔗 Links

- **GitHub:** https://github.com/mddiab/web-scraping-project
- **Steam:** https://store.steampowered.com
- **Epic Games:** https://www.epicgames.com/store
- **GOG:** https://www.gog.com
- **Xbox:** https://www.xbox.com/store
- **Instant Gaming:** https://www.instant-gaming.com
- **Loaded:** https://www.cdkeys.com

---

## ❓ Troubleshooting

### Streamlit Won't Start
```bash
# Clear Streamlit cache
streamlit run dashboard.py --logger.level=debug

# Or reset everything
streamlit cache clear
```

### Model Loading Error
```bash
# Check model files exist
ls models/best_model_*.pkl

# Reinstall dependencies
pip install --upgrade scikit-learn numpy pandas
```

### Data Loading Error
```bash
# Verify data files
ls data/cleaned/cleaned_*.csv

# Check file paths are correct (relative to working directory)
```

---

## 🎓 Learn More

- **[README.md](README.md)** - Full project overview
- **[DATASET_OVERVIEW.md](DATASET_OVERVIEW.md)** - Detailed dataset reference
- **[EDA.md](EDA.md)** - Analysis findings
- **[ML_PIPELINE_FINAL_REPORT.md](ML_PIPELINE_FINAL_REPORT.md)** - ML details

---

**Last Updated:** December 3, 2025
