# 🚀 AI Trading Dashboard

**Live Demo**: Coming soon on Streamlit Cloud!

A comprehensive mobile-friendly AI trading dashboard with live technical indicators, portfolio management, and automated alerts.

## ✨ Features

### 📊 Live Technical Indicators
- **RSI (Relative Strength Index)**: Momentum oscillator for overbought/oversold conditions
- **Supertrend**: Trend-following indicator with buy/sell signals
- **MACD**: Moving Average Convergence Divergence for trend changes
- **Smart Alerts**: Combined signals when all 3 indicators confirm

### 💰 Portfolio Management
- Google Sheets integration for holdings tracking
- Real-time buying power monitoring
- Daily trade logs and dividend calendar
- ROI calculations and performance metrics
- Trailing stop alerts
- Roth IRA dip buy triggers

### 📲 Telegram & Push Alerts
- Daily alerts at 9:25 AM EST to @SHADOWCLAW007
- Trade Now buttons for instant actions
- Optional Twilio SMS/voice alerts
- Custom alert conditions

### 🎤 Voice Commands
- Voice-to-text trading commands ("Buy PLTR now", "Check portfolio")
- Instant buy/sell voice triggers
- Trade logging via voice
- Mobile-optimized interface

### � Mobile-First Design
- **Responsive design** works on all devices
- **Touch-friendly** buttons and interface
- **Add to home screen** for app-like experience
- **Dark mode** support

## 🚀 Quick Start

### Run Locally
```bash
pip install -r requirements.txt
streamlit run demo.py
```

### Deploy to Streamlit Cloud (FREE)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy `demo.py` as main file
5. **Your app**: `https://your-repo-name.streamlit.app`

## 📱 Mobile Access
- Works on **any device** with internet
- **Responsive design** adapts to screen size
- **PWA capabilities** - add to home screen
- **Touch-optimized** for mobile trading

## 🎯 Trading Signals

**Strong Buy Signal** (3/3 indicators):
- ✅ RSI: 30-40 (oversold recovery zone)
- ✅ Supertrend: Green (confirmed uptrend)
- ✅ MACD: Above signal line (bullish momentum)

## 🔧 Configuration

Create `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USERNAME=@SHADOWCLAW007
GOOGLE_SHEETS_ID=your_sheet_id
ALERT_TIME=09:25
TIMEZONE=US/Eastern
```

## 🏗️ Tech Stack
- **Frontend**: Streamlit with mobile-responsive CSS
- **Data**: yfinance, pandas, numpy
- **Charts**: Plotly (mobile-optimized)
- **Alerts**: Telegram Bot API, Twilio
- **Storage**: Google Sheets API
- **Voice**: SpeechRecognition
- **Deployment**: Streamlit Cloud, Railway, Heroku

## 📊 Live Features
- Real-time market simulation
- Interactive charts and indicators
- Portfolio tracking and analysis
- Voice command interface
- Mobile-responsive design

---
**🎊 Ready to deploy! Your mobile AI trading dashboard awaits!** 📱📈