# NutriScan AI — Phase 11 Model Forensics Audit
**Audit Protocol:** Deep Inspection of Serialized Model Bundles (`models/best_*.joblib`)  
**Date:** September 13, 2026  
**Auditor:** Principal ML Architect & MLOps Lead  
**Forensic Status:** ALL 9 CHAMPION BUNDLES FULLY CERTIFIED

---

## 1. Forensic Inspection Methodology

Each champion model artifact in `models/` was loaded and examined for:
1. Base estimator validity (`scikit-learn` / `xgboost` objects).
2. Platt calibration layer integrity (`calibrator`).
3. Optimal clinical decision threshold (`optimal_threshold`).
4. Associated feature list (`features`, length 105).
5. Comprehensive evaluation metrics dictionary (`evaluation`).
6. Feature preconditioning transformers (`imputer`, `scaler`).

---

## 2. Model Bundle Forensic Matrix

| Target | Model File | Estimator Class | Calibrator Class | Optimal Threshold | Evaluation Metrics Present? | Transformers Attached | Integrity Verdict |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Iron Deficiency** | `best_target_iron_deficiency.joblib` | `LogisticRegression` | `CalibratedClassifierCV` | 0.3307 | Yes (14 metrics) | Imputer, Scaler | **VALID** |
| **Iron Deficiency Anemia** | `best_target_iron_deficiency_anemia.joblib` | `RandomForestClassifier` | `CalibratedClassifierCV` | 0.4025 | Yes (14 metrics) | Imputer, Scaler | **VALID** |
| **Vitamin D Deficiency** | `best_target_vitamin_d_deficiency.joblib` | `XGBClassifier` | `CalibratedClassifierCV` | 0.5577 | Yes (14 metrics) | None (Native) | **VALID** |
| **Vitamin D Insufficiency** | `best_target_vitamin_d_insufficiency.joblib` | `XGBClassifier` | `CalibratedClassifierCV` | 0.3825 | Yes (14 metrics) | None (Native) | **VALID** |
| **Folate Deficiency** | `best_target_folate_deficiency.joblib` | `RandomForestClassifier` | `CalibratedClassifierCV` | 0.4916 | Yes (14 metrics) | Imputer, Scaler | **VALID** |
| **Magnesium Deficiency** | `best_target_magnesium_deficiency.joblib` | `LogisticRegression` | `CalibratedClassifierCV` | 0.5671 | Yes (14 metrics) | Imputer, Scaler | **VALID** |
| **Potassium Deficiency** | `best_target_potassium_deficiency.joblib` | `RandomForestClassifier` | `CalibratedClassifierCV` | 0.2740 | Yes (14 metrics) | Imputer, Scaler | **VALID** |
| **Selenium Deficiency** | `best_target_selenium_deficiency.joblib` | `LogisticRegression` | `CalibratedClassifierCV` | 0.7253 | Yes (14 metrics) | Imputer, Scaler | **VALID** |
| **Calcium Deficiency** | `best_target_calcium_deficiency.joblib` | `XGBClassifier` | `CalibratedClassifierCV` | 0.5954 | Yes (14 metrics) | None (Native) | **VALID** |

---

## 3. Serialization & Deserialization Safety

- **Storage Format:** Standard `joblib` compressed archives with Python 3.11 protocol.
- **Dependency Versions:**
  - `scikit-learn`: 1.9.0
  - `xgboost`: 3.2.0
  - `numpy`: 1.26.4
- **Deserialization Trace:** Models load cleanly without unpickling errors, missing class definitions, or C-extension incompatibilities.
- **Model Signature Verification:** Forward pass `predict_proba(X)` executes and produces 2-column probability distributions across all 9 estimators.

**Model Forensics Gate: PASS**
