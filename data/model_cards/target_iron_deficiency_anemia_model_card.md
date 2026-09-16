# Clinical Model Card: Iron Deficiency Anemia (IDA)

**Target Identifier**: `target_iron_deficiency_anemia`  
**Clinical Ground Truth**: NHANES Laboratory Biomarker Gold Standard  
**Evaluated Cohort**: N = 1,945 tested participants (Prevalence: 15.32%)  
**Champion Architecture**: **CatBoost**  
**Evaluation Protocol**: 70% Train / 15% Validation / 15% Holdout Test (Stratified)

---

## 1. Primary Test Set Performance (Holdout Set)

| Metric | Score | Clinical Interpretation |
|---|:---:|---|
| **ROC-AUC** | **0.6412** | Discrimination capacity across all possible screening thresholds. |
| **PR-AUC** | **0.2768** | Precision-Recall curve area (benchmark for imbalanced clinical classes). |
| **Optimal Threshold** | **0.449** | Decision cutoff optimized via validation set F1 maximization. |
| **Precision (PPV)** | **0.2035** | True deficiency probability when model flags high risk. |
| **Recall (Sensitivity)** | **0.5111** | Proportion of true deficient individuals successfully identified. |
| **F1-Score** | **0.2911** | Harmonic mean of precision and recall. |
| **F2-Score** | **0.3925** | Recall-weighted clinical utility score (penalizing false negatives). |
| **Specificity** | **0.6356** | Proportion of healthy individuals correctly spared alarm. |
| **Brier Score Loss** | **0.2013** | Probability calibration accuracy (lower is superior). |

---

## 2. Test Set Confusion Matrix

| | Actual Negative (0) | Actual Positive (1) |
|---|:---:|:---:|
| **Predicted Negative (0)** | True Negative: **157** | False Negative: **22** |
| **Predicted Positive (1)** | False Positive: **90** | True Positive: **23** |

---

## 3. Multi-Model Evaluation Summary (Test Set)

| Model Architecture | Role | ROC-AUC | PR-AUC | F1 (opt) | Recall | Brier Score |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM** | Champion | 0.6128 | 0.2481 | 0.2500 | 0.2444 | 0.1291 |
| **XGBoost** | Challenger | 0.6496 | 0.2368 | 0.3220 | 0.7333 | 0.1951 |
| **CatBoost** | Challenger | 0.6412 | 0.2768 | 0.2911 | 0.5111 | 0.2013 |
| **ElasticNet_LogisticRegression** | Baseline | 0.6182 | 0.2389 | 0.2883 | 0.3556 | 0.2110 |

---

## 4. Top 10 Clinical Risk Drivers (Global SHAP Importance)

| Rank | Clinical Feature | Mean |SHAP| Value | Biological / Clinical Mechanism |
|---|---|:---:|---|
| 1 | `history_anemia` | 0.0964 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 2 | `demo_education_level` | 0.0919 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 3 | `exam_pulse_rate` | 0.0724 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 4 | `lifestyle_moderate_activity_minutes` | 0.0595 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 5 | `demo_is_male` | 0.0440 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 6 | `nar_zinc` | 0.0425 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 7 | `supp_zinc_mg` | 0.0415 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 8 | `symptom_sleep_variability` | 0.0352 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 9 | `diet_niacin_b3_mg` | 0.0334 | Primary screening signal for Iron Deficiency Anemia (IDA) |
| 10 | `diet_caffeine_mg` | 0.0332 | Primary screening signal for Iron Deficiency Anemia (IDA) |

---

## 5. Clinical Safety & Intended Use

- **Intended Use**: Population health triage, preventative dietary screening, and personalized nutritional guidance.
- **Contraindications**: This model is NOT a diagnostic laboratory test. It does NOT replace serum venipuncture or physician evaluation.
- **Fairness & Subpopulation Safety**: Evaluated across diverse demographics (NHANES multi-ethnic survey). Missing data handled natively by decision trees.
