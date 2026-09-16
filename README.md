# NutriScan Platform

![NutriScan Platform Banner](assets/banner.svg)

[![CI Pipeline](https://img.shields.io/badge/CI%2FCD-Passing-brightgreen?style=flat-square)](https://github.com/saifvector/nutriscan-platform/actions)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-teal?style=flat-square)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%20%2B%20Vite-61dafb?style=flat-square)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7%20Alpine-dc382d?style=flat-square)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ed?style=flat-square)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

NutriScan is an enterprise-grade clinical artificial intelligence platform engineered for precision micronutrient deficiency detection, risk stratification, pediatric safety guardrails, and personalized dietary intervention planning.

Designed for clinical decision support and nutritional research, NutriScan combines multi-target machine learning models, deterministic pediatric contraindication rules, SHAP-based feature attribution, dual-engine persistence (PostgreSQL 16 primary with automatic SQLite WAL fallback), and distributed Redis 7 session invalidation and rate limiting.

---

## Architecture and Data Flow

![NutriScan System Architecture](assets/architecture_flow.svg)

The platform follows a decoupled, cloud-native architecture partitioned into seven distinct runtime subsystems:

1. **Client Layer (SPA)**: React 18, TypeScript, and Vite single-page application providing clinical dossiers, interactive assessment wizards, meal planners, and operational dashboards.
2. **Ingress and Reverse Proxy**: Nginx Alpine gateway enforcing strict security headers (CSP, HSTS, X-Frame-Options), static asset gzip compression, client routing fallbacks, and API request routing.
3. **Distributed Security and Cache (Redis 7)**: Distributed token denylisting, microsecond session revocation on credential changes, sliding-window rate limiting (5 req/min auth, 60 req/min inference, 300 req/min general), and cached assessment states.
4. **Application Core Engine (FastAPI)**: Asynchronous REST services managing authentication, RBAC, clinical questionnaire validation, audit trail recording, and telemetry collection.
5. **Clinical Safety Engine**: Deterministic safety module enforcing age-stratified nutrient intake ceilings, drug-nutrient interaction screening, and clinician override auditing.
6. **Machine Learning Pipeline**: Multi-target ensemble classifiers (XGBoost, LightGBM, Random Forest, Logistic Regression) predicting 9 deficiency targets with Platt scaling calibration and SHAP feature attribution.
7. **Dual-Engine Persistence**: High-throughput PostgreSQL 16 primary database with an automated fail-safe SQLite WAL fallback mechanism to guarantee uninterrupted operation.

---

## Core Capabilities

### 1. Calibrated Multi-Target Machine Learning
- **9 Micronutrient Targets**: Predicts probability scores for Iron Deficiency, Vitamin D Deficiency, Folate Deficiency, Calcium Deficiency, Magnesium Deficiency, Potassium Deficiency, Selenium Deficiency, Iron Deficiency Anemia, and Vitamin D Insufficiency.
- **Model Diversity**: Incorporates LightGBM, XGBoost, Random Forest, and Calibrated Logistic Regression trained on clinical biomarker and demographic datasets.
- **Causal Explainability**: Delivers SHAP (SHapley Additive exPlanations) values for every prediction, highlighting clinical drivers for clinician review.

### 2. Pediatric Safety and Clinical Guardrails
- **Age-Stratified Ceilings**: Strict upper limit (UL) enforcement tailored to pediatric age cohorts (infants, young children, adolescents).
- **Contraindication Matrix**: Prevents hazardous supplement recommendations when conflicting clinical conditions or drug regimens are detected (e.g., iron supplementation in hemochromatosis or tetracycline interactions).
- **Clinician Override Tracking**: Full audit trail recording when a licensed practitioner overrides an automated safety alert.

### 3. Distributed Security and Session Control
- **Instant Token Revocation**: Revoked JWTs (`jti`) are immediately published to Redis denylist clusters with zero-latency propagation.
- **Global Session Invalidation**: Password updates and role changes terminate all active sessions instantly.
- **Sliding-Window Rate Limiting**: Redis-backed atomic sliding counters mitigate denial-of-service attempts and credential stuffing.
- **Thread-Safe In-Memory Fallback**: When Redis is unreachable, the security engine transparently degrades to an in-memory synchronized TTL store without crashing.

### 4. Dual-Engine Persistence Layer
- **PostgreSQL 16 Primary**: ACID transactions, connection pooling, and relational integrity for enterprise environments.
- **Automated SQLite WAL Fallback**: Dynamic SQL translation layer converts queries into SQLite WAL dialect if PostgreSQL becomes unreachable, preserving system availability.
- **Automated DDL Exporter**: Built-in persistence utilities to export schemas and transfer datasets between database backends.

### 5. Enterprise Observability and Operations
- **Structured JSON Logging**: Centralized log formatting with timestamps, correlation IDs, and context metadata.
- **Kubernetes Probes**:
  - `/health`: Fast liveness check evaluating operational status.
  - `/ready`: Deep readiness probe verifying database connectivity, cache health, and model availability.
  - `/metrics`: Standard Prometheus-compatible exposition format for infrastructure monitoring.
- **Disaster Recovery**: Automated backup orchestrator supporting online snapshots, Gzip compression, and SHA-256 checksum validation.

---

## Clinical Interface and Platform Views

The platform includes a specialized clinical workstation for practitioners, researchers, and dietary specialists:

### Clinical Copilot and Assessment Dossier
![Clinical Copilot Dossier](reports/screenshots/copilot_1_dossier.png)

### Differential Diagnosis and Risk Scoring
![Differential Diagnosis](reports/screenshots/copilot_4_differential.png)

### Clinical Decision Review and Safety Verification
![Clinical Decision Review](reports/screenshots/copilot_5_review.png)

---

## Quick Start Guide

### Prerequisites
- Docker and Docker Compose (recommended) OR
- Python 3.11+ and Node.js 20+

---

### Option A: Launch with Docker Compose (Recommended)

Run the full platform stack (Frontend, Backend, PostgreSQL 16, and Redis 7) with a single command:

```bash
docker-compose up -d --build
```

After the containers build and initialize:
- **Frontend Workstation**: `http://localhost:5173`
- **Backend API Docs**: `http://localhost:8000/docs`
- **Readiness Health Check**: `http://localhost:8000/ready`
- **Prometheus Metrics**: `http://localhost:8000/metrics`

To stop all services:
```bash
docker-compose down
```

---

### Option B: Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/saifvector/nutriscan-platform.git
cd nutriscan-platform
```

#### 2. Configure Environment Variables
Copy the template configuration:
```bash
cp .env.example .env
```
Edit `.env` to configure your database, redis, and secret preferences.

#### 3. Backend Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

The backend is now live at `http://127.0.0.1:8000`.

#### 4. Frontend Setup
In a separate terminal window:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend application is now accessible at `http://localhost:5173`.

---

### Option C: Production Deployment on Render (1-Click Blueprint)

NutriScan includes a validated [`render.yaml`](render.yaml) specification that automatically provisions:
1. `nutriscan-backend`: Dockerized FastAPI container.
2. `nutriscan-frontend`: Static web application with API reverse proxy.
3. `nutriscan-postgres`: Managed PostgreSQL 16 database.
4. `nutriscan-redis`: Managed Redis 7 cache.

#### Deployment Steps:
1. Push this repository to your GitHub account:
   ```bash
   git remote add origin https://github.com/saifvector/nutriscan-platform.git
   git push -u origin main
   ```
2. Log in to the [Render Dashboard](https://dashboard.render.com).
3. Click **New +** and select **Blueprint**.
4. Select the repository **`saifvector/nutriscan-platform`**.
5. Render reads `render.yaml` and deploys all 4 services automatically.

---

## API Reference

The FastAPI service exposes an interactive OpenAPI Swagger interface at `/docs` and ReDoc at `/redoc`.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service liveness probe (status of DB, Redis, API) | No |
| `GET` | `/ready` | Kubernetes deep readiness probe (status code 200/503) | No |
| `GET` | `/metrics` | Prometheus metrics exposition format | No |
| `POST` | `/api/v1/auth/register` | Register new user or clinician account | No |
| `POST` | `/api/v1/auth/login` | Authenticate and issue signed JWT bearer token | No |
| `POST` | `/api/v1/auth/logout` | Revoke active token via distributed Redis denylist | Yes |
| `POST` | `/api/v1/assessment/submit` | Ingest comprehensive nutritional & clinical screening | Yes |
| `GET` | `/api/v1/assessment/{id}` | Retrieve patient screening dossier | Yes |
| `POST` | `/api/v1/prediction/predict` | Run multi-target ML inference on patient biomarkers | Yes |
| `POST` | `/api/v1/prediction/explain` | Generate SHAP feature importance breakdown | Yes |
| `POST` | `/api/v1/recommendation/generate` | Synthesize dietary intervention and meal plan | Yes |
| `POST` | `/api/v1/clinical/override` | Record clinician override of safety guardrails | Yes (Clinician) |
| `GET` | `/api/v1/observability/dashboard` | Retrieve system telemetry, request latencies, and uptime | Yes (Admin) |

---

## Automated Testing and Quality Assurance

NutriScan enforces automated regression verification across persistence, caching, clinical safety, and disaster recovery.

Run the test suite locally:

```bash
# Run all production regression tests
pytest backend/test_postgres_persistence_integration.py \
       backend/test_redis_integration.py \
       backend/test_observability_operations.py \
       backend/test_automated_backup_recovery.py \
       backend/test_pediatric_safety.py \
       backend/test_e2e_production_journey.py -v
```

### Automated CI/CD Pipeline
Every pull request and push to `main` triggers `.github/workflows/production_pipeline.yml` across six sequential gates:
1. **Lint and Code Quality**: Flake8 style compliance and TypeScript compilation check (`tsc --noEmit`).
2. **Unit and Clinical Validation**: Validation of inference rules, pediatric guardrails, and unit logic.
3. **Integration Testing**: Containerized PostgreSQL 16 and Redis 7 execution with dual-engine failover tests.
4. **Security Analysis**: Bandit static application security testing (SAST) and secret leak detection.
5. **Container Build Verification**: Multi-stage Docker build certification for backend and frontend.
6. **Deployment Gate**: Automatic verification of release readiness artifacts.

---

## Automated Backups and Disaster Recovery

NutriScan includes a dedicated backup orchestrator in [`scripts/backup_manager.py`](scripts/backup_manager.py).

### Create an Online Compressed Backup:
```bash
python scripts/backup_manager.py backup --source ./nutriscan_production.db --output ./backups
```
Generates a timestamped `.gz` archive alongside a cryptographically signed SHA-256 hash manifest.

### Verify Backup Integrity:
```bash
python scripts/backup_manager.py verify --file ./backups/nutriscan_backup_<timestamp>.gz
```

### Restore Database from Backup:
```bash
python scripts/backup_manager.py restore --file ./backups/nutriscan_backup_<timestamp>.gz --target ./restored.db
```

---

## Environment Variables Configuration

| Variable | Description | Default | Example |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Application runtime environment | `development` | `production` |
| `PORT` | API server listen port | `8000` | `8000` |
| `DATABASE_ENGINE` | Active persistence driver (`postgresql` or `sqlite`) | `sqlite` | `postgresql` |
| `DATABASE_URL` | Primary database connection string | `sqlite:///./nutriscan.db` | `postgresql://user:pass@host:5432/nutriscan_db` |
| `REDIS_URL` | Redis connection string for denylist and cache | `redis://localhost:6379/0` | `redis://default:token@host:6379` |
| `JWT_SECRET` | Cryptographic secret for signing tokens | (development key) | (32+ character entropy string) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifetime of issued authentication tokens | `60` | `60` |
| `ALLOWED_ORIGINS` | Comma-separated list of permitted CORS origins | `*` | `https://nutriscan-frontend.onrender.com` |
| `LOG_LEVEL` | Structured logging verbosity | `INFO` | `INFO` |

---

## Project Structure

```text
nutriscan-platform/
├── .github/workflows/          # Production CI/CD pipeline definition
├── assets/                     # Animated SVG diagrams and graphics
│   ├── banner.svg              # Animated platform header banner
│   └── architecture_flow.svg   # Animated system architecture diagram
├── backend/
│   ├── app/
│   │   ├── core/               # Database, Redis, security, observability
│   │   ├── models/             # Relational data entities
│   │   ├── modules/            # Business modules (auth, assessment, ML, safety)
│   │   └── main.py             # FastAPI entrypoint and probe registration
│   ├── Dockerfile              # Multi-stage hardened Python 3.11 container
│   └── test_*.py               # Automated integration and regression test suites
├── docs/                       # Architecture documentation and clinical specifications
├── frontend/
│   ├── src/                    # React 18 application, components, and hooks
│   ├── Dockerfile              # Multi-stage Node 20 builder and Nginx runtime
│   ├── nginx.conf              # Production Nginx reverse proxy configuration
│   └── package.json            # Node dependencies and build scripts
├── models/                     # Trained ML estimators and calibration artifacts
├── reports/                    # Clinical evidence, audit reports, and UI screenshots
├── scripts/
│   └── backup_manager.py       # Disaster recovery backup and restore engine
├── docker-compose.yml          # Multi-container local and staging orchestration
├── render.yaml                 # 1-click cloud deployment blueprint for Render
├── requirements.txt            # Python dependencies
└── README.md                   # Platform documentation
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
