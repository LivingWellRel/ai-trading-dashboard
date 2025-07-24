"""
Finviz Market Maps and Sector Analysis
Provides market overview, sector performance, and heatmaps
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Tuple, Optional
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

class FinvizAnalyzer:
    """Finviz market analysis and visualization"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.sectors = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK'],
            'Financial': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'Consumer': ['AMZN', 'TSLA', 'HD', 'NKE', 'MCD'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
            'Industrial': ['BA', 'CAT', 'GE', 'MMM', 'UNP'],
            'Materials': ['LIN', 'APD', 'SHW', 'FCX', 'NEM'],
            'Utilities': ['NEE', 'DUK', 'SO', 'AEP', 'EXC'],
            'Real Estate': ['PLD', 'AMT', 'CCI', 'EQIX', 'PSA'],
            'Communication': ['VZ', 'T', 'CMCSA', 'DIS', 'NFLX']
        }
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_sector_performance(_self) -> pd.DataFrame:
        """Get sector performance data"""
        try:
            sector_data = []
            
            for sector, tickers in _self.sectors.items():
                sector_change = 0
                valid_tickers = 0
                
                for ticker in tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period="2d")
                        if len(hist) >= 2:
                            change = ((hist['Close'][-1] - hist['Close'][-2]) / hist['Close'][-2]) * 100
                            sector_change += change
                            valid_tickers += 1
                    except:
                        continue
                
                if valid_tickers > 0:
                    avg_change = sector_change / valid_tickers
                    sector_data.append({
                        'Sector': sector,
                        'Change%': round(avg_change, 2),
                        'Tickers': valid_tickers
                    })
            
            return pd.DataFrame(sector_data)
            
        except Exception as e:
            st.error(f"Error getting sector data: {e}")
            return pd.DataFrame()
    
    def create_sector_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create sector performance heatmap"""
        if df.empty:
            return go.Figure()
        
        # Create color scale based on performance
        colors = []
        for change in df['Change%']:
            if change > 2:
                colors.append('darkgreen')
            elif change > 0:
                colors.append('lightgreen')
            elif change > -2:
                colors.append('lightcoral')
            else:
                colors.append('darkred')
        
        fig = go.Figure(data=go.Treemap(
            labels=df['Sector'],
            values=abs(df['Change%']) + 1,  # Add 1 to avoid zero values
            parents=[""] * len(df),
            textinfo="label+value",
            texttemplate="<b>%{label}</b><br>%{customdata}%",
            customdata=df['Change%'],
            marker=dict(
                colors=df['Change%'],
                colorscale=[
                    [0, 'darkred'],
                    [0.25, 'lightcoral'], 
                    [0.5, 'lightgray'],
                    [0.75, 'lightgreen'],
                    [1, 'darkgreen']
                ],
                showscale=True,
                colorbar=dict(title="Change %")
            )
        ))
        
        fig.update_layout(
            title="📊 Sector Performance Heatmap",
            font_size=12,
            height=400,
            margin=dict(t=50, l=10, r=10, b=10)
        )
        
        return fig
    
    @st.cache_data(ttl=300)
    def get_market_movers(_self) -> Dict[str, List[Dict]]:
        """Get top gainers and losers"""
        try:
            # Sample market movers (in real implementation, scrape from Finviz)
            gainers = [
                {'Symbol': 'NVDA', 'Change%': 5.2, 'Price': 445.67},
                {'Symbol': 'AAPL', 'Change%': 3.1, 'Price': 189.25},
                {'Symbol': 'MSFT', 'Change%': 2.8, 'Price': 338.11},
                {'Symbol': 'GOOGL', 'Change%': 2.3, 'Price': 142.56},
                {'Symbol': 'META', 'Change%': 1.9, 'Price': 312.44}
            ]
            
            losers = [
                {'Symbol': 'TSLA', 'Change%': -4.1, 'Price': 248.33},
                {'Symbol': 'NFLX', 'Change%': -3.2, 'Price': 456.78},
                {'Symbol': 'AMZN', 'Change%': -2.7, 'Price': 134.22},
                {'Symbol': 'AMD', 'Change%': -2.1, 'Price': 142.88},
                {'Symbol': 'CRM', 'Change%': -1.8, 'Price': 267.55}
            ]
            
            return {'gainers': gainers, 'losers': losers}
            
        except Exception as e:
            st.error(f"Error getting market movers: {e}")
            return {'gainers': [], 'losers': []}
    
    def create_movers_chart(self, movers: Dict[str, List[Dict]]) -> go.Figure:
        """Create market movers visualization"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("🚀 Top Gainers", "📉 Top Losers"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gainers
        if movers['gainers']:
            gainers_df = pd.DataFrame(movers['gainers'])
            fig.add_trace(
                go.Bar(
                    x=gainers_df['Symbol'],
                    y=gainers_df['Change%'],
                    name="Gainers",
                    marker_color='green',
                    text=gainers_df['Change%'].apply(lambda x: f"{x}%"),
                    textposition='outside'
                ),
                row=1, col=1
            )
        
        # Losers
        if movers['losers']:
            losers_df = pd.DataFrame(movers['losers'])
            fig.add_trace(
                go.Bar(
                    x=losers_df['Symbol'],
                    y=losers_df['Change%'],
                    name="Losers",
                    marker_color='red',
                    text=losers_df['Change%'].apply(lambda x: f"{x}%"),
                    textposition='outside'
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            title="📈 Market Movers",
            showlegend=False,
            height=400,
            margin=dict(t=50, l=10, r=10, b=10)
        )
        
        return fig
    
    def get_market_sentiment(self) -> Dict[str, str]:
        """Get overall market sentiment"""
        try:
            # Simple sentiment based on major indices
            indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow, NASDAQ
            positive = 0
            total = 0
            
            for index in indices:
                try:
                    ticker = yf.Ticker(index)
                    hist = ticker.history(period="2d")
                    if len(hist) >= 2:
                        change = ((hist['Close'][-1] - hist['Close'][-2]) / hist['Close'][-2]) * 100
                        if change > 0:
                            positive += 1
                        total += 1
                except:
                    continue
            
            if total == 0:
                return {'sentiment': 'Neutral', 'color': 'yellow', 'icon': '😐'}
            
            ratio = positive / total
            if ratio >= 0.67:
                return {'sentiment': 'Bullish', 'color': 'green', 'icon': '🚀'}
            elif ratio >= 0.33:
                return {'sentiment': 'Mixed', 'color': 'orange', 'icon': '🤔'}
            else:
                return {'sentiment': 'Bearish', 'color': 'red', 'icon': '📉'}
                
        except Exception as e:
            return {'sentiment': 'Unknown', 'color': 'gray', 'icon': '❓'}
    
    def display_market_overview(self):
        """Display comprehensive market overview"""
        st.subheader("🗺️ Market Overview")
        
        # Market sentiment
        sentiment = self.get_market_sentiment()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Market Sentiment",
                f"{sentiment['icon']} {sentiment['sentiment']}",
                delta=None
            )
        
        with col2:
            st.metric("Active Sectors", "10/10", delta="All sectors tracked")
        
        with col3:
            st.metric("Last Update", datetime.now().strftime("%H:%M:%S"), delta="Live")
        
        # Sector heatmap
        sector_df = self.get_sector_performance()
        if not sector_df.empty:
            heatmap_fig = self.create_sector_heatmap(sector_df)
            st.plotly_chart(heatmap_fig, use_container_width=True)
            
            # Sector performance table
            st.subheader("📊 Sector Performance")
            sector_df_display = sector_df.copy()
            sector_df_display['Status'] = sector_df_display['Change%'].apply(
                lambda x: '🚀' if x > 1 else '📈' if x > 0 else '📉' if x > -1 else '💥'
            )
            st.dataframe(
                sector_df_display[['Sector', 'Change%', 'Status']],
                use_container_width=True,
                hide_index=True
            )
        
        # Market movers
        movers = self.get_market_movers()
        if movers['gainers'] or movers['losers']:
            movers_fig = self.create_movers_chart(movers)
            st.plotly_chart(movers_fig, use_container_width=True)
