# 🤖 Machine Learning System - User Guide

## Overview

The trading bot now includes a **Machine Learning analysis system** that analyzes your historical trades to identify patterns, provide insights, and help optimize your trading strategy.

## Features

### 1. **Trade Analysis**
- Analyzes all closed positions from the database
- Identifies profitable vs unprofitable patterns
- Calculates win rates, profit factors, and other metrics

### 2. **Performance Analytics**
- Advanced metrics like Sharpe Ratio and Maximum Drawdown
- Win/loss streak analysis
- Risk-adjusted return calculations

### 3. **Signal Scoring**
- Scores trading signals based on historical success
- Combines technical indicators with historical patterns
- Provides trade recommendations (STRONG/MODERATE/WEAK/AVOID)

## Installation

### Required Dependencies

Install the ML analysis libraries:

```bash
# Install basic dependencies (required)
pip3 install pandas numpy

# Optional: For future ML enhancements
pip3 install scikit-learn
```

## Usage

### 1. Basic Trade Analysis

Run the analysis script to get comprehensive insights:

```bash
cd ~/trading-bot-setup/life_is_a_joke
python3 scripts/analyze_trades.py
```

**Output includes:**
- Overall performance metrics
- Win rate and profit statistics
- Performance by trading pair
- Performance by strategy
- Best and worst performing pairs
- Actionable recommendations

### 2. Using ML Components in Code

You can import and use ML components programmatically:

```python
from src.ml import TradeAnalyzer, PerformanceAnalyzer, SignalScorer

# Initialize analyzers
trade_analyzer = TradeAnalyzer()
perf_analyzer = PerformanceAnalyzer()
signal_scorer = SignalScorer()

# Analyze overall performance
performance = trade_analyzer.analyze_performance(days=30)
print(f"Win rate: {performance['win_rate']:.1f}%")
print(f"Total P&L: ${performance['total_pnl']:.2f}")

# Get advanced metrics
metrics = perf_analyzer.get_performance_summary(days=30)
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown_pct']:.1f}%")

# Score a potential trade
score = signal_scorer.score_signal('BTCUSDT', 'BUY', confidence=0.75)
print(f"Trade score: {score['score']:.1f}/100")
print(f"Recommendation: {score['recommendation']}")
```

### 3. Scheduling Regular Analysis

Create a cron job to run analysis weekly:

```bash
# Edit crontab
crontab -e

# Add this line to run analysis every Sunday at 9 AM
0 9 * * 0 cd ~/trading-bot-setup/life_is_a_joke && python3 scripts/analyze_trades.py > /tmp/trading_analysis.txt 2>&1
```

## Understanding the Metrics

### Basic Metrics

- **Win Rate**: Percentage of profitable trades
  - **Good**: >60%
  - **Excellent**: >70%

- **Profit Factor**: Total profits / Total losses
  - **Good**: >1.5
  - **Excellent**: >2.0

- **Average Profit/Loss**: Average gain per winning/losing trade

### Advanced Metrics

- **Sharpe Ratio**: Risk-adjusted return measure
  - **Good**: >1.0
  - **Excellent**: >2.0
  - **Outstanding**: >3.0

- **Maximum Drawdown**: Largest peak-to-trough decline
  - **Good**: <20%
  - **Acceptable**: <30%
  - **Risky**: >30%

- **Win/Loss Streaks**: Consecutive winning/losing trades
  - Helps identify momentum patterns

## Signal Scoring System

The system scores trading signals from 0-100 based on:

1. **Historical Symbol Performance** (30%)
   - Recent 7-day success rate
   - Last 30-day success rate

2. **Side-Specific Success** (10%)
   - BUY vs SELL performance for that pair

3. **Technical Indicator Confidence** (60%)
   - Confidence from RSI, MACD, EMA, etc.

### Score Interpretation

- **75-100**: STRONG - High probability trade
- **60-74**: MODERATE - Good probability trade
- **50-59**: WEAK - Neutral probability
- **0-49**: AVOID - Low probability trade

## Practical Examples

### Example 1: Check Which Pairs to Focus On

```bash
python3 scripts/analyze_trades.py
```

Look at the "BEST PERFORMING PAIRS" section. Focus your trading on these pairs.

### Example 2: Identify Pairs to Avoid

Check the "WORST PERFORMING PAIRS" section. Consider:
- Disabling these pairs temporarily
- Adjusting strategy parameters for them
- Reducing position size

### Example 3: Optimize Strategy

1. Run analysis monthly
2. Compare win rates across strategies
3. Increase position sizes for high-performing strategies
4. Disable or adjust underperforming strategies

## Integration with Confidence-Based Sizing

The ML system works perfectly with the confidence-based position sizing feature:

```python
# In strategy_manager.py, the signal scorer can be integrated:
from src.ml import SignalScorer

scorer = SignalScorer()
ml_score = scorer.score_signal(symbol, side, technical_confidence)

# Use ML score to further adjust position size
if ml_score['score'] < 50:
    # Reduce position size or skip trade
    pass
```

## Best Practices

### 1. Accumulate Data First

- Run the bot for at least 2-4 weeks before relying on ML insights
- More data = more accurate patterns

### 2. Regular Analysis

- Run analysis weekly to track performance trends
- Adjust strategy based on findings

### 3. Act on Recommendations

- The system provides specific recommendations
- Implement changes gradually and monitor results

### 4. Monitor Key Metrics

Focus on these metrics:
- Win Rate (target: >60%)
- Profit Factor (target: >1.5)
- Sharpe Ratio (target: >1.0)
- Max Drawdown (target: <20%)

## Future Enhancements

The current ML system provides a foundation for future enhancements:

### Phase 2 (Planned)
- **Pattern Recognition**: Detect chart patterns automatically
- **Predictive Models**: ML models to predict trade success
- **Auto-optimization**: Automatically adjust strategy parameters

### Phase 3 (Advanced)
- **Deep Learning**: LSTM networks for price prediction
- **Reinforcement Learning**: Self-optimizing trading agent
- **Sentiment Analysis**: Analyze news and social media

## Troubleshooting

### "No trading data available"

**Issue**: Not enough closed positions in database

**Solution**: 
- Run the bot for longer to accumulate data
- Check that positions are being closed properly
- Verify database connection

### "ModuleNotFoundError: No module named 'src.ml'"

**Issue**: Python can't find the ML module

**Solution**:
```bash
cd ~/trading-bot-setup/life_is_a_joke
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 scripts/analyze_trades.py
```

### Low Win Rate

**Issue**: Win rate below 50%

**Potential fixes**:
- Review and adjust technical indicator thresholds
- Reduce number of trading pairs (focus on best performers)
- Enable profit-check before closing (intelligent loss prevention)
- Adjust MIN_POSITION_SIZE_PCT to reduce risk

## Support and Questions

For issues or questions:
1. Check the bot logs: `sudo journalctl -u trading-bot -f`
2. Run diagnostics: `python3 scripts/diagnose_positions.py`
3. Review this guide and try the examples

## Summary

The ML system provides:
- ✅ Data-driven insights into your trading performance
- ✅ Identification of profitable patterns
- ✅ Recommendations for optimization
- ✅ Foundation for future ML enhancements

**Start using it today:**
```bash
python3 scripts/analyze_trades.py
```

Then act on the recommendations to improve your bot's performance!
