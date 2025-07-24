# AI Trading Dashboard

A comprehensive mobile-friendly AI trading dashboard with live technical indicators, portfolio management, and automated alerts.

## Features

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
- Daily alerts at 9:25 AM EST
- Trade Now buttons for instant actions
- Optional Twilio SMS/voice alerts
- Custom alert conditions

### 🎤 Voice Commands
- Voice-to-text trading commands
- Instant buy/sell voice triggers
- Trade logging via voice
- Mobile-optimized interface

### 🖥 Streamlit Dashboard
- Mobile-responsive design
- Dark mode support
- Multiple tabs: Charts, Logs, ROI, Watchlist, Roth IRA
- Real-time data streaming

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Configure Google Sheets API credentials
5. Set up Telegram bot token
6. Run the application:
   ```bash
   streamlit run main.py
   ```

## Configuration

Create a `.env` file with the following variables:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_USERNAME`: Your Telegram username (@SHADOWCLAW007)
- `TWILIO_ACCOUNT_SID`: Twilio account SID (optional)
- `TWILIO_AUTH_TOKEN`: Twilio auth token (optional)
- `GOOGLE_SHEETS_CREDENTIALS`: Path to Google Sheets credentials JSON

## Usage

1. **Live Charts**: Monitor real-time technical indicators
2. **Portfolio**: Track holdings and performance via Google Sheets
3. **Alerts**: Receive automated trading signals
4. **Voice Commands**: Use voice for quick trading actions
5. **Mobile Access**: Full functionality on mobile devices

## Tech Stack

- **Frontend**: Streamlit with mobile-responsive design
- **Data**: yfinance, TA-Lib for technical analysis
- **Alerts**: Telegram Bot API, Twilio
- **Storage**: Google Sheets API
- **Voice**: SpeechRecognition, PyAudio
- **Charts**: Plotly for interactive visualizations

## License

MIT License
