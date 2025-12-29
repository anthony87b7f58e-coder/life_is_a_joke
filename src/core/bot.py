"""
Trading Bot Core
Main bot class that coordinates all components
"""

import time
import logging
from typing import Optional

from core.config import Config
from core.database import Database
from core.risk_manager import RiskManager
from core.exchange_adapter import ExchangeAdapter
from strategies.strategy_manager import StrategyManager


class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, config: Config):
        """
        Initialize trading bot
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # Validate configuration
        if not config.validate():
            raise ValueError("Invalid configuration")
        
        # Initialize components
        self.logger.info("Initializing trading bot components...")
        
        # Database
        self.db = Database(config)
        self.logger.info("Database initialized")
        
        # Exchange adapter (supports multiple exchanges via CCXT or Binance legacy)
        try:
            self.exchange = ExchangeAdapter(config)
            # Test connection
            self.exchange.ping()
            
            exchange_name = config.exchange_id if config.use_ccxt else 'Binance'
            testnet_str = 'TESTNET' if config.exchange_testnet else 'PRODUCTION'
            mode_str = 'CCXT' if config.use_ccxt else 'Legacy'
            
            self.logger.info(f"Connected to {exchange_name} {testnet_str} ({mode_str})")
        except Exception as e:
            self.logger.error(f"Failed to initialize exchange: {e}")
            raise
        
        # For backward compatibility, expose exchange as client
        self.client = self.exchange
        
        # Risk manager
        self.risk_manager = RiskManager(config, self.db)
        self.logger.info("Risk manager initialized")
        
        # Strategy manager
        self.strategy_manager = StrategyManager(config, self.exchange, self.db, self.risk_manager)
        self.logger.info("Strategy manager initialized")
        
        self.logger.info("Trading bot initialization complete")
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("=" * 70)
        self.logger.info("TRADING BOT STARTED")
        self.logger.info("=" * 70)
        self.logger.info(f"Exchange: {self.config.exchange_id if self.config.use_ccxt else 'Binance'}")
        self.logger.info(f"Mode: {'CCXT' if self.config.use_ccxt else 'Legacy'}")
        self.logger.info(f"Trading enabled: {self.config.trading_enabled}")
        self.logger.info(f"Default symbol: {self.config.default_symbol}")
        self.logger.info(f"Max open positions: {self.config.max_open_positions}")
        self.logger.info(f"Max daily trades: {self.config.max_daily_trades}")
        self.logger.info("=" * 70)
        
        self.running = True
        
        try:
            # Get account info
            account = self.exchange.get_account()
            self.logger.info(f"Account status: Can trade: {account.get('canTrade', True)}")
            
            # Main loop
            while self.running:
                try:
                    # Check risk limits
                    if not self.risk_manager.check_daily_limits():
                        self.logger.warning("Daily risk limits reached, skipping trading cycle")
                        time.sleep(60)
                        continue
                    
                    # Run strategy evaluation
                    if self.config.trading_enabled:
                        self.strategy_manager.evaluate_strategies()
                    else:
                        self.logger.debug("Trading disabled, running in monitoring mode only")
                    
                    # Health check
                    if self.config.health_check_enabled:
                        self._health_check()
                    
                    # Sleep before next cycle
                    time.sleep(60)  # Check every minute
                    
                except KeyboardInterrupt:
                    self.logger.info("Shutdown requested")
                    break
                except Exception as e:
                    self.logger.error(f"Error in main loop: {str(e)}", exc_info=True)
                    time.sleep(60)
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("Stopping trading bot...")
        self.running = False
        
        # Close all positions if configured
        if hasattr(self, 'strategy_manager'):
            self.strategy_manager.close_all_positions()
        
        # Close database connection
        if hasattr(self, 'db'):
            self.db.close()
        
        self.logger.info("Trading bot stopped")
    
    def _health_check(self):
        """Perform internal health check"""
        try:
            # Check API connectivity
            self.exchange.ping()
            
            # Check database
            self.db.health_check()
            
            # Log status
            open_positions = self.db.get_open_positions()
            self.logger.debug(f"Health check OK - Open positions: {len(open_positions)}")
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
