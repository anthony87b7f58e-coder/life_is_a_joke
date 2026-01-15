#!/usr/bin/env python3
"""
Position Diagnostics Script
Shows detailed information about open positions and database state
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
env_file = os.environ.get('CONFIG_DIR', '/etc/trading-bot') + '/.env'
if not os.path.exists(env_file):
    env_file = str(Path(__file__).parent.parent / '.env')

if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"📁 Loaded environment from: {env_file}")
else:
    print(f"⚠️  Warning: No .env file found, using default values")
print()

from src.core.config import Config
from src.core.database import Database


def diagnose_positions():
    """Run comprehensive position diagnostics"""
    
    print("=" * 80)
    print(" TRADING BOT POSITION DIAGNOSTICS")
    print("=" * 80)
    print()
    
    # Load config
    try:
        config = Config()
        print(f"✅ Config loaded successfully")
        print(f"   Database path: {config.db_path}")
        print(f"   Max open positions: {config.max_open_positions}")
        print(f"   Max daily trades: {config.max_daily_trades}")
        print()
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    # Connect to database
    try:
        db = Database(config)
        print(f"✅ Database connection established")
        print()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    # Check if database file exists
    db_file = Path(config.db_path)
    if db_file.exists():
        size_kb = db_file.stat().st_size / 1024
        print(f"📁 Database file: {db_file}")
        print(f"   Size: {size_kb:.2f} KB")
        print(f"   Last modified: {datetime.fromtimestamp(db_file.stat().st_mtime)}")
        print()
    else:
        print(f"⚠️  Database file does not exist: {db_file}")
        print()
    
    # Get all positions
    try:
        cursor = db.conn.cursor()
        
        # Count by status
        cursor.execute("SELECT status, COUNT(*) FROM positions GROUP BY status")
        status_counts = cursor.fetchall()
        
        print("📊 POSITION STATISTICS:")
        print("-" * 80)
        if status_counts:
            for row in status_counts:
                print(f"   {row[0]}: {row[1]} positions")
        else:
            print("   No positions found in database")
        print()
        
        # Get open positions
        open_positions = db.get_open_positions()
        
        print(f"🔓 OPEN POSITIONS: {len(open_positions)}")
        print("-" * 80)
        
        if open_positions:
            for i, pos in enumerate(open_positions, 1):
                print(f"\n   Position #{i}:")
                print(f"      ID: {pos['id']}")
                print(f"      Symbol: {pos['symbol']}")
                print(f"      Side: {pos['side']}")
                print(f"      Entry Price: {pos['entry_price']}")
                print(f"      Quantity: {pos['quantity']}")
                print(f"      Stop Loss: {pos.get('stop_loss', 'None')}")
                print(f"      Take Profit: {pos.get('take_profit', 'None')}")
                print(f"      Opened At: {pos['opened_at']}")
                print(f"      Strategy: {pos.get('strategy', 'unknown')}")
                
                # Calculate age
                opened_at = datetime.fromisoformat(pos['opened_at'])
                age = datetime.now() - opened_at
                print(f"      Age: {age.days} days, {age.seconds // 3600} hours")
        else:
            print("   ✅ No open positions")
        print()
        
        # Get today's trades
        daily_trades = db.get_daily_trade_count()
        print(f"📈 TODAY'S ACTIVITY:")
        print("-" * 80)
        print(f"   Trades today: {daily_trades} / {config.max_daily_trades} limit")
        
        daily_pl = db.get_daily_profit_loss()
        print(f"   Daily P/L: ${daily_pl:.2f}")
        print()
        
        # Check limits
        print("🚦 LIMIT CHECKS:")
        print("-" * 80)
        
        from src.core.risk_manager import RiskManager
        risk_mgr = RiskManager(config, db)
        
        daily_limits_ok = risk_mgr.check_daily_limits()
        position_limits_ok = risk_mgr.check_position_limits()
        
        print(f"   Daily limits: {'✅ PASS' if daily_limits_ok else '❌ FAIL (limit reached)'}")
        print(f"   Position limits: {'✅ PASS' if position_limits_ok else '❌ FAIL (limit reached)'}")
        print()
        
        # Recent trades
        print("📋 RECENT TRADES (last 10):")
        print("-" * 80)
        cursor.execute("""
            SELECT symbol, side, price, quantity, timestamp, strategy 
            FROM trades 
            ORDER BY id DESC 
            LIMIT 10
        """)
        recent_trades = cursor.fetchall()
        
        if recent_trades:
            for i, trade in enumerate(recent_trades, 1):
                print(f"   {i}. {trade[1]} {trade[0]} @ ${trade[2]} x {trade[3]} - {trade[4]} ({trade[5]})")
        else:
            print("   No trades recorded")
        print()
        
        # Summary
        print("=" * 80)
        print(" DIAGNOSIS SUMMARY")
        print("=" * 80)
        
        if len(open_positions) == 0:
            print("✅ No open positions - bot should be able to open new positions")
        elif len(open_positions) >= config.max_open_positions:
            print(f"❌ PROBLEM: {len(open_positions)} open positions (>= limit of {config.max_open_positions})")
            print("   Bot CANNOT open new positions until some are closed")
            print("   OLDEST positions should be closed first!")
        else:
            print(f"⚠️  {len(open_positions)} open positions (limit: {config.max_open_positions})")
            print(f"   Bot can open {config.max_open_positions - len(open_positions)} more positions")
        
        if daily_trades >= config.max_daily_trades:
            print(f"❌ PROBLEM: {daily_trades} daily trades (>= limit of {config.max_daily_trades})")
            print("   Bot CANNOT trade more today")
        
        if not daily_limits_ok or not position_limits_ok:
            print("\n⚠️  LIMITS EXCEEDED - Bot should NOT be opening new positions!")
            print("   If bot is still opening positions, server is running OLD CODE")
        
        print()
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error during diagnostics: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    diagnose_positions()
