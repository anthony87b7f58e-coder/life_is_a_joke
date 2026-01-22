# Quick Start Guide - Using the Fixed Code

## What Was Fixed?
The InsufficientFunds error from Bybit is now properly handled. The code was updated to:
1. ✅ Raise proper exceptions instead of returning empty dictionaries
2. ✅ Validate balance before placing orders (advisory check)
3. ✅ Provide detailed error messages with full context
4. ✅ Handle different error types (InsufficientFunds, NetworkError, ConnectionError)

## How to Use

### Step 1: Install Dependencies
```bash
pip install ccxt
```

### Step 2: Update Your Code
**IMPORTANT**: The API changed. You must use try-except blocks now.

#### ❌ Old Code (Won't Work)
```python
order = manager.place_order('BTC/USDT', 'limit', 'buy', 0.001, 50000)
if order:
    print("Success!")
```

#### ✅ New Code (Required)
```python
try:
    order = manager.place_order('BTC/USDT', 'limit', 'buy', 0.001, 50000)
    print(f"Order placed successfully: {order['id']}")
    
except ccxt.InsufficientFunds as e:
    print(f"⚠️  Not enough balance: {e}")
    # Option 1: Check your balance
    balance = manager.get_balance()
    print(f"Available USDT: {balance['free']['USDT']}")
    # Option 2: Reduce order amount
    # Option 3: Add funds to account
    
except ccxt.NetworkError as e:
    print(f"🌐 Network problem: {e}")
    # Retry after a delay
    
except ConnectionError as e:
    print(f"❌ Not connected: {e}")
    # Reconnect: manager.connect()
    
except Exception as e:
    print(f"❌ Unexpected error: {type(e).__name__}: {e}")
```

### Step 3: Initialize the Manager
```python
from src.core.exchange_manager import ExchangeFactory

# Create Bybit exchange manager
manager = ExchangeFactory.create_exchange(
    exchange_name='bybit',
    api_key='YOUR_API_KEY',
    api_secret='YOUR_API_SECRET'
)

# Connect to exchange
if manager.connect():
    print("✅ Connected to Bybit")
else:
    print("❌ Failed to connect")
```

### Step 4: Check Balance First (Recommended)
```python
try:
    balance = manager.get_balance()
    
    # Check specific currency
    usdt_available = balance['free'].get('USDT', 0)
    btc_available = balance['free'].get('BTC', 0)
    
    print(f"Available USDT: {usdt_available}")
    print(f"Available BTC: {btc_available}")
    
except Exception as e:
    print(f"Error fetching balance: {e}")
```

### Step 5: Place Orders with Proper Error Handling
```python
def place_order_safe(manager, symbol, order_type, side, amount, price=None):
    """Safely place an order with comprehensive error handling."""
    try:
        # The manager will now check balance automatically (advisory)
        # and log a warning if it looks insufficient
        
        order = manager.place_order(symbol, order_type, side, amount, price)
        
        print(f"✅ Order placed successfully!")
        print(f"   Order ID: {order.get('id')}")
        print(f"   Symbol: {symbol}")
        print(f"   Type: {order_type}")
        print(f"   Side: {side}")
        print(f"   Amount: {amount}")
        print(f"   Price: {price}")
        
        return order
        
    except ccxt.InsufficientFunds as e:
        print(f"⚠️  INSUFFICIENT FUNDS")
        print(f"   Error: {e}")
        print(f"   Action needed: Add funds or reduce order size")
        return None
        
    except ccxt.NetworkError as e:
        print(f"🌐 NETWORK ERROR")
        print(f"   Error: {e}")
        print(f"   Action: Check internet connection and retry")
        return None
        
    except ConnectionError as e:
        print(f"❌ CONNECTION ERROR")
        print(f"   Error: {e}")
        print(f"   Action: Reconnect to exchange")
        return None
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR")
        print(f"   Type: {type(e).__name__}")
        print(f"   Error: {e}")
        return None

# Example usage
order = place_order_safe(
    manager=manager,
    symbol='BTC/USDT',
    order_type='limit',
    side='buy',
    amount=0.001,
    price=50000
)
```

## Understanding the Logs

### Advisory Warning (Not an Error)
```
WARNING: Local balance check suggests insufficient funds for buy order: 0.001 BTC/USDT
WARNING: Insufficient USDT balance. Required: 50.0, Available: 30.0
```
**Meaning**: The code detected potential insufficient balance and warns you, but still tries to place the order (exchange is authoritative).

### Actual Error
```
ERROR: Insufficient balance for order: InsufficientFunds: bybit {"retCode":170131,"retMsg":"Insufficient balance.",...}
```
**Meaning**: The exchange rejected the order due to insufficient balance. Exception is raised to your code.

## Common Scenarios

### Scenario 1: Check Balance Before Trading
```python
try:
    balance = manager.get_balance()
    usdt = balance['free']['USDT']
    
    # Calculate max you can buy
    max_btc = usdt / 50000  # BTC price
    safe_amount = max_btc * 0.95  # Leave 5% buffer for fees
    
    order = manager.place_order('BTC/USDT', 'market', 'buy', safe_amount)
    
except ccxt.InsufficientFunds:
    print("Still not enough - check for fees and minimum amounts")
except Exception as e:
    print(f"Error: {e}")
```

### Scenario 2: Retry with Smaller Amount
```python
amounts = [0.001, 0.0005, 0.0001]  # Try decreasing amounts

for amount in amounts:
    try:
        order = manager.place_order('BTC/USDT', 'market', 'buy', amount)
        print(f"Success with amount: {amount}")
        break
    except ccxt.InsufficientFunds:
        print(f"Not enough for {amount}, trying smaller...")
        continue
    except Exception as e:
        print(f"Other error: {e}")
        break
else:
    print("All amounts failed - need to add funds")
```

### Scenario 3: Handle All Exchange Operations
```python
class TradingBot:
    def __init__(self, exchange_name, api_key, api_secret):
        self.manager = ExchangeFactory.create_exchange(
            exchange_name, api_key, api_secret
        )
        
    def connect(self):
        try:
            if self.manager.connect():
                print("✅ Connected")
                return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_balance_safe(self):
        try:
            return self.manager.get_balance()
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None
    
    def buy(self, symbol, amount, price=None):
        try:
            order_type = 'market' if price is None else 'limit'
            return self.manager.place_order(
                symbol, order_type, 'buy', amount, price
            )
        except ccxt.InsufficientFunds as e:
            print(f"Not enough balance: {e}")
            return None
        except Exception as e:
            print(f"Order failed: {e}")
            return None

# Usage
bot = TradingBot('bybit', 'key', 'secret')
if bot.connect():
    balance = bot.get_balance_safe()
    if balance:
        order = bot.buy('BTC/USDT', 0.001, 50000)
```

## Troubleshooting

### Issue: InsufficientFunds Error
**Cause**: Not enough balance in your account
**Solution**: 
1. Check balance: `manager.get_balance()`
2. Verify you have the right currency (USDT for BTC/USDT buy orders)
3. Account for fees (usually 0.1% or more)
4. Add funds or reduce order size

### Issue: ConnectionError
**Cause**: Not connected to exchange
**Solution**: Call `manager.connect()` first

### Issue: NetworkError
**Cause**: Network connectivity issues
**Solution**: 
1. Check internet connection
2. Verify exchange API is accessible
3. Retry after a delay

### Issue: Invalid Symbol
**Cause**: Trading pair not supported or wrong format
**Solution**: 
1. Use format like 'BTC/USDT' not 'BTCUSDT'
2. Check supported symbols: `manager.get_supported_symbols()`

## Additional Resources

- **FIXES.md**: Detailed technical documentation of all changes
- **SUMMARY.md**: High-level overview of the fix
- **Exchange Manager Code**: `src/core/exchange_manager.py`

## Need Help?

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify API credentials are correct
3. Ensure CCXT is installed: `pip install ccxt`
4. Check your account balance on the exchange website
5. Review the exception type and message for specific guidance

---

**Last Updated**: 2026-01-07
**Status**: ✅ Production Ready
