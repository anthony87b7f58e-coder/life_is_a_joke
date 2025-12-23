"""
Strategy Manager
Manages and executes trading strategies
"""

import logging
from typing import List, Dict
from .base_strategy import BaseStrategy
from ..simple_trend import SimpleTrendStrategy


class StrategyManager:
    """Manages multiple trading strategies"""
    
    def __init__(self, config, client, database, risk_manager):
        """
        Initialize strategy manager
        
        Args:
            config: Configuration object
            client: Binance client
            database: Database instance
            risk_manager: Risk manager instance
        """
        self.config = config
        self.client = client
        self.db = database
        self.risk_manager = risk_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize strategies
        self.strategies: List[BaseStrategy] = []
        self._load_strategies()
        
        self.logger.info(f"Strategy manager initialized with {len(self.strategies)} strategies")
    
    def _load_strategies(self):
        """Load and initialize trading strategies"""
        # Simple trend following strategy
        trend_strategy = SimpleTrendStrategy(
            self.config,
            self.client,
            self.db,
            self.risk_manager
        )
        self.strategies.append(trend_strategy)
        
        self.logger.info(f"Loaded strategy: {trend_strategy.name}")
    
    def evaluate_strategies(self):
        """Evaluate all active strategies"""
        self.logger.debug("Evaluating strategies...")
        
        for strategy in self.strategies:
            if not strategy.enabled:
                continue
            
            try:
                # Run strategy analysis
                signals = strategy.analyze()
                
                # Execute signals
                for signal in signals:
                    self._execute_signal(signal, strategy)
                    
            except Exception as e:
                self.logger.error(f"Error in strategy {strategy.name}: {str(e)}", exc_info=True)
    
    def _execute_signal(self, signal: Dict, strategy: BaseStrategy):
        """
        Execute a trading signal
        
        Args:
            signal: Signal dictionary with action, symbol, price, etc.
            strategy: Strategy that generated the signal
        """
        action = signal.get('action')
        symbol = signal.get('symbol')
        
        self.logger.info(f"Signal from {strategy.name}: {action} {symbol} at {signal.get('price')}")
        
        if action == 'BUY':
            self._execute_buy(signal, strategy)
        elif action == 'SELL':
            self._execute_sell(signal, strategy)
        elif action == 'CLOSE':
            self._close_position(signal, strategy)
    
    def _execute_buy(self, signal: Dict, strategy: BaseStrategy):
        """Execute buy order"""
        try:
            symbol = signal['symbol']
            price = signal['price']
            
            # Get account balance
            account = self.client.get_account()
            # Find USDT balance
            usdt_balance = 0
            for balance in account['balances']:
                if balance['asset'] == 'USDT':
                    usdt_balance = float(balance['free'])
                    break
            
            # Calculate position size
            quantity = self.risk_manager.calculate_position_size(symbol, price, usdt_balance)
            
            # Validate trade
            trade_data = {
                'symbol': symbol,
                'side': 'BUY',
                'price': price,
                'quantity': quantity,
                'is_opening': True
            }
            
            is_valid, error = self.risk_manager.validate_trade(trade_data)
            if not is_valid:
                self.logger.warning(f"Trade validation failed: {error}")
                return
            
            # Calculate stop loss and take profit
            stop_loss = self.risk_manager.calculate_stop_loss(price, 'BUY')
            take_profit = self.risk_manager.calculate_take_profit(price, 'BUY')
            
            self.logger.info(f"Executing BUY: {quantity} {symbol} at {price} (SL: {stop_loss}, TP: {take_profit})")
            
            # Place order (demo mode for now)
            if self.config.trading_mode == 'live' and self.config.trading_enabled:
                # Real order would go here
                self.logger.warning("Live trading not fully implemented - simulating order")
            
            # Record position in database
            position_id = self.db.create_position({
                'symbol': symbol,
                'side': 'BUY',
                'entry_price': price,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': strategy.name
            })
            
            # Record trade
            self.db.record_trade({
                'symbol': symbol,
                'side': 'BUY',
                'price': price,
                'quantity': quantity,
                'strategy': strategy.name
            })
            
            self.logger.info(f"Position opened: ID {position_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing buy order: {str(e)}", exc_info=True)
    
    def _execute_sell(self, signal: Dict, strategy: BaseStrategy):
        """Execute sell order"""
        # Similar to buy but for selling
        self.logger.info(f"SELL signal received for {signal.get('symbol')} (not implemented)")
    
    def _close_position(self, signal: Dict, strategy: BaseStrategy):
        """Close an open position"""
        position_id = signal.get('position_id')
        
        if not position_id:
            self.logger.warning("No position ID in close signal")
            return
        
        # Update position status
        self.db.update_position(
            position_id,
            status='closed',
            closed_at='CURRENT_TIMESTAMP'
        )
        
        self.logger.info(f"Position {position_id} closed")
    
    def close_all_positions(self):
        """Close all open positions"""
        self.logger.info("Closing all open positions...")
        
        open_positions = self.db.get_open_positions()
        
        for position in open_positions:
            try:
                # Close position logic here
                self.db.update_position(
                    position['id'],
                    status='closed',
                    closed_at='CURRENT_TIMESTAMP'
                )
                self.logger.info(f"Closed position: {position['symbol']}")
            except Exception as e:
                self.logger.error(f"Error closing position {position['id']}: {str(e)}")
        
        self.logger.info(f"Closed {len(open_positions)} positions")
