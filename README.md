# Life is a Joke - Terminal Pager Help

## Русский (Russian)

### Что значит "lines 1-21/21 (END)"?

Эта надпись появляется, когда вы просматриваете файл с помощью программ `less` или `more` в терминале Linux/Unix.

**Объяснение:**
- **lines 1-21** — означает, что на экране отображаются строки с 1 по 21
- **/21** — общее количество строк в файле (файл содержит 21 строку)
- **(END)** — вы находитесь в конце файла, больше строк нет

**Команды для управления просмотром:**
- `q` — выйти из программы просмотра
- `Пробел` или `Page Down` — прокрутить вниз на одну страницу
- `b` или `Page Up` — прокрутить вверх на одну страницу
- `↑` (стрелка вверх) — на одну строку вверх
- `↓` (стрелка вниз) — на одну строку вниз
- `g` — перейти к началу файла
- `G` — перейти к концу файла
- `/` — поиск (введите текст и нажмите Enter)
- `n` — следующее совпадение при поиске
- `h` — показать справку

**Другие варианты сообщений:**
- `lines 1-21/50` — вы видите строки 1-21 из 50 (есть еще строки ниже)
- `lines 10-30/50 (50%)` — строки 10-30 из 50, вы на 50% файла
- `:` — приглашение для ввода команды

**Чтобы выйти:** просто нажмите клавишу `q`

---

## English

### What does "lines 1-21/21 (END)" mean?

This message appears when you're viewing a file using `less` or `more` pager programs in a Linux/Unix terminal.

**Explanation:**
- **lines 1-21** — means you're viewing lines 1 through 21 on your screen
- **/21** — total number of lines in the file (the file has 21 lines)
- **(END)** — you're at the end of the file, there are no more lines

**Commands for navigation:**
- `q` — quit the viewer
- `Space` or `Page Down` — scroll down one page
- `b` or `Page Up` — scroll up one page
- `↑` (up arrow) — move up one line
- `↓` (down arrow) — move down one line
- `g` — go to the beginning of the file
- `G` — go to the end of the file
- `/` — search (type text and press Enter)
- `n` — next search match
- `h` — show help

**Other message variations:**
- `lines 1-21/50` — you're viewing lines 1-21 out of 50 (more lines below)
- `lines 10-30/50 (50%)` — lines 10-30 out of 50, you're at 50% of the file
- `:` — command prompt

**To exit:** simply press the `q` key

---

## About This Project

This repository contains a cryptocurrency exchange management module that provides integration with the CCXT library for managing cryptocurrency exchange connections and operations.

### Project Structure

```
life_is_a_joke/
└── src/
    └── core/
        └── exchange_manager.py  # CCXT-based exchange manager implementation
```

### Features

- Abstract base class for exchange operations
- CCXT integration for multiple cryptocurrency exchanges
- Support for major exchanges: Binance, Coinbase, Kraken, FTX, Bybit, KuCoin
- Comprehensive trading operations: balance checking, ticker data, order placement, order management
- Factory pattern for easy exchange instantiation

### Usage

```python
from src.core.exchange_manager import ExchangeFactory

# Create an exchange manager
exchange = ExchangeFactory.create_exchange(
    exchange_name='binance',
    api_key='your_api_key',
    api_secret='your_api_secret'
)

# Connect and use
if exchange.connect():
    balance = exchange.get_balance()
    ticker = exchange.get_ticker('BTC/USDT')
    # ... perform operations
    exchange.disconnect()
```

---

## Справка по проекту (Project Reference)

Этот репозиторий содержит модуль управления криптовалютными биржами с интеграцией библиотеки CCXT.
