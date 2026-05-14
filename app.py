import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Tushar Quant Terminal",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.stApp{
background:linear-gradient(180deg,#e0f2fe,#f8fbff);
}

.card{
background:white;
padding:20px;
border-radius:22px;
margin-bottom:18px;
border:1px solid #dbeafe;
box-shadow:0 10px 30px rgba(0,0,0,0.05);
}

.buy{
background:#dcfce7;
padding:18px;
border-radius:18px;
text-align:center;
font-size:32px;
font-weight:700;
color:#166534;
}

.sell{
background:#fee2e2;
padding:18px;
border-radius:18px;
text-align:center;
font-size:32px;
font-weight:700;
color:#991b1b;
}

.hold{
background:#fef9c3;
padding:18px;
border-radius:18px;
text-align:center;
font-size:32px;
font-weight:700;
color:#854d0e;
}

.news{
padding:12px;
border-radius:12px;
background:#f8fafc;
margin-bottom:10px;
border-left:4px solid #3b82f6;
}

.metric-box{
background:white;
padding:15px;
border-radius:16px;
text-align:center;
border:1px solid #dbeafe;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("📈 Quant Terminal")

    market = st.selectbox(
        "Market",
        [
            "NIFTY 50",
            "BANK NIFTY",
            "SENSEX",
            "RELIANCE",
            "TCS",
            "INFY"
        ]
    )

    timeframe = st.selectbox(
        "Timeframe",
        ["5m","15m","30m","60m","1d"],
        index=1
    )

symbol_map = {
    "NIFTY 50":"^NSEI",
    "BANK NIFTY":"^NSEBANK",
    "SENSEX":"^BSESN",
    "RELIANCE":"RELIANCE.NS",
    "TCS":"TCS.NS",
    "INFY":"INFY.NS"
}

tv_map = {
    "NIFTY 50":"NSE:NIFTY",
    "BANK NIFTY":"NSE:BANKNIFTY",
    "SENSEX":"BSE:SENSEX",
    "RELIANCE":"NSE:RELIANCE",
    "TCS":"NSE:TCS",
    "INFY":"NSE:INFY"
}

symbol = symbol_map[market]
tv_symbol = tv_map[market]

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class="card">

<h1>📊 Tushar Smart Money Terminal</h1>

<p>
AI Assisted Market Intelligence Dashboard
</p>

</div>
""", unsafe_allow_html=True)

# =====================================================
# FETCH DATA
# =====================================================

@st.cache_data(ttl=30)
def get_data():

    try:

        df = yf.download(
            symbol,
            period="5d",
            interval=timeframe,
            auto_adjust=True,
            progress=False
        )

        if isinstance(df.columns, pd.MultiIndex):

            df.columns = df.columns.get_level_values(0)

        df.dropna(inplace=True)

        return df

    except:

        return pd.DataFrame()

df = get_data()

if df.empty:

    st.error("Unable to fetch market data")

    st.stop()

# =====================================================
# INDICATORS
# =====================================================

df['EMA20'] = df['Close'].ewm(span=20).mean()

df['EMA50'] = df['Close'].ewm(span=50).mean()

delta = df['Close'].diff()

gain = delta.where(delta > 0, 0)

loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(14).mean()

avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

df['RSI'] = 100 - (100 / (1 + rs))

df['VOLAVG'] = df['Volume'].rolling(20).mean()

latest = df.iloc[-1]

price = float(latest['Close'])

# =====================================================
# SAFE VOLUME SPIKE
# =====================================================

if pd.isna(latest['VOLAVG']):

    volume_spike = False

else:

    volume_spike = (
        float(latest['Volume']) >
        float(latest['VOLAVG']) * 1.8
    )

# =====================================================
# SUPPORT / RESISTANCE
# =====================================================

support = float(
    df['Low'].rolling(20).min().iloc[-1]
)

resistance = float(
    df['High'].rolling(20).max().iloc[-1]
)

# =====================================================
# FAKE BREAKOUT
# =====================================================

fake_breakout = (

    latest['High'] > df['High'].iloc[-2]

    and

    latest['Close'] < latest['Open']

)

# =====================================================
# SIGNAL ENGINE
# =====================================================

score = 0

if latest['Close'] > latest['EMA20']:
    score += 1

if latest['EMA20'] > latest['EMA50']:
    score += 1

if latest['RSI'] > 55:
    score += 1

if volume_spike:
    score += 1

signal = "HOLD"
signal_class = "hold"

if score >= 3:

    signal = "BUY"
    signal_class = "buy"

elif score <= 1:

    signal = "SELL"
    signal_class = "sell"

confidence = score * 25

# =====================================================
# OPTION CHAIN
# =====================================================

@st.cache_data(ttl=60)
def get_option_chain():

    try:

        headers = {
            "user-agent":"Mozilla/5.0"
        }

        session = requests.Session()

        session.get(
            "https://www.nseindia.com",
            headers=headers
        )

        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        response = session.get(
            url,
            headers=headers
        )

        data = response.json()

        return data

    except:

        return None

option_data = get_option_chain()

# =====================================================
# NEWS
# =====================================================

all_news = []

try:

    news = yf.Ticker(symbol).news

    for item in news[:10]:

        title = item.get("title","")

        all_news.append(title)

except:

    pass

# =====================================================
# SENTIMENT ENGINE
# =====================================================

bullish_words = [
    "surge",
    "growth",
    "rally",
    "strong",
    "record",
    "bullish"
]

bearish_words = [
    "war",
    "crash",
    "fear",
    "inflation",
    "selloff",
    "bearish"
]

sentiment_score = 0

for item in all_news:

    text = item.lower()

    for word in bullish_words:

        if word in text:
            sentiment_score += 1

    for word in bearish_words:

        if word in text:
            sentiment_score -= 1

market_sentiment = "NEUTRAL"

if sentiment_score > 2:

    market_sentiment = "BULLISH"

elif sentiment_score < -2:

    market_sentiment = "BEARISH"

# =====================================================
# INDIA VIX
# =====================================================

try:

    vix = yf.download(
        "^INDIAVIX",
        period="1d",
        progress=False
    )

    vix_price = round(
        float(vix['Close'].iloc[-1]),
        2
    )

except:

    vix_price = 0

# =====================================================
# MARKET QUOTES
# =====================================================

quotes = [

    "Retailers chase candles. Smart money creates them.",

    "Volume reveals intention before price.",

    "Fake breakouts trap emotions.",

    "Trend is probability, not certainty.",

    "Protect capital first. Profit comes later."

]

quote = random.choice(quotes)

st.markdown(f"""
<div class="card">

<h3>💡 Market Wisdom</h3>

<p>{quote}</p>

</div>
""", unsafe_allow_html=True)

# =====================================================
# KPI ROW
# =====================================================

k1,k2,k3,k4,k5 = st.columns(5)

change = price - float(df['Close'].iloc[-2])

pct = (change / float(df['Close'].iloc[-2])) * 100

with k1:
    st.metric("Spot", round(price,2))

with k2:
    st.metric("Change %", round(pct,2))

with k3:
    st.metric("RSI", round(float(latest['RSI']),2))

with k4:
    st.metric("VIX", vix_price)

with k5:
    st.metric("Confidence", f"{confidence}%")

# =====================================================
# MAIN LAYOUT
# =====================================================

left,right = st.columns([3,1])

# =====================================================
# LEFT SIDE
# =====================================================

with left:

    # ================================================
    # TRADINGVIEW
    # ================================================

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📈 TradingView Chart")

    st.components.v1.html(f"""

    <div class="tradingview-widget-container">

      <div id="tradingview_chart"></div>

      <script type="text/javascript"
      src="https://s3.tradingview.com/tv.js"></script>

      <script type="text/javascript">

      new TradingView.widget({{

        "width": "100%",
        "height": 720,

        "symbol": "{tv_symbol}",

        "interval": "15",

        "timezone": "Asia/Kolkata",

        "theme": "light",

        "style": "1",

        "locale": "en",

        "toolbar_bg": "#f1f5f9",

        "enable_publishing": false,

        "allow_symbol_change": true,

        "studies": [

            "RSI@tv-basicstudies",
            "MACD@tv-basicstudies",
            "Volume@tv-basicstudies",
            "VWAP@tv-basicstudies",
            "BB@tv-basicstudies"

        ],

        "container_id": "tradingview_chart"

      }});

      </script>

    </div>

    """, height=740)

    st.markdown('</div>', unsafe_allow_html=True)

    # ================================================
    # OPTION CHAIN
    # ================================================

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📊 Option Chain")

    if option_data:

        try:

            records = option_data['records']['data']

            table = []

            for item in records[:15]:

                strike = item.get('strikePrice')

                ce_oi = item.get(
                    'CE',{}
                ).get(
                    'openInterest',0
                )

                pe_oi = item.get(
                    'PE',{}
                ).get(
                    'openInterest',0
                )

                ce_change = item.get(
                    'CE',{}
                ).get(
                    'changeinOpenInterest',0
                )

                pe_change = item.get(
                    'PE',{}
                ).get(
                    'changeinOpenInterest',0
                )

                table.append([

                    strike,
                    ce_oi,
                    pe_oi,
                    ce_change,
                    pe_change

                ])

            option_df = pd.DataFrame(

                table,

                columns=[

                    "Strike",
                    "CE OI",
                    "PE OI",
                    "CE Change",
                    "PE Change"

                ]

            )

            st.dataframe(
                option_df,
                use_container_width=True
            )

        except:

            st.warning("Option chain parse issue")

    else:

        st.warning("Option chain unavailable")

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# RIGHT SIDE
# =====================================================

with right:

    # ================================================
    # SIGNAL
    # ================================================

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🤖 AI Signal")

    st.markdown(

        f'<div class="{signal_class}">{signal}</div>',

        unsafe_allow_html=True

    )

    st.write(f"Signal Confidence: {confidence}%")

    st.markdown('</div>', unsafe_allow_html=True)

    # ================================================
    # WARNINGS
    # ================================================

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🚨 Smart Warnings")

    if fake_breakout:

        st.error(
            "Fake breakout detected"
        )

    if volume_spike:

        st.warning(
            "Volume spike detected"
        )

    if abs(price - support) < 30:

        st.success(
            "Support bounce possible"
        )

    if abs(price - resistance) < 30:

        st.warning(
            "Resistance pullback possible"
        )

    if latest['RSI'] > 70:

        st.error(
            "Overbought zone"
        )

    if latest['RSI'] < 30:

        st.success(
            "Oversold zone"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ================================================
    # MARKET MOOD
    # ================================================

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🌍 Market Mood")

    st.write(f"Sentiment: {market_sentiment}")

    if vix_price > 18:

        st.error("High Fear")

    elif vix_price < 12:

        st.success("Low Fear")

    else:

        st.info("Normal Volatility")

    st.markdown('</div>', unsafe_allow_html=True)

    # ================================================
    # NEWS
    # ================================================

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📰 Market News")

    if len(all_news) > 0:

        for item in all_news[:10]:

            st.markdown(f"""
            <div class="news">
            {item}
            </div>
            """, unsafe_allow_html=True)

    else:

        st.warning("News unavailable")

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================

st.caption(
    "Educational tool only. Markets involve risk. No guaranteed profit signals."
)
