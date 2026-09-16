"""
Clinical Knowledge Graph Relationships Registry
Phase 7B: Directional causal edges, biological mechanisms, and evidence citations.
"""

from typing import List, Dict, Any
from .schemas import RelationshipType

RELATIONSHIPS_REGISTRY: List[Dict[str, Any]] = [
    # ══════════════════════════════════════════════════════════════════════════
    # 1. REQUIRES (Biochemical Prerequisites & Enzymatic Co-factors)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_VIT_D_REQ_MAGNESIUM",
        "source_id": "NUTRIENT_VITAMIN_D",
        "target_id": "NUTRIENT_MAGNESIUM",
        "relationship_type": RelationshipType.REQUIRES,
        "weight": 0.95,
        "mechanism": "Hepatic 25-hydroxylase and renal 1-alpha-hydroxylase enzymes converting cholecalciferol to bioactive calcitriol (1,25(OH)2D) obligately require magnesium as a catalytic cofactor.",
        "citation": "Reddy P, Edwards LR. Magnesium Supplementation in Vitamin D Deficiency. Am J Ther. 2019;26(1):e124-e132."
    },
    {
        "id": "REL_CALCIUM_REQ_VIT_D",
        "source_id": "NUTRIENT_CALCIUM",
        "target_id": "NUTRIENT_VITAMIN_D",
        "relationship_type": RelationshipType.REQUIRES,
        "weight": 0.95,
        "mechanism": "Transcellular active calcium absorption in duodenal enterocytes requires calcitriol-mediated upregulation of apical calcium channels (TRPV6) and intracellular transport protein calbindin-D9k.",
        "citation": "Christakos S, et al. Vitamin D and Intestinal Calcium Absorption. Mol Cell Endocrinol. 2011;347(1-2):25-29."
    },
    {
        "id": "REL_IRON_REQ_VIT_C",
        "source_id": "NUTRIENT_IRON",
        "target_id": "NUTRIENT_VITAMIN_C",
        "relationship_type": RelationshipType.REQUIRES,
        "weight": 0.90,
        "mechanism": "Non-heme ferric iron (Fe3+) in the alkaline duodenal lumen requires ascorbic acid reduction to soluble ferrous iron (Fe2+) for divalent metal transporter 1 (DMT1) internalization.",
        "citation": "Hurrell R, Egli I. Iron bioavailability and dietary reference values. Am J Clin Nutr. 2010;91(5):1461S-1467S."
    },
    {
        "id": "REL_THYROID_REQ_IODINE",
        "source_id": "NUTRIENT_IODINE",
        "target_id": "SYSTEM_ENDOCRINE",
        "relationship_type": RelationshipType.REQUIRES,
        "weight": 0.98,
        "mechanism": "Thyroid peroxidase organification of tyrosine residues on thyroglobulin obligately requires elemental iodide to synthesize thyroxine (T4) and triiodothyronine (T3).",
        "citation": "Zimmermann MB. Iodine deficiency. Endocr Rev. 2009;30(4):376-408."
    },
    {
        "id": "REL_IODINE_REQ_SELENIUM",
        "source_id": "NUTRIENT_IODINE",
        "target_id": "NUTRIENT_SELENIUM",
        "relationship_type": RelationshipType.REQUIRES,
        "weight": 0.92,
        "mechanism": "Peripheral tissue activation of prohormone T4 into active T3 requires selenoenzyme iodothyronine deiodinases (DIO1, DIO2); selenium deficiency causes concurrent functional hypothyroidism.",
        "citation": "Kohrle J. Selenium and the thyroid. Curr Opin Endocrinol Diabetes Obes. 2013;20(5):441-448."
    },
    {
        "id": "REL_VIT_B12_REQ_FOLATE",
        "source_id": "NUTRIENT_VITAMIN_B12",
        "target_id": "NUTRIENT_FOLATE",
        "relationship_type": RelationshipType.REQUIRES,
        "weight": 0.92,
        "mechanism": "Methionine synthase requires both methylcobalamin and 5-methyl-THF to remethylate homocysteine into methionine; absence of B12 traps folate as 5-MTHF ('methylfolate trap').",
        "citation": "Scott JM, Weir DG. The methyl folate trap. A physiological response in man to prevent methyl group deficiency. Lancet. 1981;2(8242):337-340."
    },
    {
        "id": "REL_VIT_B1_REQ_MAGNESIUM",
        "source_id": "NUTRIENT_VITAMIN_B1",
        "target_id": "NUTRIENT_MAGNESIUM",
        "relationship_type": RelationshipType.REQUIRES,
        "weight": 0.90,
        "mechanism": "Thiamine pyrophosphokinase, the enzyme converting dietary thiamine to bioactive thiamine pyrophosphate (TPP), is strictly magnesium-dependent.",
        "citation": "Dyer J, et al. Magnesium dependence of thiamine kinase. Biochem Biophys Res Commun. 2004."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 2. CAUSES (Direct Etiologies & Clinical Endpoints)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_VIT_D_CAUSES_BONE_PAIN",
        "source_id": "NUTRIENT_VITAMIN_D",
        "target_id": "SYMPTOM_BONE_PAIN",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.92,
        "mechanism": "Prolonged severe Vitamin D depletion prevents osteoid matrix mineralization; unmineralized gelatinous collagen matrix swells upon hydration, generating outward pressure against innervated periosteum.",
        "citation": "Holick MF. Vitamin D deficiency. N Engl J Med. 2007;357(3):266-281."
    },
    {
        "id": "REL_IRON_CAUSES_FATIGUE",
        "source_id": "NUTRIENT_IRON",
        "target_id": "SYMPTOM_FATIGUE",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.95,
        "mechanism": "Depleted systemic iron stores impair erythropoiesis and mitochondrial electron transport chain cytochromes, causing reduced arterial oxygen delivery and cellular ATP depletion.",
        "citation": "Camaschella C. Iron-Deficiency Anemia. N Engl J Med. 2015;372(19):1832-1843."
    },
    {
        "id": "REL_VIT_B12_CAUSES_TINGLING",
        "source_id": "NUTRIENT_VITAMIN_B12",
        "target_id": "SYMPTOM_TINGLING_NUMBNESS",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.94,
        "mechanism": "Deficiency of cobalamin impairs S-adenosylmethionine (SAMe) production, leading to defective myelin lipid methylation, demyelination of posterior and lateral spinal columns, and peripheral neuropathy.",
        "citation": "Stabler SP. Clinical practice. Vitamin B12 deficiency. N Engl J Med. 2013;368(2):149-160."
    },
    {
        "id": "REL_POTASSIUM_CAUSES_ARRHYTHMIA",
        "source_id": "NUTRIENT_POTASSIUM",
        "target_id": "SYMPTOM_IRREGULAR_HEARTBEAT",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.96,
        "mechanism": "Hypokalemia hyperpolarizes cardiac myocyte resting membrane potential, delaying phase 3 repolarization and generating early afterdepolarizations triggering ventricular arrhythmias.",
        "citation": "Kjeldsen SE. Hypokalemia and sudden cardiac death. Exp Clin Cardiol. 2010;15(4):e96-99."
    },
    {
        "id": "REL_IODINE_CAUSES_THYROID",
        "source_id": "NUTRIENT_IODINE",
        "target_id": "SYMPTOM_THYROID_DYSFUNCTION",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.98,
        "mechanism": "Iodine substrate deprivation blunts T4/T3 synthesis, triggering persistent pituitary TSH hypersecretion and chronic thyrocyte hyperplasia (endemic goiter).",
        "citation": "World Health Organization. Assessment of iodine deficiency disorders and monitoring their elimination. WHO Guideline. 2007."
    },
    {
        "id": "REL_MAGNESIUM_CAUSES_CRAMPS",
        "source_id": "NUTRIENT_MAGNESIUM",
        "target_id": "SYMPTOM_MUSCLE_CRAMPS",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.88,
        "mechanism": "Magnesium is a natural calcium channel blocker; hypomagnesemia promotes sarcoplasmic calcium accumulation and spontaneous neuromuscular junction depolarization.",
        "citation": "Garrison SR, et al. Magnesium for skeletal muscle cramps. Cochrane Database Syst Rev. 2020."
    },
    {
        "id": "REL_PROTEIN_CAUSES_WEAKNESS",
        "source_id": "NUTRIENT_PROTEIN",
        "target_id": "SYMPTOM_MUSCLE_WEAKNESS",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.90,
        "mechanism": "Negative nitrogen balance prompts endogenous skeletal muscle proteolysis (ubiquitin-proteasome pathway), degrading actin-myosin myofibrils and causing sarcopenia.",
        "citation": "Wolfe RR. The underappreciated role of muscle in health and disease. Am J Clin Nutr. 2006;84(3):475-482."
    },
    {
        "id": "REL_VIT_A_CAUSES_NIGHT_BLINDNESS",
        "source_id": "NUTRIENT_VITAMIN_A",
        "target_id": "SYMPTOM_NIGHT_BLINDNESS",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.96,
        "mechanism": "Depleted 11-cis-retinal stores prevent regeneration of rhodopsin visual pigment in retinal rod photoreceptors, abolishing low-light dark adaptation.",
        "citation": "Sommer A. Vitamin A deficiency and clinical disease. J Nutr. 2008;138(10):1835-1839."
    },
    {
        "id": "REL_VIT_C_CAUSES_SLOW_HEALING",
        "source_id": "NUTRIENT_VITAMIN_C",
        "target_id": "SYMPTOM_SLOW_WOUND_HEALING",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.91,
        "mechanism": "Ascorbic acid deficiency halts prolyl and lysyl hydroxylase co-factor action, preventing stable triple-helix tropocollagen synthesis and wound capillary proliferation.",
        "citation": "Pullar JM, et al. The Roles of Vitamin C in Skin Health. Nutrients. 2017;9(8):866."
    },
    {
        "id": "REL_ZINC_CAUSES_POOR_IMMUNITY",
        "source_id": "NUTRIENT_ZINC",
        "target_id": "SYMPTOM_POOR_IMMUNITY",
        "relationship_type": RelationshipType.CAUSES,
        "weight": 0.92,
        "mechanism": "Zinc depletion causes thymic cortical atrophy, decreases thymulin hormone activity, and impairs Th1 cytokine production (IFN-gamma, IL-2).",
        "citation": "Prasad AS. Zinc in human health: effect of zinc on immune cells. Mol Med. 2008;14(5-6):353-357."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 3. CONTRIBUTES_TO (Lifestyle & Medical Predisposing Factors)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_LOW_SUN_TO_VIT_D",
        "source_id": "LIFESTYLE_LOW_SUN",
        "target_id": "NUTRIENT_VITAMIN_D",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.98,
        "mechanism": "Indoor lifestyles and lack of UVB radiation prevent photochemical isomerization of 7-dehydrocholesterol to pre-vitamin D3 in the skin epidermis.",
        "citation": "Holick MF. High prevalence of vitamin D inadequacy and implications for health. Mayo Clin Proc. 2006."
    },
    {
        "id": "REL_SMOKING_TO_VIT_C",
        "source_id": "LIFESTYLE_SMOKING",
        "target_id": "NUTRIENT_VITAMIN_C",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.92,
        "mechanism": "Tobacco smoke oxidants deplete circulating ascorbic acid through intense oxidative quenching, elevating daily Vitamin C metabolic requirements by >35 mg/day.",
        "citation": "Institute of Medicine (US). Dietary Reference Intakes for Vitamin C, Vitamin E, Selenium, and Carotenoids. 2000."
    },
    {
        "id": "REL_ALCOHOL_TO_VIT_B1",
        "source_id": "LIFESTYLE_ALCOHOL",
        "target_id": "NUTRIENT_VITAMIN_B1",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.96,
        "mechanism": "Ethanol suppresses active intestinal brush-border thiamine transporter ThTr-1, impairs hepatic phosphorylation to TPP, and accelerates urinary excretion.",
        "citation": "Hoyumpa AM. Mechanisms of thiamin deficiency in chronic alcoholism. Am J Clin Nutr. 1980;33(12):2750-2761."
    },
    {
        "id": "REL_ALCOHOL_TO_MAGNESIUM",
        "source_id": "LIFESTYLE_ALCOHOL",
        "target_id": "NUTRIENT_MAGNESIUM",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.90,
        "mechanism": "Acute and chronic alcohol loads induce reversible renal tubular magnesium wasting via transient magnesiuria and secondary hyperaldosteronism.",
        "citation": "Rivin BE. Magnesium deficiency in chronic alcoholism. South Med J. 1974."
    },
    {
        "id": "REL_VEGAN_TO_VIT_B12",
        "source_id": "LIFESTYLE_STRICT_VEGAN",
        "target_id": "NUTRIENT_VITAMIN_B12",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.98,
        "mechanism": "Vitamin B12 is synthesized exclusively by bacteria and concentrated in animal tissues; unfortified plant foods contain zero bioavailable cobalamin.",
        "citation": "Pawlak R, et al. How prevalent is vitamin B(12) deficiency among vegetarians? Nutr Rev. 2013;71(2):110-117."
    },
    {
        "id": "REL_VEGAN_TO_IRON",
        "source_id": "LIFESTYLE_STRICT_VEGAN",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.85,
        "mechanism": "Plant diets supply exclusively non-heme iron whose absorption is restricted to 2-10% due to potent binding by dietary phytic acids and polyphenols.",
        "citation": "Hunt JR. Bioavailability of iron, zinc, and other trace minerals from vegetarian diets. Am J Clin Nutr. 2003;78(3):633S-639S."
    },
    {
        "id": "REL_STRESS_TO_MAGNESIUM",
        "source_id": "LIFESTYLE_HIGH_STRESS",
        "target_id": "NUTRIENT_MAGNESIUM",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.88,
        "mechanism": "Prolonged adrenergic and cortisol surges increase urinary magnesium clearance while intracellular magnesium depletion amplifies stress reactivity ('vicious cycle').",
        "citation": "Pickering G, et al. Magnesium Status and Stress: The Vicious Circle Concept Revisited. Nutrients. 2020;12(12):3672."
    },
    {
        "id": "REL_POOR_SLEEP_TO_FATIGUE",
        "source_id": "LIFESTYLE_POOR_SLEEP",
        "target_id": "SYMPTOM_FATIGUE",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.90,
        "mechanism": "Sleep fragmentation disrupts nocturnal slow-wave sleep and adenosine clearance, exacerbating metabolic fatigue and daytime exhaustion.",
        "citation": "Alhola P, Polo-Kantola P. Sleep deprivation: Impact on cognitive performance. Neuropsychiatr Dis Treat. 2007."
    },
    {
        "id": "REL_CELIAC_TO_IRON",
        "source_id": "CONDITION_CELIAC",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.94,
        "mechanism": "Gluten-induced duodenal mucosal enterocyte blunting destroys apical microvillar DMT1 receptors where primary systemic iron absorption occurs.",
        "citation": "Hershko C, Patz J. Iron deficiency in celiac disease. Best Pract Res Clin Haematol. 2005;18(2):299-311."
    },
    {
        "id": "REL_CELIAC_TO_FOLATE",
        "source_id": "CONDITION_CELIAC",
        "target_id": "NUTRIENT_FOLATE",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.91,
        "mechanism": "Duodenal and proximal jejunal enteropathy diminishes proton-coupled folate transporter (PCFT) activity and brush-border pteroylpolyglutamate conjugase.",
        "citation": "Hallert C, et al. Folate status in adult celiac disease. Scand J Gastroenterol. 1982."
    },
    {
        "id": "REL_CROHNS_TO_B12",
        "source_id": "CONDITION_CROHNS",
        "target_id": "NUTRIENT_VITAMIN_B12",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.95,
        "mechanism": "Inflammatory transmural injury or resection of the terminal ileum abolishes the cubam receptor complex required for endocytosis of intrinsic factor-cobalamin complexes.",
        "citation": "Ward MG, et al. Prevalence and risk factors for vitamin B12 deficiency in patients with Crohn's disease. Inflamm Bowel Dis. 2015."
    },
    {
        "id": "REL_GASTRITIS_TO_B12",
        "source_id": "CONDITION_ATROPHIC_GASTRITIS",
        "target_id": "NUTRIENT_VITAMIN_B12",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.96,
        "mechanism": "Autoimmune or Helicobacter-driven destruction of gastric oxyntic mucosa halts intrinsic factor synthesis and suppresses pepsinogen acid cleavage of dietary B12.",
        "citation": "Toh BH. Pathophysiology and Diagnosis of Pernicious Anemia. Immunol Res. 2017."
    },
    {
        "id": "REL_BARIATRIC_TO_IRON",
        "source_id": "CONDITION_BARIATRIC",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.95,
        "mechanism": "Roux-en-Y reconstruction bypasses the duodenum and proximal jejunum and drastically reduces gastric acid production needed for iron solubilization.",
        "citation": "Mechanick JI, et al. Clinical Practice Guidelines for the Perioperative Nutritional, Metabolic, and Nonsurgical Support of the Bariatric Surgery Patient. Obesity. 2020."
    },
    {
        "id": "REL_CKD_TO_VIT_D",
        "source_id": "CONDITION_CKD",
        "target_id": "NUTRIENT_VITAMIN_D",
        "relationship_type": RelationshipType.CONTRIBUTES_TO,
        "weight": 0.95,
        "mechanism": "Loss of functional proximal renal tubular mass eliminates mitochondrial CYP27B1 (1-alpha-hydroxylase), halting endocrine production of bioactive calcitriol.",
        "citation": "Kidney Disease: Improving Global Outcomes (KDIGO) CKD-MBD Update Work Group. Kidney Int Suppl. 2017."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 4. ASSOCIATED_WITH (Clinical Manifestations & Phenotypes)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_B12_ASSOC_BRAIN_FOG",
        "source_id": "NUTRIENT_VITAMIN_B12",
        "target_id": "SYMPTOM_BRAIN_FOG",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.89,
        "mechanism": "Cobalamin deficiency produces intracellular homocysteine and MMA accumulation, provoking central neuroinflammation, white-matter hypoperfusion, and executive dysfunction.",
        "citation": "Smith AD, et al. Homocysteine-lowering by B vitamins slows the rate of accelerated brain atrophy in mild cognitive impairment. PLoS One. 2010."
    },
    {
        "id": "REL_IRON_ASSOC_HAIR_LOSS",
        "source_id": "NUTRIENT_IRON",
        "target_id": "SYMPTOM_HAIR_LOSS",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.88,
        "mechanism": "Hair follicle matrix matrix cells possess high mitotic turnover and depend upon iron-containing ribonucleotide reductase for cellular DNA synthesis.",
        "citation": "Trost LB, et al. The diagnosis and treatment of iron deficiency and its potential relationship to hair loss. J Am Acad Dermatol. 2006."
    },
    {
        "id": "REL_IRON_ASSOC_PALE_SKIN",
        "source_id": "NUTRIENT_IRON",
        "target_id": "SYMPTOM_PALE_SKIN",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.93,
        "mechanism": "Deficient hemoglobin synthesis reduces red blood cell pigment, while peripheral microvascular shunting away from dermis to core organs produces visible conjunctival and skin pallor.",
        "citation": "Kalra A, et al. Physiology, Erythrocyte. StatPearls. 2023."
    },
    {
        "id": "REL_ZINC_ASSOC_HAIR_LOSS",
        "source_id": "NUTRIENT_ZINC",
        "target_id": "SYMPTOM_HAIR_LOSS",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.87,
        "mechanism": "Zinc deficiency downregulates matrix metalloproteinases and zinc-finger protein activity essential for follicular morphogenesis and anagen-phase sustenance.",
        "citation": "Park H, et al. The Therapeutic Effect and the Changed Serum Zinc Level after Nutritional Supplementation in Alopecia Areata. Ann Dermatol. 2009."
    },
    {
        "id": "REL_FOLATE_ASSOC_FATIGUE",
        "source_id": "NUTRIENT_FOLATE",
        "target_id": "SYMPTOM_FATIGUE",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.91,
        "mechanism": "Impaired purine and thymidylate synthesis arrests marrow normoblast division, generating megaloblastic anemia with ineffective tissue oxygen transport.",
        "citation": "Koury MJ, Ponka P. New insights into erythropoiesis: the roles of folate, vitamin B12, and iron. Annu Rev Nutr. 2004."
    },
    {
        "id": "REL_MAGNESIUM_ASSOC_IRRITABILITY",
        "source_id": "NUTRIENT_MAGNESIUM",
        "target_id": "SYMPTOM_IRRITABILITY",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.86,
        "mechanism": "Magnesium acts as an allosteric voltage-dependent blocker of the NMDA excitatory receptor; deficiency causes excessive neuronal calcium influx and hyper-excitability.",
        "citation": "Boyle NB, et al. The Effects of Magnesium Supplementation on Subjective Anxiety and Stress. Nutrients. 2017."
    },
    {
        "id": "REL_VIT_B2_ASSOC_MOUTH_ULCERS",
        "source_id": "NUTRIENT_VITAMIN_B2",
        "target_id": "SYMPTOM_MOUTH_ULCERS",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.89,
        "mechanism": "Epithelial ariboflavinosis diminishes glutathione reductase antioxidant capacity, promoting oral mucosal fragility, angular stomatitis, and glossitis.",
        "citation": "Powers HJ. Riboflavin-iron interactions with particular emphasis on the gastrointestinal tract. Proc Nutr Soc. 2003."
    },
    {
        "id": "REL_SELENIUM_ASSOC_COLD",
        "source_id": "NUTRIENT_SELENIUM",
        "target_id": "SYMPTOM_COLD_INTOLERANCE",
        "relationship_type": RelationshipType.ASSOCIATED_WITH,
        "weight": 0.87,
        "mechanism": "Suboptimal iodothyronine deiodinase activity slows thyroid T3 conversion, suppressing brown adipose uncoupling protein-1 (UCP1) mitochondrial non-shivering thermogenesis.",
        "citation": "Arthur JR, et al. Selenium in the thyroid. Mol Cell Endocrinol. 1999."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 5. IMPACTS (Organ & Biological System Modulations)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_VIT_D_IMPACTS_MUSCULOSKELETAL",
        "source_id": "NUTRIENT_VITAMIN_D",
        "target_id": "SYSTEM_MUSCULOSKELETAL",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.96,
        "mechanism": "Regulates osteoclast and osteoblast bone turnover, parathyroid hormone suppression, and myofibrillar calcium flux.",
        "citation": "Bischoff-Ferrari HA, et al. Vitamin D and muscle strength in older people. Lancet. 2004."
    },
    {
        "id": "REL_VIT_D_IMPACTS_IMMUNE",
        "source_id": "NUTRIENT_VITAMIN_D",
        "target_id": "SYSTEM_IMMUNE",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.94,
        "mechanism": "Binds nuclear VDR on macrophages and dendritic cells, inducing transcription of antimicrobial peptides cathelicidin and beta-defensin-4.",
        "citation": "Aranow C. Vitamin D and the immune system. J Investig Med. 2011;59(6):881-886."
    },
    {
        "id": "REL_VIT_B12_IMPACTS_NEUROLOGICAL",
        "source_id": "NUTRIENT_VITAMIN_B12",
        "target_id": "SYSTEM_NEUROLOGICAL",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.97,
        "mechanism": "Maintains myelin sheath structural integrity and protects against optic and peripheral axonal degeneration.",
        "citation": "Green R, et al. Vitamin B12 deficiency. Nat Rev Dis Primers. 2017;3:17040."
    },
    {
        "id": "REL_IRON_IMPACTS_CARDIOVASCULAR",
        "source_id": "NUTRIENT_IRON",
        "target_id": "SYSTEM_CARDIOVASCULAR",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.96,
        "mechanism": "Dictates total blood hemoglobin oxygen-carrying capacity and governs myocardial mitochondrial ATP generation.",
        "citation": "Anker SD, et al. Iron deficiency in chronic heart failure. Eur J Heart Fail. 2009."
    },
    {
        "id": "REL_MAGNESIUM_IMPACTS_CARDIOVASCULAR",
        "source_id": "NUTRIENT_MAGNESIUM",
        "target_id": "SYSTEM_CARDIOVASCULAR",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.93,
        "mechanism": "Modulates vascular endothelial nitric oxide synthase and maintains cardiac sodium-potassium ATPase pump stability.",
        "citation": "DiNicolantonio JJ, et al. Subclinical magnesium deficiency: a principal driver of cardiovascular disease. Open Heart. 2018."
    },
    {
        "id": "REL_POTASSIUM_IMPACTS_CARDIOVASCULAR",
        "source_id": "NUTRIENT_POTASSIUM",
        "target_id": "SYSTEM_CARDIOVASCULAR",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.98,
        "mechanism": "Establishes cardiac action potential resting membrane voltage; counteracts sodium-induced arterial hypertension.",
        "citation": "Whelton PK, et al. Sodium and potassium intake and cardiovascular disease. N Engl J Med. 2014."
    },
    {
        "id": "REL_ZINC_IMPACTS_IMMUNE",
        "source_id": "NUTRIENT_ZINC",
        "target_id": "SYSTEM_IMMUNE",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.95,
        "mechanism": "Required for intracellular signaling in T-cell receptor activation, NK cell cytotoxicity, and neutrophil oxidative burst.",
        "citation": "Wessels I, et al. The Meaning of Zinc in the Immune System. Nutrients. 2017;9(12):1286."
    },
    {
        "id": "REL_IODINE_IMPACTS_ENDOCRINE",
        "source_id": "NUTRIENT_IODINE",
        "target_id": "SYSTEM_ENDOCRINE",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.99,
        "mechanism": "Primary molecular constituent of thyroid hormone hormones controlling systemic gene expression and basal metabolic rate.",
        "citation": "Pearce EN. Iodine deficiency and thyroid disorders. Endocrinol Metab Clin North Am. 2007."
    },
    {
        "id": "REL_SELENIUM_IMPACTS_ENDOCRINE",
        "source_id": "NUTRIENT_SELENIUM",
        "target_id": "SYSTEM_ENDOCRINE",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.94,
        "mechanism": "Protects thyroid gland from hydrogen peroxide toxicity during hormone synthesis and drives T4 deiodination.",
        "citation": "Schomburg L. Selenium, selenoproteins and the thyroid gland. Nat Rev Endocrinol. 2011."
    },
    {
        "id": "REL_PROTEIN_IMPACTS_MUSCULOSKELETAL",
        "source_id": "NUTRIENT_PROTEIN",
        "target_id": "SYSTEM_MUSCULOSKELETAL",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.96,
        "mechanism": "Supplies branched-chain amino acids (leucine) driving mTORC1 muscle protein synthesis and maintaining skeletal collagen scaffold.",
        "citation": "Morton RW, et al. A systematic review of protein supplementation on muscle mass. Br J Sports Med. 2018."
    },
    {
        "id": "REL_VIT_B1_IMPACTS_METABOLIC",
        "source_id": "NUTRIENT_VITAMIN_B1",
        "target_id": "SYSTEM_METABOLIC",
        "relationship_type": RelationshipType.IMPACTS,
        "weight": 0.95,
        "mechanism": "Catalyzes mitochondrial pyruvate entry into the citric acid cycle; deficiency prompts cellular lactic acid accumulation.",
        "citation": "Frank LL. Thiamin in clinical practice. JPEN J Parenter Enteral Nutr. 2015."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 6. INHIBITS & ENHANCES (Biochemical Inter-Nutrient Modulations)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_VIT_C_ENHANCES_IRON",
        "source_id": "NUTRIENT_VITAMIN_C",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.ENHANCES,
        "weight": 0.94,
        "mechanism": "Ascorbate prevents insoluble ferric hydroxide formation in alkaline intestinal pH and forms soluble, chelated coordination complexes.",
        "citation": "Lynch SR, Cook JD. Interaction of vitamin C and iron. Ann N Y Acad Sci. 1980."
    },
    {
        "id": "REL_VIT_D_ENHANCES_CALCIUM",
        "source_id": "NUTRIENT_VITAMIN_D",
        "target_id": "NUTRIENT_CALCIUM",
        "relationship_type": RelationshipType.ENHANCES,
        "weight": 0.96,
        "mechanism": "Calcitriol transcriptionally upregulates enterocyte apical TRPV6 channels, boosting dietary calcium fractional absorption from 10% to over 40%.",
        "citation": "DeLuca HF. Evolution of our understanding of vitamin D. Nutr Rev. 2008."
    },
    {
        "id": "REL_ZINC_INHIBITS_IRON",
        "source_id": "NUTRIENT_ZINC",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.INHIBITS,
        "weight": 0.85,
        "mechanism": "High molar ratios of supplemental inorganic zinc compete with ferrous iron for divalent metal transporter 1 (DMT1) uptake.",
        "citation": "Solomons NW. Competitive interaction of iron and zinc in the diet: consequences for human nutrition. J Nutr. 1986."
    },
    {
        "id": "REL_CALCIUM_INHIBITS_IRON",
        "source_id": "NUTRIENT_CALCIUM",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.INHIBITS,
        "weight": 0.88,
        "mechanism": "High calcium concentrations inhibit basolateral export of iron by enterocytic ferroportin, reducing systemic iron transfer.",
        "citation": "Hallberg L, et al. Calcium: effect of different amounts on nonheme- and heme-iron absorption in humans. Am J Clin Nutr. 1991."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 7. CONFIRMS (Diagnostic Laboratory Biomarker Verification)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_FERRITIN_CONFIRMS_IRON",
        "source_id": "LAB_FERRITIN",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.CONFIRMS,
        "weight": 0.97,
        "mechanism": "Serum ferritin is the most specific biomarker for total body iron stores; concentration < 30 ng/mL establishes absolute iron deficiency with >95% specificity.",
        "citation": "Daru J, et al. Serum ferritin as an indicator of iron status: a systematic review. Am J Clin Nutr. 2017."
    },
    {
        "id": "REL_CBC_CONFIRMS_IRON",
        "source_id": "LAB_CBC",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.CONFIRMS,
        "weight": 0.92,
        "mechanism": "Low hemoglobin accompanied by Mean Corpuscular Volume (MCV < 80 fL) verifies microcytic hypochromic anemia secondary to advanced iron lack.",
        "citation": "Killip S, et al. Iron deficiency anemia. Am Fam Physician. 2007."
    },
    {
        "id": "REL_VIT_D_LAB_CONFIRMS_VIT_D",
        "source_id": "LAB_VITAMIN_D",
        "target_id": "NUTRIENT_VITAMIN_D",
        "relationship_type": RelationshipType.CONFIRMS,
        "weight": 0.99,
        "mechanism": "Serum 25(OH)D concentration < 20 ng/mL confirms clinical insufficiency; levels < 12 ng/mL establish severe osteomalacia deficiency threshold.",
        "citation": "Endocrine Society Clinical Practice Guideline. Evaluation, Treatment, and Prevention of Vitamin D Deficiency. J Clin Endocrinol Metab. 2011."
    },
    {
        "id": "REL_MMA_CONFIRMS_B12",
        "source_id": "LAB_MMA",
        "target_id": "NUTRIENT_VITAMIN_B12",
        "relationship_type": RelationshipType.CONFIRMS,
        "weight": 0.98,
        "mechanism": "Serum methylmalonic acid elevation (> 0.40 umol/L) confirms metabolic tissue B12 deficiency even when serum cobalamin levels reside in borderline ranges.",
        "citation": "Lindenbaum J, et al. Diagnosis of cobalamin deficiency: II. Relative sensitivities of serum methylmalonic acid and total homocysteine. Am J Hematol. 1990."
    },
    {
        "id": "REL_RBC_FOLATE_CONFIRMS_FOLATE",
        "source_id": "LAB_RBC_FOLATE",
        "target_id": "NUTRIENT_FOLATE",
        "relationship_type": RelationshipType.CONFIRMS,
        "weight": 0.95,
        "mechanism": "RBC folate < 140 ng/mL provides definitive evidence of chronic tissue folate depletion unperturbed by recent acute dietary intake.",
        "citation": "Pfeiffer CM, et al. Methodological bias in the measurement of erythrocyte folate. Clin Chem. 2007."
    },
    {
        "id": "REL_POTASSIUM_LAB_CONFIRMS_POTASSIUM",
        "source_id": "LAB_POTASSIUM",
        "target_id": "NUTRIENT_POTASSIUM",
        "relationship_type": RelationshipType.CONFIRMS,
        "weight": 0.99,
        "mechanism": "Serum potassium concentration < 3.5 mEq/L directly diagnoses hypokalemia and quantifies immediate cardiac arrhythmia risk.",
        "citation": "Gennari FJ. Disorders of potassium homeostasis. Hypokalemia and hyperkalemia. Crit Care Clin. 2002."
    },
    {
        "id": "REL_THYROID_LAB_CONFIRMS_IODINE",
        "source_id": "LAB_THYROID",
        "target_id": "NUTRIENT_IODINE",
        "relationship_type": RelationshipType.CONFIRMS,
        "weight": 0.93,
        "mechanism": "Elevated serum TSH (> 4.5 mIU/L) with depressed free T4 confirms primary hypothyroid failure, frequently rooted in end-organ iodine depletion.",
        "citation": "Garber JR, et al. Clinical practice guidelines for hypothyroidism in adults. Endocr Pract. 2012."
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 8. SUPPORTS (Dietary Nutrient Sources & Replenishment)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "REL_SALMON_SUPPORTS_VIT_D",
        "source_id": "FOOD_SALMON",
        "target_id": "NUTRIENT_VITAMIN_D",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.95,
        "mechanism": "Supplies 500-1000 IU of native cholecalciferol (D3) per 100g serving along with emulsifying omega-3 lipid matrix.",
        "citation": "Lu Z, et al. An evaluation of the vitamin D3 content in wild versus farmed salmon. J Steroid Biochem Mol Biol. 2007."
    },
    {
        "id": "REL_SALMON_SUPPORTS_PROTEIN",
        "source_id": "FOOD_SALMON",
        "target_id": "NUTRIENT_PROTEIN",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.95,
        "mechanism": "Delivers 22g of high-BV protein per 100g containing optimal leucine proportions to trigger muscle protein synthesis.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_BEEF_SUPPORTS_IRON",
        "source_id": "FOOD_GRASS_FED_BEEF",
        "target_id": "NUTRIENT_IRON",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.96,
        "mechanism": "Rich source of porphyrin-bound heme iron absorbed intact across enterocyte apical membranes via HCP1 without duodenal reduction.",
        "citation": "West AR, Oates PS. Mechanisms of heme iron absorption: recent advances. Am J Physiol Gastrointest Liver Physiol. 2008."
    },
    {
        "id": "REL_BEEF_SUPPORTS_B12",
        "source_id": "FOOD_GRASS_FED_BEEF",
        "target_id": "NUTRIENT_VITAMIN_B12",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.94,
        "mechanism": "Concentrates mitochondrial methylcobalamin and adenosylcobalamin.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_EGGS_SUPPORTS_B12",
        "source_id": "FOOD_EGGS",
        "target_id": "NUTRIENT_VITAMIN_B12",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.92,
        "mechanism": "Supplies bioavailable yolk cobalamin alongside lecithin phospholipids supporting mucosal transport.",
        "citation": "Watanabe F. Vitamin B12 sources and bioavailability. Exp Biol Med. 2007."
    },
    {
        "id": "REL_SPINACH_SUPPORTS_FOLATE",
        "source_id": "FOOD_SPINACH",
        "target_id": "NUTRIENT_FOLATE",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.95,
        "mechanism": "Supplies concentrated polyglutamate tetrahydrofolates (over 250 mcg DFE per cooked cup).",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_SPINACH_SUPPORTS_MAGNESIUM",
        "source_id": "FOOD_SPINACH",
        "target_id": "NUTRIENT_MAGNESIUM",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.90,
        "mechanism": "Chlorophyll pigments possess a central coordinated magnesium atom providing ~150 mg elemental magnesium per cup.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_LENTILS_SUPPORTS_FOLATE",
        "source_id": "FOOD_LENTILS",
        "target_id": "NUTRIENT_FOLATE",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.96,
        "mechanism": "Provides 358 mcg folate per cup (90% of adult RDA), driving remethylation pathways.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_YOGURT_SUPPORTS_CALCIUM",
        "source_id": "FOOD_GREEK_YOGURT",
        "target_id": "NUTRIENT_CALCIUM",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.95,
        "mechanism": "Provides bioavailable calcium phosphopeptide complexes alongside lactic acid that enhances gut mineral solubility.",
        "citation": "Heaney RP. Dairy and bone health. J Am Coll Nutr. 2009."
    },
    {
        "id": "REL_ALMONDS_SUPPORTS_VIT_E",
        "source_id": "FOOD_ALMONDS",
        "target_id": "NUTRIENT_VITAMIN_E",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.96,
        "mechanism": "Provides 7.3 mg natural RRR-alpha-tocopherol per 30g serving (50% RDA), the most biologically active vitamer.",
        "citation": "Traber MG. Vitamin E regulatory mechanisms. Annu Rev Nutr. 2007."
    },
    {
        "id": "REL_PUMPKIN_SEEDS_SUPPORTS_ZINC",
        "source_id": "FOOD_PUMPKIN_SEEDS",
        "target_id": "NUTRIENT_ZINC",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.93,
        "mechanism": "Provides 2.2 mg elemental zinc per ounce to support zinc-finger transcription factors.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_PUMPKIN_SEEDS_SUPPORTS_MAGNESIUM",
        "source_id": "FOOD_PUMPKIN_SEEDS",
        "target_id": "NUTRIENT_MAGNESIUM",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.94,
        "mechanism": "Supplies 156 mg elemental magnesium per ounce (37% of daily requirement).",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_OYSTERS_SUPPORTS_ZINC",
        "source_id": "FOOD_OYSTERS",
        "target_id": "NUTRIENT_ZINC",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.99,
        "mechanism": "Highest dietary zinc density in nature (32 mg per 6 oysters, ~300% RDA) in an easily digested peptide matrix.",
        "citation": "King JC. Zinc: an essential but elusive nutrient. Am J Clin Nutr. 2011."
    },
    {
        "id": "REL_SARDINES_SUPPORTS_CALCIUM",
        "source_id": "FOOD_SARDINES",
        "target_id": "NUTRIENT_CALCIUM",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.94,
        "mechanism": "Whole edible bones furnish genuine microcrystalline hydroxyapatite with ideal 2:1 calcium-to-phosphorus ratios.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_NUTRITIONAL_YEAST_SUPPORTS_B_COMPLEX",
        "source_id": "FOOD_NUTRITIONAL_YEAST",
        "target_id": "NUTRIENT_VITAMIN_B1",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.95,
        "mechanism": "Supplies concentrated thiamine, riboflavin, niacin, and pyridoxine to replenish metabolic coenzymes.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_AVOCADO_SUPPORTS_POTASSIUM",
        "source_id": "FOOD_AVOCADO",
        "target_id": "NUTRIENT_POTASSIUM",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.94,
        "mechanism": "Supplies 730 mg bioavailable potassium per avocado alongside monounsaturated oleic acid matrix.",
        "citation": "Dreher ML, Davenport AJ. Hass avocado composition and potential health effects. Crit Rev Food Sci Nutr. 2013."
    },
    {
        "id": "REL_CITRUS_SUPPORTS_VIT_C",
        "source_id": "FOOD_CITRUS_FRUITS",
        "target_id": "NUTRIENT_VITAMIN_C",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.96,
        "mechanism": "Supplies 70-90 mg L-ascorbic acid per fruit alongside hesperidin and naringenin bioflavonoids.",
        "citation": "USDA FoodData Central Database."
    },
    {
        "id": "REL_BRAZIL_NUTS_SUPPORTS_SELENIUM",
        "source_id": "FOOD_BRAZIL_NUTS",
        "target_id": "NUTRIENT_SELENIUM",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.99,
        "mechanism": "A single Brazil nut provides 68-91 mcg of organic selenomethionine, instantly saturating iodothyronine deiodinase requirements.",
        "citation": "Thomson CD, et al. Brazil nuts: an effective way to improve selenium status. Am J Clin Nutr. 2008."
    },
    {
        "id": "REL_SEAWEED_SUPPORTS_IODINE",
        "source_id": "FOOD_SEAWEED",
        "target_id": "NUTRIENT_IODINE",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.99,
        "mechanism": "Concentrates marine iodide salts (>1000 mcg per gram in kelp), reversing thyroid hormone production deficits.",
        "citation": "Teas J, et al. Variability of iodine content in common commercially available edible seaweeds. Thyroid. 2004."
    },
    {
        "id": "REL_SWEET_POTATO_SUPPORTS_VIT_A",
        "source_id": "FOOD_SWEET_POTATO",
        "target_id": "NUTRIENT_VITAMIN_A",
        "relationship_type": RelationshipType.SUPPORTS,
        "weight": 0.95,
        "mechanism": "Supplies dense all-trans-beta-carotene converted by intestinal BCMO1 enzyme into retinol for vision and barrier repair.",
        "citation": "van Jaarsveld PJ, et al. Beta-carotene-rich orange-fleshed sweet potato improves the vitamin A status of primary school children. Am J Clin Nutr. 2005."
    }
]
