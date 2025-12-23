#!/bin/bash
# ============================================================
# Backup Script for Trading Bot
# ============================================================
# Backs up database, configuration, and logs
# Usage: ./backup.sh [--full] [--config-only]
# ============================================================

set -e

# Configuration
BACKUP_DIR="/var/lib/trading-bot/backups"
APP_DIR="/opt/trading-bot"
LOG_DIR="/var/log/trading-bot"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="trading-bot-backup-${TIMESTAMP}"
RETENTION_DAYS=30

# Parse arguments
FULL_BACKUP=false
CONFIG_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            FULL_BACKUP=true
            shift
            ;;
        --config-only)
            CONFIG_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--full] [--config-only]"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "TRADING BOT BACKUP - $(date)"
echo "============================================================"

# Create backup directory
mkdir -p ${BACKUP_DIR}/${BACKUP_NAME}

if [ "$CONFIG_ONLY" = true ]; then
    echo "[1/1] Backing up configuration..."
    cp ${APP_DIR}/.env ${BACKUP_DIR}/${BACKUP_NAME}/.env
    cp ${APP_DIR}/config.yaml ${BACKUP_DIR}/${BACKUP_NAME}/config.yaml
    
else
    echo "[1/4] Backing up database..."
    sudo -u postgres pg_dump trading_bot | gzip > ${BACKUP_DIR}/${BACKUP_NAME}/database.sql.gz
    
    echo "[2/4] Backing up configuration..."
    cp ${APP_DIR}/.env ${BACKUP_DIR}/${BACKUP_NAME}/.env
    cp ${APP_DIR}/config.yaml ${BACKUP_DIR}/${BACKUP_NAME}/config.yaml
    
    echo "[3/4] Backing up data directory..."
    if [ -d "${APP_DIR}/data" ]; then
        tar -czf ${BACKUP_DIR}/${BACKUP_NAME}/data.tar.gz -C ${APP_DIR} data
    fi
    
    if [ "$FULL_BACKUP" = true ]; then
        echo "[4/4] Backing up logs (full backup)..."
        tar -czf ${BACKUP_DIR}/${BACKUP_NAME}/logs.tar.gz -C ${LOG_DIR} .
    else
        echo "[4/4] Skipping logs (use --full for complete backup)"
    fi
fi

# Create compressed archive
cd ${BACKUP_DIR}
tar -czf ${BACKUP_NAME}.tar.gz ${BACKUP_NAME}/
rm -rf ${BACKUP_NAME}/

# Calculate size
BACKUP_SIZE=$(du -h ${BACKUP_NAME}.tar.gz | cut -f1)

echo ""
echo "✓ Backup complete: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})"
echo "  Location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Cleanup old backups
echo ""
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find ${BACKUP_DIR} -name "trading-bot-backup-*.tar.gz" -mtime +${RETENTION_DAYS} -delete
REMAINING=$(ls -1 ${BACKUP_DIR}/trading-bot-backup-*.tar.gz 2>/dev/null | wc -l)
echo "✓ Retained ${REMAINING} backup(s)"

echo ""
echo "============================================================"
echo "BACKUP SUMMARY"
echo "============================================================"
echo "Backup file: ${BACKUP_NAME}.tar.gz"
echo "Size: ${BACKUP_SIZE}"
echo "Location: ${BACKUP_DIR}"
echo ""
echo "To restore this backup, run:"
echo "  sudo ./restore.sh ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
