import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_data(ticker, days_back=10):
    end   = datetime.utcnow()
    start = end - timedelta(days=days_back)

    df = yf.download(
        ticker,
        start=start.strftime('%Y-%m-%d'),
        end=end.strftime('%Y-%m-%d'),
        progress=False,
        auto_adjust=True,
    )

    if df.empty:
        return None

    df = df.reset_index()
    df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
    df = df.rename(columns={'index': 'date'})
    df['date'] = pd.to_datetime(df['date'])

    return df[['date', 'open', 'high', 'low', 'close', 'volume']].dropna()