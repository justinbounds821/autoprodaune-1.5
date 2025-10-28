FROM python:3.11-slim

WORKDIR /app

# Copy common library
COPY --from=common /autopro-common /usr/local/lib/python3.11/site-packages/autopro_common

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app

ENV PORT=8001
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
