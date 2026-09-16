# NutriScan AI — Phase 11 Dataset Forensic Verification
**Target File:** `data/merged_training_dataset.parquet`  
**Audit Mode:** Zero Trust Physical Ingestion & Schema Scan  
**Date:** September 13, 2026  
**Status:** FULLY VERIFIED

---

## 1. Dataset Dimensions & Column Taxonomy

The master dataset `data/merged_training_dataset.parquet` was loaded into memory and scanned directly via Apache Arrow / Pandas:

| Metric | Target Standard | Physical Scan Result | Compliance |
| :--- | :---: | :---: | :---: |
| **Row Count** | 11,933 participants | **11,933** | **PASS** |
| **Total Column Count** | 125 variables | **125** | **PASS** |
| **Predictor Features** | Exactly 105 features | **105** | **PASS** |
| **Binary Deficiency Targets** | Exactly 9 targets | **9** | **PASS** |
| **Continuous Biomarker Targets** | Exactly 8 targets | **8** | **PASS** |
| **Survey Metadata Columns** | Exactly 3 columns | **3** | **PASS** |
| **Duplicate SEQN (Participant IDs)** | 0 duplicates | **0** | **PASS** |
| **Duplicate Rows** | 0 duplicates | **0** | **PASS** |
| **Duplicate Column Names** | 0 duplicates | **0** | **PASS** |
| **File Size on Disk** | ~2.6 MB | **2,614,952 Bytes (2.49 MB)** | **PASS** |

---

## 2. Target Variables Inventory

### Binary Deficiency Targets (9)
1. `target_iron_deficiency`: Ferritin $< 15\ \mu\text{g/L}$ (females) or $< 30\ \mu\text{g/L}$ (males)
2. `target_iron_deficiency_anemia`: Iron deficiency + Hemoglobin $< 12.0\ \text{g/dL}$ (F) / $< 13.0\ \text{g/dL}$ (M)
3. `target_vitamin_d_deficiency`: Serum $25(\text{OH})\text{D} < 30\ \text{nmol/L}$ ($12\ \text{ng/mL}$)
4. `target_vitamin_d_insufficiency`: Serum $25(\text{OH})\text{D} < 50\ \text{nmol/L}$ ($20\ \text{ng/mL}$)
5. `target_folate_deficiency`: RBC Folate $< 305\ \text{nmol/L}$
6. `target_magnesium_deficiency`: Serum Magnesium $< 0.75\ \text{mmol/L}$
7. `target_potassium_deficiency`: Serum Potassium $< 3.5\ \text{mmol/L}$
8. `target_selenium_deficiency`: Serum Selenium $< 70\ \mu\text{g/L}$
9. `target_calcium_deficiency`: Total Serum Calcium $< 2.15\ \text{mmol/L}$ ($8.6\ \text{mg/dL}$)

### Continuous Biomarker Targets (8)
`target_cont_ferritin`, `target_cont_hemoglobin`, `target_cont_vitamin_d`, `target_cont_folate_rbc`, `target_cont_magnesium`, `target_cont_potassium`, `target_cont_calcium`, `target_cont_selenium`.

### Metadata Columns (3)
`SEQN` (NHANES Unique Respondent Sequence Number), `survey_weight_interview` (WTINT2YR), `survey_weight_mec` (WTMEC2YR).

---

## 3. Missing Rate Analysis & Sparsity Audit

- **Zero-Null Features (100% complete):** 28 features (including `demo_age_years`, `demo_gender_female`, dietary energy, carbohydrate, fat, protein intakes).
- **Features with $< 10\%$ Missingness:** 84 / 105 features.
- **Features with $10\% - 50\%$ Missingness:** 15 / 105 features (primarily examination measures such as waist circumference and blood pressure).
- **Features with $> 50\%$ Missingness:** 6 features.
- **Features with $> 80\%$ Missingness:** 3 features (`symptom_concentration_trouble`: 87.69%, `symptom_memory_loss`: 87.69%, `symptom_irritability`: 87.69%).  
  *Epidemiological note:* These variables originate from NHANES mental health questionnaires administered only to specific age subsamples. The preprocessor handles these safely with zero-risk mode defaults.

**Dataset Verification Verdict: PASS**
