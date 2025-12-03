# 🎮 Game Deals Tracker
**Advanced Web Scraping & ML Analysis Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Overview

An advanced web scraping and machine learning platform that aggregates game deals from multiple major gaming sources, analyzes pricing trends, and uses **AI models** to identify the best deals. The analysis and documentation are based on the rebuilt EDA v2 (canonical) and drive the Streamlit dashboard and ML pipeline.

**📊 Dataset:** 7,058 games (canonical, per EDA v2) | **🤖 ML Models:** 3 production-ready | **🎨 Dashboard:** Interactive Streamlit UI

### 🎯 Key Features

- 🕷️ **Multi-Platform Scraping**: Automated data collection from Steam, Epic Games, GOG, Xbox, Instant Gaming, and Loaded
- 🤖 **AI Deal Predictor**: Machine learning models classify deals and predict fair market prices
- 📊 **Interactive Dashboard**: Beautiful Streamlit UI with real-time visualizations
- 💾 **Comprehensive Dataset**: 7,000+ games with pricing, discounts, and metadata
- 🎨 **Professional Design**: Modern neon-themed interface with glassmorphism effects
- 📈 **Advanced Analytics**: Price trends, discount patterns, and platform comparisons

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- 4GB+ RAM

### Installation

```bash
# Clone the repository
git clone https://github.com/mddiab/web-scraping-project.git
cd web-scraping-project

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Dashboard Features:**
- 🔍 Advanced filtering (price range, discount %, store selection)
- 🎯 AI Deal Predictor with confidence scores
- 📊 Interactive visualizations
- 🎮 Sortable game catalog
- ⚡ Real-time performance metrics

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[DATASET_OVERVIEW.md](DATASET_OVERVIEW.md)** | Complete dataset reference, schema, and quality metrics (based on EDA v2) |
| **[EDA.md](EDA.md)** | Exploratory data analysis findings and insights (canonical EDA) |
| **[ML_PIPELINE_FINAL_REPORT.md](ML_PIPELINE_FINAL_REPORT.md)** | ML models, validation, and performance metrics |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | CLI commands and common operations |

---

## 🏗️ Project Structure

```
web-scraping-project/
├── data/
│   ├── raw/                    # Unprocessed scraped data
│   └── cleaned/                # Normalized CSVs
├── scrapers/                   # Platform-specific scrapers
├── cleaners/                   # Data cleaning & normalization
├── models/                     # Trained ML models & scalers
├── notebooks/
│   ├── EDA.ipynb              # Exploratory Data Analysis
│   └── ML_Pipeline.ipynb      # Model training
├── dashboard.py               # Streamlit dashboard
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

---

## 🛠️ Technologies

| Category | Tools |
|----------|-------|
| **Scraping** | Selenium, BeautifulSoup4, Requests |
| **Data** | Pandas, NumPy |
| **ML** | scikit-learn (Random Forest, Gradient Boosting) |
| **Dashboard** | Streamlit, Plotly |
| **Visualization** | Matplotlib, Seaborn |

---

## 🤖 Machine Learning Models

Three production-ready models:

1. **Price Category Classifier** (99.58% accuracy)
   - Classifies games: Budget / Mid-range / Premium

2. **Deal Classifier** (100% accuracy)
   - Identifies good deals: ≥25% off OR ≥€10 savings

3. **Price Regressor** (€18.84 RMSE)
   - Predicts fair market price (33% better than baseline)

📖 Details: [ML_PIPELINE_FINAL_REPORT.md](ML_PIPELINE_FINAL_REPORT.md)

---

## 📊 Dataset Summary

**Total:** 7,058 games (canonical; see `EDA_V2_SUMMARY.md` and `DATASET_OVERVIEW.md`)

| Source | Games | Platform |
|--------|-------|----------|
| Steam | 3,531 | PC |
| Xbox | 1,502 | Xbox |
| Instant Gaming | 998 | Multi-platform |
| Epic Games | 899 | PC (analyzed separately due to missing discount data) |
| GOG | Varies | PC |
| Loaded/CDKeys | 128 | Multi-platform |

📖 Full details: [DATASET_OVERVIEW.md](DATASET_OVERVIEW.md)

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
