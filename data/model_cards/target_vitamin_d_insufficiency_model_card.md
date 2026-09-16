# Clinical Model Card: Vitamin D Insufficiency

**Target Identifier**: `target_vitamin_d_insufficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 7,307 tested participants (Prevalence: 53.37%)  
**Champion Architecture**: **LightGBM**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.8130** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.8227** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.338** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.6775** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.9215** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.7809** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.8596** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.4971** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.1750** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **254** | False Negative: **46** |
| **Predicted Positive (1)** | False Positive: **257** | True Positive: **540** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.8130 | 0.8227 | 0.7809 | 0.9215 | 0.1750 |
| **XGBoost** | Challenger | 0.8159 | 0.8214 | 0.7869 | 0.9044 | 0.1738 |
| **CatBoost** | Challenger | 0.8127 | 0.8239 | 0.7717 | 0.8857 | 0.1757 |
| **ElasticNet_LogisticRegression** | Baseline | 0.7997 | 0.7892 | 0.7721 | 0.8703 | 0.1812 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `supp_vitamin_d_mcg` | 0.4662 | Primary screening signal for Vitamin D Insufficiency |
| 2 | `demo_age_years` | 0.4600 | Primary screening signal for Vitamin D Insufficiency |
| 3 | `total_vitamin_d_intake_mcg` | 0.3166 | Primary screening signal for Vitamin D Insufficiency |
| 4 | `demo_race_ethnicity` | 0.2665 | Primary screening signal for Vitamin D Insufficiency |
| 5 | `demo_poverty_ratio` | 0.1611 | Primary screening signal for Vitamin D Insufficiency |
| 6 | `supp_calcium_mg` | 0.0843 | Primary screening signal for Vitamin D Insufficiency |
| 7 | `exam_weight_kg` | 0.0778 | Primary screening signal for Vitamin D Insufficiency |
| 8 | `symptom_sleep_hours_weekday` | 0.0773 | Primary screening signal for Vitamin D Insufficiency |
| 9 | `nar_vitamin_d` | 0.0726 | Primary screening signal for Vitamin D Insufficiency |
| 10 | `exam_bmi` | 0.0693 | Primary screening signal for Vitamin D Insufficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
