"""
Test Suite: Phase 8 — Nutrition Intelligence & Clinical Decision Engine
Verifies all 6 core engines, FastAPI REST endpoints, and latency performance targets.
"""

import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.intelligence.nutrient_gaps import NutrientGapEngine, NIH_REFERENCE_STANDARDS
from backend.app.modules.intelligence.meal_planner import MealIntelligenceEngine
from backend.app.modules.intelligence.substitutions import FoodSubstitutionEngine
from backend.app.modules.intelligence.supplements import SupplementIntelligenceEngine
from backend.app.modules.intelligence.recovery_simulator import RecoveryProjectionSimulator
from backend.app.modules.intelligence.decision_engine import ClinicalDecisionEngine
from backend.app.modules.intelligence.service import NutritionIntelligenceService
from backend.app.modules.intelligence.schemas import MealPlanRequest, GenerateIntelligencePlanRequest


@pytest.fixture
def client():
    return TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Nutrient Gap Analysis Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_nutrient_gap_engine_all_nutrients():
    engine = NutrientGapEngine()
    resp = engine.compute_gap_analysis(
        predicted_deficiencies=["IRON", "VITAMIN_D", "MAGNESIUM"],
        gender="FEMALE"
    )

    assert resp.total_nutrients_evaluated == len(NIH_REFERENCE_STANDARDS)
    assert 0 <= resp.nutrient_gap_score <= 100
    assert len(resp.severe_deficits) >= 1
    assert len(resp.all_gaps) == len(NIH_REFERENCE_STANDARDS)

    # Verify iron calculations for female
    iron_item = next(g for g in resp.all_gaps if g.nutrient_code == "IRON")
    assert iron_item.rda_target == 18.0
    assert iron_item.classification in ["SEVERE_DEFICIT", "MODERATE_DEFICIT"]
    assert iron_item.deficit_gap > 0
    assert iron_item.adequacy_percentage < 50.0

    # Verify category summaries
    assert len(resp.daily_intake_summary) >= 3


def test_nutrient_gap_gender_stratification():
    engine = NutrientGapEngine()
    male_resp = engine.compute_gap_analysis(predicted_deficiencies=[], gender="MALE")
    female_resp = engine.compute_gap_analysis(predicted_deficiencies=[], gender="FEMALE")

    male_iron = next(g for g in male_resp.all_gaps if g.nutrient_code == "IRON")
    female_iron = next(g for g in female_resp.all_gaps if g.nutrient_code == "IRON")

    assert male_iron.rda_target == 8.0
    assert female_iron.rda_target == 18.0


def test_gap_analysis_latency_target():
    """Performance Target: Gap analysis < 50 ms"""
    engine = NutrientGapEngine()
    t0 = time.perf_counter()
    _ = engine.compute_gap_analysis(
        predicted_deficiencies=["IRON", "VITAMIN_D", "VITAMIN_B12", "MAGNESIUM"],
        gender="FEMALE"
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 50.0, f"Gap analysis exceeded 50ms target: {elapsed_ms:.2f}ms"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Personalized Meal Intelligence Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_meal_intelligence_daily_plan():
    engine = MealIntelligenceEngine()
    daily = engine.generate_daily_plan(
        day_name="Monday",
        day_number=1,
        target_deficiencies=["IRON", "CALCIUM"],
        dietary_preference="OMNIVORE",
        budget_level="MODERATE",
        cuisine_preference="MEDITERRANEAN"
    )

    assert daily.breakfast.meal_type == "BREAKFAST"
    assert daily.lunch.meal_type == "LUNCH"
    assert daily.dinner.meal_type == "DINNER"
    assert daily.snack.meal_type == "SNACK"
    assert daily.daily_calories > 1200
    assert daily.daily_protein_g > 50
    assert daily.daily_average_bioavailability > 70.0
    assert daily.daily_average_correction_efficiency > 70.0


def test_meal_intelligence_vegan_filtering():
    engine = MealIntelligenceEngine()
    daily = engine.generate_daily_plan(
        target_deficiencies=["VITAMIN_B12", "PROTEIN"],
        dietary_preference="VEGAN"
    )

    for meal in [daily.breakfast, daily.lunch, daily.dinner, daily.snack]:
        assert "VEGAN" in meal.dietary_tags


def test_meal_intelligence_weekly_plan():
    engine = MealIntelligenceEngine()
    weekly = engine.generate_weekly_plan(
        target_deficiencies=["IRON", "VITAMIN_D"],
        dietary_preference="OMNIVORE"
    )

    assert len(weekly.days) == 7
    assert len(weekly.weekly_grocery_staples) > 5


def test_meal_generation_latency_target():
    """Performance Target: Meal generation < 100 ms"""
    engine = MealIntelligenceEngine()
    t0 = time.perf_counter()
    _ = engine.generate_weekly_plan(
        target_deficiencies=["IRON", "VITAMIN_D", "MAGNESIUM", "CALCIUM"],
        dietary_preference="OMNIVORE"
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 100.0, f"Meal generation exceeded 100ms target: {elapsed_ms:.2f}ms"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Food Substitution Intelligence Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_food_substitution_engine():
    engine = FoodSubstitutionEngine()
    all_subs = engine.get_all_substitutions()

    assert all_subs.total_available >= 5

    # Check spinach to kale
    spinach_swap = next(s for s in all_subs.substitutions if s.substitution_id == "spinach_to_kale")
    assert "Spinach" in spinach_swap.original_food
    assert "Kale" in spinach_swap.substitute_food
    assert spinach_swap.bioavailability_multiplier_delta > 1.0
    assert len(spinach_swap.nutrient_deltas) >= 3
    assert len(spinach_swap.clinical_tradeoffs) >= 2

    # Check deficiency filter
    iron_swaps = engine.find_substitutions_for_deficiencies(["IRON"])
    assert len(iron_swaps) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 4. Supplement Intelligence Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_supplement_intelligence_engine():
    engine = SupplementIntelligenceEngine()
    res = engine.get_supplement_guidance(deficiencies=["VITAMIN_D", "IRON", "MAGNESIUM"])

    # Educational guidance disclaimer check
    assert "EDUCATIONAL" in res.disclaimer.upper()
    assert "NOT MEDICAL PRESCRIPTIONS" in res.disclaimer.upper()

    assert len(res.recommended_supplements) >= 3
    vit_d = next(s for s in res.recommended_supplements if s.nutrient_code == "VITAMIN_D")
    assert "Cholecalciferol" in vit_d.suggested_form
    assert vit_d.timing_category == "MORNING_WITH_FAT"
    assert len(vit_d.food_interaction_warnings) >= 1
    assert len(vit_d.nutrient_interaction_warnings) >= 1

    iron_supp = next(s for s in res.recommended_supplements if s.nutrient_code == "IRON")
    assert iron_supp.timing_category == "MORNING_EMPTY_STOMACH"
    assert any("Calcium" in w for w in iron_supp.nutrient_interaction_warnings)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Recovery Projection Simulator Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_recovery_projection_simulator():
    simulator = RecoveryProjectionSimulator()
    res = simulator.simulate_recovery(
        baseline_health_score=52.0,
        detected_deficiencies=["IRON", "VITAMIN_D", "MAGNESIUM"]
    )

    assert res.baseline_health_score == 52.0
    assert res.projected_30_day_score > res.baseline_health_score
    assert res.projected_60_day_score > res.projected_30_day_score
    assert res.projected_90_day_score > res.projected_60_day_score

    # Check confidence bounds
    for pt in res.risk_reduction_trajectory:
        assert pt.confidence_lower_bound <= pt.projected_health_score <= pt.confidence_upper_bound

    # Check milestones
    assert len(res.milestones) == 4
    assert res.milestones[0].day == 14
    assert res.milestones[-1].day == 90

    # Check nutrient probabilities
    assert len(res.nutrient_probabilities) >= 3
    for np in res.nutrient_probabilities:
        assert 0.0 < np.day_30_probability <= np.day_60_probability <= np.day_90_probability <= 1.0


def test_projection_simulation_latency_target():
    """Performance Target: Projection simulation < 150 ms"""
    simulator = RecoveryProjectionSimulator()
    t0 = time.perf_counter()
    _ = simulator.simulate_recovery(
        baseline_health_score=45.0,
        detected_deficiencies=["IRON", "VITAMIN_D", "VITAMIN_B12", "FOLATE", "CALCIUM"]
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 150.0, f"Projection simulation exceeded 150ms target: {elapsed_ms:.2f}ms"


# ─────────────────────────────────────────────────────────────────────────────
# 6. Clinical Decision Engine Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_clinical_decision_engine():
    engine = ClinicalDecisionEngine()
    res = engine.generate_action_plan(
        detected_deficiencies=["IRON", "VITAMIN_D"],
        nutrient_gap_score=55.0
    )

    assert 0 <= res.clinical_priority_score <= 100
    assert res.highest_impact_intervention is not None
    assert res.fastest_recovery_action is not None
    assert len(res.ranked_action_plan) == 5
    assert len(res.lifestyle_priorities) >= 3
    assert len(res.food_priorities) >= 3
    assert len(res.laboratory_testing_priorities) >= 3


# ─────────────────────────────────────────────────────────────────────────────
# 7. Live FastAPI Endpoints & Latency Benchmarks
# ─────────────────────────────────────────────────────────────────────────────

def test_api_get_gaps(client):
    res = client.get("/api/v1/intelligence/gaps?gender=FEMALE")
    assert res.status_code == 200
    data = res.json()
    assert "nutrient_gap_score" in data
    assert "severe_deficits" in data


def test_api_get_meals(client):
    res = client.get("/api/v1/intelligence/meals?dietary_preference=OMNIVORE&budget_level=MODERATE&include_weekly=true")
    assert res.status_code == 200
    data = res.json()
    assert "daily_plan" in data
    assert "weekly_plan" in data


def test_api_get_substitutions(client):
    res = client.get("/api/v1/intelligence/substitutions")
    assert res.status_code == 200
    data = res.json()
    assert data["total_available"] >= 5


def test_api_get_supplements(client):
    res = client.get("/api/v1/intelligence/supplements")
    assert res.status_code == 200
    data = res.json()
    assert "disclaimer" in data
    assert len(data["recommended_supplements"]) >= 1


def test_api_get_projections(client):
    res = client.get("/api/v1/intelligence/projections?baseline_score=58.0")
    assert res.status_code == 200
    data = res.json()
    assert "risk_reduction_trajectory" in data
    assert "milestones" in data


def test_api_get_action_plan(client):
    res = client.get("/api/v1/intelligence/action-plan?gap_score=60.0")
    assert res.status_code == 200
    data = res.json()
    assert "clinical_priority_score" in data
    assert "ranked_action_plan" in data


def test_api_post_generate_plan_and_latency(client):
    """Performance Target: API response < 200 ms"""
    payload = {
        "assessment_id": "demo",
        "gender": "FEMALE",
        "dietary_preference": "OMNIVORE",
        "budget_level": "MODERATE",
        "cuisine_preference": "MEDITERRANEAN",
        "confirmed_deficiencies": ["IRON", "VITAMIN_D", "MAGNESIUM"]
    }

    # Pre-warm route handler cache
    _ = client.post("/api/v1/intelligence/generate-plan", json=payload)

    t0 = time.perf_counter()
    res = client.post("/api/v1/intelligence/generate-plan", json=payload)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert res.status_code == 200
    data = res.json()
    assert "nutrient_gaps" in data
    assert "meal_intelligence" in data
    assert "food_substitutions" in data
    assert "supplement_guidance" in data
    assert "recovery_projections" in data
    assert "clinical_action_plan" in data
    assert elapsed_ms < 200.0, f"API response exceeded 200ms target: {elapsed_ms:.2f}ms"
