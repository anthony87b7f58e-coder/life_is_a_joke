import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from backtester.cli import test
import json

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 ROFL Trading Bot\n"
        "/balance - баланс\n"
        "/backtest BTCUSDT - бэктест\n"
        "/strategies - список стратегий"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Testnet Balance: 10,000 USDT")

async def backtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    symbol = args[0] if args else "BTCUSDT"
    
    try:
        # Имитация вызова backtester
        results = {
            "profit": 245.3,
            "drawdown": -12.5,
            "sharpe_ratio": 2.1,
            "win_rate": 68.4
        }
        msg = f"📊 {symbol} Backtest:\n" + json.dumps(results, indent=2)
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def strategies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Available: RSI, DCA")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("backtest", backtest_command))
    app.add_handler(CommandHandler("strategies", strategies))
    
    app.run_polling()

if __name__ == "__main__":
    main()
