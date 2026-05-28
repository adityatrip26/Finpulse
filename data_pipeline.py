from sentiment import fetch_and_score_news
from price_data import fetch_price_data
from utils import get_aggregate_sentiment, correlate_sentiment_price

def run_pipeline(ticker, days_back=3, max_articles=30):
    news_df  = fetch_and_score_news(ticker, days_back, max_articles)
    price_df = fetch_price_data(ticker, days_back + 5)

    if news_df is None or news_df.empty:
        return None, None, None, None

    agg     = get_aggregate_sentiment(news_df)
    corr_df = correlate_sentiment_price(news_df, price_df)

    return news_df, price_df, agg, corr_df