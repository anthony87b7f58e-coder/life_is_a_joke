"""
Strategy Manager
Manages and executes trading strategies
"""

import logging
from typing import List, Dict
from strategies.base_strategy import BaseStrategy
from strategies.simple_trend import SimpleTrendStrategy
from strategies.enhanced_multi_indicator import EnhancedMultiIndicatorStrategy
from utils.notifications import get_notifier


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
        # Get active strategy from config (default to enhanced)
        active_strategy = getattr(self.config, 'active_strategy', 'enhanced').lower()
        
        if active_strategy == 'simple':
            # Simple trend following strategy
            strategy = SimpleTrendStrategy(
                self.config,
                self.client,
                self.db,
                self.risk_manager
            )
            self.strategies.append(strategy)
            self.logger.info(f"Loaded strategy: {strategy.name}")
        else:
            # Enhanced multi-indicator strategy (default)
            strategy = EnhancedMultiIndicatorStrategy(
                self.config,
                self.client,
                self.db,
                self.risk_manager
            )
            self.strategies.append(strategy)
            self.logger.info(f"Loaded strategy: {strategy.name}")
    
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
            score = signal.get('confidence')  # Get signal score
            
            # Get account balance
            usdt_balance = 0
            try:
                if self.config.use_ccxt:
                    # CCXT balance fetch
                    balance = self.client.fetch_balance()
                    self.logger.debug(f"Balance structure keys: {list(balance.keys())}")
                    
                    # CCXT balance structure: balance['free']['USDT'] or balance['USDT']['free']
                    # Try both access patterns for maximum compatibility
                    try:
                        if 'free' in balance and isinstance(balance['free'], dict) and 'USDT' in balance['free']:
                            usdt_balance = float(balance['free']['USDT'])
                            self.logger.debug(f"Found USDT in balance['free']['USDT']: {usdt_balance}")
                        elif 'USDT' in balance and isinstance(balance['USDT'], dict) and 'free' in balance['USDT']:
                            usdt_balance = float(balance['USDT']['free'])
                            self.logger.debug(f"Found USDT in balance['USDT']['free']: {usdt_balance}")
                        else:
                            self.logger.warning(f"Could not find USDT in expected locations. Balance keys: {list(balance.keys())}")
                            if 'free' in balance and isinstance(balance['free'], dict):
                                self.logger.debug(f"balance['free'] currencies: {list(balance['free'].keys())}")
                    except (KeyError, TypeError, ValueError) as e:
                        self.logger.warning(f"Error extracting USDT balance: {e}")
                    
                    self.logger.info(f"Available USDT balance: ${usdt_balance:.2f}")
                else:
                    # Binance legacy API
                    account = self.client.get_account()
                    for bal in account['balances']:
                        if bal['asset'] == 'USDT':
                            usdt_balance = float(bal['free'])
                            break
                    self.logger.info(f"Available USDT balance: ${usdt_balance:.2f}")
            except Exception as e:
                self.logger.warning(f"Failed to fetch balance: {e}. Using default position size.")
                usdt_balance = 0
            
            # Calculate position size
            if usdt_balance > 0:
                quantity = self.risk_manager.calculate_position_size(symbol, price, usdt_balance)
                self.logger.info(f"Calculated position size based on balance: {quantity}")
            else:
                # Fallback to configured max position size if balance unavailable
                quantity = self.config.max_position_size
                self.logger.warning(f"Balance is 0 or unavailable, using configured MAX_POSITION_SIZE: {quantity}")
            
            # Check minimum order size requirements
            try:
                min_order_size = self.client.get_min_order_size(symbol)
                if quantity < min_order_size:
                    self.logger.warning(f"Calculated quantity {quantity} is below minimum {min_order_size}, adjusting")
                    quantity = min_order_size
            except Exception as e:
                self.logger.warning(f"Could not check minimum order size: {e}")
            
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
            
            # Place order
            order_id = None
            if self.config.trading_enabled:
                try:
                    # Place market buy order
                    order = self.client.create_order(
                        symbol=symbol,
                        side='buy',
                        order_type='market',
                        quantity=quantity
                    )
                    order_id = order.get('orderId')
                    executed_price = float(order.get('price', price))
                    executed_qty = float(order.get('executedQty', quantity))
                    
                    self.logger.info(f"BUY order executed: Order ID {order_id}, Price: {executed_price}, Quantity: {executed_qty}")
                    
                    # Update values with actual execution data
                    price = executed_price
                    quantity = executed_qty
                    
                except Exception as e:
                    self.logger.error(f"Failed to place BUY order: {str(e)}")
                    # Send error notification
                    notifier = get_notifier()
                    if notifier:
                        notifier.notify_error("Order Execution Failed", str(e), f"BUY {symbol}")
                    return
            else:
                self.logger.warning("Trading disabled - simulating order")
            
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
            
            # Send Telegram notification with score
            notifier = get_notifier()
            if notifier:
                notifier.notify_position_opened(
                    symbol=symbol,
                    side='BUY',
                    quantity=quantity,
                    price=price,
                    strategy=strategy.name,
                    score=score
                )
            
        except Exception as e:
            self.logger.error(f"Error executing buy order: {str(e)}", exc_info=True)
            # Send error notification
            notifier = get_notifier()
            if notifier:
                notifier.notify_error("Buy Order Failed", str(e), f"Symbol: {signal.get('symbol')}")
    
    def _execute_sell(self, signal: Dict, strategy: BaseStrategy):
        """Execute sell order (short position)"""
        try:
            symbol = signal['symbol']
            price = signal['price']
            score = signal.get('confidence')  # Get signal score
            
            # Get account balance
            usdt_balance = 0
            try:
                if self.config.use_ccxt:
                    # CCXT balance fetch
                    balance = self.client.fetch_balance()
                    self.logger.debug(f"Balance structure keys: {list(balance.keys())}")
                    
                    # CCXT balance structure: balance['free']['USDT'] or balance['USDT']['free']
                    # Try both access patterns for maximum compatibility
                    try:
                        if 'free' in balance and isinstance(balance['free'], dict) and 'USDT' in balance['free']:
                            usdt_balance = float(balance['free']['USDT'])
                            self.logger.debug(f"Found USDT in balance['free']['USDT']: {usdt_balance}")
                        elif 'USDT' in balance and isinstance(balance['USDT'], dict) and 'free' in balance['USDT']:
                            usdt_balance = float(balance['USDT']['free'])
                            self.logger.debug(f"Found USDT in balance['USDT']['free']: {usdt_balance}")
                        else:
                            self.logger.warning(f"Could not find USDT in expected locations. Balance keys: {list(balance.keys())}")
                            if 'free' in balance and isinstance(balance['free'], dict):
                                self.logger.debug(f"balance['free'] currencies: {list(balance['free'].keys())}")
                    except (KeyError, TypeError, ValueError) as e:
                        self.logger.warning(f"Error extracting USDT balance: {e}")
                    
                    self.logger.info(f"Available USDT balance: ${usdt_balance:.2f}")
                else:
                    # Binance legacy API
                    account = self.client.get_account()
                    for bal in account['balances']:
                        if bal['asset'] == 'USDT':
                            usdt_balance = float(bal['free'])
                            break
                    self.logger.info(f"Available USDT balance: ${usdt_balance:.2f}")
            except Exception as e:
                self.logger.warning(f"Failed to fetch balance: {e}. Using default position size.")
                usdt_balance = 0
            
            # Calculate position size
            if usdt_balance > 0:
                quantity = self.risk_manager.calculate_position_size(symbol, price, usdt_balance)
                self.logger.info(f"Calculated position size based on balance: {quantity}")
            else:
                # Fallback to configured max position size if balance unavailable
                quantity = self.config.max_position_size
                self.logger.warning(f"Balance is 0 or unavailable, using configured MAX_POSITION_SIZE: {quantity}")
            
            # Check minimum order size requirements
            try:
                min_order_size = self.client.get_min_order_size(symbol)
                if quantity < min_order_size:
                    self.logger.warning(f"Calculated quantity {quantity} is below minimum {min_order_size}, adjusting")
                    quantity = min_order_size
            except Exception as e:
                self.logger.warning(f"Could not check minimum order size: {e}")
            
            # Validate trade
            trade_data = {
                'symbol': symbol,
                'side': 'SELL',
                'price': price,
                'quantity': quantity,
                'is_opening': True
            }
            
            is_valid, error = self.risk_manager.validate_trade(trade_data)
            if not is_valid:
                self.logger.warning(f"Trade validation failed: {error}")
                return
            
            # Calculate stop loss and take profit
            stop_loss = self.risk_manager.calculate_stop_loss(price, 'SELL')
            take_profit = self.risk_manager.calculate_take_profit(price, 'SELL')
            
            self.logger.info(f"Executing SELL: {quantity} {symbol} at {price} (SL: {stop_loss}, TP: {take_profit})")
            
            # Place order
            order_id = None
            if self.config.trading_enabled:
                try:
                    # Place market sell order
                    order = self.client.create_order(
                        symbol=symbol,
                        side='sell',
                        order_type='market',
                        quantity=quantity
                    )
                    order_id = order.get('orderId')
                    executed_price = float(order.get('price', price))
                    executed_qty = float(order.get('executedQty', quantity))
                    
                    self.logger.info(f"SELL order executed: Order ID {order_id}, Price: {executed_price}, Quantity: {executed_qty}")
                    
                    # Update values with actual execution data
                    price = executed_price
                    quantity = executed_qty
                    
                except Exception as e:
                    self.logger.error(f"Failed to place SELL order: {str(e)}")
                    # Send error notification
                    notifier = get_notifier()
                    if notifier:
                        notifier.notify_error("Order Execution Failed", str(e), f"SELL {symbol}")
                    return
            else:
                self.logger.warning("Trading disabled - simulating order")
            
            # Record position in database
            position_id = self.db.create_position({
                'symbol': symbol,
                'side': 'SELL',
                'entry_price': price,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'strategy': strategy.name
            })
            
            # Record trade
            self.db.record_trade({
                'symbol': symbol,
                'side': 'SELL',
                'price': price,
                'quantity': quantity,
                'strategy': strategy.name
            })
            
            self.logger.info(f"Position opened: ID {position_id}")
            
            # Send Telegram notification with score
            notifier = get_notifier()
            if notifier:
                notifier.notify_position_opened(
                    symbol=symbol,
                    side='SELL',
                    quantity=quantity,
                    price=price,
                    strategy=strategy.name,
                    score=score
                )
            
        except Exception as e:
            self.logger.error(f"Error executing sell order: {str(e)}", exc_info=True)
            # Send error notification
            notifier = get_notifier()
            if notifier:
                notifier.notify_error("Sell Order Failed", str(e), f"Symbol: {signal.get('symbol')}")
    
    def _close_position(self, signal: Dict, strategy: BaseStrategy):
        """Close an open position"""
        position_id = signal.get('position_id')
        score = signal.get('confidence')  # Get signal score
        
        if not position_id:
            self.logger.warning("No position ID in close signal")
            return
        
        try:
            # Get position details before closing
            position = self.db.get_position(position_id)
            if not position:
                self.logger.warning(f"Position {position_id} not found")
                return
            
            exit_price = signal.get('price', 0)
            entry_price = position.get('entry_price', 0)
            quantity = position.get('quantity', 0)
            side = position.get('side', 'BUY')
            symbol = position.get('symbol', '')
            
            # Close position on exchange
            order_id = None
            if self.config.trading_enabled:
                try:
                    # Close position with opposite order
                    close_side = 'sell' if side == 'BUY' else 'buy'
                    order = self.client.create_order(
                        symbol=symbol,
                        side=close_side,
                        order_type='market',
                        quantity=quantity
                    )
                    order_id = order.get('orderId')
                    exit_price = float(order.get('price', exit_price))
                    
                    self.logger.info(f"Position closed: Order ID {order_id}, Exit price: {exit_price}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to close position on exchange: {str(e)}")
                    # Send error notification
                    notifier = get_notifier()
                    if notifier:
                        notifier.notify_error("Position Close Failed", str(e), f"{symbol} Position ID: {position_id}")
                    return
            else:
                self.logger.warning("Trading disabled - simulating position close")
            
            # Calculate P&L
            if side == 'BUY':
                pnl = (exit_price - entry_price) * quantity
            else:
                pnl = (entry_price - exit_price) * quantity
            
            pnl_percent = (pnl / (entry_price * quantity) * 100) if (entry_price * quantity) > 0 else 0
            
            # Update position status
            self.db.update_position(
                position_id,
                status='closed',
                closed_at='CURRENT_TIMESTAMP',
                exit_price=exit_price,
                pnl=pnl
            )
            
            self.logger.info(f"Position {position_id} closed with P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)")
            
            # Send Telegram notification with score
            notifier = get_notifier()
            if notifier:
                notifier.notify_position_closed(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    strategy=position.get('strategy', 'Unknown'),
                    score=score
                )
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {str(e)}", exc_info=True)
    
    def close_all_positions(self):
        """Close all open positions"""
        self.logger.info("Closing all open positions...")
        
        open_positions = self.db.get_open_positions()
        
        for position in open_positions:
            try:
                symbol = position.get('symbol')
                quantity = position.get('quantity', 0)
                side = position.get('side', 'BUY')
                
                # Close position on exchange
                if self.config.trading_enabled:
                    try:
                        # Close position with opposite order
                        close_side = 'sell' if side == 'BUY' else 'buy'
                        order = self.client.create_order(
                            symbol=symbol,
                            side=close_side,
                            order_type='market',
                            quantity=quantity
                        )
                        self.logger.info(f"Closed position {position['id']} on exchange: Order ID {order.get('orderId')}")
                    except Exception as e:
                        self.logger.error(f"Failed to close position {position['id']} on exchange: {str(e)}")
                
                # Update database
                self.db.update_position(
                    position['id'],
                    status='closed',
                    closed_at='CURRENT_TIMESTAMP'
                )
                self.logger.info(f"Closed position in database: {position['symbol']}")
            except Exception as e:
                self.logger.error(f"Error closing position {position['id']}: {str(e)}")
        
        self.logger.info(f"Closed {len(open_positions)} positions")
