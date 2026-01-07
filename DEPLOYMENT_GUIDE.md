# Полное руководство по развертыванию
## Crypto Trading Bot - Production Deployment Guide

**Версия:** 2.0  
**Дата:** 23 декабря 2024  
**Статус:** Production-Ready Deployment Package

---

## 📋 Содержание

1. [Требования к серверу](#требования-к-серверу)
2. [Предварительная подготовка](#предварительная-подготовка)
3. [Установка на сервер](#установка-на-сервер)
4. [Настройка API ключей](#настройка-api-ключей)
5. [Настройка сервисов](#настройка-сервисов)
6. [Мониторинг и логирование](#мониторинг-и-логирование)
7. [Резервное копирование](#резервное-копирование)
8. [Обслуживание](#обслуживание)
9. [Устранение неполадок](#устранение-неполадок)

---

## 🖥️ Требования к серверу

### Минимальные требования

- **ОС:** Ubuntu 22.04 LTS или новее
- **CPU:** 2 ядра
- **RAM:** 4 GB
- **Диск:** 20 GB SSD
- **Сеть:** 10 Mbps постоянное соединение

### Рекомендуемые требования

- **ОС:** Ubuntu 22.04 LTS
- **CPU:** 4 ядра
- **RAM:** 8 GB
- **Диск:** 50 GB NVMe SSD
- **Сеть:** 100 Mbps постоянное соединение с низкой задержкой

### Выбор хостинга

**Рекомендуемые провайдеры:**
- DigitalOcean (от $24/месяц)
- Hetzner Cloud (от €15/месяц)
- Vultr (от $24/месяц)
- AWS EC2 (t3.medium, от $30/месяц)

**Критерии выбора:**
- Низкая задержка до бирж (< 50ms желательно)
- 99.9% uptime гарантия
- Возможность snapshot/backup
- Firewall и DDoS защита

---

## 🔧 Предварительная подготовка

### 1. Получение API ключей

#### Binance Testnet (для тестирования)

1. Перейдите на https://testnet.binance.vision/
2. Войдите через GitHub
3. Сгенерируйте API ключи
4. **Permissions:** Только SPOT Trading (БЕЗ Withdrawal!)
5. Сохраните ключи в безопасном месте

#### Binance Production (только после тестирования!)

1. Зарегистрируйтесь на binance.com
2. Пройдите KYC верификацию
3. Настройте 2FA (обязательно!)
4. API Management → Create API Key
5. **Permissions:** ТОЛЬКО Enable Spot & Margin Trading
6. **IP Whitelist:** Добавьте IP вашего сервера
7. **ВАЖНО:** НИКОГДА не включайте Withdrawal permission!

### 2. Домен и SSL (опционально, но рекомендуется)

```bash
# Если нужен мониторинг через веб
# 1. Зарегистрируйте домен (например: trading-bot.your-domain.com)
# 2. Установите Let's Encrypt для SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d trading-bot.your-domain.com
```

### 3. Telegram Bot (для уведомлений)

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям, сохраните токен
4. Найдите @userinfobot, узнайте свой chat_id
5. Сохраните оба значения для .env файла

---

## 🚀 Установка на сервер

### Метод 1: Автоматическая установка (Рекомендуется)

```bash
# 1. Подключитесь к серверу
ssh root@your-server-ip

# 2. Скачайте проект
cd /tmp
git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
cd life_is_a_joke

# 3. Запустите скрипт установки
chmod +x deployment/deploy.sh
sudo ./deployment/deploy.sh

# Скрипт автоматически:
# - Обновит систему
# - Установит зависимости (Python, PostgreSQL, Redis, Nginx)
# - Создаст пользователя tradingbot
# - Настроит базу данных
# - Установит Python пакеты
# - Настроит systemd service
```

### Метод 2: Ручная установка

<details>
<summary>Развернуть пошаговую установку</summary>

```bash
# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка зависимостей
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    git \
    build-essential \
    libpq-dev

# 3. Создание пользователя
sudo useradd -r -s /bin/bash -d /opt/trading-bot -m tradingbot

# 4. Создание директорий
sudo mkdir -p /opt/trading-bot
sudo mkdir -p /var/log/trading-bot
sudo mkdir -p /var/lib/trading-bot/backups

# 5. Копирование проекта
sudo cp -r . /opt/trading-bot/
cd /opt/trading-bot

# 6. Настройка прав
sudo chown -R tradingbot:tradingbot /opt/trading-bot
sudo chown -R tradingbot:tradingbot /var/log/trading-bot
sudo chown -R tradingbot:tradingbot /var/lib/trading-bot

# 7. Настройка PostgreSQL
sudo -u postgres psql << EOF
CREATE USER trading_bot_user WITH PASSWORD 'secure_password_here';
CREATE DATABASE trading_bot OWNER trading_bot_user;
GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trading_bot_user;
\q
EOF

# 8. Установка Python пакетов
sudo -u tradingbot python3.11 -m venv venv
sudo -u tradingbot ./venv/bin/pip install --upgrade pip
sudo -u tradingbot ./venv/bin/pip install -r requirements.txt

# 9. Настройка systemd
sudo cp deployment/systemd/trading-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trading-bot

# 10. Настройка Nginx (опционально)
sudo cp deployment/nginx/trading-bot.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/trading-bot.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

</details>

---

## 🔑 Настройка API ключей

### 1. Создание .env файла

```bash
# Перейдите в директорию проекта
cd /opt/trading-bot

# Запустите скрипт настройки окружения
sudo -u tradingbot python3 scripts/setup_environment.py

# Откройте .env для редактирования
sudo nano .env
```

### 2. Заполнение обязательных параметров

```bash
# =============================================================================
# КРИТИЧЕСКИ ВАЖНЫЕ ПАРАМЕТРЫ (обязательно заполнить!)
# =============================================================================

# Режим работы (ОБЯЗАТЕЛЬНО установить правильно!)
ENVIRONMENT=paper  # paper - для testnet, production - для реальной торговли

# Binance Testnet API (для начала используйте testnet!)
BINANCE_API_KEY=ваш_testnet_api_key_здесь
BINANCE_API_SECRET=ваш_testnet_secret_здесь

# База данных PostgreSQL
POSTGRES_PASSWORD=придумайте_надежный_пароль

# Секретный ключ (сгенерируйте новый!)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# =============================================================================
# ОПЦИОНАЛЬНЫЕ (но рекомендуемые)
# =============================================================================

# Telegram уведомления
TELEGRAM_TOKEN=ваш_telegram_bot_token
TELEGRAM_CHAT_ID=ваш_chat_id

# Email уведомления
SMTP_USERNAME=ваш_email@gmail.com
SMTP_PASSWORD=app_specific_password
SMTP_TO_EMAILS=admin@yourdomain.com
```

### 3. Генерация секретных ключей

```bash
# Сгенерировать SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Сгенерировать JWT_SECRET_KEY
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

# Добавьте сгенерированные ключи в .env файл
```

### 4. Проверка конфигурации

```bash
# Запустите проверку окружения
sudo -u tradingbot ./venv/bin/python scripts/health_check.py

# Должны пройти все 5 тестов:
# ✓ Dependencies
# ✓ Configuration
# ✓ Data Fetcher
# ✓ Trading Strategy
# ✓ Sentiment Analyzer
```

---

## ⚙️ Настройка сервисов

### 1. PostgreSQL

```bash
# Оптимизация для торгового бота
sudo nano /etc/postgresql/14/main/postgresql.conf

# Рекомендуемые настройки:
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Перезапуск PostgreSQL
sudo systemctl restart postgresql
```

### 2. Redis

```bash
# Настройка Redis
sudo nano /etc/redis/redis.conf

# Рекомендуемые настройки:
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Перезапуск Redis
sudo systemctl restart redis-server
```

### 3. Systemd Service

```bash
# Просмотр статуса
sudo systemctl status trading-bot

# Запуск
sudo systemctl start trading-bot

# Остановка
sudo systemctl stop trading-bot

# Перезапуск
sudo systemctl restart trading-bot

# Автозагрузка при старте системы
sudo systemctl enable trading-bot

# Просмотр логов
sudo journalctl -u trading-bot -f
```

### 4. Nginx (если используется)

```bash
# Создание пароля для защиты metrics
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Тест конфигурации
sudo nginx -t

# Перезагрузка
sudo systemctl reload nginx

# Проверка доступности
curl https://your-domain.com/health
```

---

## 📊 Мониторинг и логирование

### 1. Просмотр логов

```bash
# Логи systemd (реального времени)
sudo journalctl -u trading-bot -f

# Логи systemd (последние 100 строк)
sudo journalctl -u trading-bot -n 100

# Логи приложения
tail -f /var/log/trading-bot/bot.log

# Логи Nginx
tail -f /var/log/nginx/trading-bot-access.log
tail -f /var/log/nginx/trading-bot-error.log
```

### 2. Prometheus Metrics

```bash
# Проверка метрик
curl http://localhost:8001/metrics

# Если настроен Nginx с доменом
curl https://your-domain.com/metrics
```

### 3. Health Check

```bash
# Запуск проверки здоровья
cd /opt/trading-bot
sudo -u tradingbot ./venv/bin/python scripts/health_check.py

# Результат должен быть:
# Total: 5/5 checks passed
# ✓ All systems operational!
```

### 4. Мониторинг ресурсов

```bash
# CPU и память
htop

# Дисковое пространство
df -h

# Использование Redis
redis-cli info memory

# Активные подключения PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Размер базы данных
sudo -u postgres psql -c "\l+ trading_bot"
```

---

## 💾 Резервное копирование

### 1. Ручное резервное копирование

```bash
# Полное резервное копирование (с логами)
cd /opt/trading-bot
sudo deployment/scripts/backup.sh --full

# Обычное резервное копирование (без логов)
sudo deployment/scripts/backup.sh

# Только конфигурация
sudo deployment/scripts/backup.sh --config-only

# Резервные копии сохраняются в:
# /var/lib/trading-bot/backups/
```

### 2. Автоматическое резервное копирование

```bash
# Добавить в crontab
sudo crontab -e

# Ежедневное резервное копирование в 3:00 утра
0 3 * * * /opt/trading-bot/deployment/scripts/backup.sh

# Еженедельное полное резервное копирование (воскресенье 2:00)
0 2 * * 0 /opt/trading-bot/deployment/scripts/backup.sh --full
```

### 3. Восстановление из резервной копии

```bash
# Просмотр доступных резервных копий
ls -lh /var/lib/trading-bot/backups/

# Восстановление из резервной копии
sudo deployment/scripts/restore.sh /var/lib/trading-bot/backups/trading-bot-backup-20241223_030000.tar.gz

# Скрипт автоматически:
# 1. Остановит сервис
# 2. Восстановит базу данных
# 3. Восстановит конфигурацию
# 4. Восстановит данные
```

### 4. Резервное копирование в облако

```bash
# Установка rclone для облачного хранения
curl https://rclone.org/install.sh | sudo bash

# Настройка (например, для Google Drive)
rclone config

# Синхронизация резервных копий
rclone sync /var/lib/trading-bot/backups/ remote:trading-bot-backups/

# Автоматизация через cron (ежедневно после локального backup)
0 4 * * * rclone sync /var/lib/trading-bot/backups/ remote:trading-bot-backups/
```

---

## 🔧 Обслуживание

### Ежедневные задачи

```bash
# 1. Проверка статуса сервиса
sudo systemctl status trading-bot

# 2. Просмотр последних логов
sudo journalctl -u trading-bot --since "1 hour ago"

# 3. Проверка метрик
curl http://localhost:8001/metrics | grep -E "(trades|pnl|errors)"

# 4. Проверка дискового пространства
df -h /var/lib/trading-bot
```

### Еженедельные задачи

```bash
# 1. Запуск полной проверки здоровья
cd /opt/trading-bot
sudo -u tradingbot ./venv/bin/python scripts/health_check.py

# 2. Проверка резервных копий
ls -lh /var/lib/trading-bot/backups/

# 3. Очистка старых логов (если нужно)
sudo journalctl --vacuum-time=7d

# 4. Обновление системных пакетов
sudo apt update && sudo apt upgrade -y
```

### Ежемесячные задачи

```bash
# 1. Проверка обновлений проекта
cd /opt/trading-bot
git fetch origin
git log HEAD..origin/main --oneline

# 2. Анализ производительности базы данных
sudo -u postgres psql trading_bot -c "SELECT * FROM pg_stat_user_tables;"

# 3. Тест восстановления из резервной копии (на тестовом сервере!)

# 4. Ревизия настроек безопасности
sudo fail2ban-client status
sudo ufw status verbose
```

---

## 🔍 Устранение неполадок

### Проблема: Сервис не запускается

```bash
# 1. Проверьте статус
sudo systemctl status trading-bot

# 2. Проверьте логи
sudo journalctl -u trading-bot -n 50

# 3. Проверьте конфигурацию
cd /opt/trading-bot
sudo -u tradingbot ./venv/bin/python -c "from src.config import load_config; load_config()"

# 4. Проверьте права на файлы
ls -la /opt/trading-bot/.env
# Должно быть: -rw------- 1 tradingbot tradingbot

# 5. Ручной запуск для диагностики
cd /opt/trading-bot
sudo -u tradingbot ./venv/bin/python -m src.main
```

### Проблема: Ошибки подключения к бирже

```bash
# 1. Проверьте API ключи
grep BINANCE_API_KEY /opt/trading-bot/.env

# 2. Тест подключения
cd /opt/trading-bot
sudo -u tradingbot ./venv/bin/python scripts/test_connectivity.py

# 3. Проверьте сетевое соединение
ping -c 3 testnet.binance.vision
curl -I https://testnet.binance.vision/api/v3/ping

# 4. Проверьте лимиты rate limit
# Посмотрите на ошибки 429 в логах
```

### Проблема: База данных недоступна

```bash
# 1. Проверьте статус PostgreSQL
sudo systemctl status postgresql

# 2. Проверьте подключение
sudo -u postgres psql -c "\l"

# 3. Проверьте права пользователя
sudo -u postgres psql -c "\du"

# 4. Тест подключения от имени бота
sudo -u tradingbot psql -h localhost -U trading_bot_user -d trading_bot -c "SELECT version();"
```

### Проблема: Высокое использование памяти

```bash
# 1. Проверьте использование памяти
free -h
ps aux --sort=-%mem | head -n 10

# 2. Проверьте Redis
redis-cli info memory

# 3. Ограничьте память для сервиса
sudo nano /etc/systemd/system/trading-bot.service
# Добавьте:
# MemoryLimit=1G
# MemoryMax=1.5G

sudo systemctl daemon-reload
sudo systemctl restart trading-bot
```

### Проблема: Логи занимают много места

```bash
# 1. Проверьте размер логов
du -sh /var/log/trading-bot/
du -sh /var/log/journal/

# 2. Очистите старые логи journald
sudo journalctl --vacuum-size=100M
sudo journalctl --vacuum-time=7d

# 3. Настройте ротацию логов
sudo nano /etc/logrotate.d/trading-bot
# Добавьте:
/var/log/trading-bot/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 tradingbot tradingbot
}
```

---

## 🔐 Безопасность

### Базовые меры безопасности

```bash
# 1. Настройка firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# 2. Установка fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 3. SSH ключи вместо пароля
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-copy-id root@your-server-ip

# 4. Отключение root SSH
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
sudo systemctl restart sshd

# 5. Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

### Защита API ключей

```bash
# 1. Права только для пользователя
chmod 600 /opt/trading-bot/.env
chown tradingbot:tradingbot /opt/trading-bot/.env

# 2. Никогда не коммитить в git
echo ".env" >> /opt/trading-bot/.gitignore

# 3. IP Whitelist на Binance
# Добавьте IP сервера в настройках API на binance.com

# 4. Минимальные права API ключа
# НИКОГДА не включайте Withdrawal permission!
```

---

## 📞 Поддержка и мониторинг

### Настройка уведомлений

#### Telegram

```bash
# В .env файле:
TELEGRAM_TOKEN=ваш_bot_token
TELEGRAM_CHAT_ID=ваш_chat_id

# Тест отправки сообщения:
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
     -d "chat_id=${TELEGRAM_CHAT_ID}" \
     -d "text=Trading bot deployed successfully!"
```

#### Email

```bash
# В .env файле:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=app_specific_password
SMTP_TO_EMAILS=admin@yourdomain.com

# Для Gmail: https://myaccount.google.com/apppasswords
```

---

## ✅ Чек-лист успешного развертывания

### Перед запуском

- [ ] Сервер с Ubuntu 22.04 LTS настроен
- [ ] Все зависимости установлены (PostgreSQL, Redis, Python)
- [ ] API ключи Binance Testnet получены
- [ ] .env файл заполнен и защищен (chmod 600)
- [ ] Секретные ключи сгенерированы
- [ ] PostgreSQL база данных создана
- [ ] Redis запущен
- [ ] Health check проходит успешно (5/5)
- [ ] Firewall настроен
- [ ] SSL сертификат установлен (если используется домен)

### После запуска

- [ ] Сервис trading-bot запущен (systemctl status trading-bot)
- [ ] Логи показывают нормальную работу (journalctl -u trading-bot -f)
- [ ] Metrics доступны (curl http://localhost:8001/metrics)
- [ ] Подключение к бирже работает (scripts/test_connectivity.py)
- [ ] Резервное копирование настроено (crontab)
- [ ] Мониторинг настроен (Prometheus/Grafana)
- [ ] Уведомления работают (Telegram/Email)
- [ ] Документация изучена

### Безопасность

- [ ] API ключи имеют минимальные права (БЕЗ Withdrawal!)
- [ ] IP Whitelist настроен на Binance
- [ ] Firewall активен (ufw status)
- [ ] SSH только по ключам
- [ ] fail2ban установлен и настроен
- [ ] Автоматические обновления безопасности включены
- [ ] .env файл НЕ в git (проверить .gitignore)
- [ ] Сильные пароли для всех сервисов

---

## 📚 Дополнительные ресурсы

### Документация проекта
- README.md - Общее описание проекта
- FINAL_AUDIT_REPORT.md - Полный аудит системы
- TODO.md - Roadmap развития
- CHANGES_SUMMARY.md - История изменений

### Внешние ресурсы
- Binance Testnet: https://testnet.binance.vision/
- Binance API Docs: https://binance-docs.github.io/apidocs/
- CCXT Documentation: https://docs.ccxt.com/
- Python asyncio: https://docs.python.org/3/library/asyncio.html

### Поддержка
- GitHub Issues: Для багов и вопросов
- GitHub Discussions: Для общих вопросов

---

**Документ подготовлен:** GitHub Copilot  
**Версия:** 2.0  
**Дата:** 23 декабря 2024

---

## ⚠️ ФИНАЛЬНОЕ ПРЕДУПРЕЖДЕНИЕ

**КРИТИЧЕСКИ ВАЖНО:**

1. **ВСЕГДА начинайте с Testnet** - минимум 4-6 недель тестирования
2. **НИКОГДА не используйте API ключи с правами Withdrawal**
3. **НИКОГДА не торгуйте средствами, которые не можете позволить себе потерять**
4. **Постоянный мониторинг** обязателен при работе с реальными средствами
5. **Резервные копии** делайте регулярно
6. **Безопасность** - это не опция, а необходимость

Алгоритмическая торговля несет высокий риск. Используйте систему ответственно.
