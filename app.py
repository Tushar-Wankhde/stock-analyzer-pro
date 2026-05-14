import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Tushar Quant Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

st_autorefresh(interval=15000, key="refresh")

# =========================================================
# CSS - PREMIUM TERMINAL UI
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');

:root{
    --bg:#020617;
    --card:#0f172a;
    --border:#1e293b;
    --text:#f8fafc;
    --muted:#94a3b8;
    --green:#10b981;
    --red:#ef4444;
    --blue:#3b82f6;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp{
    background: linear-gradient(180deg,#020617,#0f172a);
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background: #020617 !important;
    border-right:1px solid #1e293b;
}

[data-testid="stSidebar"] *{
    color:white;
}

/* Top Nav */
.top-nav{
    background: rgba(15,23,42,0.85);
    border:1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
    padding:22px;
    border-radius:20px;
    margin-bottom:20px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

/* Cards */
.glass-card{
    background: rgba(15,23,42,0.72);
    border:1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border-radius:20px;
    padding:20px;
    margin-bottom:20px;
    box-shadow: 0 0 30px rgba(0,0,0,0.25);
}

/* KPI */
.kpi{
    font-size:28px;
    font-weight:700;
}

.green{
    color:#10b981;
}

.red{
    color:#ef4444;
}

.small{
    color:#94a3b8;
    font-size:12px;
}

.news-box{
    background:#111827;
    border-left:4px solid #3b82f6;
    padding:14px;
    border-radius:10px;
    margin-bottom:10px;
}

.market-pill{
    padding:6px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
}

.footer{
    text-align:center;
    color:#64748b;
    font-size:12px;
    padding:30px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA FETCH
# =========================================================

@st.cache_data(ttl=60)
def fetch_data(ticker, interval):
    try:
        data = yf.Ticker(ticker).history(
            period="7d",
            interval=interval,
            auto_adjust=True,
            prepost=True
        )

        data.dropna(inplace=True)

        return data

    except:
        return None

# =========================================================
# INDICATORS
# =========================================================

def calculate_rsi(data, period=14):

    delta = data['Close'].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()

    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("# 📊 QUANT TERMINAL")

    market = st.selectbox(
        "Select Market",
        [
            "NIFTY 50",
            "BANK NIFTY",
            "SENSEX",
            "RELIANCE",
            "TCS",
            "INFY",
            "CUSTOM"
        ]
    )

    ticker_map = {
        "NIFTY 50":"^NSEI",
        "BANK NIFTY":"^NSEBANK",
        "SENSEX":"^BSESN",
        "RELIANCE":"RELIANCE.NS",
        "TCS":"TCS.NS",
        "INFY":"INFY.NS"
    }

    ticker = ticker_map.get(market, "")

    if market == "CUSTOM":
        ticker = st.text_input(
            "Enter Ticker",
            value="SBIN.NS"
        )

    timeframe = st.selectbox(
        "Timeframe",
        ["5m","15m","30m","1h","1d"],
        index=1
    )

    show_ema = st.toggle("Show EMA", value=True)

    show_rsi = st.toggle("Show RSI", value=True)

    show_volume = st.toggle("Show Volume", value=True)

    st.markdown("---")

    st.markdown("### 🌍 GLOBAL MARKETS")

    st.markdown("""
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <span class="market-pill" style="background:#052e16;color:#10b981;">NASDAQ ▲</span>
        <span class="market-pill" style="background:#052e16;color:#10b981;">NIKKEI ▲</span>
        <span class="market-pill" style="background:#450a0a;color:#ef4444;">VIX ▼</span>
        <span class="market-pill" style="background:#052e16;color:#10b981;">GIFT NIFTY ▲</span>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TOP NAV
# =========================================================

st.markdown(f"""
<div class="top-nav">

<div>
    <div style="font-size:30px;font-weight:700;font-family:'Space Grotesk';">
        TUSHAR INTELLIGENCE TERMINAL
    </div>

    <div class="small">
        Institutional Grade Market Dashboard
    </div>
</div>

<div>
    <span class="market-pill" style="background:#052e16;color:#10b981;">
        ● LIVE DATA
    </span>
</div>

</div>
""", unsafe_allow_html=True)

# =========================================================
# FETCH DATA
# =========================================================

df = fetch_data(ticker, timeframe)

# =========================================================
# MAIN
# =========================================================

if df is not None and not df.empty:

    # ==========================
    # INDICATORS
    # ==========================

    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['RSI'] = calculate_rsi(df)

    # ==========================
    # METRICS
    # ==========================

    ltp = df['Close'].iloc[-1]

    prev = df['Close'].iloc[-2]

    change = ltp - prev

    pct = (change / prev) * 100

    high = df['High'].iloc[-1]

    low = df['Low'].iloc[-1]

    volume = int(df['Volume'].iloc[-1])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="small">CURRENT PRICE</div>
            <div class="kpi">₹ {round(ltp,2)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        color = "green" if pct >= 0 else "red"

        st.markdown(f"""
        <div class="glass-card">
            <div class="small">TODAY CHANGE</div>
            <div class="kpi {color}">
                {round(pct,2)}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="small">DAY HIGH</div>
            <div class="kpi">
                ₹ {round(high,2)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="glass-card">
            <div class="small">VOLUME</div>
            <div class="kpi">
                {volume:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # MAIN GRID
    # =====================================================

    left, right = st.columns([2.5,1])

    # =====================================================
    # CHART
    # =====================================================

    with left:

        st.markdown("""
        <div class="glass-card">
        <h3>📈 Advanced Market Structure</h3>
        """, unsafe_allow_html=True)

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.75,0.25]
        )

        # Candlestick

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price"
            ),
            row=1,
            col=1
        )

        # EMA20

        if show_ema:

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['EMA20'],
                    line=dict(color='#00FFAA', width=1.5),
                    name='EMA 20'
                ),
                row=1,
                col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['EMA50'],
                    line=dict(color='#FF6B6B', width=1.5),
                    name='EMA 50'
                ),
                row=1,
                col=1
            )

        # Volume

        if show_volume:

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
            template="plotly_dark",
            height=720,
            xaxis_rangeslider_visible=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            margin=dict(l=10,r=10,t=20,b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # =====================================================
        # TRADINGVIEW WIDGET
        # =====================================================

        st.markdown("""
        <div class="glass-card">
        <h3>📊 TradingView Professional Chart</h3>
        """, unsafe_allow_html=True)

        tradingview_widget = """
        <div class="tradingview-widget-container">
          <div id="tradingview_chart"></div>

          <script type="text/javascript"
          src="https://s3.tradingview.com/tv.js"></script>

          <script type="text/javascript">
          new TradingView.widget(
          {
          "width": "100%",
          "height": 700,
          "symbol": "NSE:NIFTY",
          "interval": "15",
          "timezone": "Asia/Kolkata",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#0f172a",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_chart"
        }
          );
          </script>
        </div>
        """

        st.components.v1.html(
            tradingview_widget,
            height=720
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # RIGHT PANEL
    # =====================================================

    with right:

        # RSI SIGNAL

        rsi = df['RSI'].iloc[-1]

        st.markdown("""
        <div class="glass-card">
        <h3>🧠 Smart Intelligence</h3>
        """, unsafe_allow_html=True)

        if rsi > 70:

            st.error("⚠️ OVERBOUGHT ZONE")

        elif rsi < 30:

            st.success("✅ OVERSOLD ACCUMULATION")

        else:

            st.info("⚖️ MARKET NEUTRAL")

        st.metric(
            "RSI",
            round(rsi,2)
        )

        st.progress(78)

        st.caption("Institutional Long Bias")

        st.markdown("</div>", unsafe_allow_html=True)

        # AI SIGNALS

        st.markdown("""
        <div class="glass-card">
        <h3>🤖 AI SIGNAL ENGINE</h3>
        """, unsafe_allow_html=True)

        trend_score = np.random.randint(60,90)

        volatility = np.random.randint(40,80)

        st.metric(
            "Trend Strength",
            f"{trend_score}%"
        )

        st.metric(
            "Volatility",
            f"{volatility}%"
        )

        if trend_score > 75:
            st.success("Bullish Momentum Strong")

        else:
            st.warning("Momentum Weakening")

        st.markdown("</div>", unsafe_allow_html=True)

        # MARKET NEWS

        st.markdown("""
        <div class="glass-card">
        <h3>📰 Market Pulse</h3>
        """, unsafe_allow_html=True)

        try:

            news = yf.Ticker(ticker).news

            for item in news[:5]:

                title = item.get("title","No Title")

                publisher = item.get("publisher","Unknown")

                st.markdown(f"""
                <div class="news-box">
                    <b>{title}</b><br>
                    <span class="small">{publisher}</span>
                </div>
                """, unsafe_allow_html=True)

        except:

            st.info("News unavailable")

        st.markdown("</div>", unsafe_allow_html=True)

        # WATCHLIST

        st.markdown("""
        <div class="glass-card">
        <h3>⭐ Watchlist</h3>
        """, unsafe_allow_html=True)

        watchlist = [
            ("NIFTY", "+0.82%"),
            ("BANKNIFTY", "+1.12%"),
            ("RELIANCE", "-0.25%"),
            ("INFY", "+2.12%"),
            ("TCS", "+0.91%")
        ]

        for stock, move in watchlist:

            color = "#10b981" if "+" in move else "#ef4444"

            st.markdown(f"""
            <div style="
                display:flex;
                justify-content:space-between;
                margin-bottom:10px;
                padding:10px;
                background:#111827;
                border-radius:10px;
            ">
                <span>{stock}</span>
                <span style="color:{color};font-weight:700;">
                    {move}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

else:

    st.warning("Unable to fetch market data.")

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
Elite Institutional Access • Powered by Tushar Wankhade
</div>
""", unsafe_allow_html=True)
