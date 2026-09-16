# NutriScan AI Healthcare Platform — Production Deployment Guide & Runbook

This guide details the end-to-end production deployment process for the NutriScan AI Healthcare Platform across modern cloud providers, serverless databases, managed container runtimes, and disaster recovery environments.

---

## 1. Architecture Overview

NutriScan is built on a 4-tier production architecture:
1. **Frontend Tier (Edge / CDN)**: React 18 + Vite SPA hosted on Vercel or Render with client routing fallbacks and immutable caching.
2. **Application Tier (Backend API)**: Multi-worker FastAPI on Python 3.11 with SHAP TreeExplainers, XGBoost champions, and clinical safety guardrails.
3. **Caching & Denylist Tier (Distributed State)**: Redis 7 for JWT token revocation denylists, sliding-window rate limiting, and API caching.
4. **Data Persistence Tier (Dual-Engine)**: PostgreSQL 16 (production) with SQLAlchemy connection pooling, asyncpg async driver, psycopg2 sync driver, and local SQLite WAL disaster-recovery fallback.

```mermaid
graph TD
    Client[Web Browser / Mobile Client] -->|HTTPS| CDN[Vercel / Nginx Edge]
    CDN -->|API Requests| Backend[FastAPI Backend - 4 Workers]
    Backend -->|JWT Denylist & Rate Limiting| Redis[(Redis 7 Cluster)]
    Backend -->|Patient Records & Predictions| Postgres[(PostgreSQL 16 Primary)]
    Backend -.->|Offline Disaster Fallback| SQLite[(Local SQLite WAL DB)]
```

---

## 2. Environment Variables & Secret Generation

### 2.1 Cryptographic Secret Requirements
In production, `JWT_SECRET` must be an unguessable cryptographic string of **at least 32 characters**.

Generate high-entropy secrets using OpenSSL:
```bash
# Generate 64-character JWT secret
openssl rand -hex 32

# Generate Database Password
openssl rand -base64 24
```

### 2.2 Production Variable Reference
| Variable | Required | Recommended Production Value | Description |
|---|---|---|---|
| `ENVIRONMENT` | Yes | `production` | Enables startup security validations |
| `DATABASE_ENGINE` | Yes | `postgresql` | Selects database persistence engine |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@host:5432/nutriscan_db` | Async connection string |
| `REDIS_URL` | Yes | `rediss://default:token@host:6379/0` | TLS-encrypted Redis connection |
| `JWT_SECRET` | Yes | 64+ char random hex string | HMAC secret for session security |
| `DB_POOL_SIZE` | No | `20` | Minimum persistent database connections |
| `DB_MAX_OVERFLOW` | No | `10` | Peak traffic connection burst pool |
| `BACKUP_RETENTION_DAYS`| No | `30` | Automated snapshot retention window |

---

## 3. Database Setup: Neon / Supabase / AWS RDS

### 3.1 Provisioning with Neon Serverless Postgres
1. Create a project at [Neon Console](https://console.neon.tech).
2. Create database `nutriscan_db`.
3. In connection settings, copy the `Pooled connection` connection string.
4. Replace the driver prefix with `postgresql+asyncpg://`:
   ```text
   DATABASE_URL=postgresql+asyncpg://[user]:[password]@[endpoint]-pooler.neon.tech/nutriscan_db?sslmode=require
   ```

### 3.2 Automated Schema Migration
The platform auto-initializes tables upon container startup. To manually generate and apply PostgreSQL DDL:
```bash
# Export production PostgreSQL DDL and seeds
py -3.11 -c "from app.core.persistence import PersistenceRepository; print(PersistenceRepository.export_to_postgres_sql())" > postgres_migration.sql

# Apply to PostgreSQL instance
psql $DATABASE_URL -f postgres_migration.sql
```

---

## 4. Distributed Cache Setup: Redis Cloud / Upstash

1. Create a Redis instance at [Upstash](https://upstash.com) or [Redis Cloud](https://redis.com).
2. Copy the `rediss://` TLS connection string.
3. Configure `REDIS_URL`:
   ```text
   REDIS_URL=rediss://default:your_token@your-cluster.upstash.io:6379/0
   ```
4. Verification: If Redis experiences network interruptions, NutriScan automatically falls back to in-memory TTL maps with zero clinical downtime.

---

## 5. Deployment Target A: Docker Compose (Self-Hosted / VPS)

For AWS EC2, DigitalOcean Droplets, or on-premise hardware:

```bash
# 1. Clone repository
git clone https://github.com/nutriscan/nutriscan.git
cd nutriscan

# 2. Configure environment
cp .env.example .env
nano .env

# 3. Launch coordinated production cluster
docker-compose up -d --build

# 4. Verify cluster health
docker-compose ps
curl -f http://localhost:8000/ready
```

---

## 6. Deployment Target B: Render Blueprint (One-Click)

1. Connect the GitHub repository to [Render Dashboard](https://dashboard.render.com).
2. Select **New > Blueprint**.
3. Choose `render.yaml` from the root of the repository.
4. Render will automatically provision:
   - `nutriscan-postgres` (PostgreSQL 16)
   - `nutriscan-redis` (Redis 7)
   - `nutriscan-backend` (Web Service with 2 instances)
   - `nutriscan-frontend` (Static Site with SPA routing)
5. Click **Apply**.

---

## 7. Deployment Target C: Railway (Backend) + Vercel (Frontend)

### 7.1 Backend on Railway
1. Go to [Railway Dashboard](https://railway.app).
2. Create **New Project > Deploy from GitHub repo**.
3. Railway detects `railway.json` and builds via `backend/Dockerfile`.
4. Add PostgreSQL and Redis plugins in the Railway canvas.
5. Link environment variables `${{Postgres.DATABASE_URL}}` and `${{Redis.REDIS_URL}}`.

### 7.2 Frontend on Vercel
1. Go to [Vercel Dashboard](https://vercel.com).
2. Import project with root directory set to `frontend`.
3. Vercel automatically detects Vite framework and applies `frontend/vercel.json`.
4. Add environment variable `VITE_API_URL` pointing to your Railway backend URL.
5. Deploy.

---

## 8. Health Checks & Kubernetes Probes

NutriScan exposes standardized container orchestration probes:

| Probe Type | Endpoint | Expected Code | Purpose |
|---|---|---|---|
| **Liveness Probe** | `/health` | `200 OK` | Verifies process responsiveness (< 20ms) |
| **Readiness Probe**| `/ready` | `200 OK` (or `503`) | Verifies DB, ML models, & persistence ready |
| **Deep Diagnostic**| `/health/deep`| `200 OK` | Model registry, SHAP explainers, & drift checks |
| **Prometheus Metrics**| `/metrics` | `200 OK` | Request rates, error rates, p95/p99 latency |

---

## 9. Automated Backups & Disaster Recovery Runbook

### 9.1 Creating an Immediate Snapshot
```bash
py -3.11 scripts/backup_manager.py --backup
```
Generates:
- `backups/nutriscan_backup_<engine>_<timestamp>.db.gz`
- `backups/nutriscan_backup_<engine>_<timestamp>.db.gz.sha256`
- `backups/nutriscan_backup_<engine>_<timestamp>_manifest.json`

### 9.2 Point-In-Time Restoration
```bash
py -3.11 scripts/backup_manager.py --restore backups/nutriscan_backup_sqlite_20260916_120000.db.gz
```
The manager automatically validates SHA-256 integrity, executes low-level SQLite integrity checks, and atomically replaces the live database file with zero data corruption.

### 9.3 Retention Pruning Policy
```bash
# Prune backups older than 30 days
py -3.11 scripts/backup_manager.py --prune
```
Configure via cron or systemd timer to execute daily at midnight:
```cron
0 0 * * * cd /app && py -3.11 scripts/backup_manager.py --backup && py -3.11 scripts/backup_manager.py --prune
```
