import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from data_pipeline import run_pipeline

st.set_page_config(page_title='FinPulse', page_icon='📡', layout='wide')

with st.sidebar:
    st.header('⚙️ Settings')
    days_back    = st.slider('Days of news', 1, 7, 3)
    max_articles = st.slider('Max articles', 10, 100, 30)

st.title('📡 FinPulse — Sentiment Tracker')

ticker = st.text_input('Enter ticker symbol', value='AAPL').strip().upper()
run    = st.button('Analyze')

if run:
    with st.spinner('Fetching news...'):
        news_df, price_df, agg, corr_df = run_pipeline(ticker, days_back, max_articles)

    if news_df is None or news_df.empty:
        st.warning('No articles found.')
        st.stop()

    # KPI cards
    c1, c2, c3 = st.columns(3)
    c1.metric('Signal',    agg['signal'])
    c2.metric('Avg Score', f"{agg['mean']:+.3f}")
    c3.metric('Articles',  agg['count'])

    # Sentiment trend chart
    daily = (
        news_df.groupby(news_df['published_at'].dt.date)['compound']
        .mean().reset_index()
    )
    daily.columns = ['date', 'sentiment']
    daily['date'] = pd.to_datetime(daily['date'])

    fig, ax = plt.subplots(figsize=(10, 3))
    colors = ['green' if v > 0 else 'red' for v in daily['sentiment']]
    ax.bar(daily['date'], daily['sentiment'], color=colors, alpha=0.8)
    ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.set_title(f'{ticker} — Daily Sentiment')
    st.pyplot(fig)
    plt.close()

    # Sentiment vs Price chart
    if not corr_df.empty and 'close' in corr_df.columns:
        fig, ax1 = plt.subplots(figsize=(10, 3))
        ax1.plot(corr_df['date'], corr_df['close'], color='steelblue', label='Price')
        ax1.set_ylabel('Price (USD)')

        ax2 = ax1.twinx()
        ax2.bar(corr_df['date'], corr_df['sentiment'],
                color=['green' if v > 0 else 'red' for v in corr_df['sentiment']],
                alpha=0.35, label='Sentiment')
        ax2.set_ylabel('Sentiment Score')
        ax1.set_title(f'{ticker} — Sentiment vs Price')
        st.pyplot(fig)
        plt.close()

    # Headlines
    st.subheader('Headlines')
    for _, row in news_df.sort_values('published_at', ascending=False).head(30).iterrows():
        score = row['compound']
        label = '▲ BULLISH' if score > 0.05 else '▼ BEARISH' if score < -0.05 else '◆ NEUTRAL'
        st.markdown(f"**{label}** `{score:+.3f}` — {row['title']}")
        st.caption(f"{row['source']} · {row['published_at'].strftime('%b %d, %H:%M')}")

    # CSV export
    csv = news_df.to_csv(index=False).encode('utf-8')
    st.download_button('⬇️ Export CSV', data=csv,
                       file_name=f'{ticker}_sentiment.csv', mime='text/csv')

