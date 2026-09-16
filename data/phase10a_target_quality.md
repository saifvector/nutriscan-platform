# Phase 10A — Target Quality & Class Balance Audit Report

**Evaluated Targets**: 9 Clinical Deficiency Binary Labels  
**Ground Truth Reference**: CDC NHANES Venous Blood Draws & Standard Laboratory Diagnostic Cutoffs  
**Audit Purpose**: Analyze class balance, sample sufficiency, loss weighting schedules, and modeling difficulty tiers.

---

## 1. Deficiency Target Summary & Imbalance Tiers

| Target Identifier | Clinical Name | Tested Sample Size | Positive Cases | Negative Cases | Prevalence (%) | Recommended `scale_pos_weight` | Imbalance Tier |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| `target_iron_deficiency` | **Iron Deficiency** | 1,950 | 750 | 1,200 | **38.46%** | **1.60** | EASY (Well-Balanced) |
| `target_iron_deficiency_anemia` | **Iron Deficiency Anemia** | 1,945 | 298 | 1,647 | **15.32%** | **5.53** | MODERATE |
| `target_vitamin_d_deficiency` | **Vitamin D Deficiency** | 7,307 | 1,573 | 5,734 | **21.53%** | **3.65** | MODERATE |
| `target_vitamin_d_insufficiency` | **Vitamin D Insufficiency** | 7,307 | 3,900 | 3,407 | **53.37%** | **0.87** | EASY (Well-Balanced) |
| `target_folate_deficiency` | **Folate Deficiency** | 7,563 | 863 | 6,700 | **11.41%** | **7.76** | MODERATE |
| `target_magnesium_deficiency` | **Magnesium Deficiency** | 6,324 | 582 | 5,742 | **9.20%** | **9.87** | HARD (Significant Imbalance) |
| `target_potassium_deficiency` | **Potassium Deficiency** | 6,281 | 115 | 6,166 | **1.83%** | **53.62** | EXTREME IMBALANCE (Rare Event) |
| `target_selenium_deficiency` | **Selenium Deficiency** | 7,586 | 257 | 7,329 | **3.39%** | **28.52** | HARD (Significant Imbalance) |
| `target_calcium_deficiency` | **Calcium Deficiency** | 6,362 | 46 | 6,316 | **0.72%** | **137.30** | EXTREME IMBALANCE (Rare Event) |

---

## 2. Modeling Difficulty Analysis

### Tier 1: EASY (Prevalence $\ge 30\%$)
- **`target_vitamin_d_insufficiency`** (53.37%): Perfectly balanced class distribution. No weight adjustment required (`scale_pos_weight = 0.87`).
- **`target_iron_deficiency`** (38.46%): Excellent balance (750 positive cases out of 1,950 tested pre-menopausal females and young children). Mild weighting (`scale_pos_weight = 1.60`).

### Tier 2: MODERATE (Prevalence $10\% - 30\%$)
- **`target_vitamin_d_deficiency`** (21.53%): 1,573 positive cases out of 7,307 tested participants. Ample statistical power.
- **`target_iron_deficiency_anemia`** (15.32%): 298 positive cases out of 1,945 tested. Strong clinical signal (`scale_pos_weight = 5.53`).
- **`target_folate_deficiency`** (11.41%): 863 positive cases out of 7,563 tested. Robust sample size (`scale_pos_weight = 7.76`).

### Tier 3: HARD (Prevalence $3\% - 10\%$)
- **`target_magnesium_deficiency`** (9.20%): 582 positive cases out of 6,324 tested. Requires gradient loss weighting (`scale_pos_weight = 9.87`).
- **`target_selenium_deficiency`** (3.39%): 257 positive cases out of 7,586 tested. Requires loss weighting (`scale_pos_weight = 28.52`).

### Tier 4: EXTREME IMBALANCE (Prevalence $< 3\%$)
- **`target_potassium_deficiency`** (1.83%): 115 positive cases out of 6,281 tested (`scale_pos_weight = 53.62`).
- **`target_calcium_deficiency`** (0.72%): 46 positive cases out of 6,362 tested (`scale_pos_weight = 137.30`).
- **Clinical Reality**: Hypokalemia and hypocalcemia are strictly regulated metabolic electrolytes. Severe serum deficiencies are rare in ambulatory populations and usually triggered by acute renal loss, diuretic therapy, or parathyroid disease. Continuous regression on raw serum levels and probability triage ranking must be prioritized over hard classification accuracy.

---

## 3. Target Quality Score

- **Ground Truth Verifiability**: **100 / 100** (CDC reference laboratory assays)
- **Target Sample Sufficiency**: **92 / 100**
- **Composite Target Score**: **96 / 100**
