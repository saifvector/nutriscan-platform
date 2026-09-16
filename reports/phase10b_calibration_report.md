# Phase 10B — Probability Calibration & Reliability Report

**Method**: Platt Scaling (Logistic Sigmoid Regression) fitted on Validation set and evaluated on Holdout Test set.  
**Diagnostic Metrics**: Brier Score Loss & Expected Calibration Error (ECE) across 10 probability bins.

---

## 1. Calibration Results Across All 9 Deficiency Targets

| Target Deficiency | Champion Model | Raw Brier Score | Calibrated Brier Score | Raw ECE | Calibrated ECE | Calibration Assessment |
|---|---|:---:|:---:|:---:|:---:|---|
| **Iron Deficiency** | Logistic Regression | 0.2321 | **0.2292** | 0.1112 | **0.0489** | Reliable empirical alignment |
| **Iron Deficiency Anemia** | Random Forest | 0.1753 | **0.1277** | 0.2073 | **0.0152** | Reliable empirical alignment |
| **Vitamin D Deficiency** | XGBoost | 0.1693 | **0.1305** | 0.1866 | **0.0342** | Reliable empirical alignment |
| **Vitamin D Insufficiency** | XGBoost | 0.1738 | **0.1743** | 0.0382 | **0.0383** | Reliable empirical alignment |
| **Folate Deficiency** | Random Forest | 0.1767 | **0.0960** | 0.2615 | **0.0203** | Reliable empirical alignment |
| **Magnesium Deficiency** | Logistic Regression | 0.2039 | **0.0787** | 0.3278 | **0.0166** | Reliable empirical alignment |
| **Selenium Deficiency** | Logistic Regression | 0.1795 | **0.0319** | 0.3186 | **0.0028** | Reliable empirical alignment |
| **Potassium Deficiency** | Random Forest | 0.0912 | **0.0176** | 0.2401 | **0.0000** | Reliable empirical alignment |
| **Calcium Deficiency** | XGBoost | 0.1383 | **0.0073** | 0.3586 | **0.0001** | Reliable empirical alignment |

---

## 2. Clinical Impact of Calibration

1. **Elimination of Extreme Overconfidence**:
   - Gradient boosted trees trained with severe `scale_pos_weight` often output shifted probability scores.
   - Platt scaling recalibrates predicted scores back into true population prevalence odds.
2. **Actionable Risk Communication**:
   - Post-calibration ECE is $< 0.05$ for all targets, ensuring that a patient assigned a 40% deficiency risk truly has an approximate 4-in-10 probability of biomarker-confirmed deficiency.
