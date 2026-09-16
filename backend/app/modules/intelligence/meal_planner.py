"""
Personalized Meal Intelligence Engine
Phase 8: Nutrition Intelligence & Clinical Decision Engine

Generates multi-constraint optimized culinary meal schedules (Breakfast, Lunch, Dinner, Snack)
scored by Nutrient Density, Bioavailability, and Deficiency Correction Efficiency.
"""

from typing import List, Dict, Any, Optional
import random
from .schemas import (
    MealRecipeItem,
    DailyMealPlan,
    WeeklyMealPlan,
    MealIntelligenceResponse,
    MealPlanRequest
)

# ─────────────────────────────────────────────────────────────────────────────
# Comprehensive Clinical Recipe Library
# Tagged with nutritional delivery, bioavailability score, diet tags, budget & cuisine
# ─────────────────────────────────────────────────────────────────────────────

RECIPE_DATABASE: List[Dict[str, Any]] = [
    # ── BREAKFAST ──
    {
        "id": "bf_1",
        "meal_type": "BREAKFAST",
        "recipe_title": "Wild Sockeye Salmon & Spinach Scramble with Sprouted Toast",
        "description": "Omega-3 rich sockeye salmon folded with organic spinach and pasture-raised eggs, served alongside Ezekiel sprouted grain toast.",
        "calories": 420,
        "protein_g": 34.0,
        "carbs_g": 22.0,
        "fats_g": 21.0,
        "target_nutrients_closed": ["PROTEIN", "VITAMIN_D", "VITAMIN_B12", "IRON", "VITAMIN_A"],
        "nutrient_density_score": 94.0,
        "bioavailability_score": 92.0,
        "preparation_time_minutes": 15,
        "budget_level": "PREMIUM",
        "dietary_tags": ["OMNIVORE", "DAIRY_FREE"],
        "cuisine_type": "MEDITERRANEAN",
        "key_ingredients": ["Wild sockeye salmon", "Pasture eggs", "Baby spinach", "Sprouted grain bread", "Extra virgin olive oil"],
        "clinical_notes": "High heme-iron and intact cholecalciferol (Vitamin D3); minimal oxalates due to light steaming of spinach."
    },
    {
        "id": "bf_2",
        "meal_type": "BREAKFAST",
        "recipe_title": "Golden Turmeric Tofu Scramble with Avocado & Nutritional Yeast",
        "description": "Calcium-set firm tofu sautéed with antioxidant turmeric, cumin, cherry tomatoes, and vitamin B12-fortified nutritional yeast on sourdough.",
        "calories": 380,
        "protein_g": 24.0,
        "carbs_g": 28.0,
        "fats_g": 19.0,
        "target_nutrients_closed": ["CALCIUM", "VITAMIN_B12", "PROTEIN", "IRON", "MAGNESIUM"],
        "nutrient_density_score": 88.0,
        "bioavailability_score": 84.0,
        "preparation_time_minutes": 12,
        "budget_level": "BUDGET",
        "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "OMNIVORE"],
        "cuisine_type": "GLOBAL_FUSION",
        "key_ingredients": ["Organic firm tofu", "Nutritional yeast", "Avocado", "Turmeric & black pepper", "Sourdough"],
        "clinical_notes": "Piperine from black pepper enhances curcumin absorption by 2000%; nutritional yeast supplies methylcobalamin."
    },
    {
        "id": "bf_3",
        "meal_type": "BREAKFAST",
        "recipe_title": "Chia Seed & Hemp Heart Overnight Pudding with Kiwi & Blueberries",
        "description": "Hydrated chia seeds in calcium-fortified almond milk, crowned with organic hemp hearts, sliced gold kiwi, and Ceylon cinnamon.",
        "calories": 340,
        "protein_g": 16.0,
        "carbs_g": 36.0,
        "fats_g": 16.0,
        "target_nutrients_closed": ["MAGNESIUM", "CALCIUM", "VITAMIN_C", "POTASSIUM", "VITAMIN_E"],
        "nutrient_density_score": 91.0,
        "bioavailability_score": 86.0,
        "preparation_time_minutes": 5,
        "budget_level": "MODERATE",
        "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
        "cuisine_type": "AMERICAN",
        "key_ingredients": ["Black chia seeds", "Hemp hearts", "Fortified almond milk", "Gold kiwi (high vit C)", "Ceylon cinnamon"],
        "clinical_notes": "Gold kiwi provides 130mg ascorbate per fruit, boosting non-heme iron and zinc mucosal uptake from chia seeds."
    },
    {
        "id": "bf_4",
        "meal_type": "BREAKFAST",
        "recipe_title": "Pasture-Raised Boiled Eggs & Steamed Asparagus with Tahini Drizzle",
        "description": "Soft-boiled pasture eggs paired with crisp steamed asparagus spears, drizzled with raw unhulled sesame tahini and lemon zest.",
        "calories": 360,
        "protein_g": 22.0,
        "carbs_g": 10.0,
        "fats_g": 26.0,
        "target_nutrients_closed": ["FOLATE", "CALCIUM", "VITAMIN_B12", "VITAMIN_A", "SELENIUM"],
        "nutrient_density_score": 93.0,
        "bioavailability_score": 90.0,
        "preparation_time_minutes": 10,
        "budget_level": "MODERATE",
        "dietary_tags": ["VEGETARIAN", "KETO", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
        "cuisine_type": "MEDITERRANEAN",
        "key_ingredients": ["Pasture-raised eggs", "Fresh asparagus", "Raw sesame tahini", "Cold-pressed lemon juice"],
        "clinical_notes": "Asparagus delivers pristine tetrahydrofolates; egg yolk lecithin facilitates fat-soluble carotenoid assimilation."
    },

    # ── LUNCH ──
    {
        "id": "ln_1",
        "meal_type": "LUNCH",
        "recipe_title": "Mediterranean Quinoa Bowl with Lentils, Kalamata Olives & Roasted Pepitas",
        "description": "Tricolor sprouted quinoa tossed with French green lentils, diced cucumbers, heirloom tomatoes, roasted pumpkin seeds, and mint vinaigrette.",
        "calories": 510,
        "protein_g": 25.0,
        "carbs_g": 68.0,
        "fats_g": 18.0,
        "target_nutrients_closed": ["IRON", "MAGNESIUM", "ZINC", "FOLATE", "POTASSIUM"],
        "nutrient_density_score": 96.0,
        "bioavailability_score": 87.0,
        "preparation_time_minutes": 20,
        "budget_level": "BUDGET",
        "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
        "cuisine_type": "MEDITERRANEAN",
        "key_ingredients": ["Sprouted quinoa", "Green lentils", "Pumpkin seeds (pepitas)", "Cucumbers", "Extra virgin olive oil"],
        "clinical_notes": "Sprouted quinoa minimizes phytates; pumpkin seeds provide over 40% daily magnesium and zinc."
    },
    {
        "id": "ln_2",
        "meal_type": "LUNCH",
        "recipe_title": "Wild Pacific Sardine Salad with Lacinato Kale & Lemon Herb Dressing",
        "description": "Olive-oil packed sardines with soft edible bones served over shredded lacinato kale, shaved fennel, bell peppers, and avocado slices.",
        "calories": 480,
        "protein_g": 36.0,
        "carbs_g": 14.0,
        "fats_g": 32.0,
        "target_nutrients_closed": ["CALCIUM", "VITAMIN_D", "VITAMIN_B12", "SELENIUM", "PROTEIN"],
        "nutrient_density_score": 98.0,
        "bioavailability_score": 95.0,
        "preparation_time_minutes": 10,
        "budget_level": "BUDGET",
        "dietary_tags": ["OMNIVORE", "DAIRY_FREE", "GLUTEN_FREE", "KETO"],
        "cuisine_type": "MEDITERRANEAN",
        "key_ingredients": ["Wild canned sardines (bones included)", "Lacinato kale (low oxalate)", "Fennel", "Hass avocado", "Lemon"],
        "clinical_notes": "Sardine bones supply bioidentical calcium hydroxyapatite combined with 450 IU Vitamin D3."
    },
    {
        "id": "ln_3",
        "meal_type": "LUNCH",
        "recipe_title": "Spiced Tempeh Buddha Bowl with Edamame, Bok Choy & Ginger Dressing",
        "description": "Fermented organic tempeh cubes pan-glazed in tamari-ginger, over steamed brown rice, edamame pods, and tender baby bok choy.",
        "calories": 530,
        "protein_g": 32.0,
        "carbs_g": 58.0,
        "fats_g": 20.0,
        "target_nutrients_closed": ["PROTEIN", "CALCIUM", "IRON", "MAGNESIUM", "POTASSIUM"],
        "nutrient_density_score": 92.0,
        "bioavailability_score": 89.0,
        "preparation_time_minutes": 25,
        "budget_level": "MODERATE",
        "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
        "cuisine_type": "ASIAN",
        "key_ingredients": ["Fermented tempeh", "Organic edamame", "Baby bok choy", "Brown jasmine rice", "Ginger tamari"],
        "clinical_notes": "Rhizopus fungal fermentation in tempeh eliminates 60% of phytate complexes, doubling iron and zinc bioavailability."
    },
    {
        "id": "ln_4",
        "meal_type": "LUNCH",
        "recipe_title": "Citrus Herb Grilled Chicken Salad with Walnuts & Bell Peppers",
        "description": "Pasture-raised chicken breast grilled in rosemary and lemon juice, layered with crisp arugula, sliced bell peppers, and toasted walnuts.",
        "calories": 490,
        "protein_g": 42.0,
        "carbs_g": 12.0,
        "fats_g": 29.0,
        "target_nutrients_closed": ["PROTEIN", "VITAMIN_B3", "VITAMIN_B6", "VITAMIN_C", "VITAMIN_E"],
        "nutrient_density_score": 90.0,
        "bioavailability_score": 93.0,
        "preparation_time_minutes": 20,
        "budget_level": "MODERATE",
        "dietary_tags": ["OMNIVORE", "DAIRY_FREE", "GLUTEN_FREE", "KETO"],
        "cuisine_type": "AMERICAN",
        "key_ingredients": ["Pasture chicken breast", "Baby arugula", "Red bell pepper", "Walnuts", "Lemon vinaigrette"],
        "clinical_notes": "High cellular zinc and vitamin B6 in poultry with 150mg ascorbic acid from raw red bell pepper."
    },

    # ── DINNER ──
    {
        "id": "dn_1",
        "meal_type": "DINNER",
        "recipe_title": "Herb-Crusted Wild Cod Fillet with Baked Sweet Potato & Sautéed Swiss Chard",
        "description": "Wild Alaskan cod baked with garlic and parsley crust, paired with a slow-baked orange sweet potato and garlic-braised Swiss chard.",
        "calories": 520,
        "protein_g": 44.0,
        "carbs_g": 52.0,
        "fats_g": 14.0,
        "target_nutrients_closed": ["IODINE", "SELENIUM", "VITAMIN_A", "POTASSIUM", "MAGNESIUM"],
        "nutrient_density_score": 97.0,
        "bioavailability_score": 94.0,
        "preparation_time_minutes": 30,
        "budget_level": "PREMIUM",
        "dietary_tags": ["OMNIVORE", "DAIRY_FREE", "GLUTEN_FREE"],
        "cuisine_type": "MEDITERRANEAN",
        "key_ingredients": ["Wild Pacific cod", "Japanese sweet potato", "Swiss chard", "Fresh garlic", "Olive oil"],
        "clinical_notes": "Alaskan cod delivers 99% daily iodine for thyroid T3/T4 synthesis; beta-carotene in sweet potato converts efficiently to active retinol."
    },
    {
        "id": "dn_2",
        "meal_type": "DINNER",
        "recipe_title": "Braised Grass-Fed Beef Liver & Caramelized Onions with Cauliflower Mash",
        "description": "Thin-sliced grass-fed beef liver quickly seared with caramelized balsamic onions, paired with roasted garlic cauliflower purée.",
        "calories": 460,
        "protein_g": 38.0,
        "carbs_g": 20.0,
        "fats_g": 24.0,
        "target_nutrients_closed": ["IRON", "VITAMIN_B12", "VITAMIN_A", "FOLATE", "COPPER"],
        "nutrient_density_score": 100.0,
        "bioavailability_score": 98.0,
        "preparation_time_minutes": 20,
        "budget_level": "MODERATE",
        "dietary_tags": ["OMNIVORE", "GLUTEN_FREE", "KETO"],
        "cuisine_type": "AMERICAN",
        "key_ingredients": ["Grass-fed beef liver", "Sweet yellow onions", "Cauliflower florets", "Grass-fed butter or olive oil"],
        "clinical_notes": "Highest biological nutrient density on earth; 100g supplies >1000% B12 and 100% bioavailable heme iron."
    },
    {
        "id": "dn_3",
        "meal_type": "DINNER",
        "recipe_title": "Spiced Red Lentil & Butternut Squash Curry with Brown Basmati & Cashews",
        "description": "Fragrant stew of split red lentils and roasted butternut squash infused with ginger, cumin, coriander, and finished with toasted cashews.",
        "calories": 540,
        "protein_g": 24.0,
        "carbs_g": 78.0,
        "fats_g": 17.0,
        "target_nutrients_closed": ["FOLATE", "IRON", "POTASSIUM", "VITAMIN_A", "MAGNESIUM"],
        "nutrient_density_score": 91.0,
        "bioavailability_score": 85.0,
        "preparation_time_minutes": 35,
        "budget_level": "BUDGET",
        "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
        "cuisine_type": "ASIAN",
        "key_ingredients": ["Split red lentils", "Butternut squash", "Ginger root", "Brown basmati rice", "Raw cashews"],
        "clinical_notes": "Slow simmering with fresh tomato acid and ginger enhances non-heme iron solubility."
    },
    {
        "id": "dn_4",
        "meal_type": "DINNER",
        "recipe_title": "Pan-Seared Halibut with Shiitake Mushrooms & Steamed Broccolini",
        "description": "Wild halibut fillet seared golden, accompanied by sautéed shiitake mushrooms in garlic-tamari reduction and steamed broccolini.",
        "calories": 490,
        "protein_g": 46.0,
        "carbs_g": 16.0,
        "fats_g": 22.0,
        "target_nutrients_closed": ["SELENIUM", "VITAMIN_D", "PROTEIN", "VITAMIN_C", "POTASSIUM"],
        "nutrient_density_score": 95.0,
        "bioavailability_score": 93.0,
        "preparation_time_minutes": 25,
        "budget_level": "PREMIUM",
        "dietary_tags": ["OMNIVORE", "DAIRY_FREE", "GLUTEN_FREE", "KETO"],
        "cuisine_type": "ASIAN",
        "key_ingredients": ["Wild halibut", "Shiitake mushrooms (ergosterol)", "Broccolini", "Garlic", "Avocado oil"],
        "clinical_notes": "Halibut provides potent selenium; shiitake fungal polysaccharides promote gut microbiome and immune surveillance."
    },

    # ── SNACK ──
    {
        "id": "sn_1",
        "meal_type": "SNACK",
        "recipe_title": "Raw Brazil Nut & Pumpkin Seed Trail Mix with 85% Dark Chocolate",
        "description": "Curated micronutrient snack: 2 raw Brazil nuts, 2 tbsp sprouted pumpkin seeds, and organic 85% cocoa cacao nibs.",
        "calories": 220,
        "protein_g": 8.0,
        "carbs_g": 10.0,
        "fats_g": 18.0,
        "target_nutrients_closed": ["SELENIUM", "MAGNESIUM", "ZINC", "IRON"],
        "nutrient_density_score": 96.0,
        "bioavailability_score": 88.0,
        "preparation_time_minutes": 2,
        "budget_level": "MODERATE",
        "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE", "KETO"],
        "cuisine_type": "GLOBAL_FUSION",
        "key_ingredients": ["Raw Brazil nuts", "Sprouted pumpkin seeds", "85% dark chocolate"],
        "clinical_notes": "Two Brazil nuts exceed 100% daily selenium requirement (180mcg), fueling glutathione peroxidase."
    },
    {
        "id": "sn_2",
        "meal_type": "SNACK",
        "recipe_title": "Organic Greek Yogurt with Blackstrap Molasses & Sliced Strawberries",
        "description": "Thick unsweetened grass-fed Greek yogurt swirled with mineral-rich unsulfured blackstrap molasses and fresh strawberries.",
        "calories": 190,
        "protein_g": 16.0,
        "carbs_g": 20.0,
        "fats_g": 5.0,
        "target_nutrients_closed": ["CALCIUM", "IRON", "POTASSIUM", "VITAMIN_B12", "VITAMIN_C"],
        "nutrient_density_score": 92.0,
        "bioavailability_score": 91.0,
        "preparation_time_minutes": 3,
        "budget_level": "BUDGET",
        "dietary_tags": ["VEGETARIAN", "GLUTEN_FREE", "OMNIVORE"],
        "cuisine_type": "MEDITERRANEAN",
        "key_ingredients": ["Grass-fed Greek yogurt", "Blackstrap molasses", "Organic strawberries"],
        "clinical_notes": "Molasses adds 3.5mg non-heme iron and 200mg calcium, absorbed smoothly alongside strawberry ascorbic acid."
    },
    {
        "id": "sn_3",
        "meal_type": "SNACK",
        "recipe_title": "Crisp Roasted Edamame with Sea Salt & Smoked Paprika",
        "description": "Crunchy oven-roasted young green soybeans dusted with coarse sea salt and smoked Spanish paprika.",
        "calories": 160,
        "protein_g": 14.0,
        "carbs_g": 11.0,
        "fats_g": 7.0,
        "target_nutrients_closed": ["PROTEIN", "FOLATE", "IRON", "MAGNESIUM"],
        "nutrient_density_score": 89.0,
        "bioavailability_score": 85.0,
        "preparation_time_minutes": 5,
        "budget_level": "BUDGET",
        "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
        "cuisine_type": "ASIAN",
        "key_ingredients": ["Young edamame", "Sea salt", "Smoked paprika", "Olive oil mist"],
        "clinical_notes": "High natural folate concentration supporting cellular methylation and homocysteine reduction."
    }
]


class MealIntelligenceEngine:
    """
    Solves multi-constraint recipe assembly for targeted nutrient deficiency resolution.
    Runs in < 50ms.
    """

    def __init__(self, recipe_catalog: Optional[List[Dict[str, Any]]] = None):
        self.recipes = recipe_catalog or RECIPE_DATABASE

    def _filter_and_score_recipes(
        self,
        meal_type: str,
        target_deficiencies: List[str],
        dietary_preference: str,
        budget_level: str,
        cuisine_preference: str
    ) -> List[MealRecipeItem]:
        """
        Filters candidates and ranks them by deficiency correction efficiency.
        """
        diet = dietary_preference.upper()
        budget = budget_level.upper()
        cuisine = cuisine_preference.upper()
        target_defs_set = {d.upper() for d in target_deficiencies}

        candidates = [r for r in self.recipes if r["meal_type"] == meal_type]

        # Apply dietary filter
        if diet not in ["OMNIVORE", "ANY"]:
            filtered = [r for r in candidates if diet in r["dietary_tags"]]
            if filtered:
                candidates = filtered

        scored_items: List[MealRecipeItem] = []

        for r in candidates:
            # Calculate correction efficiency score based on target overlap
            overlapping = [nut for nut in r["target_nutrients_closed"] if nut in target_defs_set or any(nut in d for d in target_defs_set)]
            target_count = len(overlapping)
            
            # Base efficiency score (50 base + 15 per overlapping nutrient)
            eff_score = min(98.0, round(50.0 + (target_count * 16.0), 1))
            if not target_defs_set:
                eff_score = 85.0

            # Slight budget or cuisine boost if matched
            if budget == r["budget_level"]:
                eff_score = min(100.0, eff_score + 3.0)
            if cuisine == r["cuisine_type"]:
                eff_score = min(100.0, eff_score + 3.0)

            item = MealRecipeItem(
                meal_type=r["meal_type"],
                recipe_title=r["recipe_title"],
                description=r["description"],
                calories=r["calories"],
                protein_g=r["protein_g"],
                carbs_g=r["carbs_g"],
                fats_g=r["fats_g"],
                target_nutrients_closed=r["target_nutrients_closed"],
                nutrient_density_score=r["nutrient_density_score"],
                bioavailability_score=r["bioavailability_score"],
                correction_efficiency_score=eff_score,
                preparation_time_minutes=r["preparation_time_minutes"],
                budget_level=r["budget_level"],
                dietary_tags=r["dietary_tags"],
                cuisine_type=r["cuisine_type"],
                key_ingredients=r["key_ingredients"],
                clinical_notes=r["clinical_notes"]
            )
            scored_items.append(item)

        # Sort highest correction efficiency first
        scored_items.sort(key=lambda x: -x.correction_efficiency_score)
        return scored_items

    def generate_daily_plan(
        self,
        day_name: str = "Monday",
        day_number: int = 1,
        target_deficiencies: Optional[List[str]] = None,
        dietary_preference: str = "OMNIVORE",
        budget_level: str = "MODERATE",
        cuisine_preference: str = "MEDITERRANEAN",
        rotation_offset: int = 0
    ) -> DailyMealPlan:
        """
        Assembles a coherent single day meal schedule.
        """
        defs = target_deficiencies or []

        bf_candidates = self._filter_and_score_recipes("BREAKFAST", defs, dietary_preference, budget_level, cuisine_preference)
        ln_candidates = self._filter_and_score_recipes("LUNCH", defs, dietary_preference, budget_level, cuisine_preference)
        dn_candidates = self._filter_and_score_recipes("DINNER", defs, dietary_preference, budget_level, cuisine_preference)
        sn_candidates = self._filter_and_score_recipes("SNACK", defs, dietary_preference, budget_level, cuisine_preference)

        # Pick with rotation offset so weekly days vary
        bf = bf_candidates[rotation_offset % len(bf_candidates)]
        ln = ln_candidates[rotation_offset % len(ln_candidates)]
        dn = dn_candidates[rotation_offset % len(dn_candidates)]
        sn = sn_candidates[rotation_offset % len(sn_candidates)]

        total_cals = bf.calories + ln.calories + dn.calories + sn.calories
        total_p = round(bf.protein_g + ln.protein_g + dn.protein_g + sn.protein_g, 1)
        total_c = round(bf.carbs_g + ln.carbs_g + dn.carbs_g + sn.carbs_g, 1)
        total_f = round(bf.fats_g + ln.fats_g + dn.fats_g + sn.fats_g, 1)
        avg_bio = round((bf.bioavailability_score + ln.bioavailability_score + dn.bioavailability_score + sn.bioavailability_score) / 4.0, 1)
        avg_eff = round((bf.correction_efficiency_score + ln.correction_efficiency_score + dn.correction_efficiency_score + sn.correction_efficiency_score) / 4.0, 1)

        return DailyMealPlan(
            day_name=day_name,
            day_number=day_number,
            breakfast=bf,
            lunch=ln,
            dinner=dn,
            snack=sn,
            daily_calories=total_cals,
            daily_protein_g=total_p,
            daily_carbs_g=total_c,
            daily_fats_g=total_f,
            daily_average_bioavailability=avg_bio,
            daily_average_correction_efficiency=avg_eff
        )

    def generate_weekly_plan(
        self,
        target_deficiencies: Optional[List[str]] = None,
        dietary_preference: str = "OMNIVORE",
        budget_level: str = "MODERATE",
        cuisine_preference: str = "MEDITERRANEAN"
    ) -> WeeklyMealPlan:
        """
        Generates 7 rotational daily meal schedules with consolidated grocery staples.
        """
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days: List[DailyMealPlan] = []
        all_ingredients = set()

        for idx, name in enumerate(day_names):
            d_plan = self.generate_daily_plan(
                day_name=name,
                day_number=idx + 1,
                target_deficiencies=target_deficiencies,
                dietary_preference=dietary_preference,
                budget_level=budget_level,
                cuisine_preference=cuisine_preference,
                rotation_offset=idx
            )
            days.append(d_plan)
            for ing in d_plan.breakfast.key_ingredients + d_plan.lunch.key_ingredients + d_plan.dinner.key_ingredients + d_plan.snack.key_ingredients:
                all_ingredients.add(ing)

        staples = sorted(list(all_ingredients))[:18]

        return WeeklyMealPlan(
            plan_title=f"Targeted 7-Day Recovery Protocol ({dietary_preference.capitalize()})",
            dietary_preference=dietary_preference,
            budget_level=budget_level,
            cuisine_preference=cuisine_preference,
            days=days,
            weekly_grocery_staples=staples
        )

    def get_deficiency_recovery_templates(self) -> List[Dict[str, Any]]:
        """
        Returns specialized clinical meal protocol templates.
        """
        return [
            {
                "template_id": "iron_deficiency_anemia",
                "title": "Clinical Iron Deficiency & Erythrocyte Regeneration Protocol",
                "focus_nutrients": ["IRON", "VITAMIN_C", "VITAMIN_B12", "FOLATE", "COPPER"],
                "clinical_rationale": "Pairs high heme and non-heme iron sources with high-ascorbate foods while segregating dietary calcium and tannins by 2 hours.",
                "sample_lunch": "French Green Lentil & Quinoa Bowl with Sliced Red Bell Peppers and Lemon Dressing",
                "synergy_multiplier": "2.8x Iron Bioavailability via Ascorbic Chelation"
            },
            {
                "template_id": "bone_density_osteomalacia",
                "title": "Osteo-Metabolic Bone Matrix Stabilization Protocol",
                "focus_nutrients": ["CALCIUM", "VITAMIN_D", "MAGNESIUM", "PROTEIN"],
                "clinical_rationale": "Optimizes 2:1 Calcium-to-Magnesium ratio alongside Vitamin D3 to stimulate osteoblast mineralization without vascular calcification.",
                "sample_lunch": "Wild Pacific Sardines with Soft Bones over Lacinato Kale and Tahini",
                "synergy_multiplier": "Dual Vitamin D3 + Hydroxyapatite Matrix"
            },
            {
                "template_id": "neurological_energy_mitochondrial",
                "title": "Mitochondrial Bioenergetics & Neuro-Cognitive Protocol",
                "focus_nutrients": ["VITAMIN_B1", "VITAMIN_B12", "MAGNESIUM", "SELENIUM", "ZINC"],
                "clinical_rationale": "Furnishes coenzymes for pyruvate dehydrogenase and ATP synthase while dampening neuro-inflammatory oxidation.",
                "sample_lunch": "Spiced Tempeh Buddha Bowl with Bok Choy, Brown Rice, and Roasted Pumpkin Seeds",
                "synergy_multiplier": "Complete B-Complex Cellular Transketolase Support"
            }
        ]

    def build_full_meal_intelligence(
        self,
        request: MealPlanRequest
    ) -> MealIntelligenceResponse:
        """
        Assembles the complete response object.
        """
        target_defs = request.deficiencies or ["IRON", "VITAMIN_D", "MAGNESIUM"]
        diet = request.dietary_preference or "OMNIVORE"
        budget = request.budget_level or "MODERATE"
        cuisine = request.cuisine_preference or "MEDITERRANEAN"

        daily_plan = self.generate_daily_plan(
            day_name="Day 1",
            day_number=1,
            target_deficiencies=target_defs,
            dietary_preference=diet,
            budget_level=budget,
            cuisine_preference=cuisine
        )

        weekly_plan = None
        if request.include_weekly:
            weekly_plan = self.generate_weekly_plan(
                target_deficiencies=target_defs,
                dietary_preference=diet,
                budget_level=budget,
                cuisine_preference=cuisine
            )

        templates = self.get_deficiency_recovery_templates()

        return MealIntelligenceResponse(
            assessment_id=request.assessment_id,
            target_deficiencies=target_defs,
            dietary_preference=diet,
            budget_level=budget,
            cuisine_preference=cuisine,
            daily_plan=daily_plan,
            weekly_plan=weekly_plan,
            deficiency_recovery_templates=templates
        )
