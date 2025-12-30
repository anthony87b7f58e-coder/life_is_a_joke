# Trading Bot - Deployment Infrastructure

This repository contains all the necessary deployment infrastructure files for deploying the trading bot to production.

## 📁 File Structure

```
.
├── .env.template                        # Environment variables template
├── deployment/
│   ├── deploy.sh                        # Main automated deployment script
│   ├── logrotate/
│   │   └── trading-bot                  # Log rotation configuration
│   ├── nginx/
│   │   └── trading-bot.conf             # Nginx reverse proxy configuration
│   ├── scripts/
│   │   ├── backup.sh                    # Database and configuration backup
│   │   ├── restore.sh                   # Restore from backup archive
│   │   ├── security_hardening.sh        # Security hardening script
│   │   ├── setup_cron.sh                # Automated backup scheduling
│   │   └── setup_firewall.sh            # UFW firewall configuration
│   └── systemd/
│       └── trading-bot.service          # Systemd service definition
└── scripts/
    ├── health_check.py                  # System health verification
    ├── setup_environment.py             # Interactive environment configuration
    └── test_connectivity.py             # Binance API connectivity test
```

## 🚀 Quick Start

### Prerequisites

- Ubuntu 20.04 LTS or newer (or Debian-based system)
- Python 3.8 or higher
- Root or sudo access
- Git installed

### 1. Clone the Repository

```bash
git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
cd life_is_a_joke
```

### 2. Run the Automated Deployment

```bash
sudo bash deployment/deploy.sh
```

This script will:
- Check system requirements
- Create application user and directories
- Install system dependencies
- Setup Python virtual environment
- Install Python dependencies
- Deploy application files
- Configure environment
- Install systemd service
- Setup Nginx reverse proxy
- Configure log rotation
- Setup firewall
- Apply security hardening
- Setup automated backups

### 3. Configure Environment

After deployment, edit your configuration:

```bash
sudo nano /etc/trading-bot/.env
```

Or use the interactive setup:

```bash
sudo python3 scripts/setup_environment.py
```

### 4. Start the Service

```bash
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

## 📋 Detailed Component Documentation

### Environment Configuration

The `.env.template` file contains all available configuration options:

- **Application Settings**: Name, environment, debug mode, logging
- **Binance API**: API credentials, testnet toggle
- **Database**: SQLite or PostgreSQL configuration
- **Trading Settings**: Symbols, position sizes, risk management
- **Notifications**: Telegram and email alerts
- **Security**: IP whitelisting, rate limiting

Copy and customize:
```bash
cp .env.template /etc/trading-bot/.env
# Edit with your values
sudo nano /etc/trading-bot/.env
```

### Health Checks

Run comprehensive health checks:

```bash
python3 scripts/health_check.py
```

This checks:
- System resources (CPU, memory, disk)
- Directory structure and permissions
- Configuration files
- Database connectivity
- Log files
- Running processes
- Network connectivity
- Backup status

### Connectivity Testing

Test Binance API connectivity:

```bash
python3 scripts/test_connectivity.py
```

Tests:
- Basic internet connectivity
- Binance public API endpoints
- Authenticated API endpoints
- API rate limits

### Backup and Restore

#### Create a Backup

```bash
sudo bash deployment/scripts/backup.sh
```

Backups include:
- Database
- Configuration files
- Application data
- Logs
- Metadata

#### Restore from Backup

```bash
# Interactive selection
sudo bash deployment/scripts/restore.sh

# Specify backup file
sudo bash deployment/scripts/restore.sh /var/backups/trading-bot/trading-bot_backup_20231223_120000.tar.gz
```

#### Automated Backups

Setup automated backups with cron:

```bash
sudo bash deployment/scripts/setup_cron.sh
```

Choose from:
- Daily at 2:00 AM (default)
- Every 6 hours
- Weekly on Sunday
- Monthly on the 1st
- Custom schedule

### Security

#### Firewall Configuration

Setup UFW firewall:

```bash
sudo bash deployment/scripts/setup_firewall.sh
```

This configures:
- Default deny incoming, allow outgoing
- SSH access with rate limiting
- HTTP/HTTPS (if web enabled)
- IP whitelisting
- Application-specific rules

#### Security Hardening

Apply security best practices:

```bash
sudo bash deployment/scripts/security_hardening.sh
```

Includes:
- Automatic security updates
- SSH hardening
- fail2ban configuration
- File permission securing
- Kernel parameter hardening
- Audit logging
- System limits configuration

### Service Management

```bash
# Start the service
sudo systemctl start trading-bot

# Stop the service
sudo systemctl stop trading-bot

# Restart the service
sudo systemctl restart trading-bot

# Check status
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f

# Enable auto-start on boot
sudo systemctl enable trading-bot
```

### Nginx Reverse Proxy

The Nginx configuration provides:
- Reverse proxy to the trading bot web interface
- SSL/TLS support (configure certificates)
- Security headers
- Rate limiting
- Health check endpoint
- Metrics endpoint (restricted to localhost)

Edit the configuration:
```bash
sudo nano /etc/nginx/sites-available/trading-bot
```

Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Log Rotation

Logs are automatically rotated based on the configuration in `/etc/logrotate.d/trading-bot`.

Test log rotation:
```bash
sudo logrotate -f /etc/logrotate.d/trading-bot
```

## 🔍 Monitoring and Maintenance

### Check System Health

```bash
python3 scripts/health_check.py
```

### View Logs

```bash
# Application logs
sudo tail -f /var/log/trading-bot/trading-bot.log

# Service logs
sudo journalctl -u trading-bot -f

# Nginx logs
sudo tail -f /var/log/nginx/trading-bot-access.log
sudo tail -f /var/log/nginx/trading-bot-error.log
```

### Check Backups

```bash
ls -lh /var/backups/trading-bot/
```

### Monitor Service

```bash
sudo systemctl status trading-bot
```

## 🛡️ Security Best Practices

1. **API Keys**: Store securely in `/etc/trading-bot/.env` with 600 permissions
2. **Firewall**: Enable UFW and configure rules
3. **SSH**: Use key-based authentication, disable root login
4. **Updates**: Enable automatic security updates
5. **Backups**: Schedule regular automated backups
6. **Monitoring**: Setup alerts for service failures
7. **SSL**: Configure SSL/TLS certificates for web interface
8. **Access**: Limit access with IP whitelisting

## 📊 Directory Locations

- **Application**: `/opt/trading-bot`
- **Configuration**: `/etc/trading-bot`
- **Data**: `/var/lib/trading-bot`
- **Logs**: `/var/log/trading-bot`
- **Backups**: `/var/backups/trading-bot`

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status trading-bot

# Check logs
sudo journalctl -u trading-bot -n 50

# Verify configuration
python3 /opt/trading-bot/scripts/health_check.py
```

### API Connection Issues

```bash
# Test connectivity
python3 scripts/test_connectivity.py

# Check firewall
sudo ufw status

# Verify environment
cat /etc/trading-bot/.env | grep BINANCE
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R tradingbot:tradingbot /var/lib/trading-bot
sudo chown -R tradingbot:tradingbot /var/log/trading-bot

# Fix permissions
sudo chmod 750 /etc/trading-bot
sudo chmod 600 /etc/trading-bot/.env
```

## 📝 Notes

- All scripts include error handling and logging
- Backup before making changes to production
- Test in staging environment first
- Review security settings for your use case
- Keep system and dependencies updated
- Monitor resource usage and adjust limits as needed

## 📄 License

This deployment infrastructure is provided as-is for the trading bot application.

## 🤝 Support

For issues or questions:
1. Check the logs: `sudo journalctl -u trading-bot -f`
2. Run health checks: `python3 scripts/health_check.py`
3. Review the troubleshooting section above
