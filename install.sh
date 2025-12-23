#!/bin/bash
echo "🚀 Installing ROFL OctoBot Features..."

pip install -r requirements.txt
pip install fire pandas-ta plotly fastapi uvicorn python-telegram-bot

echo "✅ Installation complete!"
echo "📊 Backtest: python -m backtester.cli test BTCUSDT 90"
echo "🌐 Dashboard: uvicorn src.dashboard:app --reload --port 8080"
echo "🤖 Telegram: python telegram_bot.py"
