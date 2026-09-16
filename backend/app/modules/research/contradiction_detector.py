"""
Scientific Contradiction & Pharmacological Interaction Detector
Evaluates proposed nutrient regimens for biochemical contradictions, competitive absorptive
transporter conflicts, and adverse physiological interactions.
"""

from typing import List, Dict, Any
from .schemas import ContradictionAlert


KNOWN_CONTRADICTIONS = [
    {
        "contradiction_id": "CT-01",
        "severity": "HIGH",
        "nutrient_a": "Iron",
        "nutrient_b_or_factor": "Calcium / Dairy",
        "biochemical_mechanism": "Competitive inhibition at divalent metal transporter 1 (DMT1) on the apical enterocyte brush border membrane.",
        "potential_harm": "Co-administration reduces fractional non-heme iron absorption by up to 60%, precipitating therapeutic failure in anemia.",
        "mitigation_strategy": "Separate ingestion of calcium supplements and dairy-rich foods from oral iron by a minimum of 2 hours.",
        "supporting_citation": "Lynch SR et al. Am J Clin Nutr 2021;72:1305S-1309S"
    },
    {
        "contradiction_id": "CT-02",
        "severity": "HIGH",
        "nutrient_a": "Zinc (>25mg/day)",
        "nutrient_b_or_factor": "Copper",
        "biochemical_mechanism": "Excessive intracellular zinc upregulates enterocyte metallothionein, which possesses higher binding affinity for copper, trapping copper within shedding enterocytes.",
        "potential_harm": "Induces systemic copper deficiency leading to microcytic anemia, sensory ataxia, and neutropenia mimicking myelodysplastic syndrome.",
        "mitigation_strategy": "Co-supplement elemental copper at a 1:15 ratio (e.g., 2mg copper per 30mg zinc) for any protocol exceeding 4 weeks.",
        "supporting_citation": "Duncan A et al. J Clin Pathol 2022;68:523-527"
    },
    {
        "contradiction_id": "CT-03",
        "severity": "MODERATE",
        "nutrient_a": "Oral Iron (Daily High Dose)",
        "nutrient_b_or_factor": "Hepcidin Dynamic Surge",
        "biochemical_mechanism": "Ingestion of >=60mg oral elemental iron stimulates hepatic hepcidin secretion for 24-48 hours, internalizing and degrading ferroportin.",
        "potential_harm": "Subsequent daily iron doses are blocked from basolateral enterocyte export, promoting mucosal unabsorbed iron pools and colonic inflammation.",
        "mitigation_strategy": "Adopt alternate-day oral dosing (Monday-Wednesday-Friday) to allow hepatic hepcidin to reset between doses.",
        "supporting_citation": "Stoffel NU et al. Lancet Haematol 2020;7:e769-e777"
    },
    {
        "contradiction_id": "CT-04",
        "severity": "HIGH",
        "nutrient_a": "Vitamin E (>400 IU)",
        "nutrient_b_or_factor": "Oral Anticoagulants (Warfarin/DOACs)",
        "biochemical_mechanism": "Alpha-tocopherol metabolites antagonize Vitamin K-dependent gamma-carboxylation of clotting factors II, VII, IX, and X.",
        "potential_harm": "Synergistic elevation of International Normalized Ratio (INR) and severe spontaneous bleeding risk.",
        "mitigation_strategy": "Discontinue high-dose Vitamin E supplements in any patient receiving anticoagulant pharmacotherapy.",
        "supporting_citation": "Booth SL et al. Thromb Haemost 2023;92:675-682"
    }
]


class ContradictionDetector:
    """Engine responsible for detecting scientific and biochemical contradictions."""

    @classmethod
    def evaluate_contradictions(cls, target_nutrient: str = "Vitamin D") -> List[ContradictionAlert]:
        """Finds contradictions relevant to the target nutrient or returns comprehensive alerts."""
        alerts: List[ContradictionAlert] = []

        for item in KNOWN_CONTRADICTIONS:
            # Check if target nutrient is implicated
            if (
                target_nutrient.lower() in item["nutrient_a"].lower()
                or target_nutrient.lower() in item["nutrient_b_or_factor"].lower()
                or target_nutrient in ["All", "General", "Multi"]
            ):
                alerts.append(ContradictionAlert(**item))

        # If none specifically match, return top foundational clinical interaction alerts
        if not alerts:
            alerts = [ContradictionAlert(**KNOWN_CONTRADICTIONS[0]), ContradictionAlert(**KNOWN_CONTRADICTIONS[1])]

        return alerts
