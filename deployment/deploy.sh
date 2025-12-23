#!/bin/bash
# ============================================================
# Trading Bot Deployment Script
# ============================================================
# This script sets up the trading bot on a fresh server
# Usage: sudo ./deploy.sh
# ============================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="trading-bot"
APP_USER="tradingbot"
APP_DIR="/opt/trading-bot"
LOG_DIR="/var/log/trading-bot"
DATA_DIR="/var/lib/trading-bot"
PYTHON_VERSION="3.11"

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}CRYPTO TRADING BOT - DEPLOYMENT SCRIPT${NC}"
echo -e "${GREEN}============================================================${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}" 
   exit 1
fi

echo -e "\n${YELLOW}[1/10] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

echo -e "\n${YELLOW}[2/10] Installing dependencies...${NC}"
apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    nginx \
    redis-server \
    postgresql \
    postgresql-contrib \
    git \
    curl \
    wget \
    supervisor \
    build-essential \
    libpq-dev

echo -e "\n${YELLOW}[3/10] Creating application user...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d $APP_DIR -m $APP_USER
    echo -e "${GREEN}✓ Created user: $APP_USER${NC}"
else
    echo -e "${GREEN}✓ User $APP_USER already exists${NC}"
fi

echo -e "\n${YELLOW}[4/10] Creating directories...${NC}"
mkdir -p $APP_DIR
mkdir -p $LOG_DIR
mkdir -p $DATA_DIR
mkdir -p $DATA_DIR/backups

chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER $LOG_DIR
chown -R $APP_USER:$APP_USER $DATA_DIR

echo -e "\n${YELLOW}[5/10] Setting up PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE USER trading_bot_user WITH PASSWORD 'change_this_password';" || echo "User might already exist"
sudo -u postgres psql -c "CREATE DATABASE trading_bot OWNER trading_bot_user;" || echo "Database might already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE trading_bot TO trading_bot_user;"

echo -e "\n${YELLOW}[6/10] Configuring Redis...${NC}"
systemctl enable redis-server
systemctl start redis-server

echo -e "\n${YELLOW}[7/10] Copying application files...${NC}"
# Assuming the script is run from the project directory
cp -r . $APP_DIR/
cd $APP_DIR

echo -e "\n${YELLOW}[8/10] Setting up Python virtual environment...${NC}"
sudo -u $APP_USER python${PYTHON_VERSION} -m venv venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt

echo -e "\n${YELLOW}[9/10] Creating environment configuration...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    sudo -u $APP_USER python3 scripts/setup_environment.py
    echo -e "${YELLOW}⚠️  Please edit $APP_DIR/.env with your API keys!${NC}"
fi

echo -e "\n${YELLOW}[10/10] Setting up systemd service...${NC}"
cp deployment/systemd/trading-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable trading-bot

echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}============================================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Edit configuration: sudo nano $APP_DIR/.env"
echo "2. Add your Binance Testnet API keys"
echo "3. Review config: sudo nano $APP_DIR/config.yaml"
echo "4. Start the service: sudo systemctl start trading-bot"
echo "5. Check status: sudo systemctl status trading-bot"
echo "6. View logs: sudo journalctl -u trading-bot -f"
echo ""
echo -e "${YELLOW}Monitoring:${NC}"
echo "• Health check: curl http://localhost:8001/metrics"
echo "• Logs: tail -f $LOG_DIR/bot.log"
echo ""
echo -e "${RED}⚠️  IMPORTANT:${NC}"
echo "• This is set up for TESTNET trading only"
echo "• NEVER use production API keys without thorough testing"
echo "• Keep your .env file secure"
echo "• Enable firewall: ufw enable && ufw allow 22,80,443/tcp"
