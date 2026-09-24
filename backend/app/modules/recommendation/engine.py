"""
Personalized Nutrition Recommendation Engine
Phase 5: Personalized Nutrition Recommendation Engine

Transforms multi-nutrient deficiency predictions, SHAP risk drivers, and patient habits into:
1. Diet-compatible food recommendations
2. Priority ranking (Priority 1, 2, 3) based on nutrient density, severity, and bioavailability
3. Biochemical nutrient-pair synergies (e.g., Iron + Vitamin C, Vit D + Calcium, Mg + Vit D)
4. Actionable lifestyle interventions (Sunlight, Activity, Hydration, Sleep, Stress)
5. Phased 7-Day, 14-Day, and 30-Day nutrient recovery plans
6. Multi-dimensional recommendation scoring (Relevance, Coverage, Compatibility)
"""

from typing import Dict, Any, List, Optional, Tuple
import math
from .knowledge_base import FOOD_KNOWLEDGE_BASE
from ...schemas.recommendation import (
    FoodItemDetail,
    FoodPriorityTierEnum,
    SynergyPairingItem,
    LifestyleInterventionItem,
    RecoveryMilestone,
    RecoveryPlan,
    RecommendationScores
)
from ..safety.pediatric_framework import (
    get_age_bracket,
    is_pediatric,
    get_pediatric_guidelines,
    AGE_0_TO_6M,
    AGE_7_TO_12M,
    AGE_1_TO_3Y,
    AGE_4_TO_8Y,
    AGE_9_TO_13Y,
    AGE_14_TO_18Y,
    AGE_ADULT
)


class PersonalizedRecommendationEngine:
    """
    Evidence-grounded clinical recommendation and nutritional intervention engine.
    """

    SEVERITY_WEIGHTS = {
        "HIGH": 1.40,
        "MODERATE": 1.15,
        "LOW": 0.90
    }

    # Reference Daily Intakes for normalization (18 Target Nutrients)
    NUTRIENT_RDA = {
        "Protein": 56.0,       # grams
        "Vitamin A": 900.0,    # mcg
        "Vitamin B12": 2.4,    # mcg
        "Folate": 400.0,       # mcg
        "Vitamin C": 90.0,     # mg
        "Vitamin D": 600.0,    # IU
        "Vitamin E": 15.0,     # mg
        "Iron": 18.0,          # mg (female default)
        "Calcium": 1000.0,     # mg
        "Zinc": 11.0,          # mg
        "Magnesium": 400.0,    # mg
        "Vitamin B1": 1.2,     # mg
        "Vitamin B2": 1.3,     # mg
        "Vitamin B3": 16.0,    # mg
        "Vitamin B6": 1.7,     # mg
        "Potassium": 3400.0,   # mg
        "Selenium": 55.0,      # mcg
        "Iodine": 150.0        # mcg
    }

    @classmethod
    def filter_foods_by_diet(
        cls,
        food_list: List[Dict[str, Any]],
        dietary_pattern: str,
        restrictions: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Applies strict boolean AND filtering against patient dietary patterns and restrictions.
        Guarantees that ALL dietary constraints and ALL restriction rules are satisfied concurrently.
        Performs dual-layer validation:
        1. Explicit dietary_tags validation
        2. Strict keyword and ingredient disjunction exclusion
        """
        pattern_clean = str(dietary_pattern or "OMNIVORE").upper().strip()
        restrictions_clean = [str(r).upper().replace("-", "_").replace(" ", "_").strip() for r in (restrictions or []) if r]

        # Clinical allergen and food-group keywords
        MEAT_KEYWORDS = [
            "beef", "chicken", "turkey", "pork", "lamb", "veal", "duck", "liver", "steak",
            "bacon", "sausage", "ham", "bison", "venison", "meat"
        ]
        SEAFOOD_KEYWORDS = [
            "salmon", "tuna", "sardine", "sardines", "mackerel", "trout", "cod", "halibut",
            "anchovies", "anchovy", "shrimp", "oyster", "oysters", "clam", "clams", "mussel",
            "mussels", "crab", "lobster", "fish", "herring", "seafood"
        ]
        DAIRY_KEYWORDS = [
            "milk", "cheese", "yogurt", "butter", "whey", "casein", "cream", "ghee",
            "cottage", "ricotta", "parmesan", "cheddar", "mozzarella", "kefir", "dairy"
        ]
        EGG_KEYWORDS = [
            "egg", "eggs", "mayonnaise", "albumin", "yolk"
        ]
        NUT_KEYWORDS = [
            "almond", "walnut", "cashew", "peanut", "pecan", "pistachio", "hazelnut",
            "macadamia", "brazil nut", "pine nut"
        ]
        GLUTEN_KEYWORDS = [
            "wheat", "barley", "rye", "spelt", "kamut", "couscous", "bulgur", "seitan", "semolina", "gluten"
        ]

        filtered = []
        for food in food_list:
            fname = str(food.get("food_name", "")).lower()
            fgroup = str(food.get("food_group", "")).upper()
            tags = {str(t).upper().replace("-", "_").replace(" ", "_") for t in food.get("dietary_tags", [])}

            # -------------------------------------------------------------
            # Layer 1: Dietary Pattern Enforcement
            # -------------------------------------------------------------
            if "VEGAN" in pattern_clean:
                if "VEGAN" not in tags:
                    continue
                if any(k in fname for k in MEAT_KEYWORDS + SEAFOOD_KEYWORDS + DAIRY_KEYWORDS + EGG_KEYWORDS):
                    continue
            elif "VEGETARIAN" in pattern_clean:
                if "VEGETARIAN" not in tags and "VEGAN" not in tags:
                    continue
                if any(k in fname for k in MEAT_KEYWORDS + SEAFOOD_KEYWORDS):
                    continue
            elif "PESCATARIAN" in pattern_clean:
                if any(k in fname for k in MEAT_KEYWORDS):
                    continue

            # -------------------------------------------------------------
            # Layer 2: Specific Dietary Restrictions (Strict AND Logic)
            # -------------------------------------------------------------
            is_violating = False

            for r in restrictions_clean:
                # 1. Meat-Free Restriction
                if "MEAT_FREE" in r or "NO_MEAT" in r:
                    if any(k in fname for k in MEAT_KEYWORDS + SEAFOOD_KEYWORDS):
                        is_violating = True
                        break
                    if "VEGAN" not in tags and "VEGETARIAN" not in tags:
                        is_violating = True
                        break

                # 2. Dairy-Free Restriction
                if "DAIRY_FREE" in r or "NO_DAIRY" in r:
                    if any(k in fname for k in DAIRY_KEYWORDS):
                        is_violating = True
                        break
                    if "DAIRY_FREE" not in tags and "VEGAN" not in tags:
                        is_violating = True
                        break

                # 3. Gluten-Free Restriction
                if "GLUTEN_FREE" in r or "NO_GLUTEN" in r or "CELIAC" in r:
                    if any(k in fname for k in GLUTEN_KEYWORDS):
                        is_violating = True
                        break
                    if "GLUTEN_FREE" not in tags:
                        is_violating = True
                        break

                # 4. Nut-Free Restriction
                if "NUT_FREE" in r or "NO_NUTS" in r:
                    if any(k in fname for k in NUT_KEYWORDS):
                        is_violating = True
                        break

                # 5. Egg-Free Restriction
                if "EGG_FREE" in r or "NO_EGGS" in r:
                    if any(k in fname for k in EGG_KEYWORDS):
                        is_violating = True
                        break

            if not is_violating:
                filtered.append(food)

        return filtered

    @classmethod
    def score_food_item(
        cls,
        food: Dict[str, Any],
        nutrient_name: str,
        risk_level: str,
        probability: float
    ) -> Tuple[float, FoodPriorityTierEnum]:
        """
        Calculates composite recommendation score (0 - 100):
        Score = (Nutrient Density Ratio * 40%) + (Severity & Probability * 30%) + (Bioavailability * 30%)
        """
        rda = cls.NUTRIENT_RDA.get(nutrient_name, 100.0)
        density = food.get("nutrient_density", 0.0)
        density_ratio = min(1.5, density / rda)  # Caps at 150% RDA

        sev_weight = cls.SEVERITY_WEIGHTS.get(risk_level, 1.0)
        prob_factor = min(1.0, max(0.2, probability))
        bioavail = food.get("bioavailability_rating", 0.7)

        raw_score = (
            (density_ratio * 40.0) +
            (sev_weight * prob_factor * 30.0) +
            (bioavail * 30.0)
        )

        score = round(min(100.0, max(25.0, raw_score * 1.1)), 1)

        if score >= 80.0 or risk_level == "HIGH" or (risk_level == "MODERATE" and probability >= 0.85):
            tier = FoodPriorityTierEnum.PRIORITY_1
        elif score >= 65.0 or risk_level == "MODERATE":
            tier = FoodPriorityTierEnum.PRIORITY_2
        else:
            tier = FoodPriorityTierEnum.PRIORITY_3

        return score, tier

    @classmethod
    def generate_food_recommendations(
        cls,
        nutrient_predictions: List[Dict[str, Any]],
        dietary_pattern: str,
        restrictions: List[str]
    ) -> Dict[str, List[FoodItemDetail]]:
        """
        Extracts, filters, scores, and prioritizes foods across all flagged nutrients.
        """
        priority_1: List[FoodItemDetail] = []
        priority_2: List[FoodItemDetail] = []
        priority_3: List[FoodItemDetail] = []

        seen_food_names = set()

        # Sort predictions so HIGH risk nutrients are prioritized first
        sorted_preds = sorted(
            nutrient_predictions,
            key=lambda x: (0 if x.get("risk_level") == "HIGH" else (1 if x.get("risk_level") == "MODERATE" else 2), -x.get("probability", 0.0))
        )

        for pred in sorted_preds:
            nut = pred.get("nutrient", "")
            risk = pred.get("risk_level", "LOW")
            prob = pred.get("probability", 0.5)

            # Skip low risk unless we need fallback foods
            if risk == "LOW" and prob < 0.25:
                continue

            available_foods = FOOD_KNOWLEDGE_BASE.get(nut, [])
            filtered_foods = cls.filter_foods_by_diet(available_foods, dietary_pattern, restrictions)

            for food in filtered_foods:
                name = food["food_name"]
                if name in seen_food_names:
                    continue

                score, tier = cls.score_food_item(food, nut, risk, prob)

                detail = FoodItemDetail(
                    food_name=food["food_name"],
                    food_group=food["food_group"],
                    target_nutrient=nut,
                    serving_size=food["serving_size"],
                    nutrient_density=food["nutrient_density"],
                    unit=food["unit"],
                    bioavailability_rating=food["bioavailability_rating"],
                    dietary_compatibility=food["dietary_tags"],
                    priority_tier=tier,
                    recommendation_score=score,
                    rationale=food["rationale"],
                    preparation_tips=food.get("preparation_tips"),
                    contraindications=food.get("contraindications")
                )

                seen_food_names.add(name)

                if tier == FoodPriorityTierEnum.PRIORITY_1:
                    priority_1.append(detail)
                elif tier == FoodPriorityTierEnum.PRIORITY_2:
                    priority_2.append(detail)
                else:
                    priority_3.append(detail)

        # Ensure priority_1 is populated if any deficiencies were identified and eligible foods exist
        if not priority_1 and priority_2:
            promoted_count = min(3, len(priority_2))
            for _ in range(promoted_count):
                item = priority_2.pop(0)
                item.priority_tier = FoodPriorityTierEnum.PRIORITY_1
                priority_1.append(item)

        # Zero-Recommendation Safeguard: If all tiers are empty (e.g. healthy control with low risk across all targets),
        # populate proactive whole-food maintenance recommendations so patient receives actionable nutrition guidance.
        if not priority_1 and not priority_2 and not priority_3:
            fallback_nuts = [p.get("nutrient") for p in sorted_preds[:4]] if sorted_preds else ["Vitamin D", "Magnesium", "Iron", "Protein"]
            for nut in fallback_nuts:
                available_foods = FOOD_KNOWLEDGE_BASE.get(nut, [])
                filtered_foods = cls.filter_foods_by_diet(available_foods, dietary_pattern, restrictions)
                for food in filtered_foods[:2]:
                    name = food["food_name"]
                    if name in seen_food_names:
                        continue
                    score = 75.0
                    tier = FoodPriorityTierEnum.PRIORITY_2 if len(priority_1) >= 2 else FoodPriorityTierEnum.PRIORITY_1
                    detail = FoodItemDetail(
                        food_name=food["food_name"],
                        food_group=food["food_group"],
                        target_nutrient=nut,
                        serving_size=food["serving_size"],
                        nutrient_density=food["nutrient_density"],
                        unit=food["unit"],
                        bioavailability_rating=food["bioavailability_rating"],
                        dietary_compatibility=food["dietary_tags"],
                        priority_tier=tier,
                        recommendation_score=score,
                        rationale=f"Foundational preventative superfood supporting optimal physiological tissue reserves of {nut}.",
                        preparation_tips=food.get("preparation_tips"),
                        contraindications=food.get("contraindications")
                    )
                    seen_food_names.add(name)
                    if tier == FoodPriorityTierEnum.PRIORITY_1:
                        priority_1.append(detail)
                    else:
                        priority_2.append(detail)

        # Sort within tiers by recommendation_score descending
        priority_1.sort(key=lambda x: x.recommendation_score, reverse=True)
        priority_2.sort(key=lambda x: x.recommendation_score, reverse=True)
        priority_3.sort(key=lambda x: x.recommendation_score, reverse=True)

        return {
            "priority_1": priority_1,
            "priority_2": priority_2,
            "priority_3": priority_3
        }

    @classmethod
    def generate_synergy_pairings(
        cls,
        elevated_nutrients: List[str],
        dietary_pattern: str
    ) -> List[SynergyPairingItem]:
        """
        Identifies and constructs biochemical synergy combinations tailored to flagged deficiencies.
        """
        pairings: List[SynergyPairingItem] = []
        is_vegan = "VEGAN" in dietary_pattern.upper()

        # 1. Iron + Vitamin C Synergy
        if "Iron" in elevated_nutrients or "Vitamin C" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Iron",
                synergistic_nutrient="Vitamin C",
                primary_food="Cooked Lentils or Spinach",
                enhancer_food="Sliced Red Bell Peppers & Fresh Lemon Juice",
                meal_concept="Lentil & Quinoa Salad topped with diced raw bell peppers and a fresh lemon-tahini vinaigrette.",
                biochemical_mechanism="Ascorbic acid donates an electron to reduce ferric iron (Fe3+) into ferrous iron (Fe2+), forming a soluble chelate that dramatically bypasses intestinal phytate inhibition and boosts non-heme absorption by 300-400%.",
                absorption_boost_factor="3-4x absorption increase",
                cautionary_timing="Avoid consuming coffee, black tea, or calcium-rich foods within 90 minutes of this meal to prevent polyphenol/tannin chelation."
            ))

        # 2. Vitamin D + Calcium Synergy
        if "Vitamin D" in elevated_nutrients or "Calcium" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Vitamin D",
                synergistic_nutrient="Calcium",
                primary_food="UV-Exposed Mushrooms or Sockeye Salmon",
                enhancer_food="Calcium-Fortified Plant Milk or Sesame Tahini",
                meal_concept="Warm breakfast porridge prepared with calcium-fortified plant milk, topped with toasted sesame seeds, followed by sauteed UV-exposed portobello mushrooms.",
                biochemical_mechanism="Activated Vitamin D (1,25(OH)2D) binds to the nuclear VDR receptor, stimulating transcription of the calcium-binding enterocyte transport protein Calbindin-D9k, facilitating active transcellular calcium uptake in the duodenum.",
                absorption_boost_factor="2-3x calcium absorption efficiency",
                cautionary_timing="Ensure adequate dietary fat with this meal; calciferol requires micelle formation for lymphatic absorption."
            ))

        # 3. Magnesium + Vitamin D Synergy
        if "Magnesium" in elevated_nutrients or "Vitamin D" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Vitamin D",
                synergistic_nutrient="Magnesium",
                primary_food="UV-Exposed Mushrooms or Sardines",
                enhancer_food="Raw Pumpkin Seeds (Pepitas) or Almonds",
                meal_concept="Snack on a quarter cup of raw pumpkin seeds alongside your Vitamin D rich meal or outdoor sun exposure.",
                biochemical_mechanism="Magnesium serves as an essential enzymatic cofactor for hepatic 25-hydroxylase (CYP2R1) and renal 1-alpha-hydroxylase (CYP27B1). Inadequate magnesium traps Vitamin D in its inactive storage form and precipitates refractory hypocalcemia.",
                absorption_boost_factor="Enzymatic cofactor activation",
                cautionary_timing="Avoid taking high-dose oral magnesium with high-dose calcium at the exact same moment to prevent divalent cation competition."
            ))

        # 4. Vitamin B12 + Folate Synergy
        if "Vitamin B12" in elevated_nutrients or "Folate" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Vitamin B12",
                synergistic_nutrient="Folate",
                primary_food="Fortified Nutritional Yeast or Salmon",
                enhancer_food="Steamed Asparagus or Baby Spinach",
                meal_concept="Steamed asparagus and baby greens generously dusted with fortified nutritional yeast.",
                biochemical_mechanism="Methionine synthase requires both methylcobalamin (B12) and 5-methyltetrahydrofolate (Folate) to remethylate toxic homocysteine to methionine. Without B12, cellular folate becomes trapped in the 5-MTHF form ('folate trap'), arresting DNA synthesis.",
                absorption_boost_factor="Cellular methylation synergy",
                cautionary_timing="Never supplement high-dose folic acid in isolated B12 deficiency without medical supervision, as it can mask progressive subacute combined spinal cord degeneration."
            ))

        # 5. Zinc + Iron Competitive Timing Advisory
        if "Zinc" in elevated_nutrients and "Iron" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Zinc",
                synergistic_nutrient="Iron",
                primary_food="Pumpkin Seeds / Cashews (Zinc Source)",
                enhancer_food="Lentils / Spinach (Iron Source)",
                meal_concept="Consume your primary Iron-dense meal at midday (lunch) and your Zinc-dense meal in the evening (dinner).",
                biochemical_mechanism="Iron and zinc compete directly for the divalent metal transporter-1 (DMT-1) enterocyte pathway. When consumed simultaneously at high ratios, iron competitively blunts zinc absorption.",
                absorption_boost_factor="Temporal separation strategy",
                cautionary_timing="Space high-dose iron and zinc foods or supplements by at least 2 to 3 hours."
            ))

        # 6. Iodine + Selenium Synergy (Thyroid Axis)
        if "Iodine" in elevated_nutrients or "Selenium" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Iodine",
                synergistic_nutrient="Selenium",
                primary_food="Wakame / Nori Seaweed or Iodized Salt",
                enhancer_food="Brazil Nuts (1-2 nuts) or Tuna",
                meal_concept="A bowl of miso soup with seaweed garnished with sliced shiitake mushrooms, accompanied by a single raw Brazil nut.",
                biochemical_mechanism="Iodine provides the direct substrate for thyroid hormone T4, while selenium-dependent iodothyronine deiodinases convert T4 into biologically active T3. Co-pairing ensures physiological thyroid conversion and prevents oxidative injury to thyrocytes.",
                absorption_boost_factor="Thyroid conversion & enzymatic synergy",
                cautionary_timing="Limit Brazil nuts to 1-2 daily to remain well under the 400 mcg selenium upper limit."
            ))

        # 7. Potassium + Magnesium Synergy (Cellular Electrolyte Equilibrium)
        if "Potassium" in elevated_nutrients or "Magnesium" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Potassium",
                synergistic_nutrient="Magnesium",
                primary_food="Baked Potato with Skin or Avocado",
                enhancer_food="Steamed Swiss Chard & Raw Pumpkin Seeds",
                meal_concept="Baked sweet potato split open, stuffed with sautéed Swiss chard, avocado slices, and crushed raw pumpkin seeds.",
                biochemical_mechanism="Magnesium is an obligate cofactor for Na+/K+-ATPase and stabilizes renal outer medullary potassium (ROMK) channels. Adequate magnesium prevents renal potassium wasting and optimizes intracellular electrolyte polarity.",
                absorption_boost_factor="Electrolyte retention & membrane potential synergy",
                cautionary_timing="Caution with supplemental potassium in patients with severe chronic renal insufficiency."
            ))

        # 8. Vitamin B1 + Magnesium Synergy
        if "Vitamin B1" in elevated_nutrients or "Magnesium" in elevated_nutrients:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Vitamin B1",
                synergistic_nutrient="Magnesium",
                primary_food="Cooked Brown Rice or Lentils",
                enhancer_food="Shelled Sunflower Seeds & Dark Chocolate",
                meal_concept="Warm brown rice and lentil pilaf topped with toasted sunflower seeds, followed by a square of 85% dark chocolate.",
                biochemical_mechanism="Thiamine pyrophosphokinase, the enzyme converting dietary thiamine to its metabolically active coenzyme form (thiamine pyrophosphate / TPP), is strictly magnesium-dependent.",
                absorption_boost_factor="Enzymatic phosphorylation synergy",
                cautionary_timing="Ensure adequate magnesium status prior to or concurrently with high-dose thiamine therapy."
            ))

        if not pairings:
            pairings.append(SynergyPairingItem(
                primary_nutrient="Vitamin D",
                synergistic_nutrient="Magnesium",
                primary_food="UV-Exposed Mushrooms or Sardines",
                enhancer_food="Raw Pumpkin Seeds or Almonds",
                meal_concept="Foundational preventative pairing supporting enzymatic activation of Vitamin D.",
                biochemical_mechanism="Magnesium acts as an essential enzymatic cofactor for hepatic 25-hydroxylase and renal 1-alpha-hydroxylase.",
                absorption_boost_factor="Enzymatic cofactor activation",
                cautionary_timing="Avoid taking high-dose oral magnesium with high-dose calcium concurrently."
            ))
            pairings.append(SynergyPairingItem(
                primary_nutrient="Iron",
                synergistic_nutrient="Vitamin C",
                primary_food="Whole Lentils or Dark Leafy Greens",
                enhancer_food="Citrus or Fresh Bell Peppers",
                meal_concept="Whole-food salad with leafy greens and lemon vinaigrette to optimize natural iron bioavailability.",
                biochemical_mechanism="Ascorbic acid maintains dietary iron in the absorbable ferrous state.",
                absorption_boost_factor="Bioavailability enhancement",
                cautionary_timing="Separate coffee or tea by 60 minutes from major meals."
            ))

        return pairings

    @classmethod
    def generate_lifestyle_interventions(
        cls,
        nutrient_predictions: List[Dict[str, Any]],
        patient_data: Dict[str, Any]
    ) -> List[LifestyleInterventionItem]:
        """
        Synthesizes practical, non-dietary lifestyle protocols based on deficiencies and screening data.
        """
        interventions: List[LifestyleInterventionItem] = []

        elevated_nutrients = [
            p.get("nutrient", p.get("target_name", ""))
            for p in nutrient_predictions
            if str(p.get("risk_tier", p.get("risk_level", ""))).upper() in ["HIGH", "MODERATE"]
        ]

        # 1. Sunlight & Phototherapy Protocol
        if "Vitamin D" in elevated_nutrients or "Calcium" in elevated_nutrients:
            interventions.append(LifestyleInterventionItem(
                category="SUNLIGHT",
                recommendation="Targeted Midday Solar UVB Photolysis",
                daily_target="15–25 minutes midday sunlight (between 10 AM and 2 PM)",
                clinical_rationale="Solar UVB radiation (290-315 nm) triggers photolysis of cutaneous 7-dehydrocholesterol to pre-vitamin D3. Expose forearms, hands, and lower legs without sunscreen for the first 15 minutes.",
                evidence_reference="Endocrine Society Clinical Practice Guidelines: Vitamin D Deficiency"
            ))

        # 2. Hydration Strategy
        weight_kg = float(patient_data.get("weight_kg", 65.0))
        target_liters = round(max(2.0, (weight_kg * 0.035)), 1)
        interventions.append(LifestyleInterventionItem(
            category="HYDRATION",
            recommendation="Cellular Electrolyte & Fluid Replenishment",
            daily_target=f"{target_liters} Liters of filtered water per day",
            clinical_rationale="Adequate hydration sustains renal clearance, prevents secondary hyperaldosteronism, and facilitates passive paracellular mineral absorption throughout the small intestine.",
            evidence_reference="European Journal of Clinical Nutrition: Water, Hydration and Health"
        ))

        # 3. Physical Activity & Musculoskeletal Loading
        act_lvl = str(patient_data.get("activity_level", "")).upper()
        if any(n in elevated_nutrients for n in ["Calcium", "Protein", "Vitamin D", "Potassium", "Iron"]) or act_lvl == "SEDENTARY":
            interventions.append(LifestyleInterventionItem(
                category="PHYSICAL_ACTIVITY",
                recommendation="Progressive Resistance & Mechanical Skeletal Loading",
                daily_target="3 sessions per week (30-45 min) of resistance or weight-bearing exercise",
                clinical_rationale="Mechanical strain activates the Wnt/beta-catenin pathway, stimulating osteoblast mineral deposition, potassium-sparing cellular uptake, and mTOR muscle protein synthesis.",
                evidence_reference="Journal of Bone and Mineral Research: Physical Exercise and Bone Mineral Density"
            ))

        # 4. Circadian Sleep Architecture
        sleep_hrs = float(patient_data.get("sleep_hours_per_night", 7.5))
        if any(n in elevated_nutrients for n in ["Magnesium", "Vitamin B12", "Vitamin B1", "Vitamin B6", "Potassium"]) or sleep_hrs < 7.0:
            interventions.append(LifestyleInterventionItem(
                category="SLEEP",
                recommendation="Circadian Rhythm Optimization & Nocturnal Sleep Hygiene",
                daily_target="7.5–8.5 hours of uninterrupted sleep in a dark, cool room (<67F / 19C)",
                clinical_rationale="Deep slow-wave sleep is the primary physiological window for cellular repair, growth hormone release, and central nervous system remyelination.",
                evidence_reference="Sleep Medicine Reviews: Micronutrients and Sleep Quality"
            ))

        # 5. Neuroendocrine Stress Mitigation
        stress_lvl = int(patient_data.get("stress_level", 5))
        if stress_lvl >= 6 or "Magnesium" in elevated_nutrients:
            interventions.append(LifestyleInterventionItem(
                category="STRESS",
                recommendation="Autonomic Down-Regulation & Cortisol Attenuation",
                daily_target="10–15 minutes daily of diaphragmatic breathing (4-7-8) or progressive relaxation",
                clinical_rationale="Sustained sympathetic activation triggers hypercortisolemia, which causes marked hypermagnesiuria (renal magnesium wasting) and gastrointestinal hypochlorhydria.",
                evidence_reference="Journal of the American College of Nutrition: Stress and Magnesium Metabolism"
            ))

        return interventions

    @classmethod
    def generate_recovery_plan(
        cls,
        elevated_nutrients: List[str],
        top_foods: List[FoodItemDetail],
        lifestyle_items: List[LifestyleInterventionItem]
    ) -> RecoveryPlan:
        """
        Creates a structured, milestone-based 7-Day, 14-Day, and 30-Day recovery roadmap.
        """
        nuts_str = ", ".join(elevated_nutrients[:4]) if elevated_nutrients else "Micronutrient Homeostasis"
        food_names = [f.food_name for f in top_foods[:5]]

        # Phase 1: Days 1 - 7
        milestone_7 = RecoveryMilestone(
            day_range="Days 1-7",
            phase_title="Acute Nutritional Stabilization & Antinutrient Elimination",
            clinical_focus="Arrest rapid micronutrient depletion and eliminate dietary inhibitors (excess phytates, tannins, ultra-processed foods).",
            primary_dietary_strategy=f"Introduce at least two Priority 1 staple foods daily (e.g. {', '.join(food_names[:2])}). Begin soaking legumes and seeds for 4-6 hours prior to cooking.",
            daily_action_checklist=[
                f"Incorporate {food_names[0] if food_names else 'Priority 1 Superfood'} into lunch or dinner",
                "Eliminate black tea and coffee consumption within 90 minutes of major meals",
                "Initiate daily 15-20 min sunlight exposure target or fortified baseline supplementation",
                "Ensure minimum daily fluid intake target is met before 7 PM"
            ],
            key_foods_to_emphasize=food_names[:3]
        )

        # Phase 2: Days 8 - 14
        milestone_14 = RecoveryMilestone(
            day_range="Days 8-14",
            phase_title="Cellular Replenishment & Synergistic Bioavailability Pairing",
            clinical_focus="Activate biochemical synergies (e.g. non-heme Iron + Vitamin C, Vitamin D + Calcium) to accelerate cellular storage replenishment.",
            primary_dietary_strategy=f"Pair high-density nutrient foods with designated bio-enhancers (e.g. citrus/peppers with iron, healthy fats with fat-soluble vitamins). Introduce {food_names[2] if len(food_names) > 2 else 'nutrient-dense rotation'}.",
            daily_action_checklist=[
                "Implement synergistic meal pairing at least once daily (e.g. Lentils + Bell Pepper)",
                "Introduce 2 sessions of resistance or weight-bearing physical activity",
                "Add nutrient-dense functional snacks (e.g. raw pumpkin seeds, almonds, or tahini)",
                "Evaluate subjective symptom shift (energy levels, muscle cramp frequency)"
            ],
            key_foods_to_emphasize=food_names[1:4] if len(food_names) >= 4 else food_names
        )

        # Phase 3: Days 15 - 30
        milestone_30 = RecoveryMilestone(
            day_range="Days 15-30",
            phase_title="Sustained Homeostasis & Habit Consolidation",
            clinical_focus="Consolidate long-term dietary routines, re-establish physiological tissue reserves, and prepare for follow-up screening.",
            primary_dietary_strategy="Transition from acute high-density intervention to sustainable daily diverse whole-food rotation across all 5 clinical food groups.",
            daily_action_checklist=[
                "Maintain broad variety of colorful produce (>4 diverse colors daily)",
                "Sustain consistent sleep hygiene and stress mitigation protocols",
                "Schedule laboratory confirmation panels if baseline risk was categorized as HIGH",
                "Complete repeat AI nutritional screening at Day 30 to quantify risk score improvement"
            ],
            key_foods_to_emphasize=food_names[:5]
        )

        return RecoveryPlan(
            plan_title=f"Targeted Nutritional Recovery Plan: {nuts_str}",
            target_deficiencies=elevated_nutrients,
            phase_7_day=milestone_7,
            phase_14_day=milestone_14,
            phase_30_day=milestone_30
        )

    @classmethod
    def calculate_recommendation_scores(
        cls,
        nutrient_predictions: List[Dict[str, Any]],
        recommended_foods: List[FoodItemDetail],
        restrictions: List[str]
    ) -> RecommendationScores:
        """
        Computes 3 distinct score dimensions:
        1. Relevance Score: How well top foods address high-severity flagged nutrients.
        2. Nutrient Coverage Score: Proportion of target nutrients receiving strong food options.
        3. Diet Compatibility Score: Strictness of restriction compliance (100 if 0 violations).
        """
        elevated = [
            p.get("nutrient", p.get("target_name", ""))
            for p in nutrient_predictions
            if str(p.get("risk_tier", p.get("risk_level", ""))).upper() in ["HIGH", "MODERATE"]
        ]
        if not elevated:
            elevated = [p.get("nutrient", p.get("target_name", "")) for p in nutrient_predictions[:3]]

        # 1. Relevance Score
        addressed_nutrients = {f.target_nutrient for f in recommended_foods if f.priority_tier == FoodPriorityTierEnum.PRIORITY_1}
        relevance_ratio = len(addressed_nutrients.intersection(set(elevated))) / max(1, len(elevated))
        relevance_score = round(min(100.0, max(50.0, (relevance_ratio * 70.0) + 30.0)), 1)

        # 2. Nutrient Coverage Score
        all_covered = {f.target_nutrient for f in recommended_foods}
        coverage_ratio = len(all_covered.intersection(set(elevated))) / max(1, len(elevated))
        coverage_score = round(min(100.0, max(40.0, coverage_ratio * 100.0)), 1)

        # 3. Diet Compatibility Score (100% since our filtering strictly excludes violations)
        diet_compat_score = 100.0

        # Weighted Overall
        overall = round((0.40 * relevance_score) + (0.35 * coverage_score) + (0.25 * diet_compat_score), 1)

        return RecommendationScores(
            relevance_score=relevance_score,
            nutrient_coverage_score=coverage_score,
            diet_compatibility_score=diet_compat_score,
            overall_recommendation_score=overall
        )

    @classmethod
    def generate_supplement_recommendations(
        cls,
        elevated_nutrients: List[str],
        dietary_pattern: str,
        patient_intake: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes evidence-based micro-supplement prescriptions strictly within age-specific Upper Tolerable Limits (UL).
        Supports pediatric brackets (0-6m, 7-12m, 1-3y, 4-8y, 9-13y, 14-18y) and clinical contraindications.
        """
        supplements = []
        patient_intake = patient_intake or {}
        age_years = float(patient_intake.get("age", 30.0) or patient_intake.get("demo_age_years", 30.0) or 30.0)
        bracket = get_age_bracket(age_years)
        patient_is_pediatric = is_pediatric(age_years)

        is_pregnant = bool(patient_intake.get("is_pregnant", False) or patient_intake.get("demo_is_pregnant", 0) == 1)
        conditions_raw = []
        if patient_intake.get("conditions"):
            conditions_raw.extend(patient_intake["conditions"] if isinstance(patient_intake["conditions"], list) else [patient_intake["conditions"]])
        if patient_intake.get("medical_conditions"):
            conditions_raw.extend(patient_intake["medical_conditions"] if isinstance(patient_intake["medical_conditions"], list) else [patient_intake["medical_conditions"]])
        if patient_intake.get("medical_history"):
            for mh in patient_intake["medical_history"]:
                if isinstance(mh, dict):
                    if mh.get("is_active", True) is not False:
                        conditions_raw.append(mh.get("condition_name", ""))
                elif isinstance(mh, str):
                    conditions_raw.append(mh)
        conditions = [str(c).strip().upper() for c in conditions_raw if c]
        if any("PREGNAN" in c for c in conditions):
            is_pregnant = True

        medications_raw = []
        if patient_intake.get("medications"):
            medications_raw.extend(patient_intake["medications"] if isinstance(patient_intake["medications"], list) else [patient_intake["medications"]])
        medications = [str(m).strip().upper() for m in medications_raw if m]

        is_ckd = any("KIDNEY" in c or "CKD" in c or "RENAL" in c for c in conditions)
        is_hemochromatosis = any("HEMOCHROMATOSIS" in c or "IRON OVERLOAD" in c for c in conditions)

        # Robust smoker status detection from lifestyle_factors, is_smoker flag, and intake fields
        lifestyle_factors = patient_intake.get("lifestyle_factors", {})
        smoking_val = str(
            patient_intake.get("smoking_status", "") or
            (lifestyle_factors.get("smoking_status", "") if isinstance(lifestyle_factors, dict) else "") or
            patient_intake.get("lifestyle", "")
        ).upper()
        is_smoker = bool(
            patient_intake.get("is_smoker", False) or
            "CURRENT" in smoking_val or
            "SMOK" in smoking_val or
            any("SMOK" in c for c in conditions)
        )
        is_warfarin = any("WARFARIN" in m or "COUMADIN" in m for m in medications)

        # ----------------------------------------------------
        # PEDIATRIC SUPPLEMENT CATALOG
        # ----------------------------------------------------
        if patient_is_pediatric:
            for nut in elevated_nutrients:
                if nut == "Vitamin D":
                    if bracket in [AGE_0_TO_6M, AGE_7_TO_12M]:
                        supplements.append({
                            "item_name": "Cholecalciferol (D3) Pediatric Oral Liquid Drops",
                            "target_nutrient": "Vitamin D",
                            "dosage": "400 IU/day (10 mcg)",
                            "frequency": "Daily single drop directly on nipple or into bottle feed",
                            "clinical_rationale": f"AAP-recommended infant prophylaxis; strictly below infant UL (1,000-1,500 IU).",
                            "evidence_reference": "Wagner CL, Greer FR; AAP Section on Breastfeeding. Pediatrics 2008; 122(5):1142-1152.",
                            "contraindications": "Infantile hypercalcemia, Williams syndrome."
                        })
                    elif bracket == AGE_1_TO_3Y:
                        supplements.append({
                            "item_name": "Cholecalciferol (D3) Toddler Chewable / Drops",
                            "target_nutrient": "Vitamin D",
                            "dosage": "600 IU/day (15 mcg)",
                            "frequency": "Daily with breakfast or snack",
                            "clinical_rationale": "IOM RDA compliant restoration; strictly complies with 2,500 IU toddler UL.",
                            "evidence_reference": "Institute of Medicine (IOM) Dietary Reference Intakes for Calcium and Vitamin D.",
                            "contraindications": "Hypercalcemia."
                        })
                    elif bracket in [AGE_4_TO_8Y, AGE_9_TO_13Y]:
                        supplements.append({
                            "item_name": "Cholecalciferol (D3) Pediatric Chewable Tablet",
                            "target_nutrient": "Vitamin D",
                            "dosage": "600 - 1000 IU/day (15 - 25 mcg)",
                            "frequency": "Daily chewable with breakfast",
                            "clinical_rationale": f"Pediatric skeletal mineralization; safely within {bracket} UL (3,000-4,000 IU).",
                            "evidence_reference": "Endocrine Society Clinical Practice Guideline for Pediatric Vitamin D.",
                            "contraindications": "Hypercalcemia, granulomatous disorders."
                        })
                    else:  # 14-18y
                        supplements.append({
                            "item_name": "Cholecalciferol (D3) Adolescent Formulation",
                            "target_nutrient": "Vitamin D",
                            "dosage": "1000 - 2000 IU/day (25 - 50 mcg)",
                            "frequency": "Daily with fat-containing meal",
                            "clinical_rationale": "Restores adolescent bone mineral accrual window without approaching 4,000 IU UL.",
                            "evidence_reference": "Endocrine Society Clinical Practice Guidelines.",
                            "contraindications": "Hypercalcemia."
                        })

                elif nut == "Vitamin B12":
                    if bracket in [AGE_0_TO_6M, AGE_7_TO_12M]:
                        supplements.append({
                            "item_name": "Pediatric Methylcobalamin Oral Liquid Drops",
                            "target_nutrient": "Vitamin B12",
                            "dosage": "0.5 - 1.0 mcg/day",
                            "frequency": "Daily oral drop with feed",
                            "clinical_rationale": "Safe physiological infant cobalamin repletion for breastfed infants of plant-based mothers.",
                            "evidence_reference": "AAP Committee on Nutrition: Pediatric Nutrition.",
                            "contraindications": "Cobalt allergy."
                        })
                    elif bracket in [AGE_1_TO_3Y, AGE_4_TO_8Y]:
                        supplements.append({
                            "item_name": "Pediatric Methylcobalamin Chewable",
                            "target_nutrient": "Vitamin B12",
                            "dosage": "2 - 5 mcg/day",
                            "frequency": "Daily chewable tablet",
                            "clinical_rationale": "Supports neurological development and erythropoiesis at toddler/child physiological levels.",
                            "evidence_reference": "IOM Dietary Reference Intakes: Vitamin B12.",
                            "contraindications": "Cobalt allergy."
                        })
                    else:
                        supplements.append({
                            "item_name": "Methylcobalamin Sublingual Lozenge",
                            "target_nutrient": "Vitamin B12",
                            "dosage": "50 - 250 mcg/day",
                            "frequency": "Daily sublingual tablet dissolved before meal",
                            "clinical_rationale": "Clears elevated homocysteine and restores serum cobalamin in adolescents.",
                            "evidence_reference": "Carmel R. Blood 2008; 112(6):2214-2221.",
                            "contraindications": "Cobalt allergy."
                        })

                elif nut == "Iron":
                    if is_hemochromatosis:
                        continue
                    if bracket in [AGE_0_TO_6M, AGE_7_TO_12M]:
                        supplements.append({
                            "item_name": "Pediatric Liquid Ferrous Sulfate / Bisglycinate Drops",
                            "target_nutrient": "Iron",
                            "dosage": "5 - 10 mg/day elemental iron under pediatrician guidance",
                            "frequency": "Single daily morning drop between feeds",
                            "clinical_rationale": "Safely manages infant iron deficit while remaining well below the 40 mg pediatric UL.",
                            "evidence_reference": "Baker RD, Greer FR; AAP Committee on Nutrition. Pediatrics 2010; 126(5):1040-1050.",
                            "contraindications": "Hemochromatosis, active gastroenteritis, hemolytic anemia."
                        })
                    elif bracket in [AGE_1_TO_3Y, AGE_4_TO_8Y]:
                        supplements.append({
                            "item_name": "Pediatric Gentle Iron Bisglycinate Drops / Chewable",
                            "target_nutrient": "Iron",
                            "dosage": "7 - 12 mg elemental iron",
                            "frequency": "Every other morning with Vitamin C / citrus juice",
                            "clinical_rationale": "Protects against toddler microcytic anemia with high enterocyte tolerance.",
                            "evidence_reference": "WHO Guideline on Daily Iron Supplementation in Children.",
                            "contraindications": "Hemochromatosis, peptic ulceration."
                        })
                    else:
                        supplements.append({
                            "item_name": "Chelated Ferrous Bisglycinate (Gentle Iron)",
                            "target_nutrient": "Iron",
                            "dosage": "15 - 25 mg elemental iron",
                            "frequency": "Every other morning on an empty stomach with Vitamin C",
                            "clinical_rationale": "Alternate-day dosing suppresses hepcidin spike in menstruating and growing adolescents.",
                            "evidence_reference": "Stoffel NU et al. Lancet Haematol 2017; 4(11):e524-e533.",
                            "contraindications": "Hemochromatosis, active inflammatory bowel disease flare."
                        })

                elif nut == "Calcium":
                    if bracket in [AGE_0_TO_6M, AGE_7_TO_12M, AGE_1_TO_3Y]:
                        supplements.append({
                            "item_name": "Dietary Calcium Optimization (Whole-Food Priority)",
                            "target_nutrient": "Calcium",
                            "dosage": "Dietary repletion via breast milk, fortified infant formula, or whole yogurt",
                            "frequency": "Daily whole-food meals",
                            "clinical_rationale": "Oral calcium pills avoided in infants/toddlers to prevent divalent cation competitive interference and hypercalciuria.",
                            "evidence_reference": "AAP Committee on Nutrition: Calcium Requirements in Pediatric Individuals.",
                            "contraindications": "Hypercalcemia."
                        })
                    else:
                        supplements.append({
                            "item_name": "Pediatric Calcium Citrate Chewable with D3",
                            "target_nutrient": "Calcium",
                            "dosage": "250 - 500 mg elemental calcium",
                            "frequency": "Daily with meal (spaced >= 2 hours from iron)",
                            "clinical_rationale": "Citrate salt provides high pediatric bioavailability and supports skeletal growth velocity.",
                            "evidence_reference": "NIH ODS Calcium Fact Sheet for Health Professionals.",
                            "contraindications": "Nephrolithiasis, hypercalcemia."
                        })

                elif nut == "Magnesium":
                    if bracket in [AGE_0_TO_6M, AGE_7_TO_12M, AGE_1_TO_3Y, AGE_4_TO_8Y]:
                        supplements.append({
                            "item_name": "Dietary Magnesium Whole-Food Matrix (Zero Supplemental Salts)",
                            "target_nutrient": "Magnesium",
                            "dosage": "Dietary beans, lentils, avocado, banana, and pumpkin seed butter",
                            "frequency": "Daily whole-food meals",
                            "clinical_rationale": "Supplemental magnesium salts induce osmotic diarrhea in young children; UL strictly limits supplemental forms (65-110 mg).",
                            "evidence_reference": "IOM Dietary Reference Intakes: Magnesium.",
                            "contraindications": "Renal insufficiency."
                        })
                    else:
                        supplements.append({
                            "item_name": "Magnesium Bisglycinate Chelate",
                            "target_nutrient": "Magnesium",
                            "dosage": "100 - 200 mg elemental magnesium",
                            "frequency": "Nightly 30 minutes before sleep",
                            "clinical_rationale": "Supports neuromuscular excitability and enzymatic activation of 25-hydroxyvitamin D.",
                            "evidence_reference": "NIH ODS Magnesium Guidelines.",
                            "contraindications": "Renal failure, heart block."
                        })

                elif nut == "Zinc":
                    if bracket in [AGE_0_TO_6M, AGE_7_TO_12M]:
                        supplements.append({
                            "item_name": "Pediatric Zinc Sulfate Oral Solution",
                            "target_nutrient": "Zinc",
                            "dosage": "2 - 3 mg elemental zinc",
                            "frequency": "Daily oral drop with feeding",
                            "clinical_rationale": "Reverses acute linear growth stunting and reinforces infant gut barrier integrity.",
                            "evidence_reference": "WHO/UNICEF Joint Statement: Clinical Management of Acute Diarrhea and Zinc.",
                            "contraindications": "Severe zinc hypersensitivity."
                        })
                    elif bracket in [AGE_1_TO_3Y, AGE_4_TO_8Y]:
                        supplements.append({
                            "item_name": "Pediatric Zinc Gluconate Chewable",
                            "target_nutrient": "Zinc",
                            "dosage": "3 - 6 mg elemental zinc",
                            "frequency": "Daily with meal",
                            "clinical_rationale": "Complies with pediatric UL (7-12 mg) while enhancing mucosal immunity.",
                            "evidence_reference": "Prasad AS. Mol Med 2008; 14(5-6):353-357.",
                            "contraindications": "Concomitant tetracycline antibiotic ingestion."
                        })
                    else:
                        supplements.append({
                            "item_name": "Zinc Bisglycinate Chelate",
                            "target_nutrient": "Zinc",
                            "dosage": "10 - 15 mg elemental zinc",
                            "frequency": "Daily with food",
                            "clinical_rationale": "High bioavailability chelate supporting pubertal endocrine synthesis.",
                            "evidence_reference": "NIH ODS Zinc Guidelines.",
                            "contraindications": "Copper deficiency (supplement copper if continued > 60 days)."
                        })

                elif nut == "Folate":
                    ped_f = get_pediatric_guidelines(bracket, "Folate")
                    rda_val = ped_f.rda if ped_f else 200.0
                    supplements.append({
                        "item_name": "Active L-5-Methyltetrahydrofolate (L-5-MTHF) Pediatric",
                        "target_nutrient": "Folate",
                        "dosage": f"{int(rda_val)} - {int(rda_val * 1.5)} mcg DFE/day",
                        "frequency": "Daily morning dose with food",
                        "clinical_rationale": "Naturally active folate form bypassing metabolic bottlenecks without risk of unmetabolized synthetic folic acid.",
                        "evidence_reference": "AAP Committee on Nutrition: Pediatric Folate Requirements.",
                        "contraindications": "Undiagnosed Vitamin B12 deficiency."
                    })

                elif nut == "Vitamin A":
                    supplements.append({
                        "item_name": "Provitamin A Carotenoid Pure Drops (Zero Preformed Retinol)",
                        "target_nutrient": "Vitamin A",
                        "dosage": "300 - 600 mcg RAE carotenoids",
                        "frequency": "Daily with lipid-containing feed",
                        "clinical_rationale": "Safely cleared through mucosal physiological cleavage without hepatotoxicity or intracranial hypertension risk.",
                        "evidence_reference": "WHO Vitamin A Supplementation in Infants and Children Guidelines.",
                        "contraindications": "Preformed retinyl palmitate supplements."
                    })

                elif nut == "Protein":
                    ped_p = get_pediatric_guidelines(bracket, "Protein")
                    rda_p = ped_p.rda if ped_p else 19.0
                    supplements.append({
                        "item_name": "Whole-Food Balanced Pediatric Protein Protocol",
                        "target_nutrient": "Protein",
                        "dosage": f"{int(rda_p)} g/day from diverse legumes, dairy/soy, and whole grains",
                        "frequency": "Evenly distributed across 3 meals and snacks",
                        "clinical_rationale": "High-dose synthetic protein powders contraindicated in pediatric patients to prevent hyperosmolar renal solute loading.",
                        "evidence_reference": "AAP Pediatric Nutrition Handbook: Protein and Amino Acid Metabolism.",
                        "contraindications": "Inborn errors of amino acid metabolism (e.g. PKU, MSUD)."
                    })

        # ----------------------------------------------------
        # ADULT SUPPLEMENT CATALOG (with Smoker, CKD & Anticoagulant guards)
        # ----------------------------------------------------
        else:
            SUPPLEMENT_CATALOG = {
                "Vitamin D": {
                    "item_name": ("Cholecalciferol (D3) without K2 (Anticoagulant-Safe)" if is_warfarin else "Cholecalciferol (D3) in Olive Oil Matrix with K2 (MK-7)"),
                    "target_nutrient": "Vitamin D",
                    "dosage": "2000 - 4000 IU/day (50 - 100 mcg)",
                    "frequency": "Daily with largest fat-containing meal",
                    "clinical_rationale": ("Restores 25(OH)D while strictly avoiding Vitamin K interactions in anticoagulated patient." if is_warfarin else "Restores serum 25(OH)D to optimal clinical sufficiency window (35-50 ng/mL). K2 guides calcium to bone matrix."),
                    "evidence_reference": "Holick MF. N Engl J Med 2007; 357:266-281. Endocrine Society Clinical Practice Guidelines.",
                    "contraindications": "Hypercalcemia, sarcoidosis, primary hyperparathyroidism."
                },
                "Vitamin B12": {
                    "item_name": "Sublingual Methylcobalamin & Adenosylcobalamin",
                    "target_nutrient": "Vitamin B12",
                    "dosage": "1000 mcg/day sublingual lozenge",
                    "frequency": "Daily dissolved under tongue before breakfast",
                    "clinical_rationale": "Bypasses gastric intrinsic factor limitation via 1-2% passive oral mucosal diffusion. Clears methylmalonic acid.",
                    "evidence_reference": "Carmel R. Blood 2008; 112(6):2214-2221. NIH ODS Vitamin B12 Fact Sheet.",
                    "contraindications": "Cobalt sensitivity, Leber's hereditary optic neuropathy."
                },
                "Iron": {
                    "item_name": "Chelated Ferrous Bisglycinate (Gentle Iron)",
                    "target_nutrient": "Iron",
                    "dosage": "25 - 45 mg elemental iron co-ingested with 100mg Vitamin C",
                    "frequency": "Every other morning on an empty stomach or with a light non-dairy meal",
                    "clinical_rationale": "Amino acid chelate reduces gastric irritation and constipation by 4-fold compared to ferrous sulfate. Alternate-day dosing optimizes hepcidin dynamics.",
                    "evidence_reference": "Stoffel NU et al. Lancet Haematol 2017; 4(11):e524-e533. WHO Guideline on Iron Supplementation.",
                    "contraindications": "Hemochromatosis, active peptic ulcer disease, thalassemia without iron deficiency."
                },
                "Calcium": {
                    "item_name": "Calcium Citrate with Magnesium & D3",
                    "target_nutrient": "Calcium",
                    "dosage": "400 - 500 mg elemental calcium BID (total 800-1000 mg/day)",
                    "frequency": "Twice daily with meals (spaced >= 2 hours from iron supplements)",
                    "clinical_rationale": "Citrate salt does not depend on gastric acid for absorption. Spacing prevents divalent cation competitive antagonism with iron and zinc.",
                    "evidence_reference": "Straub DA. Nutr Clin Pract 2007; 22(3):286-296. NIH ODS Calcium Fact Sheet.",
                    "contraindications": "Hypercalcemia, active nephrolithiasis (calcium oxalate stones), hypercalciuria."
                },
                "Magnesium": {
                    "item_name": "Magnesium Bisglycinate Chelate",
                    "target_nutrient": "Magnesium",
                    "dosage": "200 - 300 mg elemental magnesium",
                    "frequency": "Nightly 30-45 minutes before sleep",
                    "clinical_rationale": "Glycine carrier crosses blood-brain barrier and exerts GABAergic tone. Acts as essential enzymatic cofactor for Vitamin D 25-hydroxylase.",
                    "evidence_reference": "Abbasi B et al. J Res Med Sci 2012; 17(12):1161-1169. NIH ODS Magnesium Guidelines.",
                    "contraindications": "Severe renal failure (GFR < 30 mL/min/1.73m2), heart block."
                },
                "Zinc": {
                    "item_name": "Zinc Picolinate or Bisglycinate",
                    "target_nutrient": "Zinc",
                    "dosage": "15 - 25 mg elemental zinc with meal",
                    "frequency": "Once daily with food (take with 1mg copper if continued >60 days)",
                    "clinical_rationale": "Optimizes enterocyte zip-carrier transport, accelerates epithelial turnover and restores cell-mediated immunocompetence without nausea.",
                    "evidence_reference": "Prasad AS. Mol Med 2008; 14(5-6):353-357. NIH ODS Zinc Guidelines.",
                    "contraindications": "Concomitant fluoroquinolone or tetracycline antibiotic ingestion (space by 2-4 hours)."
                },
                "Folate": {
                    "item_name": "L-5-Methyltetrahydrofolate (L-5-MTHF)",
                    "target_nutrient": "Folate",
                    "dosage": "400 - 800 mcg DFE/day",
                    "frequency": "Daily morning dose with food",
                    "clinical_rationale": "Active methylated folate bypasses MTHFR enzymatic polymorphisms and prevents accumulation of unmetabolized synthetic folic acid.",
                    "evidence_reference": "Cochrane Database of Systematic Reviews: Folate supplementation. NIH ODS Folate Guidelines.",
                    "contraindications": "Undiagnosed Vitamin B12 deficiency (must rule out B12 deficiency prior to single high-dose folate to prevent masking subacute combined degeneration)."
                },
                "Vitamin A": {
                    "item_name": ("Dietary Carotenoid Protocol (Zero High-Dose Synthetic Beta-Carotene)" if is_smoker else "Mixed Provitamin A Carotenoids (Beta-Carotene, Lutein, Zeaxanthin)"),
                    "target_nutrient": "Vitamin A",
                    "dosage": ("Dietary carotenoids from whole carrots, sweet potatoes, dark leafy greens" if is_smoker else "3000 - 5000 mcg (5000 - 8000 IU)"),
                    "frequency": "Daily with a fat-containing meal",
                    "clinical_rationale": ("ATBC and CARET clinical trials showed synthetic high-dose beta-carotene increased lung neoplasm risk in smokers; whole-food carotenoids are strictly prioritized." if is_smoker else "Provitamin A carotenoids undergo regulated mucosal enzymatic cleavage, avoiding hepatic accumulation and teratogenic risk of high-dose preformed retinol."),
                    "evidence_reference": "Tanumihardjo SA. Am J Clin Nutr 2011; 94(2):658S-665S. ATBC & CARET Prevention Trials.",
                    "contraindications": "Current or former cigarette smokers (for synthetic supplements); liver cirrhosis."
                },
                "Protein": {
                    "item_name": "Fermented Pea & Organic Brown Rice Protein Isolate (with Leucine)",
                    "target_nutrient": "Protein",
                    "dosage": "20 - 25g protein powder (providing >= 2.5g leucine)",
                    "frequency": "Daily post-exercise or as breakfast protein anchor",
                    "clinical_rationale": "Delivers balanced essential amino acid profile with PDCAAS near 1.0, stimulating muscle protein synthesis and maintaining nitrogen balance.",
                    "evidence_reference": "Phillips SM et al. J Sports Sci 2011; 29(S1):S29-S38.",
                    "contraindications": "Severe renal impairment without dialysis (requires personalized nephrology protein titration)."
                },
                "Vitamin C": {
                    "item_name": ("Low-Dose Ascorbic Acid with Bioflavonoids (Smoker-Adapted)" if is_smoker else "Buffered Ascorbic Acid with Citrus Bioflavonoids"),
                    "target_nutrient": "Vitamin C",
                    "dosage": ("200 - 500 mg/day" if is_smoker else "250 - 500 mg/day"),
                    "frequency": "Divided BID with meals (morning and evening)",
                    "clinical_rationale": ("Smokers require 35 mg/day additional Vitamin C due to accelerated oxidative turnover. Supports collagen synthesis, immune function, and iron absorption." if is_smoker else "Restores ascorbate tissue saturation; enhances non-heme iron absorption by 2-3x when co-ingested. Supports collagen synthesis and immune function."),
                    "evidence_reference": "Carr AC, Maggini S. Nutrients 2017; 9(11):1211. NIH ODS Vitamin C Fact Sheet.",
                    "contraindications": "History of calcium oxalate nephrolithiasis (reduce dose); hemochromatosis (enhances iron absorption)."
                },
                "Vitamin B1": {
                    "item_name": "Benfotiamine (Fat-Soluble Thiamine Derivative)",
                    "target_nutrient": "Vitamin B1",
                    "dosage": "50 - 100 mg/day",
                    "frequency": "Daily with a meal",
                    "clinical_rationale": "Benfotiamine provides 5x greater bioavailability than water-soluble thiamine HCl. Critical for pyruvate dehydrogenase and alpha-ketoglutarate dehydrogenase in energy metabolism. Alcohol-induced depletion is a major risk factor.",
                    "evidence_reference": "Lonsdale D. Evid Based Complement Alternat Med 2006; 3(1):49-59. NIH ODS Thiamin Fact Sheet.",
                    "contraindications": "None established at physiological doses. No UL set by NIH/IOM."
                },
                "Vitamin B6": {
                    "item_name": "Pyridoxal 5'-Phosphate (P5P Active B6)",
                    "target_nutrient": "Vitamin B6",
                    "dosage": "25 - 50 mg/day",
                    "frequency": "Daily with breakfast",
                    "clinical_rationale": "Active coenzyme form bypasses hepatic conversion. Essential for transamination, neurotransmitter synthesis (serotonin, dopamine, GABA), and homocysteine metabolism.",
                    "evidence_reference": "Leklem JE. Am J Clin Nutr 1990; 51(5):859-862. NIH ODS Vitamin B6 Fact Sheet.",
                    "contraindications": "Doses >100 mg/day chronically may cause peripheral neuropathy. UL: 100 mg/day."
                },
                "Potassium": {
                    "item_name": "Potassium Citrate Capsules",
                    "target_nutrient": "Potassium",
                    "dosage": "99 mg elemental potassium per capsule, 1-2 daily",
                    "frequency": "Daily with meals, titrate based on dietary intake",
                    "clinical_rationale": "Supports electrolyte balance, nerve conduction, and muscle contraction. Citrate form provides alkalinizing effect beneficial for bone health. Dietary potassium (fruits, vegetables) remains primary strategy.",
                    "evidence_reference": "Weaver CM. Adv Nutr 2013; 4(3):368S-377S. NIH ODS Potassium Fact Sheet.",
                    "contraindications": "Chronic kidney disease (GFR <60), hyperkalemia, ACE inhibitor or ARB therapy (monitor levels), potassium-sparing diuretics."
                },
                "Selenium": {
                    "item_name": "Selenomethionine (Organic Selenium)",
                    "target_nutrient": "Selenium",
                    "dosage": "55 - 100 mcg/day",
                    "frequency": "Daily with a meal",
                    "clinical_rationale": "Organic selenomethionine integrates into selenoproteins (glutathione peroxidase, thioredoxin reductase) supporting antioxidant defense and thyroid hormone metabolism.",
                    "evidence_reference": "Rayman MP. Lancet 2012; 379(9822):1256-1268. NIH ODS Selenium Fact Sheet.",
                    "contraindications": "Doses >400 mcg/day risk selenosis (garlic breath, hair loss, nail brittleness). UL: 400 mcg/day."
                },
                "Iodine": {
                    "item_name": "Potassium Iodide (KI) Supplement",
                    "target_nutrient": "Iodine",
                    "dosage": "150 mcg/day",
                    "frequency": "Daily with a meal",
                    "clinical_rationale": "Essential for thyroid hormone synthesis (T3, T4). Iodine deficiency is the most common preventable cause of intellectual disability worldwide. Kelp-based sources have variable iodine content.",
                    "evidence_reference": "Zimmermann MB. Endocr Rev 2009; 30(4):376-408. NIH ODS Iodine Fact Sheet.",
                    "contraindications": "Autoimmune thyroid disease (Hashimoto's, Graves'). UL: 1100 mcg/day."
                }
            }

            for nut in elevated_nutrients:
                if nut == "Iron" and is_hemochromatosis:
                    continue
                if nut in ["Potassium", "Phosphorus"] and is_ckd:
                    continue
                if nut == "Magnesium" and is_ckd:
                    continue
                if nut == "Protein" and is_ckd:
                    continue
                if nut == "Vitamin A" and is_pregnant:
                    supplements.append({
                        "item_name": "Prenatal Plant Carotenoid Complex (Zero Preformed Retinol)",
                        "target_nutrient": "Vitamin A",
                        "dosage": "2500 mcg provitamin A beta-carotene",
                        "frequency": "Daily with prenatal meal",
                        "clinical_rationale": "Safe rate-limited carotenoid conversion. Preformed retinol strictly avoided during organogenesis.",
                        "evidence_reference": "American College of Obstetricians and Gynecologists (ACOG) Nutrition in Pregnancy Guidelines.",
                        "contraindications": "Preformed retinol supplements."
                    })
                    continue

                if nut in SUPPLEMENT_CATALOG:
                    supplements.append(SUPPLEMENT_CATALOG[nut])

        # If still empty (e.g. healthy patient), provide foundational daily micronutrient maintenance
        if not supplements:
            supplements.append({
                "item_name": "Foundational Whole-Food Micronutrient Maintenance Protocol",
                "target_nutrient": "Multivitamin & Mineral",
                "dosage": "1 serving daily adhering to 100% daily RDA values",
                "frequency": "Daily with breakfast",
                "clinical_rationale": "Sustains enzymatic cofactor saturation and reinforces dietary resilience across all essential vitamins and trace minerals.",
                "evidence_reference": "Harvard School of Public Health: The Nutrition Source - Vitamins and Minerals.",
                "contraindications": "None at physiological RDA thresholds."
            })

        from .supplement_assembler import SupplementRegimenAssembler
        return SupplementRegimenAssembler.assemble_regimen(supplements, patient_intake=patient_intake)

    @classmethod
    def generate_monitoring_plan(cls, elevated_nutrients: List[str]) -> List[Dict[str, Any]]:
        """
        Creates laboratory biomarker surveillance protocols with precise clinical re-testing windows.
        """
        MONITORING_PANELS = {
            "Vitamin D": {
                "biomarker_test": "Serum 25-Hydroxyvitamin D [25(OH)D] total",
                "target_clinical_range": "35 - 50 ng/mL",
                "retest_interval": "8 - 12 weeks",
                "clinical_significance": "Confirms cellular tissue replenishment and rules out hypervitaminosis or refractory malabsorption."
            },
            "Iron": {
                "biomarker_test": "Complete Blood Count (CBC) + Serum Ferritin + Total Iron Binding Capacity (TIBC)",
                "target_clinical_range": "Ferritin > 50 ng/mL, Transferrin Saturation 25-45%, Hemoglobin normal",
                "retest_interval": "6 - 8 weeks",
                "clinical_significance": "Validates reticulocyte response and hepatic iron reserve restoration without oxidative surplus."
            },
            "Vitamin B12": {
                "biomarker_test": "Serum Cobalamin + Methylmalonic Acid (MMA) + Homocysteine",
                "target_clinical_range": "B12 > 450 pg/mL, MMA < 0.28 umol/L, Homocysteine < 10 umol/L",
                "retest_interval": "8 - 12 weeks",
                "clinical_significance": "MMA provides functional metabolic proof of active cellular mitochondrial B12 coenzyme activity."
            },
            "Calcium": {
                "biomarker_test": "Serum Ionized Calcium + Albumin-Corrected Total Calcium + Intact PTH",
                "target_clinical_range": "Ionized Calcium 4.6 - 5.3 mg/dL, Total Calcium 8.8 - 10.2 mg/dL",
                "retest_interval": "12 weeks",
                "clinical_significance": "Ensures suppression of parathyroid hormone (PTH) hypersecretion without driving hypercalcemia."
            },
            "Magnesium": {
                "biomarker_test": "Red Blood Cell (RBC) Magnesium",
                "target_clinical_range": "5.5 - 6.5 mg/dL",
                "retest_interval": "8 weeks",
                "clinical_significance": "RBC magnesium reflects intracellular storage far more sensitively than standard serum magnesium (<1% total body pool)."
            },
            "Zinc": {
                "biomarker_test": "Serum Zinc + Serum Alkaline Phosphatase",
                "target_clinical_range": "Zinc 80 - 120 mcg/dL",
                "retest_interval": "8 - 12 weeks",
                "clinical_significance": "Verifies mucosal metallothionein equilibrium and prevents copper depletion during replenishment."
            },
            "Folate": {
                "biomarker_test": "Red Blood Cell (RBC) Folate",
                "target_clinical_range": "RBC Folate > 400 ng/mL",
                "retest_interval": "8 weeks",
                "clinical_significance": "Confirms continuous tissue folate stores over the 120-day erythrocyte lifespan."
            },
            "Vitamin A": {
                "biomarker_test": "Serum Retinol + Retinol-Binding Protein (RBP)",
                "target_clinical_range": "Retinol 30 - 65 mcg/dL",
                "retest_interval": "12 weeks",
                "clinical_significance": "Monitors circulating retinol binding and liver retinoid stores."
            },
            "Protein": {
                "biomarker_test": "Comprehensive Metabolic Panel (Total Protein, Serum Albumin, Prealbumin)",
                "target_clinical_range": "Albumin 3.8 - 4.8 g/dL, Prealbumin 18 - 36 mg/dL",
                "retest_interval": "6 - 8 weeks",
                "clinical_significance": "Prealbumin provides rapid 48-72h half-life sensitivity for visceral protein synthesis and nitrogen balance."
            }
        }

        plans = []
        for nut in elevated_nutrients:
            if nut in MONITORING_PANELS:
                plans.append(MONITORING_PANELS[nut])

        if not plans:
            plans.append({
                "biomarker_test": "Annual Comprehensive Wellness & Micronutrient Panel",
                "target_clinical_range": "All clinical parameters within age/gender laboratory reference intervals",
                "retest_interval": "Annual / 12 months",
                "clinical_significance": "Proactive preventative surveillance to detect subclinical micronutrient trends before symptom emergence."
            })

        return plans

    @classmethod
    def generate_followup_plan(cls, elevated_nutrients: List[str]) -> List[Dict[str, Any]]:
        """
        Creates actionable clinical follow-up milestones for patient and healthcare provider.
        """
        return [
            {
                "timeframe": "Day 14 (Symptom & Tolerability Check)",
                "action": "Assess gastrointestinal tolerability of dietary modifications and any initiated supplement protocols.",
                "clinician_role": "Clinical Dietitian or Care Navigator review"
            },
            {
                "timeframe": "Day 30 (Intermediate Nutritional Re-Assessment)",
                "action": "Complete repeat NutriScan digital screening to quantify risk score trajectory and symptom improvement.",
                "clinician_role": "Primary Care Physician or Registered Dietitian"
            },
            {
                "timeframe": "Day 60 - 90 (Laboratory Biomarker Confirmation)",
                "action": "Execute confirmatory venous blood draw as detailed in the Monitoring Plan; review with prescribing provider.",
                "clinician_role": "Attending Physician / Endocrinologist / Hematologist"
            }
        ]
