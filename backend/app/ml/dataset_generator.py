"""
Clinical Synthetic Dataset Generator for Multi-Nutrient Screening
Generates high-fidelity, epidemiologically grounded nutritional profiles
with realistic physiological and symptom co-occurrences for:
Protein, Vitamin A, Vitamin B12, Folate, Vitamin C, Vitamin D, Vitamin E,
Iron, Calcium, Zinc, Magnesium.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from .constants import TARGET_NUTRIENTS, SYMPTOM_FIELDS, PLAUSIBLE_RANGES


class NutritionalDatasetGenerator:
    """
    Generates synthetic patient records grounded in clinical nutritional epidemiology:
    - Vegans/Vegetarians without supplementation have heightened B12, Iron, Zinc, Protein risk.
    - Low sunlight exposure and indoor lifestyles strongly correlate with Vitamin D risk.
    - Low fruit and vegetable consumption correlates with Vitamin C and Folate risk.
    - Malabsorption syndromes (Celiac, Crohn's, Gastric bypass) elevate fat-soluble (A, D, E) and B12 risk.
    - Chronic alcohol intake depletes Magnesium, Zinc, and Folate.
    - Heavy menstrual blood loss or endurance athletes correlate with Iron deficiency.
    - Elderly individuals have reduced gastric acid, elevating B12 and Calcium risk.
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def generate_patient_record(self) -> Dict[str, Any]:
        rng = self.rng

        # Demographics
        gender = rng.choice(["MALE", "FEMALE"], p=[0.48, 0.52])
        age = int(rng.integers(18, 80))
        
        # Height & Weight
        if gender == "MALE":
            height_cm = float(np.clip(rng.normal(176.0, 7.5), 150.0, 205.0))
            weight_kg = float(np.clip(rng.normal(80.0, 14.0), 45.0, 150.0))
        else:
            height_cm = float(np.clip(rng.normal(163.0, 6.8), 140.0, 195.0))
            weight_kg = float(np.clip(rng.normal(68.0, 13.0), 40.0, 140.0))
        
        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m * height_m), 1)

        # Dietary Habits
        diet_pattern = rng.choice(
            ["OMNIVORE", "VEGAN", "VEGETARIAN", "PESCATARIAN", "KETO", "MEDITERRANEAN"],
            p=[0.55, 0.08, 0.12, 0.07, 0.06, 0.12]
        )
        meals_per_day = int(rng.choice([1, 2, 3, 4, 5], p=[0.05, 0.25, 0.55, 0.12, 0.03]))
        water_intake_liters = float(np.clip(rng.normal(2.1, 0.7), 0.5, 5.0))
        fruit_veg_servings = int(rng.choice([0, 1, 2, 3, 4, 5, 6], p=[0.08, 0.20, 0.32, 0.22, 0.10, 0.05, 0.03]))
        
        food_restrictions = []
        if diet_pattern in ["VEGAN", "VEGETARIAN"]:
            food_restrictions.append("meat_free")
        if diet_pattern == "VEGAN":
            food_restrictions.append("dairy_free")
        if rng.random() < 0.12:
            food_restrictions.append("gluten_free")
        if rng.random() < 0.15:
            food_restrictions.append("lactose_free")

        # Lifestyle Factors
        activity_level = rng.choice(
            ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE"],
            p=[0.35, 0.35, 0.22, 0.08]
        )
        sleep_hours = float(np.clip(rng.normal(6.8, 1.2), 3.5, 10.5))
        sunlight_min = int(np.clip(rng.exponential(20.0), 0, 180))
        stress_level = int(rng.integers(1, 11))
        smoking_status = rng.choice(["NEVER", "FORMER", "CURRENT"], p=[0.65, 0.20, 0.15])
        alcohol_consumption = rng.choice(["NONE", "OCCASIONAL", "MODERATE", "HEAVY"], p=[0.30, 0.45, 0.20, 0.05])

        # Medical History
        has_digestive_disorder = bool(rng.choice([True, False], p=[0.14, 0.86])) # e.g. Celiac, IBD, Gastritis
        has_chronic_disease = bool(rng.choice([True, False], p=[0.18, 0.82]))    # e.g. CKD, Diabetes, Thyroid
        has_prior_deficiency = bool(rng.choice([True, False], p=[0.22, 0.78]))

        # Supplement Usage
        takes_multivitamin = bool(rng.choice([True, False], p=[0.30, 0.70]))
        takes_vitamin_d = bool(rng.choice([True, False], p=[0.25, 0.75]))
        takes_iron = bool(rng.choice([True, False], p=[0.12, 0.88]))
        takes_b12 = bool(rng.choice([True, False], p=[0.15, 0.85]))
        takes_calcium = bool(rng.choice([True, False], p=[0.14, 0.86]))
        takes_magnesium = bool(rng.choice([True, False], p=[0.18, 0.82]))
        takes_zinc = bool(rng.choice([True, False], p=[0.10, 0.90]))
        supplement_duration_months = int(rng.choice([0, 1, 3, 6, 12, 24])) if (
            takes_multivitamin or takes_vitamin_d or takes_iron or takes_b12 or takes_calcium
        ) else 0

        # --- Latent Nutritional Risk Scores Calculation (0.0 - 1.0) ---
        # 1. Protein
        p_protein = 0.15
        if diet_pattern == "VEGAN" and meals_per_day <= 2: p_protein += 0.35
        elif diet_pattern in ["VEGAN", "VEGETARIAN"]: p_protein += 0.20
        if activity_level == "VERY_ACTIVE": p_protein += 0.15
        if bmi < 18.5: p_protein += 0.30
        if has_digestive_disorder: p_protein += 0.20

        # 2. Vitamin A
        p_vit_a = 0.10
        if fruit_veg_servings <= 1: p_vit_a += 0.35
        if has_digestive_disorder: p_vit_a += 0.30
        if takes_multivitamin: p_vit_a -= 0.30

        # 3. Vitamin B12
        p_vit_b12 = 0.12
        if diet_pattern == "VEGAN": p_vit_b12 += 0.65
        elif diet_pattern == "VEGETARIAN": p_vit_b12 += 0.35
        if age > 60: p_vit_b12 += 0.25
        if has_digestive_disorder: p_vit_b12 += 0.35
        if takes_b12 or takes_multivitamin: p_vit_b12 -= 0.60

        # 4. Folate (B9)
        p_folate = 0.15
        if fruit_veg_servings <= 1: p_folate += 0.40
        if alcohol_consumption == "HEAVY": p_folate += 0.35
        if has_digestive_disorder: p_folate += 0.25
        if takes_multivitamin: p_folate -= 0.35

        # 5. Vitamin C
        p_vit_c = 0.12
        if fruit_veg_servings <= 1: p_vit_c += 0.50
        if smoking_status == "CURRENT": p_vit_c += 0.30 # Cigarettes increase turnover by 35mg/day
        if takes_multivitamin: p_vit_c -= 0.40

        # 6. Vitamin D
        p_vit_d = 0.30
        if sunlight_min < 15: p_vit_d += 0.45
        elif sunlight_min < 30: p_vit_d += 0.25
        if bmi > 30.0: p_vit_d += 0.20 # Sequestration in adipose tissue
        if age > 65: p_vit_d += 0.20
        if takes_vitamin_d or takes_multivitamin: p_vit_d -= 0.55

        # 7. Vitamin E
        p_vit_e = 0.10
        if fruit_veg_servings <= 1 and diet_pattern == "KETO": p_vit_e += 0.15
        if has_digestive_disorder: p_vit_e += 0.35
        if takes_multivitamin: p_vit_e -= 0.30

        # 8. Iron
        p_iron = 0.20
        if gender == "FEMALE" and age < 50: p_iron += 0.35 # Menstruation
        if diet_pattern in ["VEGAN", "VEGETARIAN"]: p_iron += 0.25 # Non-heme absorption barrier
        if has_digestive_disorder: p_iron += 0.30
        if p_vit_c > 0.5: p_iron += 0.15 # Lack of Vit C reducing agent
        if takes_iron or takes_multivitamin: p_iron -= 0.45

        # 9. Calcium
        p_calcium = 0.18
        if "dairy_free" in food_restrictions or diet_pattern == "VEGAN": p_calcium += 0.40
        if age > 55: p_calcium += 0.25
        if p_vit_d > 0.5: p_calcium += 0.25 # Impaired calbindin-mediated absorption
        if takes_calcium or takes_multivitamin: p_calcium -= 0.45

        # 10. Zinc
        p_zinc = 0.18
        if diet_pattern in ["VEGAN", "VEGETARIAN"]: p_zinc += 0.35 # High phytates inhibit zinc
        if alcohol_consumption in ["MODERATE", "HEAVY"]: p_zinc += 0.25
        if has_digestive_disorder: p_zinc += 0.25
        if takes_zinc or takes_multivitamin: p_zinc -= 0.40

        # 11. Magnesium
        p_magnesium = 0.22
        if stress_level >= 7: p_magnesium += 0.25 # Catecholamine induced renal wasting
        if alcohol_consumption in ["MODERATE", "HEAVY"]: p_magnesium += 0.30
        if fruit_veg_servings <= 2: p_magnesium += 0.20
        if takes_magnesium or takes_multivitamin: p_magnesium -= 0.45

        # 12. Vitamin B1 (Thiamine)
        p_vit_b1 = 0.12
        if alcohol_consumption in ["MODERATE", "HEAVY"]: p_vit_b1 += 0.42 # Alcohol reduces active transport across brush border
        if diet_pattern == "KETO": p_vit_b1 += 0.18 # Absence of enriched whole grains and legumes
        if has_digestive_disorder: p_vit_b1 += 0.25
        if takes_multivitamin: p_vit_b1 -= 0.35

        # 13. Vitamin B2 (Riboflavin)
        p_vit_b2 = 0.11
        if "dairy_free" in food_restrictions or diet_pattern == "VEGAN": p_vit_b2 += 0.32
        if alcohol_consumption in ["MODERATE", "HEAVY"]: p_vit_b2 += 0.22
        if takes_multivitamin: p_vit_b2 -= 0.35

        # 14. Vitamin B3 (Niacin)
        p_vit_b3 = 0.09
        if diet_pattern in ["VEGAN", "VEGETARIAN"] and fruit_veg_servings <= 2: p_vit_b3 += 0.24
        if alcohol_consumption in ["MODERATE", "HEAVY"]: p_vit_b3 += 0.30
        if takes_multivitamin: p_vit_b3 -= 0.35

        # 15. Vitamin B6 (Pyridoxine)
        p_vit_b6 = 0.14
        if alcohol_consumption in ["MODERATE", "HEAVY"]: p_vit_b6 += 0.30
        if has_digestive_disorder: p_vit_b6 += 0.25
        if stress_level >= 7: p_vit_b6 += 0.18
        if takes_multivitamin: p_vit_b6 -= 0.35

        # 16. Potassium
        p_potassium = 0.24
        if fruit_veg_servings <= 2: p_potassium += 0.40 # Main dietary source is fruits/root vegetables
        if p_magnesium > 0.5: p_potassium += 0.22 # Hypomagnesemia impairs Na+/K+ ATPase, driving renal loss
        if takes_multivitamin: p_potassium -= 0.10

        # 17. Selenium
        p_selenium = 0.12
        if diet_pattern in ["VEGAN", "VEGETARIAN"]: p_selenium += 0.28 # Soil-variable; low in non-seafood/non-egg plant diets
        if smoking_status == "CURRENT": p_selenium += 0.22
        if takes_multivitamin: p_selenium -= 0.35

        # 18. Iodine
        p_iodine = 0.20
        if "dairy_free" in food_restrictions and diet_pattern in ["VEGAN", "VEGETARIAN"]: p_iodine += 0.45
        elif diet_pattern == "VEGAN": p_iodine += 0.38
        if takes_multivitamin: p_iodine -= 0.35

        # Clip all 18 probabilities
        risk_probs = {
            "Protein": np.clip(p_protein + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin A": np.clip(p_vit_a + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin B12": np.clip(p_vit_b12 + rng.normal(0, 0.05), 0.01, 0.99),
            "Folate": np.clip(p_folate + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin C": np.clip(p_vit_c + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin D": np.clip(p_vit_d + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin E": np.clip(p_vit_e + rng.normal(0, 0.05), 0.01, 0.99),
            "Iron": np.clip(p_iron + rng.normal(0, 0.05), 0.01, 0.99),
            "Calcium": np.clip(p_calcium + rng.normal(0, 0.05), 0.01, 0.99),
            "Zinc": np.clip(p_zinc + rng.normal(0, 0.05), 0.01, 0.99),
            "Magnesium": np.clip(p_magnesium + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin B1": np.clip(p_vit_b1 + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin B2": np.clip(p_vit_b2 + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin B3": np.clip(p_vit_b3 + rng.normal(0, 0.05), 0.01, 0.99),
            "Vitamin B6": np.clip(p_vit_b6 + rng.normal(0, 0.05), 0.01, 0.99),
            "Potassium": np.clip(p_potassium + rng.normal(0, 0.05), 0.01, 0.99),
            "Selenium": np.clip(p_selenium + rng.normal(0, 0.05), 0.01, 0.99),
            "Iodine": np.clip(p_iodine + rng.normal(0, 0.05), 0.01, 0.99)
        }

        # Convert latent probabilities to 3 Risk Categories:
        # 0: Low Risk (< 0.38)
        # 1: Moderate Risk (0.38 - 0.68)
        # 2: High Risk (>= 0.68)
        target_classes = {}
        for nut, p in risk_probs.items():
            if p < 0.38:
                target_classes[nut] = 0 # Low Risk
            elif p < 0.68:
                target_classes[nut] = 1 # Moderate Risk
            else:
                target_classes[nut] = 2 # High Risk

        # Generate Symptoms according to actual deficiency status
        symptoms: Dict[str, int] = {}
        
        # Fatigue: Iron, B12, D, Protein, Magnesium, B1
        fatigue_drivers = [risk_probs["Iron"], risk_probs["Vitamin B12"], risk_probs["Vitamin D"], risk_probs["Protein"], risk_probs["Vitamin B1"]]
        max_f = max(fatigue_drivers)
        symptoms["fatigue"] = int(np.clip(round(max_f * 8 + rng.integers(0, 3)), 0, 10))

        # Hair loss: Iron, Zinc, Protein, Selenium
        hair_drivers = [risk_probs["Iron"], risk_probs["Zinc"], risk_probs["Protein"], risk_probs["Selenium"]]
        symptoms["hair_loss"] = int(np.clip(round(max(hair_drivers) * 7.5 + rng.integers(0, 3)), 0, 10))

        # Muscle weakness: Vit D, Magnesium, Protein, Calcium, Potassium
        muscle_w_drivers = [risk_probs["Vitamin D"], risk_probs["Magnesium"], risk_probs["Protein"], risk_probs["Potassium"]]
        symptoms["muscle_weakness"] = int(np.clip(round(max(muscle_w_drivers) * 8 + rng.integers(0, 3)), 0, 10))

        # Bone pain: Vitamin D, Calcium
        bone_drivers = [risk_probs["Vitamin D"], risk_probs["Calcium"]]
        symptoms["bone_pain"] = int(np.clip(round(max(bone_drivers) * 7.5 + rng.integers(0, 3)), 0, 10))

        # Pale skin: Iron, B12, Folate
        pale_drivers = [risk_probs["Iron"], risk_probs["Vitamin B12"], risk_probs["Folate"]]
        symptoms["pale_skin"] = int(np.clip(round(max(pale_drivers) * 8.5 + rng.integers(0, 2)), 0, 10))

        # Brittle nails: Iron, Zinc, Calcium, Selenium
        nail_drivers = [risk_probs["Iron"], risk_probs["Zinc"], risk_probs["Calcium"], risk_probs["Selenium"]]
        symptoms["brittle_nails"] = int(np.clip(round(max(nail_drivers) * 7 + rng.integers(0, 3)), 0, 10))

        # Brain fog: B12, Iron, Vitamin D, Magnesium, B1
        brain_drivers = [risk_probs["Vitamin B12"], risk_probs["Iron"], risk_probs["Vitamin D"], risk_probs["Vitamin B1"]]
        symptoms["brain_fog"] = int(np.clip(round(max(brain_drivers) * 7.5 + rng.integers(0, 3)), 0, 10))

        # Muscle cramps: Magnesium, Calcium, Potassium
        cramp_drivers = [risk_probs["Magnesium"], risk_probs["Calcium"], risk_probs["Potassium"]]
        symptoms["muscle_cramps"] = int(np.clip(round(max(cramp_drivers) * 8.0 + rng.integers(0, 3)), 0, 10))

        # Cold intolerance: Iron, Iodine (hypothyroid thermal dysregulation)
        cold_drivers = [risk_probs["Iron"], risk_probs["Iodine"]]
        symptoms["cold_intolerance"] = int(np.clip(round(max(cold_drivers) * 7.5 + rng.integers(0, 3)), 0, 10))

        # Frequent infections: Vitamin C, Vitamin D, Zinc, Selenium
        immune_drivers = [risk_probs["Vitamin C"], risk_probs["Vitamin D"], risk_probs["Zinc"], risk_probs["Selenium"]]
        symptoms["frequent_infections"] = int(np.clip(round(max(immune_drivers) * 7.0 + rng.integers(0, 3)), 0, 10))

        # Mouth ulcers: Folate, B12, Iron, Zinc, B2
        ulcer_drivers = [risk_probs["Folate"], risk_probs["Vitamin B12"], risk_probs["Zinc"], risk_probs["Vitamin B2"]]
        symptoms["mouth_ulcers"] = int(np.clip(round(max(ulcer_drivers) * 6.5 + rng.integers(0, 3)), 0, 10))

        # Night blindness: Vitamin A
        symptoms["night_blindness"] = int(np.clip(round(risk_probs["Vitamin A"] * 8.0 + rng.integers(0, 2)), 0, 10))

        # Slow wound healing: Zinc, Vitamin C, Protein
        heal_drivers = [risk_probs["Zinc"], risk_probs["Vitamin C"], risk_probs["Protein"]]
        symptoms["slow_wound_healing"] = int(np.clip(round(max(heal_drivers) * 7.0 + rng.integers(0, 3)), 0, 10))

        # Tingling/Numbness (paresthesia): Vitamin B12, Calcium, B1, B6
        tingling_drivers = [risk_probs["Vitamin B12"], risk_probs["Calcium"], risk_probs["Vitamin B1"], risk_probs["Vitamin B6"]]
        symptoms["tingling_numbness"] = int(np.clip(round(max(tingling_drivers) * 7.5 + rng.integers(0, 2)), 0, 10))

        # Irritability: Vitamin B1, B6, Magnesium
        symptoms["irritability"] = int(np.clip(round(max([risk_probs["Vitamin B1"], risk_probs["Vitamin B6"], risk_probs["Magnesium"]]) * 7.0 + rng.integers(0, 2)), 0, 10))

        # Poor appetite: Vitamin B1, Zinc
        symptoms["poor_appetite"] = int(np.clip(round(max([risk_probs["Vitamin B1"], risk_probs["Zinc"]]) * 7.0 + rng.integers(0, 2)), 0, 10))

        # Cracked lips (angular cheilosis): Vitamin B2, B6, Iron
        symptoms["cracked_lips"] = int(np.clip(round(max([risk_probs["Vitamin B2"], risk_probs["Vitamin B6"], risk_probs["Iron"]]) * 7.5 + rng.integers(0, 2)), 0, 10))

        # Eye irritation / photophobia: Vitamin B2, Vitamin A
        symptoms["eye_irritation"] = int(np.clip(round(max([risk_probs["Vitamin B2"], risk_probs["Vitamin A"]]) * 6.5 + rng.integers(0, 2)), 0, 10))

        # Dermatitis: Vitamin B3, B6, Zinc
        symptoms["dermatitis"] = int(np.clip(round(max([risk_probs["Vitamin B3"], risk_probs["Vitamin B6"], risk_probs["Zinc"]]) * 7.5 + rng.integers(0, 2)), 0, 10))

        # Digestive disturbances: Vitamin B3, Potassium, Magnesium
        symptoms["digestive_disturbances"] = int(np.clip(round(max([risk_probs["Vitamin B3"], risk_probs["Potassium"], risk_probs["Magnesium"]]) * 7.0 + rng.integers(0, 2)), 0, 10))

        # Irregular heartbeat (palpitations): Potassium, Magnesium, Calcium
        symptoms["irregular_heartbeat"] = int(np.clip(round(max([risk_probs["Potassium"], risk_probs["Magnesium"], risk_probs["Calcium"]]) * 8.0 + rng.integers(0, 2)), 0, 10))

        # Thyroid dysfunction: Iodine, Selenium
        symptoms["thyroid_dysfunction"] = int(np.clip(round(max([risk_probs["Iodine"], risk_probs["Selenium"]]) * 8.5 + rng.integers(0, 2)), 0, 10))

        # Unexplained weight gain: Iodine (hypometabolism)
        symptoms["unexplained_weight_gain"] = int(np.clip(round(risk_probs["Iodine"] * 7.5 + rng.integers(0, 2)), 0, 10))

        # Assemble clean record
        record = {
            # Demographics
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            # Dietary Habits
            "dietary_pattern": diet_pattern,
            "meals_per_day": meals_per_day,
            "water_intake_liters": round(water_intake_liters, 1),
            "daily_fruit_vegetable_servings": fruit_veg_servings,
            "food_restrictions": food_restrictions,
            # Lifestyle Factors
            "activity_level": activity_level,
            "sleep_hours_per_night": round(sleep_hours, 1),
            "sunlight_exposure_min_per_day": sunlight_min,
            "stress_level": stress_level,
            "smoking_status": smoking_status,
            "alcohol_consumption": alcohol_consumption,
            # Medical History
            "has_digestive_disorder": has_digestive_disorder,
            "has_chronic_disease": has_chronic_disease,
            "has_prior_deficiency": has_prior_deficiency,
            # Supplement Usage
            "takes_multivitamin": takes_multivitamin,
            "takes_vitamin_d": takes_vitamin_d,
            "takes_iron": takes_iron,
            "takes_b12": takes_b12,
            "takes_calcium": takes_calcium,
            "takes_magnesium": takes_magnesium,
            "takes_zinc": takes_zinc,
            "supplement_duration_months": supplement_duration_months,
            # Symptoms
            "symptoms": symptoms,
            # Target labels (3-class ground truth)
            "targets": target_classes,
            # Target continuous probabilities (for ROC-AUC and scoring calibration)
            "target_probs": risk_probs
        }
        return record

    def generate_dataframe(self, n_samples: int = 2500) -> pd.DataFrame:
        """Generates a tabular dataset of patient screening records."""
        records = [self.generate_patient_record() for _ in range(n_samples)]
        
        flat_rows = []
        for r in records:
            flat = {}
            for k, v in r.items():
                if k == "symptoms":
                    for sym_name, sev in v.items():
                        flat[f"symptom_{sym_name}"] = sev
                elif k == "food_restrictions":
                    flat["has_gluten_free"] = 1 if "gluten_free" in v else 0
                    flat["has_dairy_free"] = 1 if "dairy_free" in v else 0
                    flat["has_meat_free"] = 1 if "meat_free" in v else 0
                elif k == "targets":
                    for nut, cls_val in v.items():
                        flat[f"target_{nut}"] = cls_val
                elif k == "target_probs":
                    for nut, prob_val in v.items():
                        flat[f"prob_{nut}"] = prob_val
                else:
                    flat[k] = v
            flat_rows.append(flat)
            
        df = pd.DataFrame(flat_rows)
        return df
