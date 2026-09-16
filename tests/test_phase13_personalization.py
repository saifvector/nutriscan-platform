"""
Phase 13 Comprehensive Test Suite
Validates:
1. Personalized Nutrition Optimization Engine
2. Precision Food Recommendation Engine (USDA FDC integration)
3. Intelligent Meal Planning & Smart Grocery Lists
4. Recommendation Ranking Engine (Unified Intervention Score)
5. Clinical Outcome Forecasting (30, 60, 90-day 95% CIs)
6. Longitudinal Continuous Learning & Feedback Adaptation
7. Explainable Recommendation Reasoning & Substitutions
8. FastAPI REST Endpoints across /api/v1/personalization/*, /api/v1/recommendations/*, /api/v1/meal-plans/*, /api/v1/forecasting/*
9. Backward compatibility with Phases 1-12.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.personalization.schemas import (
    OptimizationRequest,
    PrecisionFoodQuery,
    MealPlanGenerateRequest,
    OutcomeForecastRequest,
    RecommendationFeedbackRequest,
    InterventionComparisonRequest,
    DietaryPatternEnum,
    CulturalPatternEnum,
    BudgetTierEnum
)
from backend.app.modules.personalization.optimization_engine import PersonalizationOptimizationEngine
from backend.app.modules.personalization.precision_foods import PrecisionFoodEngine
from backend.app.modules.personalization.meal_planner_pro import IntelligentMealPlanner
from backend.app.modules.personalization.ranking_engine import RecommendationRankingEngine
from backend.app.modules.personalization.forecasting_engine import ClinicalOutcomeForecaster
from backend.app.modules.personalization.longitudinal_engine import LongitudinalPersonalizationEngine
from backend.app.modules.personalization.feedback_system import RecommendationFeedbackSystem
from backend.app.modules.personalization.explainable_reasoning import ExplainableRecommendationReasoning

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. OPTIMIZATION ENGINE TESTS
# ------------------------------------------------------------------------------

def test_optimization_engine_individualized_strategies():
    req = OptimizationRequest(
        target_deficiencies=["Iron", "Vitamin D"],
        dietary_pattern=DietaryPatternEnum.MEDITERRANEAN,
        cultural_pattern=CulturalPatternEnum.MEDITERRANEAN,
        budget_tier=BudgetTierEnum.MODERATE,
        daily_budget_usd=14.00,
        biomarkers={"ferritin": 14.5, "vitamin_d": 18.0}
    )
    resp = PersonalizationOptimizationEngine.optimize_strategy(req)

    assert resp.strategy_id.startswith("STRAT_")
    assert resp.dietary_pattern == "MEDITERRANEAN"
    assert "Iron" in resp.target_deficiencies
    assert "Vitamin D" in resp.target_deficiencies
    assert len(resp.ranked_interventions) >= 2
    assert resp.macro_targets["protein_pct"] > 0
    assert resp.macro_targets["carb_pct"] > 0
    assert resp.macro_targets["fat_pct"] > 0
    assert "Mediterranean Strategy" in resp.strategy_summary


def test_optimization_engine_keto_and_vegan_macros():
    # Keto check
    keto_req = OptimizationRequest(
        target_deficiencies=["Magnesium"],
        dietary_pattern=DietaryPatternEnum.KETO
    )
    keto_resp = PersonalizationOptimizationEngine.optimize_strategy(keto_req)
    assert keto_resp.macro_targets["fat_pct"] == 70.0
    assert keto_resp.macro_targets["carb_pct"] == 5.0

    # Vegan check
    vegan_req = OptimizationRequest(
        target_deficiencies=["Vitamin B12", "Iron"],
        dietary_pattern=DietaryPatternEnum.VEGAN
    )
    vegan_resp = PersonalizationOptimizationEngine.optimize_strategy(vegan_req)
    assert vegan_resp.macro_targets["carb_pct"] == 55.0


# ------------------------------------------------------------------------------
# 2. PRECISION FOOD RECOMMENDATION TESTS
# ------------------------------------------------------------------------------

def test_precision_food_recommendations_usda_density():
    q = PrecisionFoodQuery(
        target_deficiencies=["Iron", "Vitamin D", "Selenium"],
        dietary_pattern=DietaryPatternEnum.OMNIVORE,
        cultural_pattern=CulturalPatternEnum.MEDITERRANEAN,
        limit=5
    )
    resp = PrecisionFoodEngine.query_precision_foods(q)

    assert resp.total_matches > 0
    assert len(resp.top_recommended_foods) <= 5
    top_food = resp.top_recommended_foods[0]

    assert top_food.food_name is not None
    assert top_food.usda_fdc_id is not None
    assert top_food.nutrient_density_score > 0
    assert top_food.bioavailability_score > 0
    assert top_food.clinical_relevance_score > 0
    assert top_food.composite_precision_score > 0
    assert len(top_food.substitutions) > 0


def test_multi_deficiency_food_optimization():
    # Query foods specifically targeting both Vitamin D and Selenium
    q = PrecisionFoodQuery(
        target_deficiencies=["Vitamin D", "Selenium"],
        dietary_pattern=DietaryPatternEnum.PESCATARIAN
    )
    resp = PrecisionFoodEngine.query_precision_foods(q)

    # Wild Salmon and Sardines should be ranked at the very top
    top_names = [f.food_name for f in resp.top_recommended_foods[:3]]
    assert any("Salmon" in name or "Sardines" in name for name in top_names)


# ------------------------------------------------------------------------------
# 3. INTELLIGENT MEAL PLAN & GROCERY LIST TESTS
# ------------------------------------------------------------------------------

def test_daily_and_weekly_meal_generation():
    req = MealPlanGenerateRequest(
        target_deficiencies=["Iron", "Vitamin D", "Folate"],
        cultural_pattern=CulturalPatternEnum.MEDITERRANEAN,
        dietary_pattern=DietaryPatternEnum.OMNIVORE,
        daily_calorie_target=2000,
        daily_budget_usd=15.00,
        plan_duration_days=7
    )
    plan = IntelligentMealPlanner.generate_plan(req)

    assert plan.plan_id.startswith("PLAN_")
    assert plan.plan_duration_days == 7
    assert len(plan.daily_plans) == 7
    assert plan.total_weekly_cost_usd > 0
    assert plan.nutrient_adequacy_score >= 50.0

    day1 = plan.daily_plans[0]
    assert day1.day_name == "Monday"
    assert len(day1.meals) == 4 # Breakfast, Lunch, Dinner, Snack
    assert day1.total_daily_calories > 1200
    assert "Iron" in day1.nutrient_coverage_pct


def test_grocery_list_generation_and_departments():
    req = MealPlanGenerateRequest(
        target_deficiencies=["Iron", "Folate"],
        cultural_pattern=CulturalPatternEnum.MEDITERRANEAN,
        plan_duration_days=3
    )
    plan = IntelligentMealPlanner.generate_plan(req)
    grocery = plan.grocery_list

    assert grocery.total_estimated_cost_usd > 0
    assert grocery.budget_adherence_status in ["UNDER_BUDGET", "ON_BUDGET", "OVER_BUDGET"]
    assert "PRODUCE" in grocery.department_groups
    assert "PROTEINS" in grocery.department_groups
    assert len(grocery.department_groups["PRODUCE"]) > 0


# ------------------------------------------------------------------------------
# 4. RANKING & UNIFIED INTERVENTION SCORE TESTS
# ------------------------------------------------------------------------------

def test_unified_intervention_score_ranking():
    interventions = RecommendationRankingEngine.rank_interventions(
        target_deficiencies=["Iron", "Vitamin D", "Magnesium"],
        dietary_pattern="OMNIVORE"
    )

    assert len(interventions) >= 3
    # Check monotonic descending order of unified scores
    for i in range(len(interventions) - 1):
        assert interventions[i].unified_score >= interventions[i + 1].unified_score

    top = interventions[0]
    assert top.unified_score >= 50.0
    assert top.tier.value in ["TOP_PRIORITY", "HIGH_IMPACT", "SUPPORTIVE", "MAINTENANCE"]
    assert len(top.alternatives) > 0


def test_intervention_comparison_service():
    req = InterventionComparisonRequest(target_deficiencies=["Iron", "Vitamin D"])
    resp = RecommendationRankingEngine.compare_interventions(req)

    assert len(resp.comparison_table) == 3
    types = [row.intervention_type for row in resp.comparison_table]
    assert "FOOD_ONLY" in types
    assert "FOOD_PLUS_SUPPLEMENT" in types
    assert "LIFESTYLE_FIRST" in types
    assert resp.recommended_option is not None


# ------------------------------------------------------------------------------
# 5. CLINICAL OUTCOME FORECASTING TESTS
# ------------------------------------------------------------------------------

def test_clinical_outcome_forecasting_confidence_intervals():
    req = OutcomeForecastRequest(
        target_nutrients=["Iron", "Vitamin D", "Folate"],
        adherence_assumption_pct=90.0,
        include_supplements=True
    )
    resp = ClinicalOutcomeForecaster.generate_full_forecast(req)

    assert len(resp.forecasts) == 3
    assert resp.adherence_assumption_pct == 90.0
    assert len(resp.executive_prognosis) > 20
    assert "adherence" in resp.executive_prognosis.lower() or "normalization" in resp.executive_prognosis.lower()

    iron_fc = next(f for f in resp.forecasts if f.nutrient == "Iron")
    assert iron_fc.unit == "ng/mL"
    assert len(iron_fc.trajectory_points) == 3

    # Check 30, 60, 90 day points
    p30, p60, p90 = iron_fc.trajectory_points
    assert p30.horizon_days == 30
    assert p60.horizon_days == 60
    assert p90.horizon_days == 90

    # Upper bound must be strictly greater than lower bound
    assert p30.upper_bound_95 > p30.lower_bound_95
    assert p60.upper_bound_95 > p60.lower_bound_95
    assert p90.upper_bound_95 > p90.lower_bound_95

    # Saturation progression: 90 day predicted >= 30 day predicted
    assert p90.predicted_level >= p30.predicted_level
    assert 0.0 <= p60.normalization_probability <= 1.0


# ------------------------------------------------------------------------------
# 6. LONGITUDINAL CONTINUOUS LEARNING & FEEDBACK TESTS
# ------------------------------------------------------------------------------

def test_longitudinal_personalization_response_patterns():
    user_id = "USER_TEST_123"

    # Process successful outcome
    succ = LongitudinalPersonalizationEngine.process_intervention_outcome(
        user_id=user_id,
        intervention_id="INT_IRON_BISGLYCINATE",
        nutrient="Iron",
        adherence_rate=90.0,
        symptom_delta=-3.5,
        reported_side_effects=[]
    )
    assert succ["outcome_status"] == "SUCCESSFUL_INTERVENTION"
    prof = succ["adapted_profile"]
    assert "INT_IRON_BISGLYCINATE" in prof["successful_interventions"]
    assert prof["efficacy_multipliers"]["Iron"] > 1.0

    # Process failed outcome (GI distress)
    fail = LongitudinalPersonalizationEngine.process_intervention_outcome(
        user_id=user_id,
        intervention_id="INT_FERROUS_SULFATE_HARSH",
        nutrient="Iron",
        adherence_rate=30.0,
        symptom_delta=0.0,
        reported_side_effects=["Severe Nausea", "Constipation"]
    )
    assert fail["outcome_status"] == "FAILED_OR_ABANDONED"
    assert "INT_FERROUS_SULFATE_HARSH" in fail["adapted_profile"]["failed_interventions"]
    assert fail["adapted_profile"]["tolerance_penalties"]["INT_FERROUS_SULFATE_HARSH"] < 1.0


def test_recommendation_feedback_dynamic_adaptation():
    # 5-star rating
    pos_req = RecommendationFeedbackRequest(
        user_id="USER_FEEDBACK_TEST",
        recommendation_id="FOOD_SALMON_WILD",
        item_name="Wild Salmon",
        item_type="FOOD",
        rating=5,
        taste_score=5,
        preparation_ease_score=4
    )
    pos_resp = RecommendationFeedbackSystem.record_feedback(pos_req)
    assert pos_resp.status == "SUCCESS"
    assert pos_resp.adapted_preference_weight >= 1.0

    # 1-star adverse feedback
    neg_req = RecommendationFeedbackRequest(
        user_id="USER_FEEDBACK_TEST",
        recommendation_id="SUPP_ZINC_ACETATE",
        item_name="Zinc Acetate",
        item_type="SUPPLEMENT",
        rating=1,
        reported_side_effects=["Severe Acid Reflux"]
    )
    neg_resp = RecommendationFeedbackSystem.record_feedback(neg_req)
    assert neg_resp.status == "SUCCESS"
    assert neg_resp.adapted_preference_weight <= 0.5


def test_explainable_recommendation_reasoning():
    rationale = ExplainableRecommendationReasoning.generate_rationale(
        intervention_name="Heme Iron & Ascorbic Acid Pairing",
        target_nutrients=["Iron", "Vitamin C"]
    )
    assert "Iron" in rationale["target_nutrients"]
    assert len(rationale["why_selected"]) > 10
    assert len(rationale["expected_benefit"]) > 10
    assert rationale["confidence_level"] in ["HIGH", "MODERATE", "EXPLORATORY"]
    assert len(rationale["alternative_options"]) >= 2


# ------------------------------------------------------------------------------
# 7. FASTAPI API INTEGRATION TESTS
# ------------------------------------------------------------------------------

def test_api_personalization_strategy():
    payload = {
        "target_deficiencies": ["Iron", "Vitamin D"],
        "dietary_pattern": "MEDITERRANEAN",
        "cultural_pattern": "MEDITERRANEAN",
        "budget_tier": "MODERATE",
        "daily_budget_usd": 15.0
    }
    resp = client.post("/api/v1/personalization/strategy", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "strategy_id" in data
    assert len(data["ranked_interventions"]) > 0


def test_api_recommendations_precision_foods():
    resp = client.get("/api/v1/recommendations/precision-foods?deficiencies=Iron,Vitamin%20D&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_matches"] > 0
    assert len(data["top_recommended_foods"]) <= 5


def test_api_meal_plans_weekly_and_grocery():
    payload = {
        "target_deficiencies": ["Iron", "Folate"],
        "cultural_pattern": "MEDITERRANEAN",
        "dietary_pattern": "OMNIVORE",
        "plan_duration_days": 7
    }
    resp = client.post("/api/v1/meal-plans/weekly", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "plan_id" in data
    assert len(data["daily_plans"]) == 7
    assert "grocery_list" in data
    assert "department_groups" in data["grocery_list"]


def test_api_forecasting_outcomes():
    payload = {
        "target_nutrients": ["Iron", "Vitamin D"],
        "adherence_assumption_pct": 85.0,
        "include_supplements": True
    }
    resp = client.post("/api/v1/forecasting/outcomes", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["forecasts"]) == 2
    assert "executive_prognosis" in data


def test_api_personalization_compare():
    payload = {"target_deficiencies": ["Iron", "Vitamin D"]}
    resp = client.post("/api/v1/personalization/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["comparison_table"]) == 3
    assert "recommended_option" in data


def test_api_personalization_feedback():
    payload = {
        "recommendation_id": "REC_TEST_001",
        "item_name": "Greek Yogurt with Pumpkin Seeds",
        "item_type": "MEAL",
        "rating": 5,
        "taste_score": 5
    }
    resp = client.post("/api/v1/personalization/feedback", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert "adapted_preference_weight" in data


def test_backward_compatibility_regression_check():
    """Confirms Phase 1-12 prediction and health endpoints remain operational."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

    # Governance monitoring endpoint
    resp_gov = client.get("/api/v1/monitoring/metrics")
    assert resp_gov.status_code == 200
