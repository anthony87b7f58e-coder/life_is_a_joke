"""
Exchange Adapter
Provides a unified interface for multiple cryptocurrency exchanges using CCXT
"""

import logging
import ccxt
from typing import Optional, Dict, List
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException


class ExchangeAdapter:
    """
    Unified exchange interface supporting multiple exchanges via CCXT
    
    Supports both direct Binance client (for backward compatibility)
    and CCXT unified API for multi-exchange support
    """
    
    def __init__(self, config):
        """
        Initialize exchange adapter
        
        Args:
            config: Configuration object with exchange settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.exchange = None
        self.exchange_id = config.exchange_id.lower()
        self.use_ccxt = config.use_ccxt
        
        # Initialize the appropriate exchange
        if self.use_ccxt:
            self._init_ccxt_exchange()
        else:
            self._init_binance_legacy()
    
    def _init_ccxt_exchange(self):
        """Initialize exchange using CCXT"""
        self.logger.info(f"Initializing {self.exchange_id} exchange via CCXT...")
        
        try:
            # Get the exchange class from CCXT
            exchange_class = getattr(ccxt, self.exchange_id)
            
            # Configure exchange
            exchange_config = {
                'apiKey': self.config.exchange_api_key,
                'secret': self.config.exchange_api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # spot, margin, future, swap
                }
            }
            
            # Add testnet support for supported exchanges
            if self.config.exchange_testnet:
                if self.exchange_id == 'binance':
                    exchange_config['options']['defaultType'] = 'spot'
                    exchange_config['options']['test'] = True
                elif self.exchange_id in ['bybit', 'okx']:
                    exchange_config['sandbox'] = True
            
            # Create exchange instance
            self.exchange = exchange_class(exchange_config)
            
            # Load markets
            self.exchange.load_markets()
            
            self.logger.info(f"Connected to {self.exchange_id} via CCXT")
            self.logger.info(f"Supported markets: {len(self.exchange.markets)}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.exchange_id}: {str(e)}")
            raise
    
    def _init_binance_legacy(self):
        """Initialize Binance using legacy python-binance client (backward compatibility)"""
        self.logger.info("Initializing Binance (legacy mode)...")
        
        try:
            self.exchange = BinanceClient(
                self.config.exchange_api_key,
                self.config.exchange_api_secret,
                testnet=self.config.exchange_testnet
            )
            self.exchange.ping()
            self.logger.info("Connected to Binance (legacy mode)")
        except BinanceAPIException as e:
            self.logger.error(f"Failed to connect to Binance: {e}")
            raise
    
    def ping(self):
        """Test connection to exchange"""
        try:
            if self.use_ccxt:
                # Try fetch_status first, but not all exchanges support it
                try:
                    return self.exchange.fetch_status()
                except Exception:
                    # Fallback: try to fetch a ticker for a common trading pair
                    # This confirms the exchange is reachable and API keys are valid
                    # Use first symbol from trading_symbols list to ensure single symbol
                    test_symbol = self.config.trading_symbols[0] if self.config.trading_symbols else 'BTC/USDT'
                    self.exchange.fetch_ticker(test_symbol)
                    return {'status': 'ok', 'updated': None}
            else:
                return self.exchange.ping()
        except Exception as e:
            self.logger.error(f"Ping failed: {str(e)}")
            raise
    
    def get_account(self):
        """Get account information"""
        try:
            if self.use_ccxt:
                balance = self.exchange.fetch_balance()
                # Convert to similar format as Binance
                return {
                    'canTrade': True,  # CCXT doesn't provide this directly
                    'canWithdraw': True,
                    'canDeposit': True,
                    'balances': [
                        {
                            'asset': asset,
                            'free': str(balance['free'].get(asset, 0)),
                            'locked': str(balance['used'].get(asset, 0))
                        }
                        for asset in balance['total'].keys() if balance['total'][asset] > 0
                    ]
                }
            else:
                return self.exchange.get_account()
        except Exception as e:
            self.logger.error(f"Failed to get account info: {str(e)}")
            raise
    
    def get_symbol_ticker(self, symbol: str):
        """Get ticker for a symbol"""
        try:
            if self.use_ccxt:
                ticker = self.exchange.fetch_ticker(symbol)
                return {
                    'symbol': symbol,
                    'price': str(ticker['last'])
                }
            else:
                return self.exchange.get_symbol_ticker(symbol=symbol)
        except Exception as e:
            self.logger.error(f"Failed to get ticker for {symbol}: {str(e)}")
            raise
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100):
        """Get candlestick data"""
        try:
            if self.use_ccxt:
                # Convert Binance-style interval to CCXT timeframe
                timeframe_map = {
                    '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
                    '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '12h': '12h',
                    '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'
                }
                timeframe = timeframe_map.get(interval, '1h')
                
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                # Convert to Binance format
                # CCXT returns: [timestamp, open, high, low, close, volume]
                # Binance expects: [timestamp, open, high, low, close, volume, close_time, ...]
                return [
                    [
                        candle[0],  # timestamp
                        str(candle[1]),  # open
                        str(candle[2]),  # high
                        str(candle[3]),  # low
                        str(candle[4]),  # close
                        str(candle[5]),  # volume
                        candle[0] + self.exchange.parse_timeframe(timeframe) * 1000,  # close_time
                        '0',  # quote_asset_volume
                        0,  # number_of_trades
                        '0',  # taker_buy_base_volume
                        '0',  # taker_buy_quote_volume
                        '0'  # ignore
                    ]
                    for candle in ohlcv
                ]
            else:
                return self.exchange.get_klines(symbol=symbol, interval=interval, limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to get klines for {symbol}: {str(e)}")
            raise
    
    def create_order(self, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None):
        """
        Create an order
        
        Args:
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            order_type: 'market' or 'limit'
            quantity: Amount to trade
            price: Price (required for limit orders)
        """
        try:
            if self.use_ccxt:
                params = {}
                if order_type.lower() == 'market':
                    order = self.exchange.create_market_order(symbol, side.lower(), quantity, params)
                else:
                    if price is None:
                        raise ValueError("Price required for limit orders")
                    order = self.exchange.create_limit_order(symbol, side.lower(), quantity, price, params)
                
                return {
                    'orderId': order['id'],
                    'symbol': symbol,
                    'status': order['status'],
                    'side': side.upper(),
                    'type': order_type.upper(),
                    'price': str(order.get('price', price)),
                    'origQty': str(quantity),
                    'executedQty': str(order.get('filled', 0)),
                    'transactTime': order.get('timestamp', 0)
                }
            else:
                # Legacy Binance client
                if order_type.lower() == 'market':
                    return self.exchange.order_market(
                        symbol=symbol,
                        side=side.upper(),
                        quantity=quantity
                    )
                else:
                    return self.exchange.order_limit(
                        symbol=symbol,
                        side=side.upper(),
                        quantity=quantity,
                        price=price
                    )
        except Exception as e:
            self.logger.error(f"Failed to create order: {str(e)}")
            raise
    
    def get_exchange_info(self):
        """Get exchange information"""
        try:
            if self.use_ccxt:
                markets = self.exchange.markets
                return {
                    'symbols': [
                        {
                            'symbol': symbol,
                            'status': 'TRADING',
                            'baseAsset': market['base'],
                            'quoteAsset': market['quote']
                        }
                        for symbol, market in markets.items()
                    ]
                }
            else:
                return self.exchange.get_exchange_info()
        except Exception as e:
            self.logger.error(f"Failed to get exchange info: {str(e)}")
            raise
    
    def get_supported_exchanges(self) -> List[str]:
        """Get list of supported exchanges"""
        return ccxt.exchanges
