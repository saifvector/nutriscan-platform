"""
NutriScan Pediatric Clinical Safety Framework Test Suite
Tests:
1. All 7 Age Brackets (0–6m, 7–12m, 1–3y, 4–8y, 9–13y, 14–18y, Adult)
2. All 9 Required Nutrients (Vit D, B12, Fe, Ca, Mg, Zn, Folate, Vit A, Protein)
3. Quantitative RDAs, ULs, Deficiency and Toxicity cutoffs
4. Age-Aware Toxicity Evaluation & Quarantine
5. Pediatric Recommendation Calibration (Infant drops vs Toddler chewables vs Adult tablets)
6. Adult vs Pediatric Mega-Dose Divergence
"""

import pytest
from app.modules.safety.pediatric_framework import (
    get_age_bracket,
    is_pediatric,
    get_pediatric_guidelines,
    evaluate_pediatric_toxicity,
    get_pediatric_biomarker_status,
    AGE_0_TO_6M,
    AGE_7_TO_12M,
    AGE_1_TO_3Y,
    AGE_4_TO_8Y,
    AGE_9_TO_13Y,
    AGE_14_TO_18Y,
    AGE_ADULT,
    AGE_BRACKETS
)
from app.modules.governance.safety_engine import ClinicalSafetyEngine
from app.modules.recommendation.engine import PersonalizedRecommendationEngine
from app.schemas.phase12_governance import SafetySeverity, SafetyAction


REQUIRED_NUTRIENTS = [
    "Vitamin D",
    "Vitamin B12",
    "Iron",
    "Calcium",
    "Magnesium",
    "Zinc",
    "Folate",
    "Vitamin A",
    "Protein"
]


def test_age_bracket_mapping():
    """Verifies that decimal years and months correctly map to standard clinical brackets."""
    assert get_age_bracket(0.2) == AGE_0_TO_6M
    assert get_age_bracket(0.0, age_months=4.0) == AGE_0_TO_6M
    assert get_age_bracket(0.8) == AGE_7_TO_12M
    assert get_age_bracket(0.0, age_months=9.0) == AGE_7_TO_12M
    assert get_age_bracket(2.0) == AGE_1_TO_3Y
    assert get_age_bracket(5.5) == AGE_4_TO_8Y
    assert get_age_bracket(11.0) == AGE_9_TO_13Y
    assert get_age_bracket(16.0) == AGE_14_TO_18Y
    assert get_age_bracket(35.0) == AGE_ADULT
    assert is_pediatric(2.0) is True
    assert is_pediatric(17.9) is True
    assert is_pediatric(18.0) is False
    assert is_pediatric(45.0) is False


def test_coverage_of_all_brackets_and_nutrients():
    """Asserts that all 7 age brackets define profiles for all 9 required nutrients."""
    for bracket in AGE_BRACKETS:
        for nutrient in REQUIRED_NUTRIENTS:
            profile = get_pediatric_guidelines(bracket, nutrient)
            assert profile is not None, f"Missing {nutrient} in bracket {bracket}"
            assert profile.rda > 0, f"Invalid RDA for {nutrient} in {bracket}"
            if nutrient != "Magnesium":
                assert profile.ul >= profile.rda, f"UL must be >= RDA for {nutrient} in {bracket}"
            assert profile.deficiency_biomarker_cutoff > 0, f"Invalid deficiency cutoff for {nutrient} in {bracket}"
            assert profile.toxicity_biomarker_cutoff > profile.deficiency_biomarker_cutoff


def test_infant_vitamin_d_toxicity_guardrail():
    """
    Infant UL for Vitamin D is 1,000 IU.
    Feeding an infant (Age 0.3y) an adult dose of 2,500 IU must trigger acute pediatric toxicity!
    Feeding an adult 2,500 IU is completely safe (Adult UL is 4,000 IU).
    """
    # Infant test (0-6m)
    is_toxic, msg, ul = evaluate_pediatric_toxicity(age_years=0.3, nutrient="Vitamin D", intake_or_dose=2500.0)
    assert is_toxic is True
    assert ul == 1000.0
    assert "exceeds the clinical Upper Tolerable Limit (UL) of 1000.0 IU" in msg
    assert "Risk of pediatric toxicity!" in msg

    # Adult test
    is_toxic_adult, _, adult_ul = evaluate_pediatric_toxicity(age_years=35.0, nutrient="Vitamin D", intake_or_dose=2500.0)
    assert is_toxic_adult is False
    assert adult_ul == 4000.0


def test_toddler_iron_toxicity_guardrail():
    """
    Toddler (Age 2) acute iron ingestion above 40 mg must trigger toxicity warning.
    """
    is_toxic, msg, ul = evaluate_pediatric_toxicity(age_years=2.0, nutrient="Iron", intake_or_dose=65.0)
    assert is_toxic is True
    assert ul == 40.0
    assert "exceeds the clinical Upper Tolerable Limit (UL) of 40.0 mg" in msg


def test_safety_engine_pediatric_ul_blocking():
    """
    Safety engine must quarantine or block recommendations that exceed age-specific ULs for pediatric patients.
    """
    patient_intake = {
        "age": 1.5, # 18-month-old toddler (1-3y bracket, Vit D UL = 2,500 IU)
        "gender": "FEMALE",
        "dietary_pattern": "OMNIVORE"
    }

    # Propose an adult mega-dose (5000 IU = 125 mcg)
    proposed_recs = [
        {
            "food_or_supp": "Adult Vitamin D3 Mega-Dose",
            "target_nutrient": "Vitamin D",
            "amount": 125.0, # mcg -> 5000 IU
            "dose_mg": 125.0
        }
    ]

    response = ClinicalSafetyEngine.evaluate_safety(patient_intake, proposed_recs)
    assert response.is_safe_for_dispatch is False or response.safety_score < 100.0
    ped_violations = [v for v in response.violations if "PEDIATRIC_UL_EXCEEDED" in v.rule_id]
    assert len(ped_violations) > 0, "Safety engine failed to generate PEDIATRIC_UL_EXCEEDED violation!"
    assert ped_violations[0].severity in [SafetySeverity.HIGH, SafetySeverity.CRITICAL]


def test_pediatric_recommendation_calibration():
    """
    Verifies that the recommendation engine tailors supplement formulations
    and doses specifically for pediatric patients.
    """
    # 1. Infant (Age 0.3 years = ~3.6 months)
    infant_intake = {"age": 0.3, "gender": "MALE", "dietary_pattern": "VEGAN"}
    infant_supps = PersonalizedRecommendationEngine.generate_supplement_recommendations(
        elevated_nutrients=["Vitamin D", "Iron", "Protein"],
        dietary_pattern="VEGAN",
        patient_intake=infant_intake
    )

    d_supp = next(s for s in infant_supps if s["target_nutrient"] == "Vitamin D")
    assert "Drops" in d_supp["item_name"]
    assert "400 IU/day" in d_supp["dosage"]

    fe_supp = next(s for s in infant_supps if s["target_nutrient"] == "Iron")
    assert "Liquid" in fe_supp["item_name"]
    assert "pediatrician guidance" in fe_supp["dosage"]

    p_supp = next(s for s in infant_supps if s["target_nutrient"] == "Protein")
    assert "Whole-Food" in p_supp["item_name"]
    assert "powder" not in p_supp["item_name"].lower() # No powders for infants

    # 2. Toddler (Age 2 years)
    toddler_intake = {"age": 2.0, "gender": "FEMALE", "dietary_pattern": "OMNIVORE"}
    toddler_supps = PersonalizedRecommendationEngine.generate_supplement_recommendations(
        elevated_nutrients=["Vitamin D"],
        dietary_pattern="OMNIVORE",
        patient_intake=toddler_intake
    )
    toddler_d = next(s for s in toddler_supps if s["target_nutrient"] == "Vitamin D")
    assert "600 IU/day" in toddler_d["dosage"]

    # 3. Adult (Age 32 years)
    adult_intake = {"age": 32.0, "gender": "FEMALE", "dietary_pattern": "OMNIVORE"}
    adult_supps = PersonalizedRecommendationEngine.generate_supplement_recommendations(
        elevated_nutrients=["Vitamin D"],
        dietary_pattern="OMNIVORE",
        patient_intake=adult_intake
    )
    adult_d = next(s for s in adult_supps if s["target_nutrient"] == "Vitamin D")
    assert "2000 - 4000 IU/day" in adult_d["dosage"]


def test_pediatric_biomarker_status():
    """Verifies that biomarker classification reflects age-stratified reference cutoffs."""
    # Serum 25(OH)D of 14 ng/mL is DEFICIENT for both infant and adult
    res_infant = get_pediatric_biomarker_status(age_years=0.5, nutrient="Vitamin D", biomarker_value=14.0)
    assert res_infant["status"] == "DEFICIENT"

    # Serum 25(OH)D of 120 ng/mL is TOXIC
    res_toxic = get_pediatric_biomarker_status(age_years=3.0, nutrient="Vitamin D", biomarker_value=120.0)
    assert res_toxic["status"] == "TOXIC"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
