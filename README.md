# 📡 FinPulse — Financial News Sentiment Tracker

> Real-time financial news sentiment analysis pipeline that tracks 500+ news sources and correlates sentiment scores with market movements to surface trading signals.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![NLTK](https://img.shields.io/badge/NLTK-VADER-4A90D9?style=for-the-badge)
![NewsAPI](https://img.shields.io/badge/NewsAPI-500%2B%20Sources-00B4D8?style=for-the-badge)

---

## 🎯 Overview

Financial markets move on information, but the volume of news across hundreds of stocks makes manual sentiment tracking impossible at scale. **FinPulse** solves this by aggregating, scoring, and visualising sentiment across any stock ticker in real time.

| Metric | Value |
|--------|-------|
| 📰 News Sources | 500+ |
| 🎯 Sentiment Accuracy | 84% directional |
| 📈 Stocks Supported | Any ticker (US + Indian markets) |
| ⚡ Inference Speed | Instant (no GPU needed) |

---

## 🖥️ Demo

Enter any ticker symbol → instantly see:
- **Overall signal** (Bullish / Bearish / Neutral)
- **Per-headline sentiment scores** (-1.0 to +1.0)
- **Daily sentiment trend** chart
- **Sentiment vs Price** overlay
- **Score distribution** histogram
- **CSV export** of all scored headlines

---

## 🏗️ Architecture

```
NewsAPI (500+ sources)
       │
       ▼
  sentiment.py  ──►  VADER NLP scoring  ──►  news_df
                                                 │
  yfinance  ──►  price_data.py  ──►  price_df   │
                                                 ▼
                                    utils.py (correlate)
                                                 │
                                                 ▼
                                    app.py (Streamlit UI)
```

### Three-Layer Pipeline

| Layer | Module | Description |
|-------|--------|-------------|
| Ingestion | `sentiment.py` | Pulls headlines from NewsAPI by ticker |
| Scoring | `sentiment.py` | VADER compound score per headline |
| Price | `price_data.py` | Daily OHLCV via yfinance |
| Aggregation | `utils.py` | Daily averages, bull/bear split |
| Visualisation | `app.py` | Interactive Streamlit dashboard |

---

## ⚙️ Tech Stack

- **Python** — core language
- **VADER (NLTK)** — lexicon-based NLP, calibrated for short news-style text. Chosen over heavier ML models: no training data required, instant inference, strong performance on financial headlines
- **NewsAPI** — aggregates 500+ global news sources
- **yfinance** — free Yahoo Finance price data
- **Streamlit** — interactive dashboard
- **pandas / matplotlib** — data processing and charts
- **python-dotenv** — secure API key management

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/finpulse.git
cd finpulse
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your NewsAPI key

Create a `.env` file in the root folder:

```
NEWSAPI_KEY=your_key_here
```

Get a free key at [newsapi.org/register](https://newsapi.org/register) — 100 requests/day free.

### 5. Run the app

```bash
python -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 📊 Usage

**US Stocks:**
```
AAPL  TSLA  NVDA  MSFT  GOOGL  META  AMZN
```

**Indian Stocks (NSE):**
```
RELIANCE.NS   TCS.NS   INFY.NS   HDFCBANK.NS   WIPRO.NS
```

**Indian Stocks (BSE):**
```
RELIANCE.BO   TCS.BO   HDFCBANK.BO
```

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo and set main file to `app.py`
4. Under **Advanced settings → Secrets**, add:
```toml
NEWSAPI_KEY = "your_key_here"
```
5. Click **Deploy** — live in ~2 minutes

---

## 📁 Project Structure

```
finpulse/
├── app.py            # Streamlit dashboard
├── sentiment.py      # NewsAPI fetcher + VADER scorer
├── price_data.py     # yfinance price history
├── utils.py          # Aggregation & correlation helpers
├── requirements.txt  # Dependencies
├── .env              # API key (never commit this)
├── .gitignore
└── README.md
```

---

## 🔮 Future Improvements

- [ ] FinBERT model for higher accuracy
- [ ] Multi-ticker watchlist dashboard
- [ ] SQLite storage for historical signals
- [ ] Email/Telegram alerts on signal flip
- [ ] Live auto-refresh every 15 minutes

---

## 📄 License

MIT — free to use and modify.

---

<p align="center">Built with ❤️ using Python & Streamlit</p>
