# --- Stage 1: Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Use the same constraints as Airflow to ensure binary compatibility across your microservices
RUN pip install --user --no-cache-dir \
    "apache-airflow[amazon,postgres]==3.1.6" \
    -r requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.1.6/constraints-3.11.txt"

# --- Stage 2: Runtime Stage ---
FROM python:3.11-slim as runner

WORKDIR /app

# Install runtime-only system deps (like libpq for postgres)
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy the specific python packages
COPY --from=builder /root/.local /root/.local
COPY . .

# Environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000