#!/usr/bin/env python3
"""
Test exchange connectivity and data fetching
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import load_config
from src.data_fetcher import DataFetcher
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


async def test_exchange_connection():
    """Test basic exchange connectivity"""
    print("=" * 60)
    print("EXCHANGE CONNECTIVITY TEST")
    print("=" * 60)
    
    try:
        # Load config
        cfg = load_config()
        print(f"\n✓ Configuration loaded")
        print(f"  Environment: {getattr(cfg, 'environment', cfg.get('environment', 'unknown'))}")
        
        # Initialize data fetcher
        df = DataFetcher(cfg)
        await df.initialize()
        
        if not df.exchanges:
            print("\n✗ No exchanges initialized!")
            print("  Make sure API keys are configured in .env file")
            return False
        
        print(f"\n✓ Initialized {len(df.exchanges)} exchange(s)")
        for name in df.exchanges.keys():
            print(f"  - {name}")
        
        # Test fetching data
        print("\n--- Testing Data Fetch ---")
        symbol = "BTC/USDT"
        timeframe = "1h"
        
        print(f"Fetching {symbol} {timeframe} data...")
        data = await df.fetch_ohlcv(symbol, timeframe, limit=100)
        
        if data is not None and not data.empty:
            print(f"✓ Successfully fetched {len(data)} candles")
            print(f"\nLatest candle:")
            print(f"  Timestamp: {data.index[-1]}")
            print(f"  Open:      ${data['open'].iloc[-1]:.2f}")
            print(f"  High:      ${data['high'].iloc[-1]:.2f}")
            print(f"  Low:       ${data['low'].iloc[-1]:.2f}")
            print(f"  Close:     ${data['close'].iloc[-1]:.2f}")
            print(f"  Volume:    {data['volume'].iloc[-1]:.2f}")
            
            # Test ticker
            print(f"\n--- Testing Ticker ---")
            ticker = await df.fetch_ticker(symbol)
            if ticker:
                print(f"✓ Current price: ${ticker['last']:.2f}")
                print(f"  Bid: ${ticker['bid']:.2f}")
                print(f"  Ask: ${ticker['ask']:.2f}")
                print(f"  24h Volume: {ticker['volume']:.2f}")
            
            success = True
        else:
            print("✗ Failed to fetch data")
            success = False
        
        # Cleanup
        await df.shutdown()
        
        return success
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


async def test_multiple_symbols():
    """Test fetching multiple symbols"""
    print("\n" + "=" * 60)
    print("MULTIPLE SYMBOLS TEST")
    print("=" * 60)
    
    try:
        cfg = load_config()
        df = DataFetcher(cfg)
        await df.initialize()
        
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
        print(f"\nFetching data for: {', '.join(symbols)}")
        
        for symbol in symbols:
            data = await df.fetch_ohlcv(symbol, "1h", limit=10)
            if data is not None and not data.empty:
                price = data['close'].iloc[-1]
                print(f"  ✓ {symbol:12s} - Latest price: ${price:,.2f}")
            else:
                print(f"  ✗ {symbol:12s} - Failed to fetch")
        
        await df.shutdown()
        return True
        
    except Exception as e:
        logger.error(f"Multiple symbols test failed: {e}")
        return False


async def main():
    """Run all connectivity tests"""
    
    # Test 1: Basic connectivity
    test1_ok = await test_exchange_connection()
    
    # Test 2: Multiple symbols (only if test 1 passed)
    test2_ok = False
    if test1_ok:
        test2_ok = await test_multiple_symbols()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Exchange Connection:  {'✓ PASS' if test1_ok else '✗ FAIL'}")
    print(f"Multiple Symbols:     {'✓ PASS' if test2_ok else '✗ FAIL'}")
    
    if test1_ok and test2_ok:
        print("\n✓ All tests passed! Exchange connectivity is working.")
        return 0
    elif not test1_ok:
        print("\n✗ Exchange connection failed.")
        print("\nTroubleshooting:")
        print("1. Check if API keys are set in .env file")
        print("2. For testnet: Get keys from https://testnet.binance.vision/")
        print("3. Check your internet connection")
        print("4. Verify environment setting in config.yaml")
        return 1
    else:
        print("\n⚠ Some tests failed. See above for details.")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
