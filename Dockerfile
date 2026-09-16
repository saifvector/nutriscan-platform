# ==============================================================================
# NutriScan AI — Multi-Stage Production Hardened Dockerfile
# Stage 1: Build Dependencies
# Stage 2: Hardened Runtime with Non-Root Security User & Health Checks
# ==============================================================================

# --- STAGE 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtualenv for isolated dependency collection
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


# --- STAGE 2: Production Hardened Runtime ---
FROM python:3.11-slim AS runtime

LABEL maintainer="NutriScan AI Healthcare Platform Engineering Team"
LABEL version="1.0.0"
LABEL description="Enterprise AI Clinical Copilot & Precision Nutrition Screening Platform"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Install runtime utilities & dumb-init for process supervision
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Create non-root unprivileged security group and user (UID 10001)
RUN groupadd -g 10001 nutriscan && \
    useradd -u 10001 -g nutriscan -s /bin/bash -m nutriscan

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application artifacts and code
COPY --chown=nutriscan:nutriscan . /app

# Switch to unprivileged non-root user
USER nutriscan

# Expose service port
EXPOSE 8000

# Health check container probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Process supervision with dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--no-access-log"]
