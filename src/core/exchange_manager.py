"""
Exchange Manager Module

This module provides integration with CCXT (CryptoCurrency eXchange Trading) library
for managing cryptocurrency exchange connections and operations.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
import ccxt

logger = logging.getLogger(__name__)


class ExchangeManager(ABC):
    """
    Abstract base class for exchange management.
    Defines the interface for exchange operations.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the exchange."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the exchange."""
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information for a symbol."""
        pass

    @abstractmethod
    def place_order(self, symbol: str, order_type: str, side: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order on the exchange."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an open order."""
        pass


class CCXTExchangeManager(ExchangeManager):
    """
    CCXT-based exchange manager.
    Provides unified interface to multiple cryptocurrency exchanges via CCXT library.
    """

    def __init__(self, exchange_name: str, api_key: str, api_secret: str, passphrase: Optional[str] = None, **kwargs):
        """
        Initialize CCXT Exchange Manager.

        Args:
            exchange_name: Name of the exchange (e.g., 'binance', 'coinbase', 'kraken')
            api_key: API key for the exchange
            api_secret: API secret for the exchange
            passphrase: Optional passphrase (required by some exchanges like Coinbase)
            **kwargs: Additional exchange-specific configuration options
        """
        self.exchange_name = exchange_name.lower()
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.exchange = None
        self.is_connected = False
        self.config = kwargs

        logger.info(f"Initializing CCXT Exchange Manager for {self.exchange_name}")

    def connect(self) -> bool:
        """
        Connect to the exchange using CCXT.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            config = {
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                **self.config
            }

            if self.passphrase:
                config['password'] = self.passphrase

            self.exchange = exchange_class(config)
            self.is_connected = True
            logger.info(f"Successfully connected to {self.exchange_name}")
            return True

        except AttributeError:
            logger.error(f"Exchange '{self.exchange_name}' not supported by CCXT")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to {self.exchange_name}: {str(e)}")
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from the exchange.

        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.exchange:
                self.is_connected = False
                logger.info(f"Disconnected from {self.exchange_name}")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from {self.exchange_name}: {str(e)}")
            return False

    def get_balance(self) -> Dict[str, Any]:
        """
        Fetch account balance from the exchange.

        Returns:
            Dict containing account balance information
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return {}

        try:
            balance = self.exchange.fetch_balance()
            logger.info(f"Fetched balance from {self.exchange_name}")
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return {}

    def get_currency_balance(self, currency: str = 'USDT', balance_type: str = 'free') -> float:
        """
        Get balance for a specific currency.

        Args:
            currency: Currency symbol (e.g., 'USDT', 'BTC')
            balance_type: Type of balance - 'free', 'used', or 'total'

        Returns:
            float: Balance amount for the specified currency, 0.0 if not found
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return 0.0

        try:
            balance = self.exchange.fetch_balance()
            
            # CCXT returns balance in format:
            # {
            #   'info': {...},
            #   'timestamp': ...,
            #   'datetime': ...,
            #   'free': {'USDT': 10000.0, ...},
            #   'used': {'USDT': 0.0, ...},
            #   'total': {'USDT': 10000.0, ...}
            # }
            
            if balance_type not in ['free', 'used', 'total']:
                logger.warning(f"Invalid balance_type '{balance_type}', using 'free'")
                balance_type = 'free'
            
            if balance_type in balance and isinstance(balance[balance_type], dict):
                currency_balance = balance[balance_type].get(currency, 0.0)
                logger.info(f"{currency} {balance_type} balance: {currency_balance}")
                return float(currency_balance)
            else:
                logger.warning(f"Could not find {balance_type} balance dict. Balance keys: {list(balance.keys())}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error fetching {currency} balance: {str(e)}")
            return 0.0

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get ticker information for a trading pair.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')

        Returns:
            Dict containing ticker data
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return {}

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.debug(f"Fetched ticker for {symbol}")
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            return {}

    def get_orderbook(self, symbol: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get order book for a trading pair.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            limit: Optional limit on number of orders to fetch

        Returns:
            Dict containing order book data
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return {}

        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            logger.debug(f"Fetched orderbook for {symbol}")
            return orderbook
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {str(e)}")
            return {}

    def place_order(self, symbol: str, order_type: str, side: str, amount: float,
                   price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place an order on the exchange.

        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            order_type: Type of order ('limit', 'market', etc.)
            side: Order side ('buy' or 'sell')
            amount: Amount to trade
            price: Price per unit (required for limit orders)

        Returns:
            Dict containing order information
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return {}

        try:
            order = self.exchange.create_order(symbol, order_type, side, amount, price)
            logger.info(f"Placed {side} {order_type} order for {symbol}")
            return order
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {}

    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an open order.

        Args:
            order_id: Order ID to cancel
            symbol: Trading pair symbol (required by some exchanges)

        Returns:
            Dict containing cancellation result
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return {}

        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Cancelled order {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return {}

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of open orders.

        Args:
            symbol: Optional symbol to filter orders

        Returns:
            List of open orders
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return []

        try:
            orders = self.exchange.fetch_open_orders(symbol)
            logger.debug(f"Fetched open orders")
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {str(e)}")
            return []

    def get_closed_orders(self, symbol: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get list of closed orders.

        Args:
            symbol: Optional symbol to filter orders
            limit: Optional limit on number of orders

        Returns:
            List of closed orders
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return []

        try:
            orders = self.exchange.fetch_closed_orders(symbol, limit=limit)
            logger.debug(f"Fetched closed orders")
            return orders
        except Exception as e:
            logger.error(f"Error fetching closed orders: {str(e)}")
            return []

    def get_supported_symbols(self) -> List[str]:
        """
        Get list of supported trading pairs.

        Returns:
            List of trading pair symbols
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return []

        try:
            symbols = self.exchange.symbols
            logger.debug(f"Fetched {len(symbols)} supported symbols")
            return symbols
        except Exception as e:
            logger.error(f"Error fetching supported symbols: {str(e)}")
            return []

    def get_markets(self) -> Dict[str, Any]:
        """
        Get market information for all trading pairs.

        Returns:
            Dict containing market information
        """
        if not self.is_connected or not self.exchange:
            logger.error("Not connected to exchange")
            return {}

        try:
            markets = self.exchange.fetch_markets()
            logger.debug(f"Fetched market information")
            return {market['symbol']: market for market in markets}
        except Exception as e:
            logger.error(f"Error fetching markets: {str(e)}")
            return {}


class ExchangeFactory:
    """
    Factory class for creating exchange manager instances.
    """

    _supported_exchanges = {
        'binance': CCXTExchangeManager,
        'coinbase': CCXTExchangeManager,
        'kraken': CCXTExchangeManager,
        'ftx': CCXTExchangeManager,
        'bybit': CCXTExchangeManager,
        'kucoin': CCXTExchangeManager,
    }

    @classmethod
    def create_exchange(cls, exchange_name: str, api_key: str, api_secret: str,
                       passphrase: Optional[str] = None, **kwargs) -> Optional[ExchangeManager]:
        """
        Create an exchange manager instance.

        Args:
            exchange_name: Name of the exchange
            api_key: API key
            api_secret: API secret
            passphrase: Optional passphrase
            **kwargs: Additional configuration options

        Returns:
            ExchangeManager instance or None if exchange not supported
        """
        if exchange_name.lower() not in cls._supported_exchanges:
            logger.error(f"Exchange '{exchange_name}' not supported")
            return None

        manager_class = cls._supported_exchanges[exchange_name.lower()]
        return manager_class(exchange_name, api_key, api_secret, passphrase, **kwargs)

    @classmethod
    def get_supported_exchanges(cls) -> List[str]:
        """
        Get list of supported exchanges.

        Returns:
            List of supported exchange names
        """
        return list(cls._supported_exchanges.keys())
