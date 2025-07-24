"""
Enhanced Google Sheets Portfolio Manager
Professional portfolio tracking with real-time sync and advanced analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    st.warning("⚠️ Google Sheets features require gspread and google-auth packages")

class EnhancedPortfolioManager:
    """Professional portfolio management with Google Sheets integration"""
    
    def __init__(self):
        self.spreadsheet_id = st.secrets.get("google_sheets", {}).get("spreadsheet_id")
        self.service_account_info = st.secrets.get("google_sheets", {}).get("service_account")
        
        self.gc = None
        self.sheet = None
        self.portfolio_data = pd.DataFrame()
        
        if GSPREAD_AVAILABLE and self.service_account_info:
            self.setup_google_sheets()
    
    def setup_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Create credentials
            creds = Credentials.from_service_account_info(
                self.service_account_info, 
                scopes=scope
            )
            
            # Authorize and open spreadsheet
            self.gc = gspread.authorize(creds)
            
            if self.spreadsheet_id:
                self.sheet = self.gc.open_by_key(self.spreadsheet_id)
            else:
                # Create new spreadsheet
                self.sheet = self.gc.create("AI Trading Portfolio")
                st.info(f"📊 Created new portfolio spreadsheet: {self.sheet.url}")
            
            # Initialize worksheets
            self.setup_worksheets()
            
            logger.info("Google Sheets connection established")
            
        except Exception as e:
            logger.error(f"Google Sheets setup failed: {e}")
            st.error(f"❌ Google Sheets connection failed: {e}")
    
    def setup_worksheets(self):
        """Setup required worksheets"""
        try:
            required_sheets = [
                'Portfolio', 'Transactions', 'Performance', 
                'Watchlist', 'Alerts', 'Analytics'
            ]
            
            existing_sheets = [ws.title for ws in self.sheet.worksheets()]
            
            for sheet_name in required_sheets:
                if sheet_name not in existing_sheets:
                    self.create_worksheet(sheet_name)
            
            logger.info("Worksheets setup completed")
            
        except Exception as e:
            logger.error(f"Worksheet setup failed: {e}")
    
    def create_worksheet(self, sheet_name: str):
        """Create and setup individual worksheet"""
        try:
            worksheet = self.sheet.add_worksheet(title=sheet_name, rows=1000, cols=26)
            
            if sheet_name == 'Portfolio':
                headers = [
                    'Symbol', 'Shares', 'Avg_Cost', 'Current_Price', 'Market_Value',
                    'Total_Cost', 'Unrealized_PnL', 'Unrealized_PnL_Pct', 'Sector',
                    'Last_Updated', 'RSI', 'Supertrend_Signal', 'MACD_Signal',
                    'Signal_Strength', 'Risk_Level', 'Target_Price', 'Stop_Loss',
                    'Days_Held', 'Dividend_Yield', 'Beta', 'PE_Ratio'
                ]
            
            elif sheet_name == 'Transactions':
                headers = [
                    'Date', 'Time', 'Symbol', 'Action', 'Shares', 'Price',
                    'Total_Amount', 'Commission', 'Net_Amount', 'Account',
                    'Order_Type', 'Signal_Source', 'Confidence', 'Notes'
                ]
            
            elif sheet_name == 'Performance':
                headers = [
                    'Date', 'Portfolio_Value', 'Daily_PnL', 'Daily_PnL_Pct',
                    'Total_PnL', 'Total_PnL_Pct', 'Cash_Balance', 'Buying_Power',
                    'SPY_Price', 'SPY_Return', 'Alpha', 'Beta', 'Sharpe_Ratio',
                    'Max_Drawdown', 'Win_Rate', 'Avg_Win', 'Avg_Loss'
                ]
            
            elif sheet_name == 'Watchlist':
                headers = [
                    'Symbol', 'Current_Price', 'Change_Pct', 'RSI', 'Supertrend',
                    'MACD', 'Signal_Strength', 'Alert_Price', 'Alert_Type',
                    'Date_Added', 'Notes', 'Priority', 'Sector'
                ]
            
            elif sheet_name == 'Alerts':
                headers = [
                    'Date', 'Time', 'Symbol', 'Alert_Type', 'Message',
                    'Price', 'Trigger_Value', 'Status', 'Action_Taken'
                ]
            
            elif sheet_name == 'Analytics':
                headers = [
                    'Metric', 'Value', 'Benchmark', 'Percentile', 'Trend',
                    'Last_Updated', 'Description'
                ]
            
            else:
                headers = ['Column1', 'Column2', 'Column3']
            
            worksheet.append_row(headers)
            
            # Format headers
            worksheet.format('1:1', {
                'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            
            logger.info(f"Created worksheet: {sheet_name}")
            
        except Exception as e:
            logger.error(f"Failed to create worksheet {sheet_name}: {e}")
    
    def sync_portfolio_data(self) -> bool:
        """Sync portfolio data with Google Sheets"""
        if not self.sheet:
            return False
        
        try:
            # Get portfolio worksheet
            portfolio_ws = self.sheet.worksheet('Portfolio')
            
            # Get current holdings from sheet
            data = portfolio_ws.get_all_records()
            
            if data:
                self.portfolio_data = pd.DataFrame(data)
                
                # Update with current market prices
                self.update_market_prices()
                
                # Calculate metrics
                self.calculate_portfolio_metrics()
                
                # Update sheet with new data
                self.write_portfolio_data()
                
                logger.info("Portfolio data synced successfully")
                return True
            else:
                logger.info("No portfolio data found in sheets")
                return False
                
        except Exception as e:
            logger.error(f"Portfolio sync failed: {e}")
            return False
    
    def update_market_prices(self):
        """Update current market prices for all holdings"""
        if self.portfolio_data.empty:
            return
        
        try:
            symbols = self.portfolio_data['Symbol'].tolist()
            
            # Batch download prices
            price_data = yf.download(
                symbols, 
                period="1d", 
                interval="1d",
                group_by='ticker'
            )
            
            for symbol in symbols:
                try:
                    if len(symbols) == 1:
                        current_price = price_data['Close'].iloc[-1]
                    else:
                        current_price = price_data[symbol]['Close'].iloc[-1]
                    
                    # Update portfolio data
                    mask = self.portfolio_data['Symbol'] == symbol
                    self.portfolio_data.loc[mask, 'Current_Price'] = current_price
                    self.portfolio_data.loc[mask, 'Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Calculate market value and P&L
                    shares = float(self.portfolio_data.loc[mask, 'Shares'].iloc[0])
                    avg_cost = float(self.portfolio_data.loc[mask, 'Avg_Cost'].iloc[0])
                    
                    market_value = shares * current_price
                    total_cost = shares * avg_cost
                    unrealized_pnl = market_value - total_cost
                    unrealized_pnl_pct = (unrealized_pnl / total_cost) * 100 if total_cost > 0 else 0
                    
                    self.portfolio_data.loc[mask, 'Market_Value'] = market_value
                    self.portfolio_data.loc[mask, 'Total_Cost'] = total_cost
                    self.portfolio_data.loc[mask, 'Unrealized_PnL'] = unrealized_pnl
                    self.portfolio_data.loc[mask, 'Unrealized_PnL_Pct'] = unrealized_pnl_pct
                    
                except Exception as e:
                    logger.error(f"Price update failed for {symbol}: {e}")
                    continue
            
            logger.info("Market prices updated")
            
        except Exception as e:
            logger.error(f"Market price update failed: {e}")
    
    def calculate_portfolio_metrics(self):
        """Calculate advanced portfolio metrics"""
        if self.portfolio_data.empty:
            return
        
        try:
            # Import technical indicators
            from .indicators import TechnicalIndicators
            indicators = TechnicalIndicators()
            
            for index, row in self.portfolio_data.iterrows():
                symbol = row['Symbol']
                
                try:
                    # Get technical indicators
                    data = yf.download(symbol, period="3mo", interval="1d")
                    
                    if not data.empty:
                        indicator_data = indicators.calculate_all_indicators(data)
                        
                        # Update technical signals
                        self.portfolio_data.loc[index, 'RSI'] = indicator_data['rsi']['value']
                        self.portfolio_data.loc[index, 'Supertrend_Signal'] = indicator_data['supertrend']['signal']
                        self.portfolio_data.loc[index, 'MACD_Signal'] = indicator_data['macd']['signal']
                        
                        # Calculate combined signal strength
                        signal_strength = self.calculate_signal_strength(indicator_data)
                        self.portfolio_data.loc[index, 'Signal_Strength'] = signal_strength
                        
                        # Risk assessment
                        risk_level = self.assess_risk_level(indicator_data, row)
                        self.portfolio_data.loc[index, 'Risk_Level'] = risk_level
                        
                        # Price targets
                        current_price = float(row['Current_Price'])
                        self.portfolio_data.loc[index, 'Target_Price'] = current_price * 1.15  # 15% upside
                        self.portfolio_data.loc[index, 'Stop_Loss'] = current_price * 0.92    # 8% downside
                        
                        # Get additional metrics
                        ticker_info = yf.Ticker(symbol)
                        info = ticker_info.info
                        
                        self.portfolio_data.loc[index, 'Sector'] = info.get('sector', 'Unknown')
                        self.portfolio_data.loc[index, 'Dividend_Yield'] = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
                        self.portfolio_data.loc[index, 'Beta'] = info.get('beta', 1.0)
                        self.portfolio_data.loc[index, 'PE_Ratio'] = info.get('trailingPE', 0)
                
                except Exception as e:
                    logger.error(f"Metrics calculation failed for {symbol}: {e}")
                    continue
            
            logger.info("Portfolio metrics calculated")
            
        except Exception as e:
            logger.error(f"Portfolio metric calculation failed: {e}")
    
    def calculate_signal_strength(self, indicators: Dict) -> int:
        """Calculate combined signal strength (0-5)"""
        try:
            strength = 0
            
            # RSI contribution
            rsi_value = indicators['rsi']['value']
            if 30 <= rsi_value <= 70:  # Neutral zone
                strength += 1
            elif rsi_value < 30:  # Oversold - potential buy
                strength += 2
            
            # Supertrend contribution
            if indicators['supertrend']['signal'] == 'BUY':
                strength += 2
            elif indicators['supertrend']['signal'] == 'HOLD':
                strength += 1
            
            # MACD contribution
            if indicators['macd']['signal'] == 'BUY':
                strength += 1
            
            return min(strength, 5)  # Cap at 5
            
        except:
            return 0
    
    def assess_risk_level(self, indicators: Dict, position: pd.Series) -> str:
        """Assess risk level for position"""
        try:
            risk_factors = 0
            
            # Technical risk factors
            rsi_value = indicators['rsi']['value']
            if rsi_value > 80:  # Overbought
                risk_factors += 2
            elif rsi_value > 70:
                risk_factors += 1
            
            # Position size risk
            position_value = float(position.get('Market_Value', 0))
            if position_value > 50000:  # Large position
                risk_factors += 1
            
            # P&L risk
            unrealized_pnl_pct = float(position.get('Unrealized_PnL_Pct', 0))
            if unrealized_pnl_pct < -15:  # Large loss
                risk_factors += 2
            elif unrealized_pnl_pct < -8:
                risk_factors += 1
            
            # Risk level classification
            if risk_factors >= 4:
                return 'HIGH'
            elif risk_factors >= 2:
                return 'MEDIUM'
            else:
                return 'LOW'
                
        except:
            return 'UNKNOWN'
    
    def write_portfolio_data(self):
        """Write updated portfolio data back to sheets"""
        if not self.sheet or self.portfolio_data.empty:
            return
        
        try:
            portfolio_ws = self.sheet.worksheet('Portfolio')
            
            # Clear existing data (except headers)
            portfolio_ws.clear()
            
            # Write headers
            headers = self.portfolio_data.columns.tolist()
            portfolio_ws.append_row(headers)
            
            # Write data
            for _, row in self.portfolio_data.iterrows():
                portfolio_ws.append_row(row.tolist())
            
            # Format the sheet
            self.format_portfolio_sheet(portfolio_ws)
            
            logger.info("Portfolio data written to sheets")
            
        except Exception as e:
            logger.error(f"Failed to write portfolio data: {e}")
    
    def format_portfolio_sheet(self, worksheet):
        """Apply professional formatting to portfolio sheet"""
        try:
            # Header formatting
            worksheet.format('1:1', {
                'backgroundColor': {'red': 0.1, 'green': 0.3, 'blue': 0.6},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            
            # Number formatting for financial columns
            currency_cols = ['Avg_Cost', 'Current_Price', 'Market_Value', 'Total_Cost', 'Unrealized_PnL', 'Target_Price', 'Stop_Loss']
            percentage_cols = ['Unrealized_PnL_Pct', 'Dividend_Yield']
            
            # Apply currency format
            for col in currency_cols:
                try:
                    col_index = self.portfolio_data.columns.get_loc(col) + 1
                    col_letter = chr(64 + col_index)  # Convert to letter
                    worksheet.format(f'{col_letter}2:{col_letter}1000', {
                        'numberFormat': {'type': 'CURRENCY', 'pattern': '$#,##0.00'}
                    })
                except:
                    continue
            
            # Apply percentage format
            for col in percentage_cols:
                try:
                    col_index = self.portfolio_data.columns.get_loc(col) + 1
                    col_letter = chr(64 + col_index)
                    worksheet.format(f'{col_letter}2:{col_letter}1000', {
                        'numberFormat': {'type': 'PERCENT', 'pattern': '0.00%'}
                    })
                except:
                    continue
            
            logger.info("Portfolio sheet formatted")
            
        except Exception as e:
            logger.error(f"Sheet formatting failed: {e}")
    
    def add_transaction(self, symbol: str, action: str, shares: float, 
                       price: float, signal_source: str = "Manual", 
                       confidence: int = 0, notes: str = "") -> bool:
        """Add transaction to portfolio and sheets"""
        try:
            # Calculate transaction details
            total_amount = shares * price
            commission = 0  # Assuming commission-free trading
            net_amount = total_amount + commission if action == "BUY" else total_amount - commission
            
            # Create transaction record
            transaction = {
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Time': datetime.now().strftime('%H:%M:%S'),
                'Symbol': symbol,
                'Action': action,
                'Shares': shares,
                'Price': price,
                'Total_Amount': total_amount,
                'Commission': commission,
                'Net_Amount': net_amount,
                'Account': 'Main',
                'Order_Type': 'Market',
                'Signal_Source': signal_source,
                'Confidence': confidence,
                'Notes': notes
            }
            
            # Add to transactions sheet
            if self.sheet:
                trans_ws = self.sheet.worksheet('Transactions')
                trans_ws.append_row(list(transaction.values()))
            
            # Update portfolio holdings
            self.update_portfolio_position(symbol, action, shares, price)
            
            logger.info(f"Transaction added: {action} {shares} {symbol} @ ${price}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add transaction: {e}")
            return False
    
    def update_portfolio_position(self, symbol: str, action: str, shares: float, price: float):
        """Update portfolio position after transaction"""
        try:
            if self.portfolio_data.empty:
                self.portfolio_data = pd.DataFrame()
            
            # Check if position exists
            existing_position = self.portfolio_data[self.portfolio_data['Symbol'] == symbol]
            
            if existing_position.empty and action == "BUY":
                # New position
                new_position = {
                    'Symbol': symbol,
                    'Shares': shares,
                    'Avg_Cost': price,
                    'Current_Price': price,
                    'Market_Value': shares * price,
                    'Total_Cost': shares * price,
                    'Unrealized_PnL': 0,
                    'Unrealized_PnL_Pct': 0,
                    'Sector': 'Unknown',
                    'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Days_Held': 0
                }
                
                self.portfolio_data = pd.concat([
                    self.portfolio_data, 
                    pd.DataFrame([new_position])
                ], ignore_index=True)
                
            elif not existing_position.empty:
                # Update existing position
                index = existing_position.index[0]
                current_shares = float(self.portfolio_data.loc[index, 'Shares'])
                current_avg_cost = float(self.portfolio_data.loc[index, 'Avg_Cost'])
                
                if action == "BUY":
                    # Add to position
                    new_shares = current_shares + shares
                    new_avg_cost = ((current_shares * current_avg_cost) + (shares * price)) / new_shares
                    
                    self.portfolio_data.loc[index, 'Shares'] = new_shares
                    self.portfolio_data.loc[index, 'Avg_Cost'] = new_avg_cost
                    
                elif action == "SELL":
                    # Reduce position
                    new_shares = current_shares - shares
                    
                    if new_shares <= 0:
                        # Position closed
                        self.portfolio_data = self.portfolio_data.drop(index)
                    else:
                        self.portfolio_data.loc[index, 'Shares'] = new_shares
            
            # Recalculate metrics
            self.update_market_prices()
            
            logger.info(f"Portfolio position updated for {symbol}")
            
        except Exception as e:
            logger.error(f"Position update failed: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        try:
            if self.portfolio_data.empty:
                return {
                    'total_value': 0,
                    'total_cost': 0,
                    'total_pnl': 0,
                    'total_pnl_pct': 0,
                    'positions': 0,
                    'top_performers': [],
                    'worst_performers': [],
                    'risk_distribution': {}
                }
            
            # Calculate totals
            total_value = self.portfolio_data['Market_Value'].sum()
            total_cost = self.portfolio_data['Total_Cost'].sum()
            total_pnl = self.portfolio_data['Unrealized_PnL'].sum()
            total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
            
            # Get top/worst performers
            sorted_by_pnl = self.portfolio_data.sort_values('Unrealized_PnL_Pct', ascending=False)
            
            top_performers = []
            worst_performers = []
            
            for _, row in sorted_by_pnl.head(3).iterrows():
                top_performers.append({
                    'symbol': row['Symbol'],
                    'pnl_pct': row['Unrealized_PnL_Pct'],
                    'pnl': row['Unrealized_PnL']
                })
            
            for _, row in sorted_by_pnl.tail(3).iterrows():
                worst_performers.append({
                    'symbol': row['Symbol'],
                    'pnl_pct': row['Unrealized_PnL_Pct'],
                    'pnl': row['Unrealized_PnL']
                })
            
            # Risk distribution
            risk_distribution = self.portfolio_data.groupby('Risk_Level')['Market_Value'].sum().to_dict()
            
            return {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_pnl': total_pnl,
                'total_pnl_pct': total_pnl_pct,
                'positions': len(self.portfolio_data),
                'top_performers': top_performers,
                'worst_performers': worst_performers,
                'risk_distribution': risk_distribution,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Portfolio summary failed: {e}")
            return {}
    
    def update_performance_tracking(self):
        """Update daily performance tracking"""
        try:
            if not self.sheet:
                return
            
            performance_ws = self.sheet.worksheet('Performance')
            summary = self.get_portfolio_summary()
            
            # Get SPY data for benchmark
            spy_data = yf.download("SPY", period="2d", interval="1d")
            spy_return = 0
            
            if not spy_data.empty and len(spy_data) >= 2:
                spy_current = spy_data['Close'].iloc[-1]
                spy_previous = spy_data['Close'].iloc[-2]
                spy_return = ((spy_current - spy_previous) / spy_previous) * 100
            
            # Create performance record
            performance_record = [
                datetime.now().strftime('%Y-%m-%d'),
                summary.get('total_value', 0),
                summary.get('total_pnl', 0),  # Daily P&L (simplified)
                summary.get('total_pnl_pct', 0),  # Daily P&L %
                summary.get('total_pnl', 0),  # Total P&L
                summary.get('total_pnl_pct', 0),  # Total P&L %
                0,  # Cash balance (placeholder)
                0,  # Buying power (placeholder)
                spy_data['Close'].iloc[-1] if not spy_data.empty else 0,
                spy_return,
                summary.get('total_pnl_pct', 0) - spy_return,  # Alpha
                1.0,  # Beta (placeholder)
                0,  # Sharpe ratio (placeholder)
                0,  # Max drawdown (placeholder)
                0,  # Win rate (placeholder)
                0,  # Avg win (placeholder)
                0   # Avg loss (placeholder)
            ]
            
            performance_ws.append_row(performance_record)
            
            logger.info("Performance tracking updated")
            
        except Exception as e:
            logger.error(f"Performance tracking failed: {e}")
    
    def get_risk_analysis(self) -> Dict:
        """Perform comprehensive risk analysis"""
        try:
            if self.portfolio_data.empty:
                return {}
            
            analysis = {
                'position_risk': {},
                'concentration_risk': {},
                'sector_risk': {},
                'technical_risk': {},
                'overall_risk_score': 0
            }
            
            # Position risk analysis
            total_value = self.portfolio_data['Market_Value'].sum()
            
            for _, row in self.portfolio_data.iterrows():
                symbol = row['Symbol']
                position_pct = (row['Market_Value'] / total_value) * 100
                
                risk_score = 0
                if position_pct > 20:  # High concentration
                    risk_score += 3
                elif position_pct > 10:
                    risk_score += 2
                elif position_pct > 5:
                    risk_score += 1
                
                # Add technical risk
                if row['Risk_Level'] == 'HIGH':
                    risk_score += 2
                elif row['Risk_Level'] == 'MEDIUM':
                    risk_score += 1
                
                analysis['position_risk'][symbol] = {
                    'position_pct': position_pct,
                    'risk_level': row['Risk_Level'],
                    'risk_score': risk_score,
                    'unrealized_pnl_pct': row['Unrealized_PnL_Pct']
                }
            
            # Sector concentration analysis
            sector_distribution = self.portfolio_data.groupby('Sector')['Market_Value'].sum()
            sector_pcts = (sector_distribution / total_value) * 100
            
            for sector, pct in sector_pcts.items():
                risk_level = 'HIGH' if pct > 40 else 'MEDIUM' if pct > 25 else 'LOW'
                analysis['sector_risk'][sector] = {
                    'percentage': pct,
                    'risk_level': risk_level
                }
            
            # Overall risk score
            risk_scores = [pos['risk_score'] for pos in analysis['position_risk'].values()]
            analysis['overall_risk_score'] = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            return analysis
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {e}")
            return {}

# Streamlit integration functions
def get_portfolio_manager() -> EnhancedPortfolioManager:
    """Get portfolio manager instance"""
    if 'portfolio_manager' not in st.session_state:
        st.session_state.portfolio_manager = EnhancedPortfolioManager()
    return st.session_state.portfolio_manager

def sync_portfolio() -> bool:
    """Sync portfolio with Google Sheets"""
    manager = get_portfolio_manager()
    return manager.sync_portfolio_data()

def add_trade(symbol: str, action: str, shares: float, price: float) -> bool:
    """Add trade to portfolio"""
    manager = get_portfolio_manager()
    return manager.add_transaction(symbol, action, shares, price, "Dashboard", 75)

def get_portfolio_data() -> pd.DataFrame:
    """Get current portfolio data"""
    manager = get_portfolio_manager()
    return manager.portfolio_data

def get_portfolio_summary() -> Dict:
    """Get portfolio summary"""
    manager = get_portfolio_manager()
    return manager.get_portfolio_summary()
