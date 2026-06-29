# Stage 1: Dependency builder stage
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

# Install build dependencies if needed (e.g. for compiling packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install requirements to user local space
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy only installed python packages from the builder stage
COPY --from=builder /root/.local /root/.local
# Copy application source code
COPY . /app

# Ensure bin scripts from root local are on the executable path
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
# Default environment configurations
ENV PORT=8000
ENV HOST=0.0.0.0

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
