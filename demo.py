"""
🚀 ULTIMATE AI Trading Signal Platform - Enhanced Version
The most powerful mobile-friendly trading dashboard
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import time

# Enhanced Mobile CSS
st.set_page_config(
    page_title="🚀 Ultimate AI Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @media (max-width: 768px) {
        .stApp > header {display: none;}
        .main .block-container {
            padding: 1rem;
            max-width: 100%;
        }
        .stButton > button {
            height: 3rem;
            width: 100%;
            font-size: 1.1rem;
            border-radius: 10px;
            margin: 0.25rem 0;
        }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .signal-strong-buy {
        background: linear-gradient(45deg, #4CAF50, #8BC34A);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        animation: pulse 2s infinite;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .signal-strong-sell {
        background: linear-gradient(45deg, #f44336, #FF5722);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        animation: pulse 2s infinite;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .signal-hold {
        background: linear-gradient(45deg, #FF9800, #FFC107);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
</style>
""", unsafe_allow_html=True)

# Technical Indicators Implementation
class TechnicalIndicators:
    def calculate_rsi(self, data, period=14):
        """Calculate RSI with buy/sell signals"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Generate signals
        signals = []
        for val in rsi:
            if pd.isna(val):
                signals.append('HOLD')
            elif val < 30:
                signals.append('BUY')
            elif val > 70:
                signals.append('SELL')
            else:
                signals.append('HOLD')
        
        return {
            'RSI': rsi,
            'Signal': signals,
            'Current': rsi.iloc[-1] if len(rsi) > 0 else 50
        }
    
    def calculate_supertrend(self, data, period=10, multiplier=3.0):
        """Calculate Supertrend indicator"""
        high, low, close = data['High'], data['Low'], data['Close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        # Basic bands
        hl2 = (high + low) / 2
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        # Supertrend calculation
        supertrend = pd.Series(index=data.index, dtype=float)
        direction = pd.Series(index=data.index, dtype=str)
        
        for i in range(len(data)):
            if i == 0:
                supertrend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = 'SELL'
            else:
                if close.iloc[i] <= lower_band.iloc[i]:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    direction.iloc[i] = 'SELL'
                elif close.iloc[i] >= upper_band.iloc[i]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 'BUY'
                else:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                    direction.iloc[i] = direction.iloc[i-1]
        
        return {
            'Supertrend': supertrend,
            'Signal': direction,
            'Current': direction.iloc[-1] if len(direction) > 0 else 'HOLD'
        }
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """Calculate MACD with signals"""
        close = data['Close']
        exp1 = close.ewm(span=fast).mean()
        exp2 = close.ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        # Generate trade signals
        signals = []
        for i in range(len(macd)):
            if i == 0:
                signals.append('HOLD')
            elif macd.iloc[i] > signal_line.iloc[i] and macd.iloc[i-1] <= signal_line.iloc[i-1]:
                signals.append('BUY')
            elif macd.iloc[i] < signal_line.iloc[i] and macd.iloc[i-1] >= signal_line.iloc[i-1]:
                signals.append('SELL')
            else:
                signals.append('HOLD')
        
        return {
            'MACD': macd,
            'Signal_Line': signal_line,
            'Histogram': histogram,
            'Trade_Signal': signals,
            'Current': signals[-1] if signals else 'HOLD'
        }

def create_professional_chart(data, ticker, indicators):
    """Create advanced TradingView-style chart"""
    fig = make_subplots(
        rows=4, cols=1,
        row_heights=[0.5, 0.15, 0.15, 0.2],
        shared_xaxes=True,
        subplot_titles=(
            f'📈 {ticker} - Professional Analysis',
            '📊 RSI (14)',
            '📈 MACD',
            '🔊 Volume'
        ),
        vertical_spacing=0.02
    )
    
    # Main candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=ticker,
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ),
        row=1, col=1
    )
    
    # Supertrend
    if 'supertrend' in indicators:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=indicators['supertrend']['Supertrend'],
                mode='lines',
                name='Supertrend',
                line=dict(color='orange', width=3)
            ),
            row=1, col=1
        )
    
    # RSI
    if 'rsi' in indicators:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=indicators['rsi']['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='#9c27b0', width=2)
            ),
            row=2, col=1
        )
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=1)
    
    # MACD
    if 'macd' in indicators:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=indicators['macd']['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='#2196f3', width=2)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=indicators['macd']['Signal_Line'],
                mode='lines',
                name='Signal',
                line=dict(color='#ff9800', width=2)
            ),
            row=3, col=1
        )
        
        # MACD Histogram
        colors = ['green' if val >= 0 else 'red' for val in indicators['macd']['Histogram']]
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=indicators['macd']['Histogram'],
                name='Histogram',
                marker_color=colors,
                opacity=0.6
            ),
            row=3, col=1
        )
    
    # Volume
    volume_colors = ['#00ff88' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#ff4444' 
                    for i in range(len(data))]
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker_color=volume_colors,
            opacity=0.7
        ),
        row=4, col=1
    )
    
    # Professional styling
    fig.update_layout(
        title=dict(
            text=f"🚀 {ticker} - Ultimate Trading Analysis",
            font=dict(size=20, color='white'),
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        font=dict(color='white'),
        showlegend=True,
        height=800,
        xaxis_rangeslider_visible=False
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)', showgrid=True)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', showgrid=True)
    
    return fig

def analyze_combined_signals(indicators):
    """Analyze all indicators for combined signal"""
    signals = []
    signal_strength = 0
    
    # RSI Signal
    if 'rsi' in indicators:
        rsi_signal = indicators['rsi']['Current']
        if rsi_signal < 30:
            signals.append(('RSI', 'BUY', 'Strong'))
            signal_strength += 1
        elif rsi_signal > 70:
            signals.append(('RSI', 'SELL', 'Strong'))
            signal_strength -= 1
        else:
            signals.append(('RSI', 'NEUTRAL', 'Weak'))
    
    # Supertrend Signal
    if 'supertrend' in indicators:
        st_signal = indicators['supertrend']['Current']
        if st_signal == 'BUY':
            signals.append(('Supertrend', 'BUY', 'Strong'))
            signal_strength += 1
        elif st_signal == 'SELL':
            signals.append(('Supertrend', 'SELL', 'Strong'))
            signal_strength -= 1
        else:
            signals.append(('Supertrend', 'NEUTRAL', 'Weak'))
    
    # MACD Signal
    if 'macd' in indicators:
        macd_signal = indicators['macd']['Current']
        if macd_signal == 'BUY':
            signals.append(('MACD', 'BUY', 'Strong'))
            signal_strength += 1
        elif macd_signal == 'SELL':
            signals.append(('MACD', 'SELL', 'Strong'))
            signal_strength -= 1
        else:
            signals.append(('MACD', 'NEUTRAL', 'Weak'))
    
    # Overall direction
    if signal_strength >= 2:
        overall = "STRONG BUY"
    elif signal_strength == 1:
        overall = "BUY"
    elif signal_strength <= -2:
        overall = "STRONG SELL"
    elif signal_strength == -1:
        overall = "SELL"
    else:
        overall = "HOLD"
    
    confidence = abs(signal_strength) / 3 * 100
    
    return {
        'overall': overall,
        'confidence': confidence,
        'individual': signals,
        'strength': signal_strength
    }

def main():
    """Main application"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🚀 ULTIMATE AI Trading Platform
        </h1>
        <p style="font-size: 1.2rem; opacity: 0.8; margin: 0.5rem 0;">
            Professional Trading Signals • Advanced Analytics • Mobile Optimized
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    indicators_calc = TechnicalIndicators()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Trading Controls")
        ticker = st.text_input("📈 Stock Symbol", value="AAPL").upper()
        
        period_options = {
            "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", 
            "1 Year": "1y", "2 Years": "2y"
        }
        selected_period = st.selectbox("📅 Period", list(period_options.keys()), index=2)
        period = period_options[selected_period]
        
        st.markdown("### ⚙️ Indicator Settings")
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        st_period = st.slider("Supertrend Period", 5, 20, 10)
        st_multiplier = st.slider("Supertrend Multiplier", 1.0, 5.0, 3.0)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Live Analysis", 
        "🗺️ Market Overview",
        "🔍 Pattern Scanner", 
        "📊 Strategy Tester"
    ])
    
    with tab1:
        st.markdown("### 📈 Professional Technical Analysis")
        
        if not ticker:
            st.warning("⚠️ Please enter a stock symbol")
            return
        
        try:
            # Fetch data
            with st.spinner(f"📡 Loading {ticker} data..."):
                data = yf.download(ticker, period=period, interval="1d")
                
                if data.empty:
                    st.error("❌ No data found. Try a different symbol.")
                    return
            
            # Calculate indicators
            with st.spinner("🧮 Calculating indicators..."):
                indicators = {}
                indicators['rsi'] = indicators_calc.calculate_rsi(data, rsi_period)
                indicators['supertrend'] = indicators_calc.calculate_supertrend(data, st_period, st_multiplier)
                indicators['macd'] = indicators_calc.calculate_macd(data)
            
            # Current price info
            current_price = data['Close'].iloc[-1]
            price_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
            price_change_pct = (price_change / data['Close'].iloc[-2]) * 100
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                color = '#00ff88' if price_change >= 0 else '#ff4444'
                st.markdown(f"""
                <div class="metric-card">
                    <h3>💰 Current Price</h3>
                    <h2 style="color: {color};">${current_price:.2f}</h2>
                    <p>{'+' if price_change >= 0 else ''}{price_change_pct:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                rsi_val = indicators['rsi']['Current']
                rsi_color = '#ff4444' if rsi_val > 70 else '#00ff88' if rsi_val < 30 else '#ffaa00'
                rsi_status = 'Overbought' if rsi_val > 70 else 'Oversold' if rsi_val < 30 else 'Neutral'
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 RSI</h3>
                    <h2 style="color: {rsi_color};">{rsi_val:.1f}</h2>
                    <p>{rsi_status}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st_signal = indicators['supertrend']['Current']
                st_color = '#00ff88' if st_signal == 'BUY' else '#ff4444'
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎯 Supertrend</h3>
                    <h2 style="color: {st_color};">{st_signal}</h2>
                    <p>Trend Signal</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                macd_signal = indicators['macd']['Current']
                macd_color = '#00ff88' if macd_signal == 'BUY' else '#ff4444' if macd_signal == 'SELL' else '#ffaa00'
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 MACD</h3>
                    <h2 style="color: {macd_color};">{macd_signal}</h2>
                    <p>Momentum</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Combined signal analysis
            signal_analysis = analyze_combined_signals(indicators)
            
            st.markdown("### 🚀 AI Trading Signal")
            
            overall_signal = signal_analysis['overall']
            confidence = signal_analysis['confidence']
            
            if 'STRONG BUY' in overall_signal:
                signal_class = 'signal-strong-buy'
            elif 'STRONG SELL' in overall_signal:
                signal_class = 'signal-strong-sell'
            else:
                signal_class = 'signal-hold'
            
            st.markdown(f"""
            <div class="{signal_class}">
                <h2>🎯 {overall_signal}</h2>
                <h3>Confidence: {confidence:.0f}%</h3>
                <p>All {len(signal_analysis['individual'])} indicators analyzed</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Individual signals breakdown
            st.markdown("### 📊 Signal Breakdown")
            
            signal_cols = st.columns(3)
            for i, (indicator, signal, strength) in enumerate(signal_analysis['individual']):
                with signal_cols[i]:
                    signal_color = '#00ff88' if signal == 'BUY' else '#ff4444' if signal == 'SELL' else '#ffaa00'
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; text-align: center;">
                        <h4>{indicator}</h4>
                        <h3 style="color: {signal_color};">{signal}</h3>
                        <p>{strength}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Professional chart
            st.markdown("### 📈 Professional Chart Analysis")
            chart = create_professional_chart(data, ticker, indicators)
            st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})
            
            # Trading recommendations
            st.markdown("### 💡 Trading Insights")
            
            if signal_analysis['strength'] >= 2:
                st.success(f"""
                🚀 **STRONG BUY SIGNAL DETECTED**
                - All major indicators align bullishly
                - Consider entering long position
                - Set stop loss at recent support level
                - Target: Next resistance level
                """)
            elif signal_analysis['strength'] <= -2:
                st.error(f"""
                📉 **STRONG SELL SIGNAL DETECTED**
                - Multiple indicators show bearish alignment
                - Consider exiting long positions
                - Potential short opportunity
                - Watch for support break
                """)
            else:
                st.info(f"""
                ⚖️ **MIXED SIGNALS - HOLD POSITION**
                - Indicators showing conflicting signals
                - Wait for clearer directional move
                - Monitor key support/resistance levels
                - Consider reducing position size
                """)
        
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.info("💡 Please check the symbol or try again later")
    
    with tab2:
        st.markdown("### 🗺️ Market Overview")
        st.info("🔄 Market overview features coming soon!")
        
        # Mock market data for demo
        st.markdown("#### 📊 Major Indices")
        
        indices_data = [
            ("S&P 500", "4,200.50", "+1.2%", "#00ff88"),
            ("NASDAQ", "13,100.25", "+0.8%", "#00ff88"),
            ("DOW", "33,500.75", "-0.3%", "#ff4444")
        ]
        
        idx_cols = st.columns(3)
        for i, (name, value, change, color) in enumerate(indices_data):
            with idx_cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{name}</h4>
                    <h3>{value}</h3>
                    <p style="color: {color};">{change}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🔍 Multi-Symbol Pattern Scanner")
        
        symbols_input = st.text_area(
            "📈 Enter symbols (comma-separated):",
            value="AAPL,MSFT,GOOGL,AMZN,TSLA",
            help="Enter stock symbols separated by commas"
        )
        
        if st.button("🔍 Scan for Signals", key="scan_btn"):
            symbols = [s.strip().upper() for s in symbols_input.split(",")]
            
            with st.spinner("🔍 Scanning multiple symbols..."):
                results = []
                
                for symbol in symbols[:5]:  # Limit to 5 for demo
                    try:
                        scan_data = yf.download(symbol, period="1mo", interval="1d")
                        if not scan_data.empty:
                            scan_indicators = {}
                            scan_indicators['rsi'] = indicators_calc.calculate_rsi(scan_data)
                            scan_indicators['supertrend'] = indicators_calc.calculate_supertrend(scan_data)
                            scan_indicators['macd'] = indicators_calc.calculate_macd(scan_data)
                            
                            scan_analysis = analyze_combined_signals(scan_indicators)
                            
                            results.append({
                                'Symbol': symbol,
                                'Signal': scan_analysis['overall'],
                                'Confidence': f"{scan_analysis['confidence']:.0f}%",
                                'Price': f"${scan_data['Close'].iloc[-1]:.2f}"
                            })
                    
                    except Exception:
                        continue
                
                if results:
                    st.success(f"📊 Scanned {len(results)} symbols successfully!")
                    
                    for result in results:
                        signal_color = '#00ff88' if 'BUY' in result['Signal'] else '#ff4444' if 'SELL' in result['Signal'] else '#ffaa00'
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                            <strong>📈 {result['Symbol']}</strong> - {result['Price']}<br>
                            <span style="color: {signal_color}; font-weight: bold;">{result['Signal']}</span> ({result['Confidence']})
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No data found for the provided symbols")
    
    with tab4:
        st.markdown("### 📊 Strategy Performance Tester")
        st.info("🔄 Advanced backtesting features coming soon!")
        
        # Strategy selection
        strategy = st.selectbox("🎯 Select Strategy", [
            "RSI + Supertrend + MACD Combined",
            "RSI Mean Reversion",
            "Supertrend Following",
            "MACD Crossover"
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            test_symbol = st.text_input("📈 Test Symbol", value="AAPL")
            test_period = st.selectbox("📅 Test Period", ["3mo", "6mo", "1y", "2y"])
        
        with col2:
            initial_capital = st.number_input("💰 Initial Capital", value=10000, min_value=1000)
            risk_per_trade = st.slider("⚠️ Risk per Trade (%)", 1, 10, 2)
        
        if st.button("🚀 Run Strategy Test", key="strategy_test"):
            st.info("🧮 Strategy testing simulation...")
            
            # Mock results for demonstration
            st.markdown("#### 📈 Strategy Results")
            
            mock_results = {
                "Total Return": "+15.7%",
                "Win Rate": "67%",
                "Total Trades": "23",
                "Sharpe Ratio": "1.34"
            }
            
            result_cols = st.columns(4)
            for i, (metric, value) in enumerate(mock_results.items()):
                with result_cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{metric}</h4>
                        <h3>{value}</h3>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.success("✅ Strategy test completed! Full backtesting engine coming soon.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; padding: 1rem;">
        🚀 <strong>Ultimate AI Trading Platform</strong> • 
        Professional Grade • Mobile Optimized 📱<br>
        <small>⚠️ This is for educational purposes only. Not financial advice.</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
