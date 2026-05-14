import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. THEME: NEO-LIGHT INSTITUTIONAL UI ---
st.set_page_config(page_title="Tushar Zero-Hero Terminal", layout="wide")

st.markdown("""
    <style>
    /* Google Font Integration */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #fcfcfc; font-family: 'Inter', sans-serif; }

    /* Glassmorphism Header */
    .top-header {
        background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
        padding: 25px; border-radius: 15px; color: white;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.2);
        margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center;
    }

    /* Zero-Hero Alert Box */
    .zero-hero-box {
        background: #fff; border: 2px solid #e2e8f0; border-radius: 16px;
        padding: 20px; text-align: center; transition: 0.4s;
    }
    .hero-active { border: 2px solid #3b82f6; background: #eff6ff; animation: pulse 2s infinite; }
    
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); } 70% { box-shadow: 0 0 0 15px rgba(59, 130, 246, 0); } 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); } }

    /* Volume Spike Badge */
    .spike-badge { background: #fee2e2; color: #dc2626; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 11px; }
    
    /* Metrics Styling */
    .m-title { color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
    .m-val { font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #0f172a; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED DATA LOGIC (Volume & Expiry) ---
def get_advanced_data(symbol):
    ticker = "^NSEI" if "NIFTY" in symbol.upper() else symbol
    # Fetching smaller intervals for Volume Spike detection
    df = yf.download(ticker, period="2d", interval="5m", auto_adjust=True)
    if df.empty: return None
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

    # Volume Analysis
    avg_vol = df['Volume'].tail(20).mean()
    curr_vol = df['Volume'].iloc[-1]
    vol_spike = curr_vol > (avg_vol * 2.5) # 2.5x volume is a spike

    # RSI for Overbought/Oversold
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    return df, rsi, vol_spike, curr_vol, avg_vol

# --- 3. UI RENDERING ---

st.markdown("""
    <div class="top-header">
        <div>
            <h2 style="margin:0; font-family:'Space Grotesk';">TUSHAR QUANT TERMINAL</h2>
            <span style="opacity:0.8; font-size:13px;">ZERO-HERO EXPIRY RADAR ACTIVE</span>
        </div>
        <div style="text-align:right;">
            <div style="font-size:18px; font-weight:700;">""" + datetime.now().strftime("%d %b %Y") + """</div>
            <span style="color:#60a5fa;">Next Expiry: Weekly Thursday</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
symbol = st.sidebar.text_input("Asset (e.g. RELIANCE.NS)", "NIFTY50")
df_data = get_advanced_data(symbol)

if df_data:
    df, rsi, vol_spike, cv, av = df_data
    ltp = df['Close'].iloc[-1]

    # Row 1: Key Indicators
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="zero-hero-box"><p class="m-title">LTP</p><p class="m-val">₹{round(ltp,2)}</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="zero-hero-box"><p class="m-title">RSI (5M)</p><p class="m-val">{round(rsi,1)}</p></div>', unsafe_allow_html=True)
    with c3:
        spike_text = '<span class="spike-badge">SPIKE DETECTED!</span>' if vol_spike else '<span style="color:gray;">Normal</span>'
        st.markdown(f'<div class="zero-hero-box"><p class="m-title">VOL ANALYSIS</p><p class="m-val">{round(cv/av, 1)}x</p>{spike_text}</div>', unsafe_allow_html=True)
    with c4:
        # Zero-Hero Logic
        is_hero = (vol_spike and (rsi < 35 or rsi > 70))
        hero_class = "hero-active" if is_hero else ""
        hero_status = "🔥 POSSIBLITY" if is_hero else "WAITING..."
        st.markdown(f'<div class="zero-hero-box {hero_class}"><p class="m-title">ZERO-HERO</p><p class="m-val" style="color:#3b82f6;">{hero_status}</p></div>', unsafe_allow_html=True)

    # Row 2: Charting
    st.write("")
    col_chart, col_data = st.columns([2.5, 1])
    
    with col_chart:
        st.markdown('<div class="zero-hero-box" style="text-align:left;"><b>Institutional Flow (5 Min Chart)</b>', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_white", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_data:
        st.markdown('<div class="zero-hero-box" style="text-align:left;"><b>Expiry Trap Data</b>', unsafe_allow_html=True)
        st.write("Retailer Sentiment: **Panic Selling**")
        st.progress(85)
        st.write("FII Position: **Heavy Long**")
        st.progress(20)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("🎯 **ZERO-HERO STRATEGY**")
        if is_hero and rsi < 35:
            st.success(f"**BUY CALL:** Rebound at {round(ltp,2)} | Target: {round(ltp*1.01,2)}")
        elif is_hero and rsi > 70:
            st.error(f"**BUY PUT:** Trap at {round(ltp,2)} | Target: {round(ltp*0.99,2)}")
        else:
            st.info("No Volume + RSI divergence found. Wait for the 1:30 PM move.")
        
        st.markdown(f"""
            <div style="margin-top:20px; font-size:12px; color:gray;">
            <b>Day Range:</b> {round(df['Low'].min(),2)} - {round(df['High'].max(),2)}<br>
            <b>Volume Spike:</b> {'Yes' if vol_spike else 'No'}
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("Please enter a valid ticker to analyze.")
