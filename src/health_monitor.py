import asyncio
import logging
from prometheus_client import start_http_server, Gauge

logger = logging.getLogger('bot.health')

class HealthMonitor:
    def __init__(self, cfg):
        self.cfg = cfg
        self.heartbeat = Gauge('bot_heartbeat', 'Heartbeat timestamp')
        self.latency = Gauge('bot_latency_ms', 'API latency ms')
        self.running = False

    async def start(self):
        self.running = True
        # start prometheus metrics server
        start_http_server(8001)
        asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False

    async def _loop(self):
        import time
        while self.running:
            self.heartbeat.set(time.time())
            # measure latency to exchanges or nodes here
            self.latency.set(0)
            await asyncio.sleep(5)
