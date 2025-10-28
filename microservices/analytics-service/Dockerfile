FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

COPY microservices/autopro-common /build/autopro-common
RUN cd /build/autopro-common && pip install --user -e .

COPY microservices/analytics-service/requirements.txt /build/
RUN pip install --user -r /build/requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY microservices/autopro-common /workspace/microservices/autopro-common
COPY microservices/analytics-service/app /app/app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8008

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8008/health/live')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008", "--log-level", "info"]
