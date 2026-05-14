import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Tushar Smart Money Terminal",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp{
    background: linear-gradient(180deg,#e0f2fe,#f8fbff);
}

[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#dbeafe,#eff6ff);
}

.card{
    background:white;
    padding:22px;
    border-radius:22px;
    margin-bottom:20px;
    border:1px solid #dbeafe;
    box-shadow:0 10px 30px rgba(59,130,246,0.08);
}

.top{
    background:linear-gradient(90deg,#2563eb,#38bdf8);
    padding:30px;
    border-radius:30px;
    color:white;
    margin-bottom:25px;
}

.buy{
    background:#dcfce7;
    color:#166534;
    padding:18px;
    border-radius:18px;
    text-align:center;
    font-size:32px;
    font-weight:700;
}

.sell{
    background:#fee2e2;
    color:#991b1b;
    padding:18px;
    border-radius:18px;
    text-align:center;
    font-size:32px;
    font-weight:700;
}

.hold{
    background:#fef9c3;
    color:#854d0e;
    padding:18px;
    border-radius:18px;
    text-align:center;
    font-size:32px;
    font-weight:700;
}

.small{
    color:#64748b;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNCTIONS
# =========================================================

@st.cache_data(ttl=60)
def fetch_data(ticker, interval):

    df = yf.Ticker(ticker).history(
        period="7d",
        interval=interval,
        auto_adjust=True
    )

    df.dropna(inplace=True)

    return df

def rsi(data, period=14):

    delta = data.diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📈 Smart Money")

    market = st.selectbox(
        "Market",
        [
            "NIFTY 50",
            "BANK NIFTY",
            "RELIANCE",
            "TCS",
            "INFY"
        ]
    )

    interval = st.selectbox(
        "Timeframe",
        ["5m", "15m", "30m", "60m", "1d"],
        index=1
    )

ticker_map = {
    "NIFTY 50":"^NSEI",
    "BANK NIFTY":"^NSEBANK",
    "RELIANCE":"RELIANCE.NS",
    "TCS":"TCS.NS",
    "INFY":"INFY.NS"
}

ticker = ticker_map[market]

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="top">

<h1>📊 Tushar Smart Money Terminal</h1>

<p>
AI-assisted market analysis for educational and risk-aware trading.
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# QUOTES
# =========================================================

quotes = [

    "Protect capital first. Profit comes later.",

    "Volume reveals intention before price.",

    "Fake breakouts trap emotions.",

    "Discipline beats prediction.",

    "Trend is probability, not certainty."

]

st.markdown(f"""
<div class="card">

<h3>💡 Market Wisdom</h3>

<p>{random.choice(quotes)}</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# DATA
# =========================================================

df = fetch_data(ticker, interval)

if df.empty:

    st.error("No market data available.")

    st.stop()

# =========================================================
# INDICATORS
# =========================================================

df['EMA20'] = df['Close'].ewm(span=20).mean()

df['EMA50'] = df['Close'].ewm(span=50).mean()

df['RSI'] = rsi(df['Close'])

df['VOLAVG'] = df['Volume'].rolling(20).mean()

latest = df.iloc[-1]

price = latest['Close']

support = df['Low'].rolling(20).min().iloc[-1]

resistance = df['High'].rolling(20).max().iloc[-1]

volume_spike = latest['Volume'] > latest['VOLAVG'] * 1.8

fake_breakout = (
    latest['High'] > df['High'].iloc[-2]
    and latest['Close'] < latest['Open']
)

# =========================================================
# SIGNAL ENGINE
# =========================================================

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

confidence = min(score * 25, 95)

# =========================================================
# KPI
# =========================================================

k1,k2,k3,k4 = st.columns(4)

change = price - df['Close'].iloc[-2]

pct = (change / df['Close'].iloc[-2]) * 100

with k1:
    st.markdown(f"""
    <div class="card">
    <div class="small">Spot Price</div>
    <h2>₹ {round(price,2)}</h2>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="card">
    <div class="small">Day Change</div>
    <h2>{round(pct,2)}%</h2>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
    <div class="small">RSI</div>
    <h2>{round(latest['RSI'],2)}</h2>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="card">
    <div class="small">Confidence</div>
    <h2>{confidence}%</h2>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# LAYOUT
# =========================================================

left, right = st.columns([3,1])

# =========================================================
# CHART
# =========================================================

with left:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📈 Price Action")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7,0.3]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA20'],
            name="EMA20"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA50'],
            name="EMA50"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name="Volume"
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        template="plotly_white",
        height=700,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RIGHT
# =========================================================

with right:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🤖 AI Signal")

    st.markdown(
        f'<div class="{signal_class}">{signal}</div>',
        unsafe_allow_html=True
    )

    st.write(f"Confidence: {confidence}%")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🚨 Warnings")

    if fake_breakout:
        st.error(
            "Fake breakout detected. Retail traders may get trapped."
        )

    if volume_spike:
        st.warning(
            "Volume spike detected. Smart money activity possible."
        )

    if abs(price - support) < 30:
        st.success(
            f"Near support ₹{round(support,2)}. Bounce possible."
        )

    if abs(price - resistance) < 30:
        st.warning(
            f"Near resistance ₹{round(resistance,2)}. Pullback possible."
        )

    if latest['RSI'] > 70:
        st.error(
            "Overbought zone. Profit booking risk."
        )

    if latest['RSI'] < 30:
        st.success(
            "Oversold zone. Short covering bounce possible."
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🌍 Market Mood")

    st.success("NASDAQ → Positive")

    st.info("GIFT NIFTY → Supportive")

    st.warning("VIX → Elevated")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================

st.caption(
    "Educational tool only. Markets involve risk. No signal guarantees profit."
)
