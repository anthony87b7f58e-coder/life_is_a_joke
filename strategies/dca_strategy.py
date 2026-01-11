"""
Dollar Cost Averaging Strategy
"""
import pandas as pd
from typing import Dict


class DCAStrategy:
    DCA_INTERVAL = 24  # hours
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dollar Cost Averaging"""
        df['signal'] = 0
        df['buy_interval'] = range(len(df)) % self.DCA_INTERVAL
        df.loc[df['buy_interval'] == 0, 'signal'] = 1  # Buy every N periods
        return df
    
    def should_buy(self, data: dict) -> bool:
        return True  # DCA buys regularly
    
    def should_sell(self, data: dict) -> bool:
        profit_pct = data.get('unrealized_pnl', 0)
        return profit_pct > 20  # Sell at 20% profit
