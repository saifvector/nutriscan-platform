import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.modules.personalization.forecasting_engine import ClinicalOutcomeForecaster

print("============================================================")
print("PHASE 2: FORECAST STRESS TESTING ACROSS SEVERITY LEVELS")
print("============================================================")

levels = [5.0, 10.0, 18.0, 35.0, 60.0]
results = {}

for lvl in levels:
    item = ClinicalOutcomeForecaster.forecast_nutrient_trajectory("Vitamin D", baseline_override=lvl)
    results[lvl] = item
    print(f"\n[Baseline 25(OH)D = {lvl:4.1f} ng/mL]")
    print(f"  Recovery Velocity:              {item.recovery_velocity}")
    print(f"  Days to Normalization:          {item.estimated_days_to_normalization}")
    for p in item.trajectory_points:
        ci_width = round(p.upper_bound_95 - p.lower_bound_95, 2)
        print(f"  Day {p.horizon_days:2d}: Pred={p.predicted_level:5.2f} ng/mL | 95% CI=[{p.lower_bound_95:5.2f}, {p.upper_bound_95:5.2f}] (width={ci_width:4.2f}) | Prob={p.normalization_probability:5.3f} | Tier={p.clinical_tier}")

# 1. Verify different recovery times
days = [results[lvl].estimated_days_to_normalization for lvl in levels]
print(f"\nDays to Normalization Vector: {days}")
assert days[0] > days[1] > days[2], "Severe (5) must take longer than Moderate (10), which must take longer than Mild (18)!"
assert days[3] == 0, "Sufficient (35) must be 0 days to normalization!"
assert days[4] > 0, "Excess (60) must have distinct de-escalation duration!"

# 2. Verify different recovery curves (Day 30 and Day 60 predicted values)
curves = [[p.predicted_level for p in results[lvl].trajectory_points] for lvl in levels]
for i in range(len(levels)):
    for j in range(i + 1, len(levels)):
        assert curves[i] != curves[j], f"Trajectories for {levels[i]} and {levels[j]} cannot be identical!"

# 3. Verify different confidence interval widths
ci_widths_day30 = [round(results[lvl].trajectory_points[0].upper_bound_95 - results[lvl].trajectory_points[0].lower_bound_95, 2) for lvl in levels]
print(f"Day 30 95% CI Width Vector: {ci_widths_day30}")
assert len(set(ci_widths_day30)) == len(levels), "All 5 baseline levels must have distinct confidence interval widths!"
assert ci_widths_day30[0] > ci_widths_day30[1] > ci_widths_day30[2] > ci_widths_day30[3], "CI width must decrease as baseline approaches optimal!"

# 4. Verify no identical velocities across distinct states
velocities = [results[lvl].recovery_velocity for lvl in levels]
print(f"Velocity Vector: {velocities}")
assert results[5.0].recovery_velocity in ["GRADUAL", "MODERATE"]
assert results[18.0].recovery_velocity in ["MODERATE", "RAPID"]
assert results[35.0].recovery_velocity == "OPTIMAL_MAINTENANCE"
assert results[60.0].recovery_velocity == "DE-ESCALATION_MONITORING"

print("\n============================================================")
print("SUCCESS: PHASE 2 FORECAST STRESS TEST FULLY PASSED!")
print("============================================================")
