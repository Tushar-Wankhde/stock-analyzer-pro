import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Tushar Stock Analyzer", layout="wide")
st.title("🚀 Tushar's Advance Market Analyzer")

ticker = st.sidebar.text_input("NSE Ticker (उदा. SBIN.NS)", "RELIANCE.NS")
data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)

if not data.empty:
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['Upper'] = data['MA20'] + (data['Close'].rolling(window=20).std() * 2)
    data['Lower'] = data['MA20'] - (data['Close'].rolling(window=20).std() * 2)
    
    current_price = float(data['Close'].iloc[-1])
    st.metric(f"LTP: {ticker}", f"₹{round(current_price, 2)}")

    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], 
                high=data['High'], low=data['Low'], close=data['Close'], name="Market")])
    fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], line=dict(color='red', width=1), name="Upper Band"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], line=dict(color='green', width=1), name="Lower Band"))
    st.plotly_chart(fig, use_container_width=True)
    
    if current_price <= data['Lower'].iloc[-1]:
        st.success("🔥 BUY SIGNAL: Stock is at Support (Lower Band)")
    elif current_price >= data['Upper'].iloc[-1]:
        st.error("📉 SELL SIGNAL: Stock is at Resistance (Upper Band)")
    else:
        st.info("⏳ NEUTRAL: No clear signal")
else:
    st.warning("Data not found. Use .NS for Indian stocks.")