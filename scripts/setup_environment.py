#!/usr/bin/env python3
"""
Environment setup script
Creates .env file with all required variables
"""
import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file with all required environment variables"""
    
    env_template = """# ============================================================
# CRYPTO TRADING BOT - ENVIRONMENT CONFIGURATION
# ============================================================
# IMPORTANT: Never commit this file to version control!
# Get Binance Testnet API keys from: https://testnet.binance.vision/
# ============================================================

# ============================================================
# ENVIRONMENT
# ============================================================
ENVIRONMENT=paper  # Options: paper, test, production
LOG_LEVEL=INFO     # Options: DEBUG, INFO, WARNING, ERROR
TIMEZONE=UTC

# ============================================================
# EXCHANGE API CREDENTIALS
# ============================================================
# Binance Testnet (for paper trading)
BINANCE_API_KEY=your_binance_testnet_api_key_here
BINANCE_API_SECRET=your_binance_testnet_secret_here

# Binance Production (ONLY use after thorough testing!)
# BINANCE_PROD_API_KEY=
# BINANCE_PROD_API_SECRET=

# Other exchanges (optional)
# BYBIT_API_KEY=
# BYBIT_API_SECRET=

# ============================================================
# DATABASE
# ============================================================
# Redis (for caching and task queue)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# PostgreSQL (for persistent storage)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=trading_bot
POSTGRES_USER=trading_bot_user
POSTGRES_PASSWORD=change_this_password

# Database URLs (auto-generated from above, or set manually)
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# ============================================================
# MONITORING & ALERTING
# ============================================================
# Prometheus
PROMETHEUS_PORT=8001
PROMETHEUS_ENABLED=true

# Grafana
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=change_this_password

# ============================================================
# NOTIFICATIONS
# ============================================================
# Telegram Bot
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_TO_EMAILS=admin@example.com

# ============================================================
# SECURITY
# ============================================================
# Secret key for encryption (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=generate_your_secret_key_here

# API authentication (for web dashboard)
API_USERNAME=admin
API_PASSWORD=change_this_password

# JWT settings
JWT_SECRET_KEY=generate_your_jwt_secret_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ============================================================
# TRADING SETTINGS
# ============================================================
# Maximum position size (percentage of portfolio)
MAX_POSITION_PCT=10.0

# Maximum portfolio risk (percentage)
MAX_PORTFOLIO_RISK=20.0

# Stop loss percentage
STOP_LOSS_PCT=3.0

# Take profit percentage
TAKE_PROFIT_PCT=6.0

# Minimum 24h volume (USD)
MIN_24H_VOLUME=1000000

# ============================================================
# SYSTEM SETTINGS
# ============================================================
# Worker settings
MAX_WORKERS=4
THREAD_POOL_SIZE=10

# Memory limit (MB)
MEMORY_LIMIT_MB=1024

# Logging
LOG_FILE=/var/log/trading_bot/bot.log
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=5

# Data directory
DATA_DIR=./data
BACKUP_DIR=./backups

# ============================================================
# OPTIONAL SERVICES
# ============================================================
# Sentry (error tracking)
SENTRY_DSN=

# Analytics
ANALYTICS_ENABLED=false

# Debug mode (NEVER use in production!)
DEBUG=false

# ============================================================
# NOTES
# ============================================================
# 1. Replace all "your_*_here" and "change_this_*" values
# 2. Generate secret keys using: python -c "import secrets; print(secrets.token_hex(32))"
# 3. For production, use strong passwords and enable all security features
# 4. Keep this file secure and never commit it to version control
# 5. For multiple environments, create .env.production, .env.staging, etc.
# ============================================================
"""
    
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted. Existing .env file not modified.")
            return False
    
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env file")
    print("\n📝 Next steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Generate secret keys: python -c \"import secrets; print(secrets.token_hex(32))\"")
    print("3. For testnet: Get keys from https://testnet.binance.vision/")
    print("4. Never commit .env to version control!")
    
    return True


def check_gitignore():
    """Ensure .env is in .gitignore"""
    gitignore_file = Path('.gitignore')
    
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            content = f.read()
        
        if '.env' not in content:
            with open(gitignore_file, 'a') as f:
                f.write('\n# Environment variables\n.env\n.env.*\n')
            print("✅ Added .env to .gitignore")
    else:
        with open(gitignore_file, 'w') as f:
            f.write('# Environment variables\n.env\n.env.*\n')
        print("✅ Created .gitignore with .env")


def create_env_example():
    """Create .env.example without sensitive data"""
    example_content = """# Example environment configuration
# Copy this to .env and fill in your actual values

ENVIRONMENT=paper
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
REDIS_URL=redis://localhost:6379/0
POSTGRES_HOST=localhost
POSTGRES_DB=trading_bot
SECRET_KEY=generate_with_python_secrets
"""
    
    with open('.env.example', 'w') as f:
        f.write(example_content)
    
    print("✅ Created .env.example")


def main():
    """Main setup function"""
    print("=" * 60)
    print("CRYPTO TRADING BOT - ENVIRONMENT SETUP")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not Path('src').exists():
        print("❌ Error: Must run from project root directory")
        print("   Expected to find 'src' directory")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check/update .gitignore
    check_gitignore()
    
    # Create .env.example
    create_env_example()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("\n⚠️  IMPORTANT SECURITY REMINDERS:")
    print("1. Edit .env and replace all placeholder values")
    print("2. NEVER commit .env to version control")
    print("3. Use testnet keys for development/testing")
    print("4. Use strong passwords for production")
    print("5. Keep API keys with minimal permissions (no withdrawal)")


if __name__ == '__main__':
    main()
