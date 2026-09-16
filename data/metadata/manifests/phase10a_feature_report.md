# Phase 10A Feature Engineering Audit Report

**Execution Timestamp**: 2026-09-13 20:19:44
**Total Features Engineered**: 105
**Total Participant Cohort**: 11,933

## 1. Feature Domain Breakdown

| Feature Category | Count | Primary Source Tables | Key Derived Metrics |
|---|:---:|---|---|
| **Demographics & Socioeconomics** | 7 | `DEMO_L` | Age, Gender, Race/Ethnicity, Poverty-Income Ratio, Education |
| **Anthropometrics & Physical Vitals** | 7 | `BMX_L`, `BPXO_L` | BMI, Waist-to-Height Ratio, Mean Systolic/Diastolic BP, Pulse |
| **Dietary Recalls (2-Day Averaged)** | 35 | `DR1TOT_L`, `DR2TOT_L` | Macronutrients, Fiber, Micronutrients, Carotenoids, Minerals |
| **Dietary Supplements** | 13 | `DSQTOT_L` | 30-day supplement use flag, elemental nutrient supplement amounts |
| **Total Combined Intakes** | 10 | Diet + Supplements | Unified daily intake totals for 10 key micro-nutrients |
| **NIH Nutrient Adequacy Ratios (NAR)** | 11 | Intakes / NIH RDAs | Sex/age/pregnancy adjusted NARs (0.0 to 2.0) + Composite Mean Adequacy Ratio |
| **Clinical Symptoms & Mental Health** | 7 | `DPQ_L`, `SLQ_L` | PHQ-9 composite score, Fatigue, Poor Appetite, Sleep hours/apnea |
| **Lifestyle & Physical Activity** | 7 | `DBQ_L`, `PAQ_L`, `ALQ_L`, `SMQ_L` | Fast food frequency, Sedentary minutes/day, Alcohol, Smoking |
| **Medical Diagnoses History** | 5 | `MCQ_L` | Prior Anemia, Thyroid condition, Liver disease, Bone fracture |

## 2. Top Informative Features (Summary Statistics)

| Feature Name | Domain | Non-Null N | Mean ± Std | Range [Min, Max] | Missing % |
|---|---|:---:|:---:|:---:|:---:|
| `demo_age_years` | Demographics  | 11,933 | 38.32 | [0.0, 80.0] | 0.0% |
| `demo_is_male` | Demographics  | 11,933 | 0.47 | [0.0, 1.0] | 0.0% |
| `demo_race_ethnicity` | Demographics  | 11,933 | 3.32 | [1.0, 7.0] | 0.0% |
| `demo_education_level` | Demographics  | 7,783 | 3.8 | [1.0, 5.0] | 34.78% |
| `demo_poverty_ratio` | Demographics  | 9,892 | 2.71 | [0.0, 5.0] | 17.1% |
| `demo_household_size` | Demographics  | 11,933 | 3.24 | [1.0, 7.0] | 0.0% |
| `demo_is_pregnant` | Demographics  | 11,933 | 0.0 | [0.0, 1.0] | 0.0% |
| `exam_height_cm` | Anthropometrics  | 8,499 | 159.66 | [79.1, 200.7] | 28.78% |
| `exam_weight_kg` | Anthropometrics  | 8,754 | 70.55 | [2.7, 248.2] | 26.64% |
| `exam_bmi` | Anthropometrics  | 8,471 | 27.25 | [11.1, 74.8] | 29.01% |
| `exam_waist_cm` | Anthropometrics  | 8,190 | 92.12 | [39.8, 187.0] | 31.37% |
| `exam_waist_height_ratio` | Anthropometrics  | 8,174 | 0.57 | [0.34, 1.05] | 31.5% |
| `exam_systolic_bp` | Anthropometrics  | 7,518 | 119.09 | [70.0, 232.33] | 37.0% |
| `exam_diastolic_bp` | Anthropometrics  | 7,518 | 72.21 | [34.0, 139.0] | 37.0% |
| `exam_pulse_rate` | Anthropometrics  | 7,518 | 73.04 | [34.0, 151.0] | 37.0% |
| `diet_energy_kcal` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 1927.81 | [0.0, 10446.0] | 43.89% |
| `diet_protein_g` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 70.94 | [0.0, 348.46] | 43.89% |
| `diet_carbohydrate_g` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 223.92 | [0.0, 1300.94] | 43.89% |
| `diet_sugar_g` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 96.49 | [0.0, 835.1] | 43.89% |
| `diet_fiber_g` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 15.54 | [0.0, 117.3] | 43.89% |
| `diet_total_fat_g` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 80.57 | [0.0, 505.62] | 43.89% |
| `diet_saturated_fat_g` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 26.16 | [0.0, 208.84] | 43.89% |
| `diet_cholesterol_mg` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 293.86 | [0.0, 3598.0] | 43.89% |
| `diet_iron_mg` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 12.31 | [0.0, 103.83] | 43.89% |
| `diet_calcium_mg` | Dietary Nutrient Intakes (2-Day Recall) | 6,696 | 886.42 | [0.0, 6061.5] | 43.89% |
