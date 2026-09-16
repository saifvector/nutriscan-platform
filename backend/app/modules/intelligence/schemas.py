"""
Pydantic V2 Data Models for Phase 8: Nutrition Intelligence & Clinical Decision Engine
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# 1. Nutrient Gap Analysis Schemas
# ─────────────────────────────────────────────────────────────────────────────

class NutrientGapItem(BaseModel):
    nutrient_code: str
    common_name: str
    category: str
    unit: str
    estimated_daily_intake: float
    rda_target: float
    adequate_intake_target: Optional[float] = None
    tolerable_upper_limit: Optional[float] = None
    adequacy_percentage: float = Field(..., description="Estimated intake as % of RDA")
    deficit_gap: float = Field(..., description="Max(0, RDA - Estimated Intake)")
    classification: str = Field(..., description="SEVERE_DEFICIT, MODERATE_DEFICIT, OPTIMAL, EXCESS_RISK")
    clinical_urgency_weight: float
    severity_rank: int
    key_dietary_sources: List[str] = Field(default_factory=list)


class DailyIntakeSummaryItem(BaseModel):
    category: str
    total_nutrients_monitored: int
    optimal_count: int
    moderate_deficit_count: int
    severe_deficit_count: int
    excess_risk_count: int
    average_adequacy_pct: float


class NutrientGapAnalysisResponse(BaseModel):
    assessment_id: Optional[str] = None
    nutrient_gap_score: float = Field(..., description="Overall micronutrient sufficiency score (0-100)")
    status_summary: str
    total_nutrients_evaluated: int
    severe_deficits: List[NutrientGapItem]
    moderate_deficits: List[NutrientGapItem]
    optimal_nutrients: List[NutrientGapItem]
    excess_risk_nutrients: List[NutrientGapItem]
    all_gaps: List[NutrientGapItem]
    daily_intake_summary: List[DailyIntakeSummaryItem]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Personalized Meal Intelligence Schemas
# ─────────────────────────────────────────────────────────────────────────────

class MealRecipeItem(BaseModel):
    meal_type: str = Field(..., description="BREAKFAST, LUNCH, DINNER, SNACK")
    recipe_title: str
    description: str
    calories: int
    protein_g: float
    carbs_g: float
    fats_g: float
    target_nutrients_closed: List[str]
    nutrient_density_score: float = Field(..., description="Scale 0-100")
    bioavailability_score: float = Field(..., description="Scale 0-100")
    correction_efficiency_score: float = Field(..., description="Scale 0-100")
    preparation_time_minutes: int
    budget_level: str = Field(..., description="BUDGET, MODERATE, PREMIUM")
    dietary_tags: List[str]
    cuisine_type: str
    key_ingredients: List[str]
    clinical_notes: str


class DailyMealPlan(BaseModel):
    day_name: str
    day_number: int
    breakfast: MealRecipeItem
    lunch: MealRecipeItem
    dinner: MealRecipeItem
    snack: MealRecipeItem
    daily_calories: int
    daily_protein_g: float
    daily_carbs_g: float
    daily_fats_g: float
    daily_average_bioavailability: float
    daily_average_correction_efficiency: float


class WeeklyMealPlan(BaseModel):
    plan_title: str
    dietary_preference: str
    budget_level: str
    cuisine_preference: str
    days: List[DailyMealPlan]
    weekly_grocery_staples: List[str]


class MealIntelligenceResponse(BaseModel):
    assessment_id: Optional[str] = None
    target_deficiencies: List[str]
    dietary_preference: str
    budget_level: str
    cuisine_preference: str
    daily_plan: DailyMealPlan
    weekly_plan: Optional[WeeklyMealPlan] = None
    deficiency_recovery_templates: List[Dict[str, Any]] = Field(default_factory=list)


class MealPlanRequest(BaseModel):
    assessment_id: Optional[str] = None
    deficiencies: Optional[List[str]] = None
    dietary_preference: Optional[str] = "OMNIVORE"  # VEGAN, VEGETARIAN, KETO, MEDITERRANEAN, DAIRY_FREE, GLUTEN_FREE, OMNIVORE
    budget_level: Optional[str] = "MODERATE"       # BUDGET, MODERATE, PREMIUM
    cuisine_preference: Optional[str] = "MEDITERRANEAN"  # MEDITERRANEAN, ASIAN, AMERICAN, GLOBAL_FUSION
    include_weekly: Optional[bool] = False


# ─────────────────────────────────────────────────────────────────────────────
# 3. Food Substitution Intelligence Schemas
# ─────────────────────────────────────────────────────────────────────────────

class NutrientDeltaItem(BaseModel):
    nutrient_name: str
    original_value: float
    substitute_value: float
    delta_value: float
    percentage_change: float
    unit: str
    clinical_interpretation: str


class FoodSubstitutionItem(BaseModel):
    substitution_id: str
    original_food: str
    substitute_food: str
    primary_purpose: str = Field(..., description="e.g. Bioavailability boost, Plant-based swap, Lower oxalates")
    macronutrient_differences: Dict[str, str]
    nutrient_deltas: List[NutrientDeltaItem]
    bioavailability_change_description: str
    bioavailability_multiplier_delta: float
    clinical_tradeoffs: List[str]
    culinary_preparation_tips: str
    recommended_for_deficiencies: List[str]


class FoodSubstitutionsResponse(BaseModel):
    total_available: int
    substitutions: List[FoodSubstitutionItem]


# ─────────────────────────────────────────────────────────────────────────────
# 4. Supplement Intelligence Schemas
# ─────────────────────────────────────────────────────────────────────────────

class SupplementRecommendationItem(BaseModel):
    nutrient_code: str
    nutrient_name: str
    suggested_form: str
    therapeutic_dosage_range: str
    maintenance_dosage_range: str
    optimal_timing: str
    timing_category: str = Field(..., description="MORNING_WITH_FAT, MORNING_EMPTY_STOMACH, EVENING_BEFORE_BED, WITH_MAIN_MEAL")
    food_interaction_warnings: List[str]
    nutrient_interaction_warnings: List[str]
    nih_dsid_reference: str
    contraindications: List[str]
    urgency_tier: str = Field(..., description="HIGH, MODERATE, LOW")


class SupplementIntelligenceResponse(BaseModel):
    assessment_id: Optional[str] = None
    disclaimer: str = Field(
        default="EDUCATIONAL AND CLINICAL DECISION SUPPORT GUIDANCE ONLY. Not medical prescriptions. Consult a licensed healthcare provider before initiating high-dose micronutrient supplementation."
    )
    recommended_supplements: List[SupplementRecommendationItem]
    general_cautions: List[str]


# ─────────────────────────────────────────────────────────────────────────────
# 5. Recovery Projection Simulator Schemas
# ─────────────────────────────────────────────────────────────────────────────

class RecoveryMilestone(BaseModel):
    day: int
    milestone_name: str
    biological_mechanism: str
    expected_symptom_relief: List[str]
    health_score_target: float


class RecoveryTrajectoryPoint(BaseModel):
    day: int
    projected_health_score: float
    confidence_lower_bound: float
    confidence_upper_bound: float
    adherence_assumption_pct: float


class NutrientRecoveryProbability(BaseModel):
    nutrient_code: str
    common_name: str
    day_30_probability: float
    day_60_probability: float
    day_90_probability: float
    primary_limiting_factor: str


class RecoveryProjectionResponse(BaseModel):
    assessment_id: Optional[str] = None
    baseline_health_score: float
    projected_30_day_score: float
    projected_60_day_score: float
    projected_90_day_score: float
    overall_recovery_probability_90d: float
    risk_reduction_trajectory: List[RecoveryTrajectoryPoint]
    milestones: List[RecoveryMilestone]
    nutrient_probabilities: List[NutrientRecoveryProbability]


# ─────────────────────────────────────────────────────────────────────────────
# 6. Clinical Decision Engine Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ClinicalActionItem(BaseModel):
    priority_level: int = Field(..., description="1 to 5")
    action_type: str = Field(..., description="DIETARY, SUPPLEMENT, LAB_TEST, LIFESTYLE")
    headline: str
    rationale: str
    expected_impact_delta: float = Field(..., description="Predicted health score boost")
    implementation_timeframe: str
    clinical_guideline_source: str


class ClinicalDecisionResponse(BaseModel):
    assessment_id: Optional[str] = None
    clinical_priority_score: float = Field(..., description="Urgency index 0-100")
    highest_impact_intervention: ClinicalActionItem
    fastest_recovery_action: ClinicalActionItem
    ranked_action_plan: List[ClinicalActionItem]
    lifestyle_priorities: List[str]
    food_priorities: List[str]
    laboratory_testing_priorities: List[Dict[str, str]]


# ─────────────────────────────────────────────────────────────────────────────
# 7. Unified Plan Request / Response
# ─────────────────────────────────────────────────────────────────────────────

class GenerateIntelligencePlanRequest(BaseModel):
    assessment_id: Optional[str] = None
    gender: Optional[str] = "FEMALE"  # MALE, FEMALE
    dietary_preference: Optional[str] = "OMNIVORE"
    budget_level: Optional[str] = "MODERATE"
    cuisine_preference: Optional[str] = "MEDITERRANEAN"
    confirmed_deficiencies: Optional[List[str]] = None


class GenerateIntelligencePlanResponse(BaseModel):
    assessment_id: Optional[str]
    generated_at: str
    nutrient_gaps: NutrientGapAnalysisResponse
    meal_intelligence: MealIntelligenceResponse
    food_substitutions: FoodSubstitutionsResponse
    supplement_guidance: SupplementIntelligenceResponse
    recovery_projections: RecoveryProjectionResponse
    clinical_action_plan: ClinicalDecisionResponse
    execution_time_ms: float
