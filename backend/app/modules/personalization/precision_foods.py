"""
Precision Food Recommendation Engine
Phase 13: Real-World Clinical Intelligence & Personalization

Integrates USDA FoodData Central foundation food density data to optimize food selection
across multiple simultaneous deficiencies, scoring foods on:
- Nutrient Density (micro/macro ratios)
- Cost Efficiency ($ per micronutrient yield)
- Bioavailability (elemental uptake & biological value)
- Clinical Relevance (direct match to active deficiencies)
- Adherence Likelihood (palatability, preparation barrier)
"""

import os
import csv
import logging
from typing import Dict, Any, List, Optional
from .schemas import PrecisionFoodItem, PrecisionFoodQuery, PrecisionFoodResponse

logger = logging.getLogger(__name__)

# Curated USDA FoodData Central Foundation Database with verified nutrient densities
USDA_FOUNDATION_CATALOG: List[Dict[str, Any]] = [
    {
        "food_name": "Wild Atlantic Salmon (Cooked)",
        "usda_fdc_id": "173686",
        "category": "Seafood & Fish",
        "serving_size": "100g (3.5 oz)",
        "calories": 182,
        "cost_per_serving_usd": 3.20,
        "bioavailability_rank": 95.0, # High bioavailability heme & fat-soluble matrix
        "adherence_rank": 88.0,
        "primary_nutrients": {
            "Vitamin D": 11.0,      # mcg (440 IU, ~73% RDA)
            "Selenium": 36.5,       # mcg (~66% RDA)
            "Vitamin B12": 3.2,     # mcg (>100% RDA)
            "Potassium": 490.0,     # mg (~14% RDA)
            "Protein": 25.4         # g
        },
        "dietary_tags": ["PESCATARIAN", "OMNIVORE", "GLUTEN_FREE", "KETO", "MEDITERRANEAN"],
        "cultural_affinity": ["MEDITERRANEAN", "NORDIC", "EAST_ASIAN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Main Protein",
        "preparation_tips": "Pan-sear skin-side down for 4 mins, flip for 3 mins. Pair with lemon (Vitamin C) for enhanced antioxidant preservation.",
        "evidence_citation": "USDA FoodData Central FDC ID 173686; NIH ODS Vitamin D & Omega-3 PUFA Bioavailability.",
        "substitutions": ["Sardines (in olive oil)", "Mackerel", "Rainbow Trout"]
    },
    {
        "food_name": "Baby Spinach (Steamed)",
        "usda_fdc_id": "170417",
        "category": "Dark Leafy Greens",
        "serving_size": "180g (1 cup cooked)",
        "calories": 41,
        "cost_per_serving_usd": 0.85,
        "bioavailability_rank": 78.0, # Non-heme iron with moderate oxalates reduced by steaming
        "adherence_rank": 82.0,
        "primary_nutrients": {
            "Folate": 263.0,        # mcg (~65% RDA)
            "Iron": 6.4,            # mg (~35% female RDA)
            "Magnesium": 157.0,     # mg (~40% RDA)
            "Calcium": 245.0,       # mg (~25% RDA)
            "Potassium": 839.0      # mg (~25% RDA)
        },
        "dietary_tags": ["VEGAN", "VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "KETO", "MEDITERRANEAN"],
        "cultural_affinity": ["MEDITERRANEAN", "SOUTH_ASIAN", "EAST_ASIAN", "MIDDLE_EASTERN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Nutrient-Dense Vegetable Side",
        "preparation_tips": "Steam lightly for 90 seconds rather than boiling to preserve water-soluble Folate and eliminate free oxalates.",
        "evidence_citation": "USDA FDC ID 170417; Weaver CM et al. Oxalate reduction and mineral bioavailability.",
        "substitutions": ["Swiss Chard", "Kale", "Collard Greens"]
    },
    {
        "food_name": "Brown Lentils (Cooked)",
        "usda_fdc_id": "172421",
        "category": "Legumes & Pulses",
        "serving_size": "198g (1 cup cooked)",
        "calories": 230,
        "cost_per_serving_usd": 0.45,
        "bioavailability_rank": 80.0,
        "adherence_rank": 85.0,
        "primary_nutrients": {
            "Folate": 358.0,        # mcg (~90% RDA)
            "Iron": 6.6,            # mg (~37% RDA)
            "Potassium": 731.0,     # mg (~22% RDA)
            "Magnesium": 71.0,      # mg (~18% RDA)
            "Zinc": 2.5,            # mg (~23% RDA)
            "Protein": 17.9         # g
        },
        "dietary_tags": ["VEGAN", "VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "MEDITERRANEAN"],
        "cultural_affinity": ["SOUTH_ASIAN", "MEDITERRANEAN", "MIDDLE_EASTERN", "LATIN_AMERICAN"],
        "culinary_role": "High-Fiber Plant Protein",
        "preparation_tips": "Soak overnight with a bay leaf before simmering; pair with diced tomatoes or bell peppers to triple non-heme iron absorption.",
        "evidence_citation": "USDA FDC ID 172421; Hurrell R, Egli I. Iron bioavailability and dietary reference values.",
        "substitutions": ["Chickpeas", "Black Beans", "Mung Dal"]
    },
    {
        "food_name": "Pasture-Raised Egg (Hard-Boiled)",
        "usda_fdc_id": "173424",
        "category": "Eggs & Poultry",
        "serving_size": "100g (2 large eggs)",
        "calories": 143,
        "cost_per_serving_usd": 0.70,
        "bioavailability_rank": 98.0, # Complete protein, highly bioavailable lutein & choline
        "adherence_rank": 92.0,
        "primary_nutrients": {
            "Vitamin D": 2.2,       # mcg (88 IU, ~15% RDA)
            "Selenium": 30.8,       # mcg (~56% RDA)
            "Folate": 44.0,         # mcg (~11% RDA)
            "Iron": 1.8,            # mg (~10% RDA)
            "Vitamin B12": 1.1      # mcg (~45% RDA)
        },
        "dietary_tags": ["VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "KETO", "MEDITERRANEAN"],
        "cultural_affinity": ["MEDITERRANEAN", "EAST_ASIAN", "LATIN_AMERICAN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Complete Breakfast / Protein Snack",
        "preparation_tips": "Boil 7 minutes for a creamy yolk preserving heat-sensitive folate and fat-soluble carotenoids.",
        "evidence_citation": "USDA FDC ID 173424; O'Neil CE et al. Egg consumption and nutrient adequacy.",
        "substitutions": ["Firm Tofu (scrambled)", "Tempeh"]
    },
    {
        "food_name": "Greek Yogurt (Plain, Whole Milk)",
        "usda_fdc_id": "170903",
        "category": "Cultured Dairy",
        "serving_size": "200g (7 oz)",
        "calories": 190,
        "cost_per_serving_usd": 1.25,
        "bioavailability_rank": 94.0, # Highly soluble calcium lactate / caseinate
        "adherence_rank": 90.0,
        "primary_nutrients": {
            "Calcium": 230.0,       # mg (~23% RDA)
            "Potassium": 282.0,     # mg (~8% RDA)
            "Magnesium": 22.0,      # mg (~6% RDA)
            "Selenium": 19.4,       # mcg (~35% RDA)
            "Protein": 18.0         # g
        },
        "dietary_tags": ["VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "MEDITERRANEAN"],
        "cultural_affinity": ["MEDITERRANEAN", "MIDDLE_EASTERN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Fermented Probiotic Base / Snack",
        "preparation_tips": "Top with raw pumpkin seeds and a drizzle of unrefined honey to add complementary magnesium and zinc.",
        "evidence_citation": "USDA FDC ID 170903; Heaney RP et al. Bioavailability of calcium from dairy vs fortified sources.",
        "substitutions": ["Fortified Soy Yogurt", "Kefir", "Almond Milk Yogurt (Calcium Fortified)"]
    },
    {
        "food_name": "Raw Pumpkin Seeds (Pepitas)",
        "usda_fdc_id": "170556",
        "category": "Nuts & Seeds",
        "serving_size": "30g (1 oz / 2 tbsp)",
        "calories": 163,
        "cost_per_serving_usd": 0.60,
        "bioavailability_rank": 86.0,
        "adherence_rank": 89.0,
        "primary_nutrients": {
            "Magnesium": 168.0,     # mg (~42% RDA)
            "Iron": 2.5,            # mg (~14% RDA)
            "Zinc": 2.2,            # mg (~20% RDA)
            "Potassium": 261.0,     # mg (~8% RDA)
            "Selenium": 2.8         # mcg (~5% RDA)
        },
        "dietary_tags": ["VEGAN", "VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "KETO", "MEDITERRANEAN"],
        "cultural_affinity": ["LATIN_AMERICAN", "MEDITERRANEAN", "MIDDLE_EASTERN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Crunchy Topping / Trail Seed",
        "preparation_tips": "Toast dry over low skillet for 2 minutes to deactivate phytates and maximize magnesium bioaccessibility.",
        "evidence_citation": "USDA FDC ID 170556; NIH ODS Magnesium Fact Sheet for Health Professionals.",
        "substitutions": ["Hemp Hearts", "Sunflower Seeds", "Chia Seeds"]
    },
    {
        "food_name": "Brazil Nuts (Shelled)",
        "usda_fdc_id": "170569",
        "category": "Nuts & Seeds",
        "serving_size": "10g (2 kernels)",
        "calories": 66,
        "cost_per_serving_usd": 0.35,
        "bioavailability_rank": 96.0, # Extremely potent selenomethionine
        "adherence_rank": 95.0,
        "primary_nutrients": {
            "Selenium": 191.0,      # mcg (~347% RDA)
            "Magnesium": 37.0,      # mg (~9% RDA)
            "Calcium": 16.0         # mg (~2% RDA)
        },
        "dietary_tags": ["VEGAN", "VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "KETO", "MEDITERRANEAN"],
        "cultural_affinity": ["LATIN_AMERICAN", "MEDITERRANEAN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Targeted Micro-Dose Functional Food",
        "preparation_tips": "Consume strictly 1 to 2 kernels daily to achieve optimal selenium saturation without exceeding the 400 mcg UL.",
        "evidence_citation": "USDA FDC ID 170569; Thomson CD et al. Brazil nuts and selenium status.",
        "substitutions": ["Sunflower Seeds", "Yellowfin Tuna", "Sardines"]
    },
    {
        "food_name": "Sardines in Olive Oil (Canned with Bones)",
        "usda_fdc_id": "175139",
        "category": "Seafood & Fish",
        "serving_size": "92g (1 can drained)",
        "calories": 191,
        "cost_per_serving_usd": 1.75,
        "bioavailability_rank": 95.0,
        "adherence_rank": 74.0, # Lower adherence due to acquired taste, offset by immense density
        "primary_nutrients": {
            "Calcium": 351.0,       # mg (~35% RDA, soft edible bones)
            "Vitamin D": 4.4,       # mcg (176 IU, ~30% RDA)
            "Selenium": 48.5,       # mcg (~88% RDA)
            "Iron": 2.7,            # mg (~15% RDA)
            "Vitamin B12": 8.2      # mcg (>300% RDA)
        },
        "dietary_tags": ["PESCATARIAN", "OMNIVORE", "GLUTEN_FREE", "KETO", "MEDITERRANEAN"],
        "cultural_affinity": ["MEDITERRANEAN", "NORDIC", "EAST_ASIAN", "LATIN_AMERICAN"],
        "culinary_role": "High-Density Protein & Calcium Booster",
        "preparation_tips": "Mash with Dijon mustard, fresh parsley, and capers on seeded sourdough for an authentic Mediterranean tartine.",
        "evidence_citation": "USDA FDC ID 175139; FAO/WHO Expert Consultation on Human Vitamin and Mineral Requirements.",
        "substitutions": ["Canned Pink Salmon with Bones", "Anchovies in Olive Oil"]
    },
    {
        "food_name": "Avocado (Hass)",
        "usda_fdc_id": "171705",
        "category": "Fruits & Healthy Fats",
        "serving_size": "150g (1 medium)",
        "calories": 240,
        "cost_per_serving_usd": 1.20,
        "bioavailability_rank": 92.0, # Lipid matrix dramatically boosts fat-soluble uptake
        "adherence_rank": 96.0,
        "primary_nutrients": {
            "Potassium": 728.0,     # mg (~21% RDA)
            "Folate": 121.0,        # mcg (~30% RDA)
            "Magnesium": 43.5,      # mg (~11% RDA)
            "Vitamin E": 3.1        # mg (~21% RDA)
        },
        "dietary_tags": ["VEGAN", "VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "KETO", "MEDITERRANEAN"],
        "cultural_affinity": ["LATIN_AMERICAN", "MEDITERRANEAN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Healthy Lipid Vehicle & Potassium Source",
        "preparation_tips": "Eat alongside carotenoid-rich greens to boost fat-soluble vitamin absorption by up to 400%.",
        "evidence_citation": "USDA FDC ID 171705; Unlu NZ et al. Carotenoid absorption from salad is enhanced by avocado.",
        "substitutions": ["Extra Virgin Olive Oil", "Walnuts", "Tahini"]
    },
    {
        "food_name": "Organic Black Beans (Cooked)",
        "usda_fdc_id": "173735",
        "category": "Legumes & Pulses",
        "serving_size": "172g (1 cup cooked)",
        "calories": 227,
        "cost_per_serving_usd": 0.40,
        "bioavailability_rank": 82.0,
        "adherence_rank": 88.0,
        "primary_nutrients": {
            "Folate": 256.0,        # mcg (~64% RDA)
            "Magnesium": 120.0,     # mg (~30% RDA)
            "Iron": 3.6,            # mg (~20% RDA)
            "Potassium": 611.0,     # mg (~18% RDA)
            "Protein": 15.2         # g
        },
        "dietary_tags": ["VEGAN", "VEGETARIAN", "OMNIVORE", "GLUTEN_FREE", "MEDITERRANEAN"],
        "cultural_affinity": ["LATIN_AMERICAN", "AMERICAN_HEART_HEALTHY"],
        "culinary_role": "Staple Fiber & Complex Carbohydrate",
        "preparation_tips": "Simmer with cumin, Mexican oregano, and lime juice. Cumin provides synergistic digestive enzymes.",
        "evidence_citation": "USDA FDC ID 173735; American Journal of Clinical Nutrition Legume Bioavailability Studies.",
        "substitutions": ["Pinto Beans", "Black-Eyed Peas", "Red Kidney Beans"]
    }
]

# Standard Adult RDAs for Reference Scaling
NUTRIENT_RDA_SCALARS: Dict[str, float] = {
    "Iron": 18.0,          # mg
    "Vitamin D": 15.0,     # mcg (600 IU)
    "Folate": 400.0,       # mcg
    "Calcium": 1000.0,     # mg
    "Magnesium": 400.0,    # mg
    "Potassium": 3400.0,   # mg
    "Selenium": 55.0,      # mcg
    "Zinc": 11.0,          # mg
    "Vitamin B12": 2.4     # mcg
}


class PrecisionFoodEngine:
    """
    Evaluates USDA foundation foods and optimizes selection for single or multiple deficiencies.
    """

    @classmethod
    def calculate_food_metrics(
        cls,
        food: Dict[str, Any],
        target_deficiencies: List[str],
        budget_limit: float = 3.50
    ) -> PrecisionFoodItem:
        """
        Computes the 5 component scores and unified composite precision score for a food item.
        """
        nutrients = food.get("primary_nutrients", {})
        calories = max(food.get("calories", 100), 1)
        cost = max(food.get("cost_per_serving_usd", 1.0), 0.1)
        bioavail = float(food.get("bioavailability_rank", 80.0))
        adherence_base = float(food.get("adherence_rank", 85.0))

        # 1. Nutrient Density Score (Yield per 100 calories)
        density_contributions = []
        for nut, amt in nutrients.items():
            rda = NUTRIENT_RDA_SCALARS.get(nut, 100.0)
            density_contributions.append((amt / rda) * (100.0 / calories) * 100.0)
        density_score = min(100.0, (sum(density_contributions) / max(len(density_contributions), 1)) * 1.5)

        # 2. Cost Efficiency Score (Yield per dollar spent)
        cost_eff = min(100.0, (density_score / cost) * 0.8)

        # 3. Clinical Relevance Score (Direct coverage of active target deficiencies)
        relevance_points = 0.0
        active_matched = 0
        for def_name in target_deficiencies:
            matched_key = next((k for k in nutrients.keys() if def_name.lower() in k.lower()), None)
            if matched_key:
                amt = nutrients[matched_key]
                rda = NUTRIENT_RDA_SCALARS.get(matched_key, 100.0)
                relevance_points += min(100.0, (amt / rda) * 100.0)
                active_matched += 1

        if target_deficiencies:
            clinical_relevance = min(100.0, (relevance_points / len(target_deficiencies)) * (1.0 + 0.25 * (active_matched - 1)))
        else:
            clinical_relevance = 60.0

        # Multi-deficiency bonus if food covers 2+ target deficiencies
        if active_matched >= 2:
            clinical_relevance = min(100.0, clinical_relevance * 1.20)

        # 4. Adherence Likelihood
        cost_penalty = 15.0 if cost > budget_limit else 0.0
        adherence_score = max(20.0, adherence_base - cost_penalty)

        # 5. Composite Precision Score
        # Weighted formula: Clinical Relevance 35%, Nutrient Density 25%, Bioavailability 20%, Cost 10%, Adherence 10%
        composite = (
            0.35 * clinical_relevance +
            0.25 * density_score +
            0.20 * bioavail +
            0.10 * cost_eff +
            0.10 * adherence_score
        )
        composite = round(min(100.0, max(10.0, composite)), 2)

        return PrecisionFoodItem(
            food_name=food["food_name"],
            usda_fdc_id=food.get("usda_fdc_id"),
            category=food["category"],
            serving_size=food["serving_size"],
            primary_nutrients=nutrients,
            nutrient_density_score=round(density_score, 1),
            cost_efficiency_score=round(cost_eff, 1),
            bioavailability_score=round(bioavail, 1),
            clinical_relevance_score=round(clinical_relevance, 1),
            adherence_likelihood_score=round(adherence_score, 1),
            composite_precision_score=composite,
            culinary_role=food.get("culinary_role", "Versatile Ingredient"),
            preparation_tips=food.get("preparation_tips", "Prepare using low-heat cooking methods."),
            evidence_citation=food.get("evidence_citation", "USDA FoodData Central"),
            substitutions=food.get("substitutions", [])
        )

    @classmethod
    def query_precision_foods(cls, query: PrecisionFoodQuery) -> PrecisionFoodResponse:
        """
        Filters and ranks foods from the USDA foundation catalog matching dietary patterns and deficiencies.
        """
        targets = query.target_deficiencies
        diet_pat = query.dietary_pattern.value.upper() if query.dietary_pattern else "OMNIVORE"
        cult_pat = query.cultural_pattern.value.upper() if query.cultural_pattern else None
        max_cost = query.max_budget_per_serving_usd or 3.50

        matched_items: List[PrecisionFoodItem] = []

        for f in USDA_FOUNDATION_CATALOG:
            tags = [t.upper() for t in f.get("dietary_tags", [])]
            cults = [c.upper() for c in f.get("cultural_affinity", [])]

            # Dietary Pattern Filtering
            if "VEGAN" in diet_pat and "VEGAN" not in tags:
                continue
            if "VEGETARIAN" in diet_pat and ("VEGETARIAN" not in tags and "VEGAN" not in tags):
                continue
            if "PESCATARIAN" in diet_pat and ("PESCATARIAN" not in tags and "VEGAN" not in tags and "VEGETARIAN" not in tags):
                continue
            if "GLUTEN_FREE" in diet_pat and "GLUTEN_FREE" not in tags:
                continue
            if "KETO" in diet_pat and "KETO" not in tags:
                continue

            item = cls.calculate_food_metrics(f, targets, budget_limit=max_cost)

            # Boost cultural affinity score if matched
            if cult_pat and any(cult_pat in c for c in cults):
                item.composite_precision_score = round(min(100.0, item.composite_precision_score * 1.08), 2)

            matched_items.append(item)

        # Sort descending by composite precision score
        matched_items.sort(key=lambda x: x.composite_precision_score, reverse=True)
        top_results = matched_items[:query.limit]

        return PrecisionFoodResponse(
            target_deficiencies=targets,
            total_matches=len(matched_items),
            top_recommended_foods=top_results
        )
