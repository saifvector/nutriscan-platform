# Clinical Model Card: Iron Deficiency

**Target Identifier**: `target_iron_deficiency`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 1,950 tested participants (Prevalence: 38.46%)  
**Champion Architecture**: **CatBoost**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.5982** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.4813** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.439** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.4598** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.7080** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.5575** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.6390** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.4778** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.2349** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **86** | False Negative: **33** |
| **Predicted Positive (1)** | False Positive: **94** | True Positive: **80** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.6002 | 0.4698 | 0.5839 | 0.8319 | 0.2322 |
| **XGBoost** | Challenger | 0.6112 | 0.4541 | 0.5385 | 0.6814 | 0.2351 |
| **CatBoost** | Challenger | 0.5982 | 0.4813 | 0.5575 | 0.7080 | 0.2349 |
| **ElasticNet_LogisticRegression** | Baseline | 0.6302 | 0.5426 | 0.5843 | 0.9204 | 0.2321 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `diet_caffeine_mg` | 0.0660 | Primary screening signal for Iron Deficiency |
| 2 | `demo_race_ethnicity` | 0.0650 | Primary screening signal for Iron Deficiency |
| 3 | `demo_education_level` | 0.0439 | Primary screening signal for Iron Deficiency |
| 4 | `exam_weight_kg` | 0.0388 | Primary screening signal for Iron Deficiency |
| 5 | `diet_energy_kcal` | 0.0382 | Primary screening signal for Iron Deficiency |
| 6 | `diet_niacin_b3_mg` | 0.0372 | Primary screening signal for Iron Deficiency |
| 7 | `exam_bmi` | 0.0358 | Primary screening signal for Iron Deficiency |
| 8 | `nar_zinc` | 0.0325 | Primary screening signal for Iron Deficiency |
| 9 | `history_arthritis` | 0.0320 | Primary screening signal for Iron Deficiency |
| 10 | `supp_potassium_mg` | 0.0310 | Primary screening signal for Iron Deficiency |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
