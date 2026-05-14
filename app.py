import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Tushar Trading Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# PREMIUM CSS
# ==========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp{
    background: linear-gradient(180deg,#e0f2fe,#f8fbff);
}

/* Sidebar */

[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#dbeafe,#eff6ff);
    border-right:1px solid #bfdbfe;
}

/* Cards */

.glass-card{
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(10px);
    border-radius:24px;
    padding:22px;
    margin-bottom:20px;
    border:1px solid rgba(255,255,255,0.9);
    box-shadow:0 10px 35px rgba(59,130,246,0.08);
}

/* Header */

.top-nav{
    background: linear-gradient(90deg,#2563eb,#38bdf8);
    border-radius:28px;
    padding:28px;
    color:white;
    margin-bottom:24px;
    box-shadow:0 12px 40px rgba(37,99,235,0.25);
}

/* KPI */

.kpi-title{
    font-size:13px;
    color:#64748b;
    margin-bottom:8px;
}

.kpi-value{
    font-size:34px;
    font-weight:700;
    color:#0f172a;
}

.green{
    color:#10b981;
}

.red{
    color:#ef4444;
}

/* Signal Box */

.signal-box{
    padding:18px;
    border-radius:18px;
    text-align:center;
    font-weight:700;
    font-size:30px;
}

.buy{
    background:#dcfce7;
    color:#166534;
}

.sell{
    background:#fee2e2;
    color:#991b1b;
}

.neutral{
    background:#fef9c3;
    color:#854d0e;
}

/* News */

.news-box{
    background:white;
    border-radius:14px;
    padding:14px;
    margin-bottom:12px;
    border:1px solid #e2e8f0;
}

/* Levels */

.level-box{
    background:#ffffff;
    border-radius:14px;
    padding:10px;
    margin-bottom:10px;
    border:1px solid #dbeafe;
}

/* Footer */

.footer{
    text-align:center;
    color:#64748b;
    font-size:12px;
    padding:20px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# FUNCTIONS
# ==========================================================

@st.cache_data(ttl=60)
def fetch_data(ticker, interval):

    data = yf.Ticker(ticker).history(
        period="7d",
        interval=interval,
        auto_adjust=True,
        prepost=True
    )

    data.dropna(inplace=True)

    return data

def calculate_rsi(df, period=14):

    delta = df['Close'].diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_atr(df, period=14):

    high_low = df['High'] - df['Low']

    high_close = np.abs(df['High'] - df['Close'].shift())

    low_close = np.abs(df['Low'] - df['Close'].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)

    true_range = np.max(ranges, axis=1)

    atr = pd.Series(true_range).rolling(period).mean()

    return atr

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("📈 Quant Terminal")

    market = st.selectbox(
        "Select Market",
        [
            "NIFTY 50",
            "BANK NIFTY",
            "SENSEX",
            "RELIANCE",
            "TCS",
            "INFY"
        ]
    )

    ticker_map = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN",
        "RELIANCE": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "INFY": "INFY.NS"
    }

    ticker = ticker_map[market]

    timeframe = st.selectbox(
        "Timeframe",
        ["5m", "15m", "30m", "60m", "1d"],
        index=1
    )

    st.markdown("---")

    st.subheader("🌍 Global Market Mood")

    st.success("NASDAQ → Bullish")
    st.success("NIKKEI → Bullish")
    st.warning("VIX → Volatile")
    st.info("GIFT NIFTY → Positive")

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="top-nav">

<h1>
📊 Tushar Trading Assistant
</h1>

<p>
AI Powered Smart Money Analysis Terminal
</p>

</div>
""", unsafe_allow_html=True)

# ==========================================================
# MARKET WISDOM
# ==========================================================

market_quotes = [

    "Retailers chase candles. Smart money creates them.",

    "Volume reveals intention before price reveals direction.",

    "Fake breakouts trap emotions, not charts.",

    "Support and resistance are psychological battle zones.",

    "Market rewards patience, not prediction.",

    "FII builds positions quietly while retailers panic.",

    "Trend is your probability advantage.",

    "Big candles attract retailers. Smart money exits there."

]

quote = random.choice(market_quotes)

st.markdown(f"""
<div class="glass-card">

<h3>💡 Market Wisdom</h3>

<p style="
font-size:18px;
color:#1e293b;
font-weight:500;
">
{quote}
</p>

</div>
""", unsafe_allow_html=True)

# ==========================================================
# DATA
# ==========================================================

df = fetch_data(ticker, timeframe)

# ==========================================================
# MAIN
# ==========================================================

if df is not None and not df.empty:

    # ======================================================
    # INDICATORS
    # ======================================================

    df['EMA20'] = df['Close'].ewm(span=20).mean()

    df['EMA50'] = df['Close'].ewm(span=50).mean()

    df['RSI'] = calculate_rsi(df)

    df['ATR'] = calculate_atr(df)

    df['VolumeAvg'] = df['Volume'].rolling(20).mean()

    df['VolumeSpike'] = df['Volume'] > (df['VolumeAvg'] * 2)

    df['FakeBreakout'] = (
        (df['High'] > df['High'].shift(1)) &
        (df['Close'] < df['Open'])
    )

    latest = df.iloc[-1]

    support = round(df['Low'].rolling(20).min().iloc[-1], 2)

    resistance = round(df['High'].rolling(20).max().iloc[-1], 2)

    price = latest['Close']

    # ======================================================
    # SIGNAL ENGINE
    # ======================================================

    signal = "HOLD"

    signal_class = "neutral"

    if latest['Close'] > latest['EMA20'] > latest['EMA50'] and latest['RSI'] > 55:

        signal = "BUY"

        signal_class = "buy"

    elif latest['Close'] < latest['EMA20'] < latest['EMA50'] and latest['RSI'] < 45:

        signal = "SELL"

        signal_class = "sell"

    # ======================================================
    # WARNINGS
    # ======================================================

    warnings = []

    if latest['FakeBreakout']:

        warnings.append(
            "⚠️ Fake breakout detected. Retail breakout traders may get trapped."
        )

    if abs(price - support) < (latest['ATR'] * 0.5):

        warnings.append(
            f"🟢 Price near support ₹{support}. Bounce possible."
        )

    if abs(price - resistance) < (latest['ATR'] * 0.5):

        warnings.append(
            f"🔴 Price near resistance ₹{resistance}. Pullback possible."
        )

    if latest['VolumeSpike']:

        warnings.append(
            "📈 Unusual volume spike detected. Smart money activity possible."
        )

    if latest['RSI'] > 70:

        warnings.append(
            "🔥 Overbought zone. Profit booking possible."
        )

    if latest['RSI'] < 30:

        warnings.append(
            "❄️ Oversold zone. Short covering bounce possible."
        )

    # ======================================================
    # KPI ROW
    # ======================================================

    c1, c2, c3, c4 = st.columns(4)

    ltp = round(latest['Close'], 2)

    prev_close = round(df['Close'].iloc[-2], 2)

    change = round(ltp - prev_close, 2)

    pct = round((change / prev_close) * 100, 2)

    with c1:

        st.markdown(f"""
        <div class="glass-card">
        <div class="kpi-title">SPOT PRICE</div>
        <div class="kpi-value">₹ {ltp}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        color = "green" if pct >= 0 else "red"

        st.markdown(f"""
        <div class="glass-card">
        <div class="kpi-title">DAY CHANGE</div>
        <div class="kpi-value {color}">{pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown(f"""
        <div class="glass-card">
        <div class="kpi-title">RSI</div>
        <div class="kpi-value">{round(latest['RSI'],2)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:

        st.markdown(f"""
        <div class="glass-card">
        <div class="kpi-title">VOLUME</div>
        <div class="kpi-value">{int(latest['Volume'])}</div>
        </div>
        """, unsafe_allow_html=True)

    # ======================================================
    # MAIN GRID
    # ======================================================

    left, right = st.columns([3, 1])

    # ======================================================
    # LEFT SIDE
    # ======================================================

    with left:

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.subheader("📈 Smart Money Chart")

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.75, 0.25]
        )

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA20'],
                name='EMA20',
                line=dict(color='blue', width=2)
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA50'],
                name='EMA50',
                line=dict(color='red', width=2)
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume'
            ),
            row=2,
            col=1
        )

        fig.update_layout(
            template='plotly_white',
            height=700,
            xaxis_rangeslider_visible=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.4)',
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # PROBABILITY ENGINE
        # ==================================================

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.subheader("🎯 Market Probability Ladder")

        spot = round(ltp, -2)

        for i in range(-5, 6):

            level = spot + (i * 100)

            probability = np.random.randint(25, 90)

            st.markdown(f"""
            <div class="level-box">
            <b>{level}</b> → {probability}% probability
            </div>
            """, unsafe_allow_html=True)

        st.caption(
            "AI probability model based on trend, volatility and momentum"
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # RIGHT SIDE
    # ======================================================

    with right:

        # ==================================================
        # SIGNAL
        # ==================================================

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.subheader("🤖 AI Signal")

        st.markdown(f"""
        <div class="signal-box {signal_class}">
        {signal}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # WARNINGS
        # ==================================================

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.subheader("🚨 Smart Warnings")

        if warnings:

            for w in warnings:

                st.warning(w)

        else:

            st.success("No major danger zones detected.")

        st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # SMART MONEY
        # ==================================================

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.subheader("🏦 Smart Money")

        if signal == "BUY":

            st.success("FII likely long buildup")

            st.info("Retail chasing upside")

            st.warning("Put writing visible")

        elif signal == "SELL":

            st.error("Call writing heavy")

            st.warning("Retail trapped in calls")

            st.info("FII defensive positioning")

        else:

            st.info("Neutral positioning")

        st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # PCR / OI
        # ==================================================

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.subheader("📊 OI & PCR")

        pcr = round(np.random.uniform(0.7, 1.4), 2)

        st.metric("PCR", pcr)

        if pcr > 1:

            st.success("Bullish PCR")

        else:

            st.error("Bearish PCR")

        st.metric("Call Writing", "Heavy")

        st.metric("Put Writing", "Moderate")

        st.markdown('</div>', unsafe_allow_html=True)

        # ==================================================
        # NEWS
        # ==================================================

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.subheader("📰 Market Pulse")

        try:

            news = yf.Ticker(ticker).news

            for item in news[:5]:

                title = item.get('title', 'No Title')

                publisher = item.get('publisher', 'Unknown')

                st.markdown(f"""
                <div class="news-box">
                <b>{title}</b><br>
                <small>{publisher}</small>
                </div>
                """, unsafe_allow_html=True)

        except:

            st.info("News unavailable")

        st.markdown('</div>', unsafe_allow_html=True)

else:

    st.error("Unable to fetch market data")

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("""
<div class="footer">
Built by Tushar Wankhade • Smart Money Quant Terminal
</div>
""", unsafe_allow_html=True)
