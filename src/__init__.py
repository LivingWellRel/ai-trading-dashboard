"""
AI Trading Dashboard Package
"""

__version__ = "1.0.0"
__author__ = "AI Trading Dashboard Team"
__description__ = "Mobile-friendly AI trading dashboard with live technical indicators and smart alerts"

from .indicators import TechnicalIndicators
from .portfolio import PortfolioManager
from .alerts import AlertManager
# from .voice import VoiceCommands  # Commented out to avoid import issues
from .config import Config
from .utils import (
    get_market_data,
    get_current_price,
    get_market_status,
    get_multiple_prices,
    format_price,
    format_percent
)

__all__ = [
    'TechnicalIndicators',
    'PortfolioManager', 
    'AlertManager',
    # 'VoiceCommands',  # Commented out to avoid import issues
    'Config',
    'get_market_data',
    'get_current_price',
    'get_market_status',
    'get_multiple_prices',
    'format_price',
    'format_percent'
]
