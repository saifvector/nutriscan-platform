"""
NutriScan Pediatric Clinical Safety Framework
Implements age-stratified dietary reference intakes (DRIs), Recommended Dietary Allowances (RDA),
Tolerable Upper Intake Levels (UL), deficiency cutoffs, and toxicity thresholds grounded in
guidelines from the Institute of Medicine (IOM/National Academy of Medicine) and
the American Academy of Pediatrics (AAP).

Supported Age Brackets:
1. 0–6 months (Infants)
2. 7–12 months (Older Infants)
3. 1–3 years (Toddlers)
4. 4–8 years (Young Children)
5. 9–13 years (Early Adolescents)
6. 14–18 years (Adolescents)
7. Adult (>18 years)

Supported Nutrients:
- Vitamin D
- Vitamin B12
- Iron
- Calcium
- Magnesium
- Zinc
- Folate
- Vitamin A
- Protein
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger("nutrient_platform.safety.pediatric")

# Standard Age Bracket Constants
AGE_0_TO_6M = "0-6m"
AGE_7_TO_12M = "7-12m"
AGE_1_TO_3Y = "1-3y"
AGE_4_TO_8Y = "4-8y"
AGE_9_TO_13Y = "9-13y"
AGE_14_TO_18Y = "14-18y"
AGE_ADULT = "Adult"

AGE_BRACKETS = [
    AGE_0_TO_6M,
    AGE_7_TO_12M,
    AGE_1_TO_3Y,
    AGE_4_TO_8Y,
    AGE_9_TO_13Y,
    AGE_14_TO_18Y,
    AGE_ADULT
]

@dataclass(frozen=True)
class NutrientSafetyProfile:
    nutrient: str
    unit: str
    rda: float
    ul: float
    deficiency_biomarker_cutoff: float
    toxicity_biomarker_cutoff: float
    biomarker_name: str
    biomarker_unit: str
    clinical_notes: str


# Clinical Reference Tables: 7 Brackets x 9 Nutrients
PEDIATRIC_CLINICAL_PROFILES: Dict[str, Dict[str, NutrientSafetyProfile]] = {
    AGE_0_TO_6M: {
        "Vitamin D": NutrientSafetyProfile(
            nutrient="Vitamin D", unit="IU", rda=400.0, ul=1000.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=100.0,
            biomarker_name="Serum 25(OH)D", biomarker_unit="ng/mL",
            clinical_notes="AAP recommends 400 IU/day for all breastfed and partially breastfed infants."
        ),
        "Vitamin B12": NutrientSafetyProfile(
            nutrient="Vitamin B12", unit="mcg", rda=0.4, ul=2.0,
            deficiency_biomarker_cutoff=200.0, toxicity_biomarker_cutoff=1000.0,
            biomarker_name="Serum B12", biomarker_unit="pg/mL",
            clinical_notes="Exclusively breastfed infants of vegan mothers require supplementation."
        ),
        "Iron": NutrientSafetyProfile(
            nutrient="Iron", unit="mg", rda=0.27, ul=40.0,
            deficiency_biomarker_cutoff=12.0, toxicity_biomarker_cutoff=200.0,
            biomarker_name="Serum Ferritin", biomarker_unit="ng/mL",
            clinical_notes="Full-term infants have sufficient iron stores until 4-6 months."
        ),
        "Calcium": NutrientSafetyProfile(
            nutrient="Calcium", unit="mg", rda=200.0, ul=1000.0,
            deficiency_biomarker_cutoff=8.8, toxicity_biomarker_cutoff=10.8,
            biomarker_name="Serum Calcium", biomarker_unit="mg/dL",
            clinical_notes="Primarily derived from breast milk or infant formula."
        ),
        "Magnesium": NutrientSafetyProfile(
            nutrient="Magnesium", unit="mg", rda=30.0, ul=65.0,
            deficiency_biomarker_cutoff=1.6, toxicity_biomarker_cutoff=2.6,
            biomarker_name="Serum Magnesium", biomarker_unit="mg/dL",
            clinical_notes="Supplemental magnesium not recommended; diet only."
        ),
        "Zinc": NutrientSafetyProfile(
            nutrient="Zinc", unit="mg", rda=2.0, ul=4.0,
            deficiency_biomarker_cutoff=60.0, toxicity_biomarker_cutoff=130.0,
            biomarker_name="Serum Zinc", biomarker_unit="mcg/dL",
            clinical_notes="Critical for immune maturation and epithelial integrity."
        ),
        "Folate": NutrientSafetyProfile(
            nutrient="Folate", unit="mcg", rda=65.0, ul=150.0,
            deficiency_biomarker_cutoff=3.0, toxicity_biomarker_cutoff=20.0,
            biomarker_name="Serum Folate", biomarker_unit="ng/mL",
            clinical_notes="Adequate intake supplied by human milk/infant formula."
        ),
        "Vitamin A": NutrientSafetyProfile(
            nutrient="Vitamin A", unit="mcg RAE", rda=400.0, ul=600.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=80.0,
            biomarker_name="Serum Retinol", biomarker_unit="mcg/dL",
            clinical_notes="Avoid preformed retinol supplements; high toxicity sensitivity."
        ),
        "Protein": NutrientSafetyProfile(
            nutrient="Protein", unit="g", rda=9.1, ul=15.0,
            deficiency_biomarker_cutoff=7.0, toxicity_biomarker_cutoff=25.0,
            biomarker_name="Daily Protein Intake", biomarker_unit="g/day",
            clinical_notes="Excess protein can stress immature infant renal solute load."
        ),
    },

    AGE_7_TO_12M: {
        "Vitamin D": NutrientSafetyProfile(
            nutrient="Vitamin D", unit="IU", rda=400.0, ul=1500.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=100.0,
            biomarker_name="Serum 25(OH)D", biomarker_unit="ng/mL",
            clinical_notes="Maintain 400 IU/day supplementation until intake from formula/whole milk exceeds 1 L/day."
        ),
        "Vitamin B12": NutrientSafetyProfile(
            nutrient="Vitamin B12", unit="mcg", rda=0.5, ul=3.0,
            deficiency_biomarker_cutoff=200.0, toxicity_biomarker_cutoff=1000.0,
            biomarker_name="Serum B12", biomarker_unit="pg/mL",
            clinical_notes="Complementary feeding introduction."
        ),
        "Iron": NutrientSafetyProfile(
            nutrient="Iron", unit="mg", rda=11.0, ul=40.0,
            deficiency_biomarker_cutoff=12.0, toxicity_biomarker_cutoff=200.0,
            biomarker_name="Serum Ferritin", biomarker_unit="ng/mL",
            clinical_notes="Peak window for iron-deficiency anemia; prioritize iron-fortified cereals/pureed meats."
        ),
        "Calcium": NutrientSafetyProfile(
            nutrient="Calcium", unit="mg", rda=260.0, ul=1500.0,
            deficiency_biomarker_cutoff=8.8, toxicity_biomarker_cutoff=10.8,
            biomarker_name="Serum Calcium", biomarker_unit="mg/dL",
            clinical_notes="Supplied via breast milk/formula and complementary dairy."
        ),
        "Magnesium": NutrientSafetyProfile(
            nutrient="Magnesium", unit="mg", rda=75.0, ul=110.0,
            deficiency_biomarker_cutoff=1.6, toxicity_biomarker_cutoff=2.6,
            biomarker_name="Serum Magnesium", biomarker_unit="mg/dL",
            clinical_notes="Dietary intake from leafy vegetables, grains, legumes."
        ),
        "Zinc": NutrientSafetyProfile(
            nutrient="Zinc", unit="mg", rda=3.0, ul=5.0,
            deficiency_biomarker_cutoff=60.0, toxicity_biomarker_cutoff=130.0,
            biomarker_name="Serum Zinc", biomarker_unit="mcg/dL",
            clinical_notes="Essential for linear growth."
        ),
        "Folate": NutrientSafetyProfile(
            nutrient="Folate", unit="mcg", rda=80.0, ul=200.0,
            deficiency_biomarker_cutoff=3.0, toxicity_biomarker_cutoff=20.0,
            biomarker_name="Serum Folate", biomarker_unit="ng/mL",
            clinical_notes="Introduced via green purees, fruits, and enriched cereals."
        ),
        "Vitamin A": NutrientSafetyProfile(
            nutrient="Vitamin A", unit="mcg RAE", rda=500.0, ul=600.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=80.0,
            biomarker_name="Serum Retinol", biomarker_unit="mcg/dL",
            clinical_notes="Emphasize beta-carotene sources over retinyl palmitate."
        ),
        "Protein": NutrientSafetyProfile(
            nutrient="Protein", unit="g", rda=11.0, ul=20.0,
            deficiency_biomarker_cutoff=9.0, toxicity_biomarker_cutoff=35.0,
            biomarker_name="Daily Protein Intake", biomarker_unit="g/day",
            clinical_notes="Support rapid somatic growth."
        ),
    },

    AGE_1_TO_3Y: {
        "Vitamin D": NutrientSafetyProfile(
            nutrient="Vitamin D", unit="IU", rda=600.0, ul=2500.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=100.0,
            biomarker_name="Serum 25(OH)D", biomarker_unit="ng/mL",
            clinical_notes="IOM RDA is 600 IU (15 mcg). Upper Limit is 2500 IU."
        ),
        "Vitamin B12": NutrientSafetyProfile(
            nutrient="Vitamin B12", unit="mcg", rda=0.9, ul=5.0,
            deficiency_biomarker_cutoff=200.0, toxicity_biomarker_cutoff=1000.0,
            biomarker_name="Serum B12", biomarker_unit="pg/mL",
            clinical_notes="Toddler requirements."
        ),
        "Iron": NutrientSafetyProfile(
            nutrient="Iron", unit="mg", rda=7.0, ul=40.0,
            deficiency_biomarker_cutoff=12.0, toxicity_biomarker_cutoff=200.0,
            biomarker_name="Serum Ferritin", biomarker_unit="ng/mL",
            clinical_notes="Excess cow's milk (>24 oz/day) is a major risk factor for toddler microcytic anemia."
        ),
        "Calcium": NutrientSafetyProfile(
            nutrient="Calcium", unit="mg", rda=700.0, ul=2500.0,
            deficiency_biomarker_cutoff=8.8, toxicity_biomarker_cutoff=10.6,
            biomarker_name="Serum Calcium", biomarker_unit="mg/dL",
            clinical_notes="Essential for active skeletal mineralization."
        ),
        "Magnesium": NutrientSafetyProfile(
            nutrient="Magnesium", unit="mg", rda=80.0, ul=65.0,
            deficiency_biomarker_cutoff=1.6, toxicity_biomarker_cutoff=2.6,
            biomarker_name="Serum Magnesium", biomarker_unit="mg/dL",
            clinical_notes="UL applies strictly to supplemental magnesium salts."
        ),
        "Zinc": NutrientSafetyProfile(
            nutrient="Zinc", unit="mg", rda=3.0, ul=7.0,
            deficiency_biomarker_cutoff=65.0, toxicity_biomarker_cutoff=140.0,
            biomarker_name="Serum Zinc", biomarker_unit="mcg/dL",
            clinical_notes="Growth stunting prevention."
        ),
        "Folate": NutrientSafetyProfile(
            nutrient="Folate", unit="mcg", rda=150.0, ul=300.0,
            deficiency_biomarker_cutoff=3.5, toxicity_biomarker_cutoff=20.0,
            biomarker_name="Serum Folate", biomarker_unit="ng/mL",
            clinical_notes="Folic acid UL is 300 mcg."
        ),
        "Vitamin A": NutrientSafetyProfile(
            nutrient="Vitamin A", unit="mcg RAE", rda=300.0, ul=600.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=80.0,
            biomarker_name="Serum Retinol", biomarker_unit="mcg/dL",
            clinical_notes="Strict 600 mcg RAE ceiling on preformed vitamin A."
        ),
        "Protein": NutrientSafetyProfile(
            nutrient="Protein", unit="g", rda=13.0, ul=35.0,
            deficiency_biomarker_cutoff=10.0, toxicity_biomarker_cutoff=50.0,
            biomarker_name="Daily Protein Intake", biomarker_unit="g/day",
            clinical_notes="Adequate for muscular and cognitive development."
        ),
    },

    AGE_4_TO_8Y: {
        "Vitamin D": NutrientSafetyProfile(
            nutrient="Vitamin D", unit="IU", rda=600.0, ul=3000.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=100.0,
            biomarker_name="Serum 25(OH)D", biomarker_unit="ng/mL",
            clinical_notes="RDA 600 IU; Upper Limit 3,000 IU/day."
        ),
        "Vitamin B12": NutrientSafetyProfile(
            nutrient="Vitamin B12", unit="mcg", rda=1.2, ul=10.0,
            deficiency_biomarker_cutoff=200.0, toxicity_biomarker_cutoff=1000.0,
            biomarker_name="Serum B12", biomarker_unit="pg/mL",
            clinical_notes="Neurological myelination and erythropoiesis support."
        ),
        "Iron": NutrientSafetyProfile(
            nutrient="Iron", unit="mg", rda=10.0, ul=40.0,
            deficiency_biomarker_cutoff=15.0, toxicity_biomarker_cutoff=250.0,
            biomarker_name="Serum Ferritin", biomarker_unit="ng/mL",
            clinical_notes="School age iron requirement."
        ),
        "Calcium": NutrientSafetyProfile(
            nutrient="Calcium", unit="mg", rda=1000.0, ul=2500.0,
            deficiency_biomarker_cutoff=8.8, toxicity_biomarker_cutoff=10.6,
            biomarker_name="Serum Calcium", biomarker_unit="mg/dL",
            clinical_notes="Bone mineral accrual."
        ),
        "Magnesium": NutrientSafetyProfile(
            nutrient="Magnesium", unit="mg", rda=130.0, ul=110.0,
            deficiency_biomarker_cutoff=1.7, toxicity_biomarker_cutoff=2.6,
            biomarker_name="Serum Magnesium", biomarker_unit="mg/dL",
            clinical_notes="UL 110 mg for synthetic supplements."
        ),
        "Zinc": NutrientSafetyProfile(
            nutrient="Zinc", unit="mg", rda=5.0, ul=12.0,
            deficiency_biomarker_cutoff=65.0, toxicity_biomarker_cutoff=140.0,
            biomarker_name="Serum Zinc", biomarker_unit="mcg/dL",
            clinical_notes="Immune function and cell proliferation."
        ),
        "Folate": NutrientSafetyProfile(
            nutrient="Folate", unit="mcg", rda=200.0, ul=400.0,
            deficiency_biomarker_cutoff=3.5, toxicity_biomarker_cutoff=20.0,
            biomarker_name="Serum Folate", biomarker_unit="ng/mL",
            clinical_notes="UL 400 mcg synthetic folate."
        ),
        "Vitamin A": NutrientSafetyProfile(
            nutrient="Vitamin A", unit="mcg RAE", rda=400.0, ul=900.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=80.0,
            biomarker_name="Serum Retinol", biomarker_unit="mcg/dL",
            clinical_notes="Upper Limit 900 mcg RAE."
        ),
        "Protein": NutrientSafetyProfile(
            nutrient="Protein", unit="g", rda=19.0, ul=50.0,
            deficiency_biomarker_cutoff=15.0, toxicity_biomarker_cutoff=75.0,
            biomarker_name="Daily Protein Intake", biomarker_unit="g/day",
            clinical_notes="Somatic tissue growth."
        ),
    },

    AGE_9_TO_13Y: {
        "Vitamin D": NutrientSafetyProfile(
            nutrient="Vitamin D", unit="IU", rda=600.0, ul=4000.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=100.0,
            biomarker_name="Serum 25(OH)D", biomarker_unit="ng/mL",
            clinical_notes="RDA 600 IU; Upper Limit 4,000 IU/day."
        ),
        "Vitamin B12": NutrientSafetyProfile(
            nutrient="Vitamin B12", unit="mcg", rda=1.8, ul=15.0,
            deficiency_biomarker_cutoff=200.0, toxicity_biomarker_cutoff=1000.0,
            biomarker_name="Serum B12", biomarker_unit="pg/mL",
            clinical_notes="Pre-pubertal adolescent requirement."
        ),
        "Iron": NutrientSafetyProfile(
            nutrient="Iron", unit="mg", rda=8.0, ul=40.0,
            deficiency_biomarker_cutoff=15.0, toxicity_biomarker_cutoff=250.0,
            biomarker_name="Serum Ferritin", biomarker_unit="ng/mL",
            clinical_notes="If menarche has occurred, iron requirement increases to 11 mg."
        ),
        "Calcium": NutrientSafetyProfile(
            nutrient="Calcium", unit="mg", rda=1300.0, ul=3000.0,
            deficiency_biomarker_cutoff=8.8, toxicity_biomarker_cutoff=10.6,
            biomarker_name="Serum Calcium", biomarker_unit="mg/dL",
            clinical_notes="Peak bone mass velocity window (1300 mg/day)."
        ),
        "Magnesium": NutrientSafetyProfile(
            nutrient="Magnesium", unit="mg", rda=240.0, ul=350.0,
            deficiency_biomarker_cutoff=1.7, toxicity_biomarker_cutoff=2.6,
            biomarker_name="Serum Magnesium", biomarker_unit="mg/dL",
            clinical_notes="Bone matrix co-factor."
        ),
        "Zinc": NutrientSafetyProfile(
            nutrient="Zinc", unit="mg", rda=8.0, ul=23.0,
            deficiency_biomarker_cutoff=70.0, toxicity_biomarker_cutoff=150.0,
            biomarker_name="Serum Zinc", biomarker_unit="mcg/dL",
            clinical_notes="Pubertal transition and endocrine maturation."
        ),
        "Folate": NutrientSafetyProfile(
            nutrient="Folate", unit="mcg", rda=300.0, ul=600.0,
            deficiency_biomarker_cutoff=4.0, toxicity_biomarker_cutoff=20.0,
            biomarker_name="Serum Folate", biomarker_unit="ng/mL",
            clinical_notes="Synthetic folate UL 600 mcg."
        ),
        "Vitamin A": NutrientSafetyProfile(
            nutrient="Vitamin A", unit="mcg RAE", rda=600.0, ul=1700.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=80.0,
            biomarker_name="Serum Retinol", biomarker_unit="mcg/dL",
            clinical_notes="Upper Limit 1700 mcg RAE."
        ),
        "Protein": NutrientSafetyProfile(
            nutrient="Protein", unit="g", rda=34.0, ul=80.0,
            deficiency_biomarker_cutoff=25.0, toxicity_biomarker_cutoff=120.0,
            biomarker_name="Daily Protein Intake", biomarker_unit="g/day",
            clinical_notes="Accelerating pubertal growth spurt."
        ),
    },

    AGE_14_TO_18Y: {
        "Vitamin D": NutrientSafetyProfile(
            nutrient="Vitamin D", unit="IU", rda=600.0, ul=4000.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=100.0,
            biomarker_name="Serum 25(OH)D", biomarker_unit="ng/mL",
            clinical_notes="RDA 600 IU; Upper Limit 4,000 IU/day."
        ),
        "Vitamin B12": NutrientSafetyProfile(
            nutrient="Vitamin B12", unit="mcg", rda=2.4, ul=25.0,
            deficiency_biomarker_cutoff=200.0, toxicity_biomarker_cutoff=1000.0,
            biomarker_name="Serum B12", biomarker_unit="pg/mL",
            clinical_notes="Adolescent requirement equivalent to adult."
        ),
        "Iron": NutrientSafetyProfile(
            nutrient="Iron", unit="mg", rda=15.0, ul=45.0,
            deficiency_biomarker_cutoff=15.0, toxicity_biomarker_cutoff=300.0,
            biomarker_name="Serum Ferritin", biomarker_unit="ng/mL",
            clinical_notes="15 mg for menstruating females, 11 mg for males."
        ),
        "Calcium": NutrientSafetyProfile(
            nutrient="Calcium", unit="mg", rda=1300.0, ul=3000.0,
            deficiency_biomarker_cutoff=8.8, toxicity_biomarker_cutoff=10.6,
            biomarker_name="Serum Calcium", biomarker_unit="mg/dL",
            clinical_notes="Highest lifetime calcium requirement (1300 mg/day)."
        ),
        "Magnesium": NutrientSafetyProfile(
            nutrient="Magnesium", unit="mg", rda=385.0, ul=350.0,
            deficiency_biomarker_cutoff=1.7, toxicity_biomarker_cutoff=2.6,
            biomarker_name="Serum Magnesium", biomarker_unit="mg/dL",
            clinical_notes="410 mg for males, 360 mg for females. UL applies to supplements."
        ),
        "Zinc": NutrientSafetyProfile(
            nutrient="Zinc", unit="mg", rda=10.0, ul=34.0,
            deficiency_biomarker_cutoff=70.0, toxicity_biomarker_cutoff=150.0,
            biomarker_name="Serum Zinc", biomarker_unit="mcg/dL",
            clinical_notes="11 mg for males, 9 mg for females."
        ),
        "Folate": NutrientSafetyProfile(
            nutrient="Folate", unit="mcg", rda=400.0, ul=800.0,
            deficiency_biomarker_cutoff=4.0, toxicity_biomarker_cutoff=20.0,
            biomarker_name="Serum Folate", biomarker_unit="ng/mL",
            clinical_notes="Synthetic folate UL 800 mcg."
        ),
        "Vitamin A": NutrientSafetyProfile(
            nutrient="Vitamin A", unit="mcg RAE", rda=800.0, ul=2800.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=80.0,
            biomarker_name="Serum Retinol", biomarker_unit="mcg/dL",
            clinical_notes="900 mcg RAE for males, 700 mcg for females."
        ),
        "Protein": NutrientSafetyProfile(
            nutrient="Protein", unit="g", rda=49.0, ul=120.0,
            deficiency_biomarker_cutoff=35.0, toxicity_biomarker_cutoff=160.0,
            biomarker_name="Daily Protein Intake", biomarker_unit="g/day",
            clinical_notes="52 g for males, 46 g for females."
        ),
    },

    AGE_ADULT: {
        "Vitamin D": NutrientSafetyProfile(
            nutrient="Vitamin D", unit="IU", rda=800.0, ul=4000.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=100.0,
            biomarker_name="Serum 25(OH)D", biomarker_unit="ng/mL",
            clinical_notes="Endocrine Society sufficiency cutoff is 30 ng/mL; toxicity > 100 ng/mL."
        ),
        "Vitamin B12": NutrientSafetyProfile(
            nutrient="Vitamin B12", unit="mcg", rda=2.4, ul=50.0,
            deficiency_biomarker_cutoff=200.0, toxicity_biomarker_cutoff=1000.0,
            biomarker_name="Serum B12", biomarker_unit="pg/mL",
            clinical_notes="Suboptimal borderline range is 200-300 pg/mL."
        ),
        "Iron": NutrientSafetyProfile(
            nutrient="Iron", unit="mg", rda=18.0, ul=45.0,
            deficiency_biomarker_cutoff=15.0, toxicity_biomarker_cutoff=300.0,
            biomarker_name="Serum Ferritin", biomarker_unit="ng/mL",
            clinical_notes="18 mg for premenopausal women; 8 mg for men and postmenopausal women."
        ),
        "Calcium": NutrientSafetyProfile(
            nutrient="Calcium", unit="mg", rda=1000.0, ul=2500.0,
            deficiency_biomarker_cutoff=8.6, toxicity_biomarker_cutoff=10.5,
            biomarker_name="Serum Calcium", biomarker_unit="mg/dL",
            clinical_notes="1,000 mg for adults 19-50y; 1,200 mg for women >50y and men >70y."
        ),
        "Magnesium": NutrientSafetyProfile(
            nutrient="Magnesium", unit="mg", rda=400.0, ul=350.0,
            deficiency_biomarker_cutoff=1.7, toxicity_biomarker_cutoff=2.6,
            biomarker_name="Serum Magnesium", biomarker_unit="mg/dL",
            clinical_notes="UL applies to supplemental magnesium only (350 mg)."
        ),
        "Zinc": NutrientSafetyProfile(
            nutrient="Zinc", unit="mg", rda=11.0, ul=40.0,
            deficiency_biomarker_cutoff=70.0, toxicity_biomarker_cutoff=150.0,
            biomarker_name="Serum Zinc", biomarker_unit="mcg/dL",
            clinical_notes="11 mg for men, 8 mg for women."
        ),
        "Folate": NutrientSafetyProfile(
            nutrient="Folate", unit="mcg", rda=400.0, ul=1000.0,
            deficiency_biomarker_cutoff=4.0, toxicity_biomarker_cutoff=20.0,
            biomarker_name="Serum Folate", biomarker_unit="ng/mL",
            clinical_notes="600 mcg for pregnancy. UL 1,000 mcg applies to folic acid from supplements/fortification."
        ),
        "Vitamin A": NutrientSafetyProfile(
            nutrient="Vitamin A", unit="mcg RAE", rda=900.0, ul=3000.0,
            deficiency_biomarker_cutoff=20.0, toxicity_biomarker_cutoff=80.0,
            biomarker_name="Serum Retinol", biomarker_unit="mcg/dL",
            clinical_notes="900 mcg for men, 700 mcg for women. Teratogenic risk during pregnancy."
        ),
        "Protein": NutrientSafetyProfile(
            nutrient="Protein", unit="g", rda=56.0, ul=160.0,
            deficiency_biomarker_cutoff=40.0, toxicity_biomarker_cutoff=250.0,
            biomarker_name="Daily Protein Intake", biomarker_unit="g/day",
            clinical_notes="56 g for men, 46 g for women (0.8 g/kg body weight)."
        ),
    }
}


def get_age_bracket(age_years: float, age_months: Optional[float] = None) -> str:
    """
    Maps an age into the correct clinical safety age bracket.
    Supports either fractional/decimal years or explicit months.
    """
    if age_months is not None:
        if age_months <= 6.0:
            return AGE_0_TO_6M
        elif age_months <= 12.0:
            return AGE_7_TO_12M
        else:
            age_years = age_months / 12.0

    if age_years < 0.5:
        return AGE_0_TO_6M
    elif age_years < 1.0:
        return AGE_7_TO_12M
    elif age_years <= 3.0:
        return AGE_1_TO_3Y
    elif age_years <= 8.0:
        return AGE_4_TO_8Y
    elif age_years <= 13.0:
        return AGE_9_TO_13Y
    elif age_years <= 18.0:
        return AGE_14_TO_18Y
    else:
        return AGE_ADULT


def is_pediatric(age_years: float) -> bool:
    """Returns True if the patient is within pediatric age (< 18.0 years)."""
    return age_years < 18.0


def get_pediatric_guidelines(age_bracket: str, nutrient: str) -> Optional[NutrientSafetyProfile]:
    """Retrieves the clinical safety profile for a given age bracket and nutrient."""
    if age_bracket not in PEDIATRIC_CLINICAL_PROFILES:
        age_bracket = AGE_ADULT
    bracket_profiles = PEDIATRIC_CLINICAL_PROFILES.get(age_bracket, {})
    return bracket_profiles.get(nutrient)


def evaluate_pediatric_toxicity(
    age_years: float,
    nutrient: str,
    intake_or_dose: float,
    is_supplemental: bool = True
) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Checks if an intake or supplemental dose exceeds age-specific Upper Tolerable Limit (UL).
    Returns:
        (is_toxic, warning_message, age_specific_ul)
    """
    bracket = get_age_bracket(age_years)
    profile = get_pediatric_guidelines(bracket, nutrient)
    if not profile:
        return False, None, None

    # For magnesium, UL applies strictly to supplemental forms
    if nutrient == "Magnesium" and not is_supplemental:
        return False, None, profile.ul

    if intake_or_dose > profile.ul:
        msg = (
            f"SAFETY INTERVENTION: {nutrient} dose of {intake_or_dose:.1f} {profile.unit} "
            f"exceeds the clinical Upper Tolerable Limit (UL) of {profile.ul:.1f} {profile.unit} "
            f"for age bracket '{bracket}' (Age {age_years:.1f}y). Risk of pediatric toxicity!"
        )
        logger.warning(msg)
        return True, msg, profile.ul

    return False, None, profile.ul


def get_pediatric_biomarker_status(
    age_years: float,
    nutrient: str,
    biomarker_value: float
) -> Dict[str, Any]:
    """
    Evaluates a biomarker value against age-specific clinical cutoffs for deficiency and toxicity.
    """
    bracket = get_age_bracket(age_years)
    profile = get_pediatric_guidelines(bracket, nutrient)
    if not profile:
        return {"status": "UNKNOWN", "bracket": bracket}

    if biomarker_value < profile.deficiency_biomarker_cutoff:
        status = "DEFICIENT"
    elif biomarker_value > profile.toxicity_biomarker_cutoff:
        status = "TOXIC"
    else:
        status = "NORMAL"

    return {
        "nutrient": nutrient,
        "age_bracket": bracket,
        "biomarker_name": profile.biomarker_name,
        "value": biomarker_value,
        "unit": profile.biomarker_unit,
        "status": status,
        "deficiency_cutoff": profile.deficiency_biomarker_cutoff,
        "toxicity_cutoff": profile.toxicity_biomarker_cutoff,
        "notes": profile.clinical_notes
    }
