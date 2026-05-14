import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Page Config
st.set_page_config(page_title="Tushar Stock Analyzer", layout="wide")
st.title("🚀 Tushar's Advance Market Analyzer")

# Sidebar
ticker = st.sidebar.text_input("NSE Ticker (उदा. SBIN.NS)", "RELIANCE.NS")

# Data fetching
try:
    # auto_adjust=True आणि .copy() वापरल्याने डेटा स्ट्रक्चर नीट राहते
    raw_data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    
    if not raw_data.empty:
        # डेटाला साध्या फॉरमॅटमध्ये आणण्यासाठी (Fix for multi-index error)
        data = raw_data.copy()
        
        # इंडिकेटर्स कॅल्क्युलेशन (अचूक पद्धत)
        data['MA20'] = data['Close'].rolling(window=20).mean()
        std_dev = data['Close'].rolling(window=20).std()
        data['Upper'] = data['MA20'] + (std_dev * 2)
        data['Lower'] = data['MA20'] - (std_dev * 2)
        
        # लेटेस्ट व्हॅल्यूज मिळवणे
        current_price = float(data['Close'].iloc[-1])
        latest_upper = float(data['Upper'].iloc[-1])
        latest_lower = float(data['Lower'].iloc[-1])

        # डिस्प्ले मेट्रिक्स
        st.metric(f"LTP: {ticker}", f"₹{round(current_price, 2)}")

        # चार्ट तयार करणे
        fig = go.Figure()
        # Candlestick
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], 
                    high=data['High'], low=data['Low'], close=data['Close'], name="Price"))
        # Bollinger Bands
        fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], line=dict(color='rgba(255, 0, 0, 0.4)'), name="Upper Band"))
        fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], line=dict(color='rgba(0, 255, 0, 0.4)'), name="Lower Band"))
        
        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # स्मार्ट सिग्नल्स
        st.subheader("📊 Analysis Signal")
        if current_price <= latest_lower:
            st.success("🔥 BUY SIGNAL: स्टॉक सपोर्ट लेव्हलवर (Lower Band) आहे.")
        elif current_price >= latest_upper:
            st.error("📉 SELL SIGNAL: स्टॉक रेझिस्टन्स लेव्हलवर (Upper Band) आहे.")
        else:
            st.info("⏳ NEUTRAL: सध्या कोणताही मोठा मूव्ह दिसत नाही.")
            
    else:
        st.warning("डेटा मिळाला नाही. कृपया टिकर तपासा (उदा. शेवटी .NS लावा).")

except Exception as e:
    st.error(f"Error occurred: {e}")
