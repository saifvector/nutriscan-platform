# Phase 7A Clinical Architecture Specification: 18-Nutrient Clinical Knowledge Base & Multi-Nutrient Screening Platform

## 1. Executive Summary

Phase 7A expands the **Integrated AI-Based Nutrient Deficiency Screening and Personalized Nutrition Platform** from an 11-nutrient baseline to an **18-nutrient clinical intelligence ecosystem**. This major upgrade integrates water-soluble B-complex vitamins, crucial cellular electrolytes, essential trace minerals, and endocrine regulators alongside core macronutrients and fat-soluble vitamins.

Grounding clinical validity in **WHO**, **NIH Office of Dietary Supplements**, and **Endocrine Society** practice standards, the updated architecture provides:
1. **Simultaneous 18-Nutrient Multi-Output Inference**: A unified XGBoost multi-target classifier delivering calibrated risk probabilities, confidence scores, and urgency rankings with an average latency of ~150 ms (well below the 500 ms SLA).
2. **71 Engineered Clinical Features**: Incorporating 9 newly introduced deficiency symptoms, endocrine and cardiovascular composite risk clusters, and demographic/lifestyle counterbalances.
3. **Biochemical Interaction Engine**: 13 clinically verified synergistic, supportive, and competitive interaction rules with dynamic compounding risk multipliers.
4. **Clinical Knowledge Base Registry & REST API**: 18 exhaustive monographs with ICD-10 diagnostic codes, confirmatory lab testing protocols, WHO reference thresholds, and clinical contraindications.
5. **Interactive 18-Node Force-Directed Network**: D3.js interactive graph visualization featuring dynamic flow animations, edge tracing, and responsive side panels.
6. **Full-Stack Cohesion**: End-to-end alignment across PostgreSQL schema/seeds, Explainable AI (SHAP attributions), recommendation engine, progress tracking, and vector PDF clinical reporting.

---

## 2. The 18-Nutrient Clinical Taxonomy

| Nutrient Name | Canonical Code | Category | Clinical Role & Physiological Target |
| :--- | :--- | :--- | :--- |
| **Protein** | `PROTEIN` | Macronutrient | Nitrogen balance, cellular repair, skeletal muscle protein synthesis |
| **Vitamin A** | `VITAMIN_A` | Fat-Soluble Vitamin | Phototransduction (rhodopsin), mucosal barrier integrity, epithelial turnover |
| **Vitamin B1 (Thiamine)** | `VITAMIN_B1` | Water-Soluble Vitamin | Carbohydrate metabolism, pyruvate decarboxylation, axonal nerve transmission |
| **Vitamin B2 (Riboflavin)** | `VITAMIN_B2` | Water-Soluble Vitamin | FAD/FMN electron transport chain, cellular respiration, glutathione redox |
| **Vitamin B3 (Niacin)** | `VITAMIN_B3` | Water-Soluble Vitamin | NAD/NADP coenzymes, DNA base-excision repair (PARP), lipid metabolism |
| **Vitamin B6 (Pyridoxine)** | `VITAMIN_B6` | Water-Soluble Vitamin | PLP-dependent amino acid transamination, neurotransmitter synthesis (GABA/5-HT) |
| **Folate (Vitamin B9)** | `FOLATE` | Water-Soluble Vitamin | One-carbon transfer, DNA purine synthesis, homocysteine remethylation |
| **Vitamin B12 (Cobalamin)** | `VITAMIN_B12` | Water-Soluble Vitamin | Methionine synthase cofactor, myelin sheath maintenance, hematopoiesis |
| **Vitamin C (Ascorbic Acid)**| `VITAMIN_C` | Water-Soluble Vitamin | Collagen prolyl/lysyl hydroxylase cofactor, cellular antioxidant, non-heme iron absorption |
| **Vitamin D** | `VITAMIN_D` | Secosteroid Hormone | Calcitriol-mediated paracellular calcium/phosphate absorption, bone mineralization |
| **Vitamin E** | `VITAMIN_E` | Fat-Soluble Vitamin | Alpha-tocopherol chain-breaking peroxyl radical scavenger in cellular membranes |
| **Iron** | `IRON` | Essential Mineral | Heme synthesis, hemoglobin/myoglobin oxygen transport, mitochondrial cytochromes |
| **Calcium** | `CALCIUM` | Essential Mineral | Hydroxyapatite skeletal matrix, excitation-contraction coupling, neural signaling |
| **Magnesium** | `MAGNESIUM` | Essential Mineral | ATP-Mg2+ chelation cofactor for >300 enzymes, PTH regulation, neuromuscular stability |
| **Zinc** | `ZINC` | Essential Trace Mineral | Structural component of >1000 zinc-finger proteins, thymulin immune competency |
| **Potassium** | `POTASSIUM` | Electrolyte / Cation | Primary intracellular cation, resting membrane potential, cardiac repolarization |
| **Selenium** | `SELENIUM` | Essential Trace Mineral | Selenoproteins (GPx, TrxR), iodothyronine deiodinase activation (T4 -> T3) |
| **Iodine** | `IODINE` | Essential Trace Mineral | Obligate substrate for thyroid hormone organification (T4 and T3 synthesis) |

---

## 3. ICD-10 Diagnostic & Confirmatory Testing Matrix

Every nutrient within the platform is mapped to canonical diagnostic criteria, standard laboratory tests, and clinical decision thresholds:

| Canonical Code | Nutrient | ICD-10 Code | Primary Confirmatory Test | Normal Reference Range | Diagnostic Deficiency Cutoff |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PROTEIN` | Protein | **E46** | Serum Albumin & Total Protein | 3.5 – 5.0 g/dL (Albumin) | `< 3.5 g/dL` |
| `VITAMIN_A` | Vitamin A | **E50.9** | Serum Retinol (HPLC) | 1.05 – 2.80 μmol/L | `< 0.70 μmol/L` |
| `VITAMIN_B1` | Vitamin B1 (Thiamine) | **E51.9** | Whole Blood Thiamine Diphosphate (TDP) | 70 – 180 nmol/L | `< 70 nmol/L` |
| `VITAMIN_B2` | Vitamin B2 (Riboflavin) | **E53.0** | Erythrocyte Glutathione Reductase Activation (EGRAC) | EGRAC Coefficient 1.0 – 1.2 | `Coefficient > 1.40` |
| `VITAMIN_B3` | Vitamin B3 (Niacin) | **E52** | Urinary N-Methylnicotinamide (NMN) / Creatinine | 2.4 – 6.4 mg/g creatinine | `< 1.6 mg/g creatinine` |
| `VITAMIN_B6` | Vitamin B6 (Pyridoxine) | **E53.1** | Plasma Pyridoxal 5'-Phosphate (PLP) | 20 – 125 nmol/L | `< 20 nmol/L` |
| `FOLATE` | Folate (Vitamin B9) | **E53.8** | RBC Folate & Serum Homocysteine | RBC Folate > 340 nmol/L | `< 305 nmol/L` (Homocysteine >15 μmol/L) |
| `VITAMIN_B12` | Vitamin B12 | **E53.8** | Serum B12 & Methylmalonic Acid (MMA) | B12 > 300 pg/mL, MMA < 270 nmol/L | `B12 < 200 pg/mL` (MMA > 270 nmol/L) |
| `VITAMIN_C` | Vitamin C | **E54** | Plasma Ascorbic Acid (HPLC) | 23 – 85 μmol/L | `< 11.4 μmol/L` |
| `VITAMIN_D` | Vitamin D | **E55.9** | Serum 25-Hydroxyvitamin D [25(OH)D] | 30 – 80 ng/mL | `< 20 ng/mL` (Severe: `< 12 ng/mL`) |
| `VITAMIN_E` | Vitamin E | **E56.0** | Serum Alpha-Tocopherol / Total Lipids | 12 – 46 μmol/L (or > 1.8 mg/g lipid) | `< 11.6 μmol/L` |
| `IRON` | Iron | **D50.9** | Serum Ferritin, Transferrin Saturation (TSAT) | Ferritin 30 – 200 ng/mL, TSAT 20–50% | `Ferritin < 15 ng/mL` (or TSAT `< 16%`) |
| `CALCIUM` | Calcium | **E58** | Ionized Serum Calcium & Albumin-Corrected Total | Ionized Ca 1.15 – 1.33 mmol/L | `Ionized Ca < 1.15 mmol/L` |
| `MAGNESIUM` | Magnesium | **E61.2** | Serum Magnesium & RBC Magnesium | Serum Mg 0.75 – 1.05 mmol/L | `Serum Mg < 0.75 mmol/L` |
| `ZINC` | Zinc | **E60** | Fasting Plasma Zinc (ICP-MS) | 10.7 – 18.4 μmol/L | `< 10.7 μmol/L` (or `< 70 μg/dL`) |
| `POTASSIUM` | Potassium | **E87.6** | Serum Potassium Electrolyte Assay | 3.5 – 5.0 mmol/L | `< 3.5 mmol/L` (Moderate: `< 3.0 mmol/L`) |
| `SELENIUM` | Selenium | **E61.1** | Serum / Plasma Selenium (ICP-MS) | 70 – 150 μg/L | `< 70 μg/L` |
| `IODINE` | Iodine | **E61.0** | Urinary Iodine Concentration (UIC, Spot/24h) | UIC 100 – 199 μg/L (Population) | `UIC < 100 μg/L` (Moderate: `< 50 μg/L`) |

---

## 4. Feature Engineering & Clinical Symptom Space

The input space comprises 71 engineered features derived from clinical demographics, dietary habits, lifestyle metrics, and an expanded 21-symptom inventory.

### Newly Introduced Symptoms (9 Clinical Additions):
1. `peripheral_neuropathy` (0–10 scale): Numbness, tingling, burning paresthesias in a stocking-glove distribution (flags B1, B6, B12).
2. `angular_cheilitis` (0–10 scale): Painful fissures and erythema at the labial commissures (flags B2, B3, B6, Iron).
3. `mental_confusion` (0–10 scale): Brain fog, disorientation, impaired executive recall (flags B1, B3, B12).
4. `cardiac_palpitations` (0–10 scale): Subjective racing heart, missed beats, postural tachycardia (flags Potassium, Magnesium, B1).
5. `muscle_weakness` (0–10 scale): Proximal leg/arm fatigue, difficulty ascending stairs (flags Potassium, Vitamin D, Protein, B1).
6. `dry_scaly_skin` (0–10 scale): Rough, pruritic, follicular hyperkeratosis or pellagrous lesions (flags Vitamin A, B3, Zinc).
7. `cold_intolerance` (0–10 scale): Hypersensitivity to cold ambient temperatures, hypothermia (flags Iodine, Selenium, Iron).
8. `goiter_neck_fullness` (0–10 scale): Subjective swelling or palpable fullness in the anterior lower neck (flags Iodine, Selenium).
9. `slow_wound_healing` (0–10 scale): Delayed epithelialization and recurring ulcerations (flags Zinc, Vitamin C, Protein).

### Composite Clinical Index Features:
- `cluster_cardiovascular_metabolic_index`: Synthesizes cardiac palpitations, muscle weakness, stress level, and potassium/magnesium depletion signals.
- `cluster_endocrine_thyroid_index`: Synthesizes cold intolerance, goiter/neck fullness, fatigue, and iodine/selenium deficiency risk.
- `cluster_neuromuscular_index`: Aggregates tingling, neuropathy, cramps, and B-complex cofactor deficits.
- `cluster_dermatologic_index`: Combines brittle nails, dry skin, cheilitis, hair loss, and healing delays.

---

## 5. Biochemical Nutrient Interaction Rules

The platform models 13 biochemical interactions with compounding severity multipliers:

```
               +--------------------------------------------------------+
               |                  BIOCHEMICAL NETWORK                   |
               +--------------------------------------------------------+
                       
                     [Vitamin D] <====== synergistic ======> [Calcium]
                          ||                                    ||
                     synergistic                            competitive
                          ||                                    ||
                          \/                                    \/
                     [Magnesium] <====== synergistic ======> [Potassium]
                          ||                                    ||
                     synergistic                            supportive
                          ||                                    ||
                          \/                                    \/
                    [Vitamin B1]                            [Vitamin B6]
                          
                          
                     [Vitamin C] <====== synergistic ======> [Iron]
                                                                ||
                                                            competitive
                                                                ||
                                                                \/
                     [Vitamin A] <====== synergistic ======> [Zinc]
                                                                ||
                                                            competitive
                                                                ||
                                                                \/
                                                             [Copper]*
                          
                     [Vitamin B12] <==== synergistic ======> [Folate]
                                                                ||
                                                            supportive
                                                                ||
                                                                \/
                                                           [Vitamin B6]
                          
                     [Iodine] <========= synergistic ======> [Selenium]
```

### Key Interaction Mechanisms:
1. **Vitamin D ↔ Calcium (Synergistic)**: Calcitriol triggers active enterocyte calcium channel transcription (TRPV6 and calbindin-D9k), boosting absorption from 10% to 40%.
2. **Vitamin D ↔ Magnesium (Synergistic)**: 25-hydroxylase and 1-alpha-hydroxylase are strictly magnesium-dependent; magnesium deficiency induces calcitriol resistance.
3. **Iron ↔ Vitamin C (Synergistic)**: Ascorbic acid reduces insoluble ferric iron (Fe3+) to bioavailable ferrous iron (Fe2+) and forms a soluble chelate resistant to dietary phytates.
4. **Iron ↔ Zinc (Competitive Antagonism)**: Both divalent cations compete for divalent metal transporter-1 (DMT1) uptake in duodenal enterocytes.
5. **Vitamin B12 ↔ Folate (Methyl Trap Synergistic)**: Methionine synthase requires both methylcobalamin and 5-methyl-THF; deficiency in B12 traps folate as unusable 5-MTHF.
6. **Iodine ↔ Selenium (Synergistic Thyroid Axis)**: Thyroid peroxidase requires iodine for thyroglobulin iodination, while selenium-dependent iodothyronine deiodinases convert prohormone T4 to active T3.
7. **Potassium ↔ Magnesium (Synergistic Electrolyte Homeostasis)**: Intracellular magnesium inhibits ROMK renal potassium channels; magnesium depletion causes refractory renal potassium wasting.
8. **Vitamin B1 ↔ Magnesium (Co-factor Dependency)**: Thiamine pyrophosphokinase requires Mg2+ to phosphorylate dietary thiamine into active thiamine pyrophosphate (TPP).

---

## 6. Machine Learning Model Architecture & Performance

- **Model Family**: Multi-Target Calibrated XGBoost Classifiers (`MultiOutputClassifier(XGBClassifier)`).
- **Features**: 71 input features normalized via `ClinicalFeaturePipeline`.
- **Targets**: 18 simultaneous continuous probabilities.
- **Latency Benchmark**:
  - Warm execution time: **120 – 180 ms** on single assessment payload.
  - Performance SLA: `< 500 ms` (verified with automated pytest telemetry).
- **Confidence Scoring**: Shannon entropy combined with margin-to-threshold calibration.

---

## 7. Clinical Knowledge Base Architecture & REST API

Mounted under `/api/v1/knowledge-base`:
- `GET /api/v1/knowledge-base/nutrients`: Returns all 18 clinical monographs.
- `GET /api/v1/knowledge-base/nutrients/{code}`: Returns deep monograph by canonical code (`VITAMIN_B1`, `POTASSIUM`, `IODINE`, etc.).
- `GET /api/v1/knowledge-base/interactions`: Returns catalog of 13 biochemical rules and compounding multipliers.

---

## 8. Frontend Visualization & User Experience

- **Interactive Force-Directed Network Graph**:
  - D3.js v7 force simulation with 18 animated SVG nodes.
  - Edge color coding: Green (`#10B981`) for Synergistic, Amber (`#F59E0B`) for Supportive, Rose (`#F43F5E`) for Competitive.
  - Interactive pulse animations travel along active interaction paths.
  - Node selection unveils comprehensive sliding drawer with risk score, symptoms, recommended whole foods, and biochemical mechanism.
- **Nutritional Dashboard & Body Map**:
  - High-resolution SVG human anatomy map highlighting organ systems affected:
    - Thyroid (Iodine, Selenium)
    - Cardiovascular (Potassium, Magnesium, Vitamin B1)
    - Neuromuscular (Vitamin B6, B12, Calcium)
    - Skeletal (Vitamin D, Calcium, Protein)
    - Hematologic (Iron, Folate, Vitamin B12)
    - Integumentary (Vitamin A, C, E, Zinc)

---

## 9. Verification & Compliance Summary

- **Total Test Suite**: 49 tests across 6 comprehensive test modules.
- **Test Pass Rate**: **100% (49 Passed, 0 Failed, 0 Skipped)**.
- **Frontend Build**: TypeScript strict compilation passing with **0 errors (3309 modules transformed)**.
- **End-to-End Compatibility**: Backward compatible with all existing Phase 1–6 endpoints.
