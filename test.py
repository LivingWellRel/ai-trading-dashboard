"""
Simple Test Version - AI Trading Dashboard
This is a minimal version to test deployment
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="🚀 AI Trading Dashboard - Test",
    page_icon="📈",
    layout="wide"
)

def main():
    st.markdown("""
    # 🚀 AI Trading Dashboard
    ## Test Version - Deployment Check
    
    **Status:** ✅ Application is running successfully!
    
    **Timestamp:** {current_time}
    """.format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    # Simple stock price checker
    st.markdown("### 📈 Quick Stock Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Enter Stock Symbol", value="AAPL", key="test_ticker")
    
    with col2:
        if st.button("Get Price", key="get_price"):
            if ticker:
                try:
                    with st.spinner(f"Getting {ticker} price..."):
                        stock = yf.Ticker(ticker)
                        data = stock.history(period="1d")
                        
                        if not data.empty:
                            current_price = data['Close'].iloc[-1]
                            prev_close = data['Close'].iloc[0] if len(data) > 1 else current_price
                            change = current_price - prev_close
                            change_pct = (change / prev_close) * 100 if prev_close > 0 else 0
                            
                            st.success(f"""
                            **{ticker.upper()}**
                            - Current Price: ${current_price:.2f}
                            - Change: ${change:+.2f} ({change_pct:+.2f}%)
                            """)
                        else:
                            st.error(f"❌ Could not fetch data for {ticker}")
                            
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Test chart
    st.markdown("### 📊 Sample Chart")
    
    try:
        # Create a simple test chart
        test_data = yf.download("AAPL", period="1mo")
        
        if not test_data.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=test_data.index,
                y=test_data['Close'],
                mode='lines',
                name='AAPL Price',
                line=dict(color='#00d4aa', width=2)
            ))
            
            fig.update_layout(
                title="AAPL - Last 30 Days",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Sample chart data not available")
            
    except Exception as e:
        st.error(f"❌ Chart error: {e}")
    
    # System info
    st.markdown("### ⚙️ System Information")
    
    st.markdown(f"""
    **Deployment Info:**
    - Python packages: ✅ Loaded successfully  
    - Streamlit: ✅ Running
    - yfinance: ✅ Available
    - plotly: ✅ Working
    - Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
    
    **Next Steps:**
    If you can see this page, the deployment is working. The full dashboard should load from `main.py`.
    """)
    
    # Link to full dashboard
    st.markdown("---")
    st.markdown("""
    ### 🔗 Navigation
    - **Current:** Test Version (test.py)
    - **Full Dashboard:** Should load automatically from main.py
    - **Local Version:** http://localhost:8506 (if running locally)
    """)

if __name__ == "__main__":
    main()
