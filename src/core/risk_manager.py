"""
Risk Manager
Manages trading risks, position sizing, and daily limits
"""

import logging
from typing import Dict, Optional


class RiskManager:
    """Risk management for trading bot"""
    
    def __init__(self, config, database, exchange=None):
        """
        Initialize risk manager
        
        Args:
            config: Configuration object
            database: Database instance
            exchange: Exchange adapter instance (optional, for balance queries)
        """
        self.config = config
        self.db = database
        self.exchange = exchange
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Risk Manager initialized - Max daily trades: {config.max_daily_trades}, "
                        f"Max daily loss: {config.max_daily_loss_percentage}%")
    
    def check_daily_limits(self) -> bool:
        """
        Check if daily trading limits have been reached
        
        Returns:
            True if trading is allowed, False otherwise
        """
        # Check daily trade count
        daily_trades = self.db.get_daily_trade_count()
        if daily_trades >= self.config.max_daily_trades:
            self.logger.warning(f"Daily trade limit reached: {daily_trades}/{self.config.max_daily_trades}")
            return False
        
        # Check daily loss limit based on starting USDT balance
        daily_pl = self.db.get_daily_profit_loss()  # Absolute P&L in USDT
        
        # Only check if we have losses
        if daily_pl < 0:
            try:
                # Get current USDT balance
                current_usdt_balance = 0
                if self.exchange:
                    balance_data = self.exchange.fetch_balance()
                    # Extract USDT balance from various exchange formats
                    if 'USDT' in balance_data.get('free', {}):
                        current_usdt_balance = float(balance_data['free']['USDT'])
                    elif 'USDT' in balance_data.get('total', {}):
                        current_usdt_balance = float(balance_data['total']['USDT'])
                    else:
                        # Try to find USDT in other formats
                        for key in ['free', 'total', 'balances']:
                            if key in balance_data:
                                if isinstance(balance_data[key], dict) and 'USDT' in balance_data[key]:
                                    current_usdt_balance = float(balance_data[key]['USDT'])
                                    break
                
                # Calculate starting balance (current balance + losses already taken)
                starting_balance = current_usdt_balance - daily_pl  # daily_pl is negative, so this adds back the loss
                
                if starting_balance > 0:
                    # Calculate loss percentage based on starting balance
                    loss_percentage = (daily_pl / starting_balance) * 100.0
                    max_loss_percentage = -self.config.max_daily_loss_percentage
                    
                    if loss_percentage < max_loss_percentage:
                        self.logger.warning(
                            f"Daily loss limit reached: {loss_percentage:.2f}% of starting balance "
                            f"({abs(daily_pl):.2f} USDT loss from {starting_balance:.2f} USDT) "
                            f"(max: {max_loss_percentage}%)"
                        )
                        return False
                else:
                    self.logger.warning(f"Cannot calculate daily loss percentage: starting balance is {starting_balance}")
            
            except Exception as e:
                self.logger.error(f"Error checking daily loss limit: {e}", exc_info=True)
                # If we can't check properly, allow trading but log the issue
        
        return True
    
    def check_position_limits(self) -> bool:
        """
        Check if position limits have been reached
        
        Returns:
            True if new positions are allowed, False otherwise
        """
        open_positions = self.db.get_open_positions()
        
        if len(open_positions) >= self.config.max_open_positions:
            self.logger.warning(f"Max open positions reached: {len(open_positions)}/{self.config.max_open_positions}")
            return False
        
        return True
    
    def calculate_position_size(self, symbol: str, current_price: float, account_balance: float) -> float:
        """
        Calculate safe position size based on account balance and risk parameters
        
        Args:
            symbol: Trading symbol
            current_price: Current price
            account_balance: Account balance in quote currency
        
        Returns:
            Recommended position size
        """
        # Calculate position size as percentage of account balance
        position_value = account_balance * (self.config.position_size_percentage / 100.0)
        
        # Calculate quantity
        quantity = position_value / current_price
        
        # Respect max position size
        max_value = self.config.max_position_size * current_price
        if position_value > max_value:
            quantity = self.config.max_position_size
        
        self.logger.debug(f"Calculated position size for {symbol}: {quantity} (value: {quantity * current_price})")
        
        return quantity
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: 'BUY' or 'SELL'
        
        Returns:
            Stop loss price
        """
        percentage = self.config.stop_loss_percentage / 100.0
        
        if side == 'BUY':
            stop_loss = entry_price * (1 - percentage)
        else:  # SELL
            stop_loss = entry_price * (1 + percentage)
        
        return round(stop_loss, 8)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            side: 'BUY' or 'SELL'
        
        Returns:
            Take profit price
        """
        percentage = self.config.take_profit_percentage / 100.0
        
        if side == 'BUY':
            take_profit = entry_price * (1 + percentage)
        else:  # SELL
            take_profit = entry_price * (1 - percentage)
        
        return round(take_profit, 8)
    
    def validate_trade(self, trade_data: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate if a trade should be executed
        
        Args:
            trade_data: Trade data dictionary
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check daily limits
        if not self.check_daily_limits():
            return False, "Daily limits reached"
        
        # Check position limits for new positions
        if trade_data.get('is_opening', True):
            if not self.check_position_limits():
                return False, "Position limits reached"
        
        # Validate position size
        if trade_data.get('quantity', 0) <= 0:
            return False, "Invalid position size"
        
        # Validate price
        if trade_data.get('price', 0) <= 0:
            return False, "Invalid price"
        
        return True, None
