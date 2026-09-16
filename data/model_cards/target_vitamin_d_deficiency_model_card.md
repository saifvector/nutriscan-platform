# Clinical Model Card: Vitamin D Deficiency

**Target Identifier**: `target_vitamin_d_deficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 7,307 tested participants (Prevalence: 21.53%)  
**Champion Architecture**: **LightGBM**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.8191** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.5375** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.367** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.4246** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.7754** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.5487** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.6655** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.7120** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.1459** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **613** | False Negative: **53** |
| **Predicted Positive (1)** | False Positive: **248** | True Positive: **183** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.8191 | 0.5375 | 0.5487 | 0.7754 | 0.1459 |
| **XGBoost** | Challenger | 0.8262 | 0.5331 | 0.5571 | 0.6822 | 0.1693 |
| **CatBoost** | Challenger | 0.8266 | 0.5400 | 0.5533 | 0.8136 | 0.1746 |
| **ElasticNet_LogisticRegression** | Baseline | 0.8102 | 0.4916 | 0.5418 | 0.8093 | 0.1853 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `supp_vitamin_d_mcg` | 0.5332 | Primary screening signal for Vitamin D Deficiency |
| 2 | `demo_race_ethnicity` | 0.1395 | Primary screening signal for Vitamin D Deficiency |
| 3 | `demo_age_years` | 0.0605 | Primary screening signal for Vitamin D Deficiency |
| 4 | `lifestyle_sedentary_minutes_per_day` | 0.0392 | Primary screening signal for Vitamin D Deficiency |
| 5 | `exam_weight_kg` | 0.0317 | Primary screening signal for Vitamin D Deficiency |
| 6 | `exam_pulse_rate` | 0.0284 | Primary screening signal for Vitamin D Deficiency |
| 7 | `nar_vitamin_d` | 0.0280 | Primary screening signal for Vitamin D Deficiency |
| 8 | `demo_poverty_ratio` | 0.0273 | Primary screening signal for Vitamin D Deficiency |
| 9 | `diet_vitamin_a_rae_mcg` | 0.0270 | Primary screening signal for Vitamin D Deficiency |
| 10 | `diet_vitamin_d_mcg` | 0.0269 | Primary screening signal for Vitamin D Deficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
