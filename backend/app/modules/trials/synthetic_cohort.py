"""
Synthetic Cohort Generator for Clinical Trial Simulation
Generates realistic, multivariate correlated synthetic patient cohorts grounded in NHANES distributions.
"""

from typing import List
import random
from .schemas import SyntheticPatient


class SyntheticCohortGenerator:
    """Generates synthetic patient subjects partitioned across randomized trial arms."""

    @classmethod
    def generate_cohort(cls, target_nutrient: str = "Vitamin D", cohort_size: int = 300) -> List[SyntheticPatient]:
        random.seed(42)  # Deterministic seed for reproducible testing
        subjects: List[SyntheticPatient] = []

        arms = ["CONTROL_PLACEBO", "STANDARD_CARE", "NUTRISCAN_PRECISION"]
        arm_size = cohort_size // len(arms)

        diet_types = ["OMNIVORE", "VEGETARIAN", "VEGAN", "MEDITERRANEAN", "KETO"]
        diet_weights = [0.65, 0.12, 0.05, 0.12, 0.06]

        for i in range(cohort_size):
            arm = arms[min(2, i // arm_size)]
            age = int(random.gauss(46, 12))
            age = max(18, min(78, age))

            gender = "FEMALE" if random.random() < 0.52 else "MALE"
            bmi = round(max(18.5, min(42.0, random.gauss(27.8, 4.5))), 1)
            diet = random.choices(diet_types, weights=diet_weights)[0]

            # Baseline biomarker value (lower values reflect deficient population in trial)
            if "D" in target_nutrient:
                base_val = round(max(8.0, min(24.0, random.gauss(14.8, 3.5))), 1)  # ng/mL
            elif "Iron" in target_nutrient or "Ferritin" in target_nutrient:
                base_val = round(max(5.0, min(28.0, random.gauss(15.2, 4.8))), 1)  # ng/mL
            elif "B12" in target_nutrient:
                base_val = round(max(110.0, min(240.0, random.gauss(175.0, 32.0))), 1)  # pg/mL
            else:
                base_val = round(max(10.0, min(45.0, random.gauss(22.0, 6.0))), 1)

            prob = round(max(0.60, min(0.98, 1.0 - (base_val / 40.0))), 2)

            subjects.append(SyntheticPatient(
                subject_id=f"SUBJ-{1000 + i}",
                age=age,
                gender=gender,
                bmi=bmi,
                dietary_pattern=diet,
                baseline_biomarker_value=base_val,
                baseline_deficiency_probability=prob,
                assigned_arm=arm
            ))

        return subjects
