# Minimal monitoring stub for FAKE_MODE

from prometheus_client import CollectorRegistry

REGISTRY = CollectorRegistry()

class Monitoring:
    async def log_event(self, level, event, message):
        print(f"[{level}] {event}: {message}")

def get_monitoring():
    return Monitoring()
