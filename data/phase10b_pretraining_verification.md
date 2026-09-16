# Phase 10B — Pre-Training Verification Audit Report

**Audit Date**: 2026-09-13  
**Evaluated Artifact**: `data/merged_training_dataset.parquet` (Version 10A Master)  
**Dataset Architecture**: 11,933 Rows × 125 Columns  
**Audit Purpose**: Independent pre-flight data verification prior to Phase 10B model training  
**Status**: **PASSED — ALL GATES VERIFIED**

---

## 1. Missing Data Report

### 1.1 Predictor Feature Missingness (105 Total Features)

| Missingness Range | Feature Count | Percentage of Feature Space | Feature Domain Representation | Clinical Handling Strategy |
|---|:---:|:---:|---|---|
| **$\le$ 30% Missing** | **50** | **47.6%** | Demographics (`demo_*`), Anthropometrics (`exam_height`, `weight`, `bmi`), 2-Day Dietary Recall, Total Nutrients, Nutrient Adequacy Ratios (NAR) | Retain 100%. Complete or high-density core features. |
| **30% – 50% Missing** | **49** | **46.7%** | Clinical Questionnaires administered solely to adults aged $\ge 20$ (`DPQ_L` depression, `SLQ_L` sleep disturbance, `PAQ_L` physical activity) | Retain 100%. Handled natively via Tree NaN routing (optimal split-finding). |
| **50% – 80% Missing** | **3** | **2.9%** | Age-gated diagnostic items (`demo_pregnancy_months`, `symp_sleep_apnea_diagnosed`, `symp_trouble_sleeping`) | Retain with native tree branching. |
| **> 80% Missing** | **3** | **2.9%** | Rare sub-questionnaire items (`diet_days_recalled`, `symp_snoring_freq`, `symp_snort_stop_breathing`) | Retain with native tree branching or drop for linear models. |

### 1.2 Target Label Missingness

In the NHANES epidemiological protocol, biological specimens are collected from specific age-eligible subsamples (e.g., serum ferritin is restricted to pre-menopausal females and young children, while serum biochemistry is drawn on participants $\ge 12$ years).

| Target Identifier | Tested (Valid Non-Null) | Uncollected (Missing) | Missing Rate (%) | Clinical Protocol Reason |
|---|:---:|:---:|:---:|---|
| `target_iron_deficiency` | **1,950** | 9,983 | 83.7% | CDC NHANES ferritin protocol restricts testing to females 12–49 & children 1–5 |
| `target_iron_deficiency_anemia` | **1,945** | 9,988 | 83.7% | Concurrent Ferritin + Complete Blood Count hemoglobin testing |
| `target_vitamin_d_deficiency` | **7,307** | 4,626 | 38.8% | 25(OH)D testing in all mobile examination center (MEC) participants $\ge 1$ year |
| `target_vitamin_d_insufficiency` | **7,307** | 4,626 | 38.8% | 25(OH)D testing in all mobile examination center (MEC) participants $\ge 1$ year |
| `target_folate_deficiency` | **7,563** | 4,370 | 36.6% | Serum & RBC folate assayed in participants $\ge 1$ year |
| `target_magnesium_deficiency` | **6,324** | 5,609 | 47.0% | Standard biochemistry profile drawn on participants $\ge 12$ years |
| `target_potassium_deficiency` | **6,281** | 5,652 | 47.4% | Standard biochemistry profile drawn on participants $\ge 12$ years |
| `target_selenium_deficiency` | **7,586** | 4,347 | 36.4% | Whole blood trace elements assayed in participants $\ge 1$ year |
| `target_calcium_deficiency` | **6,362** | 5,571 | 46.7% | Standard biochemistry profile drawn on participants $\ge 12$ years |

### 1.3 Participant Retention Waterfall

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ 1. Master Enrolled Cohort (Demographics Complete)                                 │
│    N = 11,933 participants (100.0%)                                               │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │  - 3,196 excluded (did not attend MEC)
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ 2. Mobile Examination Center (MEC) Examined Cohort                                │
│    N = 8,737 participants (73.2%) [Anthropometrics, Vitals, Exam Weights]         │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │  - Age-eligibility protocol partitions
                                         ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ 3. Laboratory Biomarker Subsamples (Gold-Standard Clinical Target Cohorts)        │
│    ├─ Whole Blood Selenium Subsample:        N = 7,586 (63.6%)                    │
│    ├─ Serum & RBC Folate Subsample:          N = 7,563 (63.4%)                    │
│    ├─ 25(OH)D Vitamin D Subsample:           N = 7,307 (61.2%)                    │
│    ├─ Serum Biochemistry Profile (Mg, K, Ca):N = 6,362 (53.3%)                    │
│    └─ Serum Ferritin / Iron Subsample:       N = 1,950 (16.3%)                    │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Leakage Verification

### 2.1 Complete Quarantine of Excluded Laboratory Variables
The following laboratory assay panels from NHANES were completely excluded from the predictor feature space to eliminate target contamination:

1. **Direct Target Biomarkers (Quarantined Exclusively to Targets)**:
   - `LBXFER` (Serum Ferritin)
   - `LBXHGB` (Hemoglobin)
   - `LBXHCT` (Hematocrit)
   - `LBXVIDMS` (25-Hydroxyvitamin D Total)
   - `LBDRFO` (Red Blood Cell Folate)
   - `LBDFOT` (Serum Total Folate)
   - `LBXMAGN` (Serum Magnesium)
   - `LBXSKSI` (Serum Potassium)
   - `LBXSCA` (Serum Total Calcium)
   - `LBXBSE` (Whole Blood Selenium)

2. **Excluded Ancillary Laboratory Panels (Not in Predictors)**:
   - **Complete Blood Count (CBC)**: `LBXWBCSI`, `LBXRBCSI`, `LBXMCVSI`, `LBXMCHSI`, `LBXMC`, `LBXRDW`, `LBXPLTSI`.
   - **Biochemistry Profile (BIOPRO)**: `LBXSNASI` (Sodium), `LBXSCLSI` (Chloride), `LBXSC3SI` (Bicarbonate), `LBXSBU` (BUN), `LBXSCR` (Creatinine), `LBXSUA` (Uric Acid), `LBXSGL` (Glucose), `LBXSTP` (Total Protein), `LBXSAL` (Albumin), `LBXSTB` (Bilirubin), `LBXSATSI` (ALT), `LBXSASSI` (AST), `LBXSCK` (CPK), `LBXSAPSI` (Alkaline Phosphatase), `LBXSLDSI` (LDH), `LBXSPH` (Phosphorus).
   - **Trace Elements & Metals (PBCD)**: `LBXBPB` (Blood Lead), `LBXBCD` (Blood Cadmium), `LBXTHG` (Mercury), `LBXBMA` (Manganese).
   - **Lipid Profile**: Total Cholesterol, HDL, Triglycerides, LDL.
   - **Urinary Assays**: Urine Albumin, Urine Creatinine, Urine Iodine, Urine Heavy Metals.

### 2.2 Formal Leakage Boundary Verification Tests

| Verification Test | Verification Criteria | Result | Status |
|---|---|:---:|:---:|
| **Laboratory Prefix Scan** | 0 features starting with `LBX`, `LBD`, `URX`, `URD` | **0 Violations** | **PASSED** |
| **Direct Target Name Scan** | 0 features with target name matches | **0 Violations** | **PASSED** |
| **Biomarker Token Scan** | 0 features containing clinical assay tokens | **0 Violations** | **PASSED** |
| **Correlation Ceiling Check** | Max Pearson $\|r\|$ between feature and target $< 0.70$ | **Max $r = +0.490$** | **PASSED** |

---

## 3. Class Imbalance Report

| Target Label | Usable Cohort (N) | Positive Cases | Negative Cases | Prevalence (%) | Severity Tier | Recommended `scale_pos_weight` ($N_{neg} / N_{pos}$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`target_iron_deficiency`** | 1,950 | 750 | 1,200 | **38.46%** | Mild (Well-Balanced) | **1.60** |
| **`target_iron_deficiency_anemia`** | 1,945 | 298 | 1,647 | **15.32%** | Moderate | **5.53** |
| **`target_vitamin_d_deficiency`** | 7,307 | 1,573 | 5,734 | **21.53%** | Mild | **3.65** |
| **`target_vitamin_d_insufficiency`** | 7,307 | 3,900 | 3,407 | **53.37%** | Balanced | **0.87** |
| **`target_folate_deficiency`** | 7,563 | 863 | 6,700 | **11.41%** | Moderate | **7.76** |
| **`target_magnesium_deficiency`** | 6,324 | 582 | 5,742 | **9.20%** | Significant | **9.87** |
| **`target_potassium_deficiency`** | 6,281 | 115 | 6,166 | **1.83%** | Extreme (Rare Event) | **53.62** |
| **`target_selenium_deficiency`** | 7,586 | 257 | 7,329 | **3.39%** | Significant | **28.52** |
| **`target_calcium_deficiency`** | 6,362 | 46 | 6,316 | **0.72%** | Extreme (Rare Event) | **137.30** |

---

## 4. Correlation Audit & Multicollinearity Findings

### Feature Pairs with Pearson $\|r\| > 0.95$

Across the 105 engineered predictor features ($105 \times 104 / 2 = 5,460$ pairwise comparisons), exactly **7 pairs** exhibit $\|r\| > 0.95$:

| Rank | Feature 1 | Feature 2 | Pearson $\|r\|$ | Clinical / Mathematical Explanation |
|:---:|---|---|:---:|---|
| 1 | `supp_vitamin_b12_mcg` | `total_vitamin_b12_intake_mcg` | **0.9999** | Vitamin B12 supplements provide orders of magnitude higher dose than food intake; total is dominated by supplement. |
| 2 | `diet_potassium_mg` | `total_potassium_intake_mg` | **0.9975** | Potassium supplements are FDA-limited to 99 mg; dietary intake constitutes $>99\%$ of total intake. |
| 3 | `supp_vitamin_d_mcg` | `total_vitamin_d_intake_mcg` | **0.9934** | Typical food vitamin D is low; supplement consumers derive nearly all vitamin D from supplements. |
| 4 | `total_calcium_intake_mg` | `nar_calcium` | **0.9823** | `nar_calcium` is a linear scaling of total calcium relative to age/sex Recommended Dietary Allowance ($RDA$). |
| 5 | `total_potassium_intake_mg` | `nar_potassium` | **0.9799** | `nar_potassium` is a linear scaling of total potassium relative to the Adequate Intake ($AI$). |
| 6 | `total_magnesium_intake_mg` | `nar_magnesium` | **0.9707** | `nar_magnesium` is a linear scaling of total magnesium relative to the $RDA$. |
| 7 | `supp_vitamin_c_mg` | `total_vitamin_c_intake_mg` | **0.9573** | High-dose vitamin C supplements dominate composite intake. |

### Recommended Collinearity Strategy:
1. **Tree-Based Models (LightGBM, XGBoost, CatBoost)**: **Retain all features**. Collinear features do not degrade gradient boosting accuracy or tree partitioning performance; tree splits select the feature that maximizes information gain in that sub-region.
2. **Linear / Logistic Regression Baselines**: Use **ElasticNet / L1 Lasso penalty** ($l_1\_ratio = 0.5$). The L1 penalty automatically drives redundant coefficients to zero, eliminating collinear inflation.

---

## 5. Training Readiness Audit

| Audit Dimension | Metric Value | Readiness Evaluation |
|---|:---:|---|
| **Predictor Features** | **105 features** | Broad multi-modal coverage: Demographics, Vitals, Diet, Supplements, Adequacy Ratios, Symptoms |
| **Deficiency Targets** | **9 binary targets** (+ 8 continuous targets) | Clinically grounded in WHO/NIH laboratory diagnostic cutoffs |
| **Usable Rows Per Target** | **1,945 to 7,586 rows** | Ample sample size for tabular gradient boosting |
| **Parquet Storage on Disk** | **2.49 MB** | Compact, column-oriented Snappy compressed storage |
| **In-Memory DataFrame RAM** | **11.38 MB** | Ultra-lightweight footprint; easily fits into standard memory |
| **Full 5-Fold Training Runtime** | **~100–120 seconds total** | ~10–15 seconds per target across all 4 model architectures |

---

## 6. Phase 10B Go / No-Go Decision

# 🟢 GO FOR PHASE 10B

### Justification:
1. **Zero Contamination**: Complete quarantine of all laboratory assay variables and target biomarkers is mathematically verified.
2. **Clinical Sample Sufficiency**: Positive case counts provide high statistical power for primary deficiency targets ($>750$ Iron, $>1,500$ Vitamin D, $>860$ Folate, $>580$ Magnesium).
3. **Loss Weighting Calibrated**: Imbalance schedules (`scale_pos_weight`) are locked to counteract severe imbalances on rare targets.
4. **Hardware & Execution Efficiency**: 11.4 MB memory footprint enables sub-2-minute end-to-end multi-model training and cross-validation.
