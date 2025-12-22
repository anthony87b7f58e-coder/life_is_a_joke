#!/usr/bin/env python3
"""
Main entry point for the Crypto Trading Bot
"""
import asyncio
import signal
import sys
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

# Configure logging
from src.utils import setup_logging
from src.health_monitor import HealthMonitor
from src.data_fetcher import DataFetcher
from src.predictor import HybridPredictor
from src.risk_manager import RiskManager
from src.executor import Executor
from src.reporter import Reporter
from src.config import Config

logger = logging.getLogger(__name__)

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config.load(config_path)
        self.is_running = False
        self.components = {}
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False
    
    async def initialize_components(self):
        """Initialize all bot components"""
        logger.info("Initializing bot components...")
        
        self.components = {
            'health': HealthMonitor(self.config),
            'data_fetcher': DataFetcher(self.config),
            'predictor': HybridPredictor(self.config),
            'risk_manager': RiskManager(self.config),
            'executor': Executor(self.config),
            'reporter': Reporter(self.config),
        }
        
        # Initialize each component
        for name, component in self.components.items():
            try:
                if hasattr(component, 'initialize'):
                    await component.initialize()
                elif hasattr(component, '__aenter__'):
                    await component.__aenter__()
                logger.info(f"✓ {name} initialized")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
                raise
        
        logger.info("All components initialized successfully")
    
    async def trading_cycle(self):
        """Execute one trading cycle"""
        try:
            logger.info("Starting trading cycle...")
            
            # 1. Fetch market data
            market_data = await self.components['data_fetcher'].fetch_all()
            
            if not market_data:
                logger.warning("No market data available")
                return
            
            # 2. Generate trading signals
            signals = await self.components['predictor'].analyze(market_data)
            
            # Filter signals by confidence
            valid_signals = [
                s for s in signals 
                if s['confidence'] >= self.config.trading.strategies.classic_macd_rsi.min_confidence
            ]
            
            if not valid_signals:
                logger.info("No valid trading signals")
                return
            
            logger.info(f"Generated {len(valid_signals)} valid signals")
            
            # 3. Apply risk management
            risk_assessed = []
            for signal in valid_signals:
                risk_assessment = self.components['risk_manager'].assess_signal(signal)
                if risk_assessment['approved']:
                    risk_assessed.append({
                        **signal,
                        'position_size': risk_assessment['position_size'],
                        'risk_score': risk_assessment['risk_score']
                    })
            
            # 4. Execute trades
            executed_trades = []
            for trade_signal in risk_assessed:
                try:
                    trade = await self.components['executor'].execute_trade(trade_signal)
                    if trade:
                        executed_trades.append(trade)
                        logger.info(f"Executed trade: {trade['symbol']} {trade['side']}")
                except Exception as e:
                    logger.error(f"Trade execution failed: {e}")
            
            # 5. Update monitoring
            await self.components['health'].update_metrics({
                'signals_generated': len(signals),
                'signals_valid': len(valid_signals),
                'trades_executed': len(executed_trades),
                'cycle_completed': True
            })
            
            # 6. Log cycle results
            logger.info(
                f"Cycle completed: {len(signals)} signals, "
                f"{len(valid_signals)} valid, {len(executed_trades)} executed"
            )
            
            return executed_trades
            
        except Exception as e:
            logger.error(f"Trading cycle failed: {e}")
            await self.components['health'].record_error(str(e))
            return []
    
    async def run(self):
        """Main bot loop"""
        try:
            await self.initialize_components()
            
            # Start health monitor
            await self.components['health'].start()
            
            self.is_running = True
            cycle_count = 0
            
            logger.info("🚀 Trading bot started successfully")
            
            # Main loop
            while self.is_running:
                cycle_count += 1
                logger.info(f"=== Trading Cycle #{cycle_count} ===")
                
                # Run trading cycle
                trades = await self.trading_cycle()
                
                # Generate report if needed
                if trades and self.config.reporting.generate_reports:
                    await self.components['reporter'].add_trades(trades)
                
                # Wait for next cycle
                if self.is_running:
                    wait_time = self.config.data.update_interval
                    logger.info(f"Waiting {wait_time}s for next cycle...")
                    
                    # Sleep with interruption check
                    for _ in range(wait_time):
                        if not self.is_running:
                            break
                        await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True)
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down bot...")
        
        # Shutdown components in reverse order
        for name in reversed(list(self.components.keys())):
            try:
                component = self.components[name]
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
                elif hasattr(component, '__aexit__'):
                    await component.__aexit__(None, None, None)
                logger.info(f"✓ {name} shut down")
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")
        
        logger.info("Bot shutdown complete")
        await asyncio.sleep(0.1)  # Let logs flush

async def main():
    """Application entry point"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Crypto Trading Bot")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--paper", action="store_true", help="Run in paper trading mode")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Create and run bot
    bot = TradingBot(args.config)
    
    # Override config if paper mode specified
    if args.paper:
        bot.config.environment = "paper"
    
    logger.info(f"Starting bot in {bot.config.environment} mode")
    
    try:
        await bot.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
