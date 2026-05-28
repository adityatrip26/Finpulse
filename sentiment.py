import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon', quiet=True)
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
sia = SentimentIntensityAnalyzer() 
def score_text(text):
    scores = sia.polarity_scores(text)
    return {
        'compound': scores['compound'],
        'positive': scores['pos'],
        'negative': scores['neg'],
        'neutral':  scores['neu'],
    }
def fetch_and_score_news(ticker, days_back=3, max_articles=30):
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    params = {
        'q':        f'{ticker} stock OR shares OR earnings',
        'from':     from_date,
        'sortBy':   'publishedAt',
        'language': 'en',
        'pageSize': min(max_articles, 100),
        'apiKey':   NEWSAPI_KEY,
    }

    response = requests.get('https://newsapi.org/v2/everything', params=params, timeout=10)
    articles = response.json().get('articles', [])

    rows = []
    for art in articles:
        title = art.get('title') or ''
        desc  = art.get('description') or ''
        # Score the headline + first 200 chars of description
        scores = score_text(f"{title}. {desc[:200]}")
        rows.append({
            'title':        title,
            'source':       art.get('source', {}).get('name', ''),
            'url':          art.get('url', ''),
            'published_at': pd.to_datetime(art.get('publishedAt')),
            **scores,
        })

    return pd.DataFrame(rows)