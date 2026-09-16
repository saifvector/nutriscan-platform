# Clinical Model Card: Calcium Deficiency

**Target Identifier**: `target_calcium_deficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 6,362 tested participants (Prevalence: 0.72%)  
**Champion Architecture**: **XGBoost**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.7595** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.0366** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.595** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.0000** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.0000** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.0000** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.0000** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.9958** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.1383** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **944** | False Negative: **7** |
| **Predicted Positive (1)** | False Positive: **4** | True Positive: **0** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.7387 | 0.0181 | 0.0000 | 0.0000 | 0.0090 |
| **XGBoost** | Challenger | 0.7595 | 0.0366 | 0.0000 | 0.0000 | 0.1383 |
| **CatBoost** | Challenger | 0.4030 | 0.0069 | 0.0066 | 0.1429 | 0.2312 |
| **ElasticNet_LogisticRegression** | Baseline | 0.6267 | 0.0147 | 0.0000 | 0.0000 | 0.1212 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `lifestyle_moderate_activity_minutes` | 0.0594 | Primary screening signal for Calcium Deficiency |
| 2 | `diet_caffeine_mg` | 0.0580 | Primary screening signal for Calcium Deficiency |
| 3 | `demo_poverty_ratio` | 0.0528 | Primary screening signal for Calcium Deficiency |
| 4 | `demo_age_years` | 0.0520 | Primary screening signal for Calcium Deficiency |
| 5 | `diet_riboflavin_b2_mg` | 0.0497 | Primary screening signal for Calcium Deficiency |
| 6 | `symptom_sleep_variability` | 0.0496 | Primary screening signal for Calcium Deficiency |
| 7 | `exam_weight_kg` | 0.0495 | Primary screening signal for Calcium Deficiency |
| 8 | `exam_waist_height_ratio` | 0.0489 | Primary screening signal for Calcium Deficiency |
| 9 | `exam_pulse_rate` | 0.0411 | Primary screening signal for Calcium Deficiency |
| 10 | `lifestyle_alcohol_drinker` | 0.0344 | Primary screening signal for Calcium Deficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
