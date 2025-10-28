# AutoPro Common Library

Shared utilities and abstractions for all AutoPro microservices.

## Features

### 🪵 Structured Logging
- JSON-formatted logs with OpenTelemetry trace context
- Automatic service name injection
- Metric logging support

```python
from autopro_common import setup_logging, get_logger

setup_logging("my-service", level="INFO", json_format=True)
logger = get_logger(__name__)
logger.info("Service started", extra={"version": "1.0.0"})
```

### 🗄️ Async Database (SQLAlchemy)
- Connection pooling with automatic retry
- Async session management
- PostgreSQL + asyncpg driver

```python
from autopro_common import init_database, get_db_session
from fastapi import Depends

# Initialize once at startup
db = init_database(database_url="postgresql+asyncpg://user:pass@host/db")

# Use in endpoints
@app.get("/items")
async def get_items(session = Depends(get_db_session)):
    result = await session.execute(select(Item))
    return result.scalars().all()
```

### 💾 Redis Cache
- Async Redis client with connection pooling
- Automatic JSON serialization
- TTL support

```python
from autopro_common import init_redis, get_redis

# Initialize once at startup
cache = init_redis(redis_url="redis://localhost:6379/0")

# Use anywhere
cache = get_redis()
await cache.set("key", {"data": "value"}, ttl=3600)
value = await cache.get("key")
```

### 📨 RabbitMQ Messaging
- Async producer/consumer with aio-pika
- Automatic JSON serialization
- Message priority and persistence

```python
from autopro_common import init_rabbitmq, get_producer, get_consumer

# Initialize once at startup
await init_rabbitmq(amqp_url="amqp://guest:guest@localhost/")

# Publish messages
producer = get_producer()
await producer.publish("my-queue", {"task": "process"})

# Consume messages
consumer = get_consumer()
async def handle_message(data: dict):
    print(f"Received: {data}")

await consumer.consume("my-queue", handle_message)
```

### 📊 Prometheus Metrics
- Automatic HTTP request tracking
- Database, cache, and queue metrics
- Custom business metrics

```python
from autopro_common import setup_metrics

# Setup metrics (adds middleware + /metrics endpoint)
metrics = setup_metrics(app, service_name="my-service")

# Track custom business events
metrics.track_business_event("lead_created")
metrics.set_business_metric("active_users", 150)
```

### ❤️ Health Checks
- Kubernetes readiness/liveness probes
- Dependency health tracking
- Automatic uptime tracking

```python
from autopro_common import init_health_check, create_health_router

# Initialize health check
health = init_health_check("my-service")

# Add dependency checks
health.add_check("database", lambda: db.test_connection())
health.add_check("redis", lambda: cache.ping())

# Add health router
app.include_router(create_health_router(health))

# Endpoints: /health, /health/ready, /health/live
```

## Installation

```bash
pip install -e /workspace/microservices/autopro-common
```

## Complete Microservice Example

```python
from fastapi import FastAPI, Depends
from autopro_common import (
    setup_logging,
    get_logger,
    init_database,
    init_redis,
    init_rabbitmq,
    get_db_session,
    setup_metrics,
    init_health_check,
    create_health_router,
)

# Setup logging
setup_logging("my-service", level="INFO")
logger = get_logger(__name__)

# Create app
app = FastAPI(title="My Service")

# Setup monitoring
metrics = setup_metrics(app, "my-service")
health = init_health_check("my-service")

@app.on_event("startup")
async def startup():
    # Initialize dependencies
    db = init_database()
    cache = init_redis()
    await init_rabbitmq()
    
    # Add health checks
    health.add_check("database", db.test_connection)
    health.add_check("redis", cache.ping)
    
    logger.info("Service started successfully")

# Add health endpoints
app.include_router(create_health_router(health))

@app.get("/")
async def root():
    return {"status": "ok", "service": "my-service"}
```

## Architecture Benefits

- **Code Reuse**: Share common utilities across all services
- **Consistency**: Standardized logging, metrics, and health checks
- **Maintainability**: Update once, deploy everywhere
- **Observability**: Built-in monitoring and tracing support
- **Production-Ready**: Connection pooling, error handling, retry logic

## License

Proprietary - AutoPro Daune 2025
