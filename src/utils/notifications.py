"""
Telegram Notifications Module
Sends trading alerts and notifications via Telegram
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class TelegramNotifier:
    """Telegram notification handler for trading bot"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None, enabled: bool = True):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
            enabled: Whether notifications are enabled
        """
        self.logger = logging.getLogger(__name__)
        self.enabled = enabled and TELEGRAM_AVAILABLE
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', '')
        self.bot: Optional[Bot] = None
        
        if not TELEGRAM_AVAILABLE and enabled:
            self.logger.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
            self.enabled = False
        
        if self.enabled:
            if not self.bot_token or not self.chat_id:
                self.logger.warning("Telegram bot token or chat ID not configured. Notifications disabled.")
                self.enabled = False
            else:
                try:
                    self.bot = Bot(token=self.bot_token)
                    self.logger.info("Telegram notifier initialized successfully")
                except Exception as e:
                    self.logger.error(f"Failed to initialize Telegram bot: {e}")
                    self.enabled = False
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a message to Telegram
        
        Args:
            message: Message text
            parse_mode: Parse mode (HTML or Markdown)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Run async send_message in sync context
            loop = None
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If there's already a running loop, create a new one in a thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            self.bot.send_message(
                                chat_id=self.chat_id,
                                text=message,
                                parse_mode=parse_mode
                            )
                        )
                        future.result(timeout=10)
                else:
                    loop.run_until_complete(
                        self.bot.send_message(
                            chat_id=self.chat_id,
                            text=message,
                            parse_mode=parse_mode
                        )
                    )
            except RuntimeError:
                # No event loop, create one
                asyncio.run(
                    self.bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode=parse_mode
                    )
                )
            return True
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def notify_position_opened(self, symbol: str, side: str, quantity: float, 
                              price: float, strategy: str = "Unknown", score: int = None) -> bool:
        """
        Notify about opened position
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL
            quantity: Position quantity
            price: Entry price
            strategy: Strategy name
            score: Signal confidence score (0-100)
            
        Returns:
            True if sent successfully
        """
        emoji = "🟢" if side.upper() == "BUY" else "🔴"
        
        score_text = f"\n⭐ Signal Score: <b>{score}/100</b>" if score is not None else ""
        
        message = f"""
{emoji} <b>Position Opened</b>

📊 Symbol: <code>{symbol}</code>
📈 Side: <b>{side.upper()}</b>
💰 Quantity: <code>{quantity}</code>
💵 Price: <code>${price:,.2f}</code>
🎯 Strategy: <i>{strategy}</i>{score_text}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())
    
    def notify_position_closed(self, symbol: str, side: str, quantity: float,
                              entry_price: float, exit_price: float, 
                              pnl: float, pnl_percent: float, 
                              strategy: str = "Unknown", score: int = None) -> bool:
        """
        Notify about closed position
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL (original position)
            quantity: Position quantity
            entry_price: Entry price
            exit_price: Exit price
            pnl: Profit/Loss amount
            pnl_percent: Profit/Loss percentage
            strategy: Strategy name
            score: Signal confidence score (0-100)
            
        Returns:
            True if sent successfully
        """
        profit = pnl > 0
        emoji = "✅" if profit else "❌"
        pnl_emoji = "💰" if profit else "💸"
        
        score_text = f"\n⭐ Signal Score: <b>{score}/100</b>" if score is not None else ""
        
        message = f"""
{emoji} <b>Position Closed</b>

📊 Symbol: <code>{symbol}</code>
📈 Side: <b>{side.upper()}</b>
💰 Quantity: <code>{quantity}</code>
📥 Entry: <code>${entry_price:,.2f}</code>
📤 Exit: <code>${exit_price:,.2f}</code>

{pnl_emoji} P&L: <b>${pnl:,.2f}</b> ({pnl_percent:+.2f}%)
🎯 Strategy: <i>{strategy}</i>{score_text}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())
    
    def notify_stop_loss_triggered(self, symbol: str, side: str, quantity: float,
                                   entry_price: float, stop_price: float,
                                   loss: float, loss_percent: float) -> bool:
        """
        Notify about stop-loss trigger
        
        Args:
            symbol: Trading pair symbol
            side: Original position side
            quantity: Position quantity
            entry_price: Entry price
            stop_price: Stop-loss price
            loss: Loss amount
            loss_percent: Loss percentage
            
        Returns:
            True if sent successfully
        """
        message = f"""
⚠️ <b>Stop-Loss Triggered</b>

📊 Symbol: <code>{symbol}</code>
📈 Side: <b>{side.upper()}</b>
💰 Quantity: <code>{quantity}</code>
📥 Entry: <code>${entry_price:,.2f}</code>
🛑 Stop: <code>${stop_price:,.2f}</code>

💸 Loss: <b>${loss:,.2f}</b> ({loss_percent:.2f}%)

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())
    
    def notify_take_profit_triggered(self, symbol: str, side: str, quantity: float,
                                     entry_price: float, tp_price: float,
                                     profit: float, profit_percent: float) -> bool:
        """
        Notify about take-profit trigger
        
        Args:
            symbol: Trading pair symbol
            side: Original position side
            quantity: Position quantity
            entry_price: Entry price
            tp_price: Take-profit price
            profit: Profit amount
            profit_percent: Profit percentage
            
        Returns:
            True if sent successfully
        """
        message = f"""
🎯 <b>Take-Profit Triggered</b>

📊 Symbol: <code>{symbol}</code>
📈 Side: <b>{side.upper()}</b>
💰 Quantity: <code>{quantity}</code>
📥 Entry: <code>${entry_price:,.2f}</code>
✅ Target: <code>${tp_price:,.2f}</code>

💰 Profit: <b>${profit:,.2f}</b> (+{profit_percent:.2f}%)

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())
    
    def notify_daily_summary(self, total_trades: int, winning_trades: int,
                           losing_trades: int, total_pnl: float,
                           win_rate: float, largest_win: float,
                           largest_loss: float) -> bool:
        """
        Send daily trading summary
        
        Args:
            total_trades: Total number of trades
            winning_trades: Number of winning trades
            losing_trades: Number of losing trades
            total_pnl: Total profit/loss
            win_rate: Win rate percentage
            largest_win: Largest winning trade
            largest_loss: Largest losing trade
            
        Returns:
            True if sent successfully
        """
        pnl_emoji = "💰" if total_pnl > 0 else "💸" if total_pnl < 0 else "➖"
        
        message = f"""
📊 <b>Daily Summary</b>

📈 Trades: <b>{total_trades}</b>
✅ Wins: <b>{winning_trades}</b>
❌ Losses: <b>{losing_trades}</b>
🎯 Win Rate: <b>{win_rate:.1f}%</b>

{pnl_emoji} Total P&L: <b>${total_pnl:,.2f}</b>
💰 Largest Win: <code>${largest_win:,.2f}</code>
💸 Largest Loss: <code>${largest_loss:,.2f}</code>

📅 Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        return self.send_message(message.strip())
    
    def notify_error(self, error_type: str, error_message: str, 
                    details: Optional[str] = None) -> bool:
        """
        Notify about critical error
        
        Args:
            error_type: Type of error
            error_message: Error message
            details: Additional details
            
        Returns:
            True if sent successfully
        """
        message = f"""
❌ <b>Error Alert</b>

⚠️ Type: <b>{error_type}</b>
📝 Message: <code>{error_message}</code>
"""
        if details:
            message += f"\n📋 Details:\n<code>{details}</code>\n"
        
        message += f"\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message.strip())
    
    def notify_risk_limit_warning(self, limit_type: str, current_value: float,
                                 max_value: float, unit: str = "") -> bool:
        """
        Notify about risk limit warning
        
        Args:
            limit_type: Type of limit (e.g., "Daily Loss", "Max Positions")
            current_value: Current value
            max_value: Maximum allowed value
            unit: Unit of measurement (e.g., "%", "$")
            
        Returns:
            True if sent successfully
        """
        percentage = (current_value / max_value * 100) if max_value > 0 else 0
        
        message = f"""
⚠️ <b>Risk Limit Warning</b>

📊 Limit: <b>{limit_type}</b>
📈 Current: <code>{current_value}{unit}</code>
🎯 Maximum: <code>{max_value}{unit}</code>
📉 Usage: <b>{percentage:.1f}%</b>

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())
    
    def notify_bot_started(self, exchange: str, trading_enabled: bool,
                          max_positions: int, max_daily_trades: int) -> bool:
        """
        Notify about bot startup
        
        Args:
            exchange: Exchange name
            trading_enabled: Whether trading is enabled
            max_positions: Maximum open positions
            max_daily_trades: Maximum daily trades
            
        Returns:
            True if sent successfully
        """
        status = "🟢 ENABLED" if trading_enabled else "🟡 MONITORING ONLY"
        
        message = f"""
🤖 <b>Trading Bot Started</b>

🏦 Exchange: <b>{exchange}</b>
⚡ Trading: {status}
📊 Max Positions: <b>{max_positions}</b>
📈 Max Daily Trades: <b>{max_daily_trades}</b>

⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())
    
    def notify_bot_stopped(self, reason: str = "Manual stop") -> bool:
        """
        Notify about bot shutdown
        
        Args:
            reason: Reason for shutdown
            
        Returns:
            True if sent successfully
        """
        message = f"""
🛑 <b>Trading Bot Stopped</b>

📝 Reason: <i>{reason}</i>

⏰ Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())


# Global instance (initialized by config)
_notifier: Optional[TelegramNotifier] = None


def get_notifier() -> Optional[TelegramNotifier]:
    """Get global notifier instance"""
    return _notifier


def init_notifier(bot_token: Optional[str] = None, chat_id: Optional[str] = None, 
                 enabled: bool = True) -> TelegramNotifier:
    """
    Initialize global notifier instance
    
    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        enabled: Whether notifications are enabled
        
    Returns:
        TelegramNotifier instance
    """
    global _notifier
    _notifier = TelegramNotifier(bot_token, chat_id, enabled)
    return _notifier
