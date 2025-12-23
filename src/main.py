import asyncio
import logging
import signal
from typing import Dict
from src.config import load_config, get_redis_url
from src.data_fetcher import DataFetcher
from src.predictor import Predictor, HybridPredictor
from src.sentiment import SentimentAnalyzer
from src.risk_manager import RiskManager
from src.executor import Executor
from src.optimizer import Optimizer
from src.reporter import Reporter
from src.health_monitor import HealthMonitor
from metrics import Trade, MetricsTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bot.main')


async def start_services():
    cfg = load_config()
    redis_url = get_redis_url()

    health = HealthMonitor(cfg)
    await health.start()

    df = DataFetcher(cfg, redis_url)
    await df.start()

    sentiment = SentimentAnalyzer(cfg, redis_url)
    await sentiment.start()

    pred = Predictor(cfg, redis_url)
    await pred.start()

    opt = Optimizer(cfg, redis_url)
    await opt.start()

    risk = RiskManager(cfg, redis_url)
    await risk.start()

    exec_ = Executor(cfg, redis_url)
    await exec_.start()

    reporter = Reporter(cfg)
    await reporter.start()

    # Run until cancelled
    stop = asyncio.Event()

    def _signal(_signame):
        logger.info('Received stop signal: %s', _signame)
        stop.set()

    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda s=s: _signal(s))

    await stop.wait()

    # graceful shutdown
    await df.stop()
    await sentiment.stop()
    await pred.stop()
    await opt.stop()
    await risk.stop()
    await exec_.stop()
    await health.stop()


async def classic_trading_cycle(config: Dict):
    """
    Основной цикл классической торговли
    """
    logger.info("Запуск классического торгового цикла")
    
    # Инициализация компонентов
    predictor = HybridPredictor(config)
    executor = Executor(config)
    health = HealthMonitor(config)
    
    # Запуск мониторинга
    await health.start()
    
    cycle_count = 0
    max_cycles = config.get('max_cycles', 1000)
    
    try:
        while cycle_count < max_cycles:
            cycle_count += 1
            logger.info(f"Цикл #{cycle_count}")
            
            # 1. Получаем и анализируем сигналы
            signals = await predictor.predict_all()
            
            # Фильтруем сильные сигналы (уверенность > 0.6)
            strong_signals = [s for s in signals if s['confidence'] > 0.6]
            
            if strong_signals:
                logger.info(f"Найдено {len(strong_signals)} сильных сигналов")
                
                # 2. Исполняем сигналы
                executed = await executor.execute_classic_strategy(strong_signals)
                
                if executed:
                    logger.info(f"Исполнено {len(executed)} ордеров")
            
            # 3. Ждем перед следующим циклом (15 минут для 15m таймфрейма)
            wait_time = 900  # 15 минут в секундах
            logger.info(f"Ожидание {wait_time} секунд до следующего цикла...")
            await asyncio.sleep(wait_time)
            
            # 4. Проверяем здоровье системы
            if not await health.check_system_health():
                logger.error("Проблемы со здоровьем системы, приостановка")
                await asyncio.sleep(60)  # Ждем минуту и проверяем снова
                continue
            
    except KeyboardInterrupt:
        logger.info("Торговый цикл остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка в торговом цикле: {str(e)}")
    finally:
        # Безопасное завершение
        await executor.shutdown()
        await health.shutdown()
        logger.info("Классический торговый цикл завершен")


def main():
    """Main entry point for the trading bot"""
    asyncio.run(start_services())


if __name__ == '__main__':
    main()
