"""
Clinical Reasoning & Narrative Synthesis Engine
Phase 4: Explainable AI and Risk Factor Analysis System

Transforms statistical SHAP values and model feature weights into:
1. Primary clinical risk driver summaries
2. Natural, patient-accessible narrative explanations
3. Protective counterbalance analysis
4. Physician-grade pathophysiological evaluations with ICD-10 differential codes and confirmatory lab tests
5. 5-Category unified risk factor cards (Dietary, Lifestyle, Symptom, Medical, Supplement)
"""

from typing import Dict, Any, List, Optional
from .constants import TARGET_NUTRIENTS, NUTRIENT_CODES, CLINICAL_URGENCY_WEIGHTS
from .sanitization import safe_float, safe_int, safe_bool


class ClinicalReasoningEngine:
    """
    Evidence-grounded medical reasoning and clinical narrative synthesis engine.
    """

    # ICD-10 and Confirmatory Diagnostic Workup Mapping
    CLINICAL_WORKUP_CATALOG = {
        "Vitamin D": {
            "icd10": ["E55.9 - Vitamin D deficiency, unspecified", "M83.9 - Adult osteomalacia, unspecified"],
            "confirmatory_labs": "Serum 25-hydroxyvitamin D [25(OH)D], Intact PTH, Serum Calcium, Alkaline Phosphatase",
            "clinical_threshold": "< 20 ng/mL (50 nmol/L) indicates deficiency; 21-29 ng/mL indicates insufficiency.",
            "guideline": "Endocrine Society Clinical Practice Guidelines: Evaluation, Treatment, and Prevention of Vitamin D Deficiency"
        },
        "Iron": {
            "icd10": ["D50.9 - Iron deficiency anemia, unspecified", "E61.1 - Iron deficiency"],
            "confirmatory_labs": "Serum Ferritin, Total Iron Binding Capacity (TIBC), Serum Iron, Transferrin Saturation, CBC (MCV, MCH)",
            "clinical_threshold": "Serum ferritin < 30 ng/mL in adults, or transferrin saturation < 20%.",
            "guideline": "American Gastroenterological Association: Medical Evaluation of Iron Deficiency Anemia"
        },
        "Vitamin B12": {
            "icd10": ["D51.9 - Vitamin B12 deficiency anemia, unspecified", "E53.8 - Deficiency of other specified B group vitamins"],
            "confirmatory_labs": "Serum Total Cobalamin (B12), Methylmalonic Acid (MMA), Serum Homocysteine, Holotranscobalamin",
            "clinical_threshold": "Serum B12 < 200 pg/mL (< 148 pmol/L); elevated MMA (> 0.27 umol/L) confirms tissue-level cellular deficiency.",
            "guideline": "British Society for Haematology: Guidelines for the diagnosis and treatment of cobalamin and folate disorders"
        },
        "Folate": {
            "icd10": ["D52.9 - Folate deficiency anemia, unspecified", "E53.8 - Other specified B-group vitamin deficiency"],
            "confirmatory_labs": "RBC Folate (most accurate long-term tissue reserve marker), Serum Folate, Serum Homocysteine",
            "clinical_threshold": "Serum folate < 3 ng/mL (< 7 nmol/L); RBC folate < 140 ng/mL.",
            "guideline": "World Health Organization: Serum and red blood cell folate concentrations for assessing population status"
        },
        "Calcium": {
            "icd10": ["E58 - Dietary calcium deficiency", "E83.51 - Hypocalcemia"],
            "confirmatory_labs": "Ionized Calcium (biologically active fraction), Total Serum Calcium corrected for Albumin, 24-hr Urine Calcium",
            "clinical_threshold": "Corrected total calcium < 8.5 mg/dL (< 2.12 mmol/L) or ionized calcium < 4.65 mg/dL.",
            "guideline": "Institute of Medicine: Dietary Reference Intakes for Calcium and Vitamin D"
        },
        "Magnesium": {
            "icd10": ["E61.2 - Deficiency of magnesium", "E83.42 - Hypomagnesemia"],
            "confirmatory_labs": "RBC Magnesium (preferred for intracellular stores), Serum Magnesium, 24-hr Urinary Magnesium Excretion",
            "clinical_threshold": "Serum Mg < 1.7 mg/dL (< 0.70 mmol/L); note that < 1% of total body magnesium resides in serum.",
            "guideline": "Sub-clinical Magnesium Deficiency in Cardiology & Primary Care (Open Heart/BMJ)"
        },
        "Zinc": {
            "icd10": ["E60 - Dietary zinc deficiency", "E61.3 - Deficiency of zinc"],
            "confirmatory_labs": "Fasting Morning Plasma/Serum Zinc, Alkaline Phosphatase (zinc-dependent enzyme)",
            "clinical_threshold": "Fasting plasma zinc < 70 ug/dL in men, < 66 ug/dL in non-pregnant women.",
            "guideline": "International Zinc Nutrition Consultative Group (IZiNCG) Assessment Guidelines"
        },
        "Vitamin C": {
            "icd10": ["E54 - Ascorbic acid deficiency", "E54 - Scurvy"],
            "confirmatory_labs": "Plasma Ascorbic Acid Concentration, Leukocyte Ascorbic Acid (tissue reserve marker)",
            "clinical_threshold": "Plasma ascorbic acid < 0.2 mg/dL (< 11.4 umol/L) indicates severe deficiency.",
            "guideline": "NIH Office of Dietary Supplements: Vitamin C Fact Sheet for Health Professionals"
        },
        "Vitamin A": {
            "icd10": ["E50.9 - Vitamin A deficiency, unspecified", "E50.0 - Vitamin A deficiency with conjunctival xerosis"],
            "confirmatory_labs": "Serum Retinol (HPLC), Retinol-Binding Protein (RBP)",
            "clinical_threshold": "Serum retinol < 0.70 umol/L (< 20 ug/dL) indicates clinical deficiency.",
            "guideline": "WHO Global Prevalence of Vitamin A Deficiency in Populations at Risk"
        },
        "Vitamin E": {
            "icd10": ["E56.0 - Deficiency of vitamin E"],
            "confirmatory_labs": "Alpha-tocopherol/total lipid ratio, Serum Alpha-Tocopherol",
            "clinical_threshold": "Serum alpha-tocopherol < 12 umol/L (< 5 ug/mL) or ratio < 0.8 mg/g total lipids.",
            "guideline": "European Society for Clinical Nutrition and Metabolism (ESPEN) Micronutrient Guidelines"
        },
        "Protein": {
            "icd10": ["E46 - Unspecified protein-calorie malnutrition", "E43 - Severe protein-calorie malnutrition"],
            "confirmatory_labs": "Serum Albumin, Prealbumin (Transthyretin - sensitive acute marker), Transferrin, Total Protein",
            "clinical_threshold": "Prealbumin < 15 mg/dL indicates acute mild-moderate protein depletion; albumin < 3.5 g/dL.",
            "guideline": "ASPEN/AND Consensus Statement: Characteristics of Adult Malnutrition"
        },
        "Vitamin B1": {
            "icd10": ["E51.9 - Thiamine deficiency, unspecified", "E51.1 - Beriberi", "E51.2 - Wernicke encephalopathy"],
            "confirmatory_labs": "Whole blood Thiamine Pyrophosphate (TPP) by HPLC, Erythrocyte Transketolase Activity Coefficient (ETKAC)",
            "clinical_threshold": "Whole blood TPP < 70 nmol/L; ETKAC > 1.25 indicates significant intracellular deficiency.",
            "guideline": "EFSA Scientific Opinion & European Federation of Neurological Societies Wernicke Guidelines"
        },
        "Vitamin B2": {
            "icd10": ["E53.0 - Riboflavin deficiency (Ariboflavinosis)"],
            "confirmatory_labs": "Erythrocyte Glutathione Reductase Activity Coefficient (EGRAC), Urinary Riboflavin Excretion",
            "clinical_threshold": "EGRAC > 1.40 confirms deficiency (normal < 1.20); urinary riboflavin < 40 mcg/g creatinine.",
            "guideline": "WHO Vitamin and Mineral Requirements in Human Nutrition: Riboflavin"
        },
        "Vitamin B3": {
            "icd10": ["E52 - Niacin deficiency (Pellagra)"],
            "confirmatory_labs": "Urinary N1-methylnicotinamide (NMN) and 2-pyridone metabolites, Plasma Niacin",
            "clinical_threshold": "Urinary NMN < 5.8 umol/day (< 0.8 mg/day); 2-pyridone/NMN excretion ratio < 1.0.",
            "guideline": "WHO Pellagra Prevention Guidelines & NIH Dietary Supplement Fact Sheet: Niacin"
        },
        "Vitamin B6": {
            "icd10": ["E53.1 - Pyridoxine deficiency", "D64.3 - Other sideroblastic anemias (pyridoxine-responsive)"],
            "confirmatory_labs": "Fasting Plasma Pyridoxal 5'-Phosphate (PLP), Urinary 4-Pyridoxic Acid (4-PA), Plasma Homocysteine",
            "clinical_threshold": "Plasma PLP < 20 nmol/L (< 5 ug/L) indicates deficiency; 20-30 nmol/L indicates marginal status.",
            "guideline": "Endocrine Society & American Society for Hematology Guidelines"
        },
        "Potassium": {
            "icd10": ["E87.6 - Hypokalemia"],
            "confirmatory_labs": "Serum Potassium, 12-lead ECG (U-waves, ST segment depression), Urine Potassium-to-Creatinine Ratio, Serum Magnesium",
            "clinical_threshold": "Serum K+ < 3.5 mEq/L (moderate 2.5-3.0 mEq/L, severe < 2.5 mEq/L with high arrhythmia risk).",
            "guideline": "AHA/ACC Clinical Practice Guidelines for Management of Hypokalemia"
        },
        "Selenium": {
            "icd10": ["E61.4 - Deficiency of selenium", "M12.8 - Other specific arthropathies (Kashin-Beck disease)"],
            "confirmatory_labs": "Serum/Plasma Selenium (ICP-MS), Erythrocyte Glutathione Peroxidase 3 (GPx3) Activity",
            "clinical_threshold": "Serum selenium < 70 ug/L (< 0.89 umol/L); plateaus at 100 ug/L for optimal GPx activity.",
            "guideline": "World Health Organization Guidelines on Trace Elements in Human Nutrition"
        },
        "Iodine": {
            "icd10": ["E01.8 - Other iodine-deficiency related thyroid disorders and allied conditions", "E00.9 - Congenital iodine-deficiency syndrome"],
            "confirmatory_labs": "24-hr Median Spot Urinary Iodine Concentration (UIC), Serum TSH, Free T4, Serum Thyroglobulin (Tg)",
            "clinical_threshold": "Median UIC < 100 ug/L indicates population insufficiency; < 50 ug/L indicates moderate-severe deficiency.",
            "guideline": "WHO/UNICEF/IGN Guidelines for Assessment of Iodine Deficiency Disorders"
        }
    }

    @classmethod
    def synthesize_narrative(
        cls,
        nutrient_name: str,
        risk_level: str,
        probability: float,
        positive_factors: List[Dict[str, Any]],
        protective_factors: List[Dict[str, Any]],
        unscaled_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates dual-layer clinical reasoning:
        1. Non-technical patient-facing narrative.
        2. Clinician-facing pathophysiological assessment.
        """
        unscaled_features = unscaled_features or {}
        top_driver_names = [f["factor_name"] for f in positive_factors[:4]]
        protective_names = [f["factor_name"] for f in protective_factors[:3]]

        # Fallback if no specific drivers were separated
        if not top_driver_names:
            top_driver_names = ["Lifestyle and dietary screening patterns"]

        # 1. Patient-Friendly Narrative Generation
        if risk_level == "HIGH":
            drivers_text = ", ".join(top_driver_names[:-1]) + (" and " + top_driver_names[-1] if len(top_driver_names) > 1 else top_driver_names[0])
            patient_narrative = (
                f"Your screening results indicate a HIGH likelihood of {nutrient_name} deficiency (estimated probability: {int(probability*100)}%). "
                f"The primary contributors to this elevated risk are {drivers_text}. "
                f"When these factors coincide, your daily physiological requirements may significantly exceed your current dietary intake or absorption capacity."
            )
        elif risk_level == "MODERATE":
            drivers_text = ", ".join(top_driver_names[:2])
            patient_narrative = (
                f"Your assessment reflects a MODERATE risk for {nutrient_name} insufficiency (estimated probability: {int(probability*100)}%). "
                f"Key factors driving this score include {drivers_text}. "
                f"Targeted nutritional adjustments or regular dietary inclusion can proactively prevent progression into clinical deficiency."
            )
        else:
            patient_narrative = (
                f"Your current profile reflects a LOW risk for {nutrient_name} deficiency (estimated probability: {int(probability*100)}%). "
                f"Your reported dietary and lifestyle habits provide adequate baseline coverage for this nutrient."
            )

        # 2. Protective Counterbalance Analysis
        if protective_names:
            prot_text = ", ".join(protective_names)
            protective_summary = (
                f"Importantly, your reported positive habits—specifically {prot_text}—act as favorable protective factors that counterbalance further risk acceleration."
            )
        else:
            protective_summary = "No prominent protective dietary or supplementation factors were detected in your current assessment."

        # 3. Clinician-Oriented Pathophysiological Assessment
        workup = cls.CLINICAL_WORKUP_CATALOG.get(nutrient_name, {
            "icd10": [f"E56.8 - Other nutritional deficiencies"],
            "confirmatory_labs": f"Serum {nutrient_name} quantitation",
            "clinical_threshold": "Below standardized reference laboratory range.",
            "guideline": "Clinical Nutritional Assessment Guidelines"
        })

        clinician_notes = (
            f"Pathophysiological Risk Profile: Machine learning ensemble indicates a {risk_level} deficiency probability ({probability:.4f}). "
            f"Key risk attributions: {'; '.join(top_driver_names)}. "
            f"Recommended Diagnostic Workup: {workup['confirmatory_labs']}. "
            f"Diagnostic Threshold: {workup['clinical_threshold']} "
            f"Grounding Guideline: {workup['guideline']}."
        )

        return {
            "nutrient": nutrient_name,
            "risk_level": risk_level,
            "primary_contributors": top_driver_names,
            "narrative_explanation": patient_narrative,
            "protective_summary": protective_summary,
            "clinical_notes": clinician_notes,
            "icd10_considerations": workup.get("icd10", [])
        }

    @classmethod
    def extract_categorized_risk_factors(
        cls,
        unscaled_features: Dict[str, Any],
        nutrient_predictions: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extracts and organizes comprehensive patient risk factors across the 5 core categories:
        DIETARY, LIFESTYLE, SYMPTOM, MEDICAL_HISTORY, SUPPLEMENT, plus PHYSIOLOGICAL.
        """
        categories: Dict[str, List[Dict[str, Any]]] = {
            "dietary_factors": [],
            "lifestyle_factors": [],
            "symptom_factors": [],
            "medical_factors": [],
            "supplement_factors": [],
            "physiological_factors": []
        }

        # Flatten nested structures if passed
        flat: Dict[str, Any] = dict(unscaled_features)
        if "dietary_habits" in flat and isinstance(flat["dietary_habits"], dict):
            flat.update(flat["dietary_habits"])
        if "lifestyle_factors" in flat and isinstance(flat["lifestyle_factors"], dict):
            flat.update(flat["lifestyle_factors"])

        # Helper to map affected nutrients based on elevated predictions
        def get_affected_nutrients(target_keys: List[str]) -> List[str]:
            affected = []
            for pred in nutrient_predictions:
                nut = pred.get("nutrient", "")
                risk = pred.get("risk_level", "LOW")
                if risk in ["HIGH", "MODERATE"] and nut in target_keys:
                    affected.append(nut)
            return affected if affected else [target_keys[0]] if target_keys else ["General Micronutrients"]

        # --- 1. DIETARY FACTORS ---
        diet = str(flat.get("dietary_pattern", "")).upper()
        if "VEGAN" in diet:
            categories["dietary_factors"].append({
                "factor_id": "diet_vegan",
                "factor_name": "Strict Vegan Dietary Pattern",
                "category": "DIETARY",
                "severity": "HIGH",
                "impact_score": 0.42,
                "impact_magnitude": "HIGH",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Vitamin B12", "Iron", "Zinc", "Calcium"]),
                "clinical_mechanism": "Complete exclusion of animal proteins severely curtails natural cyanocobalamin and highly bioavailable heme iron.",
                "recommended_action": "Incorporate daily B12 supplementation (250-500 mcg) and fortified plant milks/nutritional yeast.",
                "evidence_citation": "American Journal of Clinical Nutrition / NIH Fact Sheet"
            })
        elif "VEGETARIAN" in diet:
            categories["dietary_factors"].append({
                "factor_id": "diet_vegetarian",
                "factor_name": "Vegetarian Dietary Pattern",
                "category": "DIETARY",
                "severity": "MODERATE",
                "impact_score": 0.28,
                "impact_magnitude": "MEDIUM",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Iron", "Vitamin B12", "Zinc"]),
                "clinical_mechanism": "Non-heme plant iron has lower fractional bioavailability (5-12% vs. 15-35% for heme iron) and is inhibited by phytates.",
                "recommended_action": "Pair iron-rich plant foods (lentils, spinach) with Vitamin C rich sources to enhance non-heme absorption.",
                "evidence_citation": "WHO Micronutrient Series: Iron Deficiency Guidelines"
            })

        has_df = flat.get("has_dairy_free", False) or "dairy-free" in str(flat.get("dietary_restrictions", [])).lower()
        if has_df:
            categories["dietary_factors"].append({
                "factor_id": "diet_dairy_free",
                "factor_name": "Dairy-Free Dietary Restriction",
                "category": "DIETARY",
                "severity": "HIGH",
                "impact_score": 0.35,
                "impact_magnitude": "HIGH",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Calcium", "Vitamin D", "Protein"]),
                "clinical_mechanism": "Exclusion of milk products eliminates the primary dietary calcium source without intentional fortified replacement.",
                "recommended_action": "Consume calcium-fortified plant milks, sesame tahini, bok choy, or calcium citrate supplements.",
                "evidence_citation": "Osteoporosis International: Dietary Calcium Intake"
            })

        raw_fv = flat.get("daily_fruit_vegetable_servings") or flat.get("fruit_veg_servings") or flat.get("produce_servings")
        fruit_veg = safe_float(raw_fv, default=3.0)
        if fruit_veg <= 1.5:
            categories["dietary_factors"].append({
                "factor_id": "low_produce",
                "factor_name": "Sub-optimal Fruit & Vegetable Intake (<= 1.5 servings/day)",
                "category": "DIETARY",
                "severity": "HIGH",
                "impact_score": 0.38,
                "impact_magnitude": "HIGH",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Vitamin C", "Folate", "Magnesium", "Vitamin A"]),
                "clinical_mechanism": "Insufficient produce intake directly causes dietary shortfall of labile ascorbic acid, natural folates, and cellular magnesium.",
                "recommended_action": "Increase intake of raw citrus fruits, berries, dark leafy greens, and cruciferous vegetables to >= 5 servings daily.",
                "evidence_citation": "WHO Guidelines: Fruit and Vegetable Intake in Disease Prevention"
            })

        # --- 2. LIFESTYLE FACTORS ---
        raw_sun = flat.get("sunlight_exposure_min_per_day") or flat.get("sunlight_minutes")
        sun_mins = safe_float(raw_sun, default=30.0)
        if sun_mins < 20:
            categories["lifestyle_factors"].append({
                "factor_id": "low_sunlight",
                "factor_name": f"Minimal Sunlight Exposure ({int(sun_mins)} min/day)",
                "category": "LIFESTYLE",
                "severity": "CRITICAL" if sun_mins < 10 else "HIGH",
                "impact_score": 0.45,
                "impact_magnitude": "HIGH",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Vitamin D", "Calcium"]),
                "clinical_mechanism": "Cutaneous UVB photolysis of 7-dehydrocholesterol to pre-vitamin D3 is insufficient to maintain physiological circulating 25(OH)D.",
                "recommended_action": "Seek 15-20 minutes of midday sunlight exposure or supplement with 2,000-4,000 IU/day Vitamin D3.",
                "evidence_citation": "Endocrine Society Clinical Practice Guidelines: Vitamin D Deficiency"
            })

        alcohol = str(flat.get("alcohol_consumption", "")).upper()
        if alcohol in ["MODERATE", "HEAVY"]:
            categories["lifestyle_factors"].append({
                "factor_id": "alcohol_consumption",
                "factor_name": f"{alcohol.capitalize()} Alcohol Intake",
                "category": "LIFESTYLE",
                "severity": "HIGH" if alcohol == "HEAVY" else "MODERATE",
                "impact_score": 0.32,
                "impact_magnitude": "MEDIUM",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Magnesium", "Folate", "Zinc", "Vitamin B12"]),
                "clinical_mechanism": "Alcohol acutely increases renal excretion of magnesium, impairs intestinal zinc transport, and accelerates folate catabolism.",
                "recommended_action": "Moderate alcohol intake and ensure replenishing intake of electrolyte-rich foods and oral magnesium.",
                "evidence_citation": "Alcoholism: Clinical and Experimental Research (Journal of Studies on Alcohol)"
            })

        smoke = str(flat.get("smoking_status", "")).upper()
        if smoke in ["CURRENT", "REGULAR", "SMOKER"]:
            categories["lifestyle_factors"].append({
                "factor_id": "active_smoking",
                "factor_name": "Active Tobacco Smoking",
                "category": "LIFESTYLE",
                "severity": "HIGH",
                "impact_score": 0.36,
                "impact_magnitude": "HIGH",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Vitamin C", "Vitamin E"]),
                "clinical_mechanism": "Inhaled oxidants induce severe oxidative stress, increasing daily metabolic turnover of Vitamin C by ~35 mg/day.",
                "recommended_action": "Increase Vitamin C intake by an additional 35-50 mg daily and engage in smoking cessation therapy.",
                "evidence_citation": "Institute of Medicine DRI Guidelines: Vitamin C in Smokers"
            })

        # --- 3. SYMPTOM FACTORS ---
        symptoms = flat.get("symptoms", {})
        if isinstance(symptoms, dict):
            for sym, sev in symptoms.items():
                if int(sev) >= 6:
                    name_clean = sym.replace("_", " ").title()
                    assoc = (
                        ["Iron", "Vitamin B12", "Folate", "Vitamin D"] if "fatigue" in sym
                        else ["Calcium", "Vitamin D"] if "bone" in sym or "joint" in sym
                        else ["Magnesium", "Calcium"] if "cramp" in sym
                        else ["Iron", "Zinc", "Protein"] if "hair" in sym or "nail" in sym
                        else ["Vitamin B12", "Folate"] if "brain" in sym or "numb" in sym
                        else ["Vitamin C"] if "bruis" in sym or "bleed" in sym
                        else ["Vitamin A"] if "vision" in sym or "eye" in sym
                        else ["General Micronutrients"]
                    )
                    categories["symptom_factors"].append({
                        "factor_id": f"symptom_{sym}",
                        "factor_name": f"Elevated {name_clean} (Severity: {sev}/10)",
                        "category": "SYMPTOM",
                        "severity": "HIGH" if int(sev) >= 8 else "MODERATE",
                        "impact_score": round(float(sev) * 0.04, 4),
                        "impact_magnitude": "HIGH" if int(sev) >= 8 else "MEDIUM",
                        "direction": "RISK_INCREASING",
                        "associated_nutrients": get_affected_nutrients(assoc),
                        "clinical_mechanism": f"Clinical manifestation frequently secondary to tissue-level depletion of {', '.join(assoc)}.",
                        "recommended_action": f"Monitor symptom trajectory upon commencement of targeted dietary and micronutrient therapy.",
                        "evidence_citation": "Mayo Clinic Medical Reference: Deficiency Symptoms & Presentations"
                    })

        # --- 4. MEDICAL FACTORS ---
        med_history = flat.get("medical_history", [])
        if isinstance(med_history, list):
            for entry in med_history:
                cond = str(entry.get("condition_name", entry.get("condition", entry if isinstance(entry, str) else ""))).lower()
                if any(k in cond for k in ["celiac", "crohn", "colitis", "gastritis", "malabsorption", "ibs"]):
                    categories["medical_factors"].append({
                        "factor_id": "med_malabsorption",
                        "factor_name": "Gastrointestinal Malabsorption Syndrome",
                        "category": "MEDICAL_HISTORY",
                        "severity": "CRITICAL",
                        "impact_score": 0.48,
                        "impact_magnitude": "HIGH",
                        "direction": "RISK_INCREASING",
                        "associated_nutrients": get_affected_nutrients(["Vitamin D", "Iron", "Vitamin B12", "Zinc", "Calcium"]),
                        "clinical_mechanism": "Intestinal mucosal inflammation or enterocyte blunting severely inhibits active and passive micronutrient transport.",
                        "recommended_action": "Refer to gastroenterologist; consider sublingual, chelated, or parenteral nutrient formulations.",
                        "evidence_citation": "American College of Gastroenterology Malabsorption Practice Guidelines"
                    })
                elif any(k in cond for k in ["bypass", "bariatric", "gastrectomy"]):
                    categories["medical_factors"].append({
                        "factor_id": "med_bariatric",
                        "factor_name": "Bariatric Surgery History",
                        "category": "MEDICAL_HISTORY",
                        "severity": "CRITICAL",
                        "impact_score": 0.50,
                        "impact_magnitude": "HIGH",
                        "direction": "RISK_INCREASING",
                        "associated_nutrients": get_affected_nutrients(["Vitamin B12", "Iron", "Calcium", "Vitamin D"]),
                        "clinical_mechanism": "Loss of gastric intrinsic factor synthesis and duodenal bypass causes profound lifelong cobalamin and mineral malabsorption.",
                        "recommended_action": "Strict adherence to lifelong high-potency post-bariatric multivitamin and mineral regimen.",
                        "evidence_citation": "ASMBS Clinical Practice Guidelines for the Bariatric Patient"
                    })

        # --- 5. SUPPLEMENT FACTORS ---
        supps = flat.get("supplement_usage", [])
        if not supps or len(supps) == 0:
            categories["supplement_factors"].append({
                "factor_id": "supp_none",
                "factor_name": "Absence of Micronutrient Supplementation",
                "category": "SUPPLEMENT",
                "severity": "MODERATE",
                "impact_score": 0.25,
                "impact_magnitude": "MEDIUM",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Vitamin D", "Vitamin B12", "Iron"]),
                "clinical_mechanism": "No exogenous baseline safety net is in place to buffer dietary intake gaps or absorption fluctuations.",
                "recommended_action": "Consider introducing targeted, evidence-based supplementation tailored to flagged deficiency risks.",
                "evidence_citation": "NIH Office of Dietary Supplements Framework"
            })
        else:
            categories["supplement_factors"].append({
                "factor_id": "supp_active",
                "factor_name": "Active Dietary Supplement Regimen Reported",
                "category": "SUPPLEMENT",
                "severity": "LOW",
                "impact_score": -0.30,
                "impact_magnitude": "MEDIUM",
                "direction": "PROTECTIVE",
                "associated_nutrients": ["General Micronutrients"],
                "clinical_mechanism": "Exogenous intake helps mitigate nutritional deficits from dietary restrictions.",
                "recommended_action": "Verify supplement bio-availability, purity (third-party tested), and avoid competing mega-doses.",
                "evidence_citation": "USP Verified Supplement Guidelines"
            })

        # --- 6. PHYSIOLOGICAL / DEMOGRAPHIC FACTORS ---
        raw_bmi = flat.get("bmi")
        bmi_val = safe_float(raw_bmi, default=None)
        if bmi_val is not None and bmi_val > 0:
            bmi = bmi_val
        else:
            h_m = safe_float(flat.get("height_cm"), default=170.0) / 100.0
            w_kg = safe_float(flat.get("weight_kg"), default=70.0)
            bmi = w_kg / (h_m ** 2) if h_m > 0 else 23.0

        if bmi >= 30.0:
            categories["physiological_factors"].append({
                "factor_id": "phys_obesity",
                "factor_name": f"Class I/II Obesity (BMI: {bmi:.1f})",
                "category": "PHYSIOLOGICAL",
                "severity": "HIGH",
                "impact_score": 0.35,
                "impact_magnitude": "HIGH",
                "direction": "RISK_INCREASING",
                "associated_nutrients": get_affected_nutrients(["Vitamin D"]),
                "clinical_mechanism": "Adipose tissue volume sequesters circulating cholecalciferol, significantly lowering bioavailable serum 25(OH)D.",
                "recommended_action": "Higher oral doses of Vitamin D3 (typically 2-3x standard RDA) are required to achieve target serum concentrations.",
                "evidence_citation": "Journal of Clinical Endocrinology & Metabolism: Obesity & Vitamin D"
            })

        gender = str(flat.get("gender", "")).upper()
        if gender == "FEMALE":
            age = int(flat.get("age") or 30)
            if 15 <= age <= 50:
                categories["physiological_factors"].append({
                    "factor_id": "phys_menstruation",
                    "factor_name": "Reproductive-Age Female Biological Sex",
                    "category": "PHYSIOLOGICAL",
                    "severity": "MODERATE",
                    "impact_score": 0.31,
                    "impact_magnitude": "MEDIUM",
                    "direction": "RISK_INCREASING",
                    "associated_nutrients": get_affected_nutrients(["Iron", "Folate"]),
                    "clinical_mechanism": "Regular menstrual blood loss elevates daily elemental iron requirement to 18 mg/day (compared to 8 mg/day for adult males).",
                    "recommended_action": "Monitor monthly blood loss severity and ensure adequate iron-rich dietary intake or gentle iron supplementation.",
                    "evidence_citation": "CDC Guidelines for the Prevention of Iron Deficiency in Women"
                })

        return categories
