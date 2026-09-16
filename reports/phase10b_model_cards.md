# Phase 10B — Production Clinical Model Cards

This document provides standardized, clinical-grade model cards for the 9 champion deficiency prediction models.

---

## Clinical Model Card: Iron Deficiency

- **Model Identifier**: `best_target_iron_deficiency.joblib`
- **Target Variable**: `target_iron_deficiency`
- **Champion Architecture**: **Logistic Regression**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.6302**
- **PR-AUC**: **0.5426**
- **Balanced Accuracy**: **0.5741**
- **Sensitivity (Recall)**: **0.9204**
- **Specificity**: **0.2278**
- **F1 Score**: **0.5843**
- **Optimal Decision Cutoff**: **0.331**
- **Brier Score (Calibrated)**: **0.2292**
- **ECE (Calibrated)**: **0.0489**

### Confusion Matrix (Test Set)
- True Negatives: **41** | False Positives: **139**
- False Negatives: **9** | True Positives: **104**

### Top 5 Clinical Predictors (SHAP)
1. `diet_carbohydrate_g` (Mean |SHAP|: 0.1833)
2. `diet_caffeine_mg` (Mean |SHAP|: 0.1277)
3. `total_zinc_intake_mg` (Mean |SHAP|: 0.1197)
4. `diet_niacin_b3_mg` (Mean |SHAP|: 0.1186)
5. `exam_waist_height_ratio` (Mean |SHAP|: 0.1080)

---

## Clinical Model Card: Iron Deficiency Anemia

- **Model Identifier**: `best_target_iron_deficiency_anemia.joblib`
- **Target Variable**: `target_iron_deficiency_anemia`
- **Champion Architecture**: **Random Forest**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.6461**
- **PR-AUC**: **0.2400**
- **Balanced Accuracy**: **0.6077**
- **Sensitivity (Recall)**: **0.5556**
- **Specificity**: **0.6599**
- **F1 Score**: **0.3247**
- **Optimal Decision Cutoff**: **0.402**
- **Brier Score (Calibrated)**: **0.1277**
- **ECE (Calibrated)**: **0.0152**

### Confusion Matrix (Test Set)
- True Negatives: **163** | False Positives: **84**
- False Negatives: **20** | True Positives: **25**

### Top 5 Clinical Predictors (SHAP)
1. `demo_education_level` (Mean |SHAP|: 0.0185)
2. `exam_height_cm` (Mean |SHAP|: 0.0146)
3. `history_anemia` (Mean |SHAP|: 0.0139)
4. `demo_household_size` (Mean |SHAP|: 0.0137)
5. `demo_age_years` (Mean |SHAP|: 0.0111)

---

## Clinical Model Card: Vitamin D Deficiency

- **Model Identifier**: `best_target_vitamin_d_deficiency.joblib`
- **Target Variable**: `target_vitamin_d_deficiency`
- **Champion Architecture**: **XGBoost**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.8262**
- **PR-AUC**: **0.5331**
- **Balanced Accuracy**: **0.7360**
- **Sensitivity (Recall)**: **0.6822**
- **Specificity**: **0.7898**
- **F1 Score**: **0.5571**
- **Optimal Decision Cutoff**: **0.558**
- **Brier Score (Calibrated)**: **0.1305**
- **ECE (Calibrated)**: **0.0342**

### Confusion Matrix (Test Set)
- True Negatives: **680** | False Positives: **181**
- False Negatives: **75** | True Positives: **161**

### Top 5 Clinical Predictors (SHAP)
1. `supp_vitamin_d_mcg` (Mean |SHAP|: 0.5449)
2. `demo_race_ethnicity` (Mean |SHAP|: 0.2757)
3. `total_vitamin_d_intake_mcg` (Mean |SHAP|: 0.1802)
4. `demo_age_years` (Mean |SHAP|: 0.1051)
5. `nar_vitamin_d` (Mean |SHAP|: 0.0744)

---

## Clinical Model Card: Vitamin D Insufficiency

- **Model Identifier**: `best_target_vitamin_d_insufficiency.joblib`
- **Target Variable**: `target_vitamin_d_insufficiency`
- **Champion Architecture**: **XGBoost**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.8159**
- **PR-AUC**: **0.8214**
- **Balanced Accuracy**: **0.7262**
- **Sensitivity (Recall)**: **0.9044**
- **Specificity**: **0.5479**
- **F1 Score**: **0.7869**
- **Optimal Decision Cutoff**: **0.383**
- **Brier Score (Calibrated)**: **0.1743**
- **ECE (Calibrated)**: **0.0383**

### Confusion Matrix (Test Set)
- True Negatives: **280** | False Positives: **231**
- False Negatives: **56** | True Positives: **530**

### Top 5 Clinical Predictors (SHAP)
1. `demo_age_years` (Mean |SHAP|: 0.4357)
2. `supp_vitamin_d_mcg` (Mean |SHAP|: 0.4135)
3. `demo_race_ethnicity` (Mean |SHAP|: 0.2374)
4. `total_vitamin_d_intake_mcg` (Mean |SHAP|: 0.2035)
5. `demo_poverty_ratio` (Mean |SHAP|: 0.1556)

---

## Clinical Model Card: Folate Deficiency

- **Model Identifier**: `best_target_folate_deficiency.joblib`
- **Target Variable**: `target_folate_deficiency`
- **Champion Architecture**: **Random Forest**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.7123**
- **PR-AUC**: **0.2331**
- **Balanced Accuracy**: **0.6253**
- **Sensitivity (Recall)**: **0.5462**
- **Specificity**: **0.7045**
- **F1 Score**: **0.2851**
- **Optimal Decision Cutoff**: **0.492**
- **Brier Score (Calibrated)**: **0.0960**
- **ECE (Calibrated)**: **0.0203**

### Confusion Matrix (Test Set)
- True Negatives: **708** | False Positives: **297**
- False Negatives: **59** | True Positives: **71**

### Top 5 Clinical Predictors (SHAP)
1. `demo_race_ethnicity` (Mean |SHAP|: 0.0230)
2. `supp_folate_dfe_mcg` (Mean |SHAP|: 0.0182)
3. `demo_poverty_ratio` (Mean |SHAP|: 0.0180)
4. `supp_vitamin_b6_mg` (Mean |SHAP|: 0.0152)
5. `supp_zinc_mg` (Mean |SHAP|: 0.0143)

---

## Clinical Model Card: Magnesium Deficiency

- **Model Identifier**: `best_target_magnesium_deficiency.joblib`
- **Target Variable**: `target_magnesium_deficiency`
- **Champion Architecture**: **Logistic Regression**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.7293**
- **PR-AUC**: **0.2100**
- **Balanced Accuracy**: **0.6581**
- **Sensitivity (Recall)**: **0.5517**
- **Specificity**: **0.7645**
- **F1 Score**: **0.2840**
- **Optimal Decision Cutoff**: **0.567**
- **Brier Score (Calibrated)**: **0.0787**
- **ECE (Calibrated)**: **0.0166**

### Confusion Matrix (Test Set)
- True Negatives: **659** | False Positives: **203**
- False Negatives: **39** | True Positives: **48**

### Top 5 Clinical Predictors (SHAP)
1. `demo_is_male` (Mean |SHAP|: 0.3425)
2. `demo_age_years` (Mean |SHAP|: 0.2925)
3. `exam_pulse_rate` (Mean |SHAP|: 0.2513)
4. `total_magnesium_intake_mg` (Mean |SHAP|: 0.2450)
5. `diet_protein_g` (Mean |SHAP|: 0.2349)

---

## Clinical Model Card: Selenium Deficiency

- **Model Identifier**: `best_target_selenium_deficiency.joblib`
- **Target Variable**: `target_selenium_deficiency`
- **Champion Architecture**: **Logistic Regression**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.7707**
- **PR-AUC**: **0.1307**
- **Balanced Accuracy**: **0.6432**
- **Sensitivity (Recall)**: **0.3846**
- **Specificity**: **0.9017**
- **F1 Score**: **0.1852**
- **Optimal Decision Cutoff**: **0.725**
- **Brier Score (Calibrated)**: **0.0319**
- **ECE (Calibrated)**: **0.0028**

### Confusion Matrix (Test Set)
- True Negatives: **991** | False Positives: **108**
- False Negatives: **24** | True Positives: **15**

### Top 5 Clinical Predictors (SHAP)
1. `exam_weight_kg` (Mean |SHAP|: 0.8563)
2. `diet_choline_mg` (Mean |SHAP|: 0.4986)
3. `diet_selenium_mcg` (Mean |SHAP|: 0.4533)
4. `exam_bmi` (Mean |SHAP|: 0.4371)
5. `nar_vitamin_c` (Mean |SHAP|: 0.4077)

---

## Clinical Model Card: Potassium Deficiency

- **Model Identifier**: `best_target_potassium_deficiency.joblib`
- **Target Variable**: `target_potassium_deficiency`
- **Champion Architecture**: **Random Forest**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.7383**
- **PR-AUC**: **0.0612**
- **Balanced Accuracy**: **0.6718**
- **Sensitivity (Recall)**: **0.7647**
- **Specificity**: **0.5788**
- **F1 Score**: **0.0619**
- **Optimal Decision Cutoff**: **0.274**
- **Brier Score (Calibrated)**: **0.0176**
- **ECE (Calibrated)**: **0.0000**

### Confusion Matrix (Test Set)
- True Negatives: **536** | False Positives: **390**
- False Negatives: **4** | True Positives: **13**

### Top 5 Clinical Predictors (SHAP)
1. `demo_age_years` (Mean |SHAP|: 0.0623)
2. `demo_is_male` (Mean |SHAP|: 0.0233)
3. `diet_folic_acid_mcg` (Mean |SHAP|: 0.0169)
4. `demo_race_ethnicity` (Mean |SHAP|: 0.0140)
5. `symptom_phq9_score` (Mean |SHAP|: 0.0122)

---

## Clinical Model Card: Calcium Deficiency

- **Model Identifier**: `best_target_calcium_deficiency.joblib`
- **Target Variable**: `target_calcium_deficiency`
- **Champion Architecture**: **XGBoost**
- **Validation Standard**: Stratified 5-Fold Cross-Validation + 15% Holdout Test

### Primary Performance Metrics (Holdout Test)
- **ROC-AUC**: **0.7595**
- **PR-AUC**: **0.0366**
- **Balanced Accuracy**: **0.4979**
- **Sensitivity (Recall)**: **0.0000**
- **Specificity**: **0.9958**
- **F1 Score**: **0.0000**
- **Optimal Decision Cutoff**: **0.595**
- **Brier Score (Calibrated)**: **0.0073**
- **ECE (Calibrated)**: **0.0001**

### Confusion Matrix (Test Set)
- True Negatives: **944** | False Positives: **4**
- False Negatives: **7** | True Positives: **0**

### Top 5 Clinical Predictors (SHAP)
1. `lifestyle_moderate_activity_minutes` (Mean |SHAP|: 0.0594)
2. `diet_caffeine_mg` (Mean |SHAP|: 0.0580)
3. `demo_poverty_ratio` (Mean |SHAP|: 0.0528)
4. `demo_age_years` (Mean |SHAP|: 0.0520)
5. `diet_riboflavin_b2_mg` (Mean |SHAP|: 0.0497)

---
