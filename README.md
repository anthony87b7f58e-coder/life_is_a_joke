# Life is a Joke - Cryptocurrency Exchange Manager

A Python-based cryptocurrency exchange management system with Telegram notifications.

## Features

### Exchange Management
- Integration with multiple cryptocurrency exchanges via CCXT library
- Support for Binance, Coinbase, Kraken, FTX, Bybit, KuCoin
- Operations: place orders, cancel orders, get balance, fetch tickers, etc.

### Telegram Notifications with Error Details
The system sends detailed Telegram notifications when operations fail, including:

- **Operation name** (in Russian)
- **Error type** (exception class name)
- **Error reason** (the actual error message)
- **Context information** (symbol, amount, price, exchange, etc.)

#### Example Notification Format:
```
🚨 Ошибка операции 🚨

Операция: Размещение ордера на binance
Тип ошибки: InsufficientFunds
Причина: Insufficient balance for trade

Дополнительная информация:
  • символ: BTC/USDT
  • тип ордера: limit
  • сторона: buy
  • количество: 0.5
  • цена: 50000
  • биржа: binance
```

### Insufficient Balance Error Handling
The system specifically handles insufficient balance errors:
- Catches `ccxt.InsufficientFunds` exceptions separately
- Sends Telegram notification with detailed context
- Returns structured error: `{"error": "insufficient_funds", "message": "..."}`

## Installation

```bash
pip install ccxt requests
```

## Configuration

### Telegram Bot Setup
1. Create a Telegram bot using [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Get your chat ID (you can use [@userinfobot](https://t.me/userinfobot))

### Environment Variables
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

## Usage

### Basic Example

```python
from src.core import ExchangeFactory, TelegramNotifier

# Setup Telegram notifications (optional)
# Reads from environment variables by default
notifier = TelegramNotifier()

# Create exchange manager
manager = ExchangeFactory.create_exchange(
    exchange_name='binance',
    api_key='your_api_key',
    api_secret='your_api_secret'
)

# Connect to exchange
if manager.connect():
    # Place an order
    result = manager.place_order(
        symbol='BTC/USDT',
        order_type='limit',
        side='buy',
        amount=0.1,
        price=50000
    )
    
    # Check for insufficient balance error
    if isinstance(result, dict) and result.get('error') == 'insufficient_funds':
        print("Insufficient balance!")
        # Telegram notification already sent with details
    elif result:
        print(f"Order placed: {result}")
```

### Notification Operations

The following operations send Telegram notifications on error:
- `connect()` - Connection errors
- `place_order()` - Order placement errors (including insufficient balance)
- `cancel_order()` - Order cancellation errors  
- `get_balance()` - Balance retrieval errors

## Module Structure

```
src/
└── core/
    ├── __init__.py              # Package initialization
    ├── exchange_manager.py      # Exchange operations with CCXT
    └── telegram_notifier.py     # Telegram notification system
```

## Security Features

- SSL verification enabled for all Telegram API requests
- Sensitive information logged at debug level only
- No credentials stored in code
- Environment variable configuration

## Error Handling

All critical operations include:
1. Proper exception handling
2. Detailed logging
3. Telegram notifications with error context
4. Graceful error returns (no crashes)

### Insufficient Balance Handling
```python
result = manager.place_order('BTC/USDT', 'limit', 'buy', 0.5, 50000)

if isinstance(result, dict):
    if result.get('error') == 'insufficient_funds':
        # Handle insufficient balance
        print(f"Error: {result.get('message')}")
    else:
        # Handle other errors
        print("Operation failed")
else:
    # Success
    print(f"Order ID: {result.get('id')}")
```

## License

This project is for educational and personal use.

## Requirements

- Python 3.7+
- ccxt >= 4.0.0
- requests >= 2.25.0

## Support

For issues related to:
- CCXT library: https://github.com/ccxt/ccxt
- Telegram Bot API: https://core.telegram.org/bots/api
