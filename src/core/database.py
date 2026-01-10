"""
Database Manager
Handles all database operations for trading history, positions, and analytics
"""

import os
import logging
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class Database:
    """Database manager for SQLite"""
    
    def __init__(self, config):
        """Initialize database connection"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if config.db_type == 'sqlite':
            # Ensure directory exists
            db_path = Path(config.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database with proper settings for persistence
            self.conn = sqlite3.connect(
                config.db_path, 
                check_same_thread=False,
                isolation_level=None  # Autocommit mode for immediate persistence
            )
            self.conn.row_factory = sqlite3.Row
            
            # Enable WAL mode for better concurrency and persistence
            self.conn.execute('PRAGMA journal_mode=WAL')
            # Ensure data is written to disk immediately
            self.conn.execute('PRAGMA synchronous=FULL')
            
            self.logger.info(f"Connected to SQLite database: {config.db_path}")
        else:
            raise NotImplementedError(f"Database type {config.db_type} not implemented")
        
        # Initialize schema
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                order_id TEXT UNIQUE,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                commission REAL,
                commission_asset TEXT,
                profit_loss REAL,
                strategy TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed'
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                current_price REAL,
                profit_loss REAL,
                status TEXT DEFAULT 'open',
                opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME,
                strategy TEXT
            )
        ''')
        
        # Daily stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_trades INTEGER DEFAULT 0,
                profitable_trades INTEGER DEFAULT 0,
                total_profit_loss REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        self.logger.info("Database schema initialized")
    
    def record_trade(self, trade_data: Dict) -> int:
        """Record a trade"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, side, order_id, price, quantity, commission, 
                              commission_asset, profit_loss, strategy, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['symbol'],
            trade_data['side'],
            trade_data.get('order_id'),
            trade_data['price'],
            trade_data['quantity'],
            trade_data.get('commission', 0),
            trade_data.get('commission_asset', 'USDT'),
            trade_data.get('profit_loss', 0),
            trade_data.get('strategy', 'unknown'),
            trade_data.get('status', 'completed')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def create_position(self, position_data: Dict) -> int:
        """Create a new position"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO positions (symbol, side, entry_price, quantity, stop_loss, 
                                 take_profit, strategy, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
        ''', (
            position_data['symbol'],
            position_data['side'],
            position_data['entry_price'],
            position_data['quantity'],
            position_data.get('stop_loss'),
            position_data.get('take_profit'),
            position_data.get('strategy', 'unknown')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_position(self, position_id: int, **kwargs):
        """Update a position"""
        updates = []
        values = []
        
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            values.append(value)
        
        values.append(position_id)
        
        cursor = self.conn.cursor()
        cursor.execute(f'''
            UPDATE positions 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', values)
        self.conn.commit()
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE status = 'open'")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_daily_trade_count(self) -> int:
        """Get number of trades today"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM trades 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        return cursor.fetchone()[0]
    
    def get_daily_profit_loss(self) -> float:
        """Get total P/L for today"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(profit_loss), 0) as total
            FROM trades 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        return cursor.fetchone()[0]
    
    def health_check(self) -> bool:
        """Check database health"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            # Ensure all pending transactions are committed
            try:
                self.conn.commit()
            except Exception:
                pass  # In autocommit mode, this might raise
            
            self.conn.close()
            self.logger.info("Database connection closed")
