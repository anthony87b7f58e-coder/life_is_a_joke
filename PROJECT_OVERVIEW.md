# Trading Bot - Life Is A Joke

**Advanced Binance Cryptocurrency Trading Bot with Automated Strategies**

## 🎯 Project Overview

This is a production-ready cryptocurrency trading bot for Binance with the following capabilities:

### Core Features

1. **Automated Trading**
   - Connects to Binance API (supports both testnet and production)
   - Executes trades based on predefined strategies
   - Automatic position management with stop-loss and take-profit

2. **Trading Strategies**
   - Simple Trend Following (Moving Average Crossover)
   - Extensible architecture for adding custom strategies
   - Multi-timeframe analysis support

3. **Risk Management**
   - Position sizing based on account balance
   - Maximum daily trade limits
   - Maximum open position limits
   - Daily loss limits
   - Automatic stop-loss and take-profit calculation

4. **Data Persistence**
   - SQLite database for trade history
   - Position tracking
   - Daily statistics and analytics
   - Performance metrics

5. **Monitoring & Health Checks**
   - Real-time health monitoring
   - API connectivity verification
   - System resource monitoring
   - Logging with rotation

6. **Security**
   - Secure credential storage
   - Firewall configuration
   - SSH hardening
   - Automated security updates
   - Audit logging

7. **Backup & Recovery**
   - Automated database backups
   - Configuration backups
   - Easy restore from backup
   - Configurable retention policies

## 📦 What's Included

### Application Code (`src/`)
- **main.py** - Application entry point
- **core/bot.py** - Main trading bot logic
- **core/config.py** - Configuration management
- **core/database.py** - Database operations
- **core/risk_manager.py** - Risk management
- **strategies/** - Trading strategy implementations
- **utils/** - Utility functions (logging, etc.)

### Deployment Infrastructure (`deployment/`)
- **deploy.sh** - Automated deployment script
- **systemd/** - Service configuration
- **nginx/** - Reverse proxy configuration
- **scripts/** - Management scripts (backup, restore, firewall, security)
- **logrotate/** - Log rotation configuration

### Utilities (`scripts/`)
- **setup_environment.py** - Interactive configuration
- **health_check.py** - System health verification
- **test_connectivity.py** - API connectivity testing

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
cd life_is_a_joke

# Run automated deployment
sudo bash deployment/deploy.sh
```

### 2. Configuration

```bash
# Interactive configuration
sudo python3 scripts/setup_environment.py

# Or manual configuration
sudo cp .env.template /etc/trading-bot/.env
sudo nano /etc/trading-bot/.env
```

**Required Configuration:**
- `BINANCE_API_KEY` - Your Binance API key
- `BINANCE_API_SECRET` - Your Binance API secret
- `DEFAULT_SYMBOL` - Trading pair (default: BTCUSDT)
- Risk parameters (position size, stop loss, take profit)

### 3. Start Trading

```bash
# Start the service
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f
```

## 📊 Trading Capabilities at Launch

### Initial Functionality

1. **Monitoring Mode** (Safe Mode)
   - Connects to Binance API
   - Monitors market prices
   - Analyzes trends
   - Logs analysis results
   - **Does NOT execute trades** until explicitly enabled

2. **Live Trading Mode** (When Enabled)
   - Analyzes BTC/USDT (or configured symbol)
   - Detects trend changes using moving averages
   - Opens positions on bullish signals
   - Closes positions on bearish signals or SL/TP triggers
   - Respects all risk limits

### Trading Strategy

The bot starts with a **Simple Trend Following Strategy**:

- **Entry Signal**: Short-term MA crosses above long-term MA
- **Exit Signal**: Short-term MA crosses below long-term MA, or SL/TP hit
- **Timeframe**: 1-hour candles
- **Indicators**: 10-period and 30-period moving averages

### Risk Controls

All trades are subject to:
- **Maximum Position Size**: Configurable (default: 0.1 BTC equivalent)
- **Position Sizing**: 2% of account balance per trade
- **Stop Loss**: 2% below entry
- **Take Profit**: 5% above entry
- **Max Daily Trades**: 10
- **Max Open Positions**: 3
- **Max Daily Loss**: 5% of account

## 🔧 Management Commands

### Service Management
```bash
sudo systemctl start trading-bot    # Start bot
sudo systemctl stop trading-bot     # Stop bot
sudo systemctl restart trading-bot  # Restart bot
sudo systemctl status trading-bot   # Check status
```

### Health Checks
```bash
python3 scripts/health_check.py          # System health
python3 scripts/test_connectivity.py     # API connectivity
```

### Backup & Restore
```bash
sudo bash deployment/scripts/backup.sh   # Create backup
sudo bash deployment/scripts/restore.sh  # Restore from backup
```

### Logs
```bash
sudo tail -f /var/log/trading-bot/trading-bot.log  # Application logs
sudo journalctl -u trading-bot -f                  # Service logs
```

## 🎯 Key Functions

### 1. Market Analysis
- Continuously monitors configured trading pairs
- Analyzes price movements and trends
- Calculates technical indicators (moving averages)
- Generates trading signals

### 2. Trade Execution
- Places market orders based on signals
- Sets stop-loss and take-profit orders
- Manages open positions
- Calculates position sizes based on risk parameters

### 3. Risk Management
- Validates all trades against risk limits
- Prevents over-trading (daily limits)
- Prevents over-leveraging (position limits)
- Stops trading when daily loss limit reached

### 4. Data Recording
- Records all trades in database
- Tracks open positions
- Calculates daily P/L
- Stores performance metrics

### 5. Health Monitoring
- Checks API connectivity
- Monitors system resources
- Verifies database health
- Logs all activities

## ⚠️ Important Notes

### Security
1. **Never commit .env file** - Contains sensitive API keys
2. **Use API keys with trading permissions only** - No withdrawal permissions
3. **Start with testnet** - Set `BINANCE_TESTNET=true` for testing
4. **Enable firewall** - Run `sudo bash deployment/scripts/setup_firewall.sh`
5. **Apply security hardening** - Run `sudo bash deployment/scripts/security_hardening.sh`

### Trading
1. **Start in monitoring mode** - Set `TRADING_ENABLED=false` initially
2. **Use testnet first** - Set `BINANCE_TESTNET=true` for testing
3. **Start with small amounts** - Test with minimal position sizes
4. **Monitor closely** - Watch logs and positions regularly
5. **Understand the risks** - Cryptocurrency trading is risky

### Maintenance
1. **Regular backups** - Automated daily backups configured
2. **Monitor logs** - Check for errors and warnings
3. **Update dependencies** - Keep Python packages updated
4. **Review performance** - Check daily stats in database

## 📈 Future Enhancements

Planned features:
- Additional trading strategies (RSI, MACD, Bollinger Bands)
- Multi-symbol trading
- Web dashboard for monitoring
- Advanced analytics and reporting
- Telegram notifications
- Backtesting framework
- Machine learning integration

## 📝 File Locations

- **Application**: `/opt/trading-bot`
- **Configuration**: `/etc/trading-bot/.env`
- **Database**: `/var/lib/trading-bot/trading_bot.db`
- **Logs**: `/var/log/trading-bot/`
- **Backups**: `/var/backups/trading-bot/`

## 🆘 Support & Troubleshooting

See `README.md` for detailed troubleshooting guide.

Common issues:
1. **API Connection Failed**: Check API keys in `.env`
2. **Service Won't Start**: Check logs with `journalctl -u trading-bot -xe`
3. **No Trades Executing**: Verify `TRADING_ENABLED=true` and risk limits

## ⚖️ Disclaimer

**This trading bot is provided for educational purposes. Cryptocurrency trading carries significant financial risk. Use at your own risk. The developers are not responsible for any financial losses.**

Always:
- Test thoroughly in testnet mode
- Start with small amounts
- Never invest more than you can afford to lose
- Monitor the bot's performance regularly
- Understand the trading strategy being used

## 📄 License

This project is open source. See LICENSE file for details.
