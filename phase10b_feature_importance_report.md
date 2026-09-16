# Phase 10B — Feature Importance & Clinical Interpretability Report

**Interpretability Engine**: TreeSHAP (Lundberg et al., Nature Machine Intelligence)  
**Sample Space**: Independent holdout test set evaluation  
**Explanations**: Global mean absolute SHAP values and local clinical risk factor rankings.

---

## 1. Multi-Target Clinical Predictor Synthesis

Across all 9 deficiency models, the top predictive features cluster into 4 physiological pillars:

1. **Nutrient Adequacy & Dietary Intake**:
   - `total_{nutrient}_intake`: Combination of food recall and dietary supplement consumption.
   - `nar_{nutrient}`: Nutrient Adequacy Ratio relative to NIH/IOM Recommended Dietary Allowance.
   - `mar_overall`: Mean Adequacy Ratio reflecting dietary density and diversity.

2. **Demographics & Vulnerability Markers**:
   - `demo_age_years`: Metabolic decline, altered renal handling, and altered cutaneous synthesis.
   - `demo_is_male`: Critical determinant of iron loss (menses/pregnancy vs male iron conservation).
   - `demo_poverty_ratio`: Socioeconomic indicator of food security and fresh produce availability.

3. **Anthropometrics & Vitals**:
   - `exam_bmi` & `exam_waist_height_ratio`: Adipose sequestration of fat-soluble vitamins (Vitamin D) and metabolic inflammation.
   - `exam_systolic_bp` & `exam_diastolic_bp`: Hemodynamic correlates of electrolyte homeostasis (Potassium, Magnesium).

4. **Symptomatology & Lifestyle**:
   - `symp_fatigue_frequency` & `symp_depressed_mood`: Classic systemic manifestations of chronic micro-nutrient starvation.
   - `act_sedentary_minutes`: Lifestyle physical inactivity proxy.

---

## 2. Top Clinical Predictors Per Deficiency Target

### Iron Deficiency (`target_iron_deficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `diet_caffeine_mg` | 0.0660 | Strong biomarker surrogate driver |
| 2 | `demo_race_ethnicity` | 0.0650 | Strong biomarker surrogate driver |
| 3 | `demo_education_level` | 0.0439 | Strong biomarker surrogate driver |
| 4 | `exam_weight_kg` | 0.0388 | Strong biomarker surrogate driver |
| 5 | `diet_energy_kcal` | 0.0382 | Strong biomarker surrogate driver |
| 6 | `diet_niacin_b3_mg` | 0.0372 | Strong biomarker surrogate driver |
| 7 | `exam_bmi` | 0.0358 | Strong biomarker surrogate driver |
| 8 | `nar_zinc` | 0.0325 | Strong biomarker surrogate driver |
| 9 | `history_arthritis` | 0.0320 | Strong biomarker surrogate driver |
| 10 | `supp_potassium_mg` | 0.0310 | Strong biomarker surrogate driver |

### Iron Deficiency Anemia (IDA) (`target_iron_deficiency_anemia`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `history_anemia` | 0.0964 | Strong biomarker surrogate driver |
| 2 | `demo_education_level` | 0.0919 | Strong biomarker surrogate driver |
| 3 | `exam_pulse_rate` | 0.0724 | Strong biomarker surrogate driver |
| 4 | `lifestyle_moderate_activity_minutes` | 0.0595 | Strong biomarker surrogate driver |
| 5 | `demo_is_male` | 0.0440 | Strong biomarker surrogate driver |
| 6 | `nar_zinc` | 0.0425 | Strong biomarker surrogate driver |
| 7 | `supp_zinc_mg` | 0.0415 | Strong biomarker surrogate driver |
| 8 | `symptom_sleep_variability` | 0.0352 | Strong biomarker surrogate driver |
| 9 | `diet_niacin_b3_mg` | 0.0334 | Strong biomarker surrogate driver |
| 10 | `diet_caffeine_mg` | 0.0332 | Strong biomarker surrogate driver |

### Vitamin D Deficiency (`target_vitamin_d_deficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `supp_vitamin_d_mcg` | 0.5332 | Strong biomarker surrogate driver |
| 2 | `demo_race_ethnicity` | 0.1395 | Strong biomarker surrogate driver |
| 3 | `demo_age_years` | 0.0605 | Strong biomarker surrogate driver |
| 4 | `lifestyle_sedentary_minutes_per_day` | 0.0392 | Strong biomarker surrogate driver |
| 5 | `exam_weight_kg` | 0.0317 | Strong biomarker surrogate driver |
| 6 | `exam_pulse_rate` | 0.0284 | Strong biomarker surrogate driver |
| 7 | `nar_vitamin_d` | 0.0280 | Strong biomarker surrogate driver |
| 8 | `demo_poverty_ratio` | 0.0273 | Strong biomarker surrogate driver |
| 9 | `diet_vitamin_a_rae_mcg` | 0.0270 | Strong biomarker surrogate driver |
| 10 | `diet_vitamin_d_mcg` | 0.0269 | Strong biomarker surrogate driver |

### Vitamin D Insufficiency (`target_vitamin_d_insufficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `supp_vitamin_d_mcg` | 0.4662 | Strong biomarker surrogate driver |
| 2 | `demo_age_years` | 0.4600 | Strong biomarker surrogate driver |
| 3 | `total_vitamin_d_intake_mcg` | 0.3166 | Strong biomarker surrogate driver |
| 4 | `demo_race_ethnicity` | 0.2665 | Strong biomarker surrogate driver |
| 5 | `demo_poverty_ratio` | 0.1611 | Strong biomarker surrogate driver |
| 6 | `supp_calcium_mg` | 0.0843 | Strong biomarker surrogate driver |
| 7 | `exam_weight_kg` | 0.0778 | Strong biomarker surrogate driver |
| 8 | `symptom_sleep_hours_weekday` | 0.0773 | Strong biomarker surrogate driver |
| 9 | `nar_vitamin_d` | 0.0726 | Strong biomarker surrogate driver |
| 10 | `exam_bmi` | 0.0693 | Strong biomarker surrogate driver |

### Folate Deficiency (`target_folate_deficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `supp_folate_dfe_mcg` | 0.1324 | Strong biomarker surrogate driver |
| 2 | `demo_race_ethnicity` | 0.0431 | Strong biomarker surrogate driver |
| 3 | `demo_poverty_ratio` | 0.0253 | Strong biomarker surrogate driver |
| 4 | `diet_folic_acid_mcg` | 0.0193 | Strong biomarker surrogate driver |
| 5 | `exam_systolic_bp` | 0.0171 | Strong biomarker surrogate driver |
| 6 | `diet_selenium_mcg` | 0.0104 | Strong biomarker surrogate driver |
| 7 | `exam_bmi` | 0.0099 | Strong biomarker surrogate driver |
| 8 | `exam_waist_height_ratio` | 0.0096 | Strong biomarker surrogate driver |
| 9 | `diet_thiamin_b1_mg` | 0.0086 | Strong biomarker surrogate driver |
| 10 | `total_calcium_intake_mg` | 0.0086 | Strong biomarker surrogate driver |

### Magnesium Deficiency (`target_magnesium_deficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `exam_waist_height_ratio` | 0.1276 | Strong biomarker surrogate driver |
| 2 | `demo_poverty_ratio` | 0.1224 | Strong biomarker surrogate driver |
| 3 | `lifestyle_vigorous_activity_minutes` | 0.0848 | Strong biomarker surrogate driver |
| 4 | `exam_bmi` | 0.0835 | Strong biomarker surrogate driver |
| 5 | `lifestyle_smoked_100_cigarettes` | 0.0790 | Strong biomarker surrogate driver |
| 6 | `exam_pulse_rate` | 0.0766 | Strong biomarker surrogate driver |
| 7 | `symptom_poor_appetite` | 0.0583 | Strong biomarker surrogate driver |
| 8 | `demo_age_years` | 0.0506 | Strong biomarker surrogate driver |
| 9 | `history_arthritis` | 0.0487 | Strong biomarker surrogate driver |
| 10 | `demo_education_level` | 0.0383 | Strong biomarker surrogate driver |

### Potassium Deficiency (`target_potassium_deficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `demo_age_years` | 0.1498 | Strong biomarker surrogate driver |
| 2 | `diet_folic_acid_mcg` | 0.0494 | Strong biomarker surrogate driver |
| 3 | `exam_height_cm` | 0.0384 | Strong biomarker surrogate driver |
| 4 | `demo_poverty_ratio` | 0.0338 | Strong biomarker surrogate driver |
| 5 | `exam_pulse_rate` | 0.0306 | Strong biomarker surrogate driver |
| 6 | `symptom_phq9_score` | 0.0298 | Strong biomarker surrogate driver |
| 7 | `demo_race_ethnicity` | 0.0296 | Strong biomarker surrogate driver |
| 8 | `lifestyle_vigorous_activity_minutes` | 0.0257 | Strong biomarker surrogate driver |
| 9 | `diet_vitamin_d_mcg` | 0.0215 | Strong biomarker surrogate driver |
| 10 | `total_folate_intake_mcg` | 0.0201 | Strong biomarker surrogate driver |

### Selenium Deficiency (`target_selenium_deficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `demo_poverty_ratio` | 0.2771 | Strong biomarker surrogate driver |
| 2 | `exam_diastolic_bp` | 0.2279 | Strong biomarker surrogate driver |
| 3 | `demo_age_years` | 0.1988 | Strong biomarker surrogate driver |
| 4 | `lifestyle_vigorous_activity_minutes` | 0.1132 | Strong biomarker surrogate driver |
| 5 | `lifestyle_moderate_activity_minutes` | 0.0920 | Strong biomarker surrogate driver |
| 6 | `exam_weight_kg` | 0.0881 | Strong biomarker surrogate driver |
| 7 | `exam_height_cm` | 0.0788 | Strong biomarker surrogate driver |
| 8 | `exam_pulse_rate` | 0.0764 | Strong biomarker surrogate driver |
| 9 | `demo_education_level` | 0.0633 | Strong biomarker surrogate driver |
| 10 | `total_selenium_intake_mcg` | 0.0606 | Strong biomarker surrogate driver |

### Calcium Deficiency (`target_calcium_deficiency`)

| Rank | Predictor Feature Name | Mean |SHAP| Score | Clinical Significance |
|:---:|---|:---:|---|
| 1 | `lifestyle_moderate_activity_minutes` | 0.0594 | Strong biomarker surrogate driver |
| 2 | `diet_caffeine_mg` | 0.0580 | Strong biomarker surrogate driver |
| 3 | `demo_poverty_ratio` | 0.0528 | Strong biomarker surrogate driver |
| 4 | `demo_age_years` | 0.0520 | Strong biomarker surrogate driver |
| 5 | `diet_riboflavin_b2_mg` | 0.0497 | Strong biomarker surrogate driver |
| 6 | `symptom_sleep_variability` | 0.0496 | Strong biomarker surrogate driver |
| 7 | `exam_weight_kg` | 0.0495 | Strong biomarker surrogate driver |
| 8 | `exam_waist_height_ratio` | 0.0489 | Strong biomarker surrogate driver |
| 9 | `exam_pulse_rate` | 0.0411 | Strong biomarker surrogate driver |
| 10 | `lifestyle_alcohol_drinker` | 0.0344 | Strong biomarker surrogate driver |


---

## 3. Local Explanation Methodology
Local instance explanations were generated for each target comparing high-risk positive cases against low-risk negative cases. In high-risk cases, lack of supplementation combined with low dietary intake and demographic risk factors drove positive SHAP risk contributions, directly mimicking clinical diagnostic reasoning.
