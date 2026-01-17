import asyncio
import pandas as pd
import numpy as np
from src.classic_strategy import ClassicTradingStrategy
from src.data_fetcher import DataFetcher

async def test_strategy():
    # Тестовые данные (симуляция)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    np.random.seed(42)
    
    # Генерируем тестовые данные с трендом
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
    
    # Тестируем стратегию
    config = {'classic_strategy': {'enabled': True}}
    strategy = ClassicTradingStrategy(config)
    
    result = strategy.analyze_market(df)
    
    print("Результат анализа:")
    print(f"Сигнал: {result['signal']}")
    print(f"Уверенность: {result['confidence']}")
    print(f"Индикаторы: {result['indicators']}")
    
    # Тест расчета позиции
    position = strategy.calculate_position_size(
        balance=10000,
        price=df['close'].iloc[-1]
    )
    print(f"\nРазмер позиции: {position}")

if __name__ == "__main__":
    asyncio.run(test_strategy())
