# Руководство по настройке торговли на Bybit

Полное руководство по настройке и развертыванию торгового бота для работы с биржей Bybit.

## 🎯 О Bybit

**Bybit** - популярная криптовалютная биржа, специализирующаяся на деривативах и спотовой торговле.

**Преимущества:**
- ✅ Поддержка testnet для безопасного тестирования
- ✅ Низкие комиссии (Maker: 0.01%, Taker: 0.06%)
- ✅ Высокая ликвидность
- ✅ API с хорошей документацией
- ✅ Поддержка спот и фьючерсной торговли

---

## 📋 Предварительные требования

1. Аккаунт на Bybit (https://www.bybit.com/)
2. API ключи от Bybit (инструкция ниже)
3. Сервер с уже установленным ботом (см. INSTALLATION_GUIDE.md)
4. Python 3.8+ с установленным CCXT

---

## 🔑 Шаг 1: Создание API ключей на Bybit

### Для Testnet (рекомендуется для начала):

1. Зайдите на **Bybit Testnet**: https://testnet.bybit.com/
2. Зарегистрируйтесь или войдите
3. Получите тестовые средства (faucet)
4. Перейдите в **API Management** → **Create New Key**
5. Настройки ключа:
   - **Key Name**: `trading-bot-testnet`
   - **Permissions**: 
     - ✅ Read-Write (для торговли)
     - ❌ Withdrawal (НЕ включайте!)
   - **IP Restriction**: Добавьте IP вашего сервера (опционально)
6. Сохраните **API Key** и **Secret Key**

### Для Production (после тестирования):

1. Зайдите на **Bybit**: https://www.bybit.com/
2. Войдите в аккаунт
3. Перейдите в **Account** → **API Management**
4. Нажмите **Create New Key**
5. Пройдите верификацию (2FA)
6. Настройки ключа:
   - **Key Name**: `trading-bot-production`
   - **Permissions**:
     - ✅ Contract Trade (для фьючерсов)
     - ✅ Spot Trade (для спотовой торговли)
     - ❌ Withdrawal (НИКОГДА не включайте!)
   - **IP Whitelist**: Добавьте IP вашего сервера (рекомендуется)
7. Сохраните **API Key** и **Secret Key** в безопасном месте

---

## ⚙️ Шаг 2: Конфигурация бота для Bybit

### 2.1. Подключитесь к серверу

```bash
ssh root@YOUR_SERVER_IP
```

### 2.2. Остановите бота (если запущен)

```bash
sudo systemctl stop trading-bot
```

### 2.3. Отредактируйте конфигурацию

```bash
sudo nano /etc/trading-bot/.env
```

### 2.4. Настройте для Bybit Testnet (для начала)

```bash
# ============================================================================
# EXCHANGE CONFIGURATION
# ============================================================================
USE_CCXT=true
EXCHANGE_ID=bybit
EXCHANGE_API_KEY=ваш_bybit_api_key_здесь
EXCHANGE_API_SECRET=ваш_bybit_api_secret_здесь
EXCHANGE_TESTNET=true  # ВАЖНО: true для testnet!

# ============================================================================
# TRADING SETTINGS
# ============================================================================
TRADING_ENABLED=false  # Начните с мониторинга!
DEFAULT_SYMBOL=BTC/USDT
MAX_POSITION_SIZE=0.001  # Маленькая позиция для тестов
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0

# ============================================================================
# RISK MANAGEMENT
# ============================================================================
MAX_DAILY_TRADES=5
MAX_OPEN_POSITIONS=2
MAX_DAILY_LOSS_PERCENTAGE=3.0
POSITION_SIZE_PERCENTAGE=1.0  # 1% от капитала
```

Сохраните: `Ctrl+X`, затем `Y`, затем `Enter`

### 2.5. Проверьте права доступа

```bash
sudo chown tradingbot:tradingbot /etc/trading-bot/.env
sudo chmod 600 /etc/trading-bot/.env
```

---

## 🚀 Шаг 3: Установка/Обновление зависимостей

### 3.1. Перейдите в директорию бота

```bash
cd /opt/trading-bot
```

### 3.2. Обновите код (если установлено из git)

```bash
# Если установлено через git clone
cd ~/trading-bot-setup/life_is_a_joke
git pull origin copilot/create-deployment-infrastructure-files

# Скопируйте обновленные файлы
sudo cp -r src/* /opt/trading-bot/src/
sudo cp requirements.txt /opt/trading-bot/
```

### 3.3. Установите/обновите зависимости

```bash
# Активируйте virtual environment
source /opt/trading-bot/venv/bin/activate

# Обновите pip
pip install --upgrade pip

# Установите зависимости
pip install -r /opt/trading-bot/requirements.txt

# Деактивируйте
deactivate
```

### 3.4. Проверьте установку CCXT

```bash
/opt/trading-bot/venv/bin/python3 -c "import ccxt; print('CCXT version:', ccxt.__version__); print('Bybit supported:', 'bybit' in ccxt.exchanges)"
```

Ожидаемый вывод:
```
CCXT version: 4.2.x
Bybit supported: True
```

---

## 🧪 Шаг 4: Тестирование подключения к Bybit

### 4.1. Создайте тестовый скрипт

```bash
sudo nano /opt/trading-bot/test_bybit.py
```

Вставьте код:

```python
#!/usr/bin/env python3
"""Test Bybit connection"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv('/etc/trading-bot/.env')

# Add src to path
sys.path.insert(0, '/opt/trading-bot/src')

from core.config import Config
from core.exchange_adapter import ExchangeAdapter

def test_bybit():
    print("=" * 70)
    print("Testing Bybit Connection")
    print("=" * 70)
    
    # Load config
    config = Config()
    print(f"Exchange ID: {config.exchange_id}")
    print(f"Use CCXT: {config.use_ccxt}")
    print(f"Testnet: {config.exchange_testnet}")
    print()
    
    # Initialize exchange
    try:
        exchange = ExchangeAdapter(config)
        print("✓ Exchange adapter initialized")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False
    
    # Test connection
    try:
        exchange.ping()
        print("✓ Connection successful")
    except Exception as e:
        print(f"✗ Ping failed: {e}")
        return False
    
    # Get account info
    try:
        account = exchange.get_account()
        print("✓ Account info retrieved")
        print(f"  Balances found: {len(account.get('balances', []))}")
    except Exception as e:
        print(f"✗ Failed to get account: {e}")
        return False
    
    # Get ticker
    try:
        ticker = exchange.get_symbol_ticker(config.default_symbol)
        print(f"✓ Ticker for {config.default_symbol}: {ticker['price']}")
    except Exception as e:
        print(f"✗ Failed to get ticker: {e}")
        return False
    
    # Get markets
    try:
        info = exchange.get_exchange_info()
        symbols = info.get('symbols', [])
        print(f"✓ Exchange info: {len(symbols)} trading pairs available")
    except Exception as e:
        print(f"✗ Failed to get exchange info: {e}")
        return False
    
    print()
    print("=" * 70)
    print("All tests PASSED! Bybit is ready to use.")
    print("=" * 70)
    return True

if __name__ == '__main__':
    success = test_bybit()
    sys.exit(0 if success else 1)
```

Сохраните: `Ctrl+X`, `Y`, `Enter`

### 4.2. Запустите тест

```bash
sudo /opt/trading-bot/venv/bin/python3 /opt/trading-bot/test_bybit.py
```

**Ожидаемый результат:**
```
======================================================================
Testing Bybit Connection
======================================================================
Exchange ID: bybit
Use CCXT: True
Testnet: True

✓ Exchange adapter initialized
✓ Connection successful
✓ Account info retrieved
  Balances found: 5
✓ Ticker for BTC/USDT: 45000.50
✓ Exchange info: 200 trading pairs available

======================================================================
All tests PASSED! Bybit is ready to use.
======================================================================
```

Если тест не прошел, проверьте:
- API ключи правильные
- Testnet режим включен (если используете testnet ключи)
- Файрвол не блокирует подключение к Bybit

---

## 🎮 Шаг 5: Запуск бота в режиме мониторинга

### 5.1. Запустите бота

```bash
sudo systemctl start trading-bot
```

### 5.2. Проверьте статус

```bash
sudo systemctl status trading-bot
```

### 5.3. Смотрите логи в реальном времени

```bash
sudo journalctl -u trading-bot -f
```

**Что вы должны увидеть:**
```
Trading Bot - Starting
Exchange: bybit
Mode: CCXT
Trading enabled: False
Default symbol: BTC/USDT
Connected to bybit TESTNET (CCXT)
Account status: Can trade: True
TRADING BOT STARTED
Trading disabled, running in monitoring mode only
```

### 5.4. Остановите просмотр логов

Нажмите `Ctrl+C`

---

## 📊 Шаг 6: Включение торговли (после тестирования мониторинга)

### 6.1. Убедитесь, что мониторинг работает стабильно (минимум 24 часа)

### 6.2. Остановите бота

```bash
sudo systemctl stop trading-bot
```

### 6.3. Включите торговлю на testnet

```bash
sudo nano /etc/trading-bot/.env
```

Измените:
```bash
TRADING_ENABLED=true  # Включить торговлю
EXCHANGE_TESTNET=true  # Оставить testnet!
```

### 6.4. Перезапустите бота

```bash
sudo systemctl start trading-bot
sudo journalctl -u trading-bot -f
```

Теперь бот будет реально торговать на Bybit Testnet с виртуальными деньгами.

---

## 🔴 Шаг 7: Переход на Production (только после успешных тестов!)

### ⚠️ ВАЖНО: Делайте это ТОЛЬКО после:
- Минимум 1 недели успешной торговли на testnet
- Проверки всех сценариев (вход, выход, stop-loss, take-profit)
- Уверенности в стратегии

### 7.1. Создайте production API ключи на Bybit

См. инструкции выше для production.

### 7.2. Остановите бота

```bash
sudo systemctl stop trading-bot
```

### 7.3. Создайте бэкап конфигурации

```bash
sudo cp /etc/trading-bot/.env /etc/trading-bot/.env.testnet.backup
```

### 7.4. Обновите конфигурацию для production

```bash
sudo nano /etc/trading-bot/.env
```

Измените:
```bash
# Production API ключи
EXCHANGE_API_KEY=ваш_PRODUCTION_bybit_api_key
EXCHANGE_API_SECRET=ваш_PRODUCTION_bybit_api_secret
EXCHANGE_TESTNET=false  # FALSE для production!

# Начните с консервативных настроек!
TRADING_ENABLED=true
MAX_POSITION_SIZE=0.001  # ОЧЕНЬ маленькая позиция для начала!
POSITION_SIZE_PERCENTAGE=0.5  # 0.5% вместо 2%
MAX_DAILY_TRADES=3  # Ограничьте кол-во сделок
MAX_OPEN_POSITIONS=1  # Только 1 позиция одновременно
```

### 7.5. Запустите и мониторьте ПОСТОЯННО

```bash
sudo systemctl start trading-bot
sudo journalctl -u trading-bot -f
```

**КРИТИЧЕСКИ ВАЖНО:**
- Следите за логами первые несколько часов
- Проверяйте каждую сделку
- Имейте план остановки при проблемах

---

## 🔍 Особенности торговли на Bybit

### Торговые пары

Bybit использует формат: `BASE/QUOTE`

**Популярные пары:**
- `BTC/USDT` - Bitcoin/Tether
- `ETH/USDT` - Ethereum/Tether
- `SOL/USDT` - Solana/Tether
- `XRP/USDT` - Ripple/Tether

### Минимальные размеры ордеров

Каждая пара имеет свои минимумы. Для BTC/USDT:
- Минимальный ордер: ~0.0001 BTC
- Минимальная стоимость: ~5-10 USDT

### Комиссии

- **Spot Trading (спот)**:
  - Maker: 0.1%
  - Taker: 0.1%
- **Derivatives (деривативы)**:
  - Maker: 0.01%
  - Taker: 0.06%

### Типы ордеров

Бот использует:
- **Market** - исполняется немедленно по текущей цене
- **Limit** - исполняется по указанной цене или лучше

---

## 🛠️ Устранение неполадок

### Проблема: "Invalid API credentials"

**Решение:**
```bash
# Проверьте ключи
sudo grep EXCHANGE_API /etc/trading-bot/.env

# Убедитесь, что используете правильные ключи:
# Testnet ключи - для testnet.bybit.com
# Production ключи - для www.bybit.com
```

### Проблема: "Symbol not found: BTC/USDT"

**Решение:**
```bash
# Проверьте доступные символы через Python
/opt/trading-bot/venv/bin/python3 << EOF
import ccxt
exchange = ccxt.bybit({'enableRateLimit': True})
exchange.load_markets()
btc_pairs = [s for s in exchange.symbols if 'BTC' in s]
print(btc_pairs[:10])
EOF
```

### Проблема: "Insufficient balance"

**Решение для testnet:**
1. Зайдите на https://testnet.bybit.com/
2. Используйте faucet для получения тестовых средств
3. Пополните USDT баланс

**Решение для production:**
1. Внесите депозит на Bybit
2. Убедитесь, что средства на Spot аккаунте (не Derivatives)

### Проблема: "Order size too small"

**Решение:**
```bash
# Увеличьте размер позиции в .env
MAX_POSITION_SIZE=0.001  # Увеличьте это значение
```

### Проблема: "Rate limit exceeded"

**Решение:**
- CCXT автоматически управляет rate limits
- Увеличьте интервал проверки в bot.py: `time.sleep(60)` → `time.sleep(120)`

---

## 📈 Мониторинг торговли на Bybit

### Проверка баланса

```bash
/opt/trading-bot/venv/bin/python3 << EOF
import sys
sys.path.insert(0, '/opt/trading-bot/src')
from dotenv import load_dotenv
load_dotenv('/etc/trading-bot/.env')
from core.config import Config
from core.exchange_adapter import ExchangeAdapter

config = Config()
exchange = ExchangeAdapter(config)
account = exchange.get_account()

for balance in account.get('balances', []):
    free = float(balance.get('free', 0))
    locked = float(balance.get('locked', 0))
    if free > 0 or locked > 0:
        print(f"{balance['asset']}: Free={free}, Locked={locked}")
EOF
```

### Просмотр открытых позиций

```bash
sudo sqlite3 /var/lib/trading-bot/trading_bot.db "SELECT * FROM positions WHERE status='open';"
```

### Просмотр последних сделок

```bash
sudo sqlite3 /var/lib/trading-bot/trading_bot.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🔄 Обновление бота на сервере

Если вышла новая версия кода:

### Шаг 1: Остановите бота

```bash
sudo systemctl stop trading-bot
```

### Шаг 2: Создайте бэкап

```bash
sudo bash /opt/trading-bot/deployment/scripts/backup.sh
```

### Шаг 3: Обновите код

```bash
cd ~/trading-bot-setup/life_is_a_joke
git pull origin copilot/create-deployment-infrastructure-files
```

### Шаг 4: Скопируйте обновленные файлы

```bash
sudo cp -r src/* /opt/trading-bot/src/
sudo cp requirements.txt /opt/trading-bot/
sudo cp BYBIT_SETUP_GUIDE.md /opt/trading-bot/
```

### Шаг 5: Обновите зависимости

```bash
sudo /opt/trading-bot/venv/bin/pip install -r /opt/trading-bot/requirements.txt --upgrade
```

### Шаг 6: Перезапустите бота

```bash
sudo systemctl start trading-bot
sudo journalctl -u trading-bot -f
```

---

## 📚 Полезные ссылки

- **Bybit Official**: https://www.bybit.com/
- **Bybit Testnet**: https://testnet.bybit.com/
- **Bybit API Docs**: https://bybit-exchange.github.io/docs/v5/intro
- **CCXT Bybit**: https://docs.ccxt.com/#/exchanges/bybit
- **Bybit Trading Fees**: https://www.bybit.com/en-US/help-center/article/Trading-Fee-Structure

---

## ⚠️ Важные напоминания

1. **ВСЕГДА начинайте с testnet**
2. **НИКОГДА не давайте API ключам права на вывод средств**
3. **Начинайте с минимальных размеров позиций**
4. **Мониторьте логи постоянно первые дни**
5. **Имейте план выхода при убытках**
6. **Торговля криптовалютами - высокий риск**
7. **Не инвестируйте больше, чем можете потерять**

---

## ✅ Контрольный список для запуска на Bybit

- [ ] Создан аккаунт на Bybit Testnet
- [ ] Получены testnet API ключи
- [ ] Получены тестовые средства (faucet)
- [ ] Установлен/обновлен CCXT на сервере
- [ ] Обновлен файл .env для Bybit testnet
- [ ] Тест подключения прошел успешно
- [ ] Бот запущен в режиме мониторинга (24+ часов)
- [ ] Логи проверены, ошибок нет
- [ ] Включена торговля на testnet
- [ ] Протестированы различные сценарии
- [ ] Созданы production API ключи (после тестов)
- [ ] Конфигурация обновлена для production
- [ ] Установлены консервативные лимиты
- [ ] Настроены автоматические бэкапы
- [ ] Готов план мониторинга и действий при проблемах

---

**Удачной торговли на Bybit! 🚀**
