import pandas as pd
import numpy as np
from typing import Dict, Any

class TechnicalIndicators:
    """
    Calculate technical indicators for trading signals
    """
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI (Relative Strength Index) manually"""
        close = data['Close'].astype(float)
        delta = close.diff()
        
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0).rolling(window=period).mean())
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = data['High']
        low = data['Low'] 
        close = data['Close']
        
        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_supertrend(self, data: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> Dict[str, pd.Series]:
        """Calculate Supertrend indicator"""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate ATR
        atr = self.calculate_atr(data, period)
        
        # Calculate HL2 (typical price)
        hl2 = (high + low) / 2
        
        # Calculate basic upper and lower bands
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        # Initialize arrays
        supertrend = pd.Series(index=data.index, dtype=float)
        direction = pd.Series(index=data.index, dtype=float)
        
        # Set initial values
        supertrend.iloc[0] = close.iloc[0]
        direction.iloc[0] = 1
        
        # Calculate Supertrend
        for i in range(1, len(close)):
            # Upper band calculation
            if upper_band.iloc[i] < upper_band.iloc[i-1] or close.iloc[i-1] > upper_band.iloc[i-1]:
                upper_band.iloc[i] = upper_band.iloc[i]
            else:
                upper_band.iloc[i] = upper_band.iloc[i-1]
            
            # Lower band calculation
            if lower_band.iloc[i] > lower_band.iloc[i-1] or close.iloc[i-1] < lower_band.iloc[i-1]:
                lower_band.iloc[i] = lower_band.iloc[i]
            else:
                lower_band.iloc[i] = lower_band.iloc[i-1]
            
            # Direction calculation
            if close.iloc[i] <= lower_band.iloc[i]:
                direction.iloc[i] = -1
            elif close.iloc[i] >= upper_band.iloc[i]:
                direction.iloc[i] = 1
            else:
                direction.iloc[i] = direction.iloc[i-1]
            
            # Supertrend calculation
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                supertrend.iloc[i] = upper_band.iloc[i]
        
        return {
            'Supertrend': direction,
            'Supertrend_Upper': upper_band,
            'Supertrend_Lower': lower_band
        }
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        close = data['Close']
        
        # Calculate MACD
        ema_fast = self.calculate_ema(close, fast)
        ema_slow = self.calculate_ema(close, slow)
        
        macd = ema_fast - ema_slow
        macd_signal = self.calculate_ema(macd, signal)
        macd_histogram = macd - macd_signal
        
        return {
            'MACD': macd,
            'MACD_Signal': macd_signal,
            'MACD_Histogram': macd_histogram
        }
    
    def calculate_all(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate all technical indicators"""
        indicators = {}
        
        # RSI
        indicators['RSI'] = pd.Series(self.calculate_rsi(data), index=data.index)
        
        # Supertrend
        supertrend_data = self.calculate_supertrend(data)
        indicators.update(supertrend_data)
        
        # MACD
        macd_data = self.calculate_macd(data)
        indicators.update(macd_data)
        
        return indicators
    
    def get_trading_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate trading signals based on combined indicators
        
        Buy Signal Criteria:
        - RSI between 30-40 (oversold but recovering)
        - Supertrend flips from Red to Green
        - MACD crosses above Signal line
        """
        indicators = self.calculate_all(data)
        
        # Current values
        current_rsi = indicators['RSI'].iloc[-1]
        current_supertrend = indicators['Supertrend'].iloc[-1]
        prev_supertrend = indicators['Supertrend'].iloc[-2]
        current_macd = indicators['MACD'].iloc[-1]
        current_macd_signal = indicators['MACD_Signal'].iloc[-1]
        prev_macd = indicators['MACD'].iloc[-2]
        prev_macd_signal = indicators['MACD_Signal'].iloc[-2]
        
        # Signal conditions
        rsi_buy = 30 <= current_rsi <= 40
        supertrend_flip = current_supertrend > 0 and prev_supertrend <= 0
        macd_cross = (current_macd > current_macd_signal) and (prev_macd <= prev_macd_signal)
        
        # Combined signal
        buy_signals = [rsi_buy, supertrend_flip, macd_cross]
        signal_strength = sum(buy_signals)
        
        return {
            'rsi_value': current_rsi,
            'rsi_buy': rsi_buy,
            'supertrend_direction': current_supertrend,
            'supertrend_flip': supertrend_flip,
            'macd_bullish': current_macd > current_macd_signal,
            'macd_cross': macd_cross,
            'signal_strength': signal_strength,
            'strong_buy': signal_strength >= 3,
            'moderate_buy': signal_strength >= 2,
            'timestamp': data.index[-1]
        }
    
    def calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        high_rolling = data['High'].rolling(window=window)
        low_rolling = data['Low'].rolling(window=window)
        
        resistance = high_rolling.max().iloc[-1]
        support = low_rolling.min().iloc[-1]
        
        return {
            'resistance': resistance,
            'support': support,
            'current_price': data['Close'].iloc[-1]
        }
