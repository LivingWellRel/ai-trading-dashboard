import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class PortfolioManager:
    """
    Manage portfolio data with Google Sheets integration
    """
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.portfolio_data = {}
        self.holdings = []
        self.buying_power = 0.0
        self.total_value = 0.0
        self.setup_google_sheets()
    
    def setup_google_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Get credentials file path
            creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
            
            if os.path.exists(creds_file):
                # Add credentials
                creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
                self.gc = gspread.authorize(creds)
                
                # Open the spreadsheet
                sheet_id = os.getenv('GOOGLE_SHEETS_ID')
                if sheet_id:
                    self.sheet = self.gc.open_by_key(sheet_id)
            else:
                print(f"Google Sheets credentials file not found: {creds_file}")
                
        except Exception as e:
            print(f"Error setting up Google Sheets: {e}")
    
    def sync_google_sheets(self) -> Dict[str, Any]:
        """Sync portfolio data with Google Sheets"""
        if not self.sheet:
            return self.get_mock_portfolio_data()
        
        try:
            # Get holdings worksheet
            holdings_ws = self.sheet.worksheet("Holdings")
            holdings_data = holdings_ws.get_all_records()
            
            # Get account info
            account_ws = self.sheet.worksheet("Account")
            account_data = account_ws.get_all_records()
            
            # Process holdings
            self.holdings = []
            total_value = 0.0
            
            for row in holdings_data:
                if row.get('Symbol'):
                    holding = {
                        'symbol': row['Symbol'],
                        'shares': float(row.get('Shares', 0)),
                        'avg_cost': float(row.get('Avg_Cost', 0)),
                        'current_price': float(row.get('Current_Price', 0)),
                        'market_value': float(row.get('Shares', 0)) * float(row.get('Current_Price', 0)),
                        'unrealized_pnl': (float(row.get('Current_Price', 0)) - float(row.get('Avg_Cost', 0))) * float(row.get('Shares', 0))
                    }
                    self.holdings.append(holding)
                    total_value += holding['market_value']
            
            # Process account info
            for row in account_data:
                if row.get('Item') == 'Buying_Power':
                    self.buying_power = float(row.get('Value', 0))
            
            self.total_value = total_value + self.buying_power
            
            return {
                'holdings': self.holdings,
                'buying_power': self.buying_power,
                'total_value': self.total_value,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error syncing with Google Sheets: {e}")
            return self.get_mock_portfolio_data()
    
    def get_mock_portfolio_data(self) -> Dict[str, Any]:
        """Return mock portfolio data for demo purposes"""
        mock_holdings = [
            {
                'symbol': 'PLTR',
                'shares': 100,
                'avg_cost': 15.50,
                'current_price': 18.25,
                'market_value': 1825.00,
                'unrealized_pnl': 275.00
            },
            {
                'symbol': 'NVDA',
                'shares': 25,
                'avg_cost': 220.00,
                'current_price': 275.50,
                'market_value': 6887.50,
                'unrealized_pnl': 1387.50
            },
            {
                'symbol': 'O',
                'shares': 50,
                'avg_cost': 55.00,
                'current_price': 58.25,
                'market_value': 2912.50,
                'unrealized_pnl': 162.50
            },
            {
                'symbol': 'AGNC',
                'shares': 200,
                'avg_cost': 12.50,
                'current_price': 13.75,
                'market_value': 2750.00,
                'unrealized_pnl': 250.00
            }
        ]
        
        self.holdings = mock_holdings
        self.buying_power = 649.78
        self.total_value = sum(h['market_value'] for h in mock_holdings) + self.buying_power
        
        return {
            'holdings': self.holdings,
            'buying_power': self.buying_power,
            'total_value': self.total_value,
            'last_updated': datetime.now().isoformat()
        }
    
    def add_trade(self, symbol: str, action: str, quantity: int, price: float) -> bool:
        """Add a new trade to the portfolio"""
        try:
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol.upper(),
                'action': action.upper(),
                'quantity': quantity,
                'price': price,
                'total_value': quantity * price
            }
            
            if self.sheet:
                # Add to Google Sheets
                trades_ws = self.sheet.worksheet("Trades")
                trades_ws.append_row([
                    trade_data['timestamp'],
                    trade_data['symbol'],
                    trade_data['action'],
                    trade_data['quantity'],
                    trade_data['price'],
                    trade_data['total_value']
                ])
            
            # Update local holdings
            self.update_holdings_after_trade(trade_data)
            
            return True
            
        except Exception as e:
            print(f"Error adding trade: {e}")
            return False
    
    def update_holdings_after_trade(self, trade: Dict[str, Any]):
        """Update holdings after a trade"""
        symbol = trade['symbol']
        action = trade['action']
        quantity = trade['quantity']
        price = trade['price']
        
        # Find existing holding
        holding_index = None
        for i, holding in enumerate(self.holdings):
            if holding['symbol'] == symbol:
                holding_index = i
                break
        
        if action == 'BUY':
            if holding_index is not None:
                # Update existing holding
                current_holding = self.holdings[holding_index]
                total_shares = current_holding['shares'] + quantity
                total_cost = (current_holding['shares'] * current_holding['avg_cost']) + (quantity * price)
                new_avg_cost = total_cost / total_shares
                
                self.holdings[holding_index].update({
                    'shares': total_shares,
                    'avg_cost': new_avg_cost
                })
            else:
                # Add new holding
                self.holdings.append({
                    'symbol': symbol,
                    'shares': quantity,
                    'avg_cost': price,
                    'current_price': price,
                    'market_value': quantity * price,
                    'unrealized_pnl': 0.0
                })
            
            # Reduce buying power
            self.buying_power -= quantity * price
            
        elif action == 'SELL' and holding_index is not None:
            # Reduce shares
            self.holdings[holding_index]['shares'] -= quantity
            
            # Remove holding if no shares left
            if self.holdings[holding_index]['shares'] <= 0:
                self.holdings.pop(holding_index)
            
            # Increase buying power
            self.buying_power += quantity * price
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary statistics"""
        total_market_value = sum(h['market_value'] for h in self.holdings)
        total_unrealized_pnl = sum(h['unrealized_pnl'] for h in self.holdings)
        total_account_value = total_market_value + self.buying_power
        
        return {
            'total_account_value': total_account_value,
            'total_market_value': total_market_value,
            'buying_power': self.buying_power,
            'total_unrealized_pnl': total_unrealized_pnl,
            'unrealized_pnl_percent': (total_unrealized_pnl / (total_market_value - total_unrealized_pnl)) * 100 if total_market_value > total_unrealized_pnl else 0,
            'holdings_count': len(self.holdings)
        }
    
    def get_trailing_stops(self) -> List[Dict[str, Any]]:
        """Get trailing stop alerts"""
        stops = []
        
        for holding in self.holdings:
            # Calculate 10% trailing stop
            stop_price = holding['current_price'] * 0.9
            distance_percent = ((holding['current_price'] - stop_price) / holding['current_price']) * 100
            
            stops.append({
                'symbol': holding['symbol'],
                'current_price': holding['current_price'],
                'stop_price': stop_price,
                'distance_percent': distance_percent,
                'shares': holding['shares'],
                'status': 'Active'
            })
        
        return stops
    
    def get_dividend_calendar(self) -> List[Dict[str, Any]]:
        """Get upcoming dividend payments"""
        # Mock dividend calendar - in production, integrate with dividend API
        dividend_stocks = ['O', 'AGNC']  # REITs typically pay monthly
        
        calendar = []
        for symbol in dividend_stocks:
            if any(h['symbol'] == symbol for h in self.holdings):
                holding = next(h for h in self.holdings if h['symbol'] == symbol)
                
                # Mock next dividend date (last Friday of month)
                next_month = datetime.now().replace(day=1) + timedelta(days=32)
                next_month = next_month.replace(day=1)
                last_friday = next_month.replace(day=1)
                while last_friday.weekday() != 4:  # Friday
                    last_friday += timedelta(days=1)
                
                estimated_dividend = 0.25 if symbol == 'O' else 0.12  # Mock dividend amounts
                
                calendar.append({
                    'symbol': symbol,
                    'ex_date': last_friday.strftime('%Y-%m-%d'),
                    'pay_date': (last_friday + timedelta(days=14)).strftime('%Y-%m-%d'),
                    'dividend_per_share': estimated_dividend,
                    'shares_owned': holding['shares'],
                    'estimated_payment': holding['shares'] * estimated_dividend
                })
        
        return calendar
    
    def calculate_roi(self, period_days: int = 30) -> Dict[str, float]:
        """Calculate ROI for specified period"""
        # Mock ROI calculation - in production, track historical values
        current_value = self.get_portfolio_summary()['total_account_value']
        
        # Assume 2% monthly growth for demo
        monthly_return = 0.02
        daily_return = monthly_return / 30
        period_return = daily_return * period_days
        
        return {
            'period_days': period_days,
            'current_value': current_value,
            'period_return_percent': period_return * 100,
            'period_return_dollars': current_value * period_return,
            'annualized_return': (period_return * (365 / period_days)) * 100
        }
