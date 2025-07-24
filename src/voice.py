import speech_recognition as sr
import threading
import time
from typing import Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

class VoiceCommands:
    """
    Handle voice-to-text commands for trading actions
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.setup_microphone()
        
        # Command patterns
        self.command_patterns = {
            'buy': r'buy\s+(\w+)(?:\s+(\d+))?(?:\s+shares?)?(?:\s+at\s+(\d+\.?\d*))?',
            'sell': r'sell\s+(\w+)(?:\s+(\d+))?(?:\s+shares?)?(?:\s+at\s+(\d+\.?\d*))?',
            'log': r'log\s+(\w+)\s+trade',
            'check': r'check\s+(\w+)(?:\s+price)?',
            'portfolio': r'(?:show|check)\s+portfolio',
            'watchlist': r'(?:show|check)\s+watchlist',
            'alerts': r'(?:enable|disable)\s+alerts',
            'stop': r'stop\s+(?:bot|trading)',
            'help': r'help|commands'
        }
    
    def setup_microphone(self):
        """Initialize microphone for speech recognition"""
        try:
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info("Microphone initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing microphone: {e}")
            self.microphone = None
    
    def listen_for_command(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice command with timeout"""
        if not self.microphone:
            return None
        
        try:
            with self.microphone as source:
                logger.info("Listening for command...")
                
                # Listen with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                # Recognize speech using Google's service
                command = self.recognizer.recognize_google(audio).lower()
                logger.info(f"Voice command recognized: '{command}'")
                
                return command
                
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout")
            return None
        except Exception as e:
            logger.error(f"Error in voice recognition: {e}")
            return None
    
    def process_command(self, command: str) -> str:
        """Process voice command and return response"""
        if not command:
            return "No command recognized"
        
        command = command.lower().strip()
        
        # Check each command pattern
        for command_type, pattern in self.command_patterns.items():
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return self.execute_command(command_type, match.groups(), command)
        
        # If no pattern matches, try to extract basic information
        return self.handle_unknown_command(command)
    
    def execute_command(self, command_type: str, groups: tuple, original_command: str) -> str:
        """Execute the recognized command"""
        try:
            if command_type == 'buy':
                symbol = groups[0].upper() if groups[0] else None
                quantity = int(groups[1]) if groups[1] else 10  # Default quantity
                price = float(groups[2]) if groups[2] else None  # Market order if no price
                
                if symbol:
                    return self.handle_buy_command(symbol, quantity, price)
                else:
                    return "Please specify a stock symbol to buy"
            
            elif command_type == 'sell':
                symbol = groups[0].upper() if groups[0] else None
                quantity = int(groups[1]) if groups[1] else None  # Sell all if no quantity
                price = float(groups[2]) if groups[2] else None  # Market order if no price
                
                if symbol:
                    return self.handle_sell_command(symbol, quantity, price)
                else:
                    return "Please specify a stock symbol to sell"
            
            elif command_type == 'log':
                symbol = groups[0].upper() if groups[0] else None
                if symbol:
                    return f"Logging trade for {symbol}. Please specify buy or sell."
                else:
                    return "Please specify a stock symbol to log"
            
            elif command_type == 'check':
                symbol = groups[0].upper() if groups[0] else None
                if symbol:
                    return f"Checking current price for {symbol}..."
                else:
                    return "Please specify a stock symbol to check"
            
            elif command_type == 'portfolio':
                return "Displaying portfolio overview..."
            
            elif command_type == 'watchlist':
                return "Displaying watchlist..."
            
            elif command_type == 'alerts':
                if 'enable' in original_command:
                    return "Alerts enabled"
                else:
                    return "Alerts disabled"
            
            elif command_type == 'stop':
                return "Trading bot stopped"
            
            elif command_type == 'help':
                return self.get_help_message()
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return f"Error executing command: {str(e)}"
        
        return "Command processed"
    
    def handle_buy_command(self, symbol: str, quantity: int, price: Optional[float]) -> str:
        """Handle buy command"""
        if price:
            return f"Placing limit order: BUY {quantity} shares of {symbol} at ${price:.2f}"
        else:
            return f"Placing market order: BUY {quantity} shares of {symbol}"
    
    def handle_sell_command(self, symbol: str, quantity: Optional[int], price: Optional[float]) -> str:
        """Handle sell command"""
        qty_text = f"{quantity} shares" if quantity else "all shares"
        
        if price:
            return f"Placing limit order: SELL {qty_text} of {symbol} at ${price:.2f}"
        else:
            return f"Placing market order: SELL {qty_text} of {symbol}"
    
    def handle_unknown_command(self, command: str) -> str:
        """Handle unrecognized commands"""
        # Try to extract stock symbols
        symbols = re.findall(r'\b[A-Z]{1,5}\b', command.upper())
        
        if symbols:
            return f"I heard you mention {', '.join(symbols)}. Could you please be more specific about what you want to do?"
        
        # Check for common words
        if any(word in command for word in ['buy', 'purchase', 'get']):
            return "I heard you want to buy something. Please say 'buy [symbol] [quantity]'"
        elif any(word in command for word in ['sell', 'dump', 'exit']):
            return "I heard you want to sell something. Please say 'sell [symbol] [quantity]'"
        elif any(word in command for word in ['price', 'quote', 'value']):
            return "I heard you want to check a price. Please say 'check [symbol] price'"
        
        return f"I didn't understand '{command}'. Say 'help' for available commands."
    
    def get_help_message(self) -> str:
        """Get help message with available commands"""
        return """
Available voice commands:

📈 Trading:
• "Buy PLTR 10 shares" - Buy 10 shares of PLTR
• "Sell NVDA 5 shares at 275" - Sell 5 NVDA at $275
• "Buy AAPL" - Buy AAPL (default 10 shares)

📊 Information:
• "Check PLTR price" - Get current price
• "Show portfolio" - Display portfolio
• "Show watchlist" - Display watchlist

🔧 Control:
• "Stop bot" - Stop trading bot
• "Enable alerts" - Enable notifications
• "Log PLTR trade" - Log a trade

Examples:
• "Buy PLTR now" → Market buy 10 shares
• "Sell NVDA 25 shares" → Market sell 25 shares
• "Check portfolio" → Show portfolio overview
        """
    
    def start_continuous_listening(self, callback_function=None):
        """Start continuous listening in background thread"""
        def listen_continuously():
            self.is_listening = True
            
            while self.is_listening:
                try:
                    command = self.listen_for_command(timeout=1)
                    if command:
                        response = self.process_command(command)
                        logger.info(f"Voice command processed: {response}")
                        
                        if callback_function:
                            callback_function(command, response)
                
                except Exception as e:
                    logger.error(f"Error in continuous listening: {e}")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
        
        # Start listening in background thread
        listen_thread = threading.Thread(target=listen_continuously, daemon=True)
        listen_thread.start()
        
        logger.info("Continuous voice listening started")
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        logger.info("Voice listening stopped")
    
    def test_microphone(self) -> Dict[str, Any]:
        """Test microphone functionality"""
        if not self.microphone:
            return {
                'success': False,
                'message': 'Microphone not available'
            }
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Say something...")
                
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                
                return {
                    'success': True,
                    'message': f'Microphone test successful. You said: "{text}"'
                }
                
        except sr.UnknownValueError:
            return {
                'success': False,
                'message': 'Could not understand audio'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'message': f'Speech recognition service error: {e}'
            }
        except sr.WaitTimeoutError:
            return {
                'success': False,
                'message': 'Microphone test timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Microphone test error: {e}'
            }
    
    def get_supported_commands(self) -> List[str]:
        """Get list of supported command patterns"""
        return [
            "Buy [symbol] [quantity] shares",
            "Sell [symbol] [quantity] shares", 
            "Buy [symbol] [quantity] at [price]",
            "Sell [symbol] [quantity] at [price]",
            "Check [symbol] price",
            "Show portfolio",
            "Show watchlist", 
            "Log [symbol] trade",
            "Stop bot",
            "Enable alerts",
            "Disable alerts",
            "Help"
        ]
