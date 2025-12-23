"""
Logging Utility
Configures application logging to file and console
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = None) -> logging.Logger:
    """
    Setup application logger
    
    Args:
        name: Logger name (default: root logger)
    
    Returns:
        Configured logger instance
    """
    # Get configuration from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_dir = os.getenv('LOG_DIR', '/var/log/trading-bot')
    log_file = os.getenv('LOG_FILE', 'trading-bot.log')
    log_to_file = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
    log_to_console = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'
    log_max_size = int(os.getenv('LOG_MAX_SIZE', '104857600'))  # 100MB
    log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', '10'))
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level, logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_dir)
            if not log_path.exists():
                # Try to create in current directory if system path fails
                log_path = Path('./logs')
                log_path.mkdir(exist_ok=True)
                log_dir = str(log_path)
            
            log_file_path = os.path.join(log_dir, log_file)
            
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=log_max_size,
                backupCount=log_backup_count
            )
            file_handler.setLevel(getattr(logging, log_level, logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            # If file logging fails, just log to console
            logger.warning(f"Could not setup file logging: {e}")
    
    return logger
