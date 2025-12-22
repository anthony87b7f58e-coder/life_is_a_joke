import asyncio
import logging
from typing import List, Dict, Optional
from src.utils import retry_async

logger = logging.getLogger('bot.executor')

class Executor:
    def __init__(self, cfg, redis_url=None):
        self.cfg = cfg
        self.redis_url = redis_url
        self.running = False

    async def start(self):
        self.running = True

    async def stop(self):
        self.running = False

    @retry_async(retries=3, delay=1)
    async def place_order(self, exchange_client, symbol, side, amount, price=None, params=None):
        # exchange_client expected to be ccxt instance or wrapper
        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, lambda: exchange_client.create_order(symbol, 'market' if price is None else 'limit', side, amount, price, params))
            return resp
        except Exception as e:
            logger.exception('Order failed: %s', e)
            raise
    
    async def execute_classic_strategy(self, signals: List[Dict]):
        """Execute trades based on classic strategy signals"""
        executed_orders = []
        
        for signal in signals:
            if signal['confidence'] < 0.5:  # Минимальный порог уверенности
                continue
                
            symbol = signal['symbol']
            action = signal['signal']
            
            # Проверяем, нет ли уже открытой позиции
            if await self.has_open_position(symbol):
                logger.info(f"Позиция {symbol} уже открыта, пропускаем")
                continue
            
            # Рассчитываем параметры ордера
            order_params = await self.prepare_classic_order(signal)
            
            if order_params:
                try:
                    # Выставляем ордер
                    if action == 'BUY':
                        order = await self.exchange.create_order(
                            symbol=symbol,
                            type='limit',
                            side='buy',
                            amount=order_params['amount'],
                            price=order_params['price']
                        )
                    else:  # SELL
                        order = await self.exchange.create_order(
                            symbol=symbol,
                            type='limit',
                            side='sell',
                            amount=order_params['amount'],
                            price=order_params['price']
                        )
                    
                    # Устанавливаем стоп-лосс и тейк-профит
                    await self.place_stop_loss_take_profit(order, signal)
                    
                    executed_orders.append(order)
                    logger.info(f"Исполнен {action} ордер для {symbol}: {order}")
                    
                except Exception as e:
                    logger.error(f"Ошибка исполнения ордера {symbol}: {str(e)}")
        
        return executed_orders
    
    async def prepare_classic_order(self, signal: Dict) -> Optional[Dict]:
        
        symbol = signal['symbol']
        action = signal['signal']
        position_size = signal.get('position_size', {})
        
        if not position_size or position_size['size'] <= 0:
            return None
        
        # Получаем текущие рыночные данные
        ticker = await self.exchange.fetch_ticker(symbol)
        
        # Определяем цену входа
        if action == 'BUY':
            # Для покупки берем цену ask (или чуть выше для быстрого исполнения)
            price = ticker['ask'] * 1.001  # +0.1% для быстрого исполнения
        else:
            # Для продажи берем цену bid
            price = ticker['bid'] * 0.999  # -0.1% для быстрого исполнения
        
        # Округляем количество согласно правилам биржи
        amount = await self.adjust_amount_to_exchange_rules(symbol, position_size['size'])
        
        # Минимальная проверка
        min_cost = 10  # Минимальная сумма ордера в USDT
        if amount * price < min_cost:
            logger.warning(f"Слишком маленький ордер для {symbol}: {amount * price:.2f} USDT")
            return None
        
        return {
            'amount': amount,
            'price': price,
            'symbol': symbol,
            'side': 'buy' if action == 'BUY' else 'sell'
        }
    
    async def place_stop_loss_take_profit(self, order: Dict, signal: Dict):
        
        symbol = signal['symbol']
        entry_price = order['price']
        action = order['side']
        
        # Параметры риск-менеджмента
        stop_loss_pct = 0.03  # 3% стоп-лосс
        take_profit_pct = 0.06  # 6% тейк-профит (риск/прибыль = 1:2)
        
        if action == 'buy':
            stop_price = entry_price * (1 - stop_loss_pct)
            take_profit_price = entry_price * (1 + take_profit_pct)
        else:  # sell
            stop_price = entry_price * (1 + stop_loss_pct)
            take_profit_price = entry_price * (1 - take_profit_pct)
        
        try:
            # Для фьючерсов можно использовать стоп-лосс ордер
            # Для спота нужно отслеживать вручную или использовать брекет-ордера
            if 'future' in symbol.lower():
                stop_order = await self.exchange.create_order(
                    symbol=symbol,
                    type='stop_market',
                    side='sell' if action == 'buy' else 'buy',
                    amount=order['amount'],
                    params={'stopPrice': stop_price}
                )
                logger.info(f"Установлен стоп-лосс для {symbol} на {stop_price}")
            
            # Логируем тейк-профит для ручного отслеживания
            logger.info(
                f"Тейк-профит для {symbol}: {take_profit_price:.2f} "
                f"(стоп: {stop_price:.2f}, вход: {entry_price:.2f})"
            )
            
        except Exception as e:
            logger.warning(f"Не удалось установить стоп-лосс для {symbol}: {str(e)}")

