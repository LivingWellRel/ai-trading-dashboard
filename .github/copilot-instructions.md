<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI Trading Dashboard - Copilot Instructions

## Project Overview
This is a mobile-friendly AI trading dashboard built with Streamlit that provides:
- Live technical indicators (RSI, Supertrend, MACD)
- Portfolio management via Google Sheets integration
- Telegram and SMS alerts
- Voice command functionality
- Mobile-responsive interface

## Code Style and Conventions

### Python Standards
- Follow PEP 8 coding standards
- Use type hints for all function parameters and return values
- Add comprehensive docstrings for all classes and functions
- Use f-string formatting for string interpolation
- Prefer pathlib over os.path for file operations

### Streamlit Best Practices
- Use `st.cache_data` for expensive computations
- Implement proper error handling with user-friendly messages
- Use columns and containers for responsive layouts
- Leverage session state for maintaining user data
- Add loading spinners for long-running operations

### Technical Indicators
- Use TA-Lib for technical indicator calculations when possible
- Implement proper data validation for OHLCV data
- Handle edge cases (insufficient data, NaN values)
- Cache indicator calculations to improve performance

### Trading Logic
- Always implement paper trading mode for testing
- Add proper risk management and position sizing
- Validate all trading inputs before execution
- Log all trading actions with timestamps

### Mobile Responsiveness
- Use CSS media queries for mobile optimization
- Implement touch-friendly button sizes
- Ensure charts are readable on small screens
- Use responsive column layouts

### Error Handling
- Use try-except blocks around all external API calls
- Provide meaningful error messages to users
- Log errors with proper context
- Implement fallback mechanisms for critical features

### Security Considerations
- Never hardcode API keys or sensitive credentials
- Use environment variables for all configuration
- Validate all user inputs
- Implement rate limiting for API calls

## Key Components

### TechnicalIndicators Class
- Calculate RSI, Supertrend, MACD indicators
- Provide combined signal analysis
- Handle different timeframes and periods
- Return structured indicator data

### PortfolioManager Class
- Sync with Google Sheets for portfolio data
- Track holdings, P&L, and buying power
- Calculate ROI and performance metrics
- Manage trailing stops and alerts

### AlertManager Class
- Send Telegram messages with inline buttons
- Schedule daily alerts at specified times
- Support SMS and voice calls via Twilio
- Handle alert cooldowns and rate limiting

### VoiceCommands Class
- Process voice-to-text commands
- Parse trading instructions (buy/sell/check)
- Provide voice feedback and confirmations
- Support continuous listening mode

## Integration Requirements

### Google Sheets API
- Use service account authentication
- Handle worksheet creation and updates
- Implement batch operations for efficiency
- Add error handling for API limits

### Telegram Bot API
- Use inline keyboards for user interactions
- Handle callback queries for button presses
- Support both text and media messages
- Implement webhook or polling modes

### Yahoo Finance API
- Use yfinance library for market data
- Handle rate limiting and API errors
- Cache frequently requested data
- Support both real-time and historical data

### Twilio API
- Send SMS messages for urgent alerts
- Support voice calls for critical notifications
- Handle delivery status and errors
- Implement cost-effective messaging strategies

## Testing Guidelines
- Write unit tests for all calculation functions
- Mock external API calls in tests
- Test mobile responsiveness across devices
- Validate all user input scenarios
- Test error handling and edge cases

## Performance Optimization
- Use caching for expensive operations
- Implement lazy loading for large datasets
- Optimize database queries and API calls
- Monitor memory usage and cleanup resources
- Use async operations where appropriate

## Deployment Considerations
- Ensure all dependencies are in requirements.txt
- Use environment variables for configuration
- Set up proper logging and monitoring
- Configure HTTPS for secure connections
- Implement health checks and status endpoints
