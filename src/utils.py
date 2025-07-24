import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_market_data(symbol: str, period: str = "1d", interval: str = "1m") -> Optional[pd.DataFrame]:
    """
    Get market data from Yahoo Finance
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'PLTR')
        period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Adjust period and interval for compatibility
        if interval in ['1m', '2m', '5m'] and period not in ['1d', '5d']:
            period = '1d'  # Intraday data only available for recent periods
        
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            logger.warning(f"No data found for {symbol}")
            return None
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Missing required columns for {symbol}")
            return None
        
        logger.info(f"Retrieved {len(data)} data points for {symbol}")
        return data
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None

def get_current_price(symbol: str) -> Optional[float]:
    """Get current price for a symbol"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try different price fields
        price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose']
        
        for field in price_fields:
            if field in info and info[field]:
                return float(info[field])
        
        # Fallback to recent data
        data = get_market_data(symbol, period='1d', interval='1m')
        if data is not None and not data.empty:
            return float(data['Close'].iloc[-1])
        
        logger.warning(f"Could not get current price for {symbol}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting current price for {symbol}: {e}")
        return None

def get_market_status() -> Dict[str, Any]:
    """Get current market status"""
    try:
        # Get market data for SPY to check if market is open
        spy_data = get_market_data('SPY', period='1d', interval='1m')
        
        now = datetime.now()
        market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
        is_market_hours = market_open_time <= now <= market_close_time
        
        # Check if we have recent data (within last 10 minutes)
        has_recent_data = False
        if spy_data is not None and not spy_data.empty:
            latest_data_time = spy_data.index[-1].to_pydatetime()
            time_diff = now - latest_data_time.replace(tzinfo=None)
            has_recent_data = time_diff.total_seconds() < 600  # 10 minutes
        
        is_open = is_weekday and is_market_hours and has_recent_data
        
        return {
            'is_open': is_open,
            'is_weekday': is_weekday,
            'is_market_hours': is_market_hours,
            'has_recent_data': has_recent_data,
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'market_open': market_open_time.strftime('%H:%M'),
            'market_close': market_close_time.strftime('%H:%M')
        }
        
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        return {
            'is_open': False,
            'error': str(e)
        }

def get_multiple_prices(symbols: list) -> Dict[str, float]:
    """Get current prices for multiple symbols"""
    prices = {}
    
    try:
        # Use yfinance to get multiple tickers at once
        tickers = yf.Tickers(' '.join(symbols))
        
        for symbol in symbols:
            try:
                ticker = tickers.tickers[symbol]
                info = ticker.info
                
                # Try different price fields
                price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose']
                
                for field in price_fields:
                    if field in info and info[field]:
                        prices[symbol] = float(info[field])
                        break
                else:
                    # Fallback to recent data
                    data = ticker.history(period='1d', interval='1m')
                    if not data.empty:
                        prices[symbol] = float(data['Close'].iloc[-1])
                    else:
                        prices[symbol] = None
                        
            except Exception as e:
                logger.error(f"Error getting price for {symbol}: {e}")
                prices[symbol] = None
        
        return prices
        
    except Exception as e:
        logger.error(f"Error getting multiple prices: {e}")
        return {symbol: None for symbol in symbols}

def calculate_percent_change(current_price: float, previous_price: float) -> float:
    """Calculate percentage change between two prices"""
    if previous_price == 0:
        return 0.0
    return ((current_price - previous_price) / previous_price) * 100

def format_price(price: Optional[float]) -> str:
    """Format price for display"""
    if price is None:
        return "N/A"
    return f"${price:.2f}"

def format_percent(percent: float) -> str:
    """Format percentage for display with color indicator"""
    if percent > 0:
        return f"+{percent:.2f}%"
    elif percent < 0:
        return f"{percent:.2f}%"
    else:
        return "0.00%"

def get_company_info(symbol: str) -> Dict[str, Any]:
    """Get company information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'company_name': info.get('longName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', None),
            'dividend_yield': info.get('dividendYield', None),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', None)
        }
        
    except Exception as e:
        logger.error(f"Error getting company info for {symbol}: {e}")
        return {
            'symbol': symbol,
            'error': str(e)
        }

def validate_symbol(symbol: str) -> bool:
    """Validate if a stock symbol exists"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if we got valid info
        return 'symbol' in info or 'shortName' in info or 'longName' in info
        
    except Exception as e:
        logger.error(f"Error validating symbol {symbol}: {e}")
        return False

def get_premarket_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Get pre-market data if available"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get pre-market data (if available)
        premarket_data = ticker.history(period='1d', interval='1m', prepost=True)
        
        if premarket_data.empty:
            return None
        
        # Filter for pre-market hours (4:00 AM - 9:30 AM EST)
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        premarket_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
        
        # Filter data for pre-market hours
        premarket_data = premarket_data[
            (premarket_data.index.time >= premarket_start.time()) &
            (premarket_data.index.time < market_open.time())
        ]
        
        if premarket_data.empty:
            return None
        
        current_premarket_price = premarket_data['Close'].iloc[-1]
        previous_close = ticker.info.get('previousClose', current_premarket_price)
        
        percent_change = calculate_percent_change(current_premarket_price, previous_close)
        
        return {
            'symbol': symbol,
            'premarket_price': current_premarket_price,
            'previous_close': previous_close,
            'percent_change': percent_change,
            'volume': premarket_data['Volume'].sum(),
            'timestamp': premarket_data.index[-1]
        }
        
    except Exception as e:
        logger.error(f"Error getting premarket data for {symbol}: {e}")
        return None

def get_after_hours_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Get after-hours data if available"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get after-hours data
        afterhours_data = ticker.history(period='1d', interval='1m', prepost=True)
        
        if afterhours_data.empty:
            return None
        
        # Filter for after-hours (4:00 PM - 8:00 PM EST)
        now = datetime.now()
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        afterhours_end = now.replace(hour=20, minute=0, second=0, microsecond=0)
        
        # Filter data for after-hours
        afterhours_data = afterhours_data[
            (afterhours_data.index.time >= market_close.time()) &
            (afterhours_data.index.time <= afterhours_end.time())
        ]
        
        if afterhours_data.empty:
            return None
        
        current_ah_price = afterhours_data['Close'].iloc[-1]
        regular_close = ticker.info.get('regularMarketPreviousClose', current_ah_price)
        
        percent_change = calculate_percent_change(current_ah_price, regular_close)
        
        return {
            'symbol': symbol,
            'afterhours_price': current_ah_price,
            'regular_close': regular_close,
            'percent_change': percent_change,
            'volume': afterhours_data['Volume'].sum(),
            'timestamp': afterhours_data.index[-1]
        }
        
    except Exception as e:
        logger.error(f"Error getting after-hours data for {symbol}: {e}")
        return None

def batch_get_market_data(symbols: list, period: str = "1d", interval: str = "1m") -> Dict[str, pd.DataFrame]:
    """Get market data for multiple symbols efficiently"""
    data_dict = {}
    
    try:
        # Process symbols in batches to avoid rate limits
        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            
            for symbol in batch_symbols:
                data = get_market_data(symbol, period, interval)
                if data is not None:
                    data_dict[symbol] = data
                
                # Small delay to respect rate limits
                time.sleep(0.1)
        
        return data_dict
        
    except Exception as e:
        logger.error(f"Error in batch market data retrieval: {e}")
        return {}

def is_trading_day() -> bool:
    """Check if today is a trading day (not weekend or holiday)"""
    now = datetime.now()
    
    # Check if it's a weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Basic holiday check (extend as needed)
    holidays_2025 = [
        datetime(2025, 1, 1),   # New Year's Day
        datetime(2025, 1, 20),  # Martin Luther King Jr. Day
        datetime(2025, 2, 17),  # Presidents' Day
        datetime(2025, 4, 18),  # Good Friday
        datetime(2025, 5, 26),  # Memorial Day
        datetime(2025, 7, 4),   # Independence Day
        datetime(2025, 9, 1),   # Labor Day
        datetime(2025, 11, 27), # Thanksgiving
        datetime(2025, 12, 25), # Christmas
    ]
    
    today = now.date()
    for holiday in holidays_2025:
        if holiday.date() == today:
            return False
    
    return True
