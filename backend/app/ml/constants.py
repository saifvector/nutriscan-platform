"""
Machine Learning & Clinical Constants for Multi-Nutrient Screening Platform
Phase 2: Dataset Engineering and Machine Learning Foundation
"""

from enum import Enum
from typing import List, Dict, Any, Tuple


class RiskCategory(str, Enum):
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"


class OverallSeverity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# The 18 Core Target Nutrients (11 Baseline + 7 Phase 7A Expanded)
TARGET_NUTRIENTS: List[str] = [
    "Protein",
    "Vitamin A",
    "Vitamin B12",
    "Folate",
    "Vitamin C",
    "Vitamin D",
    "Vitamin E",
    "Iron",
    "Calcium",
    "Zinc",
    "Magnesium",
    "Vitamin B1",
    "Vitamin B2",
    "Vitamin B3",
    "Vitamin B6",
    "Potassium",
    "Selenium",
    "Iodine"
]

NUTRIENT_CODES: Dict[str, str] = {
    "Protein": "PROTEIN",
    "Vitamin A": "VITAMIN_A",
    "Vitamin B12": "VITAMIN_B12",
    "Folate": "FOLATE_B9",
    "Vitamin C": "VITAMIN_C",
    "Vitamin D": "VITAMIN_D",
    "Vitamin E": "VITAMIN_E",
    "Iron": "IRON",
    "Calcium": "CALCIUM",
    "Zinc": "ZINC",
    "Magnesium": "MAGNESIUM",
    "Vitamin B1": "VITAMIN_B1",
    "Vitamin B2": "VITAMIN_B2",
    "Vitamin B3": "VITAMIN_B3",
    "Vitamin B6": "VITAMIN_B6",
    "Potassium": "POTASSIUM",
    "Selenium": "SELENIUM",
    "Iodine": "IODINE"
}

# Clinical Urgency Weights for Overall Risk Aggregation (Higher = More acute physiological risk)
CLINICAL_URGENCY_WEIGHTS: Dict[str, float] = {
    "Iron": 1.25,          # Rapid anemia onset, tissue hypoxia
    "Vitamin B12": 1.30,   # Irreversible neurological demyelination
    "Folate": 1.20,        # DNA synthesis failure, megaloblastic crisis
    "Vitamin D": 1.15,     # Bone demineralization & immune compromise
    "Calcium": 1.20,       # Neuromuscular excitability, cardiac arrhythmia
    "Protein": 1.25,       # Sarcopenia, immune depletion, hypoalbuminemia
    "Zinc": 1.05,          # Immune dysfunction, delayed wound healing
    "Magnesium": 1.10,     # Cardiac arrhythmias, muscle tetany, enzyme cofactor
    "Vitamin C": 1.00,     # Collagen synthesis failure, scurvy, capillary fragility
    "Vitamin A": 1.05,     # Night blindness, epithelial keratinization
    "Vitamin E": 0.90,     # Hemolytic anemia, peripheral neuropathy
    "Vitamin B1": 1.25,    # Beriberi, lactic acidosis, Wernicke-Korsakoff encephalopathy
    "Vitamin B2": 1.00,    # Ariboflavinosis, cheilosis, mucosal ulceration
    "Vitamin B3": 1.15,    # Pellagra (dermatitis, diarrhea, dementia)
    "Vitamin B6": 1.20,    # Microcytic anemia, peripheral neuropathy, seizures
    "Potassium": 1.30,     # Cardiac arrhythmias, muscular paralysis, hypokalemic crisis
    "Selenium": 1.05,      # Keshan disease, thyroid failure, antioxidant depletion
    "Iodine": 1.15         # Endemic goiter, hypothyroid myxedema, neurocognitive deficits
}

# Standard Clinical Symptoms Catalog (Expanded for 18 Nutrients)
SYMPTOM_FIELDS: List[str] = [
    "fatigue",
    "hair_loss",
    "muscle_weakness",
    "bone_pain",
    "pale_skin",
    "brittle_nails",
    "brain_fog",
    "muscle_cramps",
    "cold_intolerance",
    "frequent_infections",
    "mouth_ulcers",
    "night_blindness",
    "slow_wound_healing",
    "tingling_numbness",
    "irritability",
    "poor_appetite",
    "cracked_lips",
    "eye_irritation",
    "dermatitis",
    "digestive_disturbances",
    "irregular_heartbeat",
    "thyroid_dysfunction",
    "unexplained_weight_gain"
]

# Symptom Cluster Groupings for Dimensionality Reduction and Domain Feature Aggregation
SYMPTOM_CLUSTERS: Dict[str, List[str]] = {
    "neurological": ["brain_fog", "tingling_numbness", "fatigue", "irritability"],
    "musculoskeletal": ["muscle_weakness", "bone_pain", "muscle_cramps"],
    "integumentary": ["hair_loss", "brittle_nails", "pale_skin", "cracked_lips", "dermatitis"],
    "immunological": ["frequent_infections", "slow_wound_healing", "mouth_ulcers"],
    "sensory_ocular": ["night_blindness", "eye_irritation"],
    "cardiovascular_metabolic": ["irregular_heartbeat", "cold_intolerance", "poor_appetite", "digestive_disturbances"],
    "endocrine_thyroid": ["thyroid_dysfunction", "unexplained_weight_gain", "cold_intolerance"]
}

# Pre-defined Nutrient Interaction Rules (Synergies, Antagonisms, Dependencies)
NUTRIENT_INTERACTIONS: List[Dict[str, Any]] = [
    {
        "pair": ("Vitamin D", "Calcium"),
        "type": "SYNERGISTIC_ABSORPTION",
        "description": "Vitamin D induces synthesis of calbindin, dramatically boosting intestinal calcium absorption. Co-deficiency accelerates bone demineralization and secondary hyperparathyroidism.",
        "synergy_multiplier": 1.25,
        "clinical_action": "Co-administer Calcium with active Vitamin D; screen for parathyroid hormone abnormalities."
    },
    {
        "pair": ("Iron", "Vitamin C"),
        "type": "SYNERGISTIC_REDUCTION",
        "description": "Ascorbic acid reduces dietary ferric iron (Fe3+) to soluble ferrous iron (Fe2+), overcoming phytate inhibition and facilitating DMT-1 transporter uptake.",
        "synergy_multiplier": 1.20,
        "clinical_action": "Pair non-heme iron sources with Vitamin C rich citrus, berries, or bell peppers; avoid simultaneous tea/coffee (tannins)."
    },
    {
        "pair": ("Zinc", "Iron"),
        "type": "ANTAGONISTIC_COMPETITION",
        "description": "High luminal concentrations of inorganic iron competitively inhibit zinc intestinal uptake across shared DMT-1 and ZIP14 apical transporters.",
        "synergy_multiplier": 1.15,
        "clinical_action": "Space supplemental iron and zinc intake apart by at least 3-4 hours when managing concurrent deficiencies."
    },
    {
        "pair": ("Magnesium", "Vitamin D"),
        "type": "ENZYMATIC_DEPENDENCY",
        "description": "Magnesium is an essential obligate cofactor for hepatic 25-hydroxylase and renal 1-alpha-hydroxylase enzymes that convert Vitamin D to calcitriol. Magnesium deficiency induces refractory Vitamin D resistance.",
        "synergy_multiplier": 1.30,
        "clinical_action": "Correct intracellular magnesium levels before or concurrently with high-dose Vitamin D therapy."
    },
    {
        "pair": ("Vitamin B12", "Folate"),
        "type": "METABOLIC_INTERDEPENDENCE",
        "description": "Both participate in the methionine synthase one-carbon pathway. Unmonitored high folate supplementation without B12 corrects megaloblastic anemia but allows irreversible subacute combined spinal cord degeneration to progress.",
        "synergy_multiplier": 1.35,
        "clinical_action": "Never supplement folate in isolated high doses without confirming normal Vitamin B12 / holotranscobalamin status."
    },
    {
        "pair": ("Calcium", "Magnesium"),
        "type": "HOMEOSTATIC_BALANCE",
        "description": "High calcium intake without proportional magnesium can impair magnesium tubular reabsorption and disrupt smooth muscle contraction and cardiac rhythm.",
        "synergy_multiplier": 1.10,
        "clinical_action": "Maintain approximately a 2:1 dietary balance of Calcium to Magnesium."
    },
    {
        "pair": ("Vitamin B6", "Vitamin B12"),
        "type": "SYNERGISTIC_HOMOCYSTEINE",
        "description": "Vitamin B6 (as PLP) and Vitamin B12 (as methylcobalamin) act synergistically in the transsulfuration and remethylation pathways to clear toxic homocysteine and prevent cardiovascular endothelial damage.",
        "synergy_multiplier": 1.25,
        "clinical_action": "Co-screen and supplement B6 alongside B12 when addressing elevated plasma homocysteine."
    },
    {
        "pair": ("Vitamin B6", "Folate"),
        "type": "METABOLIC_INTERDEPENDENCE",
        "description": "Vitamin B6 is a crucial cofactor for serine hydroxymethyltransferase (SHMT), which transfers single-carbon units to tetrahydrofolate (THF) for de novo purine and thymidylate synthesis.",
        "synergy_multiplier": 1.20,
        "clinical_action": "Ensure adequate Vitamin B6 intake to enable physiological folate one-carbon shuttling."
    },
    {
        "pair": ("Iodine", "Selenium"),
        "type": "ENZYMATIC_DEPENDENCY",
        "description": "Selenium-dependent iodothyronine deiodinases (DIO1, DIO2) are required to convert thyroid prohormone T4 (produced via iodine) to active triiodothyronine T3. Co-deficiency induces severe myxedematous hypothyroidism.",
        "synergy_multiplier": 1.35,
        "clinical_action": "Never supplement high-dose iodine in the setting of severe selenium deficiency, as unneutralized hydrogen peroxide can exacerbate thyroiditis."
    },
    {
        "pair": ("Potassium", "Magnesium"),
        "type": "ELECTROLYTE_HOMEOSTASIS",
        "description": "Magnesium is an obligate cofactor for Na+/K+-ATPase and inhibits renal ROMK potassium secretory channels. Hypomagnesemia causes refractory hypokalemia that resists potassium repletion until magnesium is corrected.",
        "synergy_multiplier": 1.30,
        "clinical_action": "Check and replete serum/RBC magnesium concurrently whenever managing hypokalemia or muscular cramping."
    },
    {
        "pair": ("Vitamin B1", "Magnesium"),
        "type": "ENZYMATIC_DEPENDENCY",
        "description": "Thiamine pyrophosphokinase, the enzyme converting thiamine to active thiamine pyrophosphate (TPP), is strictly magnesium-dependent. Thiamine therapy is ineffective without adequate magnesium.",
        "synergy_multiplier": 1.25,
        "clinical_action": "Administer magnesium alongside thiamine in patients presenting with high alcohol intake or chronic malnourishment."
    },
    {
        "pair": ("Vitamin B2", "Vitamin B6"),
        "type": "ENZYMATIC_ACTIVATION",
        "description": "Pyridoxine 5'-phosphate oxidase (PNPO), which converts dietary pyridoxamine and pyridoxine into active pyridoxal 5'-phosphate (PLP), requires flavin mononucleotide (FMN, Vitamin B2).",
        "synergy_multiplier": 1.20,
        "clinical_action": "Screen for riboflavin insufficiency when B6 therapy fails to resolve neuropathy or microcytic anemia."
    },
    {
        "pair": ("Vitamin B3", "Protein"),
        "type": "BIOSYNTHETIC_PRECURSOR",
        "description": "The essential amino acid tryptophan serves as the biochemical precursor for de novo nicotinamide adenine dinucleotide (NAD+/NADH) synthesis (60 mg dietary tryptophan = 1 mg niacin equivalent).",
        "synergy_multiplier": 1.15,
        "clinical_action": "Ensure balanced dietary protein containing tryptophan to buffer against subclinical niacin deficiencies."
    }
]

# Physical and Lifestyle Plausible Ranges (Used for Outlier Detection and Clamping)
PLAUSIBLE_RANGES: Dict[str, Tuple[float, float]] = {
    "age": (1.0, 120.0),
    "height_cm": (45.0, 240.0),
    "weight_kg": (20.0, 300.0),
    "bmi": (10.0, 70.0),
    "water_intake_liters": (0.0, 10.0),
    "sleep_hours_per_night": (1.0, 18.0),
    "sunlight_exposure_min_per_day": (0.0, 720.0),
    "stress_level": (1.0, 10.0),
    "meals_per_day": (1.0, 8.0)
}
