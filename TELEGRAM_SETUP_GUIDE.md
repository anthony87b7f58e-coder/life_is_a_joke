# Telegram Bot Setup Guide

This guide will walk you through setting up Telegram notifications for your trading bot.

## Overview

The trading bot can send real-time notifications to your Telegram account for:
- 🟢 Position opened (entry price, quantity, strategy)
- ✅ Position closed (exit price, profit/loss, percentage)
- 🛑 Stop-loss triggered
- 🎯 Take-profit triggered
- 📊 Daily trading summary
- ❌ Critical errors and warnings
- ⚠️ Risk limit warnings

## Prerequisites

- Telegram account
- Active internet connection
- Trading bot with python-telegram-bot installed

## Step-by-Step Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a chat and send the command: `/newbot`
3. Follow the prompts:
   - **Bot name**: Enter a display name (e.g., "My Trading Bot")
   - **Bot username**: Enter a unique username ending in 'bot' (e.g., "my_trading_alerts_bot")
4. BotFather will provide you with a **Bot Token** that looks like:
   ```
   123456789:ABC-DEFghIJKlmnoPQRstuVWXyz_1234567890
   ```
5. **Save this token** - you'll need it later

### Step 2: Get Your Chat ID

**Option A: Using @userinfobot**
1. In Telegram, search for **@userinfobot**
2. Start a chat with it
3. Send any message or `/start`
4. The bot will reply with your user information including your **Chat ID** (a number like `123456789`)

**Option B: Using @RawDataBot**
1. Search for **@RawDataBot** in Telegram
2. Start a chat and send `/start`
3. Look for `"id":` in the response - the number after it is your Chat ID

**Option C: Manual method**
1. Send a message to your bot (the one you created in Step 1)
2. Open this URL in your browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id":` - the number is your Chat ID

### Step 3: Configure the Trading Bot

1. Open the environment configuration file:
   ```bash
   sudo nano /etc/trading-bot/.env
   ```

2. Find and update these lines:
   ```env
   ENABLE_NOTIFICATIONS=true
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=123456789:ABC-DEFghIJKlmnoPQRstuVWXyz_1234567890
   TELEGRAM_CHAT_ID=123456789
   ```

3. Replace:
   - `123456789:ABC-DEFghIJKlmnoPQRstuVWXyz_1234567890` with your actual bot token from Step 1
   - `123456789` with your actual Chat ID from Step 2

4. Save and exit (Ctrl+X, then Y, then Enter)

### Step 4: Install Required Package

If not already installed, install the Telegram bot library:

```bash
cd /opt/trading-bot
source venv/bin/activate
pip install python-telegram-bot
```

Verify installation:
```bash
python3 -c "import telegram; print('Telegram bot library version:', telegram.__version__)"
```

### Step 5: Restart the Trading Bot

```bash
sudo systemctl restart trading-bot
```

### Step 6: Verify Setup

Check the logs to confirm Telegram notifications are initialized:
```bash
sudo journalctl -u trading-bot -f
```

You should see:
```
Telegram notifier initialized successfully
```

Send a test by checking if you receive a "Trading Bot Started" notification in your Telegram chat.

## Notification Types

### Position Opened
```
🟢 Position Opened

📊 Symbol: BTC/USDT
📈 Side: BUY
💰 Quantity: 0.001
💵 Price: $50,000.00
🎯 Strategy: Simple Trend Following

⏰ Time: 2025-12-29 12:00:00
```

### Position Closed
```
✅ Position Closed

📊 Symbol: BTC/USDT
📈 Side: BUY
💰 Quantity: 0.001
📥 Entry: $50,000.00
📤 Exit: $51,000.00

💰 P&L: $10.00 (+2.00%)
🎯 Strategy: Simple Trend Following

⏰ Time: 2025-12-29 13:00:00
```

### Stop-Loss Triggered
```
⚠️ Stop-Loss Triggered

📊 Symbol: BTC/USDT
📈 Side: BUY
💰 Quantity: 0.001
📥 Entry: $50,000.00
🛑 Stop: $49,000.00

💸 Loss: -$10.00 (-2.00%)

⏰ Time: 2025-12-29 12:30:00
```

### Daily Summary
```
📊 Daily Summary

📈 Trades: 5
✅ Wins: 3
❌ Losses: 2
🎯 Win Rate: 60.0%

💰 Total P&L: $125.50
💰 Largest Win: $75.00
💸 Largest Loss: -$25.00

📅 Date: 2025-12-29
```

### Error Alert
```
❌ Error Alert

⚠️ Type: Exchange Connection Error
📝 Message: Failed to connect to exchange API

⏰ Time: 2025-12-29 14:00:00
```

## Troubleshooting

### "Telegram notifier not initialized"

**Problem**: Bot token or Chat ID is missing or incorrect.

**Solution**:
1. Verify your token and Chat ID in `/etc/trading-bot/.env`
2. Make sure there are no extra spaces
3. Ensure `ENABLE_NOTIFICATIONS=true` and `TELEGRAM_ENABLED=true`

### "ModuleNotFoundError: No module named 'telegram'"

**Problem**: python-telegram-bot library not installed.

**Solution**:
```bash
cd /opt/trading-bot
source venv/bin/activate
pip install python-telegram-bot
sudo systemctl restart trading-bot
```

### "Telegram bot library not installed"

**Problem**: Library not available in the virtual environment.

**Solution**:
```bash
cd /opt/trading-bot
source venv/bin/activate
pip install --upgrade python-telegram-bot
```

### Not Receiving Notifications

**Checklist**:
1. ✅ Did you start a chat with your bot? (Send /start to your bot)
2. ✅ Is the bot token correct?
3. ✅ Is the Chat ID correct?
4. ✅ Is `ENABLE_NOTIFICATIONS=true`?
5. ✅ Is `TELEGRAM_ENABLED=true`?
6. ✅ Check logs: `sudo journalctl -u trading-bot | grep Telegram`

### Invalid Token Error

**Problem**: Bot token is incorrect or expired.

**Solution**:
1. Go back to @BotFather
2. Send `/mybots`
3. Select your bot
4. Choose "API Token"
5. Copy the new token
6. Update `/etc/trading-bot/.env`
7. Restart: `sudo systemctl restart trading-bot`

## Testing Notifications

To test if notifications are working, you can:

1. **Enable test mode** (optional):
   ```bash
   # Temporarily set trading to enabled to trigger notifications
   sudo nano /etc/trading-bot/.env
   # Set TRADING_ENABLED=true
   sudo systemctl restart trading-bot
   ```

2. **Monitor logs** for notification attempts:
   ```bash
   sudo journalctl -u trading-bot -f | grep -i telegram
   ```

3. **Check bot startup notification**: You should receive a "Trading Bot Started" message when the bot restarts.

## Security Best Practices

1. **Keep tokens private**: Never share your bot token publicly
2. **Use private chats only**: Don't add your bot to public groups
3. **Restrict file permissions**:
   ```bash
   sudo chmod 600 /etc/trading-bot/.env
   sudo chown tradingbot:tradingbot /etc/trading-bot/.env
   ```
4. **Revoke tokens if exposed**: If you accidentally expose your token, revoke it via @BotFather and generate a new one

## Advanced Configuration

### Custom Message Format

Edit `/opt/trading-bot/src/utils/notifications.py` to customize message templates.

### Multiple Chat IDs

To send notifications to multiple chats, you can modify the code or create a group and add your bot to it.

### Disable Specific Notifications

You can selectively disable certain notification types by commenting out the relevant `notifier.notify_*()` calls in the code.

## Support

If you encounter issues:
1. Check logs: `sudo journalctl -u trading-bot -n 100 --no-pager`
2. Verify configuration: `cat /etc/trading-bot/.env | grep TELEGRAM`
3. Test bot token manually: `curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe`
4. Refer to the main documentation: `README.md` and `TROUBLESHOOTING.md`

## Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [Creating Telegram Bots Guide](https://core.telegram.org/bots#how-do-i-create-a-bot)
