import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.modules.personalization.forecasting_engine import ClinicalOutcomeForecaster

print("============================================================")
print("RUNNING FORECAST SENSITIVITY VALIDATION (PHASE 2)")
print("============================================================")

case_a = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Vitamin D", baseline_override=8.0)
case_b = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Vitamin D", baseline_override=18.0)
case_c = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Vitamin D", baseline_override=35.0)

print(f"\n[Case A - Severe Deficiency (Baseline: 8.0 ng/mL)]")
print(f"  Velocity: {case_a.recovery_velocity}")
print(f"  Estimated Days to Normalization: {case_a.estimated_days_to_normalization}")
print(f"  Day 30 Predicted: {case_a.trajectory_points[0].predicted_level} ng/mL (CI: [{case_a.trajectory_points[0].lower_bound_95}, {case_a.trajectory_points[0].upper_bound_95}]) | Tier: {case_a.trajectory_points[0].clinical_tier}")
print(f"  Day 60 Predicted: {case_a.trajectory_points[1].predicted_level} ng/mL | Prob: {case_a.trajectory_points[1].normalization_probability}")

print(f"\n[Case B - Moderate Deficiency (Baseline: 18.0 ng/mL)]")
print(f"  Velocity: {case_b.recovery_velocity}")
print(f"  Estimated Days to Normalization: {case_b.estimated_days_to_normalization}")
print(f"  Day 30 Predicted: {case_b.trajectory_points[0].predicted_level} ng/mL (CI: [{case_b.trajectory_points[0].lower_bound_95}, {case_b.trajectory_points[0].upper_bound_95}]) | Tier: {case_b.trajectory_points[0].clinical_tier}")
print(f"  Day 60 Predicted: {case_b.trajectory_points[1].predicted_level} ng/mL | Prob: {case_b.trajectory_points[1].normalization_probability}")

print(f"\n[Case C - Sufficient / Optimal (Baseline: 35.0 ng/mL)]")
print(f"  Velocity: {case_c.recovery_velocity}")
print(f"  Estimated Days to Normalization: {case_c.estimated_days_to_normalization}")
print(f"  Day 30 Predicted: {case_c.trajectory_points[0].predicted_level} ng/mL (CI: [{case_c.trajectory_points[0].lower_bound_95}, {case_c.trajectory_points[0].upper_bound_95}]) | Tier: {case_c.trajectory_points[0].clinical_tier}")
print(f"  Day 60 Predicted: {case_c.trajectory_points[1].predicted_level} ng/mL | Prob: {case_c.trajectory_points[1].normalization_probability}")

# Assertions to ensure distinct, scientifically valid outputs:
assert case_a.estimated_days_to_normalization > case_b.estimated_days_to_normalization, "Case A should take longer to normalize than Case B!"
assert case_c.estimated_days_to_normalization == 0, "Case C should have 0 days to normalization (already sufficient)!"
assert case_a.recovery_velocity != case_c.recovery_velocity, "Recovery velocities must differ between severe deficit and sufficiency!"
assert case_a.trajectory_points[0].predicted_level < case_b.trajectory_points[0].predicted_level < case_c.trajectory_points[0].predicted_level, "Predicted levels must follow baseline gradient!"

# Test B12, Zinc, Vit A, Protein profiles
for nut in ["Vitamin B12", "Zinc", "Vitamin A", "Protein"]:
    item = ClinicalOutcomeForecaster.forecast_nutrient_trajectory(nut)
    assert item.nutrient == nut, f"Failed to forecast {nut}!"
    assert len(item.trajectory_points) == 3, f"Missing points for {nut}!"
    print(f"\n[Profile Test: {nut}] Target: {item.clinical_target} {item.unit}, Baseline: {item.baseline_value}, Days to Norm: {item.estimated_days_to_normalization}")

print("\n============================================================")
print("PHASE 2 SENSITIVITY VALIDATION PASSED!")
print("============================================================")
