import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.modules.recommendation.knowledge_base import FOOD_KNOWLEDGE_BASE

target_nutrients = [
    'Vitamin D', 'Vitamin B12', 'Iron', 'Calcium', 
    'Magnesium', 'Zinc', 'Folate', 'Vitamin A', 'Protein'
]

print("=== INSPECTING FOOD_KNOWLEDGE_BASE ===")
for nut in target_nutrients:
    foods = FOOD_KNOWLEDGE_BASE.get(nut, [])
    print(f"\nNutrient: {nut} (Total foods: {len(foods)})")
    vegan_count = sum(1 for f in foods if 'VEGAN' in f.get('dietary_tags', []))
    veg_count = sum(1 for f in foods if 'VEGETARIAN' in f.get('dietary_tags', []) or 'VEGAN' in f.get('dietary_tags', []))
    print(f"  Vegan options: {vegan_count}, Vegetarian options: {veg_count}")
    for f in foods:
        print(f"    * {f['food_name']}: {f['nutrient_density']} {f['unit']} per {f['serving_size']} | tags: {f.get('dietary_tags')}")
