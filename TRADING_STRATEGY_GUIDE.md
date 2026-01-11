# Trading Strategy Guide

## Стратегии торговли

Бот поддерживает две торговые стратегии:

### 1. Simple Trend Strategy (Простая стратегия тренда)
- **Когда использовать:** Для стабильных рынков с чёткими трендами
- **Частота сделок:** Низкая (1-3 сделки в неделю)
- **Индикаторы:** Скользящие средние (MA10, MA30)
- **Риск:** Низкий

### 2. Enhanced Multi-Indicator Strategy (Расширенная мульти-индикаторная стратегия)
- **Когда использовать:** Для активной торговли с большим количеством сигналов
- **Частота сделок:** Высокая (5-15 сделок в день)
- **Индикаторы:** EMA, RSI, MACD, Bollinger Bands, Volume
- **Риск:** Средний

## Настройка в .env файле

### Выбор стратегии
```bash
# Простая стратегия
ACTIVE_STRATEGY=simple

# Расширенная стратегия (рекомендуется)
ACTIVE_STRATEGY=enhanced
```

### Настройка торговых пар

#### Вариант 1: Одна пара (консервативный подход)
```bash
DEFAULT_SYMBOL=BTCUSDT
TRADING_SYMBOLS=
```

#### Вариант 2: Топ-5 криптовалют (сбалансированный подход)
```bash
DEFAULT_SYMBOL=BTCUSDT
TRADING_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ADAUSDT
MAX_OPEN_POSITIONS=5
```

#### Вариант 3: Диверсифицированный портфель (агрессивный подход)
```bash
DEFAULT_SYMBOL=BTCUSDT
TRADING_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ADAUSDT,DOGEUSDT,XRPUSDT,DOTUSDT,LINKUSDT,MATICUSDT
MAX_OPEN_POSITIONS=10
MAX_DAILY_TRADES=30
```

## Рекомендуемые торговые пары

### Высокая ликвидность (рекомендуется для начинающих)
```
BTCUSDT   - Bitcoin
ETHUSDT   - Ethereum
BNBUSDT   - Binance Coin
SOLUSDT   - Solana
ADAUSDT   - Cardano
```

### Средняя ликвидность (для опытных трейдеров)
```
XRPUSDT   - Ripple
DOGEUSDT  - Dogecoin
DOTUSDT   - Polkadot
LINKUSDT  - Chainlink
MATICUSDT - Polygon
AVAXUSDT  - Avalanche
ATOMUSDT  - Cosmos
```

### Альткоины с высокой волатильностью (для агрессивной торговли)
```
SHIBUSDT  - Shiba Inu
PEPEUSDT  - Pepe
FLOKIUSDT - Floki
APTUSDT   - Aptos
ARBUSDT   - Arbitrum
```

## Enhanced Multi-Indicator Strategy - Условия входа

### Сигнал на покупку (BUY) генерируется при наборе ≥60 баллов из 100:

1. **EMA Alignment (25 баллов)**
   - EMA9 > EMA21 > EMA50 = 25 баллов (сильный тренд вверх)
   - EMA9 > EMA21 = 15 баллов (средний тренд)

2. **RSI Oversold (20 баллов)**
   - RSI < 30 = 20 баллов (перепроданность)
   - RSI < 40 = 10 баллов (близко к перепроданности)

3. **MACD Bullish Crossover (20 баллов)**
   - MACD > Signal и Histogram > 0 = 20 баллов
   - MACD > Signal = 10 баллов

4. **Bollinger Bands Bounce (15 баллов)**
   - Цена < Lower Band = 15 баллов (отскок от нижней границы)
   - Цена < Middle Band = 8 баллов

5. **Volume Confirmation (20 баллов)**
   - Объём > 1.5x средний = 20 баллов (сильное подтверждение)
   - Объём > средний = 10 баллов

### Сигнал на продажу (SELL) генерируется при наборе ≥60 баллов:

1. **EMA Alignment Bearish (25 баллов)**
   - EMA9 < EMA21 < EMA50 = 25 баллов
   - EMA9 < EMA21 = 15 баллов

2. **RSI Overbought (20 баллов)**
   - RSI > 70 = 20 баллов
   - RSI > 60 = 10 баллов

3. **MACD Bearish Crossover (20 баллов)**
   - MACD < Signal и Histogram < 0 = 20 баллов
   - MACD < Signal = 10 баллов

4. **Bollinger Bands Resistance (15 баллов)**
   - Цена > Upper Band = 15 баллов
   - Цена > Middle Band = 8 баллов

5. **Price Below EMAs (20 баллов)**
   - Цена < EMA9 = 20 баллов

## Настройка риск-менеджмента

### Для Enhanced Strategy (5+ сделок в день)
```bash
MAX_DAILY_TRADES=20
MAX_OPEN_POSITIONS=5
MAX_DAILY_LOSS_PERCENTAGE=3.0
POSITION_SIZE_PERCENTAGE=1.5
STOP_LOSS_PERCENTAGE=1.5
TAKE_PROFIT_PERCENTAGE=3.0
```

### Для Simple Strategy (консервативная торговля)
```bash
MAX_DAILY_TRADES=5
MAX_OPEN_POSITIONS=2
MAX_DAILY_LOSS_PERCENTAGE=2.0
POSITION_SIZE_PERCENTAGE=2.0
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0
```

## Применение изменений

После изменения настроек в `/etc/trading-bot/.env`:

```bash
# Обновите код
cd ~/trading-bot-setup/life_is_a_joke
git pull origin copilot/create-deployment-infrastructure-files
sudo cp src/strategies/enhanced_multi_indicator.py /opt/trading-bot/src/strategies/
sudo cp src/strategies/strategy_manager.py /opt/trading-bot/src/strategies/

# Перезапустите бота
sudo systemctl restart trading-bot

# Проверьте логи
sudo journalctl -u trading-bot -f
```

## Мониторинг торговли

### Проверка активных позиций
```bash
sudo sqlite3 /var/lib/trading-bot/trading_bot.db "
  SELECT symbol, side, entry_price, current_price, quantity, 
         ROUND((current_price - entry_price) / entry_price * 100, 2) as pnl_pct
  FROM positions 
  WHERE status = 'open';"
```

### Проверка истории сделок за сегодня
```bash
sudo sqlite3 /var/lib/trading-bot/trading_bot.db "
  SELECT symbol, side, price, quantity, 
         ROUND(profit_loss, 2) as pnl,
         strategy, timestamp
  FROM trades 
  WHERE DATE(timestamp) = DATE('now')
  ORDER BY timestamp DESC;"
```

### Статистика по символам
```bash
sudo sqlite3 /var/lib/trading-bot/trading_bot.db "
  SELECT symbol, 
         COUNT(*) as trades,
         ROUND(SUM(profit_loss), 2) as total_pnl,
         ROUND(AVG(profit_loss), 2) as avg_pnl
  FROM trades 
  WHERE DATE(timestamp) >= DATE('now', '-7 days')
  GROUP BY symbol
  ORDER BY total_pnl DESC;"
```

## Оптимизация для большего количества сделок

Если бот делает мало сделок даже с Enhanced Strategy:

1. **Снизьте минимальный порог входа:**
   ```python
   # В файле enhanced_multi_indicator.py измените:
   self.min_entry_score = 50  # было 60
   ```

2. **Увеличьте количество торговых пар:**
   ```bash
   TRADING_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ADAUSDT,XRPUSDT,DOGEUSDT,DOTUSDT,LINKUSDT,MATICUSDT
   ```

3. **Уменьшите таймфрейм (для более частых сигналов):**
   ```python
   # В методе _analyze_symbol замените:
   klines = self.get_klines(symbol, interval='5m', limit=200)  # было '15m'
   ```

4. **Увеличьте лимиты:**
   ```bash
   MAX_DAILY_TRADES=50
   MAX_OPEN_POSITIONS=10
   ```

## Предупреждения

⚠️ **ВАЖНО:**
- Тестируйте на TESTNET перед использованием реальных средств
- Начинайте с малых сумм и консервативных настроек
- Регулярно мониторьте логи и базу данных
- Используйте стоп-лоссы для защиты капитала
- Расширенная стратегия генерирует больше сделок = больше комиссий

## Поддержка

Если возникли вопросы по настройке стратегии, проверьте:
- `/var/log/trading-bot/trading-bot.log` - подробные логи
- `sudo journalctl -u trading-bot -f` - логи в реальном времени
- База данных SQLite для анализа истории торговли
