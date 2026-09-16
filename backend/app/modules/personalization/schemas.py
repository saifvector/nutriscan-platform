"""
Pydantic V2 Schemas for Phase 13: Personalization & Continuous Learning
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
from pydantic import BaseModel, Field


class DietaryPatternEnum(str, Enum):
    OMNIVORE = "OMNIVORE"
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    PESCATARIAN = "PESCATARIAN"
    KETO = "KETO"
    PALEO = "PALEO"
    MEDITERRANEAN = "MEDITERRANEAN"
    LOW_FODMAP = "LOW_FODMAP"
    GLUTEN_FREE = "GLUTEN_FREE"


class CulturalPatternEnum(str, Enum):
    MEDITERRANEAN = "MEDITERRANEAN"
    EAST_ASIAN = "EAST_ASIAN"
    SOUTH_ASIAN = "SOUTH_ASIAN"
    LATIN_AMERICAN = "LATIN_AMERICAN"
    NORDIC = "NORDIC"
    MIDDLE_EASTERN = "MIDDLE_EASTERN"
    WEST_AFRICAN = "WEST_AFRICAN"
    AMERICAN_HEART_HEALTHY = "AMERICAN_HEART_HEALTHY"


class BudgetTierEnum(str, Enum):
    LOW = "LOW"             # < $5/day
    MODERATE = "MODERATE"   # $5 - $12/day
    PREMIUM = "PREMIUM"     # > $12/day


class InterventionTierEnum(str, Enum):
    TOP_PRIORITY = "TOP_PRIORITY"
    HIGH_IMPACT = "HIGH_IMPACT"
    SUPPORTIVE = "SUPPORTIVE"
    MAINTENANCE = "MAINTENANCE"


# ------------------------------------------------------------------------------
# 1. OPTIMIZATION SCHEMAS
# ------------------------------------------------------------------------------

class OptimizationRequest(BaseModel):
    assessment_id: Optional[str] = Field(default=None, description="UUID of assessment")
    user_id: Optional[str] = Field(default=None, description="User UUID")
    target_deficiencies: Optional[List[str]] = Field(default=None, description="List of target deficiencies (e.g. Iron, Vitamin D)")
    biomarkers: Optional[Dict[str, float]] = Field(default_factory=dict, description="Continuous lab values (e.g. ferritin, 25(OH)D)")
    medical_history: Optional[List[str]] = Field(default_factory=list, description="Diagnosed conditions")
    food_preferences: Optional[List[str]] = Field(default_factory=list, description="Preferred ingredients or foods")
    food_dislikes: Optional[List[str]] = Field(default_factory=list, description="Disliked foods")
    dietary_pattern: DietaryPatternEnum = Field(default=DietaryPatternEnum.OMNIVORE)
    cultural_pattern: CulturalPatternEnum = Field(default=CulturalPatternEnum.MEDITERRANEAN)
    budget_tier: BudgetTierEnum = Field(default=BudgetTierEnum.MODERATE)
    daily_budget_usd: Optional[float] = Field(default=12.50, description="Daily food budget limit in USD")
    lifestyle_factors: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Sleep, sunlight, activity, stress")


class UnifiedInterventionItem(BaseModel):
    intervention_id: str
    title: str
    category: str # DIETARY, SUPPLEMENT, LIFESTYLE
    target_nutrients: List[str]
    unified_score: float = Field(..., description="Unified Intervention Score (0-100)")
    impact_score: float = Field(..., description="Expected deficiency resolution impact (0-100)")
    recovery_velocity_score: float = Field(..., description="Speed of biological replenishment (0-100)")
    burden_score: float = Field(..., description="Preparation difficulty and cost burden (0-100)")
    adherence_probability: float = Field(..., description="Model-estimated adherence likelihood (0-100)")
    tier: InterventionTierEnum
    clinical_rationale: str
    expected_benefit_30d: str
    evidence_citation: str
    alternatives: List[str] = Field(default_factory=list)


class OptimizationResponse(BaseModel):
    strategy_id: str
    assessment_id: Optional[str]
    dietary_pattern: str
    cultural_pattern: str
    budget_tier: str
    daily_budget_usd: float
    target_deficiencies: List[str]
    macro_targets: Dict[str, float]
    strategy_summary: str
    ranked_interventions: List[UnifiedInterventionItem]
    created_at: str


# ------------------------------------------------------------------------------
# 2. PRECISION FOOD SCHEMAS
# ------------------------------------------------------------------------------

class PrecisionFoodItem(BaseModel):
    food_name: str
    usda_fdc_id: Optional[str] = None
    category: str
    serving_size: str
    primary_nutrients: Dict[str, float] # nutrient: amount per serving
    nutrient_density_score: float = Field(..., description="0-100 density score per calorie")
    cost_efficiency_score: float = Field(..., description="0-100 score per dollar")
    bioavailability_score: float = Field(..., description="0-100 elemental absorption score")
    clinical_relevance_score: float = Field(..., description="0-100 alignment with patient deficiencies")
    adherence_likelihood_score: float = Field(..., description="0-100 palatability and ease")
    composite_precision_score: float = Field(..., description="Weighted composite precision score")
    culinary_role: str # Main, Side, Snack, Seasoning
    preparation_tips: str
    evidence_citation: str
    substitutions: List[str] = Field(default_factory=list)


class PrecisionFoodQuery(BaseModel):
    target_deficiencies: List[str] = Field(default_factory=lambda: ["Iron", "Vitamin D"])
    dietary_pattern: Optional[DietaryPatternEnum] = DietaryPatternEnum.OMNIVORE
    cultural_pattern: Optional[CulturalPatternEnum] = CulturalPatternEnum.MEDITERRANEAN
    max_budget_per_serving_usd: Optional[float] = 3.50
    limit: int = 15


class PrecisionFoodResponse(BaseModel):
    target_deficiencies: List[str]
    total_matches: int
    top_recommended_foods: List[PrecisionFoodItem]


# ------------------------------------------------------------------------------
# 3. INTELLIGENT MEAL PLAN SCHEMAS
# ------------------------------------------------------------------------------

class MealComponent(BaseModel):
    meal_type: str # BREAKFAST, LUNCH, DINNER, SNACK
    dish_name: str
    ingredients: List[str]
    key_nutrients_supplied: Dict[str, float]
    estimated_calories: int
    estimated_cost_usd: float
    prep_time_minutes: int
    culinary_instructions: str


class DailyMealPlan(BaseModel):
    day_number: int
    day_name: str
    meals: List[MealComponent]
    total_daily_calories: int
    total_daily_cost_usd: float
    nutrient_coverage_pct: Dict[str, float] # Nutrient -> % of RDA achieved
    daily_clinical_notes: str


class GroceryItem(BaseModel):
    item_name: str
    department: str # PRODUCE, PROTEINS, PANTRY, GRAINS, DAIRY_OR_PLANT_BASED
    quantity: str
    estimated_cost_usd: float
    serves_meals: List[str]


class GroceryListResponse(BaseModel):
    plan_id: str
    total_estimated_cost_usd: float
    department_groups: Dict[str, List[GroceryItem]]
    budget_adherence_status: str # UNDER_BUDGET, ON_BUDGET, OVER_BUDGET


class MealPlanGenerateRequest(BaseModel):
    assessment_id: Optional[str] = None
    patient_age: Optional[float] = None
    target_deficiencies: List[str] = Field(default_factory=lambda: ["Iron", "Vitamin D", "Folate"])
    dietary_pattern: DietaryPatternEnum = DietaryPatternEnum.OMNIVORE
    cultural_pattern: CulturalPatternEnum = CulturalPatternEnum.MEDITERRANEAN
    daily_calorie_target: int = 2000
    daily_budget_usd: float = 12.50
    plan_duration_days: int = Field(default=7, ge=1, le=14)
    family_servings: int = Field(default=1, ge=1, le=6)


class WeeklyMealPlan(BaseModel):
    plan_id: str
    cultural_pattern: str
    dietary_pattern: str
    plan_duration_days: int
    daily_average_cost_usd: float
    total_weekly_cost_usd: float
    nutrient_adequacy_score: float # 0-100
    overall_rda_compliance_pct: Dict[str, float] = Field(default_factory=dict)
    daily_plans: List[DailyMealPlan]
    grocery_list: GroceryListResponse
    cdss_disclosure: str = Field(
        default="NutriScan CDSS is an informational clinical decision support tool under FDA Section 520(o)(1)(E) and EU MDR (EU 2017/745). It does not replace independent professional medical judgment, laboratory diagnosis, or customized clinical prescription.",
        description="Statutory FDA 520(o)(1)(E) / CE MDR Clinical Decision Support System disclosure"
    )


# ------------------------------------------------------------------------------
# 4. CLINICAL OUTCOME FORECASTING SCHEMAS
# ------------------------------------------------------------------------------

class ForecastHorizonPoint(BaseModel):
    horizon_days: int # 30, 60, 90
    day: Optional[int] = None
    target_date: Optional[str] = None # Calculated calendar milestone date (YYYY-MM-DD)
    predicted_level: float
    predicted_value: Optional[float] = None
    lower_bound_95: float
    upper_bound_95: float
    normalization_probability: float # 0.0 - 1.0
    clinical_tier: str # SEVERELY_DEFICIENT, SUBOPTIMAL, NORMAL_REPLENISHED, OPTIMAL
    clinical_milestone: Optional[str] = None


class OutcomeForecastItem(BaseModel):
    nutrient: str
    unit: str
    baseline_value: float
    clinical_target: float
    target_value: Optional[float] = None
    recovery_velocity: str # RAPID, MODERATE, GRADUAL
    estimated_days_to_normalization: Optional[int] = None
    trajectory_points: List[ForecastHorizonPoint]
    key_drivers_accelerating: List[str]
    potential_impediments: List[str]


class OutcomeForecastRequest(BaseModel):
    assessment_id: Optional[str] = None
    patient_age: Optional[float] = None
    target_nutrients: List[str] = Field(default_factory=lambda: ["Iron", "Vitamin D", "Folate"])
    baseline_values: Optional[Dict[str, float]] = None # Patient-specific starting biomarker levels
    adherence_assumption_pct: float = Field(default=85.0, ge=20.0, le=100.0)
    include_supplements: bool = True


class OutcomeForecastResponse(BaseModel):
    assessment_id: Optional[str]
    adherence_assumption_pct: float
    forecast_model: str
    forecasts: List[OutcomeForecastItem]
    trajectories: Dict[str, Any] = Field(default_factory=dict)
    executive_prognosis: str
    cdss_disclosure: str = Field(
        default="NutriScan CDSS is an informational clinical decision support tool under FDA Section 520(o)(1)(E) and EU MDR (EU 2017/745). It does not replace independent professional medical judgment, laboratory diagnosis, or customized clinical prescription.",
        description="Statutory FDA 520(o)(1)(E) / CE MDR Clinical Decision Support System disclosure"
    )


# ------------------------------------------------------------------------------
# 5. RECOMMENDATION FEEDBACK SCHEMAS
# ------------------------------------------------------------------------------

class RecommendationFeedbackRequest(BaseModel):
    user_id: Optional[str] = None
    assessment_id: Optional[str] = None
    recommendation_id: str
    item_name: str
    item_type: str # FOOD, MEAL, SUPPLEMENT, LIFESTYLE
    rating: int = Field(..., ge=1, le=5, description="1 to 5 stars")
    taste_score: Optional[int] = Field(default=None, ge=1, le=5)
    preparation_ease_score: Optional[int] = Field(default=None, ge=1, le=5)
    adhered: bool = True
    reported_side_effects: Optional[List[str]] = Field(default_factory=list)
    comments: Optional[str] = None


class RecommendationFeedbackResponse(BaseModel):
    status: str
    feedback_id: str
    message: str
    adapted_preference_weight: float
    next_action_recommendation: str


# ------------------------------------------------------------------------------
# 6. INTERVENTION COMPARISON SCHEMAS
# ------------------------------------------------------------------------------

class InterventionComparisonRequest(BaseModel):
    target_deficiencies: List[str] = Field(default_factory=lambda: ["Iron", "Vitamin D"])
    interventions_to_compare: Optional[List[str]] = None


class ComparisonMetricItem(BaseModel):
    intervention_name: str
    intervention_type: str # FOOD_ONLY, FOOD_PLUS_SUPPLEMENT, LIFESTYLE_FIRST
    unified_score: float
    estimated_recovery_days: int
    weekly_cost_usd: float
    burden_rating: str # LOW, MODERATE, HIGH
    adherence_probability: float
    pros: List[str]
    cons: List[str]


class InterventionComparisonResponse(BaseModel):
    target_deficiencies: List[str]
    recommended_option: str
    comparison_table: List[ComparisonMetricItem]
    clinical_takeaway: str
