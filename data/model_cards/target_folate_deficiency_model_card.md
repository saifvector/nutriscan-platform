# Clinical Model Card: Folate Deficiency

**Target Identifier**: `target_folate_deficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 7,563 tested participants (Prevalence: 11.41%)  
**Champion Architecture**: **LightGBM**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.6912** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.2130** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.139** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.1560** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.7846** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.2602** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.4344** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.4507** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.0992** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **453** | False Negative: **28** |
| **Predicted Positive (1)** | False Positive: **552** | True Positive: **102** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.6912 | 0.2130 | 0.2602 | 0.7846 | 0.0992 |
| **XGBoost** | Challenger | 0.7030 | 0.2089 | 0.2746 | 0.6231 | 0.1549 |
| **CatBoost** | Challenger | 0.6979 | 0.2071 | 0.2719 | 0.5846 | 0.1984 |
| **ElasticNet_LogisticRegression** | Baseline | 0.6731 | 0.1994 | 0.2621 | 0.5615 | 0.2089 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `supp_folate_dfe_mcg` | 0.1324 | Primary screening signal for Folate Deficiency |
| 2 | `demo_race_ethnicity` | 0.0431 | Primary screening signal for Folate Deficiency |
| 3 | `demo_poverty_ratio` | 0.0253 | Primary screening signal for Folate Deficiency |
| 4 | `diet_folic_acid_mcg` | 0.0193 | Primary screening signal for Folate Deficiency |
| 5 | `exam_systolic_bp` | 0.0171 | Primary screening signal for Folate Deficiency |
| 6 | `diet_selenium_mcg` | 0.0104 | Primary screening signal for Folate Deficiency |
| 7 | `exam_bmi` | 0.0099 | Primary screening signal for Folate Deficiency |
| 8 | `exam_waist_height_ratio` | 0.0096 | Primary screening signal for Folate Deficiency |
| 9 | `diet_thiamin_b1_mg` | 0.0086 | Primary screening signal for Folate Deficiency |
| 10 | `total_calcium_intake_mg` | 0.0086 | Primary screening signal for Folate Deficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
