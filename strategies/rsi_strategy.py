import pandas as pd
import numpy as np

class RSIStrategy:
    RSI_PERIOD = 14
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Генерация сигналов"""
        df['rsi'] = self._calculate_rsi(df)
        df['signal'] = 0
        df.loc[df['rsi'] < 30, 'signal'] = 1   # BUY
        df.loc[df['rsi'] > 70, 'signal'] = -1  # SELL
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.Series:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.RSI_PERIOD).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def should_buy(self, data: dict) -> bool:
        return data.get('rsi', 50) < 30
    
    def should_sell(self, data: dict) -> bool:
        return data.get('rsi', 50) > 70
