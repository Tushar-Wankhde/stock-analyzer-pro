import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- १. CSS फॉर डार्क थीम आणि प्रोफेशनल लुक ---
st.set_page_config(page_title="Tushar Stock Pro", layout="wide")

# FIX: येथे unsafe_allow_html=True वापरले आहे
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div.stButton > button:first-child {
        background-color: #00ffcc; color: black; border-radius: 10px; border: none;
        font-weight: bold; width: 100%; height: 50px;
    }
    .stTextInput > div > div > input { background-color: #262730; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- २. निफ्टी ५० स्टॉक लिस्ट ---
nifty50_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
    "HINDUNILVR.NS", "SBI.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS"
]

# --- ३. Sidebar Layout ---
st.sidebar.title("🔍 Market Scanner")
selected_stock = st.sidebar.selectbox("Nifty 50 मधून निवडा:", nifty50_stocks)
search_stock = st.sidebar.text_input("किंवा सर्च करा (उदा. TATAMOTORS.NS):")

ticker = search_stock if search_stock else selected_stock

# --- ४. डेटा फेचिंग ---
try:
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        data = df.copy()
        
        # इंडिकेटर्स
        data['MA20'] = data['Close'].rolling(window=20).mean()
        std_dev = data['Close'].rolling(window=20).std()
        data['Upper'] = data['MA20'] + (std_dev * 2)
        data['Lower'] = data['MA20'] - (std_dev * 2)
        
        cp = float(data['Close'].iloc[-1])
        up = float(data['Upper'].iloc[-1])
        lp = float(data['Lower'].iloc[-1])

        # --- ५. व्हिज्युअलायझेशन ---
        st.title(f"📊 {ticker} Analysis")
        m1, m2, m3 = st.columns(3)
        m1.metric("LTP", f"₹{round(cp, 2)}")
        m2.metric("Resistance", f"₹{round(up, 2)}")
        m3.metric("Support", f"₹{round(lp, 2)}")

        # कँडलस्टिक चार्ट
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                   low=data['Low'], close=data['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], line=dict(color='cyan', width=1), name="Upper Band"))
        fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], line=dict(color='magenta', width=1), name="Lower Band"))
        
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # --- ६. Signal Box ---
        st.markdown("---")
        if cp <= lp:
            st.success("🚀 BUY SIGNAL: स्टॉक सपोर्टवर आहे.")
        elif cp >= up:
            st.error("📉 SELL SIGNAL: स्टॉक रेझिस्टन्सवर आहे.")
        else:
            st.info("⏳ HOLD: स्टॉक सध्या रेंजमध्ये आहे.")

    else:
        st.error("स्टॉक सापडला नाही.")

except Exception as e:
    st.error(f"Error: {e}")
