"""
Chart Pattern Recognition System
Detects support/resistance, trend lines, and classic patterns
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List, Dict, Tuple, Optional
from scipy.signal import find_peaks, find_peaks_cwt
from sklearn.linear_model import LinearRegression
import yfinance as yf
from datetime import datetime, timedelta

class PatternRecognizer:
    """Advanced chart pattern recognition"""
    
    def __init__(self):
        self.patterns_detected = []
        self.support_resistance_levels = []
    
    def find_support_resistance(self, data: pd.DataFrame, window: int = 10) -> Dict[str, List[float]]:
        """Find support and resistance levels"""
        try:
            highs = data['High'].values
            lows = data['Low'].values
            closes = data['Close'].values
            
            # Find peaks (resistance) and troughs (support)
            resistance_indices = find_peaks(highs, distance=window)[0]
            support_indices = find_peaks(-lows, distance=window)[0]
            
            # Get the actual price levels
            resistance_levels = [highs[i] for i in resistance_indices]
            support_levels = [lows[i] for i in support_indices]
            
            # Filter levels that are tested multiple times
            current_price = closes[-1]
            
            # Keep levels within reasonable range of current price
            resistance_levels = [r for r in resistance_levels if current_price * 0.95 <= r <= current_price * 1.20]
            support_levels = [s for s in support_levels if current_price * 0.80 <= s <= current_price * 1.05]
            
            return {
                'resistance': sorted(list(set(resistance_levels)), reverse=True)[:5],
                'support': sorted(list(set(support_levels)), reverse=True)[:5]
            }
            
        except Exception as e:
            st.error(f"Error finding support/resistance: {e}")
            return {'resistance': [], 'support': []}
    
    def detect_trend_lines(self, data: pd.DataFrame) -> Dict[str, Dict]:
        """Detect trend lines using linear regression"""
        try:
            closes = data['Close'].values
            dates = np.arange(len(closes))
            
            # Overall trend
            reg = LinearRegression()
            reg.fit(dates.reshape(-1, 1), closes)
            trend_slope = reg.coef_[0]
            trend_intercept = reg.intercept_
            
            # Recent trend (last 20 periods)
            recent_dates = dates[-20:]
            recent_closes = closes[-20:]
            
            reg_recent = LinearRegression()
            reg_recent.fit(recent_dates.reshape(-1, 1), recent_closes)
            recent_slope = reg_recent.coef_[0]
            recent_intercept = reg_recent.intercept_
            
            return {
                'overall_trend': {
                    'slope': trend_slope,
                    'intercept': trend_intercept,
                    'direction': 'Bullish' if trend_slope > 0 else 'Bearish',
                    'strength': abs(trend_slope)
                },
                'recent_trend': {
                    'slope': recent_slope,
                    'intercept': recent_intercept,
                    'direction': 'Bullish' if recent_slope > 0 else 'Bearish',
                    'strength': abs(recent_slope)
                }
            }
            
        except Exception as e:
            st.error(f"Error detecting trend lines: {e}")
            return {'overall_trend': {}, 'recent_trend': {}}
    
    def detect_head_shoulders(self, data: pd.DataFrame) -> List[Dict]:
        """Detect Head and Shoulders pattern"""
        try:
            highs = data['High'].values
            lows = data['Low'].values
            
            if len(highs) < 50:
                return []
            
            patterns = []
            window = 10
            
            # Find peaks for potential shoulders and head
            peaks = find_peaks(highs, distance=window, prominence=np.std(highs) * 0.5)[0]
            
            if len(peaks) >= 3:
                for i in range(len(peaks) - 2):
                    left_shoulder = peaks[i]
                    head = peaks[i + 1]
                    right_shoulder = peaks[i + 2]
                    
                    left_height = highs[left_shoulder]
                    head_height = highs[head]
                    right_height = highs[right_shoulder]
                    
                    # Check if it forms a head and shoulders
                    if (head_height > left_height * 1.02 and 
                        head_height > right_height * 1.02 and
                        abs(left_height - right_height) / left_height < 0.05):
                        
                        patterns.append({
                            'type': 'Head and Shoulders',
                            'left_shoulder': {'index': left_shoulder, 'price': left_height},
                            'head': {'index': head, 'price': head_height},
                            'right_shoulder': {'index': right_shoulder, 'price': right_height},
                            'confidence': 0.7,
                            'signal': 'Bearish'
                        })
            
            return patterns
            
        except Exception as e:
            return []
    
    def detect_triangles(self, data: pd.DataFrame) -> List[Dict]:
        """Detect triangle patterns"""
        try:
            if len(data) < 30:
                return []
            
            patterns = []
            highs = data['High'].values
            lows = data['Low'].values
            
            # Look for converging trend lines
            recent_data = data.tail(30)
            recent_highs = recent_data['High'].values
            recent_lows = recent_data['Low'].values
            dates = np.arange(len(recent_highs))
            
            # Upper trend line (resistance)
            high_peaks = find_peaks(recent_highs, distance=3)[0]
            if len(high_peaks) >= 2:
                upper_reg = LinearRegression()
                upper_reg.fit(high_peaks.reshape(-1, 1), recent_highs[high_peaks])
                upper_slope = upper_reg.coef_[0]
            else:
                upper_slope = 0
            
            # Lower trend line (support)
            low_peaks = find_peaks(-recent_lows, distance=3)[0]
            if len(low_peaks) >= 2:
                lower_reg = LinearRegression()
                lower_reg.fit(low_peaks.reshape(-1, 1), recent_lows[low_peaks])
                lower_slope = lower_reg.coef_[0]
            else:
                lower_slope = 0
            
            # Determine triangle type
            if upper_slope < -0.1 and lower_slope > 0.1:
                triangle_type = "Symmetrical Triangle"
                signal = "Breakout pending"
            elif abs(upper_slope) < 0.05 and lower_slope > 0.1:
                triangle_type = "Ascending Triangle"
                signal = "Bullish"
            elif upper_slope < -0.1 and abs(lower_slope) < 0.05:
                triangle_type = "Descending Triangle"
                signal = "Bearish"
            else:
                return patterns
            
            patterns.append({
                'type': triangle_type,
                'upper_slope': upper_slope,
                'lower_slope': lower_slope,
                'signal': signal,
                'confidence': 0.6
            })
            
            return patterns
            
        except Exception as e:
            return []
    
    def detect_double_top_bottom(self, data: pd.DataFrame) -> List[Dict]:
        """Detect double top/bottom patterns"""
        try:
            if len(data) < 20:
                return []
            
            patterns = []
            highs = data['High'].values
            lows = data['Low'].values
            
            # Find peaks and troughs
            high_peaks = find_peaks(highs, distance=5, prominence=np.std(highs) * 0.3)[0]
            low_peaks = find_peaks(-lows, distance=5, prominence=np.std(lows) * 0.3)[0]
            
            # Check for double tops
            if len(high_peaks) >= 2:
                for i in range(len(high_peaks) - 1):
                    peak1_idx = high_peaks[i]
                    peak2_idx = high_peaks[i + 1]
                    peak1_price = highs[peak1_idx]
                    peak2_price = highs[peak2_idx]
                    
                    # Check if peaks are similar height
                    if abs(peak1_price - peak2_price) / peak1_price < 0.02:
                        patterns.append({
                            'type': 'Double Top',
                            'peak1': {'index': peak1_idx, 'price': peak1_price},
                            'peak2': {'index': peak2_idx, 'price': peak2_price},
                            'signal': 'Bearish',
                            'confidence': 0.6
                        })
            
            # Check for double bottoms
            if len(low_peaks) >= 2:
                for i in range(len(low_peaks) - 1):
                    trough1_idx = low_peaks[i]
                    trough2_idx = low_peaks[i + 1]
                    trough1_price = lows[trough1_idx]
                    trough2_price = lows[trough2_idx]
                    
                    # Check if troughs are similar depth
                    if abs(trough1_price - trough2_price) / trough1_price < 0.02:
                        patterns.append({
                            'type': 'Double Bottom',
                            'trough1': {'index': trough1_idx, 'price': trough1_price},
                            'trough2': {'index': trough2_idx, 'price': trough2_price},
                            'signal': 'Bullish',
                            'confidence': 0.6
                        })
            
            return patterns
            
        except Exception as e:
            return []
    
    def analyze_breakouts(self, data: pd.DataFrame, sr_levels: Dict[str, List[float]]) -> List[Dict]:
        """Analyze potential breakouts"""
        try:
            breakouts = []
            current_price = data['Close'].iloc[-1]
            recent_high = data['High'].tail(5).max()
            recent_low = data['Low'].tail(5).min()
            
            # Check resistance breakouts
            for resistance in sr_levels['resistance']:
                if current_price > resistance and recent_high > resistance:
                    breakouts.append({
                        'type': 'Resistance Breakout',
                        'level': resistance,
                        'price': current_price,
                        'signal': 'Bullish',
                        'strength': 'Strong' if current_price > resistance * 1.02 else 'Weak'
                    })
            
            # Check support breakdowns
            for support in sr_levels['support']:
                if current_price < support and recent_low < support:
                    breakouts.append({
                        'type': 'Support Breakdown',
                        'level': support,
                        'price': current_price,
                        'signal': 'Bearish',
                        'strength': 'Strong' if current_price < support * 0.98 else 'Weak'
                    })
            
            return breakouts
            
        except Exception as e:
            return []
    
    def create_pattern_chart(self, symbol: str, data: pd.DataFrame) -> go.Figure:
        """Create chart with pattern annotations"""
        try:
            # Find support/resistance levels
            sr_levels = self.find_support_resistance(data)
            
            # Detect patterns
            head_shoulders = self.detect_head_shoulders(data)
            triangles = self.detect_triangles(data)
            double_patterns = self.detect_double_top_bottom(data)
            trend_lines = self.detect_trend_lines(data)
            breakouts = self.analyze_breakouts(data, sr_levels)
            
            # Create candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol
            )])
            
            # Add support levels
            for support in sr_levels['support']:
                fig.add_hline(
                    y=support,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"Support: ${support:.2f}",
                    annotation_position="bottom right"
                )
            
            # Add resistance levels
            for resistance in sr_levels['resistance']:
                fig.add_hline(
                    y=resistance,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Resistance: ${resistance:.2f}",
                    annotation_position="top right"
                )
            
            # Add trend lines
            if trend_lines['overall_trend']:
                dates = np.arange(len(data))
                trend_line = (trend_lines['overall_trend']['slope'] * dates + 
                             trend_lines['overall_trend']['intercept'])
                
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=trend_line,
                    mode='lines',
                    name=f"Trend ({trend_lines['overall_trend']['direction']})",
                    line=dict(color='blue', width=2, dash='dot')
                ))
            
            # Add pattern annotations
            patterns_found = head_shoulders + triangles + double_patterns
            
            fig.update_layout(
                title=f"📈 {symbol} - Pattern Analysis",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=600,
                showlegend=False
            )
            
            return fig, {
                'support_resistance': sr_levels,
                'patterns': patterns_found,
                'trend_lines': trend_lines,
                'breakouts': breakouts
            }
            
        except Exception as e:
            st.error(f"Error creating pattern chart: {e}")
            return go.Figure(), {}
    
    def display_pattern_analysis(self, symbol: str):
        """Display comprehensive pattern analysis"""
        try:
            # Get data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="3mo")
            
            if data.empty:
                st.error("No data available")
                return
            
            # Create pattern chart
            fig, analysis = self.create_pattern_chart(symbol, data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display analysis results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Support & Resistance")
                if analysis.get('support_resistance'):
                    sr = analysis['support_resistance']
                    
                    st.write("**Resistance Levels:**")
                    for r in sr['resistance']:
                        st.write(f"• ${r:.2f}")
                    
                    st.write("**Support Levels:**")
                    for s in sr['support']:
                        st.write(f"• ${s:.2f}")
            
            with col2:
                st.subheader("📊 Pattern Signals")
                
                if analysis.get('breakouts'):
                    st.write("**Active Breakouts:**")
                    for breakout in analysis['breakouts']:
                        signal_color = "🟢" if breakout['signal'] == 'Bullish' else "🔴"
                        st.write(f"{signal_color} {breakout['type']}: ${breakout['level']:.2f}")
                
                if analysis.get('patterns'):
                    st.write("**Detected Patterns:**")
                    for pattern in analysis['patterns']:
                        signal_icon = "🚀" if pattern['signal'] == 'Bullish' else "📉"
                        st.write(f"{signal_icon} {pattern['type']}")
            
            # Trend analysis
            if analysis.get('trend_lines'):
                st.subheader("📈 Trend Analysis")
                trends = analysis['trend_lines']
                
                col3, col4 = st.columns(2)
                with col3:
                    if trends.get('overall_trend'):
                        ot = trends['overall_trend']
                        trend_emoji = "📈" if ot['direction'] == 'Bullish' else "📉"
                        st.metric(
                            "Overall Trend",
                            f"{trend_emoji} {ot['direction']}",
                            f"Strength: {ot['strength']:.4f}"
                        )
                
                with col4:
                    if trends.get('recent_trend'):
                        rt = trends['recent_trend']
                        trend_emoji = "📈" if rt['direction'] == 'Bullish' else "📉"
                        st.metric(
                            "Recent Trend",
                            f"{trend_emoji} {rt['direction']}",
                            f"Strength: {rt['strength']:.4f}"
                        )
            
        except Exception as e:
            st.error(f"Error in pattern analysis: {e}")
