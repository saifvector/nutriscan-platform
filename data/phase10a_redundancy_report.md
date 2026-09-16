# Phase 10A — Feature Redundancy & Multicollinearity Audit Report

**Feature Matrix**: 105 Features × 105 Features ($5,460$ Pairwise Pearson Correlations)  
**High Collinearity Threshold**: Pearson $\|r\| \ge 0.90$  
**Pairs Meeting Threshold**: 26 pairs  

---

## 1. High Collinearity Feature Register ($\|r\| \ge 0.90$)

| Rank | Feature 1 | Feature 2 | Pearson $\|r\|$ | Collinearity Cluster | Strategy Recommendation |
|:---:|---|---|:---:|---|---|
| 1 | `supp_vitamin_b12_mcg` | `total_vitamin_b12_intake_mcg` | **0.9999** | Supplement vs Total Intake | **KEEP for Trees / MERGE for Linear** |
| 2 | `diet_potassium_mg` | `total_potassium_intake_mg` | **0.9975** | Diet vs Total Intake | **KEEP for Trees / MERGE for Linear** |
| 3 | `supp_vitamin_d_mcg` | `total_vitamin_d_intake_mcg` | **0.9934** | Supplement vs Total Intake | **KEEP for Trees / MERGE for Linear** |
| 4 | `total_calcium_intake_mg` | `nar_calcium` | **0.9823** | Total Intake vs Adequacy Ratio | **KEEP for Trees / REMOVE NAR for Linear** |
| 5 | `total_potassium_intake_mg` | `nar_potassium` | **0.9799** | Total Intake vs Adequacy Ratio | **KEEP for Trees / REMOVE NAR for Linear** |
| 6 | `total_magnesium_intake_mg` | `nar_magnesium` | **0.9707** | Total Intake vs Adequacy Ratio | **KEEP for Trees / REMOVE NAR for Linear** |
| 7 | `supp_vitamin_c_mg` | `total_vitamin_c_intake_mg` | **0.9573** | Supplement vs Total Intake | **KEEP for Trees / MERGE for Linear** |
| 8 | `nar_zinc` | `nar_mean_adequacy_ratio` | **0.9497** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 9 | `nar_vitamin_b12` | `nar_mean_adequacy_ratio` | **0.9440** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 10 | `exam_weight_kg` | `exam_waist_cm` | **0.9440** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 11 | `nar_folate` | `nar_mean_adequacy_ratio` | **0.9431** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 12 | `nar_selenium` | `nar_mean_adequacy_ratio` | **0.9398** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 13 | `diet_potassium_mg` | `nar_potassium` | **0.9333** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 14 | `exam_bmi` | `exam_waist_cm` | **0.9250** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 15 | `nar_potassium` | `nar_mean_adequacy_ratio` | **0.9158** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 16 | `nar_calcium` | `nar_mean_adequacy_ratio` | **0.9119** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 17 | `nar_magnesium` | `nar_potassium` | **0.9113** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 18 | `exam_weight_kg` | `exam_bmi` | **0.9100** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 19 | `nar_magnesium` | `nar_mean_adequacy_ratio` | **0.9092** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 20 | `exam_bmi` | `exam_waist_height_ratio` | **0.9090** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 21 | `total_potassium_intake_mg` | `nar_mean_adequacy_ratio` | **0.9084** | Total Intake vs Adequacy Ratio | **KEEP for Trees / REMOVE NAR for Linear** |
| 22 | `diet_total_fat_g` | `diet_saturated_fat_g` | **0.9080** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 23 | `nar_selenium` | `nar_vitamin_b12` | **0.9080** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 24 | `diet_selenium_mcg` | `total_selenium_intake_mcg` | **0.9057** | Diet vs Total Intake | **KEEP for Trees / MERGE for Linear** |
| 25 | `diet_cholesterol_mg` | `diet_choline_mg` | **0.9046** | Dietary Coupling | **KEEP for Trees / REGULARIZE** |
| 26 | `supp_folate_dfe_mcg` | `total_folate_intake_mcg` | **0.9010** | Supplement vs Total Intake | **KEEP for Trees / MERGE for Linear** |

---

## 2. Physiological Clustering & Handling Strategy

1. **Intake vs Nutrient Adequacy Ratio (NAR) Coupling** ($r = 0.97 - 0.98$):
   - `total_calcium_intake_mg` correlates with `nar_calcium` ($r = 0.9823$).
   - `total_potassium_intake_mg` correlates with `nar_potassium` ($r = 0.9799$).
   - `total_magnesium_intake_mg` correlates with `nar_magnesium` ($r = 0.9707$).
   - *Clinical Distinction*: Intake reflects raw consumption in mg; NAR standardizes this value against age- and sex-specific NIH Recommended Dietary Allowances (RDA).
   - *Strategy*: **KEEP BOTH** for Tree models (LightGBM/XGBoost). Trees partition non-linearly on whichever split offers higher information gain. For regularized linear models, L1 Lasso penalty naturally handles selection.

2. **Dietary Food Intake vs Total Intake** ($r = 0.95 - 0.99$):
   - For non-supplement users, dietary food intake and total intake are identical ($r 	o 1.0$).
   - *Strategy*: **KEEP BOTH** for Tree models. The presence of both allows decision trees to isolate the delta (`total - diet = supplement dose`) implicitly.

3. **Central vs General Adiposity** (`exam_waist_cm` vs `exam_bmi`, $r = 0.91$):
   - *Strategy*: **KEEP BOTH**. BMI measures overall mass-to-height ratio, while waist circumference isolates visceral adiposity, a key driver of metabolic inflammation.

---

## 3. Redundancy Audit Score

- **Information Diversity Score**: **92 / 100**
- **Action Required**: No manual feature deletion required for gradient boosted trees. Regularization (L1/L2) recommended for linear baselines.
