"""
Assessment Schemas: User Input Data Contracts
Covers all 10 core clinical input fields:
1. Age
2. Gender
3. Height
4. Weight
5. BMI (Auto-calculated/validated)
6. Dietary Habits
7. Lifestyle Factors
8. Symptoms
9. Medical History
10. Supplement Usage
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import uuid
from datetime import datetime


class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class DietPatternEnum(str, Enum):
    OMNIVORE = "OMNIVORE"
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    PESCATARIAN = "PESCATARIAN"
    KETO = "KETO"
    PALEO = "PALEO"
    MEDITERRANEAN = "MEDITERRANEAN"
    OTHER = "OTHER"


class ActivityLevelEnum(str, Enum):
    SEDENTARY = "SEDENTARY"
    LIGHTLY_ACTIVE = "LIGHTLY_ACTIVE"
    MODERATELY_ACTIVE = "MODERATELY_ACTIVE"
    VERY_ACTIVE = "VERY_ACTIVE"
    EXTRA_ACTIVE = "EXTRA_ACTIVE"


# --- Sub-models for structured fields ---

class DietaryHabits(BaseModel):
    dietary_pattern: DietPatternEnum = Field(..., description="Primary dietary pattern")
    meals_per_day: int = Field(..., ge=1, le=8, description="Average number of meals daily")
    water_intake_liters: float = Field(..., ge=0.0, le=10.0, description="Daily water intake in liters")
    daily_fruit_vegetable_servings: int = Field(default=2, ge=0, description="Servings of fruits/veggies per day")
    junk_food_frequency: str = Field(default="RARELY", description="Frequency of ultra-processed food consumption")
    dietary_restrictions: List[str] = Field(default_factory=list, description="Allergies or exclusions (e.g. dairy-free, gluten-free)")


class LifestyleFactors(BaseModel):
    activity_level: ActivityLevelEnum = Field(..., description="Weekly physical activity baseline")
    sleep_hours_per_night: float = Field(..., ge=0.0, le=24.0, description="Average sleep per night")
    smoking_status: str = Field(..., description="'NEVER', 'FORMER', or 'CURRENT'")
    alcohol_consumption: str = Field(..., description="'NONE', 'OCCASIONAL', 'MODERATE', or 'HEAVY'")
    sunlight_exposure_min_per_day: int = Field(default=15, ge=0, description="Direct sunlight exposure per day in minutes")
    stress_level: int = Field(..., ge=1, le=10, description="Perceived subjective stress on a 1-10 scale")


class SymptomItem(BaseModel):
    symptom_code: str = Field(..., description="Unique key, e.g. 'fatigue', 'hair_loss', 'brittle_nails'")
    severity: int = Field(..., ge=1, le=10, description="Severity rating 1 (mild) to 10 (debilitating)")
    duration_weeks: Optional[int] = Field(default=4, description="How many weeks symptom has persisted")


class MedicalHistoryItem(BaseModel):
    condition_name: str = Field(..., description="Condition name, e.g. 'Celiac Disease', 'Gastric Bypass', 'Hypothyroidism'")
    diagnosed_year: Optional[int] = None
    is_active: bool = True
    impacts_absorption: bool = False


class SupplementUsageItem(BaseModel):
    supplement_name: str = Field(..., description="E.g., 'Multivitamin', 'Vitamin D3 2000IU', 'Iron Bisglycinate'")
    dosage: str = Field(..., description="E.g., '50mcg', '20mg'")
    frequency: str = Field(..., description="E.g., 'DAILY', 'WEEKLY', 'AS_NEEDED'")


# --- Primary Assessment Request Payload ---

class HealthAssessmentCreate(BaseModel):
    """
    Primary DTO submitted by users during screening.
    Directly addresses all clinical input fields.
    """
    # Patient Identification
    patient_name: Optional[str] = Field(default=None, description="Patient full name or identifier")
    patient_id: Optional[str] = Field(default=None, description="Existing patient unique identifier")

    # 1. Age
    age: int = Field(..., ge=1, le=125, description="Age in completed years")
    
    # 2. Gender
    gender: GenderEnum = Field(..., description="Biological sex for baseline physiological ranges")
    
    # 3. Height
    height_cm: float = Field(..., ge=40.0, le=260.0, description="Height in centimeters")
    
    # 4. Weight
    weight_kg: float = Field(..., ge=20.0, le=350.0, description="Weight in kilograms")
    
    # 5. BMI (Optional in request because backend can auto-calculate, but accepted if pre-computed)
    bmi: Optional[float] = Field(default=None, description="Body Mass Index (auto-calculated if omitted)")

    # 6. Dietary Habits
    dietary_habits: DietaryHabits = Field(..., description="Dietary patterns, intake, and restrictions")

    # 7. Lifestyle Factors
    lifestyle_factors: LifestyleFactors = Field(..., description="Activity, sleep, stress, sun exposure, and substance usage")

    # 8. Symptoms
    symptoms: Dict[str, int] = Field(
        ...,
        description="Key-value mapping of symptom identifier to severity score (1-10). E.g. {'fatigue': 8, 'muscle_cramps': 5}"
    )

    # 9. Medical History
    medical_history: List[MedicalHistoryItem] = Field(
        default_factory=list,
        description="Chronic diseases, prior surgeries, absorption syndromes"
    )

    # 10. Supplement Usage
    supplement_usage: List[SupplementUsageItem] = Field(
        default_factory=list,
        description="Current supplements, vitamins, and minerals consumed"
    )

    # 11. Laboratory Biomarkers (Optional Grounding)
    biomarkers: Optional[Dict[str, float]] = Field(
        default_factory=dict,
        description="Clinical laboratory biomarker values (e.g., serum_ferritin, serum_25ohd, serum_b12)"
    )

    @field_validator("bmi", mode="before")
    def calculate_bmi_if_missing(cls, v, values):
        # Allow automated computation: weight / (height_m ^ 2)
        return v


class HealthAssessmentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    assessment_version: str
    age_at_assessment: int
    gender: GenderEnum
    height_cm: float
    weight_kg: float
    bmi: float
    dietary_pattern: DietPatternEnum
    meals_per_day: int
    water_intake_liters: float
    activity_level: ActivityLevelEnum
    sleep_hours_per_night: float
    symptoms: Dict[str, int]
    medical_history: List[Dict[str, Any]]
    supplement_usage: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Enterprise Assessment Schema Aliases
from .enterprise_assessment import (
    AssessmentRequest,
    Biomarkers,
    Symptoms as EnterpriseSymptoms,
    LifestyleFactors as EnterpriseLifestyleFactors,
    DietaryHabits as EnterpriseDietaryHabits,
    SupplementUsage as EnterpriseSupplementUsage
)
