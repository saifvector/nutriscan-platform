# Master Data Dictionary — NutriScan AI Platform

This dictionary establishes the schema definitions, key join columns, units of measure, and clinical roles across all ingested datasets.

## 1. Primary Entity Keys & Linkage Matrix

| Domain | Dataset Family | Primary Entity Key | Foreign Keys / Cross-Linkages | Join Logic |
|---|---|---|---|---|
| Participant Profile | NHANES Demographics | `SEQN` | None | Primary respondent key across all 82 NHANES tables |
| Clinical Labs | NHANES Laboratory | `SEQN` | `SEQN` -> `DEMO_L` | 1-to-1 join on participant identifier |
| Dietary Intakes | NHANES Dietary | `SEQN` | `DRXFDCD` -> `FNDDS` | 1-to-many join on participant foods and WWEIA codes |
| Nutrient Composition | USDA Foundation Foods | `fdc_id` | `nutrient_id` -> `nutrient.csv` | Normalized USDA relational model |
| Survey Foods | USDA FNDDS | `fdc_id`, `food_code` | `food_code` -> NHANES `DR1IFDCD` | Links survey food codes to nutrient quantities |
| Supplement Formulas | NIH DSID | `product_id`, `ingredient_id` | Mapped to USDA `nutrient_id` | Adjusts label claims to real-world analytical potency |

## 2. Core Clinical Biomarkers & Ground Truth Target Variables

| Nutrient Target | Primary NHANES Table | Biomarker Variable | Unit of Measure | Clinical Deficiency Threshold |
|---|---|---|---|---|
| **Iron** | `FERTIN_L`, `CBC_L` | `LBXFER` (Ferritin), `LBXHGB` (Hemoglobin) | ng/mL, g/dL | Ferritin < 30.0 ng/mL, Hgb < 12.0 (F) / 13.5 (M) |
| **Vitamin D** | `VID_L` | `LBXVIDMS` (25-OH Vitamin D Total) | nmol/L (ng/mL) | < 50.0 nmol/L (< 20.0 ng/mL) |
| **Vitamin B12** | `BIOPRO_L` / `CBC_L` | `LBDB12` / `LBXMCV` (Mean Corpuscular Vol) | pg/mL, fL | < 200.0 pg/mL, MCV > 100 fL |
| **Folate** | `FOLATE_L`, `FOLFMS_L` | `LBDRFO` (RBC Folate), `LBXSF1SI` (5-MTHF) | ng/mL, nmol/L | RBC Folate < 305 nmol/L, Serum < 4 ng/mL |
| **Zinc** | `PBCD_L` | `LBXZN` (Serum Zinc) | mcg/dL | < 70.0 mcg/dL |
| **Selenium** | `PBCD_L` | `LBXSEL` (Blood Selenium) | mcg/L | < 70.0 mcg/L |
| **Magnesium** | `BIOPRO_L` | `LBXSC3SI` (Serum Bicarbonate/Electrolytes) | mmol/L | Serum Mg < 1.8 mg/dL (RBC Mg < 4.5 mg/dL) |
| **Calcium** | `BIOPRO_L` | `LBXSCA` (Total Calcium) | mg/dL | < 8.5 mg/dL |
| **Blood Glucose / HbA1c**| `GHB_L`, `GLU_L` | `LBXGH` (HbA1c), `LBXGLU` (Fasting Glucose)| %, mg/dL | HbA1c >= 5.7% (Pre-DM), >= 6.5% (DM) |
| **Systemic Inflammation**| `HSCRP_L` | `LBXHSCRP` (High-Sensitivity CRP) | mg/L | > 3.0 mg/L (High cardiovascular risk) |

## 3. Linked Application Modules

- `backend/app/ml/constants.py`: Synchronized with USDA and NIH DRI references.
- `backend/app/modules/knowledge_graph/`: Grounded in NHANES multi-nutrient co-occurrences.
- `backend/app/modules/intelligence/gap_engine.py`: Direct consumers of USDA FNDDS nutrient composition tables.
- `backend/app/modules/outcomes/`: Real-world outcomes validated against NHANES laboratory percentiles.
