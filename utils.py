import pandas as pd

def get_aggregate_sentiment(news_df):
    scores    = news_df['compound']
    total     = len(scores)
    bullish   = (scores > 0.05).sum()
    bearish   = (scores < -0.05).sum()
    neutral_n = ((scores >= -0.05) & (scores <= 0.05)).sum()
    mean      = scores.mean()

    return {
        'mean':         round(float(mean), 4),
        'count':        total,
        'bullish_pct':  round(100 * bullish / total, 1),
        'bearish_pct':  round(100 * bearish / total, 1),
        'neutral_pct':  round(100 * neutral_n / total, 1),
        'signal':       'BULLISH' if mean > 0.05 else 'BEARISH' if mean < -0.05 else 'NEUTRAL',
    }
def correlate_sentiment_price(news_df, price_df):
    # Average sentiment per day
    daily = (
        news_df.groupby(news_df['published_at'].dt.date)['compound']
        .mean()
        .reset_index()
    )
    daily.columns = ['date', 'sentiment']
    daily['date'] = pd.to_datetime(daily['date'])

    if price_df is None or price_df.empty:
        return daily

    price_df['date'] = pd.to_datetime(price_df['date']).dt.normalize()
    return pd.merge(daily, price_df[['date', 'close']], on='date', how='inner')