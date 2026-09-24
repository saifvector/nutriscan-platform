"""
Phase 10C Clinical Feature Preprocessor.
Transforms raw patient assessment inputs into the exact 105-column NHANES feature space
required by the Phase 10B champion clinical models.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

# Load approved feature names and median defaults from feature dictionary
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
FEATURE_DICT_PATH = os.path.join(BASE_DIR, "data", "feature_dictionary.csv")

if os.path.exists(FEATURE_DICT_PATH):
    _feat_df = pd.read_csv(FEATURE_DICT_PATH)
    APPROVED_FEATURES = _feat_df['feature_name'].tolist()
    FEATURE_DEFAULTS = dict(zip(_feat_df['feature_name'], _feat_df['mean_value']))
else:
    APPROVED_FEATURES = []
    FEATURE_DEFAULTS = {}

# Adult Dietary Reference Intakes (RDAs) for NAR (Nutrient Adequacy Ratio) calculation
RDA_STANDARDS = {
    'iron': 18.0,         # mg (female baseline / safe reference)
    'calcium': 1000.0,    # mg
    'magnesium': 400.0,   # mg
    'zinc': 11.0,         # mg
    'copper': 0.9,        # mg
    'sodium': 2300.0,     # mg (UL/target)
    'potassium': 3400.0,  # mg
    'selenium': 55.0,     # mcg
    'vitamin_a': 900.0,   # mcg RAE
    'thiamin': 1.2,       # mg
    'riboflavin': 1.3,    # mg
    'niacin': 16.0,       # mg
    'vitamin_b6': 1.7,    # mg
    'folate': 400.0,      # mcg DFE
    'vitamin_b12': 2.4,   # mcg
    'vitamin_c': 90.0,    # mg
    'vitamin_d': 15.0,    # mcg
    'vitamin_e': 15.0,    # mg
    'vitamin_k': 120.0,   # mcg
    'choline': 550.0      # mg
}


class ClinicalFeaturePreprocessor:
    """
    Production preprocessor mapping patient questionnaire inputs into the
    canonical 105-feature vector used by Phase 10B champion models.
    """
    EXPECTED_COLUMNS = APPROVED_FEATURES

    @classmethod
    def transform_single(cls, raw_payload: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Transforms a single patient intake dictionary into a 1-row DataFrame of 105 features.
        Returns:
            (df_features, audit_meta)
        """
        feats = dict(FEATURE_DEFAULTS)
        observed_count = 0

        def set_feat(name: str, val: Any):
            nonlocal observed_count
            if name in feats and val is not None:
                try:
                    fval = float(val)
                    if not np.isnan(fval):
                        feats[name] = fval
                        observed_count += 1
                except (ValueError, TypeError):
                    pass

        # 1. Direct pass-through if exact feature names already supplied
        for k, v in raw_payload.items():
            if k in feats:
                set_feat(k, v)

        # 2. Physiological & Demographic Baselines
        age = raw_payload.get('age', raw_payload.get('demo_age_years'))
        if age is not None:
            set_feat('demo_age_years', age)

        gender = str(raw_payload.get('gender', '')).upper()
        if gender:
            set_feat('demo_is_male', 1.0 if gender in ['MALE', 'M', '1', 'TRUE'] else 0.0)

        height = raw_payload.get('height_cm', raw_payload.get('exam_height_cm'))
        weight = raw_payload.get('weight_kg', raw_payload.get('exam_weight_kg'))
        if height is not None:
            set_feat('exam_height_cm', height)
        if weight is not None:
            set_feat('exam_weight_kg', weight)

        # Calculate BMI & Waist-to-Height Ratio
        if height and weight:
            try:
                h_m = float(height) / 100.0
                bmi = float(weight) / (h_m * h_m)
                set_feat('exam_bmi', round(bmi, 2))
                waist = raw_payload.get('waist_cm', raw_payload.get('exam_waist_cm'))
                if waist:
                    set_feat('exam_waist_cm', waist)
                    set_feat('exam_waist_height_ratio', round(float(waist) / float(height), 3))
                else:
                    # Anthropometric proxy estimation: waist ~ (BMI * 3.3)
                    est_waist = min(150.0, max(50.0, bmi * 3.3))
                    set_feat('exam_waist_cm', round(est_waist, 1))
                    set_feat('exam_waist_height_ratio', round(est_waist / float(height), 3))
            except Exception:
                pass

        # Vitals
        set_feat('exam_systolic_bp', raw_payload.get('systolic_bp', raw_payload.get('exam_systolic_bp')))
        set_feat('exam_diastolic_bp', raw_payload.get('diastolic_bp', raw_payload.get('exam_diastolic_bp')))
        set_feat('exam_pulse_rate', raw_payload.get('pulse_rate', raw_payload.get('exam_pulse_rate', raw_payload.get('heart_rate'))))

        # Demographics details
        set_feat('demo_race_ethnicity', raw_payload.get('race_ethnicity', raw_payload.get('demo_race_ethnicity')))
        set_feat('demo_education_level', raw_payload.get('education_level', raw_payload.get('demo_education_level')))
        set_feat('demo_poverty_ratio', raw_payload.get('poverty_ratio', raw_payload.get('demo_poverty_ratio')))
        set_feat('demo_household_size', raw_payload.get('household_size', raw_payload.get('demo_household_size')))
        set_feat('demo_is_pregnant', 1.0 if raw_payload.get('is_pregnant') else 0.0)

        # 3. Dietary Habits & Nutrient Intakes
        diet_habits = raw_payload.get('dietary_habits', {})
        if isinstance(diet_habits, dict):
            diet_pattern = str(diet_habits.get('dietary_pattern', '')).upper()
            if diet_pattern:
                set_feat('lifestyle_special_diet', 1.0 if diet_pattern in ['VEGAN', 'VEGETARIAN', 'KETO', 'PALEO'] else 0.0)
            if 'meals_per_day' in diet_habits:
                set_feat('lifestyle_main_meal_planner', 1.0)
            if 'water_intake_liters' in diet_habits:
                set_feat('diet_water_moisture_g', float(diet_habits['water_intake_liters']) * 1000.0)

        # Direct dietary recall nutrients if present
        for nut_key, rda in RDA_STANDARDS.items():
            diet_col = f"diet_{nut_key}_mg" if nut_key not in ['selenium', 'vitamin_a', 'folate', 'vitamin_b12', 'vitamin_d', 'vitamin_k'] else f"diet_{nut_key}_mcg"
            if diet_col not in feats and f"diet_{nut_key}_dfe_mcg" in feats:
                diet_col = f"diet_{nut_key}_dfe_mcg"

            val = raw_payload.get(diet_col, raw_payload.get(f"diet_{nut_key}", diet_habits.get(f"diet_{nut_key}")))
            if val is not None:
                set_feat(diet_col, val)

            # Check for supplement intakes
            supp_col = f"supp_{nut_key}_mg" if nut_key not in ['selenium', 'vitamin_d', 'vitamin_b12'] else f"supp_{nut_key}_mcg"
            supp_val = raw_payload.get(supp_col, raw_payload.get(f"supp_{nut_key}"))
            if supp_val is not None:
                set_feat(supp_col, supp_val)

            # Compute total and NAR
            tot_col = f"total_{nut_key}_intake_mg" if nut_key not in ['selenium', 'vitamin_a', 'folate', 'vitamin_b12', 'vitamin_d', 'vitamin_k'] else f"total_{nut_key}_intake_mcg"
            tot_val = (float(feats.get(diet_col, 0.0)) + float(feats.get(supp_col, 0.0)))
            set_feat(tot_col, tot_val)

            nar_col = f"nar_{nut_key}"
            if nar_col in feats:
                set_feat(nar_col, round(min(1.0, tot_val / rda), 3))

        # Check supplement usage list
        supp_usage = raw_payload.get('supplement_usage', [])
        if isinstance(supp_usage, list) and len(supp_usage) > 0:
            for item in supp_usage:
                text = str(item).lower()
                if 'iron' in text:
                    set_feat('supp_iron_mg', 30.0)
                if 'vitamin d' in text or 'd3' in text:
                    set_feat('supp_vitamin_d_mcg', 25.0)
                if 'calcium' in text:
                    set_feat('supp_calcium_mg', 500.0)
                if 'magnesium' in text:
                    set_feat('supp_magnesium_mg', 200.0)
                if 'folate' in text or 'folic' in text or 'b9' in text:
                    set_feat('supp_folic_acid_mcg', 400.0)
                if 'b12' in text:
                    set_feat('supp_vitamin_b12_mcg', 100.0)

        # 4. Lifestyle Factors
        lifestyle = raw_payload.get('lifestyle_factors', {})
        if isinstance(lifestyle, dict):
            activity = str(lifestyle.get('activity_level', '')).upper()
            if activity == 'SEDENTARY':
                set_feat('lifestyle_sedentary_minutes_per_day', 480.0)
                set_feat('lifestyle_moderate_activity_minutes', 0.0)
            elif activity in ['LIGHTLY_ACTIVE', 'MODERATELY_ACTIVE']:
                set_feat('lifestyle_moderate_activity_minutes', 30.0)
                set_feat('lifestyle_sedentary_minutes_per_day', 300.0)
            elif activity in ['VERY_ACTIVE', 'EXTRA_ACTIVE']:
                set_feat('lifestyle_vigorous_activity_minutes', 45.0)
                set_feat('lifestyle_moderate_activity_minutes', 60.0)

            sleep_h = lifestyle.get('sleep_hours_per_night')
            if sleep_h is not None:
                try:
                    sh = float(sleep_h)
                    set_feat('symptom_short_sleep', 1.0 if sh < 6.0 else 0.0)
                except (ValueError, TypeError):
                    pass

            alcohol = str(lifestyle.get('alcohol_consumption', '')).upper()
            if alcohol in ['MODERATE', 'HEAVY']:
                set_feat('diet_alcohol_g', 28.0 if alcohol == 'HEAVY' else 14.0)

        # 5. Symptoms
        symptoms = raw_payload.get('symptoms', {})
        if isinstance(symptoms, dict):
            for sym_name, sev in symptoms.items():
                sname = str(sym_name).lower()
                try:
                    sval = float(sev) if sev is not None else 0.0
                except (ValueError, TypeError):
                    sval = 0.0
                if 'fatigue' in sname:
                    set_feat('symptom_poor_appetite', 1.0 if sval > 5 else 0.0)
                if 'sleep' in sname or 'insomnia' in sname:
                    set_feat('symptom_sleep_trouble', 1.0 if sval > 4 else 0.0)
                    set_feat('symptom_sleep_variability', sval)
                if 'pale' in sname or 'anemia' in sname or 'cramp' in sname:
                    set_feat('history_anemia', 1.0)

        # 6. Medical History
        history = raw_payload.get('medical_history', [])
        if isinstance(history, list):
            for h in history:
                htext = str(h).lower()
                if 'anemia' in htext:
                    set_feat('history_anemia', 1.0)
                if 'hypertension' in htext or 'blood pressure' in htext:
                    set_feat('history_hypertension', 1.0)
                if 'diabetes' in htext:
                    set_feat('history_diabetes', 1.0)
                if 'arthritis' in htext or 'joint' in htext:
                    set_feat('history_arthritis', 1.0)

        # Assemble final ordered DataFrame
        row_dict = {f: np.float32(feats[f]) for f in APPROVED_FEATURES}
        df_out = pd.DataFrame([row_dict], columns=APPROVED_FEATURES, dtype=np.float32)

        completeness_pct = round((observed_count / len(APPROVED_FEATURES)) * 100.0, 1)
        audit_meta = {
            'total_features': len(APPROVED_FEATURES),
            'observed_count': observed_count,
            'defaulted_count': len(APPROVED_FEATURES) - observed_count,
            'completeness_pct': completeness_pct
        }

        return df_out, audit_meta

    @classmethod
    def transform_batch(cls, raw_list: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """Transforms a batch of patient intake dictionaries into a multi-row DataFrame."""
        dfs = []
        metas = []
        for item in raw_list:
            df_i, meta_i = cls.transform_single(item)
            dfs.append(df_i)
            metas.append(meta_i)
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)[APPROVED_FEATURES].astype(np.float32)
        else:
            combined_df = pd.DataFrame(columns=APPROVED_FEATURES, dtype=np.float32)
        return combined_df, metas
