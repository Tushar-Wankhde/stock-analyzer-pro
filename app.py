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
    # 1. डेटा डाउनलोड करा
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    
    if not df.empty:
        # 2. FIX: जर डेटा Multi-index असेल (उदा. ('Close', 'RELIANCE.NS')), तर त्याला साध्या स्वरूपात आणा
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 3. डेटाची कॉपी घ्या जेणेकरून कॅल्क्युलेशन सोपे होईल
        data = df.copy()
        
        # 4. इंडिकेटर्स कॅल्क्युलेशन
        data['MA20'] = data['Close'].rolling(window=20).mean()
        std_dev = data['Close'].rolling(window=20).std()
        data['Upper'] = data['MA20'] + (std_dev * 2)
        data['Lower'] = data['MA20'] - (std_dev * 2)
        
        # 5. लेटेस्ट किमती मिळवणे
        current_price = float(data['Close'].iloc[-1])
        latest_upper = float(data['Upper'].iloc[-1])
        latest_lower = float(data['Lower'].iloc[-1])

        # डिस्प्ले
        st.metric(f"LTP: {ticker}", f"₹{round(current_price, 2)}")

        # 6. प्रोफेशनल चार्ट
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, 
                    open=data['Open'], high=data['High'], 
                    low=data['Low'], close=data['Close'], name="Price"))
        
        fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], 
                    line=dict(color='rgba(255, 0, 0, 0.5)'), name="Upper Band"))
        fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], 
                    line=dict(color='rgba(0, 255, 0, 0.5)'), name="Lower Band"))
        
        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # 7. सिग्नल्स
        st.subheader("📊 Expert Signal")
        if current_price <= latest_lower:
            st.success("🔥 BUY SIGNAL: स्टॉक सपोर्ट लेव्हलवर (Lower Band) आहे. रिव्हर्सलची शक्यता आहे!")
        elif current_price >= latest_upper:
            st.error("📉 SELL SIGNAL: स्टॉक रेझिस्टन्स लेव्हलवर (Upper Band) आहे. प्रॉफिट बुकिंग येऊ शकते.")
        else:
            st.info("⏳ NEUTRAL: स्टॉक सध्या चॅनेलच्या मध्यभागी आहे. योग्य संधीची वाट पहा.")
            
    else:
        st.warning("डेटा मिळाला नाही. कृपया टिकर तपासा (उदा. शेवटी .NS लावा).")

except Exception as e:
    st.error(f"Error occurred: {e}")
