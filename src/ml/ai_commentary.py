"""
AI Commentary Generator for Trading Bot

Generates intelligent commentary and insights for trading notifications based on
historical performance analysis and current market conditions.
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from src.ml.trade_analyzer import TradeAnalyzer
from src.ml.performance_analyzer import PerformanceAnalyzer
from src.ml.signal_scorer import SignalScorer


class AICommentaryGenerator:
    """Generates AI-powered commentary for trading notifications"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize AI Commentary Generator
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.trade_analyzer = TradeAnalyzer(logger=self.logger)
        self.perf_analyzer = PerformanceAnalyzer(logger=self.logger)
        self.signal_scorer = SignalScorer(logger=self.logger)
    
    def generate_position_open_commentary(self, symbol: str, side: str, 
                                         confidence: float = None) -> str:
        """
        Generate AI commentary for position opening
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL
            confidence: Signal confidence score (0-1 or 0-100)
            
        Returns:
            Commentary string
        """
        try:
            # Normalize confidence to 0-1 range
            if confidence and confidence > 1:
                confidence = confidence / 100
            
            # Get historical performance for this symbol
            pair_stats = self.signal_scorer.get_symbol_stats(symbol)
            side_stats = self.signal_scorer.get_side_stats(symbol, side)
            
            # Build commentary parts
            parts = []
            
            # Confidence commentary
            if confidence:
                if confidence >= 0.85:
                    parts.append("🎯 <b>High confidence signal</b> - Strong indicator alignment detected.")
                elif confidence >= 0.70:
                    parts.append("📊 <b>Moderate confidence</b> - Good technical setup.")
                else:
                    parts.append("⚠️ <b>Lower confidence</b> - Proceed with caution.")
            
            # Historical performance commentary
            if pair_stats and pair_stats['total_trades'] >= 3:
                win_rate = pair_stats['win_rate']
                if win_rate >= 60:
                    parts.append(f"✅ <b>{symbol} historically strong</b> ({win_rate:.0f}% win rate)")
                elif win_rate >= 40:
                    parts.append(f"📊 <b>{symbol} mixed performance</b> ({win_rate:.0f}% win rate)")
                else:
                    parts.append(f"⚠️ <b>{symbol} challenging pair</b> ({win_rate:.0f}% win rate)")
            
            # Side-specific commentary
            if side_stats and side_stats['trades'] >= 2:
                side_win_rate = side_stats['win_rate']
                if side_win_rate >= 60:
                    parts.append(f"💪 <b>{side} trades performing well</b> on this pair")
                elif side_win_rate < 40:
                    parts.append(f"🔍 <b>{side} trades need improvement</b> on this pair")
            
            # Tactic commentary
            parts.append(self._get_tactic_comment(symbol, side, confidence))
            
            if parts:
                return "\n\n🤖 <b>AI Insight:</b>\n" + "\n".join(parts)
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generating position open commentary: {e}")
            return ""
    
    def generate_position_close_commentary(self, symbol: str, side: str, pnl: float,
                                          pnl_percent: float) -> str:
        """
        Generate AI commentary for position closing
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL  
            pnl: Profit/loss amount
            pnl_percent: Profit/loss percentage
            
        Returns:
            Commentary string
        """
        try:
            parts = []
            
            # Outcome commentary
            if pnl > 0:
                if pnl_percent > 5:
                    parts.append("🎉 <b>Excellent trade!</b> Strong profit achieved.")
                elif pnl_percent > 2:
                    parts.append("✅ <b>Good trade!</b> Solid profit captured.")
                else:
                    parts.append("👍 <b>Profitable trade</b> - Small but consistent wins build success.")
            else:
                if pnl_percent < -5:
                    parts.append("⚠️ <b>Significant loss</b> - Review stop-loss strategy.")
                elif pnl_percent < -2:
                    parts.append("📉 <b>Loss taken</b> - Part of risk management.")
                else:
                    parts.append("➖ <b>Minor loss</b> - Well-controlled risk.")
            
            # Get recent performance
            recent_perf = self.trade_analyzer.analyze_performance(days=7)
            if recent_perf and recent_perf.get('total_trades', 0) >= 3:
                win_rate = recent_perf.get('win_rate', 0)
                recent_pnl = recent_perf.get('total_pnl', 0)
                
                if win_rate >= 60:
                    parts.append(f"📈 <b>Strategy performing well</b> ({win_rate:.0f}% recent win rate)")
                elif win_rate < 40:
                    parts.append(f"🔍 <b>Strategy needs adjustment</b> ({win_rate:.0f}% recent win rate)")
            
            # Learning commentary
            if pnl < 0:
                parts.append("📚 <b>Learning opportunity</b> - Analyzing this trade to improve future decisions.")
            
            if parts:
                return "\n\n🤖 <b>AI Analysis:</b>\n" + "\n".join(parts)
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generating position close commentary: {e}")
            return ""
    
    def generate_daily_summary_commentary(self, daily_pnl: float, 
                                         open_positions: int) -> str:
        """
        Generate AI commentary for daily summary
        
        Args:
            daily_pnl: Daily profit/loss
            open_positions: Number of open positions
            
        Returns:
            Commentary string
        """
        try:
            parts = []
            
            # Get comprehensive performance data
            perf_7d = self.trade_analyzer.analyze_performance(days=7)
            perf_30d = self.trade_analyzer.analyze_performance(days=30)
            
            # Daily performance commentary
            if daily_pnl > 0:
                parts.append(f"✅ <b>Positive day!</b> ${daily_pnl:,.2f} profit secured.")
            elif daily_pnl < 0:
                parts.append(f"📊 <b>Red day:</b> ${abs(daily_pnl):,.2f} loss - Tomorrow is a new opportunity.")
            else:
                parts.append("➖ <b>Neutral day</b> - Waiting for optimal setups.")
            
            # Weekly trend
            if perf_7d and perf_7d.get('total_trades', 0) >= 3:
                weekly_pnl = perf_7d.get('total_pnl', 0)
                win_rate_7d = perf_7d.get('win_rate', 0)
                
                if weekly_pnl > 0:
                    parts.append(f"📈 <b>Week trending positive:</b> ${weekly_pnl:,.2f} ({win_rate_7d:.0f}% win rate)")
                else:
                    parts.append(f"🔍 <b>Weekly review needed:</b> ${weekly_pnl:,.2f} ({win_rate_7d:.0f}% win rate)")
            
            # Get advanced metrics
            try:
                metrics = self.perf_analyzer.get_performance_summary()
                sharpe = metrics.get('sharpe_ratio')
                max_dd = metrics.get('max_drawdown_pct')
                
                if sharpe and sharpe > 0:
                    if sharpe > 2:
                        parts.append(f"⭐ <b>Excellent risk-adjusted returns</b> (Sharpe: {sharpe:.2f})")
                    elif sharpe > 1:
                        parts.append(f"✅ <b>Good risk management</b> (Sharpe: {sharpe:.2f})")
                
                if max_dd and max_dd > 0:
                    if max_dd < 10:
                        parts.append(f"💪 <b>Low drawdown</b> ({max_dd:.1f}%) - Excellent risk control")
                    elif max_dd > 30:
                        parts.append(f"⚠️ <b>High drawdown</b> ({max_dd:.1f}%) - Consider reducing position sizes")
            except:
                pass  # Metrics not critical
            
            # Monthly performance
            if perf_30d and perf_30d.get('total_trades', 0) >= 10:
                monthly_pnl = perf_30d.get('total_pnl', 0)
                win_rate_30d = perf_30d.get('win_rate', 0)
                profit_factor = perf_30d.get('profit_factor', 0)
                
                if profit_factor and profit_factor > 0:
                    if profit_factor > 2:
                        parts.append(f"🎯 <b>Strong monthly performance</b> (PF: {profit_factor:.2f})")
                    elif profit_factor < 1:
                        parts.append(f"📊 <b>Monthly optimization needed</b> (PF: {profit_factor:.2f})")
            
            # Active positions commentary
            if open_positions > 0:
                parts.append(f"👀 <b>Monitoring {open_positions} active position(s)</b> - Risk management active.")
            else:
                parts.append("🔎 <b>No open positions</b> - Scanning for high-quality setups.")
            
            # Strategic recommendation
            strategy_tip = self._get_strategy_recommendation(perf_7d, perf_30d)
            if strategy_tip:
                parts.append(strategy_tip)
            
            if parts:
                return "\n\n🤖 <b>AI Daily Insight:</b>\n" + "\n".join(parts)
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generating daily summary commentary: {e}")
            return ""
    
    def _get_tactic_comment(self, symbol: str, side: str, confidence: float = None) -> str:
        """Generate tactical commentary"""
        tactics = []
        
        if confidence and confidence >= 0.85:
            tactics.append("Using <b>larger position size</b> due to high confidence")
        elif confidence and confidence < 0.60:
            tactics.append("Using <b>smaller position size</b> due to lower confidence")
        
        if side == 'BUY':
            tactics.append("Following <b>long momentum</b> strategy")
        else:
            tactics.append("Following <b>short reversal</b> strategy")
        
        if tactics:
            return "🎲 <b>Tactics:</b> " + " • ".join(tactics)
        return ""
    
    def _get_strategy_recommendation(self, perf_7d: Dict, perf_30d: Dict) -> str:
        """Generate strategic recommendation based on performance"""
        try:
            if not perf_7d or not perf_30d:
                return ""
            
            win_rate_7d = perf_7d.get('win_rate', 0)
            win_rate_30d = perf_30d.get('win_rate', 0)
            
            # Improving trend
            if win_rate_7d > win_rate_30d + 10:
                return "📈 <b>Strategy improving!</b> Recent adjustments showing positive results."
            
            # Declining trend
            if win_rate_7d < win_rate_30d - 10 and win_rate_7d < 50:
                return "⚠️ <b>Recommendation:</b> Consider reducing trading frequency and focus on higher-confidence setups."
            
            # Consistent performance
            if win_rate_30d >= 60:
                return "🎯 <b>Strategy working well</b> - Maintain current approach and risk levels."
            
            # Need improvement
            if win_rate_30d < 40:
                return "🔧 <b>Strategy optimization needed</b> - Reviewing profitable patterns to improve signal quality."
            
            return ""
        except:
            return ""


# Singleton instance
_commentary_generator = None

def get_commentary_generator(logger: Optional[logging.Logger] = None) -> AICommentaryGenerator:
    """Get or create the commentary generator singleton"""
    global _commentary_generator
    if _commentary_generator is None:
        _commentary_generator = AICommentaryGenerator(logger=logger)
    return _commentary_generator
