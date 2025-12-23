# Deployment Guide for Life is a Joke

This guide provides detailed instructions for deploying the Life is a Joke application to various server environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Methods](#deployment-methods)
  - [Docker Deployment](#docker-deployment)
  - [Manual Deployment with Gunicorn](#manual-deployment-with-gunicorn)
  - [Systemd Service Deployment](#systemd-service-deployment)
- [Nginx Configuration](#nginx-configuration)
- [SSL/HTTPS Setup](#sslhttps-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Linux server (Ubuntu 20.04+ or similar)
- Python 3.11 or higher
- Docker and Docker Compose (for Docker deployment)
- Root or sudo access

## Deployment Methods

### Docker Deployment

Docker provides the easiest and most reliable deployment method.

1. **Install Docker and Docker Compose**
   ```bash
   # Update package list
   sudo apt update
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo apt install docker-compose-plugin
   
   # Add your user to docker group (optional)
   sudo usermod -aG docker $USER
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
   cd life_is_a_joke
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if you need to change PORT or other settings
   nano .env
   ```

4. **Build and start the application**
   ```bash
   docker compose up -d --build
   ```

5. **Verify the deployment**
   ```bash
   docker compose ps
   docker compose logs -f
   curl http://localhost:5000/health
   ```

6. **Stop the application**
   ```bash
   docker compose down
   ```

### Manual Deployment with Gunicorn

For environments where Docker is not available or preferred.

1. **Install Python and dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Clone the repository**
   ```bash
   cd /var/www
   sudo git clone https://github.com/anthony87b7f58e-coder/life_is_a_joke.git
   cd life_is_a_joke
   ```

3. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit as needed
   nano .env
   ```

6. **Run with start script**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   Or run Gunicorn directly:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 60 app:app
   ```

### Systemd Service Deployment

For production environments requiring automatic startup and process management.

1. **Complete manual deployment steps 1-5** from above

2. **Set correct ownership**
   ```bash
   sudo chown -R www-data:www-data /var/www/life_is_a_joke
   ```

3. **Copy systemd service file**
   ```bash
   sudo cp life_is_a_joke.service /etc/systemd/system/
   ```

4. **Edit service file if needed**
   ```bash
   sudo nano /etc/systemd/system/life_is_a_joke.service
   ```
   
   Update paths if you installed to a different directory than `/var/www/life_is_a_joke`

5. **Enable and start the service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable life_is_a_joke
   sudo systemctl start life_is_a_joke
   ```

6. **Check service status**
   ```bash
   sudo systemctl status life_is_a_joke
   ```

7. **View logs**
   ```bash
   sudo journalctl -u life_is_a_joke -f
   ```

## Nginx Configuration

Use Nginx as a reverse proxy for better performance and SSL termination.

1. **Install Nginx**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. **Create Nginx configuration**
   ```bash
   sudo nano /etc/nginx/sites-available/life_is_a_joke
   ```
   
   Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           
           # Timeout settings
           proxy_connect_timeout 60s;
           proxy_send_timeout 60s;
           proxy_read_timeout 60s;
       }
       
       # Health check endpoint (optional)
       location /health {
           proxy_pass http://127.0.0.1:5000/health;
           access_log off;
       }
   }
   ```

3. **Enable the site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/life_is_a_joke /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## SSL/HTTPS Setup

Use Let's Encrypt for free SSL certificates.

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain SSL certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

3. **Auto-renewal is configured automatically**
   Test renewal:
   ```bash
   sudo certbot renew --dry-run
   ```

## Monitoring and Logging

### Application Logs

**With systemd:**
```bash
sudo journalctl -u life_is_a_joke -f
```

**With Docker:**
```bash
docker compose logs -f
```

### Health Checks

The application provides a health check endpoint at `/health`:

```bash
curl http://localhost:5000/health
```

Returns:
```json
{
  "status": "healthy",
  "service": "life_is_a_joke"
}
```

### Monitoring with cron

Create a simple monitoring script:

```bash
#!/bin/bash
STATUS=$(curl -s http://localhost:5000/health | grep -o "healthy")
if [ "$STATUS" != "healthy" ]; then
    echo "Service is down!" | mail -s "Life is a Joke Alert" admin@example.com
    sudo systemctl restart life_is_a_joke
fi
```

Add to crontab:
```bash
*/5 * * * * /path/to/monitor.sh
```

## Troubleshooting

### Service won't start

1. **Check logs:**
   ```bash
   sudo journalctl -u life_is_a_joke -n 50
   ```

2. **Verify Python path:**
   ```bash
   /var/www/life_is_a_joke/venv/bin/python --version
   ```

3. **Test manually:**
   ```bash
   cd /var/www/life_is_a_joke
   source venv/bin/activate
   python app.py
   ```

### Port already in use

```bash
# Find what's using the port
sudo lsof -i :5000

# Kill the process if needed
sudo kill -9 <PID>
```

### Permission issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/life_is_a_joke

# Fix permissions
sudo chmod -R 755 /var/www/life_is_a_joke
```

### Docker build fails

If experiencing SSL certificate issues during Docker build:

1. Check your network proxy settings
2. Try building with `--network=host` flag
3. Consider using pre-built images or different base image

### Application returns 502 Bad Gateway

1. Verify the application is running:
   ```bash
   curl http://localhost:5000/health
   ```

2. Check Nginx error logs:
   ```bash
   sudo tail -f /var/nginx/error.log
   ```

3. Verify Nginx configuration:
   ```bash
   sudo nginx -t
   ```

## Performance Tuning

### Gunicorn Workers

Recommended formula: `(2 x CPU cores) + 1`

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### Nginx Caching

Add to Nginx configuration for static assets:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Backup and Recovery

### Backup

The application is stateless. To backup:

```bash
# Backup the code
tar -czf life_is_a_joke_backup.tar.gz /var/www/life_is_a_joke

# Backup environment configuration
cp /var/www/life_is_a_joke/.env /path/to/backup/
```

### Recovery

```bash
# Extract backup
tar -xzf life_is_a_joke_backup.tar.gz -C /var/www/

# Restore environment
cp /path/to/backup/.env /var/www/life_is_a_joke/

# Restart service
sudo systemctl restart life_is_a_joke
```

## Security Considerations

1. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Configure firewall:**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **Limit application access:**
   - Run application as non-root user (www-data)
   - Use Nginx to handle external traffic
   - Keep application bound to localhost only

4. **Regular security updates:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## Support

For issues or questions:
- Open an issue on GitHub
- Check application logs
- Review this deployment guide

---

Last updated: December 2025
