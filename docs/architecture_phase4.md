# Phase 4 Architecture Specification: Explainable AI and Risk Factor Analysis System

## Executive Summary
The **Explainable AI (XAI) and Risk Factor Analysis System** bridges the gap between complex multi-output ensemble machine learning models (XGBoost) and clinical utility. For each of the 11 target nutrients, the engine computes mathematically rigorous SHAP (SHapley Additive exPlanations) values, partitions drivers into positive risk factors and protective factors, normalizes percentage contributions ($\sum = 100\%$), translates statistical signals into natural language clinical reasoning for patients and medical practitioners, and renders interactive dashboard visual contracts (including server-side SVG waterfall plots).

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Client Application
        A[Client Web / Mobile UI]
    end

    subgraph API Gateway
        B[FastAPI /api/v1 Router]
    end

    subgraph Core ML & XAI Engine
        C[ClinicalFeaturePipeline]
        D[Champion MultiOutputClassifier XGBoost]
        E[SHAP TreeExplainer Caching Layer]
        F[Positive vs. Protective Factor Splitter]
        G[Percentage Contribution Normalizer]
        H[ClinicalReasoningEngine]
        I[DashboardVisualizer SVG Engine]
    end

    subgraph Persistence Layer
        J[(PostgreSQL 15+ nutrient_predictions & risk_factors)]
        K[In-Memory Fast LRU Cache]
    end

    A -->|POST /predict| B
    B --> C --> D --> E
    E --> F & G
    F & G --> H
    F & G --> I
    H & I --> K
    H & I --> J
    A -->|GET /predictions/{id}/explainability| B
    A -->|GET /predictions/{id}/risk-factors| B
    A -->|GET /predictions/{id}/visualizations/waterfall/{nutrient}| B
    B --> K
```

---

## 2. SHAP Explainability Engine Design

### 2.1 Mathematical Foundation
For any patient feature vector $x \in \mathbb{R}^D$ and model prediction $f(x)$ for nutrient $k$:
$$f(x) = \phi_0 + \sum_{i=1}^{D} \phi_i(x)$$
where:
- $\phi_0 = \mathbb{E}[f(X)]$ is the expected baseline prior over the representative population.
- $\phi_i(x)$ is the Shapley attribution value for feature $i$.
- $\phi_i > 0$ denotes a **Positive Risk Factor** (increases deficiency probability).
- $\phi_i < 0$ denotes a **Protective Factor** (lowers deficiency probability).

### 2.2 Feature Contribution Percentage
To present intuitive relative influence to users:
$$\text{Contribution Percentage}_i = \frac{|\phi_i|}{\sum_{j=1}^{D} |\phi_j|} \times 100\%$$
This guarantees that relative importance is scale-invariant and normalizes to $100\%$ across all contributing features.

### 2.3 Pre-Warming and Caching
Sequential calculation of exact tree traversals across 11 multi-class trees can introduce 500-700ms latency. The engine optimizes this via:
1. **TreeExplainer Pre-Caching:** Sub-models are pre-cached upon application startup (`lifespan` in `main.py`).
2. **Selective Execution:** Deep tree SHAP is computed on all flagged nutrients (`HIGH` or `MODERATE` risk) and single-nutrient drill-downs, while fast surrogate feature importances are computed for unflagged nutrients.
3. **Session Cache:** Once evaluated via `/predict`, the complete explainability payload is cached in memory, reducing subsequent `/explainability` endpoint response time to **$< 5\text{ ms}$**.

---

## 3. 5-Category Risk Factor Identification Framework

The platform organizes all identified risk factors into 5 clinical categories plus physiological determinants:

| Category | Clinical Scope | Example Factors Identified | Impact Severity |
| :--- | :--- | :--- | :--- |
| **DIETARY** | Nutritional intake, eating patterns, and exclusions | Strict Vegan, Vegetarian, Dairy-Free, Low Produce ($< 1.5$ serv/day), Low Water Intake | `HIGH`, `MODERATE` |
| **LIFESTYLE** | Environmental and behavioral habits | Low Sunlight ($< 20$ min/day), Heavy Alcohol, Active Tobacco Smoking, Sedentary Activity, High Stress ($\ge 7/10$) | `CRITICAL`, `HIGH`, `MODERATE` |
| **SYMPTOM** | Clinical phenotypic indicators of cellular depletion | Chronic Fatigue, Hair Loss, Brittle Nails, Muscle Cramps, Bone Pain, Neurological Paresthesias | `HIGH`, `MODERATE` |
| **MEDICAL_HISTORY**| Underlying pathologies and absorption disorders | Celiac Disease, Crohn's/IBD, Gastric Bypass/Bariatric Surgery, Atrophic Gastritis | `CRITICAL`, `HIGH` |
| **SUPPLEMENT** | Exogenous supplementation status | Absence of Targeted Supplementation, Regular Multivitamin Use | `MODERATE`, `PROTECTIVE` |
| **PHYSIOLOGICAL** | Intrinsic demographic & anthropometric factors | Reproductive-Age Female (Menstruation), Class I/II Obesity (Adipose Sequestration), Geriatric Age | `HIGH`, `MODERATE` |

---

## 4. Dual-Layer Clinical Reasoning Framework

The reasoning layer transforms mathematical attributions into actionable clinical insights:

### 4.1 Patient-Facing Narrative
Generated dynamically based on the combination of dominant positive drivers:
> *"Your screening results indicate a HIGH likelihood of Vitamin D deficiency (estimated probability: 88%). The primary contributors to this elevated risk are Insufficient Direct Sunlight Exposure (< 20 min/day) and Dairy-Free Dietary Restriction. When these factors coincide, your daily physiological requirements may significantly exceed your current dietary intake or absorption capacity. Importantly, your reported daily produce intake acts as a favorable protective factor."*

### 4.2 Clinician-Facing Assessment & Diagnostic Workup
Grounds findings in medical literature and specifies confirmatory laboratory orders and ICD-10 diagnostic codes:

```json
{
  "nutrient": "Vitamin D",
  "risk_level": "HIGH",
  "clinical_notes": "Pathophysiological Risk Profile: Machine learning ensemble indicates a HIGH deficiency probability (0.8800). Key risk attributions: Insufficient Direct Sunlight Exposure; Dairy-Free Dietary Restriction; Elevated BMI. Recommended Diagnostic Workup: Serum 25-hydroxyvitamin D [25(OH)D], Intact PTH, Serum Calcium, Alkaline Phosphatase. Diagnostic Threshold: < 20 ng/mL (50 nmol/L) indicates deficiency; 21-29 ng/mL indicates insufficiency. Grounding Guideline: Endocrine Society Clinical Practice Guidelines: Evaluation, Treatment, and Prevention of Vitamin D Deficiency.",
  "icd10_considerations": [
    "E55.9 - Vitamin D deficiency, unspecified",
    "M83.9 - Adult osteomalacia, unspecified"
  ]
}
```

---

## 5. Dashboard Components & Visualization Contracts

### 5.1 Standalone SVG Waterfall Chart
- Self-contained SVG with dark-mode styling (`#0f172a` slate theme), zero external JavaScript dependencies, and CSS gradients.
- Visually shows baseline expected value $\mathbb{E}[f(x)]$, green bars for protective reductions, red bars for risk increases, and final probability $f(x)$.

### 5.2 Recharts / Chart.js JSON Contract
```json
[
  {"name": "Population Baseline", "bottom": 0.0, "value": 0.25, "direction": "BASELINE", "color": "#64748b"},
  {"name": "Low Sunlight", "bottom": 0.25, "value": 0.35, "direction": "RISK_INCREASING", "color": "#ef4444"},
  {"name": "Vegan Diet", "bottom": 0.60, "value": 0.20, "direction": "RISK_INCREASING", "color": "#ef4444"},
  {"name": "Produce Intake", "bottom": 0.70, "value": 0.10, "direction": "PROTECTIVE", "color": "#10b981"},
  {"name": "Final Risk Score", "bottom": 0.0, "value": 0.70, "direction": "FINAL", "color": "#ef4444"}
]
```

---

## 6. Database Mapping & Persistence

Stored in PostgreSQL 15+ using the `risk_factors` table defined in Phase 1:

```sql
INSERT INTO risk_factors (
    id,
    prediction_id,
    factor_category,
    factor_name,
    factor_description,
    impact_score,
    impact_magnitude,
    evidence_reference
) VALUES (
    gen_random_uuid(),
    :prediction_id,
    'DIETARY',
    'Dairy-Free Dietary Restriction',
    'Exclusion of milk products eliminates the primary dietary calcium source without intentional fortified replacement.',
    0.3500,
    'HIGH',
    'Osteoporosis International: Dietary Calcium Intake'
);
```

---

## 7. API Specifications

| Method | Endpoint | Description | Response Schema |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/predictions/{id}/explainability` | Full multi-nutrient SHAP attributions, contribution percentages, and clinical reasoning | `MultiNutrientExplainabilityResponse` |
| `GET` | `/api/v1/predictions/{id}/risk-factors` | 5-category partitioned clinical risk factors with severity chips | `CategorizedRiskFactorsResponse` |
| `GET` | `/api/v1/predictions/{id}/explainability/{code}` | Single-nutrient deep dive (e.g. `VITAMIN_D`, `IRON`, `VITAMIN_B12`) | `NutrientExplainabilityDetail` |
| `GET` | `/api/v1/predictions/{id}/visualizations/waterfall/{code}` | Standalone SVG waterfall chart (`format=svg`) or JSON coordinates (`format=json`) | `image/svg+xml` or `application/json` |
| `GET` | `/api/v1/explainability/global` | Population-wide global feature importance across all 11 target nutrients | `GlobalFeatureImportanceResponse` |
