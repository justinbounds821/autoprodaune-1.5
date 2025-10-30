# Stage 1: Common library (no dependencies installed here)
FROM python:3.11-slim AS common
WORKDIR /autopro-common
COPY ../../autopro-common/ /autopro-common/

# Stage 2: Service
FROM python:3.11-slim
WORKDIR /app

# Copy common library from stage 1
COPY --from=common /autopro-common /usr/local/lib/python3.11/site-packages/autopro_common

# Install service dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app

ENV PORT=8001
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
