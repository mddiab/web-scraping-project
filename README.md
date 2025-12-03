# 🎮 Game Deals Tracker
**Advanced Web Scraping & ML Analysis Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Overview

An advanced web scraping and machine learning platform that aggregates game deals from **6 major gaming platforms**, analyzes pricing trends, and uses **AI models** to identify the best deals. Features a professional **Streamlit dashboard** with real-time analytics and ML-powered deal predictions.

### 🎯 Key Features

- 🕷️ **Multi-Platform Scraping**: Automated data collection from Steam, Epic Games, GOG, Xbox, Instant Gaming, and Loaded
- 🤖 **AI Deal Predictor**: Machine learning models classify deals and predict fair market prices
- 📊 **Interactive Dashboard**: Beautiful Streamlit UI with real-time visualizations
- 💾 **Comprehensive Dataset**: 7,000+ games with pricing, discounts, and metadata
- 🎨 **Professional Design**: Modern neon-themed interface with glassmorphism effects
- 📈 **Advanced Analytics**: Price trends, discount patterns, and platform comparisons

---

## 🚀 Live Dashboard

Launch the interactive dashboard to explore game deals:

```bash
streamlit run dashboard.py
```

**Dashboard Features:**
- 🔍 Advanced filtering (price range, discount %, store selection)
- 🎯 AI Deal Predictor with confidence scores
- 📊 Interactive visualizations (price distributions, discount heatmaps, platform comparisons)
- 🎮 Game catalog with sortable data tables
- ⚡ Real-time performance metrics

---

## 🗂️ Project Structure

```
web-scraping-project/
│
├── 📂 data/
│   ├── raw/                          # Unprocessed scraped data
│   └── cleaned/                      # Processed & normalized CSVs
│       ├── cleaned_steam.csv         (3,533 games)
│       ├── cleaned_epicgames.csv     (901 games)
│       ├── cleaned_gog.csv           (GOG games)
│       ├── cleaned_instantgaming.csv (1,000 games)
│       ├── cleaned_loaded.csv        (132 games)
│       └── cleaned_xbox.csv          (1,502 games)
│
├── 📂 scrapers/
│   ├── steam_scraper.py              # Steam Store scraper
│   ├── epicgames_scraper.py          # Epic Games Store scraper
│   ├── gog_scraper.py                # GOG scraper
│   ├── instantgaming_scraper.py      # Instant Gaming scraper
│   ├── loaded_scraper.py             # Loaded/CDKeys scraper
│   └── xbox_scraper.py               # Xbox Store scraper
│
├── 📂 cleaners/
│   └── *_cleaner.py                  # Data cleaning scripts per platform
│
├── 📂 models/
│   ├── best_model_price_category_Random_Forest.pkl
│   ├── best_model_deal_classifier_Gradient_Boosting.pkl
│   ├── best_model_price_regression_clean.pkl
│   ├── label_encoders.pkl
│   ├── scaler_*.pkl                  # Feature scalers
│   └── model_summary_report.json
│
├── 📂 notebooks/
│   ├── EDA.ipynb                     # Exploratory Data Analysis
│   └── ML_Pipeline.ipynb             # Model training pipeline
│
├── 📂 utils/
│   └── helpers.py                    # Common utilities
│
├── dashboard.py                      # Streamlit dashboard application
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
│
└── 📄 Documentation/
    ├── DATASET_OVERVIEW.md           # Data schema & statistics
    ├── EDA_STATUS.md                 # EDA findings
    ├── ML_PIPELINE_FINAL_REPORT.md   # Model performance report
    └── QUICK_REFERENCE.md            # Quick start guide
```

---

## 🛠️ Technologies Used

### Core Technologies
- **Python 3.11+** - Primary programming language
- **Selenium & BeautifulSoup4** - Web scraping frameworks
- **Pandas & NumPy** - Data manipulation and analysis
- **Requests & LXML** - HTTP requests and HTML parsing

### Machine Learning
- **scikit-learn** - ML model training (Random Forest, Gradient Boosting, Ridge Regression)
- **pickle** - Model serialization

### Visualization & Dashboard
- **Streamlit** - Interactive web dashboard
- **Plotly** - Dynamic charts and visualizations
- **Matplotlib & Seaborn** - Static visualizations

### Storage & Automation
- **CSV/JSON** - Data storage
- **GitHub Actions** - Automated scraping schedules

---

## 🤖 Machine Learning Models

### Model Performance Summary

| Model | Task | Accuracy/RMSE | Status |
|-------|------|---------------|--------|
| **Price Category Classifier** | Classify games into Budget/Mid-range/Premium | 99.58% | ✅ Production Ready |
| **Deal Classifier** | Identify "Good Deals" (≥25% off OR ≥€10 savings) | 100% | ✅ Production Ready |
| **Price Regressor** | Predict fair market price | €18.84 RMSE | ✅ Production Ready |

### Deal Classification Criteria

A game is classified as a **"Good Deal"** if:
- **Discount ≥ 25%** OR
- **Savings ≥ €10**

These rules are strictly enforced with AI-powered confidence scoring.

### Model Details

**1. Price Category Classifier**
- Algorithm: Random Forest
- Features: 9 (discount %, original price, platform, storefront, category, etc.)
- Training Data: 4,788 samples
- Test Accuracy: 99.58%

**2. Deal Classifier**
- Algorithm: Gradient Boosting
- Features: 9 engineered features
- Training Data: 4,788 samples
- Test Accuracy: 100%

**3. Price Regression Model**
- Algorithm: Random Forest Regressor
- Features: 8 (cleaned, no data leakage)
- RMSE: €18.84
- Improvement: 33.3% over baseline

📖 Full details in [ML_PIPELINE_FINAL_REPORT.md](ML_PIPELINE_FINAL_REPORT.md)

---

## 📊 Dataset Overview

### Coverage

| Metric | Value |
|--------|-------|
| **Total Games** | 7,068+ |
| **Unique Platforms** | 5 (PC, Xbox, PlayStation, Switch, Unknown) |
| **Unique Storefronts** | 6+ |
| **Price Range** | €0.00 - €249.99 |
| **Data Sources** | 6 major gaming retailers |

### Data Schema

Each cleaned dataset includes:
- `title` - Game name
- `price_eur` - Current price (€)
- `original_price_eur` - Pre-discount price
- `discount_pct` - Discount percentage
- `platform` - Gaming platform (PC, Xbox, etc.)
- `storefront` - Store source (Steam, Epic, etc.)
- `category` - Product category
- `is_preorder` - Preorder status
- `product_url` - Direct link to product page
- `release_date` - Game release date

📖 Full schema details in [DATASET_OVERVIEW.md](DATASET_OVERVIEW.md)

---

## 🚦 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- 4GB+ RAM (for ML models)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mddiab/web-scraping-project.git
cd web-scraping-project
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Launch the dashboard**
```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 🕷️ Web Scraping

### Supported Platforms

| Platform | Games | Features |
|----------|-------|----------|
| **Steam** | 3,533 | Top sellers, specials, trending |
| **Epic Games** | 901 | Free games, weekly deals |
| **GOG** | Varies | DRM-free games |
| **Xbox Store** | 1,502 | Game Pass, Xbox deals |
| **Instant Gaming** | 1,000 | Multi-platform keys |
| **Loaded/CDKeys** | 132 | Discount game keys |

### Running Scrapers

```bash
# Individual scrapers
python scrapers/steam_scraper.py
python scrapers/epicgames_scraper.py
python scrapers/gog_scraper.py

# Data cleaning
python cleaners/steam_cleaner.py
python cleaners/epicgames_cleaner.py
```

**Note:** Scrapers respect robots.txt and implement rate limiting to avoid server overload.

---

## 📈 Data Analysis Workflow

1. **Scraping** → Collect raw data from 6 platforms
2. **Cleaning** → Normalize schema, remove duplicates, validate prices
3. **EDA** → Explore pricing trends, discount patterns, outliers
4. **Feature Engineering** → Create ML features (has_discount, high_discount, etc.)
5. **Model Training** → Train 3 ML models with cross-validation
6. **Dashboard** → Visualize insights and predictions

---

## 🎨 Dashboard Features

### Visual Design
- **Neon Black/Purple Theme** with gradient accents
- **Glassmorphism** card effects
- **Custom scrollbars** and hover animations
- **Google Fonts** (Inter + Outfit) for modern typography
- **Responsive layout** optimized for all screen sizes

### Visualizations
1. **Price Distribution by Store** - Box plots comparing price ranges
2. **Top Discounts Histogram** - Frequency distribution of discounts
3. **Deal Hunter Scatter Plot** - Price vs. discount correlation
4. **Games by Store Donut Chart** - Platform distribution
5. **Average Price by Platform** - Bar chart comparison
6. **Interactive Data Table** - Sortable game catalog with links

### Filters
- **Store Selection** - Multi-select stores
- **Price Range** - Slider (€0 - €250)
- **Minimum Discount** - Percentage threshold
- **Search** - Find games by title

---

## 🧪 Model Usage Examples

### Load Models

```python
import pickle
import numpy as np

# Load deal classifier
deal_model = pickle.load(open('models/best_model_deal_classifier_Gradient_Boosting.pkl', 'rb'))
scaler = pickle.load(open('models/scaler_deal_classifier.pkl', 'rb'))

# Prepare features (9 features)
features = np.array([[50, 59.99, 1, 1, 0, 0, 0, 0, 0]])  # discount%, original_price, etc.
X_scaled = scaler.transform(features)

# Predict
prediction = deal_model.predict(X_scaled)  # 'Good Deal' or 'Not a Deal'
confidence = deal_model.predict_proba(X_scaled)[0]
print(f"Prediction: {prediction[0]} (Confidence: {max(confidence)*100:.1f}%)")
```

### Price Prediction

```python
# Load price regression model
price_model = pickle.load(open('models/best_model_price_regression_clean.pkl', 'rb'))
scaler = pickle.load(open('models/scaler_price_regression_clean.pkl', 'rb'))

# Features (8 features - NO original_price)
features = np.array([[25, 1, 0, 0, 0, 0, 0, 0]])
X_scaled = scaler.transform(features)

predicted_price = price_model.predict(X_scaled)[0]
print(f"Fair Market Price: €{predicted_price:.2f}")
```

---

## 📊 Key Insights

### Pricing Analysis
- **Average Game Price**: €24.50
- **Average Discount**: 32%
- **Best Deals Source**: Steam (50%+ discounts common)
- **Premium Platform**: Xbox Store (avg €35)

### ML Findings
- **Perfect Deal Classification** (100% accuracy) validates clear criteria
- **Price prediction** achieves €18.84 RMSE (33% better than baseline)
- **Data leakage** detected and fixed before production deployment
- **Cross-validation** ensures model reliability

📖 Full analysis in [EDA_STATUS.md](EDA_STATUS.md)

---

## 🔮 Future Enhancements

- [ ] Add more platforms (PlayStation Store, Nintendo eShop, Ubisoft Connect)
- [ ] Implement price tracking over time (temporal analysis)
- [ ] Email/SMS alerts for major price drops
- [ ] User accounts with wishlist functionality
- [ ] Historical price charts per game
- [ ] Database backend (PostgreSQL/MongoDB)
- [ ] RESTful API for mobile apps
- [ ] Deploy dashboard to cloud (Streamlit Cloud, AWS, or Heroku)

---

## 🤝 Contributors

- **Mohamad Diab** - 20220584
- **Mohamad Chehade** - 20210253
- **Sahar Sabbagh** - 20220364

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Web Scraping Frameworks**: Selenium, BeautifulSoup4
- **ML Libraries**: scikit-learn, pandas, numpy
- **Visualization**: Streamlit, Plotly
- **Data Sources**: Steam, Epic Games, GOG, Xbox, Instant Gaming, Loaded

---

## 📧 Contact

- GitHub: [@mddiab](https://github.com/mddiab)
- Project Link: [web-scraping-project](https://github.com/mddiab/web-scraping-project)

---

**⭐ If you find this project useful, please consider giving it a star!**
