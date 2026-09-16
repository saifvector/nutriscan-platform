# Phase 6 Architecture Specification: Comprehensive Nutritional Report Generation and Health Dashboard

## 1. Executive Summary

The **Comprehensive Nutritional Report Generation and Health Dashboard System** represents the capstone user-facing presentation layer of the *Integrated AI-Based Nutrient Deficiency Screening and Personalized Nutrition Platform*.

It synthesizes:
- Multi-target XGBoost deficiency probabilities across all 11 nutrients (Phase 3).
- SHAP feature attributions, contribution percentages, and risk drivers (Phase 4).
- Biochemical nutrient interaction rules, synergies, and compounding multipliers (Phase 2).
- Tailored dietary foods, synergistic pairings, lifestyle interventions, and phased 7/14/30-day recovery roadmaps (Phase 5).

The system yields:
1. An evidence-based **Overall Nutritional Health Score (0–100)** categorized into 4 clinical tiers.
2. An **Assessment Summary Engine** delivering executive narratives and key clinical findings.
3. An interactive **Nutritional Health Dashboard** providing 6 rich visualization widgets (in dual formats: JSON client contracts and standalone server-side responsive SVGs).
4. A **Vector Clinical PDF Generation Engine** powered by ReportLab (with an automatic Matplotlib fallback).
5. Fast, production-grade **FastAPI REST Endpoints** mounted under `/api/v1` with PostgreSQL relational persistence to `generated_reports`.

---

## 2. End-to-End System Architecture

```
                                  +---------------------------------------+
                                  |       Patient Health Assessment       |
                                  |  (Demographics, Diet, Symptoms, Life) |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   Phase 3: Multi-Nutrient Inference   |
                                  |  (11 Calibrated XGBoost Classifiers)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |     Phase 4: SHAP Explainability      |
                                  |    (Risk Drivers, Protective Factors) |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |    Phase 5: Recommendation Engine     |
                                  |    (Foods, Synergies, Recovery Plan)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
+=====================================================================================================+
|                        PHASE 6: REPORTING & DASHBOARD ORCHESTRATION SERVICE                         |
|                                                                                                     |
|  1. OVERALL NUTRITIONAL HEALTH SCORER (0-100)                                                       |
|     S = 100 - P_nutrients - P_interactions + M_lifestyle                                            |
|     Tiers: EXCELLENT (85-100) | GOOD (70-84) | MODERATE_RISK (50-69) | HIGH_RISK (0-49)             |
|                                                                                                     |
|  2. ASSESSMENT SUMMARY ENGINE                                                                       |
|     Executive narrative, patient profile, key findings, top risks, protective counterbalance         |
|                                                                                                     |
|  3. 6 DASHBOARD VISUALIZATIONS (JSON Contracts + Responsive Dark-Slate SVGs)                        |
|     • 11-Target Polar Radar Chart               • Ranked Probability Bar Chart                      |
|     • Deficiency Priority Tier Cards (P1/P2/P3) • Bidirectional SHAP Importance Balance             |
|     • Biochemical Interaction Network Graph     • 7 / 14 / 30-Day Recovery Timeline                 |
|                                                                                                     |
|  4. CLINICAL VECTOR PDF GENERATOR                                                                   |
|     ReportLab Platypus engine with multi-page typography, tables, and fallback to Matplotlib PDF     |
|                                                                                                     |
|  5. IN-MEMORY CACHE & POSTGRESQL PERSISTENCE                                                        |
|     Sub-35ms response time; async mapping to `generated_reports` table                              |
+=====================================================================================================+
                    |                                                         |
                    v                                                         v
    +-------------------------------+                         +-------------------------------+
    | Interactive Health Dashboard  |                         | Clinical PDF & JSON Reports   |
    | GET /api/v1/dashboard/{id}    |                         | POST /api/v1/reports/generate |
    | Fast JSON + Vector SVGs       |                         | GET  /api/v1/reports/{id}     |
    | Latency: < 35 ms              |                         | GET  /api/v1/reports/{id}/pdf |
    +-------------------------------+                         +-------------------------------+
```

---

## 3. Overall Nutritional Health Score Formulation

The score provides a unified, clinically grounded metric summarizing complete patient nutritional wellness.

### Mathematical Formulation
$$S_{health} = \max\Big(0, \min\big(100, \text{round}(100 - P_{nutrients} - P_{interactions} + M_{lifestyle})\big)\Big)$$

#### 1. Nutrient Risk Deductions ($P_{nutrients} \le 55$)
$$\text{Raw Deduction} = \sum_{i=1}^{11} \text{Probability}_i \times W_{severity}$$
- $W_{severity} = 12.0$ for `HIGH` or `SEVERE` predicted risks.
- $W_{severity} = 6.0$ for `MODERATE` risks.
- $W_{severity} = 1.5$ for `LOW` risks.
- $P_{nutrients} = \min(55.0, \text{Raw Deduction})$.

#### 2. Nutrient Interaction Compounding Penalty ($P_{interactions} \le 15$)
- Each active co-occurring deficiency interaction adds $+2.5$ (Moderate) to $+4.5$ (High).
- Compounding risk multiplier ($M_{synergy} > 1.1$) adds $(M_{synergy} - 1.0) \times 10.0$ points.
- $P_{interactions} = \min(15.0, \text{Total Interaction Deductions})$.

#### 3. Lifestyle & Dietary Habit Modifier ($-20 \le M_{lifestyle} \le +15$)
- **Hydration:** $\ge 2.5\text{L/day} \to +3.0$; $< 1.2\text{L/day} \to -4.0$.
- **Sunlight Exposure:** $\ge 30\text{ min/day} \to +3.0$; $< 15\text{ min/day} \to -4.0$.
- **Sleep Duration:** $7.0 - 9.0\text{ hours} \to +3.0$; $< 6.0\text{ or } > 10.0\text{ hours} \to -3.5$.
- **Stress Index (1-10):** $\le 3 \to +2.5$; $\ge 7 \to -4.0$.
- **Physical Activity:** Active/Athlete $\to +3.0$; Sedentary $\to -3.0$.
- **Fruit & Vegetable Servings:** $\ge 4.0\text{ serv/day} \to +3.5$; $\le 1.0\text{ serv/day} \to -4.5$.
- **Tobacco / Heavy Alcohol:** Smoker $\to -4.0$; Heavy Alcohol $\to -4.0$.

### Category Classification Matrix

| Score Range | Category Tier | Clinical Interpretation | Recommended Action |
| :---: | :---: | :--- | :--- |
| **85 – 100** | `EXCELLENT` | Optimal micronutrient homeostasis and robust lifestyle resilience. Minimal deficiency probability. | Maintain healthy dietary diversity and active lifestyle habits. |
| **70 – 84** | `GOOD` | Good nutritional foundation with isolated subclinical risk factors. | Targeted whole-food optimization to prevent future depletion. |
| **50 – 69** | `MODERATE_RISK` | Multiple elevated deficiency risks compounded by lifestyle stressors or nutrient interactions. | Implement 30-day dietary recovery plan and active habit adjustments. |
| **0 – 49** | `HIGH_RISK` | Critical deficiency probabilities across vital micronutrients with compound interaction penalties. | Prioritize immediate clinical replenishment and confirmatory lab workup. |

---

## 4. Dashboard Visualizations Specification

Each dashboard visualization produces both a structured JSON contract (ready for React Recharts, Chart.js, or D3.js) and a standalone server-side vector SVG:

1. **Nutrient Risk Radar Chart:**
   - Polar coordinate geometry ($cx=260, cy=230, r=150$).
   - 11 radial axes for the 11 target nutrients.
   - 4 concentric dotted reference rings at 25%, 50%, 75%, and 100%.
   - Shaded polygon overlay highlighting patient's personalized deficiency silhouette.
2. **Nutrient Risk Bar Chart:**
   - Ranked horizontal bars sorted from highest to lowest risk probability.
   - Severity color codes: Red (`#ef4444`) for High, Amber (`#f59e0b`) for Moderate, Emerald (`#10b981`) for Low.
   - 50% risk threshold reference line.
3. **Deficiency Priority Ranking Chart:**
   - Interactive classification cards grouping nutrients into Priority 1 (Urgent, risk $\ge 65\%$), Priority 2 (Targeted, risk $40-65\%$), and Priority 3 (Maintenance, risk $< 40\%$).
4. **SHAP Feature Importance Chart:**
   - Bidirectional bar chart with central zero baseline.
   - Right-side red bars represent positive risk drivers; left-side green bars represent protective counterbalances.
5. **Nutrient Interaction Graph:**
   - Circular network topology mapping biochemical connections between nutrients.
   - Green solid edges denote Synergies ($Fe \leftrightarrow C$, $B12 \leftrightarrow Folate$).
   - Sky-blue edges denote Co-factors ($Mg \leftrightarrow D$).
   - Rose dashed edges denote Competitive Inhibitions ($Ca \leftrightarrow Fe$, $Fe \leftrightarrow Zn$).
6. **Recovery Progress Timeline:**
   - 3-phase horizontal milestone tracker covering Days 1–7 (Acute Replenishment), Days 8–14 (Absorption Optimization), and Days 15–30 (Consolidation & Resilience).

---

## 5. Clinical PDF Generation Engine

The PDF engine formats clinical reports using ReportLab Platypus:
- **Header & Score Badge:** High-contrast score badge color-coded by health category.
- **Patient Profile:** Clean demographic grid (Age, Gender, Height, Weight, BMI, Diet).
- **Executive Findings:** Bulleted clinical highlights and synthetic narrative.
- **11-Nutrient Risk Matrix:** Formatted tabular overview with probability percentages and clinical implications.
- **Explainability & Risk Drivers:** Dual-column table comparing positive risk factors against protective habits.
- **Biochemical Interactions:** Clinical table detailing active nutrient pairs, mechanisms, and dietary action.
- **Dietary Guidance & Recovery Roadmap:** Prescribed foods, lifestyle targets (hydration, sunlight, sleep), and 30-day goals.
- **Medical Workup & Legal Disclaimers:** Guidance for primary care physicians on confirmatory venous blood panels.
- **Resilient Fallback:** Automatically switches to `matplotlib.backends.backend_pdf` if ReportLab encounters runtime issues, guaranteeing zero 500 errors.

---

## 6. REST API Endpoints Specification

Mounted under `/api/v1` via central router:

| Method | Endpoint | Description | Expected SLA |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/reports/generate` | Compiles full assessment report, stores record, renders PDF | $< 80\text{ ms}$ |
| `GET` | `/api/v1/reports/{id}` | Retrieves persisted JSON report by report UUID | $< 15\text{ ms}$ |
| `GET` | `/api/v1/reports/{id}/pdf` | Downloads vector PDF document (`application/pdf`) | $< 25\text{ ms}$ |
| `GET` | `/api/v1/dashboard/{assessment_id}` | Complete dashboard metrics, scores, alerts, and 6 SVGs | $< 35\text{ ms}$ |

---

## 7. Database Persistence Mapping

Stored in PostgreSQL `generated_reports` table:
- `id`: UUID Primary Key
- `user_id`: UUID foreign key to `users(id)`
- `assessment_id`: UUID foreign key to `health_assessments(id)`
- `report_title`: Descriptive report string
- `status`: String enum (`COMPLETED`, `PENDING`, `FAILED`)
- `summary_text`: Executive clinical narrative
- `overall_health_score`: Integer ($0 - 100$)
- `report_payload`: Static JSONB snapshot of all screening, prediction, explainability, and recommendation data
- `pdf_file_url`: REST endpoint path for PDF retrieval
- `created_at`: Timezone-aware creation timestamp
