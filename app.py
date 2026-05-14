import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# =====================================================
# 1. THEME & UI SETUP (Sky Blue & White)
# =====================================================
st.set_page_config(page_title="Tushar Quant Master", layout="wide")

st.markdown("""
<style>
    .stApp { background: #f8fafc; color: #1e293b; }
    .main-card { background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    h3 { color: #0369a1; font-size: 18px; margin-bottom: 10px; }
    .metric-box { text-align: center; padding: 10px; background: #f0f9ff; border-radius: 8px; border: 1px solid #e0f2fe; }
    .signal-buy { color: #15803d; font-weight: bold; background: #dcfce7; padding: 5px 10px; border-radius: 5px; }
    .signal-sell { color: #b91c1c; font-weight: bold; background: #fee2e2; padding: 5px 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 2. DATA ENGINE
# =====================================================
def get_market_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def get_signals(df):
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    high = df['High'].max()
    low = df['Low'].min()
    
    # Simple Price Action Logic
    if curr > prev and curr > df['Close'].tail(5).mean():
        return "CALL (BUY) 📈", "signal-buy", "Support कडे लक्ष द्या आणि रॅली राईड करा."
    elif curr < prev and curr < df['Close'].tail(5).mean():
        return "PUT (SELL) 📉", "signal-sell", "Resistance वर विक्रीचा दबाव आहे."
    return "WAIT ⚖️", "", "योग्य ब्रेकआउटची वाट पाहा."

# =====================================================
# 3. TOP SEARCH & HEADER
# =====================================================
col_h1, col_search = st.columns([2, 1])
with col_h1:
    st.markdown("# 🛡️ Tushar Quant Intelligence")
with col_search:
    search = st.text_input("🔍 स्टॉक सर्च करा (उदा. RELIANCE.NS)", placeholder="Enter Symbol...")

# =====================================================
# 4. 4-CHART GRID LAYOUT
# =====================================================
indices = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "GIFT NIFTY": "NQ=F" # Proxy for Gift Nifty (Nasdaq Futures) or use SGX symbols
}

row1 = st.columns(2)
row2 = st.columns(2)
all_cols = row1 + row2

for i, (name, sym) in enumerate(indices.items()):
    with all_cols[i]:
        df = get_market_data(sym)
        if df is not None:
            sig_text, sig_class, advice = get_signals(df)
            
            st.markdown(f'<div class="main-card">', unsafe_allow_html=True)
            st.markdown(f"### {name}")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Open", f"{df['Open'].iloc[0]:.2f}")
            m2.metric("High", f"{df['High'].max():.2f}")
            m3.metric("Low", f"{df['Low'].min():.2f}")
            m4.metric("LTP", f"{df['Close'].iloc[-1]:.2f}")

            # Chart
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                            increasing_line_color='#0ea5e9', decreasing_line_color='#ef4444')])
            fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Action Signal
            st.markdown(f"**ॲक्शन:** <span class='{sig_class}'>{sig_text}</span>", unsafe_allow_html=True)
            st.caption(f"💡 {advice}")
            st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# 5. SEARCH RESULT (IF ANY)
# =====================================================
if search:
    st.divider()
    st.subheader(f"🔍 सर्च रिझल्ट: {search}")
    s_df = get_market_data(search)
    if s_df is not None:
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            fig_s = go.Figure(data=[go.Candlestick(x=s_df.index, open=s_df['Open'], high=s_df['High'], low=s_df['Low'], close=s_df['Close'])])
            st.plotly_chart(fig_s, use_container_width=True)
        with col_s2:
            st.info(f"करंट प्राईस: {s_df['Close'].iloc[-1]:.2f}")
            st.write("येथे तुमची वैयक्तिक स्टॉक ॲनॅलिसिस रिपोर्ट दिसेल.")

st.markdown("---")
st.caption("टर्मिनल v10.0 | डेटा स्रोत: Yahoo Finance & Google Finance | सर्व माहिती शैक्षणिक उद्देशाने आहे.")
