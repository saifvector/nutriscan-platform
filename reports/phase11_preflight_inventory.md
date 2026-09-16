# NutriScan AI — Phase 11 Preflight Repository Inventory
**Audit Mode:** Zero Trust Independent Verification  
**Date:** September 13, 2026  
**Auditor:** Principal ML Architect, Clinical AI Auditor, MLOps Engineer, Healthcare QA Lead  
**Integrity Status:** EMPIRICALLY VERIFIED

---

## 1. Directory Tree & Physical Storage Summary

An exhaustive filesystem scan was executed across the primary architectural directories of the NutriScan AI repository. File counts, byte allocations, and structure were verified from physical disk:

| Directory | Role | Total Files | Total Size (MB) | Integrity Status |
| :--- | :--- | :---: | :---: | :---: |
| `backend/` | Production FastAPI application, ML engine, services | 91 | 0.90 MB | **VERIFIED** |
| `frontend/` | React 19 / TypeScript clinical dashboard & UI | 69 | 2.13 MB | **VERIFIED** |
| `tests/` | Complete automated pytest regression suite | 12 | 0.14 MB | **VERIFIED** |
| `models/` | Serialized champion & benchmark model bundles | 45 | 31.83 MB | **VERIFIED** |
| `reports/` | Quality, benchmark, and clinical verification artifacts | 14 | 0.11 MB | **VERIFIED** |
| `data/` | NHANES cycles, USDA, NIH references, master Parquet | 462 | 418.75 MB | **VERIFIED** |
| **Total** | **NutriScan AI Core Workspace** | **693 files** | **453.86 MB** | **COMPLETE** |

*(Note: `.venv/`, `node_modules/`, `.git/`, and `__pycache__/` excluded from core source asset totals).*

---

## 2. Core Model Artifact Inventory

All 9 champion model artifacts for Phase 10C reside in `models/` alongside benchmark comparator models:

| Filename | Algorithm | Size (Bytes) | Integrity Check |
| :--- | :--- | :---: | :---: |
| `best_target_iron_deficiency.joblib` | Logistic Regression | 11,481 B | **VALID** |
| `best_target_iron_deficiency_anemia.joblib` | Random Forest | 2,020,617 B | **VALID** |
| `best_target_vitamin_d_deficiency.joblib` | XGBoost | 182,094 B | **VALID** |
| `best_target_vitamin_d_insufficiency.joblib` | XGBoost | 284,581 B | **VALID** |
| `best_target_folate_deficiency.joblib` | Random Forest | 3,229,673 B | **VALID** |
| `best_target_magnesium_deficiency.joblib` | Logistic Regression | 11,497 B | **VALID** |
| `best_target_potassium_deficiency.joblib` | Random Forest | 1,362,169 B | **VALID** |
| `best_target_selenium_deficiency.joblib` | Logistic Regression | 11,481 B | **VALID** |
| `best_target_calcium_deficiency.joblib` | XGBoost | 68,954 B | **VALID** |

Total champion model footprint: **7.18 MB**.

---

## 3. Missing & Orphaned Artifact Report

- **Missing Critical Datasets:** **0**. Master parquet `merged_training_dataset.parquet` is present and readable.
- **Missing Dictionaries:** **0**. Both `feature_dictionary.csv` (105 features) and `target_dictionary.csv` (17 targets) verified.
- **Missing API Routers:** **0**. Routes for predictions, recommendations, intelligence, reporting, and outcomes are registered in `api_router.py`.
- **Orphaned Artifacts:** None. All 36 challenger model joblib files (`lightgbm_*`, `random_forest_*`, `xgboost_*`, `logistic_regression_*`) correspond to audited Phase 10B benchmark comparisons.

**Inventory Verdict: PASS**
