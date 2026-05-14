import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- १. Page Config & Professional UI ---
st.set_page_config(page_title="Tushar Pro Terminal", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    .news-card { background-color: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; margin-bottom: 10px; }
    .buy-signal { background-color: #1e3d2f; color: #00ffcc; padding: 15px; border-radius: 10px; border: 1px solid #00ffcc; }
    .sell-signal { background-color: #3d1e1e; color: #ff4b4b; padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- २. Sidebar: Inputs & Nifty 50 List ---
nifty50_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", "BAJFINANCE.NS", "TATAMOTORS.NS"] # मोजके महत्वाचे किंवा पूर्ण लिस्ट

st.sidebar.title("🚀 Tushar Pro Terminal")
selected_stock = st.sidebar.selectbox("Market Watch", sorted(nifty50_list))
search_ticker = st.sidebar.text_input("Search Symbol (उदा. IRFC.NS)")
ticker = search_ticker if search_ticker else selected_stock

# --- ३. Indicators Calculation Logic ---
def get_indicators(data):
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['Upper'] = data['MA20'] + (data['Close'].rolling(window=20).std() * 2)
    data['Lower'] = data['MA20'] - (data['Close'].rolling(window=20).std() * 2)
    return data

# --- ४. Main Dashboard Layout ---
col_main, col_news = st.columns([3, 1])

with col_main:
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            data = get_indicators(df.copy())
            
            cp = float(data['Close'].iloc[-1])
            rsi = float(data['RSI'].iloc[-1])
            macd = float(data['MACD'].iloc[-1])
            signal = float(data['Signal_Line'].iloc[-1])
            
            st.title(f"📊 {ticker} Live Analysis")
            
            # Top Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("LTP", f"₹{round(cp, 2)}")
            m2.metric("RSI (14)", f"{round(rsi, 2)}")
            m3.metric("MACD", f"{round(macd, 2)}")
            m4.metric("Trend", "Bullish" if macd > signal else "Bearish")

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], line=dict(color='rgba(0, 255, 204, 0.3)'), name="Upper Band"))
            fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], line=dict(color='rgba(255, 75, 75, 0.3)'), name="Lower Band"))
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

            # Signal Generation Based on RSI & MACD
            st.subheader("🛠 Expert Trading Signal")
            if rsi < 35 and macd > signal:
                st.markdown('<div class="buy-signal">🚀 STRONG BUY: RSI Oversold + MACD Bullish Crossover!</div>', unsafe_allow_html=True)
            elif rsi > 65 and macd < signal:
                st.markdown('<div class="sell-signal">📉 STRONG SELL: RSI Overbought + MACD Bearish Crossover!</div>', unsafe_allow_html=True)
            else:
                st.info("⏳ HOLD: No High-Conviction Signal currently.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

# --- ५. Live News Section ---
with col_news:
    st.subheader("📰 Market News")
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:5] # Latest 5 news items
        for item in news:
            st.markdown(f"""
                <div class="news-card">
                    <small>{datetime.fromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d')}</small><br>
                    <strong>{item['title']}</strong><br>
                    <a href="{item['link']}" target="_blank" style="color:#00ffcc; text-decoration:none;">Read More...</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.write("News currently unavailable.")

# --- ६. Market Trend (Bottom Section) ---
st.markdown("---")
st.subheader("🌐 Global Market Trend")
t1, t2, t3 = st.columns(3)
t1.write("**Nifty 50:** Neutral")
t2.write("**RSI Status:** Normal")
t3.write("**VIX:** Low Volatility")
