# Clinical Model Card: Selenium Deficiency

**Target Identifier**: `target_selenium_deficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 7,586 tested participants (Prevalence: 3.39%)  
**Champion Architecture**: **XGBoost**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.7130** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.0893** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.674** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.1944** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.1795** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.1867** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.1823** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.9736** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.1094** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **1070** | False Negative: **32** |
| **Predicted Positive (1)** | False Positive: **29** | True Positive: **7** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.6372 | 0.0626 | 0.0656 | 0.0513 | 0.0332 |
| **XGBoost** | Challenger | 0.7130 | 0.0893 | 0.1867 | 0.1795 | 0.1094 |
| **CatBoost** | Challenger | 0.6969 | 0.0873 | 0.1795 | 0.1795 | 0.1587 |
| **ElasticNet_LogisticRegression** | Baseline | 0.7707 | 0.1307 | 0.1852 | 0.3846 | 0.1795 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `demo_poverty_ratio` | 0.2771 | Primary screening signal for Selenium Deficiency |
| 2 | `exam_diastolic_bp` | 0.2279 | Primary screening signal for Selenium Deficiency |
| 3 | `demo_age_years` | 0.1988 | Primary screening signal for Selenium Deficiency |
| 4 | `lifestyle_vigorous_activity_minutes` | 0.1132 | Primary screening signal for Selenium Deficiency |
| 5 | `lifestyle_moderate_activity_minutes` | 0.0920 | Primary screening signal for Selenium Deficiency |
| 6 | `exam_weight_kg` | 0.0881 | Primary screening signal for Selenium Deficiency |
| 7 | `exam_height_cm` | 0.0788 | Primary screening signal for Selenium Deficiency |
| 8 | `exam_pulse_rate` | 0.0764 | Primary screening signal for Selenium Deficiency |
| 9 | `demo_education_level` | 0.0633 | Primary screening signal for Selenium Deficiency |
| 10 | `total_selenium_intake_mcg` | 0.0606 | Primary screening signal for Selenium Deficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
