"""
NutriScan Enterprise Input Validation Framework (Pydantic V2)
============================================================
Provides rigorous type-safe schemas, range boundaries, clinical enum validation,
and missing object recovery for clinical assessment payloads.

Guarantees:
- Safe handling and coercion of malformed/corrupted values
- Missing nested object recovery (auto-initializes defaults if None/omitted)
- Rejection of impossible biological values with HTTP 422
- Zero unhandled crashes on adversarial payloads.
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re
from ..ml.sanitization import safe_float, safe_int, safe_bool


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
    LOW_FODMAP = "LOW_FODMAP"
    OTHER = "OTHER"


class ActivityLevelEnum(str, Enum):
    SEDENTARY = "SEDENTARY"
    LIGHTLY_ACTIVE = "LIGHTLY_ACTIVE"
    MODERATELY_ACTIVE = "MODERATELY_ACTIVE"
    VERY_ACTIVE = "VERY_ACTIVE"
    EXTRA_ACTIVE = "EXTRA_ACTIVE"


class SmokingStatusEnum(str, Enum):
    NEVER = "NEVER"
    FORMER = "FORMER"
    CURRENT = "CURRENT"


class AlcoholConsumptionEnum(str, Enum):
    NONE = "NONE"
    OCCASIONAL = "OCCASIONAL"
    MODERATE = "MODERATE"
    HEAVY = "HEAVY"


class Biomarkers(BaseModel):
    """Clinical laboratory biomarker values with physiological boundaries."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    serum_ferritin: Optional[float] = Field(default=None, ge=0.0, le=5000.0)
    serum_25ohd: Optional[float] = Field(default=None, ge=0.0, le=500.0)
    serum_b12: Optional[float] = Field(default=None, ge=0.0, le=10000.0)
    serum_calcium: Optional[float] = Field(default=None, ge=0.0, le=25.0)
    serum_magnesium: Optional[float] = Field(default=None, ge=0.0, le=15.0)
    serum_potassium: Optional[float] = Field(default=None, ge=0.0, le=15.0)
    serum_zinc: Optional[float] = Field(default=None, ge=0.0, le=500.0)
    rbc_folate: Optional[float] = Field(default=None, ge=0.0, le=3000.0)
    serum_folate: Optional[float] = Field(default=None, ge=0.0, le=200.0)
    hemoglobin: Optional[float] = Field(default=None, ge=0.0, le=30.0)
    serum_albumin: Optional[float] = Field(default=None, ge=0.0, le=10.0)

    @model_validator(mode="before")
    @classmethod
    def sanitize_biomarkers(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return {}
        sanitized = {}
        for k, v in data.items():
            f_val = safe_float(v, default=None)
            # Enforce non-negative biological constraint
            if f_val is not None:
                if f_val < 0.0:
                    raise ValueError(f"Biomarker '{k}' cannot be negative ({f_val}).")
                sanitized[k] = f_val
        return sanitized


class Symptoms(BaseModel):
    """Subjective symptom ratings (0 to 10 scale) with missing recovery."""
    model_config = ConfigDict(extra="ignore")

    fatigue: float = Field(default=0.0, ge=0.0, le=10.0)
    hair_loss: float = Field(default=0.0, ge=0.0, le=10.0)
    muscle_weakness: float = Field(default=0.0, ge=0.0, le=10.0)
    bone_pain: float = Field(default=0.0, ge=0.0, le=10.0)
    pale_skin: float = Field(default=0.0, ge=0.0, le=10.0)
    brittle_nails: float = Field(default=0.0, ge=0.0, le=10.0)
    brain_fog: float = Field(default=0.0, ge=0.0, le=10.0)
    muscle_cramps: float = Field(default=0.0, ge=0.0, le=10.0)
    cold_intolerance: float = Field(default=0.0, ge=0.0, le=10.0)
    frequent_infections: float = Field(default=0.0, ge=0.0, le=10.0)
    mouth_ulcers: float = Field(default=0.0, ge=0.0, le=10.0)
    night_blindness: float = Field(default=0.0, ge=0.0, le=10.0)
    slow_wound_healing: float = Field(default=0.0, ge=0.0, le=10.0)
    tingling_numbness: float = Field(default=0.0, ge=0.0, le=10.0)
    irritability: float = Field(default=0.0, ge=0.0, le=10.0)
    poor_appetite: float = Field(default=0.0, ge=0.0, le=10.0)
    cracked_lips: float = Field(default=0.0, ge=0.0, le=10.0)
    eye_irritation: float = Field(default=0.0, ge=0.0, le=10.0)
    dermatitis: float = Field(default=0.0, ge=0.0, le=10.0)
    digestive_disturbances: float = Field(default=0.0, ge=0.0, le=10.0)
    irregular_heartbeat: float = Field(default=0.0, ge=0.0, le=10.0)
    thyroid_dysfunction: float = Field(default=0.0, ge=0.0, le=10.0)

    @model_validator(mode="before")
    @classmethod
    def sanitize_symptoms(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return {}
        sanitized = {}
        for k, v in data.items():
            f_val = safe_float(v, default=0.0)
            if f_val < 0.0 or f_val > 10.0:
                raise ValueError(f"Symptom severity for '{k}' must be between 0 and 10, got {f_val}")
            sanitized[k] = f_val
        return sanitized


class LifestyleFactors(BaseModel):
    """Activity, sleep, stress, sun exposure, and substance usage."""
    model_config = ConfigDict(extra="ignore")

    activity_level: ActivityLevelEnum = Field(default=ActivityLevelEnum.MODERATELY_ACTIVE)
    sleep_hours_per_night: float = Field(default=7.0, ge=0.0, le=24.0)
    smoking_status: SmokingStatusEnum = Field(default=SmokingStatusEnum.NEVER)
    alcohol_consumption: AlcoholConsumptionEnum = Field(default=AlcoholConsumptionEnum.NONE)
    sunlight_exposure_min_per_day: float = Field(default=20.0, ge=0.0, le=720.0)
    stress_level: int = Field(default=4, ge=1, le=10)

    @model_validator(mode="before")
    @classmethod
    def coerce_lifestyle(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return {}
        res = dict(data)
        if "sleep_hours_per_night" in res:
            res["sleep_hours_per_night"] = safe_float(res["sleep_hours_per_night"], default=7.0)
        if "stress_level" in res:
            res["stress_level"] = safe_int(res["stress_level"], default=4)
        if "sunlight_exposure_min_per_day" in res:
            res["sunlight_exposure_min_per_day"] = safe_float(res["sunlight_exposure_min_per_day"], default=20.0)
        return res


class DietaryHabits(BaseModel):
    """Dietary patterns, meal frequency, hydration, and restrictions."""
    model_config = ConfigDict(extra="ignore")

    dietary_pattern: DietPatternEnum = Field(default=DietPatternEnum.OMNIVORE)
    meals_per_day: float = Field(default=3.0, ge=1.0, le=10.0)
    water_intake_liters: float = Field(default=2.0, ge=0.0, le=15.0)
    daily_fruit_vegetable_servings: float = Field(default=3.0, ge=0.0, le=30.0)
    junk_food_frequency: str = Field(default="RARELY")
    dietary_restrictions: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def coerce_dietary(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return {}
        res = dict(data)
        if "meals_per_day" in res:
            res["meals_per_day"] = safe_float(res["meals_per_day"], default=3.0)
        if "water_intake_liters" in res:
            res["water_intake_liters"] = safe_float(res["water_intake_liters"], default=2.0)
        if "daily_fruit_vegetable_servings" in res:
            res["daily_fruit_vegetable_servings"] = safe_float(res["daily_fruit_vegetable_servings"], default=3.0)
        return res


class SupplementItem(BaseModel):
    supplement_name: str = Field(..., min_length=1)
    dosage: Optional[str] = Field(default="Standard")
    frequency: Optional[str] = Field(default="DAILY")


class SupplementUsage(BaseModel):
    supplements: List[SupplementItem] = Field(default_factory=list)


class AssessmentRequest(BaseModel):
    """
    Enterprise Patient Assessment Request Schema.
    Features automatic coercion, range verification, and missing object recovery.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    age: int = Field(..., ge=1, le=125, description="Patient age in completed years")
    gender: GenderEnum = Field(default=GenderEnum.OTHER)
    height_cm: float = Field(..., ge=40.0, le=260.0, description="Height in centimeters")
    weight_kg: float = Field(..., ge=20.0, le=350.0, description="Weight in kilograms")
    bmi: Optional[float] = Field(default=None, ge=10.0, le=90.0)

    # Missing Object Recovery: defaults instantiated if None
    dietary_habits: DietaryHabits = Field(default_factory=DietaryHabits)
    lifestyle_factors: LifestyleFactors = Field(default_factory=LifestyleFactors)
    symptoms: Symptoms = Field(default_factory=Symptoms)
    biomarkers: Optional[Biomarkers] = Field(default_factory=Biomarkers)
    supplement_usage: List[Dict[str, Any]] = Field(default_factory=list)
    medical_history: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def sanitize_assessment(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            raise ValueError("Assessment payload must be a JSON dictionary.")

        res = dict(data)

        # Sanitize age
        if "age" in res:
            res["age"] = safe_int(res["age"], default=-1)
            if res["age"] < 1 or res["age"] > 125:
                raise ValueError(f"Age must be between 1 and 125, got {res['age']}")

        # Sanitize height
        if "height_cm" in res:
            res["height_cm"] = safe_float(res["height_cm"], default=-1.0)
            if res["height_cm"] < 40.0 or res["height_cm"] > 260.0:
                raise ValueError(f"Height must be between 40.0 and 260.0 cm, got {res['height_cm']}")

        # Sanitize weight
        if "weight_kg" in res:
            res["weight_kg"] = safe_float(res["weight_kg"], default=-1.0)
            if res["weight_kg"] < 20.0 or res["weight_kg"] > 350.0:
                raise ValueError(f"Weight must be between 20.0 and 350.0 kg, got {res['weight_kg']}")

        # Auto-compute BMI if omitted
        if res.get("bmi") is None and res.get("height_cm", 0) > 0 and res.get("weight_kg", 0) > 0:
            h_m = res["height_cm"] / 100.0
            res["bmi"] = round(res["weight_kg"] / (h_m * h_m), 1)

        # Missing object recovery
        if res.get("dietary_habits") is None:
            res["dietary_habits"] = {}
        if res.get("lifestyle_factors") is None:
            res["lifestyle_factors"] = {}
        if res.get("symptoms") is None:
            res["symptoms"] = {}
        if res.get("biomarkers") is None:
            res["biomarkers"] = {}

        return res
