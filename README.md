# Integrated AI-Based Nutrient Deficiency Screening and Personalized Nutrition Platform

## Phase 1: Project Foundation & Database Architecture

Production-grade foundational architecture, scalable relational database schema, user clinical data contracts, and modular backend design designed for seamless AI/ML inference and SHAP explainability.

---

### Project Architecture Overview

The system captures multi-dimensional user nutritional screenings, extracts standardized feature vectors, predicts micronutrient deficiencies with confidence bounds, performs causal attribution (Explainability via SHAP), and outputs personalized food recommendations and clinical reports.

#### Key Tech Stack:
- **Database**: PostgreSQL 15+ (Relational integrity, UUID PKs, GIN-indexed JSONB for symptoms & clinical history)
- **Backend API**: Python 3.11+, FastAPI, Pydantic V2, SQLAlchemy 2.0 (Async)
- **Machine Learning Integration Ready**: Scikit-Learn, XGBoost, SHAP, NumPy
- **Orchestration**: Docker & Docker Compose

---

### Project Structure

```
Nutrient deficiency/
├── backend/
│   ├── app/
│   │   ├── main.py                     # API Application factory & middlewares
│   │   ├── core/                       # App configuration, security & DB session
│   │   ├── models/                     # SQLAlchemy declarative ORM models
│   │   │   ├── user.py                 # Users & UserProfiles (1:1)
│   │   │   ├── assessment.py           # HealthAssessments (10 input fields)
│   │   │   ├── prediction.py           # NutrientPredictions & RiskFactors
│   │   │   ├── recommendation.py       # FoodRecommendations
│   │   │   └── report.py               # GeneratedReports
│   │   ├── schemas/                    # Pydantic validation schemas
│   │   │   ├── assessment.py           # Validates 10 input clinical fields
│   │   │   ├── prediction.py           # ML prediction & risk levels
│   │   │   ├── recommendation.py       # Dietary interventions
│   │   │   └── report.py               # Aggregated report payloads
│   │   └── modules/                    # Six Core Business Modules
│   │       ├── auth/                   # Authentication & RBAC
│   │       ├── assessment/             # Screening questionnaire ingestion
│   │       ├── prediction/             # ML inference & feature pipeline
│   │       ├── explainability/         # SHAP feature attribution
│   │       ├── recommendation/         # Nutritional matching engine
│   │       └── reporting/              # Clinical PDF & JSON generation
├── database/
│   ├── schema.sql                      # Production PostgreSQL DDL (7 tables, indexes, triggers)
│   └── seeds.sql                       # Real-world clinical seed records
├── docs/
│   └── architecture_phase1.md          # Master architecture blueprint & ER diagrams
├── docker-compose.yml                  # PostgreSQL 16 & Backend services
├── Dockerfile                          # Production container build
├── requirements.txt                    # Python runtime & ML dependencies
└── README.md
```

---

### Quick Start (Local Setup)

#### Option 1: Docker Compose (Recommended)
Launch PostgreSQL and the FastAPI service with one command:
```bash
docker compose up -d --build
```
PostgreSQL will automatically load `database/schema.sql` and `database/seeds.sql`.

- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative ReDoc**: `http://localhost:8000/redoc`
- **PostgreSQL**: `localhost:5432` (User: `nutrient_admin`, Pass: `nutrient_secure_password_2026`)

#### Option 2: Local PostgreSQL
Run DDL and seeds directly against your local PostgreSQL instance:
```bash
psql -U postgres -d postgres -c "CREATE DATABASE nutrient_screening_db;"
psql -U postgres -d nutrient_screening_db -f database/schema.sql
psql -U postgres -d nutrient_screening_db -f database/seeds.sql
```

Install backend dependencies:
```bash
pip install -r requirements.txt
```

---

### Phase 1 Documentation Deliverables
Read the full system architecture blueprint in [docs/architecture_phase1.md](file:///c:/Users/saifu/Desktop/Nutrient%20deficiency/docs/architecture_phase1.md).
