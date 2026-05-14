import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- १. CSS फॉर डार्क थीम आणि प्रोफेशनल लुक ---
st.set_page_config(page_title="Tushar Stock Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div.stButton > button:first-child {
        background-color: #00ffcc; color: black; border-radius: 10px; border: none;
        font-weight: bold; width: 100%; height: 50px;
    }
    .stTextInput > div > div > input { background-color: #262730; color: white; border-radius: 10px; }
    .css-1n76uvr { border: 1px solid #00ffcc; border-radius: 10px; padding: 20px; }
    </style>
    """, unsafe_allow_input=True)

# --- २. निफ्टी ५० स्टॉक लिस्ट ---
nifty50_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
    "HINDUNILVR.NS", "SBI.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS"
]

# --- ३. Sidebar Layout ---
st.sidebar.title("🔍 Market Scanner")
selected_stock = st.sidebar.selectbox("Nifty 50 मधून निवडा:", nifty50_stocks)
search_stock = st.sidebar.text_input("किंवा कोणताही स्टॉक सर्च करा (उदा. TATAMOTORS.NS):")

# फायनल टिकर ठरवणे
ticker = search_stock if search_stock else selected_stock

# --- ४. डेटा फेचिंग आणि प्रॉसेसिंग ---
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
        
        # लेटेस्ट डेटा
        cp = float(data['Close'].iloc[-1])
        up = float(data['Upper'].iloc[-1])
        lp = float(data['Lower'].iloc[-1])
        change = cp - float(data['Close'].iloc[-2])

        # --- ५. विझ्युअलायझेशन (Metrics) ---
        st.title(f"📊 {ticker} Analysis")
        m1, m2, m3 = st.columns(3)
        m1.metric("LTP", f"₹{round(cp, 2)}", f"{round(change, 2)}")
        m2.metric("Resistance (Upper)", f"₹{round(up, 2)}")
        m3.metric("Support (Lower)", f"₹{round(lp, 2)}")

        # --- ६. कँडलस्टिक चार्ट (Dark Theme) ---
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                   low=data['Low'], close=data['Close'], name="Market Price"))
        fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], line=dict(color='cyan', width=1), name="Resistance"))
        fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], line=dict(color='magenta', width=1), name="Support"))
        
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False,
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # --- ७. Strategy Signal Box ---
        st.markdown("---")
        st.subheader("🛠 Trading Strategy Signal")
        
        if cp <= lp:
            st.markdown(f'<div style="background-color:#1e3d2f; padding:20px; border-radius:10px; border:2px solid #00ffcc;">'
                        f'<h3 style="color:#00ffcc; margin:0;">🚀 BUY SIGNAL (Oversold)</h3>'
                        f'<p style="color:white;">स्टॉक सपोर्ट लेव्हलवर आहे. इथून बाऊन्स बॅक होण्याची शक्यता जास्त आहे.</p></div>', unsafe_allow_html=True)
        elif cp >= up:
            st.markdown(f'<div style="background-color:#3d1e1e; padding:20px; border-radius:10px; border:2px solid #ff4b4b;">'
                        f'<h3 style="color:#ff4b4b; margin:0;">📉 SELL SIGNAL (Overbought)</h3>'
                        f'<p style="color:white;">स्टॉक रेझिस्टन्स लेव्हलवर आहे. प्रॉफिट बुकिंग येऊ शकते.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color:#1e263d; padding:20px; border-radius:10px; border:2px solid #1e90ff;">'
                        f'<h3 style="color:#1e90ff; margin:0;">⏳ HOLD / NEUTRAL</h3>'
                        f'<p style="color:white;">स्टॉक सध्या रेंजमध्ये आहे. ब्रेकआऊटची वाट पहा.</p></div>', unsafe_allow_html=True)

        # --- ८. OI Data (Simulated for visualization) ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("💎 Option Chain (OI) Stats")
        st.sidebar.write("PCR Ratio: 0.85 (Neutral)")
        st.sidebar.write("Max Pain: 22400")

    else:
        st.error("स्टॉक सापडला नाही. कृपया NSE टिकर नीट तपासा.")

except Exception as e:
    st.error(f"Error: {e}")
