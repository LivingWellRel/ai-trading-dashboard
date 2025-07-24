import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from src.indicators import TechnicalIndicators
from src.portfolio import PortfolioManager
from src.alerts import AlertManager
from src.voice import VoiceCommands
from src.utils import get_market_data

# Page configuration
st.set_page_config(
    page_title="AI Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile responsiveness and dark mode
st.markdown("""
<style>
    /* Main App Styling */
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
    
    .alert-button {
        background: #ff4b4b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        width: 100%;
        margin: 0.25rem 0;
        font-size: 16px;
        min-height: 44px; /* iOS touch target */
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
        
        /* Larger buttons for mobile */
        .stButton button {
            height: 48px;
            font-size: 16px;
            border-radius: 8px;
        }
        
        /* Better spacing for mobile */
        .block-container {
            padding-top: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        /* Mobile-friendly tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 14px;
        }
        
        /* Charts responsive */
        .js-plotly-plot {
            width: 100% !important;
        }
    }
    
    /* Touch-friendly improvements */
    @media (max-width: 480px) {
        .main-header {
            padding: 0.75rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .main-header h1 {
            font-size: 1.25rem;
        }
        
        /* Stack columns on very small screens */
        .row-widget {
            flex-direction: column;
        }
        
        /* Bigger touch targets */
        .stSelectbox, .stButton {
            margin-bottom: 1rem;
        }
        
        /* Voice button prominence */
        .voice-button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 1.5rem;
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    }
    
    /* PWA-like styling */
    .main {
        max-width: 100%;
        padding: 0;
    }
    
    /* Hide streamlit branding on mobile */
    @media (max-width: 768px) {
        footer {
            display: none;
        }
        .viewerBadge_container__1QSob {
            display: none;
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
    
    # Initialize managers
    if 'indicators' not in st.session_state:
        st.session_state.indicators = TechnicalIndicators()
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = PortfolioManager()
    if 'alerts' not in st.session_state:
        st.session_state.alerts = AlertManager()
    if 'voice' not in st.session_state:
        st.session_state.voice = VoiceCommands()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Live Charts", 
        "💼 Portfolio", 
        "📈 Trade Log", 
        "📋 Watchlist", 
        "🏦 Roth IRA"
    ])
    
    with tab1:
        show_live_charts()
    
    with tab2:
        show_portfolio()
    
    with tab3:
        show_trade_log()
    
    with tab4:
        show_watchlist()
    
    with tab5:
        show_roth_ira()
    
    # Voice command button
    st.sidebar.markdown("## 🎤 Voice Commands")
    if st.sidebar.button("🎙️ Start Voice Command", key="voice_btn"):
        with st.spinner("Listening..."):
            command = st.session_state.voice.listen_for_command()
            if command:
                st.sidebar.success(f"Command: {command}")
                result = st.session_state.voice.process_command(command)
                st.sidebar.info(result)
    
    # Control buttons
    st.sidebar.markdown("## 🎛️ Controls")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📈 Trade Now", key="trade_now"):
            st.success("Trade execution initiated!")
    
    with col2:
        if st.button("🛑 Stop Bot", key="stop_bot"):
            st.warning("Bot stopped!")
    
    # Alert settings
    st.sidebar.markdown("## 🔔 Alert Settings")
    enable_telegram = st.sidebar.checkbox("Telegram Alerts", value=True)
    enable_sms = st.sidebar.checkbox("SMS Alerts", value=False)
    
    # Dark mode toggle
    if st.sidebar.button("🌙 Toggle Dark Mode"):
        st.rerun()

def show_live_charts():
    st.subheader("📊 Live Technical Indicators")
    
    # Ticker selection
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        ticker = st.selectbox("Select Ticker", ["PLTR", "NVDA", "O", "AGNC", "AAPL", "TSLA", "SPY"])
    with col2:
        timeframe = st.selectbox("Timeframe", ["1d", "1h", "15m", "5m"])
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Get market data
    data = get_market_data(ticker, timeframe)
    
    if data is not None and not data.empty:
        # Calculate indicators
        indicators = st.session_state.indicators.calculate_all(data)
        
        # Display current values
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                f"${data['Close'].iloc[-1]:.2f}",
                f"{((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100:.2f}%"
            )
        
        with col2:
            rsi_value = indicators['RSI'].iloc[-1]
            rsi_color = "🟢" if 30 <= rsi_value <= 40 else "🔴" if rsi_value < 30 else "🟡"
            st.metric("RSI", f"{rsi_value:.1f} {rsi_color}")
        
        with col3:
            supertrend = indicators['Supertrend'].iloc[-1]
            st_signal = "🟢 BUY" if supertrend > 0 else "🔴 SELL"
            st.metric("Supertrend", st_signal)
        
        with col4:
            macd = indicators['MACD'].iloc[-1]
            macd_signal = indicators['MACD_Signal'].iloc[-1]
            macd_status = "🟢 BUY" if macd > macd_signal else "🔴 SELL"
            st.metric("MACD", macd_status)
        
        # Combined signal
        buy_signals = [
            30 <= rsi_value <= 40,
            supertrend > 0,
            macd > macd_signal
        ]
        
        if all(buy_signals):
            st.markdown('<div class="buy-signal">🚀 STRONG BUY SIGNAL - ALL INDICATORS CONFIRM!</div>', 
                       unsafe_allow_html=True)
        elif sum(buy_signals) >= 2:
            st.markdown('<div style="background: #ffa500; color: white; padding: 0.5rem; border-radius: 5px; text-align: center; font-weight: bold;">⚠️ MODERATE BUY SIGNAL</div>', 
                       unsafe_allow_html=True)
        
        # Price chart with indicators
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker
        ))
        
        # Add Supertrend
        fig.add_trace(go.Scatter(
            x=data.index,
            y=indicators['Supertrend_Upper'],
            mode='lines',
            name='Supertrend Upper',
            line=dict(color='red', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=indicators['Supertrend_Lower'],
            mode='lines',
            name='Supertrend Lower',
            line=dict(color='green', width=1)
        ))
        
        fig.update_layout(
            title=f"{ticker} - Live Chart with Technical Indicators",
            xaxis_title="Time",
            yaxis_title="Price ($)",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # RSI subplot
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=data.index,
            y=indicators['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple')
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        fig_rsi.add_hrect(y0=30, y1=40, fillcolor="green", opacity=0.2, annotation_text="Buy Zone")
        
        fig_rsi.update_layout(
            title="RSI (Relative Strength Index)",
            xaxis_title="Time",
            yaxis_title="RSI",
            height=200
        )
        
        st.plotly_chart(fig_rsi, use_container_width=True)
        
        # MACD subplot
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=data.index,
            y=indicators['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')
        ))
        fig_macd.add_trace(go.Scatter(
            x=data.index,
            y=indicators['MACD_Signal'],
            mode='lines',
            name='Signal Line',
            line=dict(color='red')
        ))
        
        fig_macd.update_layout(
            title="MACD (Moving Average Convergence Divergence)",
            xaxis_title="Time",
            yaxis_title="MACD",
            height=200
        )
        
        st.plotly_chart(fig_macd, use_container_width=True)

def show_portfolio():
    st.subheader("💼 Portfolio Management")
    
    # Sync with Google Sheets
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("📊 Syncing with Google Sheets for real-time portfolio data")
    with col2:
        if st.button("🔄 Sync Now"):
            with st.spinner("Syncing with Google Sheets..."):
                portfolio_data = st.session_state.portfolio.sync_google_sheets()
                st.success("Portfolio synced!")
    
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
        'Avg Cost': [15.50, 220.00, 55.00, 12.50],
        'Current Price': [18.25, 275.50, 58.25, 13.75],
        'P&L': ['+$275.00', '+$1,387.50', '+$162.50', '+$250.00'],
        'P&L %': ['+17.7%', '+25.2%', '+5.9%', '+10.0%']
    }
    
    df = pd.DataFrame(holdings_data)
    st.dataframe(df, use_container_width=True)
    
    # Trailing stops
    st.subheader("🛑 Trailing Stop Alerts")
    stops_data = {
        'Symbol': ['PLTR', 'NVDA'],
        'Current Price': ['$18.25', '$275.50'],
        'Stop Price': ['$16.43', '$248.95'],
        'Distance': ['-10%', '-9.6%'],
        'Status': ['🟢 Active', '🟢 Active']
    }
    
    st.dataframe(pd.DataFrame(stops_data), use_container_width=True)

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
                st.success(f"Trade logged: {trade_action} {trade_quantity} {trade_symbol} @ ${trade_price}")
    
    # Recent trades
    trades_data = {
        'Date': ['2025-01-24', '2025-01-23', '2025-01-22'],
        'Symbol': ['PLTR', 'NVDA', 'O'],
        'Action': ['BUY', 'SELL', 'BUY'],
        'Quantity': [50, 10, 25],
        'Price': ['$18.25', '$270.00', '$57.50'],
        'Total': ['$912.50', '$2,700.00', '$1,437.50'],
        'P&L': ['+$137.50', '+$450.00', '+$62.50']
    }
    
    st.dataframe(pd.DataFrame(trades_data), use_container_width=True)

def show_watchlist():
    st.subheader("📋 Weekly Watchlist")
    
    # Watchlist with signals
    watchlist_data = {
        'Symbol': ['AAPL', 'TSLA', 'SPY', 'QQQ'],
        'Price': ['$175.50', '$185.25', '$485.75', '$385.25'],
        'RSI': [45.2, 32.1, 55.8, 48.3],
        'Supertrend': ['🔴 SELL', '🟢 BUY', '🔴 SELL', '🟡 NEUTRAL'],
        'MACD': ['🟢 BUY', '🟢 BUY', '🔴 SELL', '🟡 NEUTRAL'],
        'Signal Strength': ['Medium', 'Strong', 'Weak', 'Medium']
    }
    
    df_watchlist = pd.DataFrame(watchlist_data)
    st.dataframe(df_watchlist, use_container_width=True)
    
    # Add to watchlist
    with st.expander("➕ Add to Watchlist"):
        new_symbol = st.text_input("Symbol to Add", "")
        if st.button("Add Symbol") and new_symbol:
            st.success(f"Added {new_symbol} to watchlist!")

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
        'Symbol': ['PLTR', 'NVDA', 'VTI'],
        'Target Dip %': ['-15%', '-20%', '-10%'],
        'Current Price': ['$18.25', '$275.50', '$285.75'],
        'Trigger Price': ['$15.51', '$220.40', '$257.18'],
        'Buy Amount': ['$500', '$750', '$300'],
        'Status': ['🟡 Monitoring', '🔴 Triggered', '🟢 Set']
    }
    
    st.dataframe(pd.DataFrame(dip_data), use_container_width=True)
    
    # Performance chart
    dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
    values = [20000, 20500, 21200, 20800, 22100, 23000, 22500, 23800, 24200, 25100, 24800, 25750]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name='Roth IRA Value',
        line=dict(color='green', width=3)
    ))
    
    fig.update_layout(
        title="Roth IRA Performance - 2024",
        xaxis_title="Month",
        yaxis_title="Value ($)",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
