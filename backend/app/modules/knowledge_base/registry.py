"""
Clinical Knowledge Base Registry
Phase 7A: Nutrient Expansion & Clinical Knowledge Base Enhancement

Comprehensive evidence-based database covering all 18 monitored nutrients:
- 11 Baseline Nutrients: Protein, Vitamin A, Vitamin B12, Folate, Vitamin C, Vitamin D, Vitamin E, Iron, Calcium, Zinc, Magnesium
- 7 Expanded Nutrients: Vitamin B1 (Thiamine), Vitamin B2 (Riboflavin), Vitamin B3 (Niacin), Vitamin B6 (Pyridoxine), Potassium, Selenium, Iodine
"""

from typing import Dict, Any, List, Optional
from .schemas import ClinicalNutrientProfile, DietaryIntakeRef, EvidenceCitations

CLINICAL_NUTRIENT_REGISTRY: Dict[str, Dict[str, Any]] = {
    "VITAMIN_B1": {
        "nutrient_code": "VITAMIN_B1",
        "common_name": "Vitamin B1 (Thiamine)",
        "category": "Water-Soluble Vitamin",
        "active_vitamers": ["Thiamine Pyrophosphate (TPP)", "Thiamine Diphosphate (ThDP)", "Thiamine Monophosphate"],
        "clinical_role": "Obligate coenzyme for pyruvate dehydrogenase, alpha-ketoglutarate dehydrogenase, and transketolase in glucose oxidative metabolism and ATP generation. Critical for central nervous system myelin stability and cardiac contractility.",
        "daily_recommended_intake": {
            "standard_adult_male": "1.2 mg/day",
            "standard_adult_female": "1.1 mg/day",
            "pregnancy_lactation": "1.4 mg/day",
            "tolerable_upper_limit": "No established UL due to rapid renal clearance; parenteral doses > 100mg safe under clinical oversight."
        },
        "toxicity_limits": "No established Tolerable Upper Intake Level (UL). Excess oral doses are eliminated rapidly via renal excretion; exceptionally rare anaphylactoid reactions reported with rapid intravenous bolus.",
        "deficiency_symptoms": [
            "Severe fatigue & generalized muscular weakness",
            "Irritability, mood lability, and sleep fragmentation",
            "Loss of appetite, nausea, and gastroparesis",
            "Peripheral neuropathy (burning feet syndrome, loss of ankle reflexes)",
            "High-output heart failure (Wet Beriberi)",
            "Wernicke-Korsakoff syndrome (ocular ophthalmoplegia, ataxia, acute confusion)"
        ],
        "high_risk_populations": [
            "Individuals with chronic heavy alcohol intake (impaired brush-border transport & storage)",
            "Patients following bariatric Roux-en-Y gastric bypass",
            "Individuals on chronic high-dose loop diuretics (elevated urinary wasting)",
            "Patients with anorexia nervosa or prolonged hyperemesis gravidarum",
            "Elderly individuals on low-variety refined carbohydrate diets"
        ],
        "key_dietary_sources": [
            "Enriched or whole-grain brown rice and nutritional yeast",
            "Sunflower seeds, flaxseeds, and sesame tahini",
            "Black beans, green peas, and French green lentils",
            "Pasture-raised pork tenderloin and trout"
        ],
        "absorption_enhancers": ["Magnesium (obligate cofactor for thiamine pyrophosphokinase)", "Adequate dietary protein"],
        "absorption_inhibitors": ["Ethanol (inhibits active intestinal thiamine transporter ThTr-1)", "Thermal degradation (>100°C prolonged boiling)", "Thiaminases in raw freshwater fish and betel nuts", "Chronic loop diuretics (furosemide)"],
        "citations": {
            "who_reference": "World Health Organization: Thiamine deficiency and its prevention and control in major emergencies (WHO/NHD/99.13).",
            "nih_reference": "NIH Office of Dietary Supplements: Thiamin Health Professional Fact Sheet.",
            "additional_guidelines": ["EFSA Scientific Opinion on Dietary Reference Values for Thiamine (2016)."]
        }
    },

    "VITAMIN_B2": {
        "nutrient_code": "VITAMIN_B2",
        "common_name": "Vitamin B2 (Riboflavin)",
        "category": "Water-Soluble Vitamin",
        "active_vitamers": ["Flavin Mononucleotide (FMN)", "Flavin Adenine Dinucleotide (FAD)"],
        "clinical_role": "Central electron carrier coenzyme in the mitochondrial respiratory chain (Complex I and Complex II). Essential for fatty acid beta-oxidation, conversion of tryptophan to niacin, activation of Vitamin B6 to PLP, and regeneration of reduced glutathione via glutathione reductase.",
        "daily_recommended_intake": {
            "standard_adult_male": "1.3 mg/day",
            "standard_adult_female": "1.1 mg/day",
            "pregnancy_lactation": "1.4 - 1.6 mg/day",
            "tolerable_upper_limit": "No established UL; intestinal transport saturation at ~27 mg per single dose limits toxicity."
        },
        "toxicity_limits": "No established UL. Excess riboflavin is excreted in urine, imparting an intense, benign fluorescent yellow-green color (flavinuria).",
        "deficiency_symptoms": [
            "Angular cheilosis (painful fissure cracks at lip corners)",
            "Magenta-hued swollen glossitis and mucosal mouth ulcers",
            "Normocytic normochromic anemia (secondary to impaired iron mobilization)",
            "Photophobia, burning ocular conjunctivitis, and corneal vascularization",
            "Seborrheic dermatitis around nasolabial folds and scrotum"
        ],
        "high_risk_populations": [
            "Strict vegans and individuals on dairy-free diets without enriched alternatives",
            "Vegetarian pregnant and lactating women",
            "Individuals with Riboflavin Transporter Deficiency (Brown-Vialetto-Van Laere syndrome)",
            "Endurance athletes with low energy intake",
            "Alcohol-dependent patients"
        ],
        "key_dietary_sources": [
            "Fortified nutritional yeast (delivers >500% RDA/serving)",
            "Organic whole milk, Greek yogurt, and aged cheeses",
            "Pasture-raised whole eggs and organ meats (beef liver)",
            "Raw almonds, cremini mushrooms, and dark leafy greens (spinach)"
        ],
        "absorption_enhancers": ["Gastric hydrochloric acid (liberates flavins from dietary proteins)", "Presence of meal dietary lipids"],
        "absorption_inhibitors": ["Photodegradation (UV and visible light rapidly cleaves riboflavin to lumiflavin)", "Chronic alcoholism", "Tricyclic antidepressants and phenothiazines (competitive inhibition of riboflavin kinase)"],
        "citations": {
            "who_reference": "World Health Organization: Vitamin and mineral requirements in human nutrition (2nd Edition).",
            "nih_reference": "NIH Office of Dietary Supplements: Riboflavin Fact Sheet for Health Professionals.",
            "additional_guidelines": ["Institute of Medicine (US) Dietary Reference Intakes for Thiamin, Riboflavin, Niacin, Vitamin B6, Folate, Vitamin B12."]
        }
    },

    "VITAMIN_B3": {
        "nutrient_code": "VITAMIN_B3",
        "common_name": "Vitamin B3 (Niacin / Nicotinamide)",
        "category": "Water-Soluble Vitamin",
        "active_vitamers": ["Nicotinamide Adenine Dinucleotide (NAD+)", "Nicotinamide Adenine Dinucleotide Phosphate (NADP+)", "Nicotinamide", "Nicotinic Acid"],
        "clinical_role": "Participates in >400 biochemical enzymatic oxidation-reduction reactions across glycolysis, Krebs cycle, and lipid synthesis. Crucial substrate for poly(ADP-ribose) polymerases (PARPs) responsible for DNA repair, genome stability, and sirtuin longevity enzymes.",
        "daily_recommended_intake": {
            "standard_adult_male": "16 mg NE/day (Niacin Equivalents)",
            "standard_adult_female": "14 mg NE/day",
            "pregnancy_lactation": "17 - 18 mg NE/day",
            "tolerable_upper_limit": "35 mg/day of synthetic/fortified nicotinic acid in adults (based on cutaneous prostaglandin flushing)."
        },
        "toxicity_limits": "High-dose nicotinic acid (>500 mg/day) produces transient prostaglandin-mediated cutaneous flushing and pruritus; sustained doses >1000 mg/day risk hepatotoxicity, hyperuricemia, and impaired insulin sensitivity.",
        "deficiency_symptoms": [
            "Classic Pellagra triad/tetrad: Photosensitive dermatitis, Diarrhea, Dementia, Death",
            "Bilateral symmetric erythema and hyperkeratosis on sun-exposed skin (Casal's necklace)",
            "Chronic watery diarrhea, nausea, and abdominal cramping",
            "Cognitive memory lapses, disorientation, depression, and severe fatigue",
            "Beefy red inflamed tongue and stomatitis"
        ],
        "high_risk_populations": [
            "Populations consuming un-nixtamalized corn/maize as primary caloric staple",
            "Individuals with severe alcohol use disorder",
            "Patients with Carcinoid Syndrome (diverts >70% tryptophan to serotonin away from NAD)",
            "Hartnup disease (impaired neutral amino acid transport)",
            "Chronic malabsorption (Crohn's disease, prolonged hemodialysis)"
        ],
        "key_dietary_sources": [
            "Free-range chicken breast and roasted turkey",
            "Wild yellowfin tuna, Atlantic salmon, and sardines",
            "Dry-roasted peanuts and peanut butter",
            "Fortified nutritional yeast and brown rice",
            "Cooked lentils and Portobello mushrooms"
        ],
        "absorption_enhancers": ["Adequate dietary protein (60 mg dietary tryptophan generates 1 mg niacin equivalent)", "Vitamin B6, B2, and Iron cofactors"],
        "absorption_inhibitors": ["Un-nixtamalized maize (niacytin complexed to hemicellulose requires alkaline lime treatment)", "Isoniazid and 6-mercaptopurine pharmacological therapies", "Alcohol toxicity"],
        "citations": {
            "who_reference": "World Health Organization: Pellagra and its prevention and control in major emergencies (WHO/NHD/00.10).",
            "nih_reference": "NIH Office of Dietary Supplements: Niacin Fact Sheet for Health Professionals.",
            "additional_guidelines": ["European Food Safety Authority: Tolerable upper intake levels for vitamins and minerals."]
        }
    },

    "VITAMIN_B6": {
        "nutrient_code": "VITAMIN_B6",
        "common_name": "Vitamin B6 (Pyridoxine)",
        "category": "Water-Soluble Vitamin",
        "active_vitamers": ["Pyridoxal 5'-Phosphate (PLP - active form)", "Pyridoxine", "Pyridoxamine"],
        "clinical_role": "Primary coenzyme for >140 enzymatic reactions in amino acid decarboxylation, transamination, and transsulfuration. Catalyzes delta-aminolevulinic acid synthase in heme synthesis, converts homocysteine to cystathionine, and produces neurotransmitters (serotonin, dopamine, GABA, norepinephrine).",
        "daily_recommended_intake": {
            "standard_adult_male": "1.3 mg/day (1.7 mg/day if >50 years)",
            "standard_adult_female": "1.3 mg/day (1.5 mg/day if >50 years)",
            "pregnancy_lactation": "1.9 - 2.0 mg/day",
            "tolerable_upper_limit": "100 mg/day in adults (established to prevent sensory peripheral neuropathy)."
        },
        "toxicity_limits": "Chronic supplemental intake exceeding 200-500 mg/day induces progressive sensory peripheral neuropathy, ataxia, and dermatological lesions. Reversible upon prompt cessation.",
        "deficiency_symptoms": [
            "Microcytic hypochromic sideroblastic anemia with elevated serum ferritin",
            "Peripheral symmetrical polyneuropathy (burning tingling extremities)",
            "Electroencephalographic abnormalities, irritability, depression, and seizures",
            "Seborrheic dermatitis around eyebrows and nasolabial folds",
            "Angular stomatitis and cheilosis",
            "Hyperhomocysteinemia elevating cardiovascular atherothrombotic risk"
        ],
        "high_risk_populations": [
            "Patients on long-term Isoniazid (INH), hydralazine, penicillamine, or L-DOPA medications",
            "Individuals with end-stage renal disease (ESRD) on peritoneal or hemodialysis",
            "Chronic alcoholics (acetaldehyde accelerates cellular PLP degradation)",
            "Patients with autoimmune rheumatoid arthritis or celiac disease",
            "Women taking oral contraceptive formulations"
        ],
        "key_dietary_sources": [
            "Cooked chickpeas / garbanzo beans (1.1 mg per cup)",
            "Wild Alaskan sockeye salmon and pasture-raised poultry",
            "Fresh yellow bananas and baked potatoes with skin",
            "Avocados, pistachios, and sunflower seeds"
        ],
        "absorption_enhancers": ["Flavin Mononucleotide (FMN / Vitamin B2) for intestinal conversion to PLP", "Normal gastric acidity"],
        "absorption_inhibitors": ["Isoniazid and levodopa (form inactive hydrazone complexes with PLP)", "Alcohol (impairs hepatic pyridoxal kinase)", "Thermal cooking loss (up to 40-50% in processed foods)"],
        "citations": {
            "who_reference": "World Health Organization: Guidelines on Food Fortification with Micronutrients.",
            "nih_reference": "NIH Office of Dietary Supplements: Vitamin B6 Fact Sheet for Health Professionals.",
            "additional_guidelines": ["Endocrine and Neurological Complications of Vitamin B6 Deficiencies (Lancet Neurology)."]
        }
    },

    "POTASSIUM": {
        "nutrient_code": "POTASSIUM",
        "common_name": "Potassium",
        "category": "Macromineral",
        "active_vitamers": ["Ionic Potassium (K+)", "Intracellular Potassium"],
        "clinical_role": "Predominant intracellular cation (98% intracellular, ~140-150 mEq/L). Maintains resting cell membrane potential, drives neuromuscular excitation, fuels cardiac electrical conduction via delayed rectifier potassium channels, and counteracts sodium-induced vascular hypertension.",
        "daily_recommended_intake": {
            "standard_adult_male": "3,400 mg/day (Adequate Intake - AI)",
            "standard_adult_female": "2,600 mg/day (Adequate Intake - AI)",
            "pregnancy_lactation": "2,800 - 2,900 mg/day",
            "tolerable_upper_limit": "No UL established for dietary potassium in healthy renal function; critical caution in chronic kidney disease."
        },
        "toxicity_limits": "Excess dietary intake in healthy individuals is handled by aldosterone-mediated renal secretion. In acute oliguric renal failure or with ACE inhibitors/spironolactone, hyperkalemia (>5.5 mEq/L) risks fatal ventricular fibrillation and asystole.",
        "deficiency_symptoms": [
            "Profound muscular weakness, ascending flaccid paralysis, and hypoventilation",
            "Painful nocturnal calf cramps and fasciculations",
            "Cardiac dysrhythmias (prominent U waves, ST depression, ventricular ectopy)",
            "Paralytic ileus, severe constipation, and abdominal distension",
            "Metabolic alkalosis and persistent polyuria/polydipsia",
            "Elevated systolic blood pressure and heightened stroke risk"
        ],
        "high_risk_populations": [
            "Patients on non-potassium-sparing loop or thiazide diuretics",
            "Individuals with severe chronic diarrhea, vomiting, or laxative abuse",
            "Patients with primary or secondary hyperaldosteronism",
            "Populations consuming ultra-processed low-plant modern Western diets",
            "Individuals with concurrent hypomagnesemia (refractory potassium wasting)"
        ],
        "key_dietary_sources": [
            "Baked Russet or sweet potato with skin intact (900-950 mg each)",
            "Cooked spinach, Swiss chard, and beet greens",
            "Hass avocados (700 mg per whole avocado) and fresh bananas",
            "White beans, adzuki beans, and lentils",
            "Coconut water (unsweetened) and wild Atlantic salmon"
        ],
        "absorption_enhancers": ["Magnesium (supports Na+/K+ ATPase activity and closes renal ROMK potassium channels)"],
        "absorption_inhibitors": ["High sodium-to-potassium dietary ratio", "Profuse diaphoresis/sweating in hot environments", "Loop/thiazide diuretics and high glucocorticoid levels", "Chronic metabolic acidosis"],
        "citations": {
            "who_reference": "WHO Guideline: Potassium intake for adults and children (Geneva, World Health Organization, 2012).",
            "nih_reference": "NIH Office of Dietary Supplements: Potassium Fact Sheet for Health Professionals.",
            "additional_guidelines": ["American Heart Association Guideline on Potassium and Cardiovascular Health."]
        }
    },

    "SELENIUM": {
        "nutrient_code": "SELENIUM",
        "common_name": "Selenium",
        "category": "Trace Mineral",
        "active_vitamers": ["Selenocysteine (21st amino acid)", "Selenomethionine", "Selenite", "Selenate"],
        "clinical_role": "Essential catalytic constituent of 25 human selenoproteins. Forms active catalytic sites of glutathione peroxidases (GPx1-4) protecting lipid membranes from oxidative peroxides, and iodothyronine deiodinases (DIO1-3) converting T4 to active T3 thyroid hormone.",
        "daily_recommended_intake": {
            "standard_adult_male": "55 mcg/day",
            "standard_adult_female": "55 mcg/day",
            "pregnancy_lactation": "60 - 70 mcg/day",
            "tolerable_upper_limit": "400 mcg/day in adults (established to prevent chronic selenosis)."
        },
        "toxicity_limits": "Chronic intake >400-800 mcg/day produces Selenosis: garlic-like breath odor (dimethyl selenide), brittle ridged nails, patchy alopecia, peripheral neuropathy, and tooth discoloration.",
        "deficiency_symptoms": [
            "Impaired thyroid hormone activation (hypothyroidism symptoms despite adequate iodine)",
            "Endemic congestive cardiomyopathy (Keshan disease)",
            "Osteochondropathy with joint deformation (Kashin-Beck disease)",
            "Diffuse hair loss, nail fragility, and leukonychia",
            "Weakened cell-mediated antiviral immune defenses (heightened viral mutation risk)",
            "Elevated oxidative stress and male reproductive infertility (impaired sperm motility)"
        ],
        "high_risk_populations": [
            "Individuals living in geographic regions with severe soil selenium depletion (e.g., volcanic low-Se belts)",
            "Patients maintained on long-term total parenteral nutrition (TPN) without trace minerals",
            "Individuals with severe gastrointestinal malabsorption (active Crohn's or surgical resection)",
            "Patients undergoing regular chronic hemodialysis",
            "Strict long-term vegans in low-soil selenium regions"
        ],
        "key_dietary_sources": [
            "Brazil nuts (a single nut delivers 68-91 mcg, >100% daily adult requirement)",
            "Yellowfin and albacore tuna, wild halibut, and sardines",
            "Pasture-raised eggs and turkey breast",
            "Shiitake mushrooms and sunflower seeds"
        ],
        "absorption_enhancers": ["Vitamin C, Vitamin A, and Vitamin E (synergistic antioxidant network)"],
        "absorption_inhibitors": ["Heavy metals (mercury, cadmium, arsenic form insoluble selenide precipitates)", "Excessive phytates in unrefined grains"],
        "citations": {
            "who_reference": "World Health Organization: Trace elements in human nutrition and health (WHO Technical Report).",
            "nih_reference": "NIH Office of Dietary Supplements: Selenium Fact Sheet for Health Professionals.",
            "additional_guidelines": ["Selenium in Global Health and Disease (Lancet Comprehensive Review)."]
        }
    },

    "IODINE": {
        "nutrient_code": "IODINE",
        "common_name": "Iodine",
        "category": "Trace Mineral",
        "active_vitamers": ["Iodide (I-)", "Iodate (IO3-)", "Thyroxine (T4)", "Triiodothyronine (T3)"],
        "clinical_role": "Obligate structural component of thyroid hormones thyroxine (T4, 4 iodine atoms) and triiodothyronine (T3, 3 iodine atoms). Regulates basal metabolic rate, mitochondrial thermogenesis, cardiac contractility, and early fetal/neonatal central nervous system myelination.",
        "daily_recommended_intake": {
            "standard_adult_male": "150 mcg/day",
            "standard_adult_female": "150 mcg/day",
            "pregnancy_lactation": "220 - 290 mcg/day (critical for fetal neurogenesis)",
            "tolerable_upper_limit": "1,100 mcg/day in adults (based on elevated TSH and thyroiditis risk)."
        },
        "toxicity_limits": "High-dose iodine (>1,100 mcg/day or excessive seaweed consumption) triggers the Wolff-Chaikoff effect (transient autoregulatory shutdown of thyroid hormone synthesis) or Jod-Basedow hyperthyroidism in susceptible multinodular goiters.",
        "deficiency_symptoms": [
            "Compensatory thyroid gland hypertrophy and visible nodular goiter",
            "Systemic hypothyroidism: cold intolerance, unprovoked weight gain, and profound sluggishness",
            "Dry coarse skin, brittle hair, periorbital myxedema puffiness, and constipation",
            "Impaired neurocognitive concentration, memory deficits, and clinical depression",
            "Severe fetal neurocognitive developmental deficit (Congenital Iodine Deficiency Syndrome / Cretinism)",
            "Increased spontaneous abortion, stillbirth, and infant mortality"
        ],
        "high_risk_populations": [
            "Pregnant and breastfeeding women without targeted prenatal iodine supplementation",
            "Strict vegans and individuals consuming exclusively un-iodized specialty salts (Himalayan pink, sea salt)",
            "Individuals with dairy-free and seafood-free diets in non-coastal inland areas",
            "Populations consuming high concentrations of dietary goitrogens (cassava, millet, raw brassicas) without adequate iodine"
        ],
        "key_dietary_sources": [
            "Marine sea vegetables (kelp, kombu, nori, wakame)",
            "Iodized table salt (1/2 teaspoon provides ~140 mcg, ~90% daily RDA)",
            "Wild Atlantic cod, haddock, and shrimp",
            "Organic whole milk, Greek yogurt, and pasture-raised eggs"
        ],
        "absorption_enhancers": ["Adequate selenium status (essential for deiodinase activation)"],
        "absorption_inhibitors": ["Goitrogens: Glucosinolates in unsteamed cruciferous vegetables (thiocyanates compete for NIS symporter)", "Perchlorates and nitrates in contaminated drinking water", "Fluoride and bromide halides"],
        "citations": {
            "who_reference": "WHO/UNICEF/IGN: Assessment of iodine deficiency disorders and monitoring their elimination (3rd Edition).",
            "nih_reference": "NIH Office of Dietary Supplements: Iodine Fact Sheet for Health Professionals.",
            "additional_guidelines": ["American Thyroid Association Guidelines for Diagnosis and Management of Thyroid Disease."]
        }
    },

    "PROTEIN": {
        "nutrient_code": "PROTEIN",
        "common_name": "Protein & Essential Amino Acids",
        "category": "Macronutrient",
        "active_vitamers": ["9 Essential Amino Acids", "Branched-Chain Amino Acids (Leucine, Isoleucine, Valine)"],
        "clinical_role": "Primary structural and functional matrix of human physiology: synthesizes peptide hormones, immunoglobulins, muscle contractile fibers (actin, myosin), and hepatic transport proteins (albumin). Maintains oncotic colloidal pressure.",
        "daily_recommended_intake": {
            "standard_adult_male": "0.8 - 1.2 g/kg body weight/day (56-80g)",
            "standard_adult_female": "0.8 - 1.2 g/kg body weight/day (46-70g)",
            "pregnancy_lactation": "1.1 - 1.3 g/kg body weight/day",
            "tolerable_upper_limit": "No formal UL; intakes up to 2.0-2.5 g/kg safe in preserved renal filtration."
        },
        "toxicity_limits": "High chronic intake (>3.0 g/kg) increases glomerular hyperfiltration; contraindicated in established CKD without specialist oversight.",
        "deficiency_symptoms": ["Sarcopenia and muscle wasting", "Peripheral edema (hypoalbuminemia / Kwashiorkor)", "Impaired wound healing and surgical dehiscence", "Thinning brittle hair and transverse nail ridging (Beau's lines)"],
        "high_risk_populations": ["Elderly populations (anabolic resistance)", "Strict low-calorie vegans without legume variety", "Critical care / burn trauma patients", "Chronic liver disease patients"],
        "key_dietary_sources": ["Pasture-raised eggs", "Organic firm tofu", "Lentils and chickpeas", "Wild Atlantic salmon", "Skinless chicken breast"],
        "absorption_enhancers": ["Cooking/heat denaturation", "Adequate digestive protease enzymes"],
        "absorption_inhibitors": ["Raw legume trypsin inhibitors", "Severe hypochlorhydria"],
        "citations": {
            "who_reference": "WHO/FAO/UNU: Protein and amino acid requirements in human nutrition (Technical Report Series 935).",
            "nih_reference": "Dietary Guidelines for Americans: Protein Intake Guidelines.",
            "additional_guidelines": ["ESPEN Guidelines on Clinical Nutrition and Protein in Chronic Diseases."]
        }
    },

    "VITAMIN_A": {
        "nutrient_code": "VITAMIN_A",
        "common_name": "Vitamin A (Retinol & Provitamin Carotenoids)",
        "category": "Fat-Soluble Vitamin",
        "active_vitamers": ["Retinol", "Retinal (Rhodopsin chromophore)", "Retinoic Acid", "Beta-Carotene"],
        "clinical_role": "Photopigment synthesis in retinal rod photoreceptors, maintenance of mucociliary mucosal barriers, and transcriptional gene regulation via RAR/RXR nuclear receptors.",
        "daily_recommended_intake": {
            "standard_adult_male": "900 mcg RAE/day (3,000 IU)",
            "standard_adult_female": "700 mcg RAE/day (2,330 IU)",
            "pregnancy_lactation": "770 - 1,300 mcg RAE/day",
            "tolerable_upper_limit": "3,000 mcg RAE/day (10,000 IU) of preformed retinol (teratogenic limit)."
        },
        "toxicity_limits": "Hypervitaminosis A produces elevated intracranial pressure (pseudotumor cerebri), hepatic fibrosis, teratogenicity in pregnancy, and bone fractures.",
        "deficiency_symptoms": ["Nyctalopia (night blindness)", "Xerophthalmia and Bitot's spots", "Follicular hyperkeratosis ('goose-flesh' skin)", "Heightened susceptibility to respiratory infections"],
        "high_risk_populations": ["Premature infants", "Patients with cystic fibrosis or cholestatic liver disease", "Bariatric surgery patients", "Poverty-stricken communities with low produce intake"],
        "key_dietary_sources": ["Baked sweet potato with skin", "Steamed spinach and carrots", "Grass-fed beef liver", "Pasture-raised egg yolks"],
        "absorption_enhancers": ["Dietary lipids/fats", "Zinc (required for Retinol-Binding Protein synthesis)"],
        "absorption_inhibitors": ["Fat malabsorption syndromes", "Orlistat and bile acid sequestrants"],
        "citations": {
            "who_reference": "WHO: Global prevalence of vitamin A deficiency in populations at risk 1995-2005.",
            "nih_reference": "NIH ODS: Vitamin A Fact Sheet for Health Professionals.",
            "additional_guidelines": ["EFSA Scientific Opinion on Dietary Reference Values for Vitamin A."]
        }
    },

    "VITAMIN_B12": {
        "nutrient_code": "VITAMIN_B12",
        "common_name": "Vitamin B12 (Cobalamin)",
        "category": "Water-Soluble Vitamin",
        "active_vitamers": ["Methylcobalamin", "Adenosylcobalamin", "Cyanocobalamin", "Hydroxocobalamin"],
        "clinical_role": "Cofactor for methionine synthase (DNA methylation and homocysteine conversion) and L-methylmalonyl-CoA mutase (fatty acid energy production and myelin sheath integrity).",
        "daily_recommended_intake": {
            "standard_adult_male": "2.4 mcg/day",
            "standard_adult_female": "2.4 mcg/day",
            "pregnancy_lactation": "2.6 - 2.8 mcg/day",
            "tolerable_upper_limit": "No established UL due to exceptionally low toxicity profile."
        },
        "toxicity_limits": "No toxicity documented. Excess absorbed cobalamin is cleared through urinary excretion.",
        "deficiency_symptoms": ["Macrocytic megaloblastic anemia", "Subacute combined degeneration of the spinal cord (ataxia, paresthesia)", "Depression, cognitive dementia, and memory loss", "Glossitis and stomatitis"],
        "high_risk_populations": ["Strict vegans and vegetarians", "Patients with autoimmune pernicious anemia", "Long-term Metformin or PPI (Omeprazole) users", "Elderly with atrophic gastritis"],
        "key_dietary_sources": ["Fortified nutritional yeast", "Steamed clams, oysters, and mackerel", "Wild Atlantic salmon", "Pasture-raised whole eggs"],
        "absorption_enhancers": ["Gastric intrinsic factor", "Gastric hydrochloric acid"],
        "absorption_inhibitors": ["Proton pump inhibitors", "Metformin (impairs ileal calcium-dependent uptake)", "Nitrous oxide anesthesia"],
        "citations": {
            "who_reference": "WHO: Conclusions of a WHO Technical Consultation on folate and vitamin B12 deficiencies.",
            "nih_reference": "NIH ODS: Vitamin B12 Health Professional Fact Sheet.",
            "additional_guidelines": ["British Society for Haematology: Guidelines on Cobalamin and Folate Disorders."]
        }
    },

    "FOLATE_B9": {
        "nutrient_code": "FOLATE_B9",
        "common_name": "Folate (Vitamin B9)",
        "category": "Water-Soluble Vitamin",
        "active_vitamers": ["5-Methyltetrahydrofolate (5-MTHF)", "Tetrahydrofolate (THF)", "Folic Acid"],
        "clinical_role": "Universal single-carbon carrier for purine and thymidylate nucleotide synthesis and epigenetic methylation of DNA and histones.",
        "daily_recommended_intake": {
            "standard_adult_male": "400 mcg DFE/day",
            "standard_adult_female": "400 mcg DFE/day",
            "pregnancy_lactation": "600 mcg DFE/day (prevents neural tube defects)",
            "tolerable_upper_limit": "1,000 mcg/day of synthetic folic acid (avoids masking B12 deficiency neuropathy)."
        },
        "toxicity_limits": "High synthetic folic acid (>1,000 mcg/day) can mask the hematologic presentation of Vitamin B12 deficiency while allowing neuropathy to proceed.",
        "deficiency_symptoms": ["Megaloblastic macrocytic anemia", "Neural tube birth defects (spina bifida, anencephaly)", "Severe fatigue and shortness of breath", "Oral aphthous ulcers"],
        "high_risk_populations": ["Women of reproductive age", "Alcohol-dependent individuals", "Individuals with homozygous MTHFR C677T polymorphisms", "Patients on Methotrexate or antiepileptics"],
        "key_dietary_sources": ["Steamed asparagus and broccoli", "Cooked black-eyed peas and lentils", "Fresh raw baby spinach", "Hass avocado"],
        "absorption_enhancers": ["Vitamin C (protects folate from oxidative degradation)"],
        "absorption_inhibitors": ["Thermal destruction (>50% lost in prolonged boiling)", "Alcohol", "Methotrexate and trimethoprim"],
        "citations": {
            "who_reference": "WHO: Guideline on optimal serum and red blood cell folate concentrations.",
            "nih_reference": "NIH ODS: Folate Fact Sheet for Health Professionals.",
            "additional_guidelines": ["US Preventive Services Task Force: Folic Acid Supplementation Guidelines."]
        }
    },

    "VITAMIN_C": {
        "nutrient_code": "VITAMIN_C",
        "common_name": "Vitamin C (Ascorbic Acid)",
        "category": "Water-Soluble Vitamin",
        "active_vitamers": ["L-Ascorbic Acid", "Dehydroascorbic Acid"],
        "clinical_role": "Primary water-soluble antioxidant; essential electron donor for prolyl and lysyl hydroxylase enzymes in collagen triple-helix assembly. Reduces non-heme ferric iron to absorbable ferrous iron.",
        "daily_recommended_intake": {
            "standard_adult_male": "90 mg/day (+35 mg if smoking)",
            "standard_adult_female": "75 mg/day (+35 mg if smoking)",
            "pregnancy_lactation": "85 - 120 mg/day",
            "tolerable_upper_limit": "2,000 mg/day (osmotic diarrhea and GI upset threshold)."
        },
        "toxicity_limits": "Doses >2,000 mg/day produce osmotic diarrhea, abdominal cramping, and increase calcium oxalate kidney stone risk in hyperoxaluric individuals.",
        "deficiency_symptoms": ["Scurvy (corkscrew hairs, follicular petechiae)", "Bleeding spongy gingivitis and tooth loss", "Impaired wound healing", "Perifollicular hemorrhages and bruising"],
        "high_risk_populations": ["Cigarette smokers (increased metabolic turnover)", "Individuals with low fruit/vegetable intake", "Patients with malabsorption or institutionalized elderly"],
        "key_dietary_sources": ["Yellow and red bell peppers", "Fresh kiwi fruit and strawberries", "Citrus fruits (oranges, lemons)", "Steamed broccoli florets"],
        "absorption_enhancers": ["Citrus bioflavonoids"],
        "absorption_inhibitors": ["High-heat cooking and boiling", "Alkaline pH", "Aspirin and corticosteroids"],
        "citations": {
            "who_reference": "World Health Organization: Vitamin and mineral requirements in human nutrition (2nd ed).",
            "nih_reference": "NIH ODS: Vitamin C Health Professional Fact Sheet.",
            "additional_guidelines": ["Linus Pauling Institute Micronutrient Information Center: Vitamin C."]
        }
    },

    "VITAMIN_D": {
        "nutrient_code": "VITAMIN_D",
        "common_name": "Vitamin D (Calciferol)",
        "category": "Fat-Soluble Vitamin / Prohormone",
        "active_vitamers": ["Cholecalciferol (D3)", "Ergocalciferol (D2)", "Calcifediol (25(OH)D)", "Calcitriol (1,25(OH)2D)"],
        "clinical_role": "Secosteroid prohormone that binds nuclear VDR receptors to upregulate intestinal calbindin, boosting calcium and phosphate absorption. Modulates T-regulatory and dendritic immune cells.",
        "daily_recommended_intake": {
            "standard_adult_male": "600 - 800 IU/day (15-20 mcg)",
            "standard_adult_female": "600 - 800 IU/day (15-20 mcg)",
            "pregnancy_lactation": "600 - 1,000 IU/day",
            "tolerable_upper_limit": "4,000 IU/day (100 mcg) in adults."
        },
        "toxicity_limits": "Chronic extreme megadosing (>40,000 IU/day for months) produces Hypervitaminosis D: severe hypercalcemia, vascular and soft-tissue calcification, nephrolithiasis, and renal failure.",
        "deficiency_symptoms": ["Adult osteomalacia and bone pain", "Rickets in children (craniotabes, bowed legs)", "Chronic muscle weakness and elevated fall risk", "Frequent viral respiratory tract infections"],
        "high_risk_populations": ["Indoor workers and populations living at high latitudes (>37° N/S)", "Individuals with deep skin melanin pigmentation", "Obese individuals (adipose tissue sequestration)", "Strict dairy-free vegans"],
        "key_dietary_sources": ["Wild Atlantic sockeye salmon", "Canned sardines in olive oil", "Pasture-raised egg yolks", "UV-irradiated Portobello mushrooms"],
        "absorption_enhancers": ["Dietary lipids/fats", "Magnesium (essential for hepatic and renal hydroxylase activation)"],
        "absorption_inhibitors": ["Fat malabsorption (celiac, pancreatitis)", "Glucocorticoids, antiepileptics (phenytoin, carbamazepine)"],
        "citations": {
            "who_reference": "World Health Organization: Prevention and management of osteoporosis.",
            "nih_reference": "NIH ODS: Vitamin D Fact Sheet for Health Professionals.",
            "additional_guidelines": ["Endocrine Society Clinical Practice Guideline: Evaluation, Treatment, and Prevention of Vitamin D Deficiency."]
        }
    },

    "VITAMIN_E": {
        "nutrient_code": "VITAMIN_E",
        "common_name": "Vitamin E (Tocopherols & Tocotrienols)",
        "category": "Fat-Soluble Vitamin",
        "active_vitamers": ["d-Alpha-Tocopherol (biologically active form)", "Gamma-Tocopherol", "Tocotrienols"],
        "clinical_role": "Primary lipophilic chain-breaking antioxidant protecting polyunsaturated fatty acids in biological membranes against reactive oxygen species (ROS) and lipid peroxidation.",
        "daily_recommended_intake": {
            "standard_adult_male": "15 mg/day (22.4 IU)",
            "standard_adult_female": "15 mg/day (22.4 IU)",
            "pregnancy_lactation": "15 - 19 mg/day",
            "tolerable_upper_limit": "1,000 mg/day (1,500 IU) in adults (hemorrhagic stroke risk threshold)."
        },
        "toxicity_limits": "Excess supplemental intake (>1,000 mg/day) antagonizes Vitamin K-dependent clotting factor gamma-carboxylation, elevating hemorrhagic stroke risk.",
        "deficiency_symptoms": ["Hemolytic anemia (erythrocyte fragility)", "Spinocerebellar ataxia and peripheral sensory neuropathy", "Loss of vibratory and proprioceptive sensation", "Retinal pigmentary degeneration"],
        "high_risk_populations": ["Patients with severe fat malabsorption (cystic fibrosis, cholestasis)", "Individuals with abetalipoproteinemia", "Very low-fat diet adherents", "Premature very-low-birth-weight infants"],
        "key_dietary_sources": ["Raw sunflower seeds and sunflower oil", "Raw whole almonds and hazelnuts", "Hass avocados", "Steamed Swiss chard and spinach"],
        "absorption_enhancers": ["Dietary fats/lipids", "Vitamin C (regenerates oxidized alpha-tocopherol radical back to active vitamin)"],
        "absorption_inhibitors": ["Orlistat and colestyramine", "High dietary iron intake (oxidative degradation in lumen)"],
        "citations": {
            "who_reference": "World Health Organization: Vitamin and mineral requirements in human nutrition.",
            "nih_reference": "NIH ODS: Vitamin E Fact Sheet for Health Professionals.",
            "additional_guidelines": ["IOM Dietary Reference Intakes for Vitamin C, Vitamin E, Selenium, and Carotenoids."]
        }
    },

    "IRON": {
        "nutrient_code": "IRON",
        "common_name": "Iron (Heme & Non-Heme)",
        "category": "Trace Mineral",
        "active_vitamers": ["Ferrous Iron (Fe2+ - absorbable form)", "Ferric Iron (Fe3+)", "Heme Iron", "Ferritin & Hemosiderin"],
        "clinical_role": "Central functional atom of hemoglobin (oxygen delivery) and myoglobin (muscle oxygen storage). Essential component of cytochromes in mitochondrial electron transport.",
        "daily_recommended_intake": {
            "standard_adult_male": "8 mg/day",
            "standard_adult_female": "18 mg/day (premenopausal), 8 mg/day (postmenopausal)",
            "pregnancy_lactation": "27 mg/day (pregnancy)",
            "tolerable_upper_limit": "45 mg/day (GI ulceration threshold)."
        },
        "toxicity_limits": "Chronic overload leads to Hemochromatosis: organ hemosiderin deposition, hepatic cirrhosis, bronze diabetes, and dilated cardiomyopathy. Acute pediatric ingestion >20 mg/kg causes lethal hemorrhagic gastroenteritis.",
        "deficiency_symptoms": ["Microcytic hypochromic anemia and pallor", "Severe chronic fatigue and exercise dyspnea", "Koilonychia (spoon-shaped concave nails)", "Pica (compulsive ice or clay eating)", "Restless legs syndrome"],
        "high_risk_populations": ["Menstruating and pregnant women", "Strict vegans and vegetarians", "Endurance athletes (foot-strike hemolysis)", "Patients with occult GI bleeding"],
        "key_dietary_sources": ["Grass-fed beef liver and lean beef", "Steamed green/brown lentils and chickpeas", "Cooked spinach paired with lemon juice", "Shelled pumpkin seeds"],
        "absorption_enhancers": ["Vitamin C / Ascorbic acid (reduces Fe3+ to Fe2+)", "Meat protein factor"],
        "absorption_inhibitors": ["Phytates in unsoaked grains", "Polyphenols/tannins in black tea and coffee", "Calcium supplements", "Antacids and PPIs"],
        "citations": {
            "who_reference": "WHO: The global prevalence of anaemia in 2011 (WHO/NMH/NHD/15.2).",
            "nih_reference": "NIH ODS: Iron Fact Sheet for Health Professionals.",
            "additional_guidelines": ["British Society of Gastroenterology guidelines for the management of iron deficiency anaemia."]
        }
    },

    "CALCIUM": {
        "nutrient_code": "CALCIUM",
        "common_name": "Calcium",
        "category": "Macromineral",
        "active_vitamers": ["Ionized Calcium (Ca2+ - active fraction)", "Hydroxyapatite (Bone Matrix)"],
        "clinical_role": "Mineral structural matrix of bones and teeth (99%). Extracellular Ca2+ mediates blood clotting cascades, second-messenger signal transduction, acetylcholine neurotransmitter exocytosis, and actin-myosin cross-bridge cycling.",
        "daily_recommended_intake": {
            "standard_adult_male": "1,000 mg/day (1,200 mg if >70 years)",
            "standard_adult_female": "1,000 mg/day (1,200 mg if >50 years)",
            "pregnancy_lactation": "1,000 - 1,300 mg/day",
            "tolerable_upper_limit": "2,500 mg/day (19-50 yrs); 2,000 mg/day (>50 yrs)."
        },
        "toxicity_limits": "Excessive supplementation (>2,000-2,500 mg/day) produces Milk-Alkali syndrome, nephrocalcinosis, nephrolithiasis, and impairs vascular distensibility.",
        "deficiency_symptoms": ["Tetany, muscle spasms, and carpopedal spasm (Trousseau's sign)", "Facial twitching (Chvostek's sign)", "Osteopenia and severe osteoporosis fragility fractures", "Cardiac arrhythmias and prolonged QTc interval"],
        "high_risk_populations": ["Postmenopausal women", "Strict vegans and dairy-allergic individuals", "Patients with hypoparathyroidism or Vitamin D deficiency", "Female athletic triad adherents"],
        "key_dietary_sources": ["Plain unsweetened Greek yogurt", "Calcium-set organic firm tofu", "Canned bone-in sardines", "Steamed kale and fortified plant milk"],
        "absorption_enhancers": ["Active Vitamin D (Calcitriol induces calbindin-D9k)", "Gastric acidity"],
        "absorption_inhibitors": ["Oxalates (spinach, beet greens)", "Phytates", "High sodium and caffeine intake (increases renal excretion)"],
        "citations": {
            "who_reference": "WHO: Calcium and magnesium in drinking-water: Public health significance.",
            "nih_reference": "NIH ODS: Calcium Fact Sheet for Health Professionals.",
            "additional_guidelines": ["National Osteoporosis Foundation Clinical Guidelines for Osteoporosis Prevention."]
        }
    },

    "ZINC": {
        "nutrient_code": "ZINC",
        "common_name": "Zinc",
        "category": "Trace Mineral",
        "active_vitamers": ["Ionic Zinc (Zn2+)", "Zinc Finger DNA-Binding Motifs"],
        "clinical_role": "Catalytic cofactor in >300 enzymes (alkaline phosphatase, carbonic anhydrase, superoxide dismutase). Crucial structural motif in 'zinc-finger' transcription factors, wound re-epithelialization, and gustin enzyme synthesis.",
        "daily_recommended_intake": {
            "standard_adult_male": "11 mg/day",
            "standard_adult_female": "8 mg/day",
            "pregnancy_lactation": "11 - 12 mg/day",
            "tolerable_upper_limit": "40 mg/day in adults (copper depletion threshold)."
        },
        "toxicity_limits": "Chronic high intake (>40-50 mg/day) induces intestinal metallothionein synthesis, competitively blocking copper absorption and causing severe secondary copper-deficiency myeloneuropathy and neutropenia.",
        "deficiency_symptoms": ["Acrodermatitis enteropathica (periorificial and acral dermatitis)", "Loss of taste (hypogeusia) and smell (hyposmia)", "Impaired wound healing and alopecia", "Severe cellular immune deficiency and frequent opportunistic infections"],
        "high_risk_populations": ["Vegetarians and vegans with high unfermented phytate intake", "Patients with Crohn's, ulcerative colitis, or short bowel syndrome", "Alcohol use disorder patients", "Sickle cell disease patients"],
        "key_dietary_sources": ["Pacific oysters and steamed shellfish", "Grass-fed beef tenderloin", "Raw pumpkin seeds / pepitas", "Cooked chickpeas and cashews"],
        "absorption_enhancers": ["Animal dietary proteins", "Citric acid"],
        "absorption_inhibitors": ["Dietary phytates", "High-dose supplemental iron (competes for DMT-1)", "Tetracyclines and fluoroquinolones"],
        "citations": {
            "who_reference": "World Health Organization: Zinc in human health.",
            "nih_reference": "NIH ODS: Zinc Fact Sheet for Health Professionals.",
            "additional_guidelines": ["International Zinc Nutrition Consultative Group (IZiNCG) Technical Document."]
        }
    },

    "MAGNESIUM": {
        "nutrient_code": "MAGNESIUM",
        "common_name": "Magnesium",
        "category": "Macromineral",
        "active_vitamers": ["Ionic Magnesium (Mg2+)", "Mg-ATP Chelate Complex"],
        "clinical_role": "Obligate catalytic cofactor for >300 enzymatic systems, notably every single enzyme utilizing or synthesizing ATP. Regulates cardiac voltage-gated calcium channels, modulates NMDA receptor tone, and enables hepatic/renal activation of Vitamin D.",
        "daily_recommended_intake": {
            "standard_adult_male": "400 - 420 mg/day",
            "standard_adult_female": "310 - 320 mg/day",
            "pregnancy_lactation": "350 - 400 mg/day",
            "tolerable_upper_limit": "350 mg/day from pharmacological/supplemental sources (dietary food magnesium has no UL)."
        },
        "toxicity_limits": "Excess supplemental magnesium causes osmotic diarrhea. Severe hypermagnesemia (>4-5 mEq/L) seen in renal failure produces loss of deep tendon reflexes, flaccid paralysis, respiratory arrest, and heart block.",
        "deficiency_symptoms": ["Nocturnal calf muscle cramps, fasciculations, and tremors", "Cardiac dysrhythmias (ventricular extrasystoles, Torsades de Pointes)", "Hypokalemia and hypocalcemia resistant to repletion", "Sleep fragmentation, anxiety, migraine headaches, and fatigue"],
        "high_risk_populations": ["Individuals with type 2 diabetes (glycosuria-induced osmotic renal wasting)", "Patients on chronic Proton Pump Inhibitors (PPIs) or loop diuretics", "Chronic alcoholics (tubular dysfunction)", "Elderly on processed diets"],
        "key_dietary_sources": ["Raw pumpkin seeds and dark chocolate 85%+", "Cooked Swiss chard and spinach", "Raw almonds, cashews, and black beans", "Hass avocado and quinoa"],
        "absorption_enhancers": ["Fermentable prebiotic fibers", "Vitamin D"],
        "absorption_inhibitors": ["Phytates and oxalates", "High unabsorbed dietary fat (forms insoluble magnesium soaps)", "Alcohol and chronic PPIs"],
        "citations": {
            "who_reference": "World Health Organization: Calcium and magnesium in drinking-water (Geneva, 2009).",
            "nih_reference": "NIH ODS: Magnesium Fact Sheet for Health Professionals.",
            "additional_guidelines": ["Subclinical Magnesium Deficiency: A Principal Driver of Cardiovascular Disease (Open Heart BMJ)."]
        }
    }
}


class ClinicalKnowledgeBaseService:
    """
    Service layer providing queries and lookups against the clinical knowledge base.
    """

    @classmethod
    def get_all_nutrients(cls) -> List[Dict[str, Any]]:
        return list(CLINICAL_NUTRIENT_REGISTRY.values())

    @classmethod
    def get_nutrient_by_code(cls, code: str) -> Optional[Dict[str, Any]]:
        clean_code = code.strip().upper()
        # Direct lookup or alias search
        if clean_code in CLINICAL_NUTRIENT_REGISTRY:
            return CLINICAL_NUTRIENT_REGISTRY[clean_code]
        for k, v in CLINICAL_NUTRIENT_REGISTRY.items():
            if clean_code in k or clean_code in v["common_name"].upper():
                return v
        return None
