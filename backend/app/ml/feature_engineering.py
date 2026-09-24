"""
Comprehensive Feature Engineering & Data Processing Pipeline
Phase 2: Dataset Engineering and Machine Learning Foundation

Implements:
1. Missing Value Imputation (context-aware median/mode)
2. Outlier Detection & Physiological Clamping
3. BMI Auto-Calculation
4. Symptom Severity Aggregation & Domain Indexing
5. Ordinal Label Encoding
6. Nominal One-Hot Encoding
7. Feature Scaling & Normalization (Fitted strictly on Training Split to prevent data leakage)
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder
from .constants import SYMPTOM_CLUSTERS, PLAUSIBLE_RANGES, SYMPTOM_FIELDS
from .sanitization import safe_float, safe_int, safe_bool, normalize_numeric_feature


class ClinicalFeaturePipeline(BaseEstimator, TransformerMixin):
    """
    Production-grade Feature Engineering Pipeline.
    Guarantees strict separation between fitting and transforming to prevent data leakage.
    Preserves exact column mappings for SHAP Explainability.
    """

    ORDINAL_ACTIVITY = {
        "SEDENTARY": 0,
        "LIGHTLY_ACTIVE": 1,
        "MODERATELY_ACTIVE": 2,
        "VERY_ACTIVE": 3
    }

    ORDINAL_SMOKING = {
        "NEVER": 0,
        "NONE": 0,
        "FORMER": 1,
        "CURRENT": 2,
        "DAILY": 2,
        "CURRENT_DAILY": 2,
        "REGULAR": 2,
        "YES": 2
    }

    ORDINAL_ALCOHOL = {
        "NONE": 0,
        "NEVER": 0,
        "OCCASIONAL": 1,
        "MODERATE": 2,
        "HEAVY": 3,
        "DAILY": 3,
        "FREQUENT": 3
    }

    NOMINAL_DIETS = ["OMNIVORE", "VEGAN", "VEGETARIAN", "PESCATARIAN", "KETO", "MEDITERRANEAN", "OTHER"]

    def __init__(self, scaler_type: str = "robust"):
        self.scaler_type = scaler_type
        self.scaler = RobustScaler() if scaler_type == "robust" else StandardScaler()
        self.is_fitted = False
        
        # Learned statistics from training set
        self.medians_: Dict[str, float] = {}
        self.modes_: Dict[str, Any] = {}
        self.feature_names_: List[str] = []

    def _impute_and_clamp_outliers(self, df: pd.DataFrame, is_fitting: bool = False) -> pd.DataFrame:
        """
        Handles missing values and clamps extreme outliers using clinically plausible biological bounds.
        Ensures all expected columns exist with sensible defaults to support partial payloads.
        """
        df_clean = df.copy()

        # 1. Compute or apply medians for continuous physiological features
        continuous_cols = [
            "age", "height_cm", "weight_kg", "meals_per_day",
            "water_intake_liters", "daily_fruit_vegetable_servings",
            "sleep_hours_per_night", "sunlight_exposure_min_per_day",
            "stress_level", "supplement_duration_months"
        ]

        # Sensible clinical defaults for missing continuous columns
        _continuous_defaults = {
            "age": 35.0, "height_cm": 170.0, "weight_kg": 70.0,
            "meals_per_day": 3.0, "water_intake_liters": 2.0,
            "daily_fruit_vegetable_servings": 3.0,
            "sleep_hours_per_night": 7.0, "sunlight_exposure_min_per_day": 30.0,
            "stress_level": 5.0, "supplement_duration_months": 0.0
        }

        # Ensure all continuous columns exist before imputation
        for col in continuous_cols:
            if col not in df_clean.columns:
                df_clean[col] = _continuous_defaults.get(col, 0.0)

        for col in continuous_cols:
            default_val = self.medians_.get(col, _continuous_defaults.get(col, 0.0))
            df_clean[col] = df_clean[col].apply(lambda v: safe_float(v, default=default_val)).astype(float)
            if is_fitting:
                self.medians_[col] = float(df_clean[col].median())
            
            # Apply biological plausibility clamping
            if col in PLAUSIBLE_RANGES:
                min_val, max_val = PLAUSIBLE_RANGES[col]
                df_clean[col] = df_clean[col].clip(lower=float(min_val), upper=float(max_val))

        # 2. Compute or apply modes for categorical features
        cat_cols = ["gender", "dietary_pattern", "activity_level", "smoking_status", "alcohol_consumption"]
        _cat_defaults = {
            "gender": "UNKNOWN", "dietary_pattern": "OMNIVORE",
            "activity_level": "SEDENTARY", "smoking_status": "NEVER",
            "alcohol_consumption": "NONE"
        }
        for col in cat_cols:
            if col not in df_clean.columns:
                df_clean[col] = _cat_defaults.get(col, "UNKNOWN")
            if is_fitting:
                mode_val = df_clean[col].mode()
                self.modes_[col] = mode_val[0] if len(mode_val) > 0 else "UNKNOWN"
            df_clean[col] = df_clean[col].fillna(self.modes_.get(col, _cat_defaults.get(col, "UNKNOWN")))

        # 3. Impute Boolean & Supplement fields
        bool_cols = [
            "has_digestive_disorder", "has_chronic_disease", "has_prior_deficiency",
            "takes_multivitamin", "takes_vitamin_d", "takes_iron", "takes_b12",
            "takes_calcium", "takes_magnesium", "takes_zinc",
            "has_gluten_free", "has_dairy_free", "has_meat_free"
        ]
        for col in bool_cols:
            if col not in df_clean.columns:
                df_clean[col] = 0.0
            else:
                df_clean[col] = df_clean[col].apply(lambda v: 1.0 if safe_bool(v, default=False) else 0.0).astype(float)

        # 4. Impute symptoms (missing symptom = 0 severity)
        for sym in SYMPTOM_FIELDS:
            col = f"symptom_{sym}"
            if col not in df_clean.columns:
                df_clean[col] = 0.0
            else:
                df_clean[col] = df_clean[col].apply(lambda v: safe_float(v, default=0.0, min_val=0.0, max_val=10.0)).astype(float)

        return df_clean

    def _engineer_features(self, df_clean: pd.DataFrame) -> pd.DataFrame:
        """
        Generates domain-specific features:
        - BMI auto-calculation and classification
        - Aggregate symptom severity indices
        - Nutritional risk indicator flags
        """
        df_feat = pd.DataFrame(index=df_clean.index)

        # --- A. Demographics & BMI Auto Calculation ---
        df_feat["age"] = df_clean["age"]
        df_feat["is_female"] = (df_clean["gender"] == "FEMALE").astype(float)
        df_feat["height_cm"] = df_clean["height_cm"]
        df_feat["weight_kg"] = df_clean["weight_kg"]
        
        # BMI Calculation
        height_m = df_clean["height_cm"] / 100.0
        bmi_computed = df_clean["weight_kg"] / (height_m * height_m)
        df_feat["bmi"] = bmi_computed.clip(10.0, 70.0)
        
        # BMI categories (Non-linear risk flags)
        df_feat["is_underweight"] = (df_feat["bmi"] < 18.5).astype(float)
        df_feat["is_obese"] = (df_feat["bmi"] >= 30.0).astype(float) # Adipose sequestration of fat-soluble vitamins

        # --- B. Dietary Habits & Restriction Encodings ---
        # One-Hot Encoding for Dietary Pattern
        for diet in self.NOMINAL_DIETS:
            df_feat[f"diet_{diet.lower()}"] = (df_clean["dietary_pattern"] == diet).astype(float)
        
        df_feat["meals_per_day"] = df_clean["meals_per_day"]
        df_feat["water_intake_liters"] = df_clean["water_intake_liters"]
        df_feat["fruit_veg_servings"] = df_clean["daily_fruit_vegetable_servings"]
        df_feat["is_low_produce"] = (df_feat["fruit_veg_servings"] <= 1.0).astype(float) # Vit C & Folate risk flag
        
        # Food restrictions
        df_feat["has_gluten_free"] = df_clean.get("has_gluten_free", 0.0)
        df_feat["has_dairy_free"] = df_clean.get("has_dairy_free", 0.0)
        df_feat["has_meat_free"] = df_clean.get("has_meat_free", 0.0)

        # --- C. Lifestyle Factors & Ordinal Encodings ---
        df_feat["activity_level_code"] = df_clean["activity_level"].map(
            lambda x: self.ORDINAL_ACTIVITY.get(str(x).strip().upper(), 1)
        ).astype(float)
        df_feat["sleep_hours"] = df_clean["sleep_hours_per_night"]
        df_feat["sunlight_minutes"] = df_clean["sunlight_exposure_min_per_day"]
        df_feat["is_low_sunlight"] = (df_feat["sunlight_minutes"] < 20.0).astype(float) # Vit D risk flag
        df_feat["stress_level"] = df_clean["stress_level"]
        df_feat["smoking_code"] = df_clean["smoking_status"].map(
            lambda x: self.ORDINAL_SMOKING.get(str(x).strip().upper(), 0)
        ).astype(float)
        df_feat["alcohol_code"] = df_clean["alcohol_consumption"].map(
            lambda x: self.ORDINAL_ALCOHOL.get(str(x).strip().upper(), 0)
        ).astype(float)

        # --- D. Medical History & Malabsorption ---
        df_feat["has_digestive_disorder"] = df_clean["has_digestive_disorder"] if "has_digestive_disorder" in df_clean.columns else 0.0
        df_feat["has_chronic_disease"] = df_clean["has_chronic_disease"] if "has_chronic_disease" in df_clean.columns else 0.0
        df_feat["has_prior_deficiency"] = df_clean["has_prior_deficiency"] if "has_prior_deficiency" in df_clean.columns else 0.0

        # --- E. Supplement Usage ---
        supplement_flags = [
            "takes_multivitamin", "takes_vitamin_d", "takes_iron", "takes_b12",
            "takes_calcium", "takes_magnesium", "takes_zinc"
        ]
        for s_flag in supplement_flags:
            df_feat[s_flag] = df_clean[s_flag] if s_flag in df_clean.columns else 0.0
        df_feat["supplement_duration_months"] = df_clean["supplement_duration_months"] if "supplement_duration_months" in df_clean.columns else 0.0
        df_feat["active_supplements_count"] = df_feat[supplement_flags].sum(axis=1)

        # --- F. Symptom Severities & Composite Aggregations ---
        symptom_cols_present = []
        for sym in SYMPTOM_FIELDS:
            col = f"symptom_{sym}"
            if col in df_clean.columns:
                df_feat[col] = df_clean[col]
                symptom_cols_present.append(col)
            else:
                df_feat[col] = 0.0
                symptom_cols_present.append(col)

        # Total Symptom Burden Score (Sum of all reported symptom severities)
        df_feat["total_symptom_burden"] = df_feat[symptom_cols_present].sum(axis=1)

        # Domain Cluster Aggregations (Averages across physiological clusters)
        for cluster_name, sym_list in SYMPTOM_CLUSTERS.items():
            cluster_cols = [f"symptom_{s}" for s in sym_list if f"symptom_{s}" in df_feat.columns]
            if cluster_cols:
                df_feat[f"cluster_{cluster_name}_index"] = df_feat[cluster_cols].mean(axis=1)
            else:
                df_feat[f"cluster_{cluster_name}_index"] = 0.0

        return df_feat

    def fit(self, X: pd.DataFrame, y=None):
        """
        Fits imputers, encodings, and scalers strictly on training data.
        """
        df_clean = self._impute_and_clamp_outliers(X, is_fitting=True)
        df_features = self._engineer_features(df_clean)
        
        self.feature_names_ = list(df_features.columns)
        self.scaler.fit(df_features.values)
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms screening inputs into scaled, normalized feature matrix.
        """
        if not self.is_fitted:
            raise RuntimeError("ClinicalFeaturePipeline must be fitted on training data before transform.")
            
        df_clean = self._impute_and_clamp_outliers(X, is_fitting=False)
        df_features = self._engineer_features(df_clean)
        
        # Ensure identical column alignment
        df_features = df_features.reindex(columns=self.feature_names_, fill_value=0.0)
        
        scaled_vals = self.scaler.transform(df_features.values)
        scaled_df = pd.DataFrame(scaled_vals, columns=self.feature_names_, index=df_features.index)
        return scaled_df

    def transform_single(self, record_dict: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Helper for single patient assessment inference.
        Returns both the scaled feature DataFrame and the unscaled raw feature dictionary for SHAP.
        """
        # Unpack nested dictionary if needed
        flat = dict(record_dict)

        if "dietary_habits" in record_dict and isinstance(record_dict["dietary_habits"], dict):
            for k, v in record_dict["dietary_habits"].items():
                flat[k] = v
                if k == "dietary_restrictions" and isinstance(v, list):
                    flat["has_gluten_free"] = 1 if any("gluten" in str(x).lower() for x in v) else 0
                    flat["has_dairy_free"] = 1 if any("dairy" in str(x).lower() for x in v) else 0
                    flat["has_meat_free"] = 1 if any("meat" in str(x).lower() for x in v) else 0

        if "lifestyle_factors" in record_dict and isinstance(record_dict["lifestyle_factors"], dict):
            for k, v in record_dict["lifestyle_factors"].items():
                flat[k] = v

        if "symptoms" in record_dict and isinstance(record_dict["symptoms"], dict):
            for k, v in record_dict["symptoms"].items():
                flat[f"symptom_{k}"] = v

        if "food_restrictions" in record_dict and isinstance(record_dict["food_restrictions"], list):
            flat["has_gluten_free"] = 1 if any("gluten" in str(x).lower() for x in record_dict["food_restrictions"]) else 0
            flat["has_dairy_free"] = 1 if any("dairy" in str(x).lower() for x in record_dict["food_restrictions"]) else 0
            flat["has_meat_free"] = 1 if any("meat" in str(x).lower() for x in record_dict["food_restrictions"]) else 0

        df_single = pd.DataFrame([flat])
        df_clean = self._impute_and_clamp_outliers(df_single, is_fitting=False)
        df_unscaled = self._engineer_features(df_clean).reindex(columns=self.feature_names_, fill_value=0.0)
        
        scaled_vals = self.scaler.transform(df_unscaled.values)
        df_scaled = pd.DataFrame(scaled_vals, columns=self.feature_names_)
        
        unscaled_dict = df_unscaled.iloc[0].to_dict()
        return df_scaled, unscaled_dict
