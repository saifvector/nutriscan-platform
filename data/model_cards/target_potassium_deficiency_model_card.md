# Clinical Model Card: Potassium Deficiency

**Target Identifier**: `target_potassium_deficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 6,281 tested participants (Prevalence: 1.83%)  
**Champion Architecture**: **XGBoost**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.6976** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.0690** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.584** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.0000** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.0000** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.0000** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.0000** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.9968** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.1924** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **923** | False Negative: **17** |
| **Predicted Positive (1)** | False Positive: **3** | True Positive: **0** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.7175 | 0.0452 | 0.0980 | 0.2941 | 0.0201 |
| **XGBoost** | Challenger | 0.6976 | 0.0690 | 0.0000 | 0.0000 | 0.1924 |
| **CatBoost** | Challenger | 0.7433 | 0.0592 | 0.0000 | 0.0000 | 0.2054 |
| **ElasticNet_LogisticRegression** | Baseline | 0.6378 | 0.0534 | 0.0711 | 0.4706 | 0.1830 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `demo_age_years` | 0.1498 | Primary screening signal for Potassium Deficiency |
| 2 | `diet_folic_acid_mcg` | 0.0494 | Primary screening signal for Potassium Deficiency |
| 3 | `exam_height_cm` | 0.0384 | Primary screening signal for Potassium Deficiency |
| 4 | `demo_poverty_ratio` | 0.0338 | Primary screening signal for Potassium Deficiency |
| 5 | `exam_pulse_rate` | 0.0306 | Primary screening signal for Potassium Deficiency |
| 6 | `symptom_phq9_score` | 0.0298 | Primary screening signal for Potassium Deficiency |
| 7 | `demo_race_ethnicity` | 0.0296 | Primary screening signal for Potassium Deficiency |
| 8 | `lifestyle_vigorous_activity_minutes` | 0.0257 | Primary screening signal for Potassium Deficiency |
| 9 | `diet_vitamin_d_mcg` | 0.0215 | Primary screening signal for Potassium Deficiency |
| 10 | `total_folate_intake_mcg` | 0.0201 | Primary screening signal for Potassium Deficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
