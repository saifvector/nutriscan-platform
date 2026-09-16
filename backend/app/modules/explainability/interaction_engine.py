"""
Phase 11: Nutrient Interaction Reasoning Engine
Provides mechanistic pathophysiological reasoning on:
- Biochemical Synergies (Enhanced absorption and metabolic co-factors)
- Competitive Transporter Antagonisms (Shared apical/basolateral transporters)
- Enzymatic Dependencies (Obligate mineral cofactors for vitamin activation)
- Clinical Administration Spacing and Timing Protocols
"""

import logging
from typing import Dict, Any, List, Optional
from ...schemas.phase11_explainability import NutrientInteractionItem, InteractionType

logger = logging.getLogger(__name__)


class NutrientInteractionReasoningEngine:
    """
    Evaluates multi-nutrient interactions, transporter competition,
    and metabolic synergies for clinical decision support.
    """

    INTERACTION_RULES: List[NutrientInteractionItem] = [
        NutrientInteractionItem(
            nutrient_a="Vitamin D",
            nutrient_b="Calcium",
            interaction_type=InteractionType.SYNERGISTIC_ABSORPTION,
            description="Active calcitriol binds to VDR nuclear receptors in enterocytes, inducing transcriptional synthesis of calbindin-D9k and TRPV6 channels to boost intestinal calcium absorption from ~15% to over 40%.",
            biochemical_mechanism="1,25(OH)2D3-mediated upregulation of apical calcium channels (TRPV6) and cytosolic calbindin shuttles across the enterocyte.",
            synergy_multiplier=1.25,
            clinical_action="Co-prescribe or co-administer Calcium alongside active Vitamin D status optimization. In concurrent deficiency, replete Vitamin D concurrently.",
            timing_advice="Can be consumed together with meals containing moderate dietary fats to maximize lipophilic Vitamin D assimilation."
        ),
        NutrientInteractionItem(
            nutrient_a="Iron",
            nutrient_b="Vitamin C",
            interaction_type=InteractionType.SYNERGISTIC_ABSORPTION,
            description="Ascorbic acid acts as an electron donor, reducing poorly soluble ferric iron (Fe3+) into readily soluble ferrous iron (Fe2+) and forming an absorbable chelate that prevents precipitation by dietary phytates and polyphenols.",
            biochemical_mechanism="Chemical reduction of Fe3+ to Fe2+ facilitating substrate availability for the Divalent Metal Transporter-1 (DMT-1).",
            synergy_multiplier=1.20,
            clinical_action="Pair non-heme plant iron sources (lentils, spinach, legumes) with Vitamin C rich foods (citrus, bell peppers, kiwi).",
            timing_advice="Consume Vitamin C simultaneously with non-heme iron meals; avoid tea, coffee, and red wine for 60-90 minutes post-meal (tannins inhibit Fe2+)."
        ),
        NutrientInteractionItem(
            nutrient_a="Zinc",
            nutrient_b="Iron",
            interaction_type=InteractionType.ANTAGONISTIC_COMPETITION,
            description="High luminal concentrations of elemental iron competitively inhibit zinc uptake across shared DMT-1 and ZIP14 apical transporters in the proximal duodenum, leading to secondary zinc depletion.",
            biochemical_mechanism="Competitive saturation of divalent cation transporters (DMT-1/SLC11A2 and ZIP14/SLC39A14) by excess iron ions.",
            synergy_multiplier=1.15,
            clinical_action="When therapeutic supplemental doses of both iron (>30 mg) and zinc (>15 mg) are clinically indicated, do not co-administer in the same pill.",
            timing_advice="Space supplemental iron and zinc intake apart by at least 3 to 4 hours (e.g. Iron in the morning with citrus, Zinc at night with dinner)."
        ),
        NutrientInteractionItem(
            nutrient_a="Magnesium",
            nutrient_b="Vitamin D",
            interaction_type=InteractionType.ENZYMATIC_DEPENDENCY,
            description="Magnesium is an obligate cofactor for hepatic 25-hydroxylase (CYP2R1) and renal 1-alpha-hydroxylase (CYP27B1). In hypomagnesemia, exogenous Vitamin D cannot be hydroxylated to active calcitriol, producing refractory Vitamin D resistance.",
            biochemical_mechanism="Magnesium-dependent allosteric activation of hepatic CYP2R1 and renal CYP27B1 cytochrome P450 enzymes.",
            synergy_multiplier=1.30,
            clinical_action="Evaluate and replete magnesium stores (RBC magnesium or dietary intake) before or concurrently with high-dose Vitamin D therapy.",
            timing_advice="Magnesium glycinate or citrate may be taken in the evening to additionally support neuromuscular relaxation and sleep quality."
        ),
        NutrientInteractionItem(
            nutrient_a="Vitamin B12",
            nutrient_b="Folate",
            interaction_type=InteractionType.METABOLIC_INTERDEPENDENCE,
            description="Both vitamins are obligate coenzymes for methionine synthase (MTR). Isolated high-dose folate corrects the macrocytic anemia of B12 deficiency via the folate trap bypass while allowing irreversible subacute combined spinal cord degeneration to progress silently.",
            biochemical_mechanism="Coupled homocysteine remethylation to methionine; 5-methyl-THF transfers methyl group to cob(I)alamin to generate methylcobalamin and THF.",
            synergy_multiplier=1.35,
            clinical_action="Never initiate high-dose therapeutic folic acid (>1 mg/day) without first obtaining serum B12 and methylmalonic acid (MMA) to rule out concurrent B12 deficiency.",
            timing_advice="B-complex formulations providing balanced methylated forms (L-methylfolate + methylcobalamin) prevent isolated substrate trapping."
        ),
        NutrientInteractionItem(
            nutrient_a="Potassium",
            nutrient_b="Magnesium",
            interaction_type=InteractionType.ELECTROLYTE_HOMEOSTASIS,
            description="Magnesium regulates the renal outer medullary potassium (ROMK) channels in the thick ascending limb and distal nephron. Intracellular magnesium depletion disinhibits ROMK channels, causing excessive renal potassium wasting and refractory hypokalemia.",
            biochemical_mechanism="Magnesium pore-block of ROMK channels preventing outward potassium leak; magnesium stabilization of the Na+/K+-ATPase pump.",
            synergy_multiplier=1.30,
            clinical_action="In patients presenting with hypokalemia or persistent muscle cramps, always check and replete serum/RBC magnesium concurrently.",
            timing_advice="Include potassium-rich whole foods (potatoes, squash, chard) alongside magnesium-dense seeds (pepitas) in daily dietary planning."
        ),
        NutrientInteractionItem(
            nutrient_a="Calcium",
            nutrient_b="Iron",
            interaction_type=InteractionType.ANTAGONISTIC_COMPETITION,
            description="High doses of calcium (>= 300-500 mg) significantly inhibit both non-heme and heme iron absorption at the enterocyte basolateral membrane, reducing systemic iron repletion.",
            biochemical_mechanism="Calcium-mediated internalization or functional inhibition of basolateral ferroportin-1 (FPN1) export.",
            synergy_multiplier=1.15,
            clinical_action="Advise patients taking therapeutic iron to avoid simultaneous consumption of high-dose calcium supplements, milk, or calcium-fortified beverages.",
            timing_advice="Maintain a minimum 2-hour window between high-calcium dairy or supplements and therapeutic iron intake."
        ),
        NutrientInteractionItem(
            nutrient_a="Selenium",
            nutrient_b="Iodine",
            interaction_type=InteractionType.ENZYMATIC_DEPENDENCY,
            description="Iodine provides the chemical precursor for thyroid prohormone thyroxine (T4), but selenium-dependent iodothyronine deiodinases (DIO1, DIO2) are required to convert T4 into biologically active triiodothyronine (T3).",
            biochemical_mechanism="Selenocysteine-dependent reductive deiodination of T4 to T3 and cellular glutathione peroxidase neutralization of H2O2 in thyrocytes.",
            synergy_multiplier=1.35,
            clinical_action="Never supplement high-dose iodine in the presence of uncorrected selenium deficiency, as excess thyrocyte oxidation can accelerate autoimmune thyroiditis.",
            timing_advice="Maintain regular dietary selenium intake (1-2 Brazil nuts daily, seafood) to support thyroid enzymatic conversion."
        )
    ]

    @classmethod
    def get_all_interactions(cls) -> List[NutrientInteractionItem]:
        """Returns complete biochemical interaction catalog."""
        return cls.INTERACTION_RULES

    @classmethod
    def detect_interactions(cls, active_nutrients: List[str]) -> List[NutrientInteractionItem]:
        """
        Filters interaction rules relevant to a list of flagged patient nutrients or deficiencies.
        """
        clean_nuts = [n.lower().replace("target_", "").replace("_deficiency", "").replace("_insufficiency", "").replace("_", " ") for n in active_nutrients]
        
        detected: List[NutrientInteractionItem] = []
        for rule in cls.INTERACTION_RULES:
            match_a = any(rule.nutrient_a.lower() in cn or cn in rule.nutrient_a.lower() for cn in clean_nuts)
            match_b = any(rule.nutrient_b.lower() in cn or cn in rule.nutrient_b.lower() for cn in clean_nuts)
            if match_a or match_b:
                detected.append(rule)

        return detected
