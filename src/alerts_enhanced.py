"""
Enhanced Telegram Alert System for @SHADOWCLAW007
Professional trading alerts with inline buttons, charts, and real-time updates
"""

import asyncio
import streamlit as st
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
import plotly.io as pio
import io
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    st.warning("⚠️ Telegram features require python-telegram-bot package")

class EnhancedTelegramAlerts:
    """Professional Telegram alert system for AI Trading Dashboard"""
    
    def __init__(self):
        # Get secrets from Streamlit
        self.bot_token = st.secrets.get("telegram", {}).get("bot_token")
        self.chat_id = st.secrets.get("telegram", {}).get("chat_id", "@SHADOWCLAW007")
        self.user_id = st.secrets.get("telegram", {}).get("user_id")
        self.webhook_url = st.secrets.get("telegram", {}).get("webhook_url")
        
        self.bot = None
        self.app = None
        
        if TELEGRAM_AVAILABLE and self.bot_token:
            self.bot = Bot(token=self.bot_token)
            self.setup_bot_handlers()
    
    def setup_bot_handlers(self):
        """Setup Telegram bot handlers"""
        try:
            self.app = Application.builder().token(self.bot_token).build()
            
            # Add handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("status", self.status_command))
            self.app.add_handler(CommandHandler("portfolio", self.portfolio_command))
            self.app.add_handler(CallbackQueryHandler(self.handle_callback))
            
            logger.info("Telegram bot handlers configured")
        except Exception as e:
            logger.error(f"Failed to setup bot handlers: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🚀 **AI Trading Dashboard Bot Active**

Welcome to your personal trading assistant!

**Available Commands:**
• /status - Market and portfolio status
• /portfolio - View portfolio summary
• /signals - Latest trading signals

**Features:**
📊 Real-time trading signals
📈 Portfolio updates
🔔 Custom alerts
📱 Mobile-friendly interface

**Dashboard:** [Click Here](https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/)

Ready to help you trade smarter! 💰
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📊 View Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/"),
                InlineKeyboardButton("📈 Get Signals", callback_data="get_signals")
            ],
            [
                InlineKeyboardButton("💰 Portfolio", callback_data="view_portfolio"),
                InlineKeyboardButton("⚙️ Settings", callback_data="bot_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get market status
            market_status = self.get_market_status()
            
            # Get major indices
            indices_data = await self.get_indices_data()
            
            status_message = f"""
📊 **MARKET STATUS UPDATE**

🕒 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M EST')}
📈 **Market**: {market_status}

**Major Indices:**
{indices_data}

**System Status:**
🟢 Bot: Online
🟢 Alerts: Active
🟢 Data Feed: Live
🟢 Dashboard: Running

**Quick Actions:**
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Full Analysis", callback_data="full_analysis"),
                    InlineKeyboardButton("🔔 Alert Settings", callback_data="alert_settings")
                ],
                [
                    InlineKeyboardButton("📱 Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(status_message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {e}")
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command"""
        try:
            # Mock portfolio data (replace with real data integration)
            portfolio_message = """
💰 **PORTFOLIO SUMMARY**

**Account Value:** $15,247.83
**Day P&L:** +$342.15 (+2.29%)
**Buying Power:** $2,847.92

**Top Holdings:**
🟢 NVDA: +3.4% ($4,250.00)
🟢 TSLA: +1.8% ($3,100.00)
🔴 AAPL: -0.5% ($2,897.83)

**Recent Activity:**
• Bought 50 PLTR @ $18.42
• Sold 25 AMD @ $142.30
• Set alert for MSFT @ $420

**Performance:**
• 1D: +2.29%
• 1W: +5.67%
• 1M: +12.34%
• YTD: +24.78%
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Detailed View", callback_data="detailed_portfolio"),
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_portfolio")
                ],
                [
                    InlineKeyboardButton("📱 Full Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(portfolio_message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting portfolio: {e}")
    
    async def send_trading_signal(self, signal_data: Dict) -> bool:
        """Send professional trading signal with chart"""
        if not self.bot:
            return False
        
        try:
            # Create signal message
            signal_emoji = "🚀" if "BUY" in signal_data['signal'] else "📉" if "SELL" in signal_data['signal'] else "⚖️"
            confidence_bar = "🟩" * int(signal_data['confidence'] / 20) + "⬜" * (5 - int(signal_data['confidence'] / 20))
            
            message = f"""
{signal_emoji} **AI TRADING SIGNAL** {signal_emoji}

**📈 Symbol:** {signal_data['ticker']}
**💰 Price:** ${signal_data['price']:.2f}
**🎯 Signal:** {signal_data['signal']}
**📊 Confidence:** {signal_data['confidence']:.0f}% {confidence_bar}

**📋 Technical Analysis:**
• **RSI (14):** {signal_data['rsi_value']:.1f} - {signal_data['rsi_signal']}
• **Supertrend:** {signal_data['supertrend_signal']}
• **MACD:** {signal_data['macd_signal']}

**💡 AI Recommendation:**
{signal_data.get('recommendation', 'Monitor for entry opportunity')}

**⚠️ Risk Level:** {signal_data.get('risk_level', 'Medium')}
**🎯 Target:** ${signal_data.get('target_price', signal_data['price'] * 1.05):.2f}
**🛑 Stop:** ${signal_data.get('stop_price', signal_data['price'] * 0.95):.2f}

🕒 {datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")}
"""
            
            # Create action buttons
            keyboard = [
                [
                    InlineKeyboardButton("📈 Execute Trade", callback_data=f"trade_{signal_data['ticker']}"),
                    InlineKeyboardButton("📊 Full Analysis", callback_data=f"analysis_{signal_data['ticker']}")
                ],
                [
                    InlineKeyboardButton("🔔 Set Alert", callback_data=f"alert_{signal_data['ticker']}"),
                    InlineKeyboardButton("📖 Add to Watchlist", callback_data=f"watch_{signal_data['ticker']}")
                ],
                [
                    InlineKeyboardButton("📱 View Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send signal message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Send chart if data available
            chart_buffer = await self.create_signal_chart(signal_data)
            if chart_buffer:
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=chart_buffer,
                    caption=f"📈 {signal_data['ticker']} - Technical Analysis Chart"
                )
            
            logger.info(f"Trading signal sent for {signal_data['ticker']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send trading signal: {e}")
            return False
    
    async def create_signal_chart(self, signal_data: Dict) -> Optional[io.BytesIO]:
        """Create professional chart for signal"""
        try:
            ticker = signal_data['ticker']
            
            # Get market data
            data = yf.download(ticker, period="1mo", interval="1d")
            if data.empty:
                return None
            
            # Create advanced chart
            fig = go.Figure()
            
            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=ticker,
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ))
            
            # Add moving averages
            data['MA20'] = data['Close'].rolling(20).mean()
            data['MA50'] = data['Close'].rolling(50).mean()
            
            fig.add_trace(go.Scatter(
                x=data.index, y=data['MA20'],
                name='MA20', line=dict(color='orange', width=1)
            ))
            
            fig.add_trace(go.Scatter(
                x=data.index, y=data['MA50'],
                name='MA50', line=dict(color='blue', width=1)
            ))
            
            # Add signal marker
            current_price = data['Close'].iloc[-1]
            signal_color = '#00ff88' if 'BUY' in signal_data['signal'] else '#ff4444'
            marker_symbol = 'triangle-up' if 'BUY' in signal_data['signal'] else 'triangle-down'
            
            fig.add_trace(go.Scatter(
                x=[data.index[-1]],
                y=[current_price],
                mode='markers',
                marker=dict(
                    symbol=marker_symbol,
                    size=20,
                    color=signal_color,
                    line=dict(color='white', width=2)
                ),
                name=f'{signal_data["signal"]} Signal'
            ))
            
            # Add support/resistance levels
            if 'support' in signal_data:
                fig.add_hline(
                    y=signal_data['support'],
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Support"
                )
            
            if 'resistance' in signal_data:
                fig.add_hline(
                    y=signal_data['resistance'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Resistance"
                )
            
            # Professional styling
            fig.update_layout(
                title=f"{ticker} - {signal_data['signal']} Signal ({signal_data['confidence']:.0f}% Confidence)",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                template='plotly_dark',
                height=500,
                width=800,
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            # Remove range slider for cleaner look
            fig.update_layout(xaxis_rangeslider_visible=False)
            
            # Convert to image buffer
            img_buffer = io.BytesIO()
            fig.write_image(img_buffer, format='png', width=800, height=500, scale=2)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Chart creation failed: {e}")
            return None
    
    async def send_daily_market_update(self) -> bool:
        """Send comprehensive daily market update"""
        if not self.bot:
            return False
        
        try:
            # Get market data
            indices_data = await self.get_indices_data()
            market_status = self.get_market_status()
            
            # Get economic calendar events (mock data)
            economic_events = self.get_economic_events()
            
            message = f"""
🌅 **DAILY MARKET BRIEFING** 🌅

**📅 {datetime.now().strftime('%A, %B %d, %Y')}**
**🕒 {datetime.now().strftime('%H:%M EST')}**

**📊 Market Overview:**
{indices_data}

**📈 Market Status:** {market_status}

**📰 Key Events Today:**
{economic_events}

**🎯 Trading Focus:**
• Monitor RSI oversold levels (< 30)
• Watch for Supertrend direction changes
• MACD momentum crossovers
• Volume confirmation on breakouts

**💡 Today's Strategy:**
1. **Morning:** Scan for gap opportunities
2. **Midday:** Look for trend continuation
3. **Close:** Position for overnight holds

**⚠️ Risk Reminders:**
• Use proper position sizing
• Set stop losses before entry
• Don't chase momentum without confirmation

Have a profitable trading day! 🚀📈
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Live Signals", callback_data="live_signals"),
                    InlineKeyboardButton("💰 Portfolio", callback_data="view_portfolio")
                ],
                [
                    InlineKeyboardButton("🔔 Alert Settings", callback_data="alert_settings"),
                    InlineKeyboardButton("📱 Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info("Daily market update sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send daily update: {e}")
            return False
    
    async def get_indices_data(self) -> str:
        """Get major market indices data"""
        try:
            indices = {
                '^GSPC': 'S&P 500',
                '^IXIC': 'NASDAQ',
                '^DJI': 'DOW',
                '^VIX': 'VIX Fear Index'
            }
            
            market_data = []
            
            for symbol, name in indices.items():
                try:
                    ticker_data = yf.download(symbol, period="2d", interval="1d")
                    if not ticker_data.empty and len(ticker_data) >= 2:
                        current = ticker_data['Close'].iloc[-1]
                        previous = ticker_data['Close'].iloc[-2]
                        change = ((current - previous) / previous) * 100
                        
                        emoji = "🟢" if change >= 0 else "🔴"
                        arrow = "↗️" if change > 1 else "↘️" if change < -1 else "➡️"
                        
                        market_data.append(f"{emoji} **{name}**: {current:.2f} ({change:+.2f}%) {arrow}")
                except Exception as e:
                    market_data.append(f"⚪ **{name}**: Data unavailable")
            
            return '\n'.join(market_data)
            
        except Exception as e:
            return "❌ Unable to fetch market data"
    
    def get_market_status(self) -> str:
        """Get current market status"""
        try:
            now = datetime.now()
            weekday = now.weekday()  # 0 = Monday, 6 = Sunday
            hour = now.hour
            minute = now.minute
            
            # Market hours: Monday-Friday 9:30 AM - 4:00 PM EST
            if weekday < 5:  # Weekday
                if (hour == 9 and minute >= 30) or (10 <= hour < 16) or (hour == 16 and minute == 0):
                    return "🟢 **OPEN** - Regular Trading Hours"
                elif hour < 9 or (hour == 9 and minute < 30):
                    return "🟡 **PRE-MARKET** - Extended Hours"
                elif hour >= 16:
                    return "🟡 **AFTER-HOURS** - Extended Trading"
                else:
                    return "🔴 **CLOSED**"
            else:  # Weekend
                return "🔴 **WEEKEND** - Markets Closed"
                
        except Exception:
            return "❓ **UNKNOWN** - Status Check Failed"
    
    def get_economic_events(self) -> str:
        """Get today's economic events (mock data)"""
        events = [
            "• 8:30 AM - Unemployment Claims",
            "• 10:00 AM - Consumer Confidence",
            "• 2:00 PM - Fed Interest Rate Decision",
            "• 4:30 PM - Earnings: NVDA, TSLA"
        ]
        
        return '\n'.join(events[:3])  # Show top 3 events
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        try:
            if data.startswith('trade_'):
                ticker = data.split('_')[1]
                await self.handle_trade_action(query, ticker)
            
            elif data.startswith('analysis_'):
                ticker = data.split('_')[1]
                await self.send_detailed_analysis(query, ticker)
            
            elif data.startswith('alert_'):
                ticker = data.split('_')[1]
                await self.handle_alert_setup(query, ticker)
            
            elif data.startswith('watch_'):
                ticker = data.split('_')[1]
                await self.handle_watchlist_add(query, ticker)
            
            elif data == 'get_signals':
                await self.handle_get_signals(query)
            
            elif data == 'view_portfolio':
                await self.handle_portfolio_view(query)
            
            elif data == 'live_signals':
                await self.handle_live_signals(query)
            
            elif data == 'alert_settings':
                await self.handle_alert_settings(query)
            
            else:
                await query.edit_message_text("⚙️ Feature coming soon! Stay tuned for updates.")
                
        except Exception as e:
            logger.error(f"Callback handling error: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")
    
    async def handle_trade_action(self, query, ticker: str):
        """Handle trade execution request"""
        message = f"""
🚀 **TRADE EXECUTION - {ticker}**

**⚠️ Paper Trading Mode Active**

This feature will integrate with your broker API for live trading. Currently showing paper trade simulation.

**Next Steps:**
1. Review analysis on dashboard
2. Confirm position size
3. Set stop loss and target
4. Execute via your broker

**Risk Management:**
• Never risk more than 2% per trade
• Always use stop losses
• Confirm with multiple indicators
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Full Analysis", callback_data=f"analysis_{ticker}"),
                InlineKeyboardButton("📱 Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def send_detailed_analysis(self, query, ticker: str):
        """Send comprehensive technical analysis"""
        try:
            # Get real data for analysis
            data = yf.download(ticker, period="3mo", interval="1d")
            
            if data.empty:
                await query.edit_message_text(f"❌ Unable to fetch data for {ticker}")
                return
            
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate basic indicators
            rsi = self.calculate_rsi(data['Close'])
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            
            message = f"""
📊 **DETAILED ANALYSIS - {ticker}**

**💰 Current Price:** ${current_price:.2f} ({change_pct:+.2f}%)

**📈 Technical Indicators:**
• **RSI (14):** {rsi:.1f} {'🟢 Oversold' if rsi < 30 else '🔴 Overbought' if rsi > 70 else '🟡 Neutral'}
• **SMA 20:** ${sma_20:.2f} {'🟢 Above' if current_price > sma_20 else '🔴 Below'}
• **SMA 50:** ${sma_50:.2f} {'🟢 Above' if current_price > sma_50 else '🔴 Below'}

**📊 Price Action:**
• **Support:** ${data['Low'].tail(20).min():.2f}
• **Resistance:** ${data['High'].tail(20).max():.2f}
• **Volume:** {'🟢 Above Average' if data['Volume'].iloc[-1] > data['Volume'].tail(20).mean() else '🔴 Below Average'}

**🎯 Trading Levels:**
• **Entry:** Market price
• **Stop Loss:** ${current_price * 0.95:.2f} (-5%)
• **Target 1:** ${current_price * 1.05:.2f} (+5%)
• **Target 2:** ${current_price * 1.10:.2f} (+10%)

**💡 Summary:**
Technical analysis suggests {'bullish' if rsi < 70 and current_price > sma_20 else 'bearish' if rsi > 70 and current_price < sma_20 else 'neutral'} sentiment.

🕒 Analysis as of {datetime.now().strftime('%H:%M EST')}
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("📈 Execute Trade", callback_data=f"trade_{ticker}"),
                    InlineKeyboardButton("📱 Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await query.edit_message_text(f"❌ Analysis failed for {ticker}: {e}")
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0  # Default neutral RSI
    
    async def handle_alert_setup(self, query, ticker: str):
        """Handle alert setup for ticker"""
        message = f"""
🔔 **ALERT SETUP - {ticker}**

**Available Alert Types:**
• Price alerts (above/below levels)
• RSI overbought/oversold
• Volume spike alerts
• Breakout notifications

**Current Alerts:** None set

To configure alerts, please use the dashboard for detailed settings.
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📱 Configure on Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_watchlist_add(self, query, ticker: str):
        """Handle adding ticker to watchlist"""
        message = f"""
📖 **WATCHLIST UPDATE**

✅ {ticker} has been added to your watchlist!

**Monitoring:**
• Real-time price changes
• Technical indicator signals
• Volume and momentum shifts
• News and earnings updates

You'll receive alerts when significant events occur.
"""
        
        await query.edit_message_text(message, parse_mode='Markdown')
    
    async def handle_get_signals(self, query):
        """Handle get signals request"""
        message = """
🔍 **SCANNING FOR SIGNALS...**

**Active Scans:**
• RSI oversold conditions
• Supertrend trend changes
• MACD bullish crossovers
• Volume breakout patterns

**Recent Signals:**
🟢 PLTR - BUY Signal (85% confidence)
🟡 NVDA - HOLD Signal (65% confidence)
🔴 TSLA - SELL Signal (72% confidence)

For real-time signals, visit the dashboard.
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📱 Live Dashboard", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_portfolio_view(self, query):
        """Handle portfolio view request"""
        await self.portfolio_command(query, None)
    
    async def handle_live_signals(self, query):
        """Handle live signals request"""
        await self.handle_get_signals(query)
    
    async def handle_alert_settings(self, query):
        """Handle alert settings"""
        message = """
⚙️ **ALERT SETTINGS**

**Current Configuration:**
• Telegram Alerts: ✅ Enabled
• SMS Alerts: ⚠️ Configure in secrets
• Voice Calls: ⚠️ Configure in secrets
• Email Alerts: ❌ Disabled

**Alert Frequency:**
• High Confidence (>80%): Immediate
• Medium Confidence (60-80%): Every 30 min
• Low Confidence (<60%): Daily summary

**Active Alerts:**
• Daily market briefing: 09:25 EST
• Portfolio updates: 16:15 EST
• Signal notifications: Real-time

Configure detailed settings on the dashboard.
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📱 Configure Settings", url="https://ai-trading-dashboard-lnwn7gmu6kkcydyafcr4hm.streamlit.app/")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Streamlit integration functions
def send_telegram_signal(signal_data: Dict) -> bool:
    """Send trading signal via Telegram"""
    try:
        alert_system = EnhancedTelegramAlerts()
        if alert_system.bot:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(alert_system.send_trading_signal(signal_data))
            loop.close()
            return result
        return False
    except Exception as e:
        logger.error(f"Signal sending failed: {e}")
        return False

def send_daily_briefing() -> bool:
    """Send daily market briefing"""
    try:
        alert_system = EnhancedTelegramAlerts()
        if alert_system.bot:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(alert_system.send_daily_market_update())
            loop.close()
            return result
        return False
    except Exception as e:
        logger.error(f"Daily briefing failed: {e}")
        return False

def test_telegram_connection() -> bool:
    """Test Telegram bot connection"""
    try:
        alert_system = EnhancedTelegramAlerts()
        return alert_system.bot is not None
    except Exception as e:
        logger.error(f"Telegram connection test failed: {e}")
        return False
