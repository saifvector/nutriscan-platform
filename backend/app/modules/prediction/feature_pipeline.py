"""
ML Feature Extraction Pipeline
Transforms raw 10-field user screening inputs into a standardized,
normalized numerical feature vector suitable for Gradient Boosting (XGBoost/LightGBM)
and SHAP TreeExplainer integration.
"""

from typing import Dict, Any, List
import numpy as np


class NutritionFeaturePipeline:
    """
    Standardizes categorical encodings, imputes missing values, and
    builds dense feature representations for multi-label deficiency prediction.
    """

    DIET_MAP = {
        "OMNIVORE": 0,
        "MEDITERRANEAN": 1,
        "PESCATARIAN": 2,
        "VEGETARIAN": 3,
        "VEGAN": 4,
        "KETO": 5,
        "PALEO": 6,
        "OTHER": 7
    }

    ACTIVITY_MAP = {
        "SEDENTARY": 0,
        "LIGHTLY_ACTIVE": 1,
        "MODERATELY_ACTIVE": 2,
        "VERY_ACTIVE": 3,
        "EXTRA_ACTIVE": 4
    }

    STANDARD_SYMPTOMS = [
        "chronic_fatigue",
        "hair_loss",
        "brittle_nails",
        "cold_hands_feet",
        "brain_fog",
        "muscle_cramps",
        "bone_pain",
        "mouth_ulcers",
        "restless_legs",
        "frequent_infections"
    ]

    @classmethod
    def transform(cls, assessment_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts raw assessment JSON into a structured feature vector dictionary
        ready for ML inference and reproducible SHAP explanation.
        """
        features: Dict[str, float] = {}

        # 1. Physiological Baselines
        features["age"] = float(assessment_dict.get("age", 25))
        features["is_female"] = 1.0 if assessment_dict.get("gender") == "FEMALE" else 0.0
        features["height_cm"] = float(assessment_dict.get("height_cm", 170.0))
        features["weight_kg"] = float(assessment_dict.get("weight_kg", 70.0))
        
        # 2. BMI Calculation
        height_m = features["height_cm"] / 100.0
        features["bmi"] = round(features["weight_kg"] / (height_m * height_m), 1)

        # 3. Dietary Habits
        dietary = assessment_dict.get("dietary_habits", {})
        diet_str = dietary.get("dietary_pattern", "OMNIVORE")
        features["diet_pattern_code"] = float(cls.DIET_MAP.get(diet_str, 0))
        features["is_strict_plant_based"] = 1.0 if diet_str in ["VEGAN", "VEGETARIAN"] else 0.0
        features["meals_per_day"] = float(dietary.get("meals_per_day", 3))
        features["water_intake_liters"] = float(dietary.get("water_intake_liters", 2.0))
        features["fruit_veg_servings"] = float(dietary.get("daily_fruit_vegetable_servings", 2))

        # 4. Lifestyle Factors
        lifestyle = assessment_dict.get("lifestyle_factors", {})
        activity_str = lifestyle.get("activity_level", "SEDENTARY")
        features["activity_level_code"] = float(cls.ACTIVITY_MAP.get(activity_str, 0))
        features["sleep_hours"] = float(lifestyle.get("sleep_hours_per_night", 7.0))
        features["sunlight_minutes"] = float(lifestyle.get("sunlight_exposure_min_per_day", 15))
        features["stress_score"] = float(lifestyle.get("stress_level", 5))
        features["is_smoker"] = 1.0 if lifestyle.get("smoking_status") == "CURRENT" else 0.0
        features["is_heavy_drinker"] = 1.0 if lifestyle.get("alcohol_consumption") == "HEAVY" else 0.0

        # 5. Symptom Severities (0 if unselected, 1-10 if present)
        symptoms_map = assessment_dict.get("symptoms", {})
        for sym in cls.STANDARD_SYMPTOMS:
            features[f"sym_{sym}"] = float(symptoms_map.get(sym, 0.0))

        # 6. Malabsorption Flags from Medical History
        med_history = assessment_dict.get("medical_history", [])
        malabsorption_flag = 0.0
        for item in med_history:
            if isinstance(item, dict) and item.get("impacts_absorption"):
                malabsorption_flag = 1.0
                break
        features["gi_malabsorption_risk"] = malabsorption_flag

        # 7. Supplement Counteracting Factor
        supplements = assessment_dict.get("supplement_usage", [])
        features["active_supplements_count"] = float(len(supplements))

        return features

    @classmethod
    def to_numpy_array(cls, feature_dict: Dict[str, float]) -> np.ndarray:
        """Flattens feature dictionary into an ordered 1D array for scikit-learn/XGBoost."""
        keys = sorted(feature_dict.keys())
        return np.array([feature_dict[k] for k in keys], dtype=np.float32)
