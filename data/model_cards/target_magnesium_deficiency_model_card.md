# Clinical Model Card: Magnesium Deficiency

**Target Identifier**: `target_magnesium_deficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 6,324 tested participants (Prevalence: 9.20%)  
**Champion Architecture**: **CatBoost**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.6798** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.1727** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.509** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.1512** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.4483** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.2261** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.3218** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.7459** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.1969** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **643** | False Negative: **48** |
| **Predicted Positive (1)** | False Positive: **219** | True Positive: **39** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.6110 | 0.1316 | 0.1992 | 0.5632 | 0.0829 |
| **XGBoost** | Challenger | 0.6557 | 0.1665 | 0.2287 | 0.5862 | 0.1685 |
| **CatBoost** | Challenger | 0.6798 | 0.1727 | 0.2261 | 0.4483 | 0.1969 |
| **ElasticNet_LogisticRegression** | Baseline | 0.7293 | 0.2100 | 0.2840 | 0.5517 | 0.2039 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `exam_waist_height_ratio` | 0.1276 | Primary screening signal for Magnesium Deficiency |
| 2 | `demo_poverty_ratio` | 0.1224 | Primary screening signal for Magnesium Deficiency |
| 3 | `lifestyle_vigorous_activity_minutes` | 0.0848 | Primary screening signal for Magnesium Deficiency |
| 4 | `exam_bmi` | 0.0835 | Primary screening signal for Magnesium Deficiency |
| 5 | `lifestyle_smoked_100_cigarettes` | 0.0790 | Primary screening signal for Magnesium Deficiency |
| 6 | `exam_pulse_rate` | 0.0766 | Primary screening signal for Magnesium Deficiency |
| 7 | `symptom_poor_appetite` | 0.0583 | Primary screening signal for Magnesium Deficiency |
| 8 | `demo_age_years` | 0.0506 | Primary screening signal for Magnesium Deficiency |
| 9 | `history_arthritis` | 0.0487 | Primary screening signal for Magnesium Deficiency |
| 10 | `demo_education_level` | 0.0383 | Primary screening signal for Magnesium Deficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
