# Crypto Trading Bot Framework & Educational Template

> ⚠️ **Important Disclaimer**  
> This is an **educational scaffold and framework**, not a production-ready trading bot. It demonstrates architecture for a high-frequency trading system. **Never use real funds with this code.** Cryptocurrency trading involves substantial risk of loss.

## 🎯 Project Overview

This project provides a structured Python framework for building algorithmic trading systems. It implements a microservices-style architecture suitable for backtesting, paper trading, and eventual live deployment—with proper risk management and monitoring components.

**Realistic Expectations:** This is a starting template. You should expect to:
- Implement your own trading strategies
- Thoroughly backtest and paper trade for weeks
- Start with tiny position sizes (1-2% of portfolio)
- Monitor continuously when live

## 📁 Project Structure (Refactored)

```
rofl/
├── src/                          # Application source code
│   ├── core/                     # Core trading logic
│   │   ├── data_fetcher.py      # Exchange data via CCXT
│   │   ├── strategy.py          # Trading strategy implementations
│   │   ├── risk_manager.py      # Position sizing & risk controls
│   │   └── executor.py          # Order placement with retry logic
│   ├── utils/                    # Utilities & infrastructure
│   │   ├── config_loader.py     # YAML configuration
│   │   ├── logger.py            # Structured logging
│   │   └── health_monitor.py    # System health checks
│   └── main.py                  # Primary application entry point
├── configs/                      # Configuration files
│   ├── config.yaml              # Main configuration
│   └── paper_trading.yaml       # Paper trading settings
├── scripts/                      # Utility scripts
│   ├── backtest.py              # Strategy backtesting
│   └── report_generator.py      # Performance reporting
├── tests/                        # Comprehensive test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── infrastructure/               # Deployment configurations
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── k8s/                     # Kubernetes manifests
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose (optional)
- Binance Testnet account (for paper trading)

### Local Development Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/Gexyby/rofl.git
   cd rofl
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure for paper trading**
   ```bash
   cp configs/paper_trading.yaml configs/local.yaml
   # Edit local.yaml with your Binance Testnet API keys
   ```

3. **Run basic validation**
   ```bash
   # Test exchange connectivity
   python scripts/test_connectivity.py
   
   # Run unit tests
   pytest tests/unit/
   ```

### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose -f infrastructure/docker/docker-compose.yml up --build
```

## 🔧 Configuration

Edit `configs/paper_trading.yaml`:

```yaml
environment: "paper"
exchange:
  name: "binance"
  testnet: true
  api_key: "${BINANCE_TESTNET_API_KEY}"  # Load from env var
  api_secret: "${BINANCE_TESTNET_API_SECRET}"

trading:
  symbols: ["BTC/USDT", "ETH/USDT"]
  timeframe: "1h"
  
risk:
  max_position_pct: 5.0     # Max 5% per position
  stop_loss_pct: 2.0        # 2% stop loss
  daily_loss_limit: 5.0     # Stop trading after 5% daily loss

monitoring:
  health_check_interval: 60
  prometheus_enabled: true
```

**Security Note:** Never commit API keys. Use environment variables or secrets management.

## 📈 Implemented Features

### ✅ Currently Working
- **Exchange Integration**: CCXT-based data fetching for Binance (spot & futures testnet)
- **Basic Strategy Framework**: Template for implementing classical strategies (MACD, RSI, etc.)
- **Risk Management Core**: Position sizing, basic stop-loss, and portfolio risk limits
- **Modular Architecture**: Clean separation between data, strategy, execution, and risk layers
- **Paper Trading Mode**: Safe testing with exchange testnets

### 🔄 Under Development
- Advanced backtesting engine
- Performance reporting and visualization
- Additional exchange integrations

### 📋 Planned (Contributions Welcome!)
- Machine learning signal integration
- Multi-timeframe analysis
- Advanced risk metrics and drawdown controls
- Telegram/Discord notifications

## 🧪 Testing & Validation

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/                    # Unit tests
pytest tests/integration/             # Integration tests

# Test with coverage report
pytest --cov=src tests/
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                 Main Controller             │
│              (Orchestrates flow)           │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐  ┌────▼────┐  ┌─────▼────┐
│ Data   │  │Strategy │  │ Risk     │
│ Fetcher│  │ Engine  │  │ Manager  │
│(CCXT)  │  │(Custom) │  │(Position │
└───┬────┘  └────┬────┘  │  Sizing) │
    │             │       └─────┬────┘
    └─────────────┼─────────────┘
                  │
             ┌────▼────┐
             │Executor │
             │(Orders) │
             └─────────┘
```

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. **Report Issues**: Found a bug? Open an issue with detailed steps to reproduce.
2. **Suggest Features**: Have ideas? Share them in the discussions.
3. **Submit Pull Requests**:
   - Fork the repository
   - Create a feature branch
   - Add tests for new functionality
   - Ensure all tests pass
   - Submit a PR with clear description

### Priority Areas for Contributors
- Implement classical trading strategies
- Enhance risk management modules
- Add comprehensive test coverage
- Improve documentation and examples

## ⚠️ Risk Warning & Disclaimer

**CRITICAL WARNINGS:**

1. **This is not financial advice** or a guaranteed profit system.
2. **Never trade with funds you cannot afford to lose**.
3. **Always start with paper trading** for at least 4-6 weeks.
4. **This software is provided "as is"** without warranties.
5. **You are solely responsible** for your trading decisions and outcomes.

Cryptocurrency markets are extremely volatile. Even well-tested algorithms can fail due to:
- Exchange outages
- Liquidity crises
- Regulatory changes
- Unforeseen market events

## 🔒 Security Best Practices

If you develop this into a live trading system:

1. **Use separate API keys** with minimal permissions (no withdrawal rights)
2. **Implement hardware-enforced stop losses**
3. **Run in isolated environments** (Docker containers, isolated VMs)
4. **Monitor 24/7** with alerts for system failures
5. **Regular security audits** of your deployment

## 📞 Support & Community

- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for strategy ideas and general questions
- **Contributing**: See CONTRIBUTING.md for development guidelines

## 📚 Learning Resources

- [CCXT Documentation](https://docs.ccxt.com/) - Exchange integration library
- [Algorithmic Trading](https://www.amazon.com/Algorithmic-Trading-Winning-Strategies-Rationale/dp/1118460146) - Recommended reading
- [Binance Testnet](https://testnet.binance.vision/) - Practice trading environment

## 📄 License

MIT License - see LICENSE file for details.

---

**Remember**: Successful algorithmic trading requires continuous learning, adaptation, and risk management. This framework is a starting point for your journey, not a destination.
