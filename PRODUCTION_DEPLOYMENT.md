# Production Deployment Guide

## Overview

This guide covers deploying the crypto trading bot to **production** across AWS EC2, Hetzner, and local nodes with **99.99% uptime**, automatic failover, and complete monitoring.

---

## 1. Pre-Deployment Checklist

- [ ] API keys in AWS Secrets Manager (Binance, ByBit, 1inch, etc.)
- [ ] Kubernetes cluster ready (3+ nodes)
- [ ] SSL certificates for HTTPS (Let's Encrypt)
- [ ] Monitoring stack (Prometheus + Grafana) deployed
- [ ] Backup S3 bucket configured
- [ ] Telegram bot token for alerts
- [ ] Paper trading validated for 2+ weeks
- [ ] Position size limits set (max 1-2% per trade)

---

## 2. Architecture: Multi-Node Deployment

```
┌──────────────────────────────────────────────────────────────────┐
│                       Load Balancer (NLB)                        │
│                         Port 8000, 8001                          │
└──────────────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┐
        │                     │              │
    ┌───▼────┐           ┌───▼────┐    ┌───▼────┐
    │AWS EC2 │           │Hetzner │    │ Local  │
    │Primary │  (Active) │ Backup │    │ Host   │
    │Node    │───────────│ Node   │    │(Warm)  │
    │Port 22 │(Heartbeat)│        │    │        │
    └───┬────┘           └────────┘    └────────┘
        │
    ┌───▼──────────────────────────────────┐
    │   Redis Cluster (3 replicas)         │
    │   - Data persistence (RDB + AOF)     │
    │   - Sentinel for auto-failover       │
    └──────────────────────────────────────┘
        │
    ┌───▼──────────────────────────────────┐
    │   PostgreSQL (Transaction Log)        │
    │   - WAL enabled for durability        │
    │   - Replication to hot-standby        │
    └──────────────────────────────────────┘
```

---

## 3. Node Setup (AWS EC2 Primary)

### 3.1 Launch Instance

```bash
# 1. Create EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.xlarge \
  --key-name my-key-pair \
  --security-groups crypto-bot-sg \
  --region us-east-1

# 2. SSH into instance
ssh -i my-key-pair.pem ec2-user@ec2-instance-ip

# 3. Update system
sudo yum update -y
sudo yum install -y docker git docker-compose-v2
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

### 3.2 Install Bot & Dependencies

```bash
# Clone bot repository
git clone https://github.com/yourorg/crypto-bot.git
cd crypto-bot

# Build Docker image
docker build -t crypto-bot:latest .

# Pull dependencies
docker pull redis:7
docker pull postgres:15
```

### 3.3 Set Environment Secrets

```bash
# 1. Fetch API keys from AWS Secrets Manager
export BINANCE_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id bot/binance_api_key \
  --query SecretString --output text)

export BINANCE_SECRET=$(aws secretsmanager get-secret-value \
  --secret-id bot/binance_secret \
  --query SecretString --output text)

# 2. Create .env file (NOT committed to git)
cat > .env << EOF
BINANCE_API_KEY=${BINANCE_API_KEY}
BINANCE_SECRET=${BINANCE_SECRET}
REDIS_URL=redis://redis:6379/0
POSTGRES_URL=postgresql://bot:password@postgres:5432/trading_db
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF
```

### 3.4 Configure & Start Services (Docker Compose)

```bash
# Override docker-compose for production
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    ports:
      - '6379:6379'
    healthcheck:
      test: redis-cli ping
      interval: 10s
      timeout: 3s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: bot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: trading_db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - '5432:5432'
    healthcheck:
      test: pg_isready -U bot
      interval: 10s
      timeout: 3s
      retries: 3

  worker:
    build: .
    command: celery -A src.celery_app worker --loglevel=info --concurrency=4
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
    restart: always

  bot-api:
    build: .
    command: python -m src.main
    depends_on:
      - redis
      - postgres
    environment:
      - REDIS_URL=redis://redis:6379/0
      - POSTGRES_URL=postgresql://bot:${DB_PASSWORD}@postgres:5432/trading_db
      - ENVIRONMENT=production
    ports:
      - '8000:8000'
      - '8001:8001'  # Prometheus metrics
    restart: always
    healthcheck:
      test: curl -f http://localhost:8001/metrics || exit 1
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis-data:
  postgres-data:
EOF

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Verify services
docker-compose ps
docker logs crypto-bot-api
```

---

## 4. Multi-Node Failover Setup

### 4.1 Deploy Backup Node (Hetzner)

```bash
# Repeat section 3 (SSH, Docker, etc.)

# Modify hostname for clarity
sudo hostnamectl set-hostname crypto-bot-backup

# Configure as Backup (read-only initially)
export PRIMARY_NODE_IP=10.0.0.100
echo "PRIMARY_NODE_IP=${PRIMARY_NODE_IP}" >> .env
```

### 4.2 Redis Sentinel for Auto-Failover

```bash
# Create sentinel config on primary
cat > redis-sentinel.conf << 'EOF'
port 26379
sentinel monitor master-redis 10.0.0.100 6379 2
sentinel down-after-milliseconds master-redis 5000
sentinel parallel-syncs master-redis 1
sentinel failover-timeout master-redis 180000
EOF

# Start Sentinel
docker run -d --name redis-sentinel \
  -p 26379:26379 \
  -v $(pwd)/redis-sentinel.conf:/etc/sentinel.conf \
  redis:7 redis-sentinel /etc/sentinel.conf
```

### 4.3 Health Monitor Integration

Update `src/health_monitor.py`:

```python
import asyncio
from prometheus_client import start_http_server, Gauge, Counter
import socket

class HealthMonitor:
    def __init__(self, cfg):
        self.cfg = cfg
        self.node_name = socket.gethostname()
        self.heartbeat = Gauge('bot_heartbeat_ts', 'Heartbeat timestamp', ['node'])
        self.latency_ms = Gauge('bot_latency_ms', 'API latency', ['node', 'target'])
        self.failover_counter = Counter('failover_events', 'Failover count', ['from_node', 'to_node'])
    
    async def start(self):
        start_http_server(8001)
        asyncio.create_task(self._monitor_health())
    
    async def _monitor_health(self):
        import time
        while True:
            self.heartbeat.labels(node=self.node_name).set(time.time())
            
            # Measure latency to primary redis
            latency = await self._measure_latency('redis:6379')
            self.latency_ms.labels(node=self.node_name, target='redis').set(latency)
            
            # If latency > 500ms, trigger failover
            if latency > 500:
                await self._trigger_failover()
            
            await asyncio.sleep(10)
    
    async def _measure_latency(self, host: str) -> float:
        import time
        start = time.time()
        try:
            # Ping test
            proc = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', '1', host,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            return (time.time() - start) * 1000
        except:
            return 9999.0
    
    async def _trigger_failover(self):
        """Promote backup node"""
        logger.critical('PRIMARY FAILED! Promoting backup node...')
        # Sentinel should auto-promote, but we can force:
        # sentinel failover master-redis
        self.failover_counter.labels(from_node='primary', to_node='backup').inc()
```

---

## 5. Kubernetes Deployment (Recommended for Scale)

### 5.1 Create Namespace & Secrets

```bash
# Create namespace
kubectl create namespace crypto-bot

# Create secrets
kubectl create secret generic bot-secrets \
  --from-literal=binance_api_key=${BINANCE_API_KEY} \
  --from-literal=binance_secret=${BINANCE_SECRET} \
  --from-literal=db_password=${DB_PASSWORD} \
  -n crypto-bot

# Verify
kubectl get secrets -n crypto-bot
```

### 5.2 Deploy with Kubernetes

```bash
# Apply deployment manifests
kubectl apply -f k8s/deployment.yaml -n crypto-bot

# Verify pods
kubectl get pods -n crypto-bot

# Logs
kubectl logs -f deployment/bot-api -n crypto-bot

# Port forward for local access
kubectl port-forward svc/bot-svc 8000:8000 -n crypto-bot
```

### 5.3 Horizontal Pod Autoscaling

```yaml
# Add to k8s/deployment.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bot-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Apply:
```bash
kubectl apply -f k8s/hpa.yaml -n crypto-bot
```

---

## 6. Monitoring & Observability

### 6.1 Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bot-metrics'
    static_configs:
      - targets: ['localhost:8001']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']  # postgres_exporter
```

Start Prometheus:
```bash
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 6.2 Grafana Dashboard

```bash
# Start Grafana
docker run -d -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana

# Access at http://localhost:3000

# Add Prometheus as data source:
# URL: http://prometheus:9090

# Import dashboard JSON for:
# - Equity curve
# - PnL heatmap
# - Latency/uptime
# - Trade volume
```

### 6.3 Alert Rules

```yaml
# alerts.yml
groups:
  - name: bot_alerts
    rules:
      - alert: HighLatencyToExchange
        expr: bot_latency_ms > 500
        for: 2m
        annotations:
          summary: "High latency to exchange"
      
      - alert: FailoverTriggered
        expr: increase(failover_events_total[1h]) > 0
        annotations:
          summary: "Failover event occurred"
      
      - alert: LargeDrawdown
        expr: bot_drawdown_percent > 5
        annotations:
          summary: "Drawdown exceeded 5%"
```

---

## 7. Logging & Debugging

### 7.1 Centralized Logging (ELK Stack)

```bash
# Start Elasticsearch
docker run -d -p 9200:9200 \
  -e discovery.type=single-node \
  docker.elastic.co/elasticsearch/elasticsearch:8.0.0

# Start Kibana
docker run -d -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  docker.elastic.co/kibana/kibana:8.0.0

# Configure bot to ship logs to Elasticsearch
# (Add to src/main.py or logging.conf)
```

### 7.2 Debug Logs

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
docker-compose -f docker-compose.prod.yml up -d

# Stream logs
docker logs -f bot-api

# Save to file
docker logs bot-api > /var/log/bot-api.log 2>&1
```

---

## 8. Backup & Disaster Recovery

### 8.1 Database Backup

```bash
#!/bin/bash
# backup_db.sh (run daily via cron)

BACKUP_DIR="/data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup Redis
redis-cli BGSAVE
cp /data/dump.rdb "${BACKUP_DIR}/redis_${TIMESTAMP}.rdb"

# Backup PostgreSQL
pg_dump trading_db > "${BACKUP_DIR}/postgres_${TIMESTAMP}.sql"

# Upload to S3
aws s3 cp "${BACKUP_DIR}/" s3://bot-backups/ --recursive

# Keep only last 30 days
find "${BACKUP_DIR}" -mtime +30 -delete
```

Schedule with cron:
```bash
# Add to crontab
0 2 * * * /home/ec2-user/backup_db.sh
```

### 8.2 Recovery Process

```bash
# Restore Redis
redis-cli SHUTDOWN
cp /data/backups/redis_latest.rdb /data/dump.rdb
redis-server

# Restore PostgreSQL
psql trading_db < /data/backups/postgres_latest.sql

# Verify
redis-cli ping
psql -U bot -d trading_db -c "SELECT COUNT(*) FROM trades;"
```

---

## 9. Security Hardening

### 9.1 Network Security

```bash
# UFW firewall (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 8000/tcp   # Bot API
sudo ufw allow 8001/tcp   # Prometheus
sudo ufw deny 6379/tcp    # Redis (internal only)
sudo ufw deny 5432/tcp    # PostgreSQL (internal only)
```

### 9.2 API Key Rotation

```python
# Implement in src/utils.py
async def rotate_api_keys():
    """Rotate API keys every 7 days"""
    old_key = os.getenv('BINANCE_API_KEY')
    new_key = await aws_secrets_manager.get_secret('bot/binance_api_key_new')
    
    # Test new key
    test_exchange = ccxt.binance({'apiKey': new_key, 'secret': new_secret})
    balance = test_exchange.fetch_balance()
    
    # Switch
    os.environ['BINANCE_API_KEY'] = new_key
    logger.info('✓ API keys rotated successfully')
```

---

## 10. Performance Tuning

### 10.1 Redis Optimization

```bash
# Increase max clients
redis-cli CONFIG SET maxclients 10000

# Enable persistence
redis-cli CONFIG SET save "900 1 300 10"

# Memory limits
redis-cli CONFIG SET maxmemory 4gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### 10.2 PostgreSQL Tuning

```sql
-- connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '8GB';

-- indices for performance
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_symbol ON trades(symbol);

SELECT pg_reload_conf();
```

---

## 11. Testing Before Go-Live

```bash
# 1. Paper trading (2+ weeks)
export ENVIRONMENT=paper_trading
docker-compose up -d

# 2. Load testing
ab -n 1000 -c 100 http://localhost:8000/health

# 3. Failover simulation
# Kill primary node and verify backup takes over
docker stop bot-api

# 4. Backtest validation
python scripts/backtest_sim.py

# 5. Sentiment analysis test
python tests/test_sentiment.py

# 6. Risk management test
python tests/test_risk_limits.py
```

---

## 12. Production Checklist (Go-Live)

- [ ] All API keys securely stored in Secrets Manager
- [ ] 3+ nodes deployed and heartbeat verified
- [ ] Redis Sentinel failover tested and working
- [ ] Prometheus + Grafana dashboards created
- [ ] Alert rules configured (latency, drawdown, failover)
- [ ] ELK stack for centralized logging
- [ ] Daily backups configured and tested
- [ ] SSL/TLS certificates installed
- [ ] Load balancer health checks enabled
- [ ] Database WAL enabled and replication working
- [ ] Paper trading completed (2+ weeks, >10% ROI)
- [ ] Position size limits hardcoded (max 2% per trade)
- [ ] Stop-loss orders automated (hardware kill-switch)
- [ ] Telegram alert bot configured
- [ ] On-call rotation schedule established
- [ ] Disaster recovery playbook documented

---

## Troubleshooting

### Issue: HighLatency Alert

```bash
# Check exchange connectivity
curl -I https://api.binance.com/api/v3/ping

# Check Redis latency
redis-cli --latency

# Check network
mtr -r -c 100 api.binance.com
```

### Issue: Failover Not Triggering

```bash
# Check Sentinel status
redis-cli -p 26379 sentinel masters

# Force failover
redis-cli -p 26379 sentinel failover master-redis

# Verify backup promoted
redis-cli -p 26379 sentinel slaves master-redis
```

### Issue: OOM Killer

```bash
# Increase memory
docker update --memory 4g crypto-bot-api

# Or scale pod
kubectl set resources deployment bot-api --limits=memory=4Gi -n crypto-bot

# Check memory usage
docker stats
```

---

## Support & Escalation

1. **Check logs**: `docker logs bot-api`
2. **Check metrics**: `curl localhost:8001/metrics`
3. **Check health**: `curl localhost:8000/health`
4. **Escalate**: Page on-call engineer via PagerDuty

---

**Deployment completed!** 🚀

Next: Monitor via Grafana (http://your-domain:3000) and Prometheus (http://your-domain:9090).

*Last updated: 2025-12-18*
