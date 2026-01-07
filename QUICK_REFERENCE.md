# QUICK REFERENCE - All Commands

## Installation & Setup

```bash
# 1. Navigate to project
cd bot_project

# 2. Build Docker image
docker build -t crypto-bot:local .

# 3. Start all services
docker-compose up -d --remove-orphans

# 4. Verify services
docker-compose ps
```

## Run Tests & Demos

```bash
# 1. Integration test (full system demo)
python tests/integration_test.py

# 2. Failover simulation (3 nodes)
python scripts/failover_demo.py

# 3. 1-year backtest
python scripts/backtest_sim.py

# 4. Generate PDF report
python scripts/generate_weekly_report.py
```

## View Results

```bash
# Check metrics
curl http://localhost:8001/metrics | head -20

# View logs
docker logs -f bot-api

# List generated reports
ls -lh ./reports/

# Display project summary
python PROJECT_SUMMARY.py
```

## Deployment

```bash
# Kubernetes deployment
kubectl create namespace crypto-bot
kubectl apply -f k8s/deployment.yaml -n crypto-bot

# Monitor pods
kubectl get pods -n crypto-bot
kubectl logs deployment/bot-api -n crypto-bot
```

## Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Remove image
docker rmi crypto-bot:local
```

## File Locations

- Core code: `src/`
- Tests: `tests/`
- Scripts: `scripts/`
- Reports: `./reports/`
- Kubernetes: `k8s/`
- Config: `config.yaml`

## Key Files

- `FULL_README.md` - Complete documentation
- `PRODUCTION_DEPLOYMENT.md` - Production guide (12 sections)
- `CODE_EXAMPLES.py` - 10+ code examples
- `PROJECT_SUMMARY.py` - Architecture & statistics
- `PROJECT_COMPLETION_REPORT.txt` - Final report

## Troubleshooting

```bash
# Check service health
docker-compose logs

# Rebuild without cache
docker build --no-cache -t crypto-bot:local .

# Reset everything
docker-compose down -v && docker build -t crypto-bot:local .
```

---

**All tools ready! Run the integration test to see the full system in action.**
