"""
Pydantic V2 Schemas: Personalized Nutrition Recommendations
Phase 5: Personalized Nutrition Recommendation Engine

Contracts for:
- Individual food recommendation items with priority ranking and bioavailability
- Synergistic nutrient-food pairings and antinutrient warnings
- Evidence-based lifestyle intervention items (sunlight, activity, hydration, sleep)
- 7-Day, 14-Day, and 30-Day structured nutrient recovery plans
- Multi-dimensional recommendation scoring (Relevance, Coverage, Compatibility)
- Standardized FastAPI API response payloads
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime


class DietaryPreferenceEnum(str, Enum):
    OMNIVORE = "OMNIVORE"
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    DAIRY_FREE = "DAIRY_FREE"
    GLUTEN_FREE = "GLUTEN_FREE"


class FoodPriorityTierEnum(str, Enum):
    PRIORITY_1 = "PRIORITY_1"  # Powerhouse staple (>85 score)
    PRIORITY_2 = "PRIORITY_2"  # Core supportive food (70-85 score)
    PRIORITY_3 = "PRIORITY_3"  # Complementary rotation (50-70 score)


class FoodItemDetail(BaseModel):
    food_name: str = Field(..., description="Common culinary name of recommended food")
    food_group: str = Field(..., description="E.g., LEGUMES, LEAFY_GREENS, NUTS_SEEDS, SEAFOOD, POULTRY")
    target_nutrient: str = Field(..., description="Primary nutrient addressed (e.g. Iron, Vitamin D)")
    serving_size: str = Field(..., description="Standard clinical serving size (e.g. '1 cup cooked', '100g')")
    nutrient_density: float = Field(..., description="Estimated concentration of target nutrient per serving")
    unit: str = Field(..., description="'mg', 'mcg', 'IU', 'g'")
    bioavailability_rating: float = Field(..., ge=0.0, le=1.0, description="Fractional absorption index")
    dietary_compatibility: List[str] = Field(default_factory=list, description="Compatible diets (Vegan, Gluten-Free, etc.)")
    priority_tier: FoodPriorityTierEnum = Field(..., description="Priority tier based on severity and density")
    recommendation_score: float = Field(..., ge=0.0, le=100.0, description="Composite ranking score (0-100)")
    rationale: str = Field(..., description="Clinical mechanism why this food is recommended")
    preparation_tips: Optional[str] = Field(None, description="Culinary instructions to enhance bioavailability")
    contraindications: Optional[str] = Field(None, description="Precautions (e.g. oxalates, medications, allergies)")

    model_config = ConfigDict(from_attributes=True)


class SynergyPairingItem(BaseModel):
    primary_nutrient: str
    synergistic_nutrient: str
    primary_food: str
    enhancer_food: str
    meal_concept: str = Field(..., description="Practical culinary combination for optimal absorption")
    biochemical_mechanism: str = Field(..., description="Physiological explanation of synergistic absorption")
    absorption_boost_factor: Optional[str] = Field(None, description="Estimated absorption increase (e.g. '3-4x')")
    cautionary_timing: Optional[str] = Field(None, description="Inhibitory timing warning (e.g. 'Avoid tea within 1h')")


class LifestyleInterventionItem(BaseModel):
    category: str = Field(..., description="SUNLIGHT, PHYSICAL_ACTIVITY, HYDRATION, SLEEP, STRESS")
    recommendation: str = Field(..., description="Core actionable instruction")
    daily_target: str = Field(..., description="Measurable metric (e.g. '20-30 min/day', '2.5 liters')")
    clinical_rationale: str = Field(..., description="Why this intervention aids nutrient status")
    evidence_reference: Optional[str] = Field(None, description="Medical guideline reference")


class RecoveryMilestone(BaseModel):
    day_range: str = Field(..., description="'Days 1-7', 'Days 8-14', 'Days 15-30'")
    phase_title: str = Field(..., description="Phase clinical objective")
    clinical_focus: str
    primary_dietary_strategy: str
    daily_action_checklist: List[str] = Field(default_factory=list)
    key_foods_to_emphasize: List[str] = Field(default_factory=list)


class RecoveryPlan(BaseModel):
    plan_title: str
    target_deficiencies: List[str]
    phase_7_day: RecoveryMilestone
    phase_14_day: RecoveryMilestone
    phase_30_day: RecoveryMilestone


class RecommendationScores(BaseModel):
    relevance_score: float = Field(..., ge=0.0, le=100.0, description="Alignment with flagged risk severity")
    nutrient_coverage_score: float = Field(..., ge=0.0, le=100.0, description="Percentage of target RDAs addressed")
    diet_compatibility_score: float = Field(..., ge=0.0, le=100.0, description="Adherence to user dietary restrictions")
    overall_recommendation_score: float = Field(..., ge=0.0, le=100.0, description="Weighted composite score")


class PersonalizedRecommendationsResponse(BaseModel):
    assessment_id: uuid.UUID
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    dietary_pattern_applied: str
    active_restrictions: List[str]
    target_nutrients: List[str]
    scoring_summary: RecommendationScores
    priority_1_foods: List[FoodItemDetail] = Field(default_factory=list)
    priority_2_foods: List[FoodItemDetail] = Field(default_factory=list)
    priority_3_foods: List[FoodItemDetail] = Field(default_factory=list)
    synergistic_pairings: List[SynergyPairingItem] = Field(default_factory=list)
    lifestyle_interventions: List[LifestyleInterventionItem] = Field(default_factory=list)
    supplement_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    monitoring_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    followup_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    recovery_plan: RecoveryPlan
    clinical_summary_note: str
    cdss_disclosure: str = Field(
        default="NutriScan CDSS is an informational clinical decision support tool under FDA Section 520(o)(1)(E) and EU MDR (EU 2017/745). It does not replace independent professional medical judgment, laboratory diagnosis, or customized clinical prescription.",
        description="Statutory FDA 520(o)(1)(E) / CE MDR Clinical Decision Support System disclosure"
    )


class FoodRecommendationsResponse(BaseModel):
    assessment_id: uuid.UUID
    dietary_pattern: str
    total_foods_recommended: int
    priority_1_foods: List[FoodItemDetail] = Field(default_factory=list)
    priority_2_foods: List[FoodItemDetail] = Field(default_factory=list)
    priority_3_foods: List[FoodItemDetail] = Field(default_factory=list)
    foods_by_nutrient: Dict[str, List[FoodItemDetail]] = Field(default_factory=dict)


class LifestyleRecommendationsResponse(BaseModel):
    assessment_id: uuid.UUID
    total_interventions: int
    interventions: List[LifestyleInterventionItem] = Field(default_factory=list)


class RecoveryPlanResponse(BaseModel):
    assessment_id: uuid.UUID
    recovery_plan: RecoveryPlan
