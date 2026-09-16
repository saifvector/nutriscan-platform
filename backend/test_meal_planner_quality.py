import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.modules.personalization.meal_planner_pro import IntelligentMealPlanner, is_dish_compatible
from backend.app.modules.personalization.schemas import (
    MealPlanGenerateRequest,
    CulturalPatternEnum,
    DietaryPatternEnum
)

print("============================================================")
print("PHASE 1: MEAL PLANNER QUALITY & NUTRIENT COVERAGE VALIDATION")
print("============================================================")

patterns = [
    ("Vegetarian Mediterranean", DietaryPatternEnum.VEGETARIAN, CulturalPatternEnum.MEDITERRANEAN),
    ("Vegan Mediterranean", DietaryPatternEnum.VEGAN, CulturalPatternEnum.MEDITERRANEAN),
    ("Omnivore Mediterranean", DietaryPatternEnum.OMNIVORE, CulturalPatternEnum.MEDITERRANEAN),
    ("Vegetarian South Asian", DietaryPatternEnum.VEGETARIAN, CulturalPatternEnum.SOUTH_ASIAN),
]

for name, diet, cult in patterns:
    req = MealPlanGenerateRequest(
        target_deficiencies=["Vitamin D", "Iron", "Calcium", "Zinc"],
        dietary_pattern=diet,
        cultural_pattern=cult,
        daily_calorie_target=2000,
        daily_budget_usd=14.00,
        plan_duration_days=7
    )
    plan = IntelligentMealPlanner.generate_plan(req)
    
    comp = plan.overall_rda_compliance_pct
    print(f"\n[{name}]")
    print(f"  Plan ID: {plan.plan_id}")
    print(f"  Total Cost: ${plan.total_weekly_cost_usd} (Daily avg: ${plan.daily_average_cost_usd})")
    print(f"  Nutrient Adequacy Score: {plan.nutrient_adequacy_score}%")
    print(f"  Weekly RDA Compliance:")
    for nut, val in comp.items():
        print(f"    - {nut}: {val}%")
        
    # Check targets: Vit D > 70%, Calcium > 80%, Zinc > 80%, Iron > 80%
    vit_d = next((v for k, v in comp.items() if "vitamin d" in k.lower()), 0.0)
    calc = next((v for k, v in comp.items() if "calcium" in k.lower()), 0.0)
    zinc = next((v for k, v in comp.items() if "zinc" in k.lower()), 0.0)
    iron = next((v for k, v in comp.items() if "iron" in k.lower()), 0.0)
    
    assert vit_d >= 70.0, f"{name}: Vitamin D coverage {vit_d}% < 70% target!"
    assert calc >= 80.0, f"{name}: Calcium coverage {calc}% < 80% target!"
    assert zinc >= 80.0, f"{name}: Zinc coverage {zinc}% < 80% target!"
    assert iron >= 80.0, f"{name}: Iron coverage {iron}% < 80% target!"
    
    # Check dietary restriction compliance
    for dp in plan.daily_plans:
        for meal in dp.meals:
            dish_dict = {
                "dish_name": meal.dish_name,
                "ingredients": meal.ingredients
            }
            assert is_dish_compatible(dish_dict, diet.value), f"Dish '{meal.dish_name}' violates dietary pattern '{diet.value}'!"

print("\n============================================================")
print("SUCCESS: ALL PHASE 1 MEAL PLANNER TARGETS EXCEEDED (>70% D, >80% Ca/Zn/Fe)")
print("============================================================")
