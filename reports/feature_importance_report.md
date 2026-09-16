# Phase 10B — Feature Importance & SHAP Ranking Report

**Interpretability Framework**: TreeSHAP (Lundberg et al., Nature Machine Intelligence)  
**Scope**: Top 20 clinical predictor rankings for each of the 9 nutrient deficiency models.  
**Dataset Evaluation**: Evaluated on independent holdout test cohort.

---

## 1. Cross-Nutrient Global Predictor Summary

Across all 9 deficiency models, the top predictors reflect four foundational physiological domains:
1. **Direct Intake & Adequacy Ratios**: `total_{nutrient}_intake`, `nar_{nutrient}`, and dietary supplement dosages.
2. **Demographics**: `demo_age_years`, `demo_is_male`, `demo_race_ethnicity`, and `demo_poverty_ratio`.
3. **Anthropometrics & Hemodynamics**: `exam_bmi`, `exam_waist_height_ratio`, `exam_systolic_bp`, and `exam_pulse_rate`.
4. **Clinical Symptoms & Lifestyle**: `history_anemia`, `symp_fatigue_frequency`, `lifestyle_sedentary_minutes_per_day`, and smoking.

---

## 2. Top 20 Clinical Predictors Per Deficiency Target

### Iron Deficiency (`target_iron_deficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `diet_carbohydrate_g` | 0.1833 | Primary screening signal for Iron Deficiency |
| 2 | `diet_caffeine_mg` | 0.1277 | Primary screening signal for Iron Deficiency |
| 3 | `total_zinc_intake_mg` | 0.1197 | Primary screening signal for Iron Deficiency |
| 4 | `diet_niacin_b3_mg` | 0.1186 | Primary screening signal for Iron Deficiency |
| 5 | `exam_waist_height_ratio` | 0.1080 | Primary screening signal for Iron Deficiency |
| 6 | `exam_height_cm` | 0.1049 | Primary screening signal for Iron Deficiency |
| 7 | `supp_potassium_mg` | 0.0990 | Primary screening signal for Iron Deficiency |
| 8 | `diet_iron_mg` | 0.0961 | Primary screening signal for Iron Deficiency |
| 9 | `nar_vitamin_c` | 0.0910 | Primary screening signal for Iron Deficiency |
| 10 | `nar_folate` | 0.0893 | Primary screening signal for Iron Deficiency |
| 11 | `symptom_sleep_variability` | 0.0886 | Primary screening signal for Iron Deficiency |
| 12 | `symptom_poor_appetite` | 0.0882 | Primary screening signal for Iron Deficiency |
| 13 | `lifestyle_sedentary_minutes_per_day` | 0.0727 | Primary screening signal for Iron Deficiency |
| 14 | `demo_age_years` | 0.0725 | Primary screening signal for Iron Deficiency |
| 15 | `demo_race_ethnicity` | 0.0705 | Primary screening signal for Iron Deficiency |
| 16 | `history_anemia` | 0.0678 | Primary screening signal for Iron Deficiency |
| 17 | `symptom_short_sleep` | 0.0601 | Primary screening signal for Iron Deficiency |
| 18 | `history_arthritis` | 0.0537 | Primary screening signal for Iron Deficiency |
| 19 | `lifestyle_main_meal_planner` | 0.0522 | Primary screening signal for Iron Deficiency |
| 20 | `demo_is_male` | 0.0504 | Primary screening signal for Iron Deficiency |

### Iron Deficiency Anemia (`target_iron_deficiency_anemia`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `demo_education_level` | 0.0185 | Primary screening signal for Iron Deficiency Anemia |
| 2 | `exam_height_cm` | 0.0146 | Primary screening signal for Iron Deficiency Anemia |
| 3 | `history_anemia` | 0.0139 | Primary screening signal for Iron Deficiency Anemia |
| 4 | `demo_household_size` | 0.0137 | Primary screening signal for Iron Deficiency Anemia |
| 5 | `demo_age_years` | 0.0111 | Primary screening signal for Iron Deficiency Anemia |
| 6 | `exam_weight_kg` | 0.0104 | Primary screening signal for Iron Deficiency Anemia |
| 7 | `demo_is_male` | 0.0101 | Primary screening signal for Iron Deficiency Anemia |
| 8 | `demo_poverty_ratio` | 0.0095 | Primary screening signal for Iron Deficiency Anemia |
| 9 | `exam_diastolic_bp` | 0.0083 | Primary screening signal for Iron Deficiency Anemia |
| 10 | `exam_waist_cm` | 0.0078 | Primary screening signal for Iron Deficiency Anemia |
| 11 | `diet_caffeine_mg` | 0.0076 | Primary screening signal for Iron Deficiency Anemia |
| 12 | `diet_sugar_g` | 0.0073 | Primary screening signal for Iron Deficiency Anemia |
| 13 | `symptom_sleep_variability` | 0.0067 | Primary screening signal for Iron Deficiency Anemia |
| 14 | `lifestyle_moderate_activity_minutes` | 0.0060 | Primary screening signal for Iron Deficiency Anemia |
| 15 | `supp_calcium_mg` | 0.0058 | Primary screening signal for Iron Deficiency Anemia |
| 16 | `supp_vitamin_d_mcg` | 0.0058 | Primary screening signal for Iron Deficiency Anemia |
| 17 | `demo_race_ethnicity` | 0.0055 | Primary screening signal for Iron Deficiency Anemia |
| 18 | `supp_vitamin_b12_mcg` | 0.0051 | Primary screening signal for Iron Deficiency Anemia |
| 19 | `symptom_phq9_score` | 0.0051 | Primary screening signal for Iron Deficiency Anemia |
| 20 | `supp_vitamin_b6_mg` | 0.0050 | Primary screening signal for Iron Deficiency Anemia |

### Vitamin D Deficiency (`target_vitamin_d_deficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `supp_vitamin_d_mcg` | 0.5449 | Primary screening signal for Vitamin D Deficiency |
| 2 | `demo_race_ethnicity` | 0.2757 | Primary screening signal for Vitamin D Deficiency |
| 3 | `total_vitamin_d_intake_mcg` | 0.1802 | Primary screening signal for Vitamin D Deficiency |
| 4 | `demo_age_years` | 0.1051 | Primary screening signal for Vitamin D Deficiency |
| 5 | `nar_vitamin_d` | 0.0744 | Primary screening signal for Vitamin D Deficiency |
| 6 | `demo_poverty_ratio` | 0.0594 | Primary screening signal for Vitamin D Deficiency |
| 7 | `exam_pulse_rate` | 0.0577 | Primary screening signal for Vitamin D Deficiency |
| 8 | `lifestyle_sedentary_minutes_per_day` | 0.0489 | Primary screening signal for Vitamin D Deficiency |
| 9 | `exam_weight_kg` | 0.0474 | Primary screening signal for Vitamin D Deficiency |
| 10 | `exam_bmi` | 0.0418 | Primary screening signal for Vitamin D Deficiency |
| 11 | `diet_vitamin_d_mcg` | 0.0402 | Primary screening signal for Vitamin D Deficiency |
| 12 | `symptom_sleep_variability` | 0.0309 | Primary screening signal for Vitamin D Deficiency |
| 13 | `diet_retinol_mcg` | 0.0266 | Primary screening signal for Vitamin D Deficiency |
| 14 | `exam_waist_height_ratio` | 0.0249 | Primary screening signal for Vitamin D Deficiency |
| 15 | `exam_waist_cm` | 0.0242 | Primary screening signal for Vitamin D Deficiency |
| 16 | `supp_uses_supplements` | 0.0241 | Primary screening signal for Vitamin D Deficiency |
| 17 | `history_arthritis` | 0.0218 | Primary screening signal for Vitamin D Deficiency |
| 18 | `diet_vitamin_a_rae_mcg` | 0.0192 | Primary screening signal for Vitamin D Deficiency |
| 19 | `supp_vitamin_c_mg` | 0.0190 | Primary screening signal for Vitamin D Deficiency |
| 20 | `diet_calcium_mg` | 0.0168 | Primary screening signal for Vitamin D Deficiency |

### Vitamin D Insufficiency (`target_vitamin_d_insufficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `demo_age_years` | 0.4357 | Primary screening signal for Vitamin D Insufficiency |
| 2 | `supp_vitamin_d_mcg` | 0.4135 | Primary screening signal for Vitamin D Insufficiency |
| 3 | `demo_race_ethnicity` | 0.2374 | Primary screening signal for Vitamin D Insufficiency |
| 4 | `total_vitamin_d_intake_mcg` | 0.2035 | Primary screening signal for Vitamin D Insufficiency |
| 5 | `demo_poverty_ratio` | 0.1556 | Primary screening signal for Vitamin D Insufficiency |
| 6 | `nar_vitamin_d` | 0.1409 | Primary screening signal for Vitamin D Insufficiency |
| 7 | `exam_weight_kg` | 0.0819 | Primary screening signal for Vitamin D Insufficiency |
| 8 | `symptom_sleep_hours_weekday` | 0.0707 | Primary screening signal for Vitamin D Insufficiency |
| 9 | `symptom_sleep_variability` | 0.0679 | Primary screening signal for Vitamin D Insufficiency |
| 10 | `exam_bmi` | 0.0667 | Primary screening signal for Vitamin D Insufficiency |
| 11 | `exam_waist_height_ratio` | 0.0544 | Primary screening signal for Vitamin D Insufficiency |
| 12 | `supp_calcium_mg` | 0.0497 | Primary screening signal for Vitamin D Insufficiency |
| 13 | `diet_caffeine_mg` | 0.0447 | Primary screening signal for Vitamin D Insufficiency |
| 14 | `diet_retinol_mcg` | 0.0344 | Primary screening signal for Vitamin D Insufficiency |
| 15 | `lifestyle_moderate_activity_minutes` | 0.0339 | Primary screening signal for Vitamin D Insufficiency |
| 16 | `demo_is_male` | 0.0304 | Primary screening signal for Vitamin D Insufficiency |
| 17 | `lifestyle_sedentary_minutes_per_day` | 0.0290 | Primary screening signal for Vitamin D Insufficiency |
| 18 | `symptom_sleep_hours_weekend` | 0.0247 | Primary screening signal for Vitamin D Insufficiency |
| 19 | `diet_vitamin_a_rae_mcg` | 0.0219 | Primary screening signal for Vitamin D Insufficiency |
| 20 | `demo_education_level` | 0.0205 | Primary screening signal for Vitamin D Insufficiency |

### Folate Deficiency (`target_folate_deficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `demo_race_ethnicity` | 0.0230 | Primary screening signal for Folate Deficiency |
| 2 | `supp_folate_dfe_mcg` | 0.0182 | Primary screening signal for Folate Deficiency |
| 3 | `demo_poverty_ratio` | 0.0180 | Primary screening signal for Folate Deficiency |
| 4 | `supp_vitamin_b6_mg` | 0.0152 | Primary screening signal for Folate Deficiency |
| 5 | `supp_zinc_mg` | 0.0143 | Primary screening signal for Folate Deficiency |
| 6 | `supp_vitamin_b12_mcg` | 0.0135 | Primary screening signal for Folate Deficiency |
| 7 | `supp_vitamin_c_mg` | 0.0133 | Primary screening signal for Folate Deficiency |
| 8 | `nar_folate` | 0.0120 | Primary screening signal for Folate Deficiency |
| 9 | `total_folate_intake_mcg` | 0.0097 | Primary screening signal for Folate Deficiency |
| 10 | `exam_waist_height_ratio` | 0.0090 | Primary screening signal for Folate Deficiency |
| 11 | `diet_folic_acid_mcg` | 0.0078 | Primary screening signal for Folate Deficiency |
| 12 | `supp_iodine_mcg` | 0.0070 | Primary screening signal for Folate Deficiency |
| 13 | `demo_age_years` | 0.0066 | Primary screening signal for Folate Deficiency |
| 14 | `nar_vitamin_d` | 0.0062 | Primary screening signal for Folate Deficiency |
| 15 | `exam_height_cm` | 0.0061 | Primary screening signal for Folate Deficiency |
| 16 | `nar_mean_adequacy_ratio` | 0.0059 | Primary screening signal for Folate Deficiency |
| 17 | `supp_vitamin_d_mcg` | 0.0059 | Primary screening signal for Folate Deficiency |
| 18 | `diet_fiber_g` | 0.0055 | Primary screening signal for Folate Deficiency |
| 19 | `exam_waist_cm` | 0.0049 | Primary screening signal for Folate Deficiency |
| 20 | `total_vitamin_d_intake_mcg` | 0.0048 | Primary screening signal for Folate Deficiency |

### Magnesium Deficiency (`target_magnesium_deficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `demo_is_male` | 0.3425 | Primary screening signal for Magnesium Deficiency |
| 2 | `demo_age_years` | 0.2925 | Primary screening signal for Magnesium Deficiency |
| 3 | `exam_pulse_rate` | 0.2513 | Primary screening signal for Magnesium Deficiency |
| 4 | `total_magnesium_intake_mg` | 0.2450 | Primary screening signal for Magnesium Deficiency |
| 5 | `diet_protein_g` | 0.2349 | Primary screening signal for Magnesium Deficiency |
| 6 | `lifestyle_smoked_100_cigarettes` | 0.2090 | Primary screening signal for Magnesium Deficiency |
| 7 | `nar_calcium` | 0.1963 | Primary screening signal for Magnesium Deficiency |
| 8 | `exam_diastolic_bp` | 0.1924 | Primary screening signal for Magnesium Deficiency |
| 9 | `exam_bmi` | 0.1838 | Primary screening signal for Magnesium Deficiency |
| 10 | `nar_zinc` | 0.1754 | Primary screening signal for Magnesium Deficiency |
| 11 | `diet_phosphorus_mg` | 0.1623 | Primary screening signal for Magnesium Deficiency |
| 12 | `nar_magnesium` | 0.1610 | Primary screening signal for Magnesium Deficiency |
| 13 | `diet_sodium_mg` | 0.1596 | Primary screening signal for Magnesium Deficiency |
| 14 | `exam_systolic_bp` | 0.1549 | Primary screening signal for Magnesium Deficiency |
| 15 | `demo_poverty_ratio` | 0.1462 | Primary screening signal for Magnesium Deficiency |
| 16 | `diet_saturated_fat_g` | 0.1407 | Primary screening signal for Magnesium Deficiency |
| 17 | `demo_education_level` | 0.1254 | Primary screening signal for Magnesium Deficiency |
| 18 | `diet_fiber_g` | 0.1133 | Primary screening signal for Magnesium Deficiency |
| 19 | `diet_caffeine_mg` | 0.1121 | Primary screening signal for Magnesium Deficiency |
| 20 | `lifestyle_sedentary_minutes_per_day` | 0.1076 | Primary screening signal for Magnesium Deficiency |

### Potassium Deficiency (`target_potassium_deficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `demo_age_years` | 0.0623 | Primary screening signal for Potassium Deficiency |
| 2 | `demo_is_male` | 0.0233 | Primary screening signal for Potassium Deficiency |
| 3 | `diet_folic_acid_mcg` | 0.0169 | Primary screening signal for Potassium Deficiency |
| 4 | `demo_race_ethnicity` | 0.0140 | Primary screening signal for Potassium Deficiency |
| 5 | `symptom_phq9_score` | 0.0122 | Primary screening signal for Potassium Deficiency |
| 6 | `exam_height_cm` | 0.0116 | Primary screening signal for Potassium Deficiency |
| 7 | `demo_education_level` | 0.0089 | Primary screening signal for Potassium Deficiency |
| 8 | `diet_vitamin_d_mcg` | 0.0083 | Primary screening signal for Potassium Deficiency |
| 9 | `total_folate_intake_mcg` | 0.0080 | Primary screening signal for Potassium Deficiency |
| 10 | `total_magnesium_intake_mg` | 0.0062 | Primary screening signal for Potassium Deficiency |
| 11 | `exam_pulse_rate` | 0.0059 | Primary screening signal for Potassium Deficiency |
| 12 | `demo_poverty_ratio` | 0.0059 | Primary screening signal for Potassium Deficiency |
| 13 | `supp_magnesium_mg` | 0.0055 | Primary screening signal for Potassium Deficiency |
| 14 | `diet_beta_carotene_mcg` | 0.0052 | Primary screening signal for Potassium Deficiency |
| 15 | `total_vitamin_c_intake_mg` | 0.0050 | Primary screening signal for Potassium Deficiency |
| 16 | `diet_vitamin_e_mg` | 0.0049 | Primary screening signal for Potassium Deficiency |
| 17 | `nar_vitamin_c` | 0.0049 | Primary screening signal for Potassium Deficiency |
| 18 | `symptom_sleep_hours_weekend` | 0.0049 | Primary screening signal for Potassium Deficiency |
| 19 | `diet_vitamin_b6_mg` | 0.0047 | Primary screening signal for Potassium Deficiency |
| 20 | `exam_waist_height_ratio` | 0.0046 | Primary screening signal for Potassium Deficiency |

### Selenium Deficiency (`target_selenium_deficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
| 1 | `exam_weight_kg` | 0.8563 | Primary screening signal for Selenium Deficiency |
| 2 | `diet_choline_mg` | 0.4986 | Primary screening signal for Selenium Deficiency |
| 3 | `diet_selenium_mcg` | 0.4533 | Primary screening signal for Selenium Deficiency |
| 4 | `exam_bmi` | 0.4371 | Primary screening signal for Selenium Deficiency |
| 5 | `nar_vitamin_c` | 0.4077 | Primary screening signal for Selenium Deficiency |
| 6 | `nar_zinc` | 0.3982 | Primary screening signal for Selenium Deficiency |
| 7 | `diet_thiamin_b1_mg` | 0.3896 | Primary screening signal for Selenium Deficiency |
| 8 | `demo_age_years` | 0.3594 | Primary screening signal for Selenium Deficiency |
| 9 | `nar_folate` | 0.3038 | Primary screening signal for Selenium Deficiency |
| 10 | `diet_calcium_mg` | 0.2868 | Primary screening signal for Selenium Deficiency |
| 11 | `diet_vitamin_e_mg` | 0.2663 | Primary screening signal for Selenium Deficiency |
| 12 | `nar_magnesium` | 0.2624 | Primary screening signal for Selenium Deficiency |
| 13 | `nar_calcium` | 0.2607 | Primary screening signal for Selenium Deficiency |
| 14 | `demo_poverty_ratio` | 0.2551 | Primary screening signal for Selenium Deficiency |
| 15 | `diet_zinc_mg` | 0.2521 | Primary screening signal for Selenium Deficiency |
| 16 | `total_selenium_intake_mcg` | 0.2473 | Primary screening signal for Selenium Deficiency |
| 17 | `exam_diastolic_bp` | 0.2288 | Primary screening signal for Selenium Deficiency |
| 18 | `diet_energy_kcal` | 0.2090 | Primary screening signal for Selenium Deficiency |
| 19 | `history_arthritis` | 0.2013 | Primary screening signal for Selenium Deficiency |
| 20 | `supp_uses_supplements` | 0.1999 | Primary screening signal for Selenium Deficiency |

### Calcium Deficiency (`target_calcium_deficiency`)

| Rank | Feature Identifier | Mean |SHAP| Value | Domain / Clinical Interpretation |
|:---:|---|:---:|---|
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
| 11 | `diet_calcium_mg` | 0.0297 | Primary screening signal for Calcium Deficiency |
| 12 | `diet_copper_mg` | 0.0281 | Primary screening signal for Calcium Deficiency |
| 13 | `diet_iron_mg` | 0.0271 | Primary screening signal for Calcium Deficiency |
| 14 | `exam_waist_cm` | 0.0228 | Primary screening signal for Calcium Deficiency |
| 15 | `lifestyle_sedentary_minutes_per_day` | 0.0213 | Primary screening signal for Calcium Deficiency |
| 16 | `diet_cholesterol_mg` | 0.0207 | Primary screening signal for Calcium Deficiency |
| 17 | `diet_alcohol_g` | 0.0196 | Primary screening signal for Calcium Deficiency |
| 18 | `total_vitamin_b12_intake_mcg` | 0.0180 | Primary screening signal for Calcium Deficiency |
| 19 | `demo_race_ethnicity` | 0.0177 | Primary screening signal for Calcium Deficiency |
| 20 | `diet_vitamin_k_mcg` | 0.0176 | Primary screening signal for Calcium Deficiency |

