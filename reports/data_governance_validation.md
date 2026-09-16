# NutriScan AI — Data Governance, Lineage & Audit Integrity Validation Report

**Audit Execution Date:** September 14, 2026  
**Governance Standard:** FAIR Data Principles (Findable, Accessible, Interoperable, Reusable) & FDA Good Machine Learning Practice (GMLP)  
**Audit Scope:** Full Data Pipeline Lineage, Feature Definitions, Serialized Model Lineage, and SHA-256 Decision Integrity  

---

## 1. Executive Summary & Verification Matrix

```
+====================================================================================================+
|                                DATA GOVERNANCE AUDIT MATRIX                                        |
+====================================================================================================+
| Governance Component                 | Target Standard / Evidence Base      | Audit Status         |
+--------------------------------------+--------------------------------------+----------------------+
| 1. Dataset Ingestion Lineage         | 82 CDC NHANES, USDA FNDDS, NIH DSID  | **VERIFIED**         |
| 2. File Integrity & Byte Verification| 310 Audited Files, 0 Corrupted Files | **VERIFIED**         |
| 3. Feature Lineage & Dictionary      | 120+ Features in Feature Dictionary  | **VERIFIED**         |
| 4. Model Lineage & Reproducibility   | 45 Serialized Artifacts in `models/` | **VERIFIED**         |
| 5. Ground Truth Target Biomarkers    | CDC Laboratory Cutoffs (9 Targets)   | **VERIFIED**         |
| 6. Audit Trail Immutability (SHA-256)| Cryptographic Hash Generation        | **VERIFIED**         |
| 7. Relational Audit Persistence      | PostgreSQL Append-Only Storage       | **PARTIALLY VERIFIED**|
+====================================================================================================+
```

---

## 2. Dataset Ingestion Lineage & Physical File Verification

| Dataset Family | Storage Path | File Count & Format | Source Organization | Verification Finding |
| :--- | :--- | :--- | :--- | :---: |
| **NHANES Demographics** | `data/nhanes/demographics/` | `DEMO_L.xpt` + Codebooks | CDC National Center for Health Statistics | **VERIFIED** |
| **NHANES Laboratory** | `data/nhanes/laboratory/` | 24 SAS Transport files (`VID_L`, `FERTIN_L`, `CBC_L`, etc.) | CDC / NCHS Reference Laboratories | **VERIFIED** |
| **NHANES Dietary** | `data/nhanes/dietary/` | 18 SAS Transport files (`DR1TOT_L`, `DR2TOT_L`, `DSQTOT_L`)| USDA Food Surveys Research Group | **VERIFIED** |
| **USDA Foundation Foods**| `data/usda/foundation_foods/`| Normalized CSV tables (`food.csv`, `nutrient.csv`)| USDA Agricultural Research Service | **VERIFIED** |
| **USDA FNDDS Survey Foods**| `data/usda/fndds/` | Survey food item composition tables | USDA What We Eat In America (WWEIA) | **VERIFIED** |
| **NIH DSID Supplements** | `data/nih/dsid/` | Analytical ingredient regression models | NIH Office of Dietary Supplements (ODS) | **VERIFIED** |
| **Merged Training Dataset**| `data/merged_training_dataset.parquet` | 2.61 MB Parquet file ($N > 2,000$ holdout participants) | Consolidated Pipeline Preprocessor | **VERIFIED** |

- **Integrity Status:** Evaluated via MD5 checksum verification in `data/data_quality_report.md`. 100% of files parsed without byte truncation or schema mismatch.

---

## 3. Feature Lineage & Target Variable Mapping

### 3.1 Feature Pipeline Lineage
- **Source Module:** `backend/app/ml/feature_engineering.py` & `backend/app/modules/prediction/clinical_preprocessor.py`.
- **Feature Dictionary:** Fully documented in `data/feature_dictionary.csv` (120+ clinical variables).
- **Engineering Logic:**
  - *Dietary Aggregation:* 24-hour recall averages combined with supplement intake.
  - *Interaction Ratios:* Calcium-to-Magnesium ($\text{Ca}:\text{Mg}$), Sodium-to-Potassium ($\text{Na}:\text{K}$), and Iron-to-Phytate competitive ratios.
  - *Symptom Scores:* Normalized severity ratings across fatigue, paresthesia, pallor, brittle nails, and cognitive fog.

### 3.2 Target Biomarker Lineage (Ground Truth)

| Clinical Target | NHANES Biomarker Variable | Standard Clinical Unit | Clinical Cutoff Threshold | Model Artifact |
| :--- | :--- | :--- | :--- | :---: |
| **Iron Deficiency** | `LBXFER` (Serum Ferritin) | $\text{ng/mL}$ | $< 30.0\text{ ng/mL}$ | `best_target_iron_deficiency.joblib` |
| **Iron Defic. Anemia**| `LBXFER` + `LBXHGB` (Hgb) | $\text{g/dL}$ | $\text{Ferritin} < 30\text{ \& Hgb} < 12.0(\text{F})/13.5(\text{M})$ | `best_target_iron_deficiency_anemia.joblib` |
| **Vitamin D Defic.** | `LBXVIDMS` (25-OH-D Total) | $\text{nmol/L}$ ($\text{ng/mL}$) | $< 50.0\text{ nmol/L}$ ($< 20.0\text{ ng/mL}$) | `best_target_vitamin_d_deficiency.joblib` |
| **Vitamin D Insuff.**| `LBXVIDMS` (25-OH-D Total) | $\text{nmol/L}$ ($\text{ng/mL}$) | $50.0 - 75.0\text{ nmol/L}$ ($20.0 - 30.0\text{ ng/mL}$) | `best_target_vitamin_d_insufficiency.joblib` |
| **Folate Deficiency**| `LBDRFO` (RBC Folate) | $\text{nmol/L}$ | $< 305.0\text{ nmol/L}$ | `best_target_folate_deficiency.joblib` |
| **Calcium Defic.** | `LBXSCA` (Total Calcium) | $\text{mg/dL}$ | $< 8.5\text{ mg/dL}$ | `best_target_calcium_deficiency.joblib` |
| **Magnesium Defic.**| `LBXSC3SI` (Electrolytes) | $\text{mg/dL}$ | Serum $\text{Mg} < 1.8\text{ mg/dL}$ | `best_target_magnesium_deficiency.joblib` |
| **Selenium Defic.** | `LBXSEL` (Blood Selenium) | $\text{mcg/L}$ | $< 70.0\text{ mcg/L}$ | `best_target_selenium_deficiency.joblib` |
| **Potassium Defic.**| `LBXSKSI` (Serum Potassium)| $\text{mmol/L}$ | $< 3.5\text{ mmol/L}$ | `best_target_potassium_deficiency.joblib` |

---

## 4. Model Lineage & Artifact Verification

- **Storage Directory:** `models/` contains 45 serialized `.joblib` model artifacts.
- **Model Breakdown:**
  - 9 Logistic Regression models with L2 regularization.
  - 9 Random Forest classifiers (100 trees, max depth 12).
  - 9 XGBoost gradient boosted classifiers with early stopping.
  - 9 LightGBM gradient boosted decision trees.
  - 9 Champion ensemble models selected via holdout AUROC/AUPRC optimization.
- **Reproducibility:** Training script `backend/app/modules/training/pipeline.py` maintains deterministic random seeds (`random_state=42`) with full cross-validation logs documented in `phase10b_training_report.md`.
- **Verdict:** [**VERIFIED**]

---

## 5. Audit Trail Immutability & Cryptographic Integrity

- **Cryptographic Hash Engine:** `backend/app/modules/governance/audit_service.py` computes canonical SHA-256 hashes combining assessment inputs, prediction vectors, clinician actions, and timestamps.
- **PDF Certification:** `ClinicalAuditService.generate_pdf_certificate()` compiles tamper-evident PDF documents containing embedded SHA-256 hashes, doctor sign-off blocks, and legal disclaimers.
- **Finding & Remediation:** Active decision records are stored in memory (`_audit_store`) and streamable via `/api/v1/audit/export/csv`. For full enterprise disaster recovery, asynchronous flushing to PostgreSQL `clinical_audit_records` table must be maintained [**PARTIALLY VERIFIED**].
