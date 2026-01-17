#!/usr/bin/env python3
"""
System health check utility
Tests all components and reports status
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import load_config
from src.data_fetcher import DataFetcher
from src.classic_strategy import ClassicTradingStrategy
from src.sentiment import SentimentAnalyzer
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def check_configuration():
    """Check if configuration loads correctly"""
    try:
        cfg = load_config()
        logger.info("✓ Configuration loaded successfully")
        
        # Check critical config sections
        checks = [
            ('environment', hasattr(cfg, 'environment') or 'environment' in cfg),
            ('trading', hasattr(cfg, 'trading') or 'trading' in cfg),
            ('exchanges', hasattr(cfg, 'exchanges') or 'exchanges' in cfg),
        ]
        
        for name, status in checks:
            if status:
                logger.info(f"  ✓ {name} section present")
            else:
                logger.warning(f"  ⚠ {name} section missing")
        
        return True
    except Exception as e:
        logger.error(f"✗ Configuration error: {e}")
        return False


async def check_data_fetcher():
    """Check if data fetcher can initialize"""
    try:
        cfg = load_config()
        df = DataFetcher(cfg)
        logger.info("✓ DataFetcher initialized")
        return True
    except Exception as e:
        logger.error(f"✗ DataFetcher error: {e}")
        return False


async def check_strategy():
    """Check if trading strategy works"""
    try:
        import pandas as pd
        import numpy as np
        
        # Create test data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
        np.random.seed(42)
        trend = np.linspace(100, 150, 100)
        noise = np.random.normal(0, 2, 100)
        close_prices = trend + noise
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices - np.random.uniform(0.5, 1.5, 100),
            'high': close_prices + np.random.uniform(0.5, 2, 100),
            'low': close_prices - np.random.uniform(0.5, 2, 100),
            'close': close_prices,
            'volume': np.random.uniform(1000, 5000, 100)
        })
        
        cfg = load_config()
        strategy = ClassicTradingStrategy(cfg)
        result = strategy.analyze_market(df)
        
        logger.info(f"✓ Trading strategy working (Signal: {result['signal']}, Confidence: {result['confidence']})")
        return True
    except Exception as e:
        logger.error(f"✗ Trading strategy error: {e}")
        return False


async def check_sentiment():
    """Check if sentiment analyzer works"""
    try:
        cfg = load_config()
        sentiment = SentimentAnalyzer(cfg)
        
        test_texts = [
            "Bitcoin is bullish and going to the moon!",
            "Market crash incoming, everything is bearish",
            "Stable price movement today"
        ]
        
        result = sentiment.analyze_texts(test_texts)
        logger.info(f"✓ Sentiment analyzer working (Score: {result['score']:.3f}, Sentiment: {result['sentiment']})")
        return True
    except Exception as e:
        logger.error(f"✗ Sentiment analyzer error: {e}")
        return False


async def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computing',
        'ccxt': 'Exchange connectivity',
        'yaml': 'Configuration',
        'cachetools': 'Caching',
    }
    
    all_ok = True
    for pkg, description in dependencies.items():
        try:
            __import__(pkg)
            logger.info(f"✓ {pkg:15s} - {description}")
        except ImportError:
            logger.error(f"✗ {pkg:15s} - MISSING ({description})")
            all_ok = False
    
    return all_ok


async def main():
    """Run all health checks"""
    print("=" * 60)
    print("CRYPTO TRADING BOT - HEALTH CHECK")
    print("=" * 60)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("Data Fetcher", check_data_fetcher),
        ("Trading Strategy", check_strategy),
        ("Sentiment Analyzer", check_sentiment),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        result = await check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:25s} {status}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All systems operational!")
        return 0
    else:
        print(f"\n⚠ {total - passed} system(s) need attention")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
