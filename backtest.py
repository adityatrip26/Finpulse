import pandas as pd
import yfinance as yf
from sentiment import fetch_and_score_news
from utils import correlate_sentiment_price

WATCHLIST = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "NVDA", "META", "NFLX", "AMD", "INTC",
    "JPM", "BAC", "GS", "V", "MA",
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS"
]

def backtest_ticker(ticker):
    try:
        news_df = fetch_and_score_news(ticker, days_back=7, max_articles=50)
        if news_df is None or news_df.empty:
            return None

        raw = yf.download(ticker, period="10d", progress=False, auto_adjust=True)
        if raw.empty:
            return None

        raw = raw.reset_index()
        raw.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in raw.columns]
        raw = raw.rename(columns={'index': 'date'})
        raw['date'] = pd.to_datetime(raw['date'])

        price_df = raw[['date', 'close']].dropna()

        corr = correlate_sentiment_price(news_df, price_df).sort_values('date')
        if len(corr) < 2:
            return None

        corr['price_dir'] = corr['close'].diff().shift(-1).apply(
            lambda x: 1 if x > 0 else -1 if x < 0 else 0
        )
        corr['sent_dir'] = corr['sentiment'].apply(
            lambda x: 1 if x > 0.05 else -1 if x < -0.05 else 0
        )

        mask = corr['sent_dir'] != 0
        sub  = corr[mask]
        if sub.empty:
            return None

        correct  = (sub['price_dir'] == sub['sent_dir']).sum()
        accuracy = round(100 * correct / len(sub), 1)

        return {'ticker': ticker, 'days': len(sub), 'accuracy': accuracy}

    except Exception as e:
        print(f"Error on {ticker}: {e}")
        return None


if __name__ == "__main__":
    print(f"Running backtest on {len(WATCHLIST)} tickers...\n")
    results = []

    for ticker in WATCHLIST:
        r = backtest_ticker(ticker)
        if r:
            results.append(r)
            print(f"  {ticker:<20} {r['accuracy']}% over {r['days']} days")

    if results:
        df = pd.DataFrame(results)
        avg = df["accuracy"].mean()
        print(f"\n{'─'*40}")
        print(f"Overall directional accuracy: {avg:.1f}%")
        print(f"Tickers tested: {len(df)}")
        df.to_csv("backtest_results.csv", index=False)
        print("Results saved to backtest_results.csv")
    else:
        print("No results — check your NewsAPI key and internet connection.")