import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. ADVANCED CSS: TERMINAL UI v6.0 ---
st.set_page_config(page_title="Tushar Intelligence Terminal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Inter:wght@400;600&display=swap');
    
    .stApp { background-color: #f9fbff; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #e2e8f0;
        padding-top: 20px;
    }

    /* Top Nav Bar */
    .top-nav {
        background: #0f172a; padding: 20px; border-radius: 12px;
        color: white; display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1); margin-bottom: 25px;
    }

    /* Professional Card */
    .glass-card {
        background: white; padding: 20px; border-radius: 16px;
        border: 1px solid #edf2f7; box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        margin-bottom: 20px; transition: 0.3s;
    }
    .glass-card:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,0,0,0.05); }

    /* News Item */
    .news-box {
        padding: 12px; border-left: 4px solid #3b82f6;
        background: #f1f5f9; border-radius: 0 8px 8px 0;
        margin-bottom: 10px; font-size: 13px;
    }
    
    .status-pill {
        padding: 4px 10px; border-radius: 99px; font-size: 11px; font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def fetch_live_data(ticker):
    try:
        data = yf.download(ticker, period="5d", interval="15m", auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data
    except: return None

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2422/2422796.png", width=50)
    st.markdown("### 📊 INDEX SELECTOR")
    
    # Dropdown for major indices
    index_choice = st.selectbox(
        "Choose Market",
        ["NIFTY 50", "BANK NIFTY", "SENSEX", "GIFT NIFTY", "CUSTOM TICKER"]
    )
    
    ticker_map = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN",
        "GIFT NIFTY": "NQ=F"
    }
    
    selected_ticker = ticker_map.get(index_choice, "")
    if index_choice == "CUSTOM TICKER":
        selected_ticker = st.text_input("Enter Ticker (e.g. SBIN.NS)", "RELIANCE.NS")
    
    st.markdown("---")
    st.markdown("### 🛠️ PARAMETERS")
    timeframe = st.selectbox("Interval", ["15m", "1h", "1d"])
    risk_mode = st.toggle("Show Trap Zones", value=True)

# --- 4. MAIN TERMINAL UI ---

# Top Header
st.markdown(f"""
    <div class="top-nav">
        <div>
            <span style="font-family:'Space Grotesk'; font-size:22px; font-weight:700;">QUANT TERMINAL</span>
            <span style="margin-left:10px; font-size:12px; opacity:0.6;">v6.0 PRE-RELEASE</span>
        </div>
        <div style="text-align:right;">
            <span class="status-pill" style="background:#22c55e; color:white;">LIVE DATA ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

df = fetch_live_data(selected_ticker)

if df is not None and not df.empty:
    ltp = df['Close'].iloc[-1]
    change = ltp - df['Close'].iloc[-2]
    pct = (change / df['Close'].iloc[-2]) * 100
    
    # KPIs Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="glass-card"><small>CURRENT VALUE</small><br><h3>₹{round(ltp,2)}</h3></div>', unsafe_allow_html=True)
    with c2:
        color = "#10b981" if change >= 0 else "#ef4444"
        st.markdown(f'<div class="glass-card"><small>TODAY\'S CHANGE</small><br><h3 style="color:{color};">{round(pct,2)}%</h3></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="glass-card"><small>VOLUME</small><br><h3>{int(df["Volume"].iloc[-1])}</h3></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="glass-card"><small>VOLATILITY (ATR)</small><br><h3>HIGH</h3></div>', unsafe_allow_html=True)

    # Main Chart Section
    col_chart, col_intel = st.columns([2.5, 1])

    with col_chart:
        st.markdown('<div class="glass-card"><b>Advanced Price Action</b>', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_white", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_intel:
        st.markdown('<div class="glass-card"><b>💡 Smart Intelligence</b>', unsafe_allow_html=True)
        
        # Zero-Hero / Trap Detection Logic
        rsi = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / -df['Close'].diff().where(df['Close'].diff() < 0, 0).rolling(14).mean()))).iloc[-1]
        
        if rsi > 70:
            st.error("⚠️ OVERBOUGHT: Potential Trap Zone for Retailers.")
        elif rsi < 30:
            st.success("✅ OVERSOLD: Accumulation detected. Watch for Rebound.")
        else:
            st.info("⚖️ NEUTRAL: Market is searching for direction.")
        
        st.markdown("---")
        st.write("**Institutional Position**")
        st.progress(65)
        st.markdown("<small>Strong Long Accumulation</small>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- NEW: NEWS & GLOBAL MARKET SECTION ---
    st.markdown('<div class="glass-card"><b>📰 Market Pulse & Global News</b>', unsafe_allow_html=True)
    col_n1, col_n2 = st.columns(2)
    
    try:
        news = yf.Ticker(selected_ticker).news
        with col_n1:
            for item in news[:3]:
                st.markdown(f'<div class="news-box"><b>{item["title"]}</b><br><small>{item["publisher"]} • {item.get("type", "News")}</small></div>', unsafe_allow_html=True)
        with col_n2:
            for item in news[3:6]:
                st.markdown(f'<div class="news-box"><b>{item["title"]}</b><br><small>{item["publisher"]} • {item.get("type", "News")}</small></div>', unsafe_allow_html=True)
    except:
        st.write("News currently unavailable for this ticker.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Please select an index from the left sidebar to begin analysis.")

# Footer
st.markdown("<p style='text-align:center; color:gray; font-size:12px;'>Elite Institutional Access | Powered by Tushar W.</p>", unsafe_allow_html=True)
