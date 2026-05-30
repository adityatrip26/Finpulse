import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

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
    with st.spinner(f'Analyzing market sentiment for {ticker}...'):
        news_df, price_df, agg, corr_df = run_pipeline(ticker, days_back, max_articles)

    if news_df is None or news_df.empty:
        st.warning('No articles found. Try a different ticker or increase days.')
        st.stop()

    # ── KPI Cards ─────────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric('Signal',        agg['signal'])
    c2.metric('Avg Score',     f"{agg['mean']:+.3f}")
    c3.metric('Articles',      agg['count'])
    c4.metric('Bullish',       f"{agg['bullish_pct']}%")
    c5.metric('Bearish',       f"{agg['bearish_pct']}%")
    c6.metric('Neutral',       f"{agg['neutral_pct']}%")

    st.markdown("---")

    # ── Daily sentiment ────────────────────────────────────────────────────
    daily = (
        news_df.groupby(news_df['published_at'].dt.date)['compound']
        .mean().reset_index()
    )
    daily.columns = ['date', 'sentiment']
    daily['date'] = pd.to_datetime(daily['date'])
    daily['color'] = daily['sentiment'].apply(lambda x: '#00c896' if x > 0 else '#ff4d6d')

    # Most bullish / bearish day
    most_bullish = daily.loc[daily['sentiment'].idxmax(), 'date'].strftime('%b %d')
    most_bearish = daily.loc[daily['sentiment'].idxmin(), 'date'].strftime('%b %d')
    most_bullish_headline = news_df.loc[news_df['compound'].idxmax(), 'title']
    sentiment_volatility  = round(news_df['compound'].std(), 3)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"🟢 **Most Bullish Day:** {most_bullish}")
        st.markdown(f"🔴 **Most Bearish Day:** {most_bearish}")
    with col2:
        st.markdown(f"📰 **Most Bullish Headline:** {most_bullish_headline[:80]}...")
        st.markdown(f"📊 **Sentiment Volatility:** {sentiment_volatility}")

    st.markdown("---")

    # ── Chart 1: Sentiment trend ───────────────────────────────────────────
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=daily['date'],
        y=daily['sentiment'],
        marker_color=daily['color'],
        name='Daily Sentiment',
        hovertemplate='<b>%{x}</b><br>Sentiment: %{y:.3f}<extra></extra>'
    ))
    fig1.add_hline(y=0, line_dash='dash', line_color='grey', line_width=1)
    fig1.update_layout(
        title=f'{ticker} — Daily Sentiment Trend',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1e3a5f'),
        height=350,
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Chart 2: Sentiment vs Price ────────────────────────────────────────
    if corr_df is not None and not corr_df.empty and 'close' in corr_df.columns:
        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(
            x=corr_df['date'],
            y=corr_df['close'],
            name='Price',
            line=dict(color='#60a0ff', width=2),
            hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>',
            yaxis='y1'
        ))

        fig2.add_trace(go.Bar(
            x=corr_df['date'],
            y=corr_df['sentiment'],
            name='Sentiment',
            marker_color=['#00c896' if v > 0 else '#ff4d6d' for v in corr_df['sentiment']],
            opacity=0.5,
            hovertemplate='<b>%{x}</b><br>Sentiment: %{y:.3f}<extra></extra>',
            yaxis='y2'
        ))

        fig2.update_layout(
            title=f'{ticker} — Sentiment vs Price',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(title='Price (USD)', showgrid=True, gridcolor='#1e3a5f'),
            yaxis2=dict(title='Sentiment', overlaying='y', side='right', showgrid=False),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ── Market Reaction Table ──────────────────────────────────────────
        st.markdown("### 📊 Market Reaction Correlation")
        corr_df['next_day_return'] = corr_df['close'].pct_change().shift(-1) * 100
        corr_df['next_day_return'] = corr_df['next_day_return'].round(2)

        display_corr = corr_df[['date', 'sentiment', 'close', 'next_day_return']].copy()
        display_corr.columns = ['Date', 'Sentiment Score', 'Close Price', 'Next Day Return (%)']
        display_corr['Date'] = display_corr['Date'].dt.strftime('%b %d')
        display_corr['Sentiment Score'] = display_corr['Sentiment Score'].apply(lambda x: f"{x:+.3f}")
        display_corr['Next Day Return (%)'] = display_corr['Next Day Return (%)'].apply(
            lambda x: f"+{x}%" if x > 0 else f"{x}%" if pd.notna(x) else "—"
        )
        st.dataframe(display_corr, use_container_width=True, hide_index=True)

    # ── Headlines ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader('📰 Headlines')
    for _, row in news_df.sort_values('published_at', ascending=False).head(30).iterrows():
        score = row['compound']
        label = '▲ BULLISH' if score > 0.05 else '▼ BEARISH' if score < -0.05 else '◆ NEUTRAL'
        color = 'green' if score > 0.05 else 'red' if score < -0.05 else 'gray'
        st.markdown(f":{color}[**{label}**] `{score:+.3f}` — {row['title']}")
        st.caption(f"{row['source']} · {row['published_at'].strftime('%b %d, %H:%M')}")

    # ── CSV Export ─────────────────────────────────────────────────────────
    csv = news_df.to_csv(index=False).encode('utf-8')
    st.download_button('⬇️ Export CSV', data=csv,
                       file_name=f'{ticker}_sentiment.csv', mime='text/csv')

