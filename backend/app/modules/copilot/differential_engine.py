"""
Differential Diagnostic Reasoning Engine
Evaluates competing clinical etiologies, uncertainty intervals, confidence scores,
and suggests gold-standard confirmatory testing for all predicted nutrient deficiencies.
"""

from typing import Dict, Any, List
from .schemas import (
    UnifiedPatientDossier,
    DifferentialReasoningItem,
    DifferentialDiagnosticReport,
    CompetingCause
)


class DifferentialEngine:
    """Evaluates competing etiologies and diagnostic uncertainty across micronutrient deficiencies."""

    # Knowledge base of clinical etiologies and gold-standard confirmatory diagnostics
    DIFFERENTIAL_KNOWLEDGE_BASE = {
        "Vitamin D": {
            "primary": "Inadequate cutaneous ultraviolet B (UVB) photoproduction coupled with low dietary intake.",
            "competing": [
                {
                    "etiology": "Fat Malabsorption Syndrome (Celiac, Crohn's, Exocrine Pancreatic Insufficiency)",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "Vitamin D is fat-soluble; intestinal lipid transport impairment blunts micellar incorporation.",
                    "distinguishing_features": "Steatorrhea, chronic diarrhea, unexplained weight loss, concurrent fat-soluble vitamin (A, E, K) deficits."
                },
                {
                    "etiology": "Impaired Renal 1-alpha-hydroxylation (Occult CKD)",
                    "likelihood": "LOW",
                    "clinical_rationale": "Declining eGFR reduces renal CYP27B1 activity, impeding conversion of 25-OH D to active 1,25-(OH)2 D.",
                    "distinguishing_features": "Elevated serum creatinine/BUN, secondary hyperparathyroidism with normal or borderline 25-OH D."
                },
                {
                    "etiology": "Hepatic Hydroxylation Defect (Chronic Liver Disease)",
                    "likelihood": "LOW",
                    "clinical_rationale": "Hepatic 25-hydroxylase (CYP2R1) suppression due to severe parenchymal disease.",
                    "distinguishing_features": "Elevated transaminases, hypoalbuminemia, prolonged prothrombin time."
                }
            ],
            "confirmatory_tests": [
                {"test": "Serum 25-Hydroxyvitamin D [25(OH)D]", "purpose": "Gold standard indicator of total body Vitamin D stores.", "cutoff": "< 20 ng/mL is deficient; 20-30 ng/mL is insufficient."},
                {"test": "Intact Parathyroid Hormone (iPTH)", "purpose": "Evaluates compensatory secondary hyperparathyroidism.", "cutoff": "> 65 pg/mL indicates functional bone resorption."},
                {"test": "Serum Calcium & Phosphate Panel", "purpose": "Rules out concurrent hypocalcemia / osteomalacia risk.", "cutoff": "Ca < 8.5 mg/dL; PO4 < 2.5 mg/dL."}
            ]
        },
        "Iron": {
            "primary": "Insufficient dietary bioavailability (non-heme predominance) or elevated physiologic utilization.",
            "competing": [
                {
                    "etiology": "Occult Gastrointestinal Blood Loss (Peptic Ulcer, Polyp, Angiodysplasia, IBD)",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "Chronic microscopic blood loss outpaces enterocyte iron absorptive capacity.",
                    "distinguishing_features": "Positive fecal occult blood / FIT, microcytic hypochromic anemia in post-menopausal or male patients."
                },
                {
                    "etiology": "Duodenal Malabsorption (Celiac Disease or H. pylori gastritis)",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "Iron is absorbed primarily in the duodenum; enteropathy blunts apical DMT1 transport.",
                    "distinguishing_features": "Positive anti-tTG IgA, refractory response to oral iron therapy, chronic dyspepsia."
                },
                {
                    "etiology": "Anemia of Chronic Disease / Inflammation",
                    "likelihood": "LOW",
                    "clinical_rationale": "Hepcidin elevation sequesters iron within macrophages, reducing circulating transferrin saturation.",
                    "distinguishing_features": "Elevated CRP/ESR, normal or elevated ferritin despite low serum iron and low TIBC."
                }
            ],
            "confirmatory_tests": [
                {"test": "Serum Ferritin", "purpose": "Direct reflection of total reticuloendothelial iron stores.", "cutoff": "< 30 ng/mL establishes absolute iron deficiency."},
                {"test": "Total Iron Binding Capacity (TIBC) & Transferrin Saturation", "purpose": "Evaluates iron transport saturation.", "cutoff": "Transferrin Saturation < 16% confirms functional iron deficiency."},
                {"test": "Complete Blood Count (CBC) with Reticulocyte Index", "purpose": "Evaluates microcytosis (MCV < 80 fL) and marrow response.", "cutoff": "MCV < 80 fL, MCH < 27 pg."}
            ]
        },
        "Vitamin B12": {
            "primary": "Strict vegan/vegetarian dietary pattern devoid of animal protein cobalamin.",
            "competing": [
                {
                    "etiology": "Autoimmune Pernicious Anemia (Anti-Intrinsic Factor / Parietal Cell Antibodies)",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "Autoimmune destruction of gastric parietal cells abrogates intrinsic factor production.",
                    "distinguishing_features": "Severe macrocytic anemia (MCV > 100 fL), atrophic glossitis, subacute combined degeneration."
                },
                {
                    "etiology": "Terminal Ileal Resection or Crohn's Disease",
                    "likelihood": "LOW",
                    "clinical_rationale": "The B12-IF complex requires cubam receptors in the terminal ileum for receptor-mediated endocytosis.",
                    "distinguishing_features": "History of ileal resection, right lower quadrant abdominal pain, diarrhea."
                },
                {
                    "etiology": "Drug-Induced Hypochlorhydria (Long-term PPI or Metformin therapy)",
                    "likelihood": "HIGH",
                    "clinical_rationale": "Suppressed gastric acid prevents cleavage of B12 from dietary protein; metformin interferes with calcium-dependent ileal uptake.",
                    "distinguishing_features": "Documented PPI use > 12 months or metformin dose >= 1000mg/day."
                }
            ],
            "confirmatory_tests": [
                {"test": "Serum Methylmalonic Acid (MMA)", "purpose": "Most sensitive functional cellular marker of B12 deficiency.", "cutoff": "> 270 nmol/L confirms intracellular B12 depletion."},
                {"test": "Total Homocysteine", "purpose": "Secondary metabolic marker of impaired methylation.", "cutoff": "> 15 mcmol/L confirms hyperhomocysteinemia."},
                {"test": "Holotranscobalamin (Active B12)", "purpose": "Directly measures the bioavailable fraction delivering cobalamin to tissues.", "cutoff": "< 35 pmol/L is highly diagnostic."}
            ]
        },
        "Folate": {
            "primary": "Suboptimal green leafy vegetable and fortified grain intake.",
            "competing": [
                {
                    "etiology": "Jejunal Enteropathy / Celiac Disease",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "Folate polyglutamates require jejunal deconjugation; mucosal blunting impairs uptake.",
                    "distinguishing_features": "Concurrent iron and vitamin D malabsorption."
                },
                {
                    "etiology": "Antifolate Drug Interaction (Methotrexate, Trimethoprim, Anticonvulsants)",
                    "likelihood": "LOW",
                    "clinical_rationale": "Inhibits dihydrofolate reductase (DHFR) enzyme activity.",
                    "distinguishing_features": "Medication reconciliation positive for dihydrofolate reductase antagonists."
                }
            ],
            "confirmatory_tests": [
                {"test": "RBC Folate", "purpose": "Measures tissue stores over prior 90-120 days (unaffected by recent meals).", "cutoff": "< 305 ng/mL indicates chronic tissue deficiency."},
                {"test": "Serum Folate", "purpose": "Reflects acute dietary folate status.", "cutoff": "< 4.0 ng/mL."}
            ]
        },
        "Magnesium": {
            "primary": "High refined carbohydrate consumption, chronic psychosocial stress, and low whole seed intake.",
            "competing": [
                {
                    "etiology": "Renal Wasting Secondary to Medication (Thiazide/Loop Diuretics, PPIs, Calcineurin Inhibitors)",
                    "likelihood": "HIGH",
                    "clinical_rationale": "Interferes with TRPM6 magnesium channels in the distal convoluted tubule.",
                    "distinguishing_features": "Current diuretic prescription, hypokalemia refractory to potassium supplementation."
                },
                {
                    "etiology": "Chronic Alcohol-Induced Tubular Dysfunction",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "Ethanol induces acute reversible magnesium hypercalciuria and tubular wasting.",
                    "distinguishing_features": "Elevated GGT, AST/ALT ratio > 2.0, macrocytosis."
                }
            ],
            "confirmatory_tests": [
                {"test": "RBC Magnesium", "purpose": "Intracellular magnesium concentration (only 1% resides in serum).", "cutoff": "< 4.2 mg/dL demonstrates intracellular deficit."},
                {"test": "Serum Magnesium & Total Calcium", "purpose": "Assesses extracellular levels and concurrent hypocalcemia.", "cutoff": "< 1.8 mg/dL is deficient."}
            ]
        },
        "Calcium": {
            "primary": "Dietary exclusion of dairy and fortified alternatives, coupled with low Vitamin D.",
            "competing": [
                {
                    "etiology": "Hypoparathyroidism or Pseudohypoparathyroidism",
                    "likelihood": "LOW",
                    "clinical_rationale": "Absence of PTH prevents renal calcium reabsorption and osseous release.",
                    "distinguishing_features": "Elevated serum phosphorus, low PTH, normal renal function."
                },
                {
                    "etiology": "Hypomagnesemia-Induced PTH Resistance",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "Severe magnesium depletion blocks adenylate cyclase, causing end-organ PTH resistance.",
                    "distinguishing_features": "Concurrent serum Mg < 1.4 mg/dL refractory to calcium infusion until magnesium is restored."
                }
            ],
            "confirmatory_tests": [
                {"test": "Ionized Calcium", "purpose": "Physiologically active free calcium independent of albumin fluctuations.", "cutoff": "< 4.6 mg/dL (1.15 mmol/L)."},
                {"test": "Serum Albumin + Corrected Calcium", "purpose": "Calculates corrected calcium = Serum Ca + 0.8 * (4.0 - Albumin).", "cutoff": "< 8.5 mg/dL."}
            ]
        },
        "Zinc": {
            "primary": "High dietary phytate-to-zinc molar ratio (> 15) inhibiting enterocyte zinc transporters.",
            "competing": [
                {
                    "etiology": "Chronic Diarrheal Illness or IBD",
                    "likelihood": "MODERATE",
                    "clinical_rationale": "High endogenous enteropancreatic zinc secretions lost in stool.",
                    "distinguishing_features": "Persistent loose stools, perioral dermatitis."
                }
            ],
            "confirmatory_tests": [
                {"test": "Serum/Plasma Zinc (Fasting Morning Trace-Free Tube)", "purpose": "Circulating zinc biomarker.", "cutoff": "< 70 mcg/dL."}
            ]
        }
    }

    @classmethod
    def analyze_differential(cls, dossier: UnifiedPatientDossier) -> DifferentialDiagnosticReport:
        """
        Runs differential diagnostic reasoning across all identified nutrient deficiencies.
        """
        items: List[DifferentialReasoningItem] = []

        for d in dossier.deficiencies:
            nutrient = d.nutrient
            kb = cls.DIFFERENTIAL_KNOWLEDGE_BASE.get(nutrient)
            
            # Compute confidence & uncertainty bounds (95% CI)
            prob = d.probability
            half_width = round(1.96 * ((prob * (1.0 - prob) / 100.0) ** 0.5), 3)
            lower_ci = max(0.0, round(prob - half_width, 3))
            upper_ci = min(1.0, round(prob + half_width, 3))
            conf = d.confidence_score

            if kb:
                primary = kb["primary"]
                competing_causes = [
                    CompetingCause(
                        etiology=c["etiology"],
                        likelihood=c["likelihood"],
                        clinical_rationale=c["clinical_rationale"],
                        distinguishing_features=c["distinguishing_features"]
                    )
                    for c in kb["competing"]
                ]
                confirmatory = kb["confirmatory_tests"]
            else:
                primary = f"Primary dietary deficiency and increased metabolic consumption of {nutrient}."
                competing_causes = [
                    CompetingCause(
                        etiology="Primary Dietary Insufficiency",
                        likelihood="HIGH",
                        clinical_rationale="Inadequate daily micronutrient density.",
                        distinguishing_features="Survey food frequency questionnaire correlates."
                    )
                ]
                confirmatory = [
                    {"test": f"Serum {nutrient}", "purpose": "Baseline laboratory quantification.", "cutoff": "Clinical reference minimum."}
                ]

            uncertainty_text = (
                f"Model predicted risk for {nutrient} is {prob:.1%} with 95% Confidence Interval [{lower_ci:.1%}, {upper_ci:.1%}]. "
                f"Statistical confidence is rated at {conf:.2f}. "
                f"Differential diagnosis must rule out competing non-dietary etiologies prior to irreversible or high-dose therapy."
            )

            items.append(DifferentialReasoningItem(
                nutrient=nutrient,
                predicted_probability=prob,
                confidence_score=conf,
                uncertainty_interval=[lower_ci, upper_ci],
                primary_suspected_cause=primary,
                competing_causes=competing_causes,
                confirmatory_diagnostics=confirmatory,
                clinical_uncertainty_explanation=uncertainty_text
            ))

        return DifferentialDiagnosticReport(
            patient_id=dossier.demographics.patient_id,
            differential_items=items,
            diagnostic_algorithm_notes=(
                "Differential diagnostic logic synthesizes machine learning calibrated probability distributions, "
                "biochemical pathway constraints, and peer-reviewed clinical nutrition literature. "
                "Confirmatory testing targets gold-standard cellular biomarkers to establish definitive root causes."
            )
        )
