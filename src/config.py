# -*- coding: utf-8 -*-
"""
Configuration settings for AI Trading Dashboard
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_USERNAME = os.getenv('TELEGRAM_USERNAME', '@SHADOWCLAW007')
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_FROM = os.getenv('TWILIO_PHONE_FROM')
    TWILIO_PHONE_TO = os.getenv('TWILIO_PHONE_TO')
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
    
    # Trading Configuration
    ALERT_TIME = os.getenv('ALERT_TIME', '09:25')
    TIMEZONE = os.getenv('TIMEZONE', 'US/Eastern')
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'True').lower() == 'true'
    
    # Dashboard Configuration
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 8501))
    
    # Technical Indicator Settings
    RSI_PERIOD = 14
    RSI_BUY_MIN = 30
    RSI_BUY_MAX = 40
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    SUPERTREND_PERIOD = 10
    SUPERTREND_MULTIPLIER = 3.0
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    # Default watchlist
    DEFAULT_WATCHLIST = ['PLTR', 'NVDA', 'O', 'AGNC', 'AAPL', 'TSLA', 'SPY', 'QQQ']
    
    # Portfolio settings
    DEFAULT_POSITION_SIZE = 100  # Default number of shares
    TRAILING_STOP_PERCENT = 10   # 10% trailing stop
    
    # Alert settings
    MAX_ALERTS_PER_DAY = 20
    ALERT_COOLDOWN_MINUTES = 15
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        warnings = []
        errors = []
        
        # Check required Telegram settings
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        # Check optional but recommended settings
        if not cls.GOOGLE_SHEETS_ID:
            warnings.append("GOOGLE_SHEETS_ID not set - portfolio sync will use mock data")
        
        if not cls.TWILIO_ACCOUNT_SID or not cls.TWILIO_AUTH_TOKEN:
            warnings.append("Twilio credentials not set - SMS alerts disabled")
        
        if not os.path.exists(cls.GOOGLE_SHEETS_CREDENTIALS):
            warnings.append(f"Google Sheets credentials file not found: {cls.GOOGLE_SHEETS_CREDENTIALS}")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

# Market hours configuration
MARKET_HOURS = {
    'premarket_start': '04:00',
    'market_open': '09:30', 
    'market_close': '16:00',
    'afterhours_end': '20:00',
    'timezone': 'US/Eastern'
}

# Color scheme for dashboard
COLORS = {
    'primary': '#1f4e79',
    'secondary': '#2e8b57',
    'success': '#00d4aa',
    'danger': '#ff4b4b',
    'warning': '#ffa500',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Chart styling
CHART_CONFIG = {
    'candlestick_colors': {
        'increasing': '#00d4aa',
        'decreasing': '#ff4b4b'
    },
    'indicator_colors': {
        'rsi': '#9467bd',
        'macd': '#2ca02c',
        'signal': '#ff7f0e',
        'supertrend_up': '#00d4aa',
        'supertrend_down': '#ff4b4b'
    },
    'background_color': '#ffffff',
    'grid_color': '#e6e6e6',
    'text_color': '#333333'
}
