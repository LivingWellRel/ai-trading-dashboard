import asyncio
import schedule
import time
from datetime import datetime, timedelta
import pytz
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from twilio.rest import Client
import os
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertManager:
    """
    Manage alerts via Telegram and SMS
    """
    
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_username = os.getenv('TELEGRAM_USERNAME', '@SHADOWCLAW007')
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN') 
        self.twilio_from = os.getenv('TWILIO_PHONE_FROM')
        self.twilio_to = os.getenv('TWILIO_PHONE_TO')
        
        # Initialize services
        self.telegram_bot = None
        self.twilio_client = None
        self.setup_telegram()
        self.setup_twilio()
        
        # Alert settings
        self.alert_time = os.getenv('ALERT_TIME', '09:25')
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'US/Eastern'))
        
        # Schedule daily alerts
        self.schedule_daily_alerts()
    
    def setup_telegram(self):
        """Initialize Telegram bot"""
        if self.telegram_token:
            try:
                self.telegram_bot = Bot(token=self.telegram_token)
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Telegram bot: {e}")
    
    def setup_twilio(self):
        """Initialize Twilio client"""
        if self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = Client(self.twilio_sid, self.twilio_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Twilio client: {e}")
    
    def schedule_daily_alerts(self):
        """Schedule daily alerts at specified time"""
        schedule.every().day.at(self.alert_time).do(self.send_daily_alert)
        logger.info(f"Daily alerts scheduled for {self.alert_time} EST")
    
    async def send_telegram_message(self, message: str, chat_id: str = None, buttons: List[Dict] = None):
        """Send message via Telegram"""
        if not self.telegram_bot:
            logger.warning("Telegram bot not initialized")
            return False
        
        try:
            # If no chat_id provided, use username
            if not chat_id:
                chat_id = self.telegram_username
            
            # Create inline keyboard if buttons provided
            reply_markup = None
            if buttons:
                keyboard = []
                for button in buttons:
                    keyboard.append([InlineKeyboardButton(
                        button['text'], 
                        callback_data=button['callback_data']
                    )])
                reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await self.telegram_bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            logger.info(f"Telegram message sent successfully to {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_sms_alert(self, message: str):
        """Send SMS alert via Twilio"""
        if not self.twilio_client or not self.twilio_from or not self.twilio_to:
            logger.warning("Twilio not properly configured")
            return False
        
        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from,
                to=self.twilio_to
            )
            
            logger.info(f"SMS sent successfully: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def make_voice_call(self, message: str):
        """Make voice call via Twilio"""
        if not self.twilio_client or not self.twilio_from or not self.twilio_to:
            logger.warning("Twilio not properly configured")
            return False
        
        try:
            # Create TwiML for voice message
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice">{message}</Say>
            </Response>'''
            
            call = self.twilio_client.calls.create(
                twiml=twiml,
                from_=self.twilio_from,
                to=self.twilio_to
            )
            
            logger.info(f"Voice call initiated: {call.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error making voice call: {e}")
            return False
    
    def send_daily_alert(self):
        """Send daily market alert at 9:25 AM EST"""
        try:
            current_time = datetime.now(self.timezone)
            
            # Mock portfolio and market data
            portfolio_summary = {
                'total_value': 12450.78,
                'day_pnl': 234.56,
                'day_pnl_percent': 1.89,
                'buying_power': 649.78
            }
            
            # Mock watchlist signals
            signals = [
                {'symbol': 'PLTR', 'signal': 'BUY', 'strength': 'Strong'},
                {'symbol': 'NVDA', 'signal': 'HOLD', 'strength': 'Medium'}
            ]
            
            # Create alert message
            message = self.create_daily_alert_message(portfolio_summary, signals, current_time)
            
            # Create action buttons
            buttons = [
                {'text': '📈 Trade Now', 'callback_data': 'trade_now'},
                {'text': '📊 View Portfolio', 'callback_data': 'view_portfolio'},
                {'text': '🛑 Stop Bot', 'callback_data': 'stop_bot'}
            ]
            
            # Send alerts
            asyncio.create_task(self.send_telegram_message(message, buttons=buttons))
            
            logger.info("Daily alert sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending daily alert: {e}")
    
    def create_daily_alert_message(self, portfolio: Dict, signals: List[Dict], timestamp: datetime) -> str:
        """Create formatted daily alert message"""
        message = f"""
🚀 <b>AI Trading Dashboard - Daily Alert</b>

📅 <b>{timestamp.strftime('%Y-%m-%d %H:%M')} EST</b>

💰 <b>Portfolio Summary:</b>
• Total Value: ${portfolio['total_value']:,.2f}
• Day P&L: ${portfolio['day_pnl']:+.2f} ({portfolio['day_pnl_percent']:+.1f}%)
• Buying Power: ${portfolio['buying_power']:,.2f}

🎯 <b>Trading Signals:</b>"""
        
        for signal in signals:
            emoji = "🟢" if signal['signal'] == 'BUY' else "🔴" if signal['signal'] == 'SELL' else "🟡"
            message += f"\n• {signal['symbol']}: {emoji} {signal['signal']} ({signal['strength']})"
        
        message += f"""

📊 <b>Market Status:</b>
• Market Open: {self.is_market_open()}
• Next Alert: Tomorrow 9:25 AM EST

💡 <b>Quick Actions:</b>
Use the buttons below to take immediate action!
        """
        
        return message.strip()
    
    def send_trade_signal_alert(self, symbol: str, signal_data: Dict[str, Any]):
        """Send immediate trade signal alert"""
        try:
            signal_strength = signal_data.get('signal_strength', 0)
            rsi_value = signal_data.get('rsi_value', 0)
            
            if signal_strength >= 2:  # Moderate or strong signal
                emoji = "🚀" if signal_strength >= 3 else "⚠️"
                strength_text = "STRONG BUY" if signal_strength >= 3 else "MODERATE BUY"
                
                message = f"""
{emoji} <b>TRADING SIGNAL ALERT</b>

📊 <b>{symbol}</b> - {strength_text}
⏰ {datetime.now(self.timezone).strftime('%H:%M:%S EST')}

🎯 <b>Signal Details:</b>
• RSI: {rsi_value:.1f} {'✅' if 30 <= rsi_value <= 40 else '❌'}
• Supertrend: {'✅ Green' if signal_data.get('supertrend_flip') else '❌ Red'}
• MACD: {'✅ Bullish Cross' if signal_data.get('macd_cross') else '❌ No Cross'}

🎪 <b>Confirmation Score: {signal_strength}/3</b>

💡 Consider taking action if this aligns with your strategy!
                """
                
                buttons = [
                    {'text': f'📈 Buy {symbol}', 'callback_data': f'buy_{symbol}'},
                    {'text': '📊 View Chart', 'callback_data': f'chart_{symbol}'},
                    {'text': '🔕 Mute Alerts', 'callback_data': 'mute_alerts'}
                ]
                
                # Send Telegram alert
                asyncio.create_task(self.send_telegram_message(message, buttons=buttons))
                
                # Send SMS if enabled and strong signal
                if signal_strength >= 3:
                    sms_message = f"🚀 STRONG BUY SIGNAL: {symbol} - All indicators confirm! Check Telegram for details."
                    self.send_sms_alert(sms_message)
                
                logger.info(f"Trade signal alert sent for {symbol}")
                
        except Exception as e:
            logger.error(f"Error sending trade signal alert: {e}")
    
    def send_roth_ira_dip_alert(self, symbol: str, current_price: float, dip_percent: float):
        """Send Roth IRA dip buy alert"""
        try:
            message = f"""
🏦 <b>ROTH IRA DIP ALERT</b>

📉 <b>{symbol}</b> dipped {dip_percent:.1f}%!
💰 Current Price: ${current_price:.2f}

🎯 <b>Dip Buy Trigger Activated</b>
Consider adding to your Roth IRA position.

⚡ Time-sensitive opportunity!
            """
            
            buttons = [
                {'text': f'🏦 Buy for Roth IRA', 'callback_data': f'roth_buy_{symbol}'},
                {'text': '📊 View Analysis', 'callback_data': f'analysis_{symbol}'},
                {'text': '⏰ Remind Later', 'callback_data': f'remind_{symbol}'}
            ]
            
            # Send alert
            asyncio.create_task(self.send_telegram_message(message, buttons=buttons))
            
            # Send SMS for dip alerts
            sms_message = f"🏦 ROTH IRA ALERT: {symbol} dipped {dip_percent:.1f}% to ${current_price:.2f}. Consider buying the dip!"
            self.send_sms_alert(sms_message)
            
            logger.info(f"Roth IRA dip alert sent for {symbol}")
            
        except Exception as e:
            logger.error(f"Error sending Roth IRA dip alert: {e}")
    
    def send_portfolio_summary(self, summary_data: Dict[str, Any]):
        """Send daily portfolio recap"""
        try:
            trades_today = summary_data.get('trades_today', [])
            pnl_percent = summary_data.get('pnl_percent', 0)
            new_watchlist = summary_data.get('new_watchlist', [])
            
            message = f"""
📊 <b>Daily Portfolio Recap</b>

💰 <b>Performance:</b>
• Day P&L: {pnl_percent:+.2f}%
• Total Trades: {len(trades_today)}

📈 <b>Today's Trades:</b>"""
            
            for trade in trades_today[:3]:  # Show last 3 trades
                message += f"\n• {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}"
            
            if len(trades_today) > 3:
                message += f"\n• ... and {len(trades_today) - 3} more"
            
            if new_watchlist:
                message += f"\n\n🎯 <b>New Watchlist Entries:</b>"
                for symbol in new_watchlist:
                    message += f"\n• {symbol}"
            
            message += f"\n\n🌙 See you tomorrow for more opportunities!"
            
            # Send recap
            asyncio.create_task(self.send_telegram_message(message))
            
            logger.info("Daily portfolio recap sent")
            
        except Exception as e:
            logger.error(f"Error sending portfolio recap: {e}")
    
    def is_market_open(self) -> str:
        """Check if market is currently open"""
        now = datetime.now(self.timezone)
        weekday = now.weekday()
        hour = now.hour
        minute = now.minute
        
        # Market hours: Monday-Friday 9:30 AM - 4:00 PM EST
        if weekday < 5:  # Monday = 0, Friday = 4
            if hour == 9 and minute >= 30:
                return "✅ Open"
            elif 10 <= hour < 16:
                return "✅ Open"
            elif hour == 16 and minute == 0:
                return "✅ Open"
            else:
                return "🔴 Closed"
        else:
            return "🔴 Weekend"
    
    def start_alert_scheduler(self):
        """Start the alert scheduler in a separate thread"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        import threading
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Alert scheduler started")
    
    def test_alerts(self):
        """Test alert functionality"""
        test_message = """
🧪 <b>Test Alert</b>

This is a test message from your AI Trading Dashboard.

All systems are working correctly! 🚀
        """
        
        buttons = [
            {'text': '✅ Test Successful', 'callback_data': 'test_success'},
            {'text': '❌ Report Issue', 'callback_data': 'test_issue'}
        ]
        
        # Test Telegram
        asyncio.create_task(self.send_telegram_message(test_message, buttons=buttons))
        
        # Test SMS
        self.send_sms_alert("🧪 Test SMS from AI Trading Dashboard - All systems operational!")
        
        logger.info("Test alerts sent")
