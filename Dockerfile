# --- Stage 1: Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# THE CHANGE: We remove the manual "apache-airflow[...]" string here.
# Since apache-airflow and its providers are NOW inside your requirements.txt,
# pip will install them all together using the 3.1.6 constraints.
RUN pip install --user --no-cache-dir \
    -r requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.1.6/constraints-3.11.txt"

# --- Stage 2: Runtime Stage ---
FROM python:3.11-slim as runner

WORKDIR /app

# Install runtime-only system deps
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000