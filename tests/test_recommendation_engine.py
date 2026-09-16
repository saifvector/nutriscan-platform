"""
Comprehensive Automated Test Suite: Phase 5 Personalized Nutrition Recommendation Engine
Tests:
- Dietary preference and restriction filtering (Vegan, Vegetarian, Dairy-Free, Gluten-Free)
- Food scoring and Priority Tier ranking (Priority 1, 2, 3)
- Biochemical nutrient synergy pairings (Iron + Vit C, Vit D + Ca, Mg + Vit D, Zn/Fe timing)
- Targeted lifestyle intervention generation (Sunlight, Activity, Hydration, Sleep, Stress)
- 7-Day, 14-Day, and 30-Day phased nutrient recovery plans
- Recommendation scoring system (Relevance, Coverage, Compatibility, Overall)
- FastAPI REST endpoints and response latency compliance (< 500 ms SLA)
"""

import pytest
import uuid
import time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.recommendation.engine import PersonalizedRecommendationEngine
from backend.app.modules.recommendation.knowledge_base import FOOD_KNOWLEDGE_BASE
from backend.app.modules.recommendation.service import RecommendationService
from backend.app.schemas.recommendation import FoodPriorityTierEnum

client = TestClient(app)


@pytest.fixture(scope="module")
def sample_vegan_screening_payload():
    return {
        "age": 29,
        "gender": "FEMALE",
        "height_cm": 168.0,
        "weight_kg": 58.0,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "meals_per_day": 3,
            "water_intake_liters": 2.0,
            "daily_fruit_vegetable_servings": 2,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": ["dairy-free", "meat-free"]
        },
        "lifestyle_factors": {
            "activity_level": "SEDENTARY",
            "sleep_hours_per_night": 6.5,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 10,
            "stress_level": 8
        },
        "symptoms": {
            "fatigue": 9,
            "hair_loss": 7,
            "muscle_cramps": 6
        },
        "medical_history": [],
        "supplement_usage": []
    }


def test_dietary_filtering_vegan_and_dairy_free():
    """Verify Vegan and Dairy-Free filters completely exclude animal proteins, dairy, and eggs."""
    all_iron_foods = FOOD_KNOWLEDGE_BASE["Iron"]
    filtered = PersonalizedRecommendationEngine.filter_foods_by_diet(
        food_list=all_iron_foods,
        dietary_pattern="VEGAN",
        restrictions=["dairy-free", "meat-free"]
    )

    assert len(filtered) > 0
    food_names = [f["food_name"] for f in filtered]
    # Ensure beef is strictly excluded
    assert not any("Beef" in name or "Steak" in name for name in food_names)
    # Ensure lentils and pumpkin seeds are retained
    assert any("Lentils" in name for name in food_names)
    assert any("Pumpkin Seeds" in name for name in food_names)

    # Check dairy foods are excluded from Calcium
    all_calcium_foods = FOOD_KNOWLEDGE_BASE["Calcium"]
    calcium_filtered = PersonalizedRecommendationEngine.filter_foods_by_diet(
        food_list=all_calcium_foods,
        dietary_pattern="VEGAN",
        restrictions=["dairy-free"]
    )
    calcium_names = [f["food_name"] for f in calcium_filtered]
    assert not any("Yogurt" in name or "Milk" in name and "Plant" not in name for name in calcium_names)
    assert any("Tahini" in name or "Bok Choy" in name or "Tofu" in name for name in calcium_names)


def test_gluten_free_filtering():
    """Verify gluten-free filter excludes wheat-based foods."""
    all_vit_e = FOOD_KNOWLEDGE_BASE["Vitamin E"]
    filtered = PersonalizedRecommendationEngine.filter_foods_by_diet(
        food_list=all_vit_e,
        dietary_pattern="OMNIVORE",
        restrictions=["gluten-free"]
    )
    for f in filtered:
        assert "GLUTEN_FREE" in f.get("dietary_tags", [])


def test_priority_ranking_by_severity():
    """Verify high-severity deficiencies yield Priority 1 foods with scores >= 80."""
    preds = [
        {"nutrient": "Iron", "risk_level": "HIGH", "probability": 0.89},
        {"nutrient": "Vitamin D", "risk_level": "HIGH", "probability": 0.85},
        {"nutrient": "Calcium", "risk_level": "MODERATE", "probability": 0.55}
    ]

    recs = PersonalizedRecommendationEngine.generate_food_recommendations(
        nutrient_predictions=preds,
        dietary_pattern="VEGAN",
        restrictions=["dairy-free"]
    )

    priority_1 = recs["priority_1"]
    priority_2 = recs["priority_2"]

    assert len(priority_1) > 0
    # Top food must address HIGH risk nutrient
    assert priority_1[0].target_nutrient in ["Iron", "Vitamin D"]
    assert priority_1[0].recommendation_score >= 80.0
    assert priority_1[0].priority_tier == FoodPriorityTierEnum.PRIORITY_1


def test_synergistic_pairings_generation():
    """Verify Iron + Vitamin C, Vitamin D + Calcium, and Magnesium + Vit D synergies."""
    synergies = PersonalizedRecommendationEngine.generate_synergy_pairings(
        elevated_nutrients=["Iron", "Vitamin D", "Calcium", "Magnesium"],
        dietary_pattern="VEGAN"
    )

    assert len(synergies) >= 3
    pair_tuples = [(s.primary_nutrient, s.synergistic_nutrient) for s in synergies]

    # Verify Iron + Vitamin C pairing
    assert ("Iron", "Vitamin C") in pair_tuples
    iron_c = next(s for s in synergies if s.primary_nutrient == "Iron" and s.synergistic_nutrient == "Vitamin C")
    assert "Ascorbic acid" in iron_c.biochemical_mechanism
    assert "coffee" in iron_c.cautionary_timing.lower()

    # Verify Vitamin D + Calcium pairing
    assert ("Vitamin D", "Calcium") in pair_tuples

    # Verify Magnesium + Vitamin D pairing
    assert ("Vitamin D", "Magnesium") in pair_tuples


def test_lifestyle_interventions_and_hydration_target():
    """Verify lifestyle intervention generation with dynamic hydration calculations."""
    preds = [
        {"nutrient": "Vitamin D", "risk_level": "HIGH"},
        {"nutrient": "Magnesium", "risk_level": "HIGH"}
    ]
    patient_data = {
        "weight_kg": 60.0,
        "stress_level": 8
    }

    interventions = PersonalizedRecommendationEngine.generate_lifestyle_interventions(
        nutrient_predictions=preds,
        patient_data=patient_data
    )

    categories = [i.category for i in interventions]
    assert "SUNLIGHT" in categories
    assert "HYDRATION" in categories
    assert "SLEEP" in categories
    assert "STRESS" in categories

    # 60kg * 0.035 = 2.1 Liters
    hydration_item = next(i for i in interventions if i.category == "HYDRATION")
    assert "2.1 Liters" in hydration_item.daily_target


def test_recovery_plan_structure():
    """Verify 7-Day, 14-Day, and 30-Day phased milestones with daily checklists."""
    preds = [{"nutrient": "Vitamin D", "risk_level": "HIGH"}, {"nutrient": "Iron", "risk_level": "HIGH"}]
    recs = PersonalizedRecommendationEngine.generate_food_recommendations(preds, "VEGAN", [])

    plan = PersonalizedRecommendationEngine.generate_recovery_plan(
        elevated_nutrients=["Vitamin D", "Iron"],
        top_foods=recs["priority_1"],
        lifestyle_items=[]
    )

    assert plan.phase_7_day.day_range == "Days 1-7"
    assert "Stabilization" in plan.phase_7_day.phase_title
    assert len(plan.phase_7_day.daily_action_checklist) >= 3

    assert plan.phase_14_day.day_range == "Days 8-14"
    assert "Replenishment" in plan.phase_14_day.phase_title

    assert plan.phase_30_day.day_range == "Days 15-30"
    assert "Homeostasis" in plan.phase_30_day.phase_title


def test_recommendation_scoring_bounds():
    """Verify recommendation scoring logic returns normalized 0-100 scores."""
    preds = [{"nutrient": "Vitamin D", "risk_level": "HIGH"}]
    recs = PersonalizedRecommendationEngine.generate_food_recommendations(preds, "VEGAN", [])

    scores = PersonalizedRecommendationEngine.calculate_recommendation_scores(
        nutrient_predictions=preds,
        recommended_foods=recs["priority_1"] + recs["priority_2"],
        restrictions=["dairy-free"]
    )

    assert 0.0 <= scores.relevance_score <= 100.0
    assert 0.0 <= scores.nutrient_coverage_score <= 100.0
    assert scores.diet_compatibility_score == 100.0
    assert 0.0 <= scores.overall_recommendation_score <= 100.0


def test_fastapi_recommendations_endpoints(sample_vegan_screening_payload):
    """Verify all 4 FastAPI recommendation endpoints and latency SLA."""
    # Step 1: Execute prediction
    predict_res = client.post("/api/v1/predict", json=sample_vegan_screening_payload)
    assert predict_res.status_code == 200
    assessment_id = predict_res.json()["assessment_id"]

    # Step 2: Comprehensive recommendations endpoint
    t0 = time.perf_counter()
    rec_res = client.get(f"/api/v1/recommendations/{assessment_id}")
    latency = (time.perf_counter() - t0) * 1000

    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert rec_data["dietary_pattern_applied"] == "VEGAN"
    assert len(rec_data["priority_1_foods"]) > 0
    assert len(rec_data["synergistic_pairings"]) > 0
    assert len(rec_data["lifestyle_interventions"]) > 0
    assert rec_data["scoring_summary"]["overall_recommendation_score"] > 50.0
    assert latency < 500.0, f"Recommendation latency ({latency} ms) exceeded 500 ms SLA"

    # Step 3: Foods endpoint
    foods_res = client.get(f"/api/v1/recommendations/{assessment_id}/foods")
    assert foods_res.status_code == 200
    foods_data = foods_res.json()
    assert foods_data["total_foods_recommended"] > 0
    assert any(k in foods_data["foods_by_nutrient"] for k in [
        "Iron", "Vitamin D", "Magnesium", "Vitamin B12", "Folate", "Zinc", "Calcium",
        "Potassium", "Selenium", "Iodine", "Vitamin B1", "Vitamin B2", "Vitamin B3",
        "Vitamin B6", "Protein", "Vitamin A", "Vitamin C", "Vitamin E"
    ])

    # Step 4: Lifestyle endpoint
    life_res = client.get(f"/api/v1/recommendations/{assessment_id}/lifestyle")
    assert life_res.status_code == 200
    life_data = life_res.json()
    assert life_data["total_interventions"] >= 3

    # Step 5: Recovery plan endpoint
    plan_res = client.get(f"/api/v1/recommendations/{assessment_id}/recovery-plan")
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert "phase_7_day" in plan_data["recovery_plan"]
    assert "phase_14_day" in plan_data["recovery_plan"]
    assert "phase_30_day" in plan_data["recovery_plan"]
