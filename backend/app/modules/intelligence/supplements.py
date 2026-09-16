"""
Supplement Intelligence Engine
Phase 8: Nutrition Intelligence & Clinical Decision Engine

Authoritative Clinical References:
- National Institutes of Health (NIH) Office of Dietary Supplements (ODS)
- Dietary Supplement Ingredient Database (DSID)
- USP (United States Pharmacopeia) & NSF Clinical Standards

CRITICAL: Educational and clinical decision support guidance only; not medical prescriptions.
"""

from typing import List, Dict, Any, Optional
from .schemas import (
    SupplementRecommendationItem,
    SupplementIntelligenceResponse
)

# ─────────────────────────────────────────────────────────────────────────────
# Evidence-Based Supplement Knowledge Base
# Grounded in NIH ODS and DSID clinical monographs
# ─────────────────────────────────────────────────────────────────────────────

SUPPLEMENT_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "VITAMIN_D": {
        "nutrient_code": "VITAMIN_D",
        "nutrient_name": "Vitamin D3 (Cholecalciferol)",
        "suggested_form": "Liquid softgel emulsified in extra virgin olive oil or MCT oil (Cholecalciferol D3 + Vitamin K2 MK-7)",
        "therapeutic_dosage_range": "2,000 – 5,000 IU/day for 8–12 weeks (under 25(OH)D lab monitoring)",
        "maintenance_dosage_range": "1,000 – 2,000 IU/day",
        "optimal_timing": "Morning or early afternoon with a fat-containing meal (avocado, eggs, or nuts).",
        "timing_category": "MORNING_WITH_FAT",
        "food_interaction_warnings": [
            "Requires dietary lipids: Taking on an empty stomach reduces micellar absorption by up to 50%.",
            "Avoid taking simultaneously with high doses of mineral oil or orlistat which bind fat-soluble vitamins."
        ],
        "nutrient_interaction_warnings": [
            "Vitamin K2 (MK-7) Synergy: D3 increases calcium absorption; K2 activates osteocalcin and Matrix Gla Protein to direct calcium into bone matrix and prevent vascular calcification.",
            "Magnesium Requirement: Magnesium is an obligate enzymatic cofactor for hepatic 25-hydroxylase and renal 1-alpha-hydroxylase; severe magnesium deficiency renders high-dose D3 inert."
        ],
        "nih_dsid_reference": "NIH ODS Vitamin D Fact Sheet for Health Professionals; DSID-4 Multi-Vitamin Database.",
        "contraindications": [
            "Hypercalcemia, hypervitaminosis D, or severe primary hyperparathyroidism.",
            "Sarcoidosis or granulomatous diseases due to autonomous calcitriol conversion."
        ],
        "urgency_tier": "HIGH"
    },
    "IRON": {
        "nutrient_code": "IRON",
        "nutrient_name": "Iron (Elemental Fe)",
        "suggested_form": "Iron Bisglycinate Chelate (Ferrochel®) or Liposomal Iron (minimizes gastric irritation and constipation)",
        "therapeutic_dosage_range": "25 – 65 mg elemental iron on alternate days (improves hepcidin kinetics)",
        "maintenance_dosage_range": "15 – 25 mg elemental iron / day",
        "optimal_timing": "Morning upon waking on an empty stomach with 200mg Vitamin C or citrus juice; or 2 hours away from meals.",
        "timing_category": "MORNING_EMPTY_STOMACH",
        "food_interaction_warnings": [
            "Tannin & Polyphenol Blockade: Coffee, black tea, and red wine reduce non-heme iron uptake by up to 80% if ingested within 2 hours.",
            "Phytate Binding: Avoid co-ingesting with raw bran cereals or unsoaked seeds.",
            "Dairy / Calcium Competition: Calcium competes directly for duodenal divalent metal transporter 1 (DMT-1)."
        ],
        "nutrient_interaction_warnings": [
            "Calcium / Iron Antagonism: Separate supplemental calcium or dairy from iron by at least 2 to 3 hours.",
            "Zinc Competition: Doses of elemental iron > 25mg can inhibit zinc mucosal uptake.",
            "Vitamin C Enhancement: Ascorbic acid reduces ferric (Fe3+) to ferrous (Fe2+) iron, boosting absorption 3-fold."
        ],
        "nih_dsid_reference": "NIH ODS Iron Fact Sheet for Health Professionals; WHO Guidelines for Iron Deficiency.",
        "contraindications": [
            "Hereditary hemochromatosis, hemosiderosis, or chronic hemolytic anemias.",
            "Active acute bacterial infections (iron is a bacterial siderophore growth factor)."
        ],
        "urgency_tier": "HIGH"
    },
    "MAGNESIUM": {
        "nutrient_code": "MAGNESIUM",
        "nutrient_name": "Magnesium (Elemental Mg)",
        "suggested_form": "Magnesium Bisglycinate (for sleep/relaxation/cramps) or Magnesium Malate (for ATP/fibromyalgia)",
        "therapeutic_dosage_range": "200 – 400 mg elemental magnesium daily in divided doses",
        "maintenance_dosage_range": "150 – 250 mg elemental magnesium daily",
        "optimal_timing": "Evening, approximately 60 to 90 minutes before bedtime.",
        "timing_category": "EVENING_BEFORE_BED",
        "food_interaction_warnings": [
            "Oxalate & Phytate Precipitation: Insoluble complexes form when taken with high-oxalate raw foods.",
            "Alcohol: Acute alcohol consumption stimulates renal magnesium excretion via tubular wasting."
        ],
        "nutrient_interaction_warnings": [
            "Calcium Competition: Very high calcium doses (>1000mg in a single bolus) compete for intestinal paracellular uptake.",
            "Vitamin B6 Synergy: Pyridoxal-5-phosphate facilitates intracellular magnesium transport into erythrocytes."
        ],
        "nih_dsid_reference": "NIH ODS Magnesium Health Professional Fact Sheet; DSID Single Ingredient Database.",
        "contraindications": [
            "Severe renal impairment / stage 4-5 CKD (GFR < 30 mL/min) due to risk of hypermagnesemia.",
            "Myasthenia gravis or high-grade atrioventricular heart block."
        ],
        "urgency_tier": "HIGH"
    },
    "VITAMIN_B12": {
        "nutrient_code": "VITAMIN_B12",
        "nutrient_name": "Vitamin B12 (Cobalamin)",
        "suggested_form": "Methylcobalamin or Adenosylcobalamin sublingual lozenge (bypasses gastric intrinsic factor limitations)",
        "therapeutic_dosage_range": "1,000 – 2,000 mcg/day sublingually for 4–8 weeks",
        "maintenance_dosage_range": "500 – 1,000 mcg 2–3 times per week",
        "optimal_timing": "Morning with breakfast (supports daytime cellular methylation and circadian alert state).",
        "timing_category": "MORNING_WITH_FAT",
        "food_interaction_warnings": [
            "Gastric acid dependency: Proton pump inhibitors (omeprazole) and metformin impair dietary B12 release; sublingual forms bypass this limitation."
        ],
        "nutrient_interaction_warnings": [
            "Folate Masking: High supplemental folate (>1000mcg) can resolve megaloblastic anemia while allowing B12-induced subacute combined spinal cord degeneration to progress silently.",
            "Potassium Shift: Aggressive B12 repletion in severe megaloblastic anemia causes rapid reticulocytosis and severe hypokalemia; monitor serum potassium."
        ],
        "nih_dsid_reference": "NIH ODS Vitamin B12 Fact Sheet; DSID Vitamin B-Complex Profile.",
        "contraindications": [
            "Leber's hereditary optic neuropathy (cyanocobalamin specifically contraindicated; methylcobalamin safe).",
            "Known cobalamin hypersensitivity."
        ],
        "urgency_tier": "HIGH"
    },
    "CALCIUM": {
        "nutrient_code": "CALCIUM",
        "nutrient_name": "Calcium (Elemental Ca)",
        "suggested_form": "Calcium Citrate (can be taken with or without food; optimal for low stomach acid) or Microcrystalline Hydroxyapatite",
        "therapeutic_dosage_range": "500 – 1,000 mg elemental daily (in divided doses of max 500mg per dose)",
        "maintenance_dosage_range": "400 – 600 mg elemental daily (if dietary intake < 700mg)",
        "optimal_timing": "Split between lunch and dinner (maximum 500mg elemental calcium absorbed per single bolus).",
        "timing_category": "WITH_MAIN_MEAL",
        "food_interaction_warnings": [
            "Avoid taking simultaneously with high-phytate grain meals or concentrated spinach.",
            "High sodium diets increase urinary calcium clearance."
        ],
        "nutrient_interaction_warnings": [
            "Iron Blockade: Inhibits non-heme and heme iron absorption by 40-60% if taken concurrently.",
            "Zinc & Magnesium Competition: Competes for common divalent cation transporters at doses > 500mg.",
            "Vitamin D & K2 Co-Administration: Essential to ensure calcium is deposited into osseous tissue rather than arterial endothelium."
        ],
        "nih_dsid_reference": "NIH ODS Calcium Health Professional Fact Sheet; USP Verified Dietary Supplements.",
        "contraindications": [
            "Hypercalcemia, hypercalciuria, calcium oxalate nephrolithiasis, or severe vascular calcification."
        ],
        "urgency_tier": "MODERATE"
    },
    "ZINC": {
        "nutrient_code": "ZINC",
        "nutrient_name": "Zinc (Elemental Zn)",
        "suggested_form": "Zinc Picolinate or Zinc Bisglycinate (high bioavailability with minimal gastric distress)",
        "therapeutic_dosage_range": "20 – 30 mg elemental zinc daily for 4–6 weeks",
        "maintenance_dosage_range": "10 – 15 mg elemental zinc daily",
        "optimal_timing": "With a substantial meal (e.g., lunch) to prevent mild nausea.",
        "timing_category": "WITH_MAIN_MEAL",
        "food_interaction_warnings": [
            "Taking zinc on a completely empty stomach frequently causes transient acute nausea.",
            "Phytates in unrefined grains reduce zinc uptake by up to 50%."
        ],
        "nutrient_interaction_warnings": [
            "Copper Depletion Warning: Sustained zinc doses (>30-40mg/day for >8 weeks) induce intestinal metallothionein, which irreversibly traps dietary copper and causes severe secondary copper deficiency anemia and neutropenia.",
            "Iron / Zinc Ratio: If supplementing both, maintain a 2-hour window between doses."
        ],
        "nih_dsid_reference": "NIH ODS Zinc Fact Sheet; DSID Mineral Formulation Data.",
        "contraindications": [
            "Concomitant fluoroquinolone or tetracycline antibiotic therapy (zinc chelates antibiotics; separate by 3 hours)."
        ],
        "urgency_tier": "MODERATE"
    },
    "FOLATE": {
        "nutrient_code": "FOLATE",
        "nutrient_name": "Folate (Vitamin B9)",
        "suggested_form": "L-5-Methyltetrahydrofolate (L-5-MTHF) Calcium Salt (bypasses MTHFR C677T genetic polymorphism)",
        "therapeutic_dosage_range": "400 – 1,000 mcg DFE daily",
        "maintenance_dosage_range": "400 mcg DFE daily",
        "optimal_timing": "Morning with breakfast alongside B-complex cofactors.",
        "timing_category": "MORNING_WITH_FAT",
        "food_interaction_warnings": [
            "Chronic alcohol intake severely inhibits intestinal folate brush border conjugase activity and accelerates urinary excretion."
        ],
        "nutrient_interaction_warnings": [
            "Always evaluate Vitamin B12 status prior to high-dose folate therapy to prevent masked neuropathy.",
            "Vitamin B6 and B2 are required cofactors for MTHFR and homocysteine transsulfuration."
        ],
        "nih_dsid_reference": "NIH ODS Folate Fact Sheet for Health Professionals.",
        "contraindications": [
            "Undiagnosed megaloblastic anemia prior to ruling out Vitamin B12 deficiency."
        ],
        "urgency_tier": "MODERATE"
    },
    "SELENIUM": {
        "nutrient_code": "SELENIUM",
        "nutrient_name": "Selenium",
        "suggested_form": "Selenomethionine or High-Selenium Yeast (or 1-2 organic Brazil nuts daily)",
        "therapeutic_dosage_range": "100 – 200 mcg daily for 6–8 weeks",
        "maintenance_dosage_range": "55 – 100 mcg daily (or 1 Brazil nut daily)",
        "optimal_timing": "Midday with lunch or snack.",
        "timing_category": "WITH_MAIN_MEAL",
        "food_interaction_warnings": [
            "Brazil nuts vary widely in selenium based on soil content; 2 nuts per day provides ample therapeutic selenium."
        ],
        "nutrient_interaction_warnings": [
            "Toxicity Window: Tolerable Upper Intake Level is 400 mcg/day; avoid combining high-dose selenium pills with daily Brazil nuts to avoid selenosis (garlic breath, brittle nails, alopecia)."
        ],
        "nih_dsid_reference": "NIH ODS Selenium Health Professional Fact Sheet.",
        "contraindications": [
            "Excessive baseline serum selenium (>135 mcg/L)."
        ],
        "urgency_tier": "LOW"
    },
    "POTASSIUM": {
        "nutrient_code": "POTASSIUM",
        "nutrient_name": "Potassium (Electrolyte)",
        "suggested_form": "Dietary food sources preferred (coconut water, sweet potatoes); Potassium Citrate or Bicarbonate if indicated",
        "therapeutic_dosage_range": "99 mg elemental OTC limit / dose (dietary target 3,000–3,500 mg from whole foods)",
        "maintenance_dosage_range": "Food-first approach recommended; OTC supplements capped at 99mg",
        "optimal_timing": "Distributed evenly across meals with ample hydration (8-10 oz water).",
        "timing_category": "WITH_MAIN_MEAL",
        "food_interaction_warnings": [
            "Over-the-counter potassium supplements are legally restricted to 99mg per capsule to prevent localized intestinal mucosa ulceration."
        ],
        "nutrient_interaction_warnings": [
            "ACE Inhibitors / ARBs / Potassium-Sparing Diuretics (Spironolactone): High risk of life-threatening hyperkalemia with potassium supplementation; strict physician monitoring required."
        ],
        "nih_dsid_reference": "NIH ODS Potassium Fact Sheet for Health Professionals.",
        "contraindications": [
            "Chronic kidney disease, hyperkalemia, type 4 renal tubular acidosis, or acute oliguric state."
        ],
        "urgency_tier": "LOW"
    }
}


class SupplementIntelligenceEngine:
    """
    Evidence-grounded supplement guidance generator incorporating
    therapeutic ranges, chrono-nutrition timing, and pharmacological interaction warnings.
    """

    def __init__(self, knowledge_base: Optional[Dict[str, Dict[str, Any]]] = None):
        self.kb = knowledge_base or SUPPLEMENT_KNOWLEDGE_BASE

    def get_supplement_guidance(
        self,
        deficiencies: Optional[List[str]] = None,
        assessment_id: Optional[str] = None
    ) -> SupplementIntelligenceResponse:
        """
        Generates targeted supplement recommendations and interaction warnings.
        """
        target_defs = [d.upper() for d in (deficiencies or ["IRON", "VITAMIN_D", "MAGNESIUM", "VITAMIN_B12"])]
        
        items: List[SupplementRecommendationItem] = []
        cautions: List[str] = [
            "Clinical Safety Rule: Always confirm baseline serum levels (e.g. Ferritin, 25(OH)D, B12) via certified laboratory testing before initiating high-dose therapeutic protocols.",
            "Pharmaceutical Interaction Warning: Separate all multi-mineral supplements from thyroid hormones (Levothyroxine) by at least 4 hours.",
            "Mineral Transporter Competition: Do not consume high-dose calcium, iron, and zinc in the same single bolus; distribute throughout the day."
        ]

        for code, meta in self.kb.items():
            # Include if in targeted deficiencies or if high urgency
            is_targeted = any(code in d for d in target_defs)
            if is_targeted:
                item = SupplementRecommendationItem(
                    nutrient_code=code,
                    nutrient_name=meta["nutrient_name"],
                    suggested_form=meta["suggested_form"],
                    therapeutic_dosage_range=meta["therapeutic_dosage_range"],
                    maintenance_dosage_range=meta["maintenance_dosage_range"],
                    optimal_timing=meta["optimal_timing"],
                    timing_category=meta["timing_category"],
                    food_interaction_warnings=meta["food_interaction_warnings"],
                    nutrient_interaction_warnings=meta["nutrient_interaction_warnings"],
                    nih_dsid_reference=meta["nih_dsid_reference"],
                    contraindications=meta["contraindications"],
                    urgency_tier=meta["urgency_tier"]
                )
                items.append(item)

        # If no targeted matched, provide the top clinical ones
        if not items:
            for code in ["VITAMIN_D", "MAGNESIUM", "VITAMIN_B12"]:
                if code in self.kb:
                    meta = self.kb[code]
                    items.append(SupplementRecommendationItem(
                        nutrient_code=code,
                        nutrient_name=meta["nutrient_name"],
                        suggested_form=meta["suggested_form"],
                        therapeutic_dosage_range=meta["therapeutic_dosage_range"],
                        maintenance_dosage_range=meta["maintenance_dosage_range"],
                        optimal_timing=meta["optimal_timing"],
                        timing_category=meta["timing_category"],
                        food_interaction_warnings=meta["food_interaction_warnings"],
                        nutrient_interaction_warnings=meta["nutrient_interaction_warnings"],
                        nih_dsid_reference=meta["nih_dsid_reference"],
                        contraindications=meta["contraindications"],
                        urgency_tier=meta["urgency_tier"]
                    ))

        # Sort items: HIGH urgency first
        urgency_order = {"HIGH": 0, "MODERATE": 1, "LOW": 2}
        items.sort(key=lambda x: urgency_order.get(x.urgency_tier, 3))

        return SupplementIntelligenceResponse(
            assessment_id=assessment_id,
            recommended_supplements=items,
            general_cautions=cautions
        )
