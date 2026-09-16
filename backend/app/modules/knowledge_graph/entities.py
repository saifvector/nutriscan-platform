"""
Clinical Knowledge Graph Entities Registry
Phase 7B: Defines all 7 entity classes with rigorous clinical metadata.
"""

from typing import Dict, Any, List
from .schemas import EntityType

ENTITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ══════════════════════════════════════════════════════════════════════════
    # 1. NUTRIENTS (All 18 Clinical Target Nutrients)
    # ══════════════════════════════════════════════════════════════════════════
    "NUTRIENT_PROTEIN": {
        "id": "NUTRIENT_PROTEIN",
        "name": "Protein",
        "entity_type": EntityType.NUTRIENT,
        "category": "Macronutrient",
        "description": "Essential nitrogenous organic compound vital for cellular structure, enzyme catalysis, tissue remodeling, and immune antibody synthesis.",
        "metadata": {"canonical_code": "PROTEIN", "urgency_weight": 1.25, "unit": "g/day"}
    },
    "NUTRIENT_VITAMIN_A": {
        "id": "NUTRIENT_VITAMIN_A",
        "name": "Vitamin A",
        "entity_type": EntityType.NUTRIENT,
        "category": "Fat-Soluble Vitamin",
        "description": "Retinoids and provitamin carotenoids critical for rhodopsin phototransduction, epithelial barrier integrity, and mucosal immunity.",
        "metadata": {"canonical_code": "VITAMIN_A", "urgency_weight": 1.05, "unit": "mcg RAE/day"}
    },
    "NUTRIENT_VITAMIN_B1": {
        "id": "NUTRIENT_VITAMIN_B1",
        "name": "Vitamin B1 (Thiamine)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Water-Soluble Vitamin",
        "description": "Cofactor for pyruvate dehydrogenase and alpha-ketoglutarate dehydrogenase in carbohydrate metabolism and ATP generation.",
        "metadata": {"canonical_code": "VITAMIN_B1", "urgency_weight": 1.25, "unit": "mg/day"}
    },
    "NUTRIENT_VITAMIN_B2": {
        "id": "NUTRIENT_VITAMIN_B2",
        "name": "Vitamin B2 (Riboflavin)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Water-Soluble Vitamin",
        "description": "Precursor of FAD and FMN electron carriers in the mitochondrial respiratory chain and glutathione antioxidant recycling.",
        "metadata": {"canonical_code": "VITAMIN_B2", "urgency_weight": 1.00, "unit": "mg/day"}
    },
    "NUTRIENT_VITAMIN_B3": {
        "id": "NUTRIENT_VITAMIN_B3",
        "name": "Vitamin B3 (Niacin)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Water-Soluble Vitamin",
        "description": "Core substrate for NAD/NADP synthesis required for cellular energy, DNA repair via PARP-1, and steroid hormone biosynthesis.",
        "metadata": {"canonical_code": "VITAMIN_B3", "urgency_weight": 1.15, "unit": "mg NE/day"}
    },
    "NUTRIENT_VITAMIN_B6": {
        "id": "NUTRIENT_VITAMIN_B6",
        "name": "Vitamin B6 (Pyridoxine)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Water-Soluble Vitamin",
        "description": "Coenzyme PLP for >140 enzymatic reactions, amino acid transamination, neurotransmitter synthesis (GABA, serotonin, dopamine), and hemoglobin formation.",
        "metadata": {"canonical_code": "VITAMIN_B6", "urgency_weight": 1.20, "unit": "mg/day"}
    },
    "NUTRIENT_VITAMIN_B12": {
        "id": "NUTRIENT_VITAMIN_B12",
        "name": "Vitamin B12 (Cobalamin)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Water-Soluble Vitamin",
        "description": "Cobalt-containing cofactor for methionine synthase and methylmalonyl-CoA mutase, essential for axonal myelin preservation and erythropoiesis.",
        "metadata": {"canonical_code": "VITAMIN_B12", "urgency_weight": 1.30, "unit": "mcg/day"}
    },
    "NUTRIENT_FOLATE": {
        "id": "NUTRIENT_FOLATE",
        "name": "Folate (Vitamin B9)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Water-Soluble Vitamin",
        "description": "One-carbon transfer coenzyme critical for thymidylate purine synthesis, genomic DNA methylation, and homocysteine regulation.",
        "metadata": {"canonical_code": "FOLATE_B9", "urgency_weight": 1.20, "unit": "mcg DFE/day"}
    },
    "NUTRIENT_VITAMIN_C": {
        "id": "NUTRIENT_VITAMIN_C",
        "name": "Vitamin C (Ascorbic Acid)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Water-Soluble Vitamin",
        "description": "Potent aqueous antioxidant and cofactor for prolyl/lysyl hydroxylases in collagen biosynthesis, carnitine production, and non-heme iron reduction.",
        "metadata": {"canonical_code": "VITAMIN_C", "urgency_weight": 1.00, "unit": "mg/day"}
    },
    "NUTRIENT_VITAMIN_D": {
        "id": "NUTRIENT_VITAMIN_D",
        "name": "Vitamin D",
        "entity_type": EntityType.NUTRIENT,
        "category": "Secosteroid Hormone",
        "description": "Secosteroid prohormone activated to calcitriol, regulating gene transcription, paracellular intestinal calcium/phosphate absorption, and innate immunity.",
        "metadata": {"canonical_code": "VITAMIN_D", "urgency_weight": 1.15, "unit": "IU/day"}
    },
    "NUTRIENT_VITAMIN_E": {
        "id": "NUTRIENT_VITAMIN_E",
        "name": "Vitamin E (Alpha-Tocopherol)",
        "entity_type": EntityType.NUTRIENT,
        "category": "Fat-Soluble Vitamin",
        "description": "Primary lipid-soluble chain-breaking antioxidant protecting polyunsaturated fatty acids in cell membranes from lipid peroxidation.",
        "metadata": {"canonical_code": "VITAMIN_E", "urgency_weight": 0.90, "unit": "mg/day"}
    },
    "NUTRIENT_IRON": {
        "id": "NUTRIENT_IRON",
        "name": "Iron",
        "entity_type": EntityType.NUTRIENT,
        "category": "Essential Mineral",
        "description": "Central transition metal of heme in hemoglobin and myoglobin, executing systemic oxygen transport and mitochondrial electron transfer.",
        "metadata": {"canonical_code": "IRON", "urgency_weight": 1.25, "unit": "mg/day"}
    },
    "NUTRIENT_CALCIUM": {
        "id": "NUTRIENT_CALCIUM",
        "name": "Calcium",
        "entity_type": EntityType.NUTRIENT,
        "category": "Essential Mineral",
        "description": "Dominant structural mineral of the hydroxyapatite skeletal matrix and key second messenger mediating muscle contraction and neurosecretion.",
        "metadata": {"canonical_code": "CALCIUM", "urgency_weight": 1.20, "unit": "mg/day"}
    },
    "NUTRIENT_MAGNESIUM": {
        "id": "NUTRIENT_MAGNESIUM",
        "name": "Magnesium",
        "entity_type": EntityType.NUTRIENT,
        "category": "Essential Mineral",
        "description": "Divalent intracellular cation obligate for Mg-ATP chelation across >300 enzymatic steps, parathyroid hormone release, and neuromuscular membrane polarization.",
        "metadata": {"canonical_code": "MAGNESIUM", "urgency_weight": 1.10, "unit": "mg/day"}
    },
    "NUTRIENT_ZINC": {
        "id": "NUTRIENT_ZINC",
        "name": "Zinc",
        "entity_type": EntityType.NUTRIENT,
        "category": "Essential Trace Mineral",
        "description": "Catalytic and structural component of >1,000 zinc-finger transcription factors, alkaline phosphatase, thymulin hormone, and collagenase wound remodeling.",
        "metadata": {"canonical_code": "ZINC", "urgency_weight": 1.05, "unit": "mg/day"}
    },
    "NUTRIENT_POTASSIUM": {
        "id": "NUTRIENT_POTASSIUM",
        "name": "Potassium",
        "entity_type": EntityType.NUTRIENT,
        "category": "Electrolyte",
        "description": "Chief intracellular cation maintaining cellular resting membrane potential, myocardial electrophysiology, and vascular smooth muscle tone.",
        "metadata": {"canonical_code": "POTASSIUM", "urgency_weight": 1.30, "unit": "mg/day"}
    },
    "NUTRIENT_SELENIUM": {
        "id": "NUTRIENT_SELENIUM",
        "name": "Selenium",
        "entity_type": EntityType.NUTRIENT,
        "category": "Essential Trace Mineral",
        "description": "Obligate component of 25 selenoproteins, including glutathione peroxidase and iodothyronine deiodinases governing peripheral thyroid hormone activation.",
        "metadata": {"canonical_code": "SELENIUM", "urgency_weight": 1.05, "unit": "mcg/day"}
    },
    "NUTRIENT_IODINE": {
        "id": "NUTRIENT_IODINE",
        "name": "Iodine",
        "entity_type": EntityType.NUTRIENT,
        "category": "Essential Trace Mineral",
        "description": "Integral substrate for thyroglobulin iodination and thyroxine (T4) and triiodothyronine (T3) synthesis, regulating systemic metabolic rate.",
        "metadata": {"canonical_code": "IODINE", "urgency_weight": 1.15, "unit": "mcg/day"}
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 2. SYMPTOMS (Clinical Deficiency Manifestations)
    # ══════════════════════════════════════════════════════════════════════════
    "SYMPTOM_FATIGUE": {
        "id": "SYMPTOM_FATIGUE",
        "name": "Chronic Fatigue",
        "entity_type": EntityType.SYMPTOM,
        "category": "Constitutional",
        "description": "Profound, unrefreshing exhaustion caused by tissue hypoxia, impaired ATP mitochondrial bioenergetics, or neurochemical depletion.",
        "metadata": {"severity_level": "Moderate", "icd10": "R53.83"}
    },
    "SYMPTOM_HAIR_LOSS": {
        "id": "SYMPTOM_HAIR_LOSS",
        "name": "Hair Loss (Telogen Effluvium)",
        "entity_type": EntityType.SYMPTOM,
        "category": "Integumentary",
        "description": "Premature termination of anagen hair follicle growth phase, leading to diffuse shedding and keratin structural fragility.",
        "metadata": {"severity_level": "Mild-Moderate", "icd10": "L65.0"}
    },
    "SYMPTOM_BRAIN_FOG": {
        "id": "SYMPTOM_BRAIN_FOG",
        "name": "Brain Fog & Cognitive Sluggishness",
        "entity_type": EntityType.SYMPTOM,
        "category": "Neurological",
        "description": "Impaired executive function, reduced working memory capacity, and mental clouding stemming from neuroinflammation or monoamine deficits.",
        "metadata": {"severity_level": "Moderate", "icd10": "R41.84"}
    },
    "SYMPTOM_BONE_PAIN": {
        "id": "SYMPTOM_BONE_PAIN",
        "name": "Bone Pain & Osteomalacia Discomfort",
        "entity_type": EntityType.SYMPTOM,
        "category": "Musculoskeletal",
        "description": "Deep, aching skeletal pain triggered by unmineralized osteoid collagen matrix hydration swelling against periosteal nerve endings.",
        "metadata": {"severity_level": "Severe", "icd10": "M89.8"}
    },
    "SYMPTOM_MUSCLE_CRAMPS": {
        "id": "SYMPTOM_MUSCLE_CRAMPS",
        "name": "Muscle Cramps & Spasms",
        "entity_type": EntityType.SYMPTOM,
        "category": "Neuromuscular",
        "description": "Involuntary, painful muscle spasms arising from altered intracellular electrolyte gradients and sarcoplasmic calcium clearance failure.",
        "metadata": {"severity_level": "Moderate", "icd10": "R25.2"}
    },
    "SYMPTOM_MUSCLE_WEAKNESS": {
        "id": "SYMPTOM_MUSCLE_WEAKNESS",
        "name": "Muscle Weakness & Sarcopenia",
        "entity_type": EntityType.SYMPTOM,
        "category": "Musculoskeletal",
        "description": "Reduced maximal contractile force and early physical exhaustion caused by myofibrillar protein breakdown or impaired oxidative phosphorylation.",
        "metadata": {"severity_level": "Moderate-Severe", "icd10": "M62.81"}
    },
    "SYMPTOM_POOR_IMMUNITY": {
        "id": "SYMPTOM_POOR_IMMUNITY",
        "name": "Frequent Infections & Poor Immunity",
        "entity_type": EntityType.SYMPTOM,
        "category": "Immunological",
        "description": "Recurrent upper respiratory and cutaneous infections due to impaired T-cell maturation, reduced neutrophil oxidative burst, or compromised mucosal barriers.",
        "metadata": {"severity_level": "Moderate", "icd10": "D84.9"}
    },
    "SYMPTOM_TINGLING_NUMBNESS": {
        "id": "SYMPTOM_TINGLING_NUMBNESS",
        "name": "Peripheral Tingling & Paresthesia",
        "entity_type": EntityType.SYMPTOM,
        "category": "Neurological",
        "description": "Glove-and-stocking sensory paresthesia, burning feet, or numbness caused by sensory nerve demyelination or axonal microvascular ischemia.",
        "metadata": {"severity_level": "Severe", "icd10": "R20.2"}
    },
    "SYMPTOM_DRY_SKIN": {
        "id": "SYMPTOM_DRY_SKIN",
        "name": "Dry Skin & Follicular Hyperkeratosis",
        "entity_type": EntityType.SYMPTOM,
        "category": "Integumentary",
        "description": "Epidermal barrier disruption, xerosis, and plugged follicular papules resulting from abnormal keratinocyte differentiation.",
        "metadata": {"severity_level": "Mild", "icd10": "L85.3"}
    },
    "SYMPTOM_SLOW_WOUND_HEALING": {
        "id": "SYMPTOM_SLOW_WOUND_HEALING",
        "name": "Delayed Wound Healing",
        "entity_type": EntityType.SYMPTOM,
        "category": "Integumentary",
        "description": "Impaired epithelialization and reduced tensile strength of healing tissues due to deficient collagen cross-linking and fibroblast arrest.",
        "metadata": {"severity_level": "Moderate", "icd10": "T81.89"}
    },
    "SYMPTOM_IRRITABILITY": {
        "id": "SYMPTOM_IRRITABILITY",
        "name": "Mood Irritability & Anxiety",
        "entity_type": EntityType.SYMPTOM,
        "category": "Neuropsychiatric",
        "description": "Heightened emotional reactivity, anxiety, and sleep fragmentation linked to altered GABAergic inhibition and central monoamine dysregulation.",
        "metadata": {"severity_level": "Moderate", "icd10": "R45.4"}
    },
    "SYMPTOM_BRITTLE_NAILS": {
        "id": "SYMPTOM_BRITTLE_NAILS",
        "name": "Brittle Nails & Koilonychia",
        "entity_type": EntityType.SYMPTOM,
        "category": "Integumentary",
        "description": "Thin, concave, spoon-shaped, or splitting nail plates caused by matrix iron-dependent enzymatic arrest.",
        "metadata": {"severity_level": "Mild", "icd10": "L60.3"}
    },
    "SYMPTOM_PALE_SKIN": {
        "id": "SYMPTOM_PALE_SKIN",
        "name": "Pallor & Mucosal Blanching",
        "entity_type": EntityType.SYMPTOM,
        "category": "Hematological",
        "description": "Abnormal skin and conjunctival pallor secondary to reduced circulating oxyhemoglobin concentration and peripheral vasoconstriction.",
        "metadata": {"severity_level": "Moderate", "icd10": "R23.1"}
    },
    "SYMPTOM_NIGHT_BLINDNESS": {
        "id": "SYMPTOM_NIGHT_BLINDNESS",
        "name": "Night Blindness (Nyctalopia)",
        "entity_type": EntityType.SYMPTOM,
        "category": "Ophthalmological",
        "description": "Inability to adapt to low-illumination environments caused by retinal rod cell rhodopsin regeneration failure.",
        "metadata": {"severity_level": "Moderate-Severe", "icd10": "H53.6"}
    },
    "SYMPTOM_COLD_INTOLERANCE": {
        "id": "SYMPTOM_COLD_INTOLERANCE",
        "name": "Cold Intolerance & Hypothermia Tendency",
        "entity_type": EntityType.SYMPTOM,
        "category": "Endocrine / Metabolic",
        "description": "Excessive sensitivity to cool environments caused by downregulated basal metabolic thermogenesis and diminished thyroid hormone output.",
        "metadata": {"severity_level": "Moderate", "icd10": "R68.83"}
    },
    "SYMPTOM_MOUTH_ULCERS": {
        "id": "SYMPTOM_MOUTH_ULCERS",
        "name": "Recurrent Aphthous Ulcers & Stomatitis",
        "entity_type": EntityType.SYMPTOM,
        "category": "Gastrointestinal",
        "description": "Painful superficial oral mucosal erosions and angular cheilitis linked to mucosal epithelial rapid turnover failure.",
        "metadata": {"severity_level": "Moderate", "icd10": "K12.0"}
    },
    "SYMPTOM_IRREGULAR_HEARTBEAT": {
        "id": "SYMPTOM_IRREGULAR_HEARTBEAT",
        "name": "Cardiac Palpitations & Arrhythmias",
        "entity_type": EntityType.SYMPTOM,
        "category": "Cardiovascular",
        "description": "Sensation of skipped heartbeats or tachyarrhythmias caused by cardiac myocyte delayed repolarization and prolonged QT intervals.",
        "metadata": {"severity_level": "Severe", "icd10": "R00.2"}
    },
    "SYMPTOM_THYROID_DYSFUNCTION": {
        "id": "SYMPTOM_THYROID_DYSFUNCTION",
        "name": "Goiter & Hypothyroid Signs",
        "entity_type": EntityType.SYMPTOM,
        "category": "Endocrine",
        "description": "Thyroid gland hyperplasia, slowed mentation, constipation, and edema from blunted iodination and peripheral T3 conversion.",
        "metadata": {"severity_level": "Severe", "icd10": "E03.9"}
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 3. FOODS (Nutrient-Dense Clinical Food Sources)
    # ══════════════════════════════════════════════════════════════════════════
    "FOOD_SALMON": {
        "id": "FOOD_SALMON",
        "name": "Wild-Caught Salmon",
        "entity_type": EntityType.FOOD,
        "category": "Seafood",
        "description": "Fatty cold-water fish exceptionally rich in bioavailable calciferol (Vit D), EPA/DHA omega-3s, complete protein, and selenium.",
        "metadata": {"serving": "100g cooked", "key_nutrients": ["Vitamin D", "Protein", "Selenium", "Vitamin B12"]}
    },
    "FOOD_EGGS": {
        "id": "FOOD_EGGS",
        "name": "Pasture-Raised Eggs",
        "entity_type": EntityType.FOOD,
        "category": "Poultry & Dairy",
        "description": "Whole nutrient matrix with high biological value protein, yolk cobalamin, lutein, choline, and fat-soluble vitamins.",
        "metadata": {"serving": "2 whole eggs", "key_nutrients": ["Protein", "Vitamin B12", "Vitamin A", "Choline"]}
    },
    "FOOD_SPINACH": {
        "id": "FOOD_SPINACH",
        "name": "Baby Spinach",
        "entity_type": EntityType.FOOD,
        "category": "Leafy Greens",
        "description": "Dense leafy green offering abundant natural folates, non-heme iron, chlorophyll, carotenoids, and magnesium.",
        "metadata": {"serving": "1 cup cooked", "key_nutrients": ["Folate", "Iron", "Magnesium", "Vitamin A"]}
    },
    "FOOD_LENTILS": {
        "id": "FOOD_LENTILS",
        "name": "Cooked Brown Lentils",
        "entity_type": EntityType.FOOD,
        "category": "Legumes",
        "description": "Complex legume rich in dietary fiber, polyphenols, plant protein, iron, and folate.",
        "metadata": {"serving": "1 cup cooked", "key_nutrients": ["Folate", "Iron", "Protein", "Potassium"]}
    },
    "FOOD_GRASS_FED_BEEF": {
        "id": "FOOD_GRASS_FED_BEEF",
        "name": "Grass-Fed Lean Beef",
        "entity_type": EntityType.FOOD,
        "category": "Meat",
        "description": "Premier source of highly bioavailable heme iron, zinc, cobalamin (B12), and branched-chain amino acids.",
        "metadata": {"serving": "100g cooked", "key_nutrients": ["Iron", "Zinc", "Vitamin B12", "Protein"]}
    },
    "FOOD_GREEK_YOGURT": {
        "id": "FOOD_GREEK_YOGURT",
        "name": "Plain Greek Yogurt",
        "entity_type": EntityType.FOOD,
        "category": "Dairy",
        "description": "Fermented dairy with concentrated casein/whey protein, live probiotic cultures, and bioavailable calcium.",
        "metadata": {"serving": "1 cup (200g)", "key_nutrients": ["Calcium", "Protein", "Vitamin B2", "Vitamin B12"]}
    },
    "FOOD_ALMONDS": {
        "id": "FOOD_ALMONDS",
        "name": "Raw Almonds",
        "entity_type": EntityType.FOOD,
        "category": "Nuts & Seeds",
        "description": "Tree nut containing alpha-tocopherol (Vitamin E), magnesium, riboflavin, and plant sterols.",
        "metadata": {"serving": "30g (1 oz)", "key_nutrients": ["Vitamin E", "Magnesium", "Calcium"]}
    },
    "FOOD_PUMPKIN_SEEDS": {
        "id": "FOOD_PUMPKIN_SEEDS",
        "name": "Raw Pumpkin Seeds (Pepitas)",
        "entity_type": EntityType.FOOD,
        "category": "Nuts & Seeds",
        "description": "Mineral-packed seed rich in bioavailable zinc, magnesium, phosphorus, and essential fatty acids.",
        "metadata": {"serving": "30g (1 oz)", "key_nutrients": ["Zinc", "Magnesium", "Iron", "Potassium"]}
    },
    "FOOD_SARDINES": {
        "id": "FOOD_SARDINES",
        "name": "Sardines in Olive Oil (with Bones)",
        "entity_type": EntityType.FOOD,
        "category": "Seafood",
        "description": "Small pelagic fish providing soft calcium-rich bones, Vitamin D, cobalamin, and marine lipids.",
        "metadata": {"serving": "1 can (85g)", "key_nutrients": ["Calcium", "Vitamin D", "Vitamin B12", "Protein"]}
    },
    "FOOD_OYSTERS": {
        "id": "FOOD_OYSTERS",
        "name": "Pacific Oysters",
        "entity_type": EntityType.FOOD,
        "category": "Seafood",
        "description": "Bivalve mollusk with the highest natural concentration of zinc, along with copper, selenium, and B12.",
        "metadata": {"serving": "6 medium raw (84g)", "key_nutrients": ["Zinc", "Vitamin B12", "Copper", "Selenium"]}
    },
    "FOOD_NUTRITIONAL_YEAST": {
        "id": "FOOD_NUTRITIONAL_YEAST",
        "name": "Fortified Nutritional Yeast",
        "entity_type": EntityType.FOOD,
        "category": "Plant Derivative",
        "description": "Deactivated Saccharomyces cerevisiae rich in complete protein, beta-glucans, and the full B-complex spectrum.",
        "metadata": {"serving": "2 tbsp (10g)", "key_nutrients": ["Vitamin B1", "Vitamin B2", "Vitamin B3", "Vitamin B6", "Vitamin B12"]}
    },
    "FOOD_AVOCADO": {
        "id": "FOOD_AVOCADO",
        "name": "Hass Avocado",
        "entity_type": EntityType.FOOD,
        "category": "Fruit",
        "description": "Monounsaturated fatty fruit providing dense potassium (more than bananas), folate, lutein, and Vitamin E.",
        "metadata": {"serving": "1 medium", "key_nutrients": ["Potassium", "Folate", "Vitamin E", "Magnesium"]}
    },
    "FOOD_CITRUS_FRUITS": {
        "id": "FOOD_CITRUS_FRUITS",
        "name": "Oranges & Lemons",
        "entity_type": EntityType.FOOD,
        "category": "Fruit",
        "description": "Citrus fruits loaded with L-ascorbic acid, bioflavonoids, and citric acid which enhance mineral uptake.",
        "metadata": {"serving": "1 large orange", "key_nutrients": ["Vitamin C", "Folate", "Potassium"]}
    },
    "FOOD_BRAZIL_NUTS": {
        "id": "FOOD_BRAZIL_NUTS",
        "name": "Brazil Nuts",
        "entity_type": EntityType.FOOD,
        "category": "Nuts & Seeds",
        "description": "Premier terrestrial source of organic selenomethionine, providing 100%+ daily selenium in a single nut.",
        "metadata": {"serving": "1-2 nuts (10g)", "key_nutrients": ["Selenium", "Magnesium", "Vitamin E"]}
    },
    "FOOD_SEAWEED": {
        "id": "FOOD_SEAWEED",
        "name": "Kelp / Nori Seaweed",
        "entity_type": EntityType.FOOD,
        "category": "Marine Botanical",
        "description": "Marine macroalgae with exceptional iodine concentration essential for thyroid hormone synthesis.",
        "metadata": {"serving": "1 sheet nori / 1g kelp", "key_nutrients": ["Iodine", "Potassium", "Iron"]}
    },
    "FOOD_SWEET_POTATO": {
        "id": "FOOD_SWEET_POTATO",
        "name": "Baked Sweet Potato",
        "entity_type": EntityType.FOOD,
        "category": "Tubers",
        "description": "Complex orange tuber rich in beta-carotene (provitamin A), potassium, dietary fiber, and Vitamin C.",
        "metadata": {"serving": "1 medium baked", "key_nutrients": ["Vitamin A", "Potassium", "Vitamin C"]}
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 4. LIFESTYLE FACTORS (Behavioral & Environmental Drivers)
    # ══════════════════════════════════════════════════════════════════════════
    "LIFESTYLE_LOW_SUN": {
        "id": "LIFESTYLE_LOW_SUN",
        "name": "Low Sun Exposure & Indoor Confinement",
        "entity_type": EntityType.LIFESTYLE_FACTOR,
        "category": "Environmental",
        "description": "Insufficient dermal ultraviolet-B (UVB, 290-315nm) radiation exposure preventing 7-dehydrocholesterol conversion into cholecalciferol.",
        "metadata": {"risk_level": "High", "modifiable": True}
    },
    "LIFESTYLE_POOR_SLEEP": {
        "id": "LIFESTYLE_POOR_SLEEP",
        "name": "Chronic Sleep Deprivation & Shift Work",
        "entity_type": EntityType.LIFESTYLE_FACTOR,
        "category": "Behavioral",
        "description": "Fragmented or <6h sleep perturbing nocturnal cellular repair, growth hormone release, and metabolic oxidative balance.",
        "metadata": {"risk_level": "Moderate", "modifiable": True}
    },
    "LIFESTYLE_HIGH_STRESS": {
        "id": "LIFESTYLE_HIGH_STRESS",
        "name": "Chronic Neuroendocrine Stress",
        "entity_type": EntityType.LIFESTYLE_FACTOR,
        "category": "Psychosocial",
        "description": "Sustained HPA axis activation and hypercortisolemia increasing urinary excretion of water-soluble B vitamins and magnesium.",
        "metadata": {"risk_level": "High", "modifiable": True}
    },
    "LIFESTYLE_SMOKING": {
        "id": "LIFESTYLE_SMOKING",
        "name": "Tobacco & Nicotine Smoking",
        "entity_type": EntityType.LIFESTYLE_FACTOR,
        "category": "Behavioral",
        "description": "Inhalation of combustion oxidants generating massive free-radical loads and accelerating ascorbic acid and antioxidant turnover.",
        "metadata": {"risk_level": "High", "modifiable": True}
    },
    "LIFESTYLE_ALCOHOL": {
        "id": "LIFESTYLE_ALCOHOL",
        "name": "Excess Alcohol Consumption",
        "entity_type": EntityType.LIFESTYLE_FACTOR,
        "category": "Behavioral",
        "description": "Ethanol toxicity damaging intestinal brush-border transporters, impairing hepatic storage, and inducing renal electrolyte wasting.",
        "metadata": {"risk_level": "High", "modifiable": True}
    },
    "LIFESTYLE_STRICT_VEGAN": {
        "id": "LIFESTYLE_STRICT_VEGAN",
        "name": "Strict Unsupplemented Vegan Diet",
        "entity_type": EntityType.LIFESTYLE_FACTOR,
        "category": "Dietary Pattern",
        "description": "Total absence of animal-derived foods without fortified sources, creating severe vulnerabilities for cobalamin, heme iron, and bioavailable zinc.",
        "metadata": {"risk_level": "High", "modifiable": True}
    },
    "LIFESTYLE_SEDENTARY": {
        "id": "LIFESTYLE_SEDENTARY",
        "name": "Sedentary Physical Behavior",
        "entity_type": EntityType.LIFESTYLE_FACTOR,
        "category": "Behavioral",
        "description": "Absence of mechanical bone loading and muscular contraction leading to accelerated osteopenia and reduced metabolic insulin sensitivity.",
        "metadata": {"risk_level": "Moderate", "modifiable": True}
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 5. MEDICAL CONDITIONS (Pathophysiologies & Comorbidities)
    # ══════════════════════════════════════════════════════════════════════════
    "CONDITION_CELIAC": {
        "id": "CONDITION_CELIAC",
        "name": "Celiac Disease (Gluten Enteropathy)",
        "entity_type": EntityType.MEDICAL_CONDITION,
        "category": "Gastroenterology",
        "description": "Autoimmune small-bowel villous atrophy severely blunting proximal duodenal iron, folate, and general micronutrient absorption.",
        "metadata": {"icd10": "K90.0", "pathology": "Villous blunting, crypt hyperplasia"}
    },
    "CONDITION_CROHNS": {
        "id": "CONDITION_CROHNS",
        "name": "Crohn's Disease & Terminal Ileitis",
        "entity_type": EntityType.MEDICAL_CONDITION,
        "category": "Gastroenterology",
        "description": "Transmural inflammation of the gastrointestinal tract, especially terminal ileum, impairing active B12-intrinsic factor and bile acid uptake.",
        "metadata": {"icd10": "K50.9", "pathology": "Transmural inflammation, ileal malabsorption"}
    },
    "CONDITION_ATROPHIC_GASTRITIS": {
        "id": "CONDITION_ATROPHIC_GASTRITIS",
        "name": "Chronic Atrophic Gastritis & Achlorhydria",
        "entity_type": EntityType.MEDICAL_CONDITION,
        "category": "Gastroenterology",
        "description": "Gastric parietal cell loss eliminating hydrochloric acid and intrinsic factor, preventing food-bound B12 and non-heme iron extraction.",
        "metadata": {"icd10": "K29.4", "pathology": "Parietal cell atrophy, hypochlorhydria"}
    },
    "CONDITION_BARIATRIC": {
        "id": "CONDITION_BARIATRIC",
        "name": "Post-Bariatric Roux-en-Y Surgery",
        "entity_type": EntityType.MEDICAL_CONDITION,
        "category": "Surgical / Anatomy",
        "description": "Surgical bypass of the duodenum and proximal jejunum preventing acid mixing and physiological absorption of iron, calcium, B1, and B12.",
        "metadata": {"icd10": "Z98.84", "pathology": "Anatomic bypass of primary absorptive zones"}
    },
    "CONDITION_HYPOTHYROIDISM": {
        "id": "CONDITION_HYPOTHYROIDISM",
        "name": "Hypothyroidism & Hashimoto's Thyroiditis",
        "entity_type": EntityType.MEDICAL_CONDITION,
        "category": "Endocrinology",
        "description": "Suboptimal thyroid hormone synthesis causing hypometabolism, cold intolerance, slow GI transit, and blunted carotenoid conversion to Vitamin A.",
        "metadata": {"icd10": "E03.9", "pathology": "Autoimmune thyroid gland destruction"}
    },
    "CONDITION_CKD": {
        "id": "CONDITION_CKD",
        "name": "Chronic Kidney Disease (Stages 3-5)",
        "entity_type": EntityType.MEDICAL_CONDITION,
        "category": "Nephrology",
        "description": "Renal parenchymal loss impairing 1-alpha-hydroxylase calcitriol synthesis, causing hyperphosphatemia, hypocalcemia, and renal osteodystrophy.",
        "metadata": {"icd10": "N18.9", "pathology": "Loss of 1-alpha-hydroxylase and erythropoietin"}
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 6. LABORATORY TESTS (Diagnostic Biomarkers & Clinical Decision Points)
    # ══════════════════════════════════════════════════════════════════════════
    "LAB_FERRITIN": {
        "id": "LAB_FERRITIN",
        "name": "Serum Ferritin Panel",
        "entity_type": EntityType.LAB_TEST,
        "category": "Hematology",
        "description": "Primary iron-storage glycoprotein; values < 30 ng/mL demonstrate depleted bone marrow iron stores prior to microcytic anemia onset.",
        "metadata": {"normal_range": "30 - 300 ng/mL", "cutoff_deficiency": "< 30 ng/mL"}
    },
    "LAB_CBC": {
        "id": "LAB_CBC",
        "name": "Complete Blood Count (CBC & MCV)",
        "entity_type": EntityType.LAB_TEST,
        "category": "Hematology",
        "description": "Quantifies hemoglobin, hematocrit, and Mean Corpuscular Volume (MCV: low in iron deficiency < 80 fL; high in B12/folate deficiency > 100 fL).",
        "metadata": {"normal_mcv": "80 - 100 fL", "normal_hb": "12.0 - 17.5 g/dL"}
    },
    "LAB_VITAMIN_D": {
        "id": "LAB_VITAMIN_D",
        "name": "Serum 25-Hydroxy Vitamin D [25(OH)D]",
        "entity_type": EntityType.LAB_TEST,
        "category": "Endocrinology",
        "description": "Circulating prehormone metric reflecting total cutaneous and dietary Vitamin D sufficiency.",
        "metadata": {"cutoff_deficiency": "< 20 ng/mL", "optimal_range": "30 - 60 ng/mL"}
    },
    "LAB_B12": {
        "id": "LAB_B12",
        "name": "Serum Cobalamin (Total B12)",
        "entity_type": EntityType.LAB_TEST,
        "category": "Biochemistry",
        "description": "Circulating cobalamin concentration; borderline values (200-350 pg/mL) require confirmatory MMA testing.",
        "metadata": {"cutoff_deficiency": "< 200 pg/mL", "optimal_range": "400 - 900 pg/mL"}
    },
    "LAB_MMA": {
        "id": "LAB_MMA",
        "name": "Serum / Urine Methylmalonic Acid (MMA)",
        "entity_type": EntityType.LAB_TEST,
        "category": "Functional Biomarker",
        "description": "Gold-standard functional marker of intracellular Vitamin B12 deficiency; mutase inactivity triggers systemic MMA elevation.",
        "metadata": {"normal_range": "< 0.40 umol/L", "cutoff_deficiency": "> 0.40 umol/L"}
    },
    "LAB_RBC_FOLATE": {
        "id": "LAB_RBC_FOLATE",
        "name": "Red Blood Cell (RBC) Folate",
        "entity_type": EntityType.LAB_TEST,
        "category": "Hematology",
        "description": "Intra-erythrocytic folate concentration reflecting long-term tissue storage over the preceding 120-day red cell lifespan.",
        "metadata": {"cutoff_deficiency": "< 140 ng/mL", "optimal_range": "> 300 ng/mL"}
    },
    "LAB_MAGNESIUM": {
        "id": "LAB_MAGNESIUM",
        "name": "Serum & RBC Magnesium",
        "entity_type": EntityType.LAB_TEST,
        "category": "Biochemistry",
        "description": "Total serum magnesium and RBC intracellular magnesium measuring cellular cofactor reserves.",
        "metadata": {"normal_serum": "1.7 - 2.2 mg/dL", "optimal_rbc": "> 5.5 mg/dL"}
    },
    "LAB_ZINC_PLASMA": {
        "id": "LAB_ZINC_PLASMA",
        "name": "Plasma / Serum Zinc Test",
        "entity_type": EntityType.LAB_TEST,
        "category": "Trace Elements",
        "description": "Fasting morning plasma zinc concentration evaluating circulating zinc pool; susceptible to acute-phase reactant suppression.",
        "metadata": {"normal_range": "70 - 120 mcg/dL", "cutoff_deficiency": "< 70 mcg/dL"}
    },
    "LAB_POTASSIUM": {
        "id": "LAB_POTASSIUM",
        "name": "Serum Potassium Electrolyte Test",
        "entity_type": EntityType.LAB_TEST,
        "category": "Electrolytes",
        "description": "Critical electrolyte assay evaluating cardiac conduction stability and hypokalemia risk.",
        "metadata": {"normal_range": "3.5 - 5.0 mEq/L", "cutoff_hypokalemia": "< 3.5 mEq/L"}
    },
    "LAB_THYROID": {
        "id": "LAB_THYROID",
        "name": "Serum TSH & Free T4 / Free T3 Panel",
        "entity_type": EntityType.LAB_TEST,
        "category": "Endocrinology",
        "description": "Pituitary thyroid-stimulating hormone and unbound thyroxine assessing thyroid gland organification status.",
        "metadata": {"normal_tsh": "0.45 - 4.5 mIU/L", "normal_ft4": "0.8 - 1.8 ng/dL"}
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 7. BIOLOGICAL SYSTEMS (The 6 Core Physiological Body Systems)
    # ══════════════════════════════════════════════════════════════════════════
    "SYSTEM_IMMUNE": {
        "id": "SYSTEM_IMMUNE",
        "name": "Immune & Defense System",
        "entity_type": EntityType.BIOLOGICAL_SYSTEM,
        "category": "Physiological System",
        "description": "Innate and adaptive immunological barriers, neutrophil phagocytosis, T/B lymphocyte proliferation, and cytokine orchestration.",
        "metadata": {"critical_nutrients": ["Zinc", "Vitamin C", "Vitamin D", "Vitamin A", "Protein", "Selenium"]}
    },
    "SYSTEM_NEUROLOGICAL": {
        "id": "SYSTEM_NEUROLOGICAL",
        "name": "Neurological & Cognitive System",
        "entity_type": EntityType.BIOLOGICAL_SYSTEM,
        "category": "Physiological System",
        "description": "Central and peripheral nervous system conduction, myelin sheath maintenance, neurotransmitter synthesis, and synaptic plasticity.",
        "metadata": {"critical_nutrients": ["Vitamin B12", "Vitamin B1", "Vitamin B6", "Folate", "Magnesium", "Potassium"]}
    },
    "SYSTEM_MUSCULOSKELETAL": {
        "id": "SYSTEM_MUSCULOSKELETAL",
        "name": "Musculoskeletal & Skeletal System",
        "entity_type": EntityType.BIOLOGICAL_SYSTEM,
        "category": "Physiological System",
        "description": "Bone mineral density, osteoclast/osteoblast remodeling, skeletal muscle protein mass, and excitation-contraction mechanics.",
        "metadata": {"critical_nutrients": ["Vitamin D", "Calcium", "Protein", "Magnesium", "Potassium"]}
    },
    "SYSTEM_CARDIOVASCULAR": {
        "id": "SYSTEM_CARDIOVASCULAR",
        "name": "Cardiovascular & Hematological System",
        "entity_type": EntityType.BIOLOGICAL_SYSTEM,
        "category": "Physiological System",
        "description": "Erythrocyte oxygenation, vascular endothelial tone, myocardial contractility, and cardiac action potential repolarization.",
        "metadata": {"critical_nutrients": ["Iron", "Potassium", "Vitamin B12", "Folate", "Magnesium", "Vitamin B1"]}
    },
    "SYSTEM_ENDOCRINE": {
        "id": "SYSTEM_ENDOCRINE",
        "name": "Endocrine & Hormonal System",
        "entity_type": EntityType.BIOLOGICAL_SYSTEM,
        "category": "Physiological System",
        "description": "Pituitary, thyroid, parathyroid, and adrenal gland feedback loops regulating basal metabolic rate and systemic calcium homeostasis.",
        "metadata": {"critical_nutrients": ["Iodine", "Selenium", "Vitamin D", "Zinc", "Magnesium"]}
    },
    "SYSTEM_METABOLIC": {
        "id": "SYSTEM_METABOLIC",
        "name": "Metabolic & Cellular Bioenergetics",
        "entity_type": EntityType.BIOLOGICAL_SYSTEM,
        "category": "Physiological System",
        "description": "Mitochondrial Krebs cycle, oxidative phosphorylation, ATP generation, DNA repair, and systemic antioxidant glutathione recycling.",
        "metadata": {"critical_nutrients": ["Vitamin B1", "Vitamin B2", "Vitamin B3", "Magnesium", "Protein", "Selenium"]}
    }
}
