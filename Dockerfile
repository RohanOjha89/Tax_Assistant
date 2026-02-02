# --- Stage 1: Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# FIXED: We use the same constraint file here as we did in Airflow!
# This ensures that both containers are "speaking the same language" (NumPy 1.x).
RUN pip install --user --no-cache-dir -r requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.2/constraints-3.11.txt"

# --- Stage 2: Runtime Stage ---
FROM python:3.11-slim as runner

WORKDIR /app

# Copy the specific python packages
COPY --from=builder /root/.local /root/.local
COPY . .

# IMPORTANT: Ensure your PATH and PYTHONPATH are clean
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000