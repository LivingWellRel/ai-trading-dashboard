import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="🚀 AI Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f4e79, #2e8b57);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    
    .buy-signal {
        background: #00d4aa;
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sell-signal {
        background: #ff4b4b;
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem;
        }
        .main-header p {
            font-size: 0.9rem;
        }
        .metric-card {
            margin: 0.25rem 0;
            padding: 0.75rem;
        }
        
        .stButton button {
            height: 48px;
            font-size: 16px;
            border-radius: 8px;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Trading Dashboard</h1>
        <p>Live Technical Analysis • Portfolio Management • Smart Alerts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo data
    demo_stocks = ['PLTR', 'NVDA', 'O', 'AGNC', 'AAPL', 'TSLA', 'SPY']
    demo_prices = [18.25, 275.50, 58.25, 13.75, 175.50, 185.25, 485.75]
    demo_changes = [2.34, -1.8, 1.2, 0.8, -0.5, 3.2, 0.9]
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Live Charts", 
        "💼 Portfolio", 
        "📈 Trade Log", 
        "📋 Watchlist", 
        "🏦 Roth IRA"
    ])
    
    with tab1:
        show_live_charts(demo_stocks, demo_prices, demo_changes)
    
    with tab2:
        show_portfolio()
    
    with tab3:
        show_trade_log()
    
    with tab4:
        show_watchlist()
    
    with tab5:
        show_roth_ira()
    
    # Sidebar controls
    st.sidebar.markdown("## 🎤 Voice Commands")
    if st.sidebar.button("🎙️ Start Voice Command", key="voice_btn"):
        st.sidebar.success("Voice command feature ready! (Demo mode)")
        st.sidebar.info("Say: 'Buy PLTR 10 shares' or 'Check portfolio'")
    
    st.sidebar.markdown("## 🎛️ Controls")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📈 Trade Now", key="trade_now"):
            st.success("🚀 Trade execution ready!")
    
    with col2:
        if st.button("🛑 Stop Bot", key="stop_bot"):
            st.warning("⏸️ Bot paused!")
    
    # Alert settings
    st.sidebar.markdown("## 🔔 Alert Settings")
    enable_telegram = st.sidebar.checkbox("Telegram Alerts (@SHADOWCLAW007)", value=True)
    enable_sms = st.sidebar.checkbox("SMS Alerts", value=False)
    daily_alert_time = st.sidebar.selectbox("Daily Alert Time", ["09:25", "09:30", "10:00"])

def show_live_charts(stocks, prices, changes):
    st.subheader("📊 Live Technical Indicators")
    
    # Ticker selection
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_ticker = st.selectbox("Select Ticker", stocks)
    with col2:
        timeframe = st.selectbox("Timeframe", ["1d", "1h", "15m", "5m"])
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Get selected stock data
    stock_idx = stocks.index(selected_ticker)
    current_price = prices[stock_idx]
    price_change = changes[stock_idx]
    
    # Display current values
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Price",
            f"${current_price:.2f}",
            f"{price_change:+.2f}%"
        )
    
    with col2:
        # Mock RSI
        rsi_value = np.random.uniform(25, 75)
        rsi_color = "🟢" if 30 <= rsi_value <= 40 else "🔴" if rsi_value < 30 else "🟡"
        st.metric("RSI", f"{rsi_value:.1f} {rsi_color}")
    
    with col3:
        # Mock Supertrend
        supertrend = np.random.choice([1, -1])
        st_signal = "🟢 BUY" if supertrend > 0 else "🔴 SELL"
        st.metric("Supertrend", st_signal)
    
    with col4:
        # Mock MACD
        macd_bullish = np.random.choice([True, False])
        macd_status = "🟢 BUY" if macd_bullish else "🔴 SELL"
        st.metric("MACD", macd_status)
    
    # Combined signal analysis
    buy_signals = [
        30 <= rsi_value <= 40,
        supertrend > 0,
        macd_bullish
    ]
    
    signal_strength = sum(buy_signals)
    
    if signal_strength >= 3:
        st.markdown('<div class="buy-signal">🚀 STRONG BUY SIGNAL - ALL INDICATORS CONFIRM!</div>', 
                   unsafe_allow_html=True)
    elif signal_strength >= 2:
        st.markdown('<div style="background: #ffa500; color: white; padding: 0.75rem; border-radius: 8px; text-align: center; font-weight: bold;">⚠️ MODERATE BUY SIGNAL</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div style="background: #6c757d; color: white; padding: 0.75rem; border-radius: 8px; text-align: center; font-weight: bold;">⏳ WAITING FOR SIGNAL</div>', 
                   unsafe_allow_html=True)
    
    # Mock chart data
    st.subheader(f"📈 {selected_ticker} Price Chart")
    
    # Generate mock price data
    dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
    base_price = current_price
    price_data = []
    
    for i in range(100):
        price_change = np.random.normal(0, 2)  # Random walk
        base_price += price_change
        price_data.append(max(base_price, 0.01))  # Ensure positive prices
    
    chart_data = pd.DataFrame({
        'Date': dates,
        'Price': price_data
    })
    
    st.line_chart(chart_data.set_index('Date'))
    
    # Technical indicators explanation
    with st.expander("📚 How Our Trading Signals Work"):
        st.markdown("""
        **🎯 Our AI combines 3 powerful indicators:**
        
        **RSI (Relative Strength Index)**
        - 🟢 **Buy Zone**: 30-40 (oversold but recovering)
        - 🔴 **Overbought**: Above 70
        - 🟡 **Neutral**: 40-70
        
        **Supertrend**
        - 🟢 **Green**: Uptrend confirmed
        - 🔴 **Red**: Downtrend active
        
        **MACD**
        - 🟢 **Bullish**: MACD line above signal line
        - 🔴 **Bearish**: MACD line below signal line
        
        **🎪 Signal Strength:**
        - **3/3**: Strong Buy (all indicators confirm)
        - **2/3**: Moderate Buy (majority confirm)
        - **1/3 or 0/3**: Wait for better entry
        """)

def show_portfolio():
    st.subheader("💼 Portfolio Management")
    
    # Portfolio overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Value", "$12,450.78", "2.34%")
    
    with col2:
        st.metric("Buying Power", "$649.78", "-$100.00")
    
    with col3:
        st.metric("Day P&L", "+$234.56", "1.89%")
    
    with col4:
        st.metric("Total P&L", "+$1,450.78", "13.2%")
    
    # Holdings table
    st.subheader("📈 Current Holdings")
    holdings_data = {
        'Symbol': ['PLTR', 'NVDA', 'O', 'AGNC'],
        'Shares': [100, 25, 50, 200],
        'Avg Cost': ['$15.50', '$220.00', '$55.00', '$12.50'],
        'Current Price': ['$18.25', '$275.50', '$58.25', '$13.75'],
        'Market Value': ['$1,825.00', '$6,887.50', '$2,912.50', '$2,750.00'],
        'P&L': ['+$275.00', '+$1,387.50', '+$162.50', '+$250.00'],
        'P&L %': ['+17.7%', '+25.2%', '+5.9%', '+10.0%']
    }
    
    df = pd.DataFrame(holdings_data)
    st.dataframe(df, use_container_width=True)
    
    # Google Sheets sync status
    st.info("📊 **Google Sheets Integration**: Connect to sync your real portfolio data automatically")
    
    if st.button("🔗 Connect Google Sheets"):
        st.success("✅ Ready to connect! Add your Google Sheets credentials to sync live data.")

def show_trade_log():
    st.subheader("📈 Trade Log")
    
    # Add new trade
    with st.expander("➕ Add New Trade"):
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_symbol = st.text_input("Symbol", "PLTR")
        with col2:
            trade_action = st.selectbox("Action", ["BUY", "SELL"])
        with col3:
            trade_quantity = st.number_input("Quantity", min_value=1, value=10)
        
        col1, col2 = st.columns(2)
        with col1:
            trade_price = st.number_input("Price", min_value=0.01, value=18.25)
        with col2:
            if st.button("📝 Log Trade"):
                st.success(f"✅ Trade logged: {trade_action} {trade_quantity} {trade_symbol} @ ${trade_price:.2f}")
    
    # Recent trades
    st.subheader("📋 Recent Trades")
    trades_data = {
        'Date': ['2025-01-24', '2025-01-23', '2025-01-22', '2025-01-21'],
        'Time': ['10:30 AM', '02:15 PM', '09:45 AM', '11:20 AM'],
        'Symbol': ['PLTR', 'NVDA', 'O', 'AGNC'],
        'Action': ['BUY', 'SELL', 'BUY', 'BUY'],
        'Quantity': [50, 10, 25, 100],
        'Price': ['$18.25', '$270.00', '$57.50', '$13.25'],
        'Total': ['$912.50', '$2,700.00', '$1,437.50', '$1,325.00'],
        'P&L': ['+$137.50', '+$450.00', '+$62.50', '+$50.00']
    }
    
    st.dataframe(pd.DataFrame(trades_data), use_container_width=True)

def show_watchlist():
    st.subheader("📋 Weekly Watchlist")
    
    # Watchlist with signals
    watchlist_data = {
        'Symbol': ['AAPL', 'TSLA', 'SPY', 'QQQ', 'AMD', 'MSFT'],
        'Price': ['$175.50', '$185.25', '$485.75', '$385.25', '$142.80', '$422.15'],
        'Change': ['-0.5%', '+3.2%', '+0.9%', '+1.1%', '+2.8%', '-0.8%'],
        'RSI': [45.2, 32.1, 55.8, 48.3, 38.5, 52.1],
        'Supertrend': ['🔴 SELL', '🟢 BUY', '🔴 SELL', '🟡 NEUTRAL', '🟢 BUY', '🟡 NEUTRAL'],
        'MACD': ['🟢 BUY', '🟢 BUY', '🔴 SELL', '🟡 NEUTRAL', '🟢 BUY', '🔴 SELL'],
        'Signal': ['Medium', 'Strong', 'Weak', 'Medium', 'Strong', 'Weak']
    }
    
    df_watchlist = pd.DataFrame(watchlist_data)
    st.dataframe(df_watchlist, use_container_width=True)
    
    # Add to watchlist
    with st.expander("➕ Add to Watchlist"):
        new_symbol = st.text_input("Symbol to Add", "")
        if st.button("Add Symbol") and new_symbol:
            st.success(f"✅ Added {new_symbol.upper()} to watchlist!")

def show_roth_ira():
    st.subheader("🏦 Roth IRA Planner")
    
    # Roth IRA overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Roth IRA Value", "$25,750.00", "+8.5%")
    
    with col2:
        st.metric("2025 Contribution", "$3,500.00", "Remaining: $3,500")
    
    with col3:
        st.metric("Dip Buy Fund", "$1,250.00", "Available")
    
    # Dip buy triggers
    st.subheader("📉 Dip Buy Triggers")
    dip_data = {
        'Symbol': ['PLTR', 'NVDA', 'VTI', 'SCHD'],
        'Target Dip %': ['-15%', '-20%', '-10%', '-12%'],
        'Current Price': ['$18.25', '$275.50', '$285.75', '$78.90'],
        'Trigger Price': ['$15.51', '$220.40', '$257.18', '$69.43'],
        'Buy Amount': ['$500', '$750', '$300', '$400'],
        'Status': ['🟡 Monitoring', '🔴 Triggered', '🟢 Set', '🟢 Set']
    }
    
    st.dataframe(pd.DataFrame(dip_data), use_container_width=True)
    
    # Performance visualization
    st.subheader("📊 Roth IRA Performance")
    
    # Generate mock performance data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    values = [20000, 20500, 21200, 20800, 22100, 23000, 22500, 23800, 24200, 25100, 24800, 25750]
    
    performance_data = pd.DataFrame({
        'Month': months,
        'Value': values
    })
    
    st.line_chart(performance_data.set_index('Month'))

# Footer with deployment info
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <h4>🚀 Ready for Mobile Deployment!</h4>
    <p><strong>Next Steps:</strong></p>
    <p>1️⃣ Deploy to <strong>Streamlit Cloud</strong> for free mobile access</p>
    <p>2️⃣ Set up <strong>Telegram Bot</strong> for @SHADOWCLAW007 alerts</p>
    <p>3️⃣ Connect <strong>Google Sheets</strong> for real portfolio sync</p>
    <p>4️⃣ Add your phone to home screen for app-like experience!</p>
    <br>
    <p>📱 <strong>This dashboard is fully mobile-responsive and ready to deploy!</strong></p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
