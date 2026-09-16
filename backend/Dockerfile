# Multi-stage production build for NutriScan Backend API
# Stage 1: Build virtualenv with dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Hardened Runtime with Non-Root Security User
FROM python:3.11-slim AS runtime

LABEL maintainer="NutriScan AI Healthcare Engineering Team"
LABEL version="1.0.0"
LABEL description="NutriScan AI Production Backend API"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend:/app \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 10001 nutriscan && \
    useradd -u 10001 -g nutriscan -s /bin/bash -m nutriscan

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=nutriscan:nutriscan . /app

USER nutriscan

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
