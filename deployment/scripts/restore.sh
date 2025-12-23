#!/bin/bash
# ============================================================
# Restore Script for Trading Bot
# ============================================================
# Restores database, configuration, and data from backup
# Usage: sudo ./restore.sh <backup_file.tar.gz>
# ============================================================

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Error: No backup file specified"
    echo "Usage: $0 <backup_file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /var/lib/trading-bot/backups/trading-bot-backup-*.tar.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"
APP_DIR="/opt/trading-bot"
TEMP_DIR="/tmp/trading-bot-restore-$$"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "============================================================"
echo "TRADING BOT RESTORE - $(date)"
echo "============================================================"
echo "Backup file: $BACKUP_FILE"
echo ""
echo "⚠️  WARNING: This will OVERWRITE current configuration!"
read -p "Continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Stop the service
echo ""
echo "[1/5] Stopping trading bot service..."
systemctl stop trading-bot || echo "Service not running"

# Extract backup
echo "[2/5] Extracting backup..."
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_FILE -C $TEMP_DIR

# Find the backup directory name
BACKUP_DIR=$(ls -d $TEMP_DIR/trading-bot-backup-* | head -n 1)

# Restore database
echo "[3/5] Restoring database..."
if [ -f "$BACKUP_DIR/database.sql.gz" ]; then
    sudo -u postgres dropdb --if-exists trading_bot
    sudo -u postgres createdb trading_bot -O trading_bot_user
    gunzip < $BACKUP_DIR/database.sql.gz | sudo -u postgres psql trading_bot
    echo "✓ Database restored"
else
    echo "⚠️  No database backup found, skipping"
fi

# Restore configuration
echo "[4/5] Restoring configuration..."
if [ -f "$BACKUP_DIR/.env" ]; then
    cp $BACKUP_DIR/.env $APP_DIR/.env
    echo "✓ .env restored"
fi

if [ -f "$BACKUP_DIR/config.yaml" ]; then
    cp $BACKUP_DIR/config.yaml $APP_DIR/config.yaml
    echo "✓ config.yaml restored"
fi

# Restore data directory
echo "[5/5] Restoring data..."
if [ -f "$BACKUP_DIR/data.tar.gz" ]; then
    tar -xzf $BACKUP_DIR/data.tar.gz -C $APP_DIR
    chown -R tradingbot:tradingbot $APP_DIR/data
    echo "✓ Data directory restored"
else
    echo "⚠️  No data backup found, skipping"
fi

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo "============================================================"
echo "RESTORE COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Review configuration: sudo nano $APP_DIR/.env"
echo "2. Start the service: sudo systemctl start trading-bot"
echo "3. Check status: sudo systemctl status trading-bot"
echo "4. Monitor logs: sudo journalctl -u trading-bot -f"
