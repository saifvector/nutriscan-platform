"""
Nutrient-to-Food Clinical Knowledge Base
Phase 5: Personalized Nutrition Recommendation Engine

Comprehensive evidence-based database of whole foods for all 11 target nutrients:
1. Protein
2. Vitamin A
3. Vitamin B12
4. Folate (Vitamin B9)
5. Vitamin C
6. Vitamin D
7. Vitamin E
8. Iron
9. Calcium
10. Zinc
11. Magnesium

Includes:
- Nutrient density per standard clinical serving
- Fractional bioavailability rating
- Dietary compatibility tags (VEGAN, VEGETARIAN, DAIRY_FREE, GLUTEN_FREE, OMNIVORE)
- Clinical preparation methods to minimize antinutrients (phytates, oxalates)
- Contraindications and pharmaceutical interactions
"""

from typing import Dict, Any, List

FOOD_KNOWLEDGE_BASE: Dict[str, List[Dict[str, Any]]] = {
    "Protein": [
        {
            "food_name": "Cooked Green or Brown Lentils",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (198g)",
            "nutrient_density": 17.9,
            "unit": "g",
            "bioavailability_rating": 0.78,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Soak lentils for 4-6 hours prior to boiling to degrade phytates and enhance protein assimilation.",
            "contraindications": "Caution in severe irritable bowel syndrome due to fermentable oligosaccharides (FODMAPs).",
            "rationale": "High-density plant protein delivering all essential amino acids when paired with whole grains."
        },
        {
            "food_name": "Organic Firm Tofu (Calcium-Set)",
            "food_group": "LEGUMES",
            "serving_size": "100g (approx 1/2 cup)",
            "nutrient_density": 10.0,
            "unit": "g",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Press excess water before pan-searing or baking with nutritional yeast.",
            "contraindications": "Soy allergy.",
            "rationale": "Complete plant protein featuring low glycemic impact and dual calcium delivery."
        },
        {
            "food_name": "Shelled Hemp Hearts",
            "food_group": "NUTS_SEEDS",
            "serving_size": "3 tablespoons (30g)",
            "nutrient_density": 9.5,
            "unit": "g",
            "bioavailability_rating": 0.88,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Sprinkle raw onto salads, smoothies, or oatmeal; avoid high-heat frying.",
            "contraindications": None,
            "rationale": "Complete amino acid profile rich in edestin and albumin storage proteins."
        },
        {
            "food_name": "Wild Atlantic Sockeye Salmon",
            "food_group": "SEAFOOD",
            "serving_size": "100g fillet cooked",
            "nutrient_density": 25.0,
            "unit": "g",
            "bioavailability_rating": 0.96,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Bake or poach with lemon and olive oil to preserve omega-3 fatty acids.",
            "contraindications": "Seafood/fish allergy.",
            "rationale": "Highest biological value protein matrix rich in bioactive peptides and anti-inflammatory EPA/DHA."
        },
        {
            "food_name": "Pasture-Raised Eggs",
            "food_group": "EGGS",
            "serving_size": "2 large eggs (100g)",
            "nutrient_density": 12.6,
            "unit": "g",
            "bioavailability_rating": 0.97,
            "dietary_tags": ["VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Cook whites thoroughly to denature avidin; keep yolks soft to preserve lutein and choline.",
            "contraindications": "Egg albumin allergy.",
            "rationale": "The nutritional gold standard for Protein Digestibility-Corrected Amino Acid Score (PDCAAS = 1.0)."
        },
        {
            "food_name": "Skinless Chicken Breast",
            "food_group": "POULTRY",
            "serving_size": "100g cooked",
            "nutrient_density": 31.0,
            "unit": "g",
            "bioavailability_rating": 0.95,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Herb-roasted with rosemary and garlic.",
            "contraindications": None,
            "rationale": "Lean protein with optimal leucine concentration for stimulating muscle protein synthesis."
        },
        {
            "food_name": "Plain Greek Yogurt (Unsweetened)",
            "food_group": "DAIRY",
            "serving_size": "1 cup (170g)",
            "nutrient_density": 17.0,
            "unit": "g",
            "bioavailability_rating": 0.95,
            "dietary_tags": ["VEGETARIAN", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Combine with raw berries and crushed walnuts.",
            "contraindications": "Severe lactose intolerance or dairy casein allergy.",
            "rationale": "High whey and micellar casein protein supporting prolonged satiety and tissue repair."
        },
        {
            "food_name": "Cooked Quinoa",
            "food_group": "GRAINS",
            "serving_size": "1 cup cooked (185g)",
            "nutrient_density": 8.1,
            "unit": "g",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Rinse thoroughly prior to boiling to eliminate bitter saponin coatings.",
            "contraindications": None,
            "rationale": "Pseudo-cereal complete protein containing all 9 essential amino acids."
        }
    ],

    "Vitamin A": [
        {
            "food_name": "Baked Sweet Potato (with Skin)",
            "food_group": "VEGETABLES",
            "serving_size": "1 medium baked (114g)",
            "nutrient_density": 1096.0,
            "unit": "mcg",
            "bioavailability_rating": 0.70,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume with a teaspoon of olive oil or avocado; dietary lipids multiply provitamin A carotenoid absorption by ~300%.",
            "contraindications": None,
            "rationale": "Rich in all-trans-beta-carotene converted to retinol via intestinal BCMO1 enzymes."
        },
        {
            "food_name": "Fresh Steamed Spinach",
            "food_group": "LEAFY_GREENS",
            "serving_size": "1 cup cooked (180g)",
            "nutrient_density": 943.0,
            "unit": "mcg",
            "bioavailability_rating": 0.65,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Light steaming disrupts plant cellular matrix, liberating carotenoids while degrading oxalic acid.",
            "contraindications": "History of calcium oxalate nephrolithiasis (kidney stones).",
            "rationale": "Dense source of provitamin A carotenoids, lutein, and zeaxanthin protecting retinal pigment epithelium."
        },
        {
            "food_name": "Raw Carrots & Hummus",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup chopped (128g)",
            "nutrient_density": 1069.0,
            "unit": "mcg",
            "bioavailability_rating": 0.60,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Pairing raw carrots with sesame tahini/hummus provides the necessary lipid carrier for beta-carotene.",
            "contraindications": None,
            "rationale": "High alpha and beta-carotene delivering continuous cellular antioxidant barrier defense."
        },
        {
            "food_name": "Butternut Squash Puree",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup cooked (205g)",
            "nutrient_density": 1144.0,
            "unit": "mcg",
            "bioavailability_rating": 0.72,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Roast at 375F with a drizzle of coconut or avocado oil.",
            "contraindications": None,
            "rationale": "Provides >100% of adult daily RDA of provitamin A carotenoids."
        },
        {
            "food_name": "Grass-Fed Beef Liver",
            "food_group": "MEAT",
            "serving_size": "70g cooked",
            "nutrient_density": 6582.0,
            "unit": "mcg",
            "bioavailability_rating": 0.98,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Saute gently with caramelized onions; do not overcook. Limit to once weekly.",
            "contraindications": "Pregnancy (hypervitaminosis A teratogenic risk).",
            "rationale": "Preformed retinyl palmitate with instantaneous biological utilization."
        }
    ],

    "Vitamin B12": [
        {
            "food_name": "Fortified Nutritional Yeast",
            "food_group": "DAIRY_ALTERNATIVES",
            "serving_size": "2 tablespoons (16g)",
            "nutrient_density": 17.6,
            "unit": "mcg",
            "bioavailability_rating": 0.90,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Sprinkle over hot soup, pasta, popcorn, or roasted vegetables after cooking.",
            "contraindications": None,
            "rationale": "Primary non-animal cyanocobalamin source for vegans; delivers >700% daily RDA per serving."
        },
        {
            "food_name": "Fortified Soy or Oat Milk",
            "food_group": "DAIRY_ALTERNATIVES",
            "serving_size": "1 cup (240ml)",
            "nutrient_density": 3.0,
            "unit": "mcg",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Shake carton well before pouring to ensure micro-encapsulated vitamins are evenly distributed.",
            "contraindications": None,
            "rationale": "Reliable bioavailable cyanocobalamin vehicle easily integrated into daily breakfast."
        },
        {
            "food_name": "Atlantic Mackerel or Sardines",
            "food_group": "SEAFOOD",
            "serving_size": "100g canned in olive oil",
            "nutrient_density": 8.9,
            "unit": "mcg",
            "bioavailability_rating": 0.95,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume whole fish with bones on sourdough toast or over dark leafy salads.",
            "contraindications": "Seafood allergy.",
            "rationale": "Dense marine source of methylcobalamin and adenosylcobalamin paired with anti-inflammatory fats."
        },
        {
            "food_name": "Wild Sockeye Salmon",
            "food_group": "SEAFOOD",
            "serving_size": "100g cooked",
            "nutrient_density": 4.8,
            "unit": "mcg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Pan-seared medium-rare.",
            "contraindications": "Seafood allergy.",
            "rationale": "Natural intrinsic cobalamin complexed with animal protein."
        },
        {
            "food_name": "Pasture-Raised Whole Eggs",
            "food_group": "EGGS",
            "serving_size": "2 large eggs (100g)",
            "nutrient_density": 1.1,
            "unit": "mcg",
            "bioavailability_rating": 0.65,
            "dietary_tags": ["VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Soft-boiled or poached.",
            "contraindications": "Egg allergy.",
            "rationale": "Natural whole-food cobalamin concentrated in the nutrient-dense yolk matrix."
        }
    ],

    "Folate": [
        {
            "food_name": "Steamed Asparagus Spears",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup cooked (180g)",
            "nutrient_density": 268.0,
            "unit": "mcg",
            "bioavailability_rating": 0.80,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Steam lightly for 3-5 minutes; avoid prolonged boiling which leaches water-soluble folates.",
            "contraindications": None,
            "rationale": "Delivers over 65% of adult daily requirement of active tetrahydrofolate."
        },
        {
            "food_name": "Cooked Black-Eyed Peas or Lentils",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (172g)",
            "nutrient_density": 358.0,
            "unit": "mcg",
            "bioavailability_rating": 0.78,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Simmer with bay leaves and garlic until tender.",
            "contraindications": None,
            "rationale": "Concentrated polyglutamate folates supporting critical single-carbon methylation pathways."
        },
        {
            "food_name": "Fresh Baby Spinach Salad",
            "food_group": "LEAFY_GREENS",
            "serving_size": "2 cups raw (60g)",
            "nutrient_density": 116.0,
            "unit": "mcg",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Eat fresh and raw with lemon juice dressing; heat destroys up to 50% of natural folates.",
            "contraindications": None,
            "rationale": "Direct namesake food of folate (folium = leaf) with high active bioavailability."
        },
        {
            "food_name": "Hass Avocado",
            "food_group": "FRUITS",
            "serving_size": "1 whole medium (150g)",
            "nutrient_density": 122.0,
            "unit": "mcg",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Slice fresh over meals or mash onto seed bread.",
            "contraindications": None,
            "rationale": "Nutrient-dense fruit delivering folate paired with monounsaturated fatty acids."
        }
    ],

    "Vitamin C": [
        {
            "food_name": "Sliced Yellow or Red Bell Pepper",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup chopped raw (149g)",
            "nutrient_density": 190.0,
            "unit": "mg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume raw or lightly stir-fried; ascorbic acid is heat-labile and degrades at >140F.",
            "contraindications": None,
            "rationale": "Contains over 200% the Vitamin C concentration of oranges per serving."
        },
        {
            "food_name": "Fresh Kiwi Fruit",
            "food_group": "FRUITS",
            "serving_size": "2 medium kiwis (140g)",
            "nutrient_density": 137.0,
            "unit": "mg",
            "bioavailability_rating": 0.94,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Slice and eat fresh; the thin skin is edible and packed with fiber.",
            "contraindications": "Kiwi actinidin allergy.",
            "rationale": "Potent L-ascorbic acid delivery combined with prebiotic actinidin and digestive enzymes."
        },
        {
            "food_name": "Organic Strawberries",
            "food_group": "FRUITS",
            "serving_size": "1 cup whole (144g)",
            "nutrient_density": 85.0,
            "unit": "mg",
            "bioavailability_rating": 0.90,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Wash thoroughly under cold water; eat fresh.",
            "contraindications": None,
            "rationale": "Antioxidant powerhouse delivering ellagic acid alongside active ascorbic acid."
        },
        {
            "food_name": "Steamed Broccoli Florets",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup cooked (156g)",
            "nutrient_density": 81.0,
            "unit": "mg",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Light 3-minute steam preserves sulforaphane-producing myrosinase enzymes and Vitamin C.",
            "contraindications": None,
            "rationale": "Cruciferous vegetable delivering immune defense and connective tissue collagen support."
        }
    ],

    "Vitamin D": [
        {
            "food_name": "UV-Exposed Portobello Mushrooms",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup sliced (120g)",
            "nutrient_density": 634.0,
            "unit": "IU",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Saute in extra virgin olive oil or ghee; place gills-up in midday sunlight for 15 min to further boost ergocalciferol.",
            "contraindications": None,
            "rationale": "The sole natural plant-based source of Vitamin D2 (ergocalciferol) photolyzed via mushroom ergosterol."
        },
        {
            "food_name": "Fortified Soy or Almond Milk (with D3/D2)",
            "food_group": "DAIRY_ALTERNATIVES",
            "serving_size": "1 cup (240ml)",
            "nutrient_density": 120.0,
            "unit": "IU",
            "bioavailability_rating": 0.88,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Combine with whole-grain oats or drink chilled.",
            "contraindications": None,
            "rationale": "Fortified non-dairy vehicle delivering reliable baseline daily calciferol."
        },
        {
            "food_name": "Wild Atlantic Sockeye Salmon",
            "food_group": "SEAFOOD",
            "serving_size": "100g cooked fillet",
            "nutrient_density": 668.0,
            "unit": "IU",
            "bioavailability_rating": 0.95,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Bake with sea salt and garlic; do not over-char the skin.",
            "contraindications": "Fish allergy.",
            "rationale": "Superlative natural animal cholecalciferol (Vitamin D3) source accompanied by marine fatty acids."
        },
        {
            "food_name": "Canned Sardines in Olive Oil",
            "food_group": "SEAFOOD",
            "serving_size": "1 can drained (92g)",
            "nutrient_density": 193.0,
            "unit": "IU",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Mash with Dijon mustard and capers on rye crackers or mixed greens.",
            "contraindications": "Fish allergy.",
            "rationale": "High-density natural D3 paired with rich calcium from soft edible bones."
        },
        {
            "food_name": "Pasture-Raised Egg Yolks",
            "food_group": "EGGS",
            "serving_size": "2 large yolks (34g)",
            "nutrient_density": 88.0,
            "unit": "IU",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Poach or soft-boil to keep yolk lipids liquid.",
            "contraindications": "Egg allergy.",
            "rationale": "Pasture access elevates hen cutaneous synthesis, yielding 3-4x the Vitamin D of caged eggs."
        }
    ],

    "Vitamin E": [
        {
            "food_name": "Raw Sunflower Seeds",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (35g)",
            "nutrient_density": 12.3,
            "unit": "mg",
            "bioavailability_rating": 0.88,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume raw or lightly toasted; store in refrigerator to protect delicate polyunsaturated lipids.",
            "contraindications": None,
            "rationale": "Supplies over 80% of daily RDA of d-alpha-tocopherol in a single handful."
        },
        {
            "food_name": "Raw Whole Almonds",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (28g)",
            "nutrient_density": 7.3,
            "unit": "mg",
            "bioavailability_rating": 0.84,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Eat unblanched with brown skin intact for synergistic polyphenols.",
            "contraindications": "Tree nut allergy.",
            "rationale": "Lipophilic antioxidant powerhouse protecting biological cell membranes from lipid peroxidation."
        },
        {
            "food_name": "Hass Avocado",
            "food_group": "FRUITS",
            "serving_size": "1 whole medium (150g)",
            "nutrient_density": 3.1,
            "unit": "mg",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Eat fresh with lime juice and sea salt.",
            "contraindications": None,
            "rationale": "Natural lipid carrier providing optimal endogenous absorption for fat-soluble alpha-tocopherol."
        },
        {
            "food_name": "Steamed Swiss Chard or Spinach",
            "food_group": "LEAFY_GREENS",
            "serving_size": "1 cup cooked (180g)",
            "nutrient_density": 3.7,
            "unit": "mg",
            "bioavailability_rating": 0.75,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Toss steamed chard with extra virgin olive oil.",
            "contraindications": None,
            "rationale": "Crucial green leafy tocopherol source with minimal caloric footprint."
        }
    ],

    "Iron": [
        {
            "food_name": "Steamed French Green or Brown Lentils",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (198g)",
            "nutrient_density": 6.6,
            "unit": "mg",
            "bioavailability_rating": 0.45,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "MANDATORY SYNERGY: Pair with red bell pepper or lemon juice. Vitamin C reduces ferric iron (Fe3+) to absorbable ferrous (Fe2+), boosting uptake by 300%.",
            "contraindications": "Avoid tea, coffee, or calcium supplements within 90 minutes of consumption.",
            "rationale": "Premier plant-based non-heme iron source delivering essential ferritin stores."
        },
        {
            "food_name": "Raw Pumpkin Seeds (Pepitas)",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (32g)",
            "nutrient_density": 4.2,
            "unit": "mg",
            "bioavailability_rating": 0.48,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Light roasting reduces inhibitory phytates. Eat alongside mandarin oranges or strawberries.",
            "contraindications": None,
            "rationale": "Exceptionally dense mineral seed delivering iron, zinc, and magnesium simultaneously."
        },
        {
            "food_name": "Firm Organic Tofu",
            "food_group": "LEGUMES",
            "serving_size": "1/2 cup (126g)",
            "nutrient_density": 3.4,
            "unit": "mg",
            "bioavailability_rating": 0.50,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Stir-fry with broccoli florets and ginger-garlic sauce.",
            "contraindications": "Soy allergy.",
            "rationale": "Substantial non-heme iron concentration in an easily digestible, versatile matrix."
        },
        {
            "food_name": "Cooked Black Beans",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (172g)",
            "nutrient_density": 3.6,
            "unit": "mg",
            "bioavailability_rating": 0.42,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Combine with fresh salsa (rich in tomatoes and lime juice).",
            "contraindications": None,
            "rationale": "Fiber-rich legume supporting sustained hemoglobin regeneration."
        },
        {
            "food_name": "Grass-Fed Beef Sirloin Steak",
            "food_group": "MEAT",
            "serving_size": "100g cooked",
            "nutrient_density": 2.9,
            "unit": "mg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Grill or sear in cast-iron skillet. Rest meat 5 minutes before slicing.",
            "contraindications": "Gout or severe hyperuricemia.",
            "rationale": "High-fractional-bioavailability heme iron unaffected by dietary phytates or polyphenols."
        }
    ],

    "Calcium": [
        {
            "food_name": "Whole Sesame Tahini",
            "food_group": "NUTS_SEEDS",
            "serving_size": "2 tablespoons (30g)",
            "nutrient_density": 130.0,
            "unit": "mg",
            "bioavailability_rating": 0.65,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Whisk with lemon juice, garlic, and water into a creamy salad dressing.",
            "contraindications": "Sesame seed allergy.",
            "rationale": "Top non-dairy calcium reserve delivering substantial bone-mineralizing density."
        },
        {
            "food_name": "Calcium-Fortified Plant Milk",
            "food_group": "DAIRY_ALTERNATIVES",
            "serving_size": "1 cup (240ml)",
            "nutrient_density": 350.0,
            "unit": "mg",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Shake carton well to suspend calcium carbonate or tricalcium phosphate.",
            "contraindications": None,
            "rationale": "Provides more elemental calcium per cup than conventional bovine cow's milk."
        },
        {
            "food_name": "Steamed Bok Choy (Chinese Cabbage)",
            "food_group": "LEAFY_GREENS",
            "serving_size": "1 cup cooked (170g)",
            "nutrient_density": 158.0,
            "unit": "mg",
            "bioavailability_rating": 0.90,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Stir-fry with sesame oil and ginger. Lowest oxalate green, resulting in superior absorption (>50% fractional absorption vs. 5% for spinach).",
            "contraindications": None,
            "rationale": "Low-oxalate cruciferous powerhouse with the highest bioavailable fractional calcium absorption."
        },
        {
            "food_name": "Firm Tofu (Calcium Sulfate Set)",
            "food_group": "LEGUMES",
            "serving_size": "1/2 cup (126g)",
            "nutrient_density": 434.0,
            "unit": "mg",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Cube and roast until crisp.",
            "contraindications": "Soy allergy.",
            "rationale": "Calcium sulfate coagulant creates an exceptionally dense bioavailable bone-building matrix."
        },
        {
            "food_name": "Greek Yogurt (Plain, Whole Milk)",
            "food_group": "DAIRY",
            "serving_size": "1 cup (200g)",
            "nutrient_density": 230.0,
            "unit": "mg",
            "bioavailability_rating": 0.90,
            "dietary_tags": ["VEGETARIAN", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Eat with raw honey and chia seeds.",
            "contraindications": "Lactose intolerance or dairy casein allergy.",
            "rationale": "Lactic acid bacteria culture lowers pH, enhancing ionic calcium solubility and absorption."
        }
    ],

    "Zinc": [
        {
            "food_name": "Raw Shelled Pumpkin Seeds",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (32g)",
            "nutrient_density": 2.9,
            "unit": "mg",
            "bioavailability_rating": 0.55,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Light soaking or dry roasting reduces phytate-to-zinc molar ratios.",
            "contraindications": None,
            "rationale": "Premier plant zinc powerhouse supporting cellular immunity and testosterone/fertility."
        },
        {
            "food_name": "Raw Cashews",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (35g)",
            "nutrient_density": 2.0,
            "unit": "mg",
            "bioavailability_rating": 0.52,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Soak and blend into creamy vegan sauces or eat raw.",
            "contraindications": "Tree nut allergy.",
            "rationale": "Delicious plant zinc source supporting wound healing and epithelial barrier integrity."
        },
        {
            "food_name": "Cooked Chickpeas (Garbanzo Beans)",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (164g)",
            "nutrient_density": 2.5,
            "unit": "mg",
            "bioavailability_rating": 0.48,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Roast with paprika and olive oil for a crunchy zinc snack.",
            "contraindications": None,
            "rationale": "High prebiotic fiber legume supporting thymic hormone thymulin and T-cell function."
        },
        {
            "food_name": "Grass-Fed Lean Beef Tenderloin",
            "food_group": "MEAT",
            "serving_size": "100g cooked",
            "nutrient_density": 5.8,
            "unit": "mg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Quick sear over high heat to preserve internal moisture.",
            "contraindications": None,
            "rationale": "Amino acid-chelated zinc without any phytate inhibition, maximizing fractional intestinal uptake."
        }
    ],

    "Magnesium": [
        {
            "food_name": "Raw Pumpkin Seeds (Pepitas)",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (32g)",
            "nutrient_density": 168.0,
            "unit": "mg",
            "bioavailability_rating": 0.75,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume daily in smoothies or on oatmeal.",
            "contraindications": None,
            "rationale": "The single most concentrated whole-food source of elemental magnesium (>40% adult RDA per serving)."
        },
        {
            "food_name": "Raw Whole Almonds",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (35g)",
            "nutrient_density": 95.0,
            "unit": "mg",
            "bioavailability_rating": 0.70,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Soak overnight in salted water to deactivate enzyme inhibitors.",
            "contraindications": "Tree nut allergy.",
            "rationale": "Essential cofactor for ATP production and muscular relaxation."
        },
        {
            "food_name": "Steamed Spinach",
            "food_group": "LEAFY_GREENS",
            "serving_size": "1 cup cooked (180g)",
            "nutrient_density": 157.0,
            "unit": "mg",
            "bioavailability_rating": 0.65,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Steaming concentrates green chlorophyll-bound central magnesium ions.",
            "contraindications": "Kidney stone history (oxalates).",
            "rationale": "Every chlorophyll molecule contains a central Mg2+ atom; cooking collapses foliage to deliver high density."
        },
        {
            "food_name": "Dark Chocolate (85% Cocoa)",
            "food_group": "LEGUMES",
            "serving_size": "1 oz / 28g square",
            "nutrient_density": 65.0,
            "unit": "mg",
            "bioavailability_rating": 0.78,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Choose chocolate with >80% cocoa solids and <5g sugar.",
            "contraindications": "Severe gastroesophageal reflux (GERD).",
            "rationale": "Rich in polyphenol-stabilized magnesium promoting vascular vasodilation and anxiety relief."
        },
        {
            "food_name": "Cooked Black Beans",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (172g)",
            "nutrient_density": 120.0,
            "unit": "mg",
            "bioavailability_rating": 0.68,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Cook thoroughly with cumin and sea salt.",
            "contraindications": None,
            "rationale": "Cardioprotective mineral density regulating cardiac rhythm and neuromuscular tone."
        }
    ],

    "Vitamin B1": [
        {
            "food_name": "Shelled Sunflower Seeds",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (35g)",
            "nutrient_density": 0.52,
            "unit": "mg",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume raw or lightly toasted over salads or morning cereal.",
            "contraindications": None,
            "rationale": "Delivers ~45% of adult daily thiamine RDA in a single compact serving."
        },
        {
            "food_name": "Cooked Green Lentils",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (198g)",
            "nutrient_density": 0.33,
            "unit": "mg",
            "bioavailability_rating": 0.78,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Soak prior to cooking; avoid high-heat prolonged pressure boiling.",
            "contraindications": None,
            "rationale": "High-density plant thiamine supporting mitochondrial carbohydrate metabolism."
        },
        {
            "food_name": "Cooked Brown Rice (Long-Grain)",
            "food_group": "GRAINS",
            "serving_size": "1 cup cooked (195g)",
            "nutrient_density": 0.36,
            "unit": "mg",
            "bioavailability_rating": 0.80,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Keep intact germ and bran layers; do not discard cooking water.",
            "contraindications": None,
            "rationale": "Whole-grain thiamine complex protecting against refined carb depletion."
        },
        {
            "food_name": "Pasture-Raised Pork Tenderloin",
            "food_group": "MEAT",
            "serving_size": "100g roasted",
            "nutrient_density": 0.95,
            "unit": "mg",
            "bioavailability_rating": 0.95,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Roast gently to an internal temp of 145F.",
            "contraindications": "Pork dietary restriction.",
            "rationale": "Highest biological animal source delivering ~80% adult RDA."
        }
    ],

    "Vitamin B2": [
        {
            "food_name": "Fortified Nutritional Yeast",
            "food_group": "DAIRY_ALTERNATIVES",
            "serving_size": "2 tablespoons (16g)",
            "nutrient_density": 9.6,
            "unit": "mg",
            "bioavailability_rating": 0.90,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Add to cooked grains, pasta, or soups. Store in opaque container away from light.",
            "contraindications": None,
            "rationale": "Massive riboflavin density (>700% daily value) in a light-sensitive protected matrix."
        },
        {
            "food_name": "Pasture-Raised Whole Eggs",
            "food_group": "EGGS",
            "serving_size": "2 large eggs (100g)",
            "nutrient_density": 0.45,
            "unit": "mg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Poach or boil; protein denaturation liberates bound riboflavin.",
            "contraindications": "Egg allergy.",
            "rationale": "Bioavailable FAD and FMN electron carriers for cellular respiration."
        },
        {
            "food_name": "Raw Whole Almonds",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (35g)",
            "nutrient_density": 0.38,
            "unit": "mg",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Eat unblanched with brown skins intact for polyphenol synergy.",
            "contraindications": "Tree nut allergy.",
            "rationale": "Premier plant-based riboflavin supporting glutathione antioxidant recycling."
        },
        {
            "food_name": "Sautéed Cremini Mushrooms",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup sliced cooked (140g)",
            "nutrient_density": 0.49,
            "unit": "mg",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Sauté with garlic and olive oil.",
            "contraindications": None,
            "rationale": "Delivers over 35% of adult daily requirement in a savory plant food."
        }
    ],

    "Vitamin B3": [
        {
            "food_name": "Skinless Roasted Chicken Breast",
            "food_group": "POULTRY",
            "serving_size": "100g cooked",
            "nutrient_density": 13.7,
            "unit": "mg",
            "bioavailability_rating": 0.96,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Herb-roasted with thyme and olive oil.",
            "contraindications": None,
            "rationale": "Supplies >85% of adult daily RDA of preformed nicotinamide."
        },
        {
            "food_name": "Wild Yellowfin Tuna",
            "food_group": "SEAFOOD",
            "serving_size": "100g cooked",
            "nutrient_density": 18.8,
            "unit": "mg",
            "bioavailability_rating": 0.98,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Pan-seared; avoid overcooking to preserve B-vitamins.",
            "contraindications": "Fish allergy.",
            "rationale": "Superlative animal niacin source delivering over 100% daily adult requirement."
        },
        {
            "food_name": "Dry-Roasted Peanuts",
            "food_group": "NUTS_SEEDS",
            "serving_size": "1/4 cup (37g)",
            "nutrient_density": 4.9,
            "unit": "mg",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume as whole peanuts or pure natural peanut butter.",
            "contraindications": "Peanut allergy.",
            "rationale": "Dense plant-based niacin source protecting against Pellagra."
        },
        {
            "food_name": "Cooked Brown Lentils",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (198g)",
            "nutrient_density": 2.1,
            "unit": "mg",
            "bioavailability_rating": 0.75,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Pair with brown rice for complementary amino acid tryptophan conversion.",
            "contraindications": None,
            "rationale": "High-fiber legume delivering both niacin and tryptophan precursor."
        }
    ],

    "Vitamin B6": [
        {
            "food_name": "Cooked Chickpeas (Garbanzo Beans)",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (164g)",
            "nutrient_density": 1.1,
            "unit": "mg",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Blend into lemon-tahini hummus or roast with paprika.",
            "contraindications": None,
            "rationale": "Supplies >65% of adult daily requirement of active pyridoxine."
        },
        {
            "food_name": "Fresh Yellow Bananas",
            "food_group": "FRUITS",
            "serving_size": "1 large banana (136g)",
            "nutrient_density": 0.5,
            "unit": "mg",
            "bioavailability_rating": 0.90,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Consume fresh when ripe with speckled peel.",
            "contraindications": None,
            "rationale": "Readily bioavailable pyridoxal supporting neurotransmitter dopamine/serotonin synthesis."
        },
        {
            "food_name": "Wild Alaskan Sockeye Salmon",
            "food_group": "SEAFOOD",
            "serving_size": "100g cooked",
            "nutrient_density": 0.9,
            "unit": "mg",
            "bioavailability_rating": 0.95,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Broil or steam with lemon.",
            "contraindications": "Fish allergy.",
            "rationale": "High-density natural PLP paired with omega-3 anti-inflammatory EPA/DHA."
        },
        {
            "food_name": "Baked Russet Potato with Skin",
            "food_group": "VEGETABLES",
            "serving_size": "1 medium baked (173g)",
            "nutrient_density": 0.7,
            "unit": "mg",
            "bioavailability_rating": 0.88,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Eat skin and flesh together.",
            "contraindications": None,
            "rationale": "Starchy staple providing concurrent potassium and pyridoxine."
        }
    ],

    "Potassium": [
        {
            "food_name": "Baked Russet Potato with Skin",
            "food_group": "VEGETABLES",
            "serving_size": "1 medium potato (173g)",
            "nutrient_density": 926.0,
            "unit": "mg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Bake whole with olive oil and rosemary; retain skin.",
            "contraindications": "Chronic kidney disease with hyperkalemia.",
            "rationale": "Highest density dietary potassium staple delivering ~30% adult AI."
        },
        {
            "food_name": "Fresh Hass Avocado",
            "food_group": "FRUITS",
            "serving_size": "1 medium avocado (150g)",
            "nutrient_density": 708.0,
            "unit": "mg",
            "bioavailability_rating": 0.94,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Slice raw on seed toast or salads.",
            "contraindications": "Hyperkalemia.",
            "rationale": "Potassium-dense fruit containing healthy monounsaturated fatty acids."
        },
        {
            "food_name": "Cooked Swiss Chard or Spinach",
            "food_group": "LEAFY_GREENS",
            "serving_size": "1 cup cooked (175g)",
            "nutrient_density": 961.0,
            "unit": "mg",
            "bioavailability_rating": 0.88,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Lightly steam; discard excess blanching water if oxalate sensitive.",
            "contraindications": "Oxalate nephrolithiasis.",
            "rationale": "Super-concentrated electrolyte green supporting blood pressure regulation."
        },
        {
            "food_name": "Cooked White Cannellini Beans",
            "food_group": "LEGUMES",
            "serving_size": "1 cup cooked (182g)",
            "nutrient_density": 1004.0,
            "unit": "mg",
            "bioavailability_rating": 0.85,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Simmer with garlic and bay leaves.",
            "contraindications": "Severe renal impairment.",
            "rationale": "Over 1,000 mg potassium per cup coupled with prebiotic resistant starch."
        }
    ],

    "Selenium": [
        {
            "food_name": "Raw Brazil Nuts",
            "food_group": "NUTS_SEEDS",
            "serving_size": "2 whole nuts (10g)",
            "nutrient_density": 137.0,
            "unit": "mcg",
            "bioavailability_rating": 0.95,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Limit to 1-2 nuts daily to avoid exceeding tolerable upper intake (400 mcg).",
            "contraindications": "Tree nut allergy; do not consume >4 nuts daily.",
            "rationale": "The single most concentrated selenium food on earth (>200% daily RDA in 2 nuts)."
        },
        {
            "food_name": "Yellowfin Tuna Canned in Olive Oil",
            "food_group": "SEAFOOD",
            "serving_size": "1 can drained (85g)",
            "nutrient_density": 92.0,
            "unit": "mcg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Mix with fresh herbs and lemon juice.",
            "contraindications": "Seafood allergy.",
            "rationale": "Selenoneine marine antioxidant protecting against lipid peroxidation."
        },
        {
            "food_name": "Pasture-Raised Whole Eggs",
            "food_group": "EGGS",
            "serving_size": "2 large eggs (100g)",
            "nutrient_density": 31.0,
            "unit": "mcg",
            "bioavailability_rating": 0.88,
            "dietary_tags": ["VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Poached or soft-boiled.",
            "contraindications": "Egg allergy.",
            "rationale": "Delivers over 55% of adult daily requirement in natural yolk phospholipids."
        },
        {
            "food_name": "Cooked Shiitake Mushrooms",
            "food_group": "VEGETABLES",
            "serving_size": "1 cup cooked (145g)",
            "nutrient_density": 36.0,
            "unit": "mcg",
            "bioavailability_rating": 0.82,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Stir-fry with ginger and tamari.",
            "contraindications": None,
            "rationale": "Excellent non-animal selenium source supporting thyroid T4-to-T3 deiodinases."
        }
    ],

    "Iodine": [
        {
            "food_name": "Organic Dried Wakame or Nori Seaweed",
            "food_group": "VEGETABLES",
            "serving_size": "2 sheets nori (5g)",
            "nutrient_density": 116.0,
            "unit": "mcg",
            "bioavailability_rating": 0.96,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Snack on dried nori crisps or add rehydrated wakame to miso soup.",
            "contraindications": "Graves' disease or active hyperthyroidism.",
            "rationale": "Pure marine iodide delivery supplying ~80% of adult daily requirement."
        },
        {
            "food_name": "Iodized Table Sea Salt",
            "food_group": "FORTIFIED_FOODS",
            "serving_size": "1/4 teaspoon (1.5g)",
            "nutrient_density": 71.0,
            "unit": "mcg",
            "bioavailability_rating": 0.98,
            "dietary_tags": ["VEGAN", "VEGETARIAN", "DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Use in normal home seasoning; do not over-consume sodium.",
            "contraindications": "Severe sodium restriction in congestive heart failure.",
            "rationale": "The WHO gold-standard public health vehicle preventing endemic goiter."
        },
        {
            "food_name": "Wild Atlantic Cod Fillet",
            "food_group": "SEAFOOD",
            "serving_size": "100g cooked",
            "nutrient_density": 110.0,
            "unit": "mcg",
            "bioavailability_rating": 0.94,
            "dietary_tags": ["DAIRY_FREE", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Herb-baked with garlic and parsley.",
            "contraindications": "Fish allergy.",
            "rationale": "Clean white fish delivering ~75% of daily adult requirement."
        },
        {
            "food_name": "Organic Plain Greek Yogurt",
            "food_group": "DAIRY",
            "serving_size": "1 cup (200g)",
            "nutrient_density": 116.0,
            "unit": "mcg",
            "bioavailability_rating": 0.92,
            "dietary_tags": ["VEGETARIAN", "GLUTEN_FREE", "OMNIVORE"],
            "preparation_tips": "Enjoy chilled with raw berries and crushed walnuts.",
            "contraindications": "Dairy casein allergy or severe lactose intolerance.",
            "rationale": "High iodine content derived from dairy cattle dietary feed and teat sanitation."
        }
    ]
}
