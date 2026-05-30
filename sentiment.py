import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import yfinance as yf

nltk.download('vader_lexicon', quiet=True)
load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
sia = SentimentIntensityAnalyzer()

NOISE_KEYWORDS = [
    'car', 'vehicle', 'suv', 'automobile', 'launched', 'price booking',
    'university', 'admission', 'pharma trial', 'clinical trial', 'atopic',
    'salmonella', 'subaru', 'seinfeld', 'pypi', 'apparel',
    'chargesheet', 'fir', 'police', 'nashik', 'crime', 'case filed'
]

FINANCE_KEYWORDS = [
    'stock', 'share', 'market', 'earnings', 'revenue', 'profit', 'loss',
    'quarter', 'q1', 'q2', 'q3', 'q4', 'investor', 'analyst', 'nse', 'bse',
    'nasdaq', 'nyse', 'deal', 'contract', 'partnership', 'acquisition',
    'merger', 'ipo', 'dividend', 'guidance', 'forecast', 'results', 'ai',
    'growth', 'business', 'enterprise', 'financial', 'fund', 'trading'
]


def score_text(text):
    scores = sia.polarity_scores(text)
    return {
        'compound': scores['compound'],
        'positive': scores['pos'],
        'negative': scores['neg'],
        'neutral':  scores['neu'],
    }


def get_company_keywords(ticker):
    """Dynamically fetch company name from yfinance for any ticker."""
    try:
        info = yf.Ticker(ticker).info
        name = info.get('longName') or info.get('shortName') or ''
        words = name.lower().split()
        keywords = [
            ticker.lower().replace('.ns', '').replace('.bo', ''),
            name.lower(),
        ]
        if len(words) >= 2:
            keywords.append(f"{words[0]} {words[1]}")
        if words and len(words[0]) > 3:
            keywords.append(words[0])
        return [k for k in keywords if k and len(k) > 1]
    except:
        return [ticker.lower().replace('.ns', '').replace('.bo', '')]


def is_relevant(title, description, keywords):
    text = f"{title} {description}".lower()

    # Must contain company keyword
    if not any(kw in text for kw in keywords):
        return False

    # Must contain at least one finance keyword
    if not any(fk in text for fk in FINANCE_KEYWORDS):
        return False

    # Must NOT be noise
    if any(nk in text for nk in NOISE_KEYWORDS):
        return False

    return True


def fetch_and_score_news(ticker, days_back=3, max_articles=30):
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    keywords = get_company_keywords(ticker)
    primary_kw = keywords[1] if len(keywords) > 1 else ticker

    params = {
        'q':        f'"{primary_kw}" stock OR shares OR earnings OR market',
        'from':     from_date,
        'sortBy':   'publishedAt',
        'language': 'en',
        'pageSize': 100,
        'apiKey':   NEWSAPI_KEY,
    }

    response = requests.get('https://newsapi.org/v2/everything', params=params, timeout=10)
    articles = response.json().get('articles', [])

    rows = []
    for art in articles:
        title = art.get('title') or ''
        desc  = art.get('description') or ''

        if not is_relevant(title, desc, keywords):
            continue

        scores = score_text(f"{title}. {desc[:200]}")
        rows.append({
            'title':        title,
            'source':       art.get('source', {}).get('name', ''),
            'url':          art.get('url', ''),
            'published_at': pd.to_datetime(art.get('publishedAt')),
            **scores,
        })

        if len(rows) >= max_articles:
            break

    return pd.DataFrame(rows)