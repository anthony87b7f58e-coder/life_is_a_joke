# Example: How the Symbol Format Fix Solves the CCXT/Bybit Issue

## Problem Statement

The trading bot was experiencing this error:
```
ccxt.base.errors.BadSymbol: bybit does not have market symbol BNB/USDT
```

And the log shows:
```
Default symbol: BTCUSDT
```

This indicates a mismatch between:
1. The bot's symbol format (BTCUSDT - no slash)
2. CCXT's expected format (BTC/USDT - with slash)

## Root Cause

- CCXT library uses a unified format with slashes (e.g., BTC/USDT)
- Bot configuration or code was using concatenated format (e.g., BTCUSDT)
- When the bot tried to use BNB/USDT on Bybit, it failed because:
  - a) The symbol might not exist on Bybit
  - b) The format wasn't being normalized properly

## Solution

The fix adds three key improvements to the CCXTExchangeManager class:

1. **load_markets()** on connection:
   - Ensures the exchange object has all available symbols loaded
   - This populates exchange.markets with all valid trading pairs
   
2. **normalize_symbol()** method:
   - Converts BTCUSDT → BTC/USDT automatically
   - Checks if symbol already exists in correct format
   - Tries common quote currencies (USDT, USDC, USD, BTC, ETH, etc.)
   - Returns original symbol if normalization fails
   
3. **validate_symbol()** method:
   - Checks if a symbol exists on the exchange
   - Provides helpful error messages when symbol is invalid
   - Suggests available alternatives

## Usage Example

Before the fix:
```python
manager.get_ticker('BTCUSDT')  # ❌ Would fail with BadSymbol error
```

After the fix:
```python
manager.get_ticker('BTCUSDT')  # ✓ Automatically converts to 'BTC/USDT'
manager.get_ticker('BTC/USDT')  # ✓ Works as-is (already correct format)
```

The normalization happens transparently in all methods:
- get_ticker()
- get_orderbook()
- place_order()
- cancel_order()
- get_open_orders()
- get_closed_orders()

## Example Code

```python
from src.core.exchange_manager import CCXTExchangeManager

# Create exchange manager
manager = CCXTExchangeManager(
    exchange_name='bybit',
    api_key='your_api_key',
    api_secret='your_api_secret'
)

# Connect to exchange
if manager.connect():
    # Now you can use EITHER format:
    
    # Format 1: Concatenated (BTCUSDT) - will be normalized
    ticker1 = manager.get_ticker('BTCUSDT')
    
    # Format 2: CCXT unified (BTC/USDT) - will be used as-is
    ticker2 = manager.get_ticker('BTC/USDT')
    
    # Both work the same way!
    
    # You can also validate before using:
    if manager.validate_symbol('BNBUSDT'):
        # Symbol exists on this exchange
        ticker = manager.get_ticker('BNBUSDT')
    else:
        # Symbol doesn't exist, use a different one
        ticker = manager.get_ticker('BTCUSDT')
```

## Benefits

1. **Backward Compatible**: Old code using 'BTCUSDT' format still works
2. **Forward Compatible**: New code can use 'BTC/USDT' format
3. **Error Prevention**: Validates symbols before API calls
4. **Better Debugging**: Clear error messages when symbols don't exist
5. **Exchange Agnostic**: Works with any CCXT-supported exchange

## Technical Details

The normalize_symbol() method:
1. Returns symbol immediately if it already exists in exchange.markets
2. Tries to split concatenated symbols using common quote currencies
3. Checks if the normalized format exists in exchange.markets
4. Falls back to original symbol if no match found

This solves the original error because:
- 'BTCUSDT' → normalized to → 'BTC/USDT' (exists on Bybit)
- 'BNB/USDT' → checked directly → might not exist on Bybit (proper error)
- 'BNBUSDT' → normalized to → 'BNB/USDT' → checked if exists

The fix ensures that regardless of input format, CCXT gets the correct unified format that it expects.
