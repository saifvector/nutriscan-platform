# Phase 10A Master Dataset Summary Report

**Dataset Artifact**: `data/merged_training_dataset.parquet`
**Generation Date**: 2026-09-13 20:19:45
**Pipeline Duration**: 2.05 seconds

## 1. Key High-Level Metrics

- **Total Participants Ingested**: **11,933**
- **Total Feature Columns (X)**: **105**
- **Total Target Columns (y)**: **17** (9 binary labels, 8 continuous biomarkers)
- **Total Metadata Columns**: **3** (`SEQN`, survey weights)
- **Total Dataset Dimensions**: **11,933 rows × 125 columns**
- **Parquet Storage Size**: **2.49 MB**
- **Target Leakage Status**: **CLEAN (0 violations)**

## 2. Multi-Modal Domain Coverage

| Domain | Source Datasets | Feature Count | Records with Complete Data |
|---|---|:---:|:---:|
| Demographics | NHANES `DEMO_L` | 7 | 11,933 (100.0%) |
| Examination & Vitals | NHANES `BMX_L`, `BPXO_L` | 7 | 8,860 (74.2%) |
| Dietary Recalls | NHANES `DR1TOT_L`, `DR2TOT_L` | 35 | 8,860 (74.2%) |
| Dietary Supplements | NHANES `DSQTOT_L` | 13 | 11,933 (100.0%) |
| Total Daily Intakes | Combined Diet + Supp | 10 | 8,860 (74.2%) |
| NIH Nutrient Adequacy (NAR) | Intake / NIH RDA | 11 | 8,860 (74.2%) |
| Clinical Symptoms & Mood | NHANES `DPQ_L`, `SLQ_L` | 7 | 6,337 (53.1%) |
| Lifestyle & Behavior | NHANES `DBQ_L`, `PAQ_L`, `ALQ_L`, `SMQ_L` | 7 | 6,337 - 11,933 |
| Medical Diagnoses History | NHANES `MCQ_L` | 5 | 8,501 (71.2%) |
| Ground Truth Targets | NHANES `VID_L`, `FERTIN_L`, `BIOPRO_L`, `CBC_L`, etc. | 16 | 2,564 - 8,727 per target |

## 3. Phase 10B Hand-Off Decision

> [!IMPORTANT]
> **Dataset Status**: **READY FOR MODEL TRAINING (Phase 10B)**.
> The dataset is cleanly formatted, zero leakage is verified, class distributions are quantified, and dictionaries are published.
> Per user instructions, execution has halted here without initiating training.
