"""
Advanced Backtesting Engine
Professional-grade strategy backtesting and performance analysis
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import yfinance as yf
from src.indicators import TechnicalIndicators
from src.patterns import PatternRecognizer


@dataclass
class Trade:
    """Individual trade record"""
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: int
    side: str  # 'long' or 'short'
    pnl: float
    pnl_pct: float
    duration: int  # days
    signal_strength: float


@dataclass
class BacktestResults:
    """Comprehensive backtest results"""
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float
    best_trade: float
    worst_trade: float
    trades: List[Trade]
    equity_curve: List[float]
    drawdown_curve: List[float]


class AdvancedBacktester:
    """Professional backtesting engine with multiple strategies"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.patterns = PatternRecognizer()
        self.initial_capital = 100000  # $100k starting capital
        self.position_size = 0.1  # 10% of capital per trade
        self.commission = 0.001  # 0.1% commission
        self.slippage = 0.0005  # 0.05% slippage
    
    def backtest_strategy(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        strategy: str = 'combined_signals',
        **kwargs
    ) -> BacktestResults:
        """Run comprehensive backtest"""
        try:
            # Get historical data
            data = yf.download(symbol, start=start_date, end=end_date)
            if data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Calculate indicators
            rsi = self.indicators.calculate_rsi(data['Close'])
            supertrend = self.indicators.calculate_supertrend(data)
            macd_data = self.indicators.calculate_macd(data['Close'])
            
            # Add indicators to data
            data['RSI'] = rsi
            data['Supertrend'] = supertrend['trend']
            data['SupertrendDirection'] = supertrend['direction']
            data['MACD'] = macd_data['macd']
            data['MACD_Signal'] = macd_data['signal']
            data['MACD_Histogram'] = macd_data['histogram']
            
            # Generate signals based on strategy
            if strategy == 'combined_signals':
                signals = self._generate_combined_signals(data)
            elif strategy == 'rsi_mean_reversion':
                signals = self._generate_rsi_signals(data)
            elif strategy == 'trend_following':
                signals = self._generate_trend_signals(data)
            elif strategy == 'breakout':
                signals = self._generate_breakout_signals(data)
            else:
                signals = self._generate_combined_signals(data)
            
            # Execute trades
            trades = self._execute_trades(data, signals)
            
            # Calculate performance metrics
            results = self._calculate_performance(trades, data)
            
            return results
            
        except Exception as e:
            st.error(f"Backtest error: {e}")
            return self._empty_results()
    
    def _generate_combined_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals using combined RSI + Supertrend + MACD"""
        signals = pd.Series(0, index=data.index)  # 0 = hold, 1 = buy, -1 = sell
        
        try:
            for i in range(1, len(data)):
                buy_signals = 0
                sell_signals = 0
                
                # RSI signals
                if data['RSI'].iloc[i] < 30 and data['RSI'].iloc[i-1] >= 30:
                    buy_signals += 1
                elif data['RSI'].iloc[i] > 70 and data['RSI'].iloc[i-1] <= 70:
                    sell_signals += 1
                
                # Supertrend signals
                if (data['SupertrendDirection'].iloc[i] == 1 and 
                    data['SupertrendDirection'].iloc[i-1] == -1):
                    buy_signals += 1
                elif (data['SupertrendDirection'].iloc[i] == -1 and 
                      data['SupertrendDirection'].iloc[i-1] == 1):
                    sell_signals += 1
                
                # MACD signals
                if (data['MACD'].iloc[i] > data['MACD_Signal'].iloc[i] and
                    data['MACD'].iloc[i-1] <= data['MACD_Signal'].iloc[i-1]):
                    buy_signals += 1
                elif (data['MACD'].iloc[i] < data['MACD_Signal'].iloc[i] and
                      data['MACD'].iloc[i-1] >= data['MACD_Signal'].iloc[i-1]):
                    sell_signals += 1
                
                # Generate signal based on majority
                if buy_signals >= 2:  # At least 2 indicators agree
                    signals.iloc[i] = 1
                elif sell_signals >= 2:
                    signals.iloc[i] = -1
                    
        except Exception as e:
            st.error(f"Signal generation error: {e}")
        
        return signals
    
    def _generate_rsi_signals(self, data: pd.DataFrame) -> pd.Series:
        """RSI mean reversion strategy"""
        signals = pd.Series(0, index=data.index)
        
        for i in range(1, len(data)):
            if data['RSI'].iloc[i] < 25:  # Oversold
                signals.iloc[i] = 1
            elif data['RSI'].iloc[i] > 75:  # Overbought
                signals.iloc[i] = -1
        
        return signals
    
    def _generate_trend_signals(self, data: pd.DataFrame) -> pd.Series:
        """Trend following strategy"""
        signals = pd.Series(0, index=data.index)
        
        for i in range(1, len(data)):
            if (data['SupertrendDirection'].iloc[i] == 1 and 
                data['MACD'].iloc[i] > data['MACD_Signal'].iloc[i]):
                signals.iloc[i] = 1
            elif (data['SupertrendDirection'].iloc[i] == -1 and 
                  data['MACD'].iloc[i] < data['MACD_Signal'].iloc[i]):
                signals.iloc[i] = -1
        
        return signals
    
    def _generate_breakout_signals(self, data: pd.DataFrame) -> pd.Series:
        """Breakout strategy using support/resistance"""
        signals = pd.Series(0, index=data.index)
        
        # Calculate 20-period high/low for breakouts
        data['High_20'] = data['High'].rolling(20).max()
        data['Low_20'] = data['Low'].rolling(20).min()
        
        for i in range(20, len(data)):
            # Breakout above resistance
            if (data['Close'].iloc[i] > data['High_20'].iloc[i-1] and
                data['Volume'].iloc[i] > data['Volume'].rolling(10).mean().iloc[i]):
                signals.iloc[i] = 1
            # Breakdown below support
            elif (data['Close'].iloc[i] < data['Low_20'].iloc[i-1] and
                  data['Volume'].iloc[i] > data['Volume'].rolling(10).mean().iloc[i]):
                signals.iloc[i] = -1
        
        return signals
    
    def _execute_trades(self, data: pd.DataFrame, signals: pd.Series) -> List[Trade]:
        """Execute trades based on signals"""
        trades = []
        position = None  # Current position
        capital = self.initial_capital
        
        try:
            for i, signal in enumerate(signals):
                if signal == 0:
                    continue
                
                current_date = data.index[i]
                current_price = data['Close'].iloc[i]
                
                # Apply slippage and commission
                if signal == 1:  # Buy signal
                    if position is None or position['side'] == 'short':
                        # Close short position if exists
                        if position:
                            exit_price = current_price * (1 + self.slippage)
                            pnl = (position['entry_price'] - exit_price) * position['quantity']
                            pnl_pct = pnl / (position['entry_price'] * position['quantity']) * 100
                            
                            trades.append(Trade(
                                entry_date=position['entry_date'],
                                exit_date=str(current_date.date()),
                                entry_price=position['entry_price'],
                                exit_price=exit_price,
                                quantity=position['quantity'],
                                side='short',
                                pnl=pnl,
                                pnl_pct=pnl_pct,
                                duration=(current_date - pd.to_datetime(position['entry_date'])).days,
                                signal_strength=0.5
                            ))
                            
                            capital += pnl
                        
                        # Open long position
                        entry_price = current_price * (1 + self.slippage)
                        quantity = int((capital * self.position_size) / entry_price)
                        
                        if quantity > 0:
                            position = {
                                'side': 'long',
                                'entry_date': str(current_date.date()),
                                'entry_price': entry_price,
                                'quantity': quantity
                            }
                
                elif signal == -1:  # Sell signal
                    if position is None or position['side'] == 'long':
                        # Close long position if exists
                        if position:
                            exit_price = current_price * (1 - self.slippage)
                            pnl = (exit_price - position['entry_price']) * position['quantity']
                            pnl_pct = pnl / (position['entry_price'] * position['quantity']) * 100
                            
                            trades.append(Trade(
                                entry_date=position['entry_date'],
                                exit_date=str(current_date.date()),
                                entry_price=position['entry_price'],
                                exit_price=exit_price,
                                quantity=position['quantity'],
                                side='long',
                                pnl=pnl,
                                pnl_pct=pnl_pct,
                                duration=(current_date - pd.to_datetime(position['entry_date'])).days,
                                signal_strength=0.5
                            ))
                            
                            capital += pnl
                        
                        # Open short position
                        entry_price = current_price * (1 - self.slippage)
                        quantity = int((capital * self.position_size) / entry_price)
                        
                        if quantity > 0:
                            position = {
                                'side': 'short',
                                'entry_date': str(current_date.date()),
                                'entry_price': entry_price,
                                'quantity': quantity
                            }
            
            # Close final position if exists
            if position:
                final_price = data['Close'].iloc[-1]
                if position['side'] == 'long':
                    exit_price = final_price * (1 - self.slippage)
                    pnl = (exit_price - position['entry_price']) * position['quantity']
                else:
                    exit_price = final_price * (1 + self.slippage)
                    pnl = (position['entry_price'] - exit_price) * position['quantity']
                
                pnl_pct = pnl / (position['entry_price'] * position['quantity']) * 100
                
                trades.append(Trade(
                    entry_date=position['entry_date'],
                    exit_date=str(data.index[-1].date()),
                    entry_price=position['entry_price'],
                    exit_price=exit_price,
                    quantity=position['quantity'],
                    side=position['side'],
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    duration=(data.index[-1] - pd.to_datetime(position['entry_date'])).days,
                    signal_strength=0.5
                ))
                
        except Exception as e:
            st.error(f"Trade execution error: {e}")
        
        return trades
    
    def _calculate_performance(self, trades: List[Trade], data: pd.DataFrame) -> BacktestResults:
        """Calculate comprehensive performance metrics"""
        try:
            if not trades:
                return self._empty_results()
            
            # Basic metrics
            total_pnl = sum(trade.pnl for trade in trades)
            total_return = total_pnl / self.initial_capital * 100
            
            # Win rate
            winning_trades = [t for t in trades if t.pnl > 0]
            losing_trades = [t for t in trades if t.pnl <= 0]
            win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
            
            # Profit factor
            gross_profit = sum(t.pnl for t in winning_trades)
            gross_loss = abs(sum(t.pnl for t in losing_trades))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Duration analysis
            avg_duration = np.mean([t.duration for t in trades]) if trades else 0
            
            # Best and worst trades
            best_trade = max(trades, key=lambda t: t.pnl_pct).pnl_pct if trades else 0
            worst_trade = min(trades, key=lambda t: t.pnl_pct).pnl_pct if trades else 0
            
            # Equity curve and drawdown
            equity_curve = [self.initial_capital]
            running_total = self.initial_capital
            peak_equity = self.initial_capital
            max_drawdown = 0
            drawdown_curve = [0]
            
            for trade in trades:
                running_total += trade.pnl
                equity_curve.append(running_total)
                
                if running_total > peak_equity:
                    peak_equity = running_total
                
                drawdown = (peak_equity - running_total) / peak_equity * 100
                drawdown_curve.append(drawdown)
                
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # Sharpe ratio (simplified)
            if trades:
                returns = [t.pnl_pct for t in trades]
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Annualized return
            days_total = (pd.to_datetime(trades[-1].exit_date) - pd.to_datetime(trades[0].entry_date)).days
            annual_return = total_return * (365 / days_total) if days_total > 0 else 0
            
            return BacktestResults(
                total_return=total_return,
                annual_return=annual_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_trades=len(trades),
                avg_trade_duration=avg_duration,
                best_trade=best_trade,
                worst_trade=worst_trade,
                trades=trades,
                equity_curve=equity_curve,
                drawdown_curve=drawdown_curve
            )
            
        except Exception as e:
            st.error(f"Performance calculation error: {e}")
            return self._empty_results()
    
    def _empty_results(self) -> BacktestResults:
        """Return empty results for error cases"""
        return BacktestResults(
            total_return=0, annual_return=0, sharpe_ratio=0, max_drawdown=0,
            win_rate=0, profit_factor=0, total_trades=0, avg_trade_duration=0,
            best_trade=0, worst_trade=0, trades=[], equity_curve=[100000], 
            drawdown_curve=[0]
        )
    
    def create_backtest_charts(self, results: BacktestResults, symbol: str) -> go.Figure:
        """Create comprehensive backtest visualization"""
        try:
            fig = make_subplots(
                rows=3, cols=2,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(
                    'Equity Curve', 'Drawdown Curve',
                    'Trade Distribution', 'Monthly Returns',
                    'Trade Timeline', 'Performance Metrics'
                ),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}],
                       [{"colspan": 2}, None]]
            )
            
            # Equity curve
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(results.equity_curve))),
                    y=results.equity_curve,
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='green', width=2)
                ),
                row=1, col=1
            )
            
            # Drawdown curve
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(results.drawdown_curve))),
                    y=[-d for d in results.drawdown_curve],
                    mode='lines',
                    name='Drawdown %',
                    fill='tonexty',
                    line=dict(color='red', width=1),
                    fillcolor='rgba(255, 0, 0, 0.3)'
                ),
                row=1, col=2
            )
            
            # Trade distribution
            if results.trades:
                trade_returns = [t.pnl_pct for t in results.trades]
                fig.add_trace(
                    go.Histogram(
                        x=trade_returns,
                        nbinsx=20,
                        name='Trade Returns',
                        marker_color='blue',
                        opacity=0.7
                    ),
                    row=2, col=1
                )
            
            # Performance metrics table
            metrics_text = f"""
            <b>Performance Summary</b><br>
            Total Return: {results.total_return:.2f}%<br>
            Annual Return: {results.annual_return:.2f}%<br>
            Sharpe Ratio: {results.sharpe_ratio:.2f}<br>
            Max Drawdown: {results.max_drawdown:.2f}%<br>
            Win Rate: {results.win_rate:.1f}%<br>
            Profit Factor: {results.profit_factor:.2f}<br>
            Total Trades: {results.total_trades}<br>
            Avg Duration: {results.avg_trade_duration:.1f} days<br>
            Best Trade: {results.best_trade:.2f}%<br>
            Worst Trade: {results.worst_trade:.2f}%
            """
            
            fig.add_annotation(
                text=metrics_text,
                xref="x domain", yref="y domain",
                x=0.02, y=0.98,
                xanchor="left", yanchor="top",
                showarrow=False,
                font=dict(size=12),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="black",
                borderwidth=1,
                row=2, col=2
            )
            
            # Trade timeline
            if results.trades:
                trade_dates = [pd.to_datetime(t.entry_date) for t in results.trades]
                trade_pnl = [t.pnl_pct for t in results.trades]
                colors = ['green' if pnl > 0 else 'red' for pnl in trade_pnl]
                
                fig.add_trace(
                    go.Scatter(
                        x=trade_dates,
                        y=trade_pnl,
                        mode='markers',
                        name='Individual Trades',
                        marker=dict(
                            color=colors,
                            size=8,
                            opacity=0.7
                        ),
                        text=[f"Trade {i+1}: {pnl:.2f}%" for i, pnl in enumerate(trade_pnl)],
                        hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
                    ),
                    row=3, col=1
                )
            
            fig.update_layout(
                title=f"📊 {symbol} - Backtest Results Analysis",
                height=1000,
                showlegend=True,
                template='plotly_dark'
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Chart error: {e}", 
                             xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
    
    def optimize_strategy(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """Optimize strategy parameters"""
        try:
            best_params = {}
            best_return = -float('inf')
            
            # Parameter ranges to test
            rsi_oversold_range = [20, 25, 30, 35]
            rsi_overbought_range = [65, 70, 75, 80]
            
            for oversold in rsi_oversold_range:
                for overbought in rsi_overbought_range:
                    # Run backtest with these parameters
                    results = self.backtest_strategy(
                        symbol, start_date, end_date,
                        rsi_oversold=oversold,
                        rsi_overbought=overbought
                    )
                    
                    if results.total_return > best_return:
                        best_return = results.total_return
                        best_params = {
                            'rsi_oversold': oversold,
                            'rsi_overbought': overbought,
                            'return': best_return
                        }
            
            return best_params
            
        except Exception as e:
            st.error(f"Optimization error: {e}")
            return {}


class PortfolioBacktester:
    """Multi-asset portfolio backtesting"""
    
    def __init__(self):
        self.backtester = AdvancedBacktester()
    
    def backtest_portfolio(self, symbols: List[str], weights: List[float], 
                          start_date: str, end_date: str) -> Dict:
        """Backtest a portfolio of assets"""
        try:
            portfolio_results = {}
            
            for symbol, weight in zip(symbols, weights):
                results = self.backtester.backtest_strategy(symbol, start_date, end_date)
                portfolio_results[symbol] = {
                    'results': results,
                    'weight': weight,
                    'weighted_return': results.total_return * weight
                }
            
            # Calculate portfolio metrics
            total_return = sum(r['weighted_return'] for r in portfolio_results.values())
            
            return {
                'individual_results': portfolio_results,
                'portfolio_return': total_return,
                'portfolio_sharpe': self._calculate_portfolio_sharpe(portfolio_results)
            }
            
        except Exception as e:
            st.error(f"Portfolio backtest error: {e}")
            return {}
    
    def _calculate_portfolio_sharpe(self, results: Dict) -> float:
        """Calculate portfolio Sharpe ratio"""
        try:
            weighted_sharpes = [r['results'].sharpe_ratio * r['weight'] 
                              for r in results.values()]
            return sum(weighted_sharpes)
        except:
            return 0
