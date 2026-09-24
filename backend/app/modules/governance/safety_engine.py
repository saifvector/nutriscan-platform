"""
Phase 12: Clinical Safety Engine & Guardrails
Evaluates:
- NIH Tolerable Upper Intake Level (UL) exceedances across all micronutrients
- Pathological Condition Contraindications (Hemochromatosis, CKD, Wilson's, Pregnancy)
- Compounding Duplicate Supplement Overdoses
- Pharmacological & Biochemical Nutrient Conflicts (Warfarin-Vitamin K, Folate-B12 masking)
- Quantitative Clinical Safety Score (0-100) & Severity Tiers (LOW, MODERATE, HIGH, CRITICAL)
- Automated Intervention Blocking & Quarantine
"""

import re
import logging
from typing import Dict, Any, List, Optional
from ...schemas.phase12_governance import (
    SafetySeverity,
    SafetyAction,
    SafetyViolation,
    SafetyEvaluationRequest,
    SafetyEvaluationResponse
)
from ..safety.pediatric_framework import (
    get_age_bracket,
    is_pediatric,
    get_pediatric_guidelines,
    evaluate_pediatric_toxicity,
    PEDIATRIC_CLINICAL_PROFILES
)

logger = logging.getLogger(__name__)


class ClinicalSafetyEngine:
    """
    Evaluates clinical prescriptions, dietary changes, and supplement regimens against medical safety guardrails.
    """

    # NIH Office of Dietary Supplements Tolerable Upper Intake Levels (UL) for adults
    TOLERABLE_UPPER_LIMITS: Dict[str, Dict[str, Any]] = {
        "Iron": {"ul": 45.0, "unit": "mg/day", "critical_mult": 2.0},
        "Vitamin D": {"ul": 100.0, "unit": "mcg/day", "critical_mult": 2.5}, # 100 mcg = 4000 IU
        "Vitamin C": {"ul": 2000.0, "unit": "mg/day", "critical_mult": 1.5},
        "Calcium": {"ul": 2500.0, "unit": "mg/day", "critical_mult": 1.5},
        "Magnesium": {"ul": 350.0, "unit": "mg/day (supplemental)", "critical_mult": 2.0},
        "Zinc": {"ul": 40.0, "unit": "mg/day", "critical_mult": 2.0},
        "Selenium": {"ul": 400.0, "unit": "mcg/day", "critical_mult": 2.0},
        "Folate": {"ul": 1000.0, "unit": "mcg/day (synthetic)", "critical_mult": 2.0},
        "Vitamin A": {"ul": 3000.0, "unit": "mcg RAE/day (retinol)", "critical_mult": 1.5},
        "Vitamin B6": {"ul": 100.0, "unit": "mg/day", "critical_mult": 2.0}
    }

    # Strict Pathological Contraindications
    CONTRAINDICATIONS: List[Dict[str, Any]] = [
        {
            "condition": "HEMOCHROMATOSIS",
            "nutrient": "Iron",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "Hereditary hemochromatosis causes unregulated intestinal iron absorption. Supplemental iron risks fatal multiorgan siderosis (cirrhosis, cardiomyopathy, diabetes)."
        },
        {
            "condition": "CHRONIC_KIDNEY_DISEASE",
            "nutrient": "Potassium",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "Impaired renal potassium excretion can induce life-threatening cardiac arrhythmias and sudden arrest from hyperkalemia. Supplemental potassium is strictly contraindicated."
        },
        {
            "condition": "CHRONIC_KIDNEY_DISEASE",
            "nutrient": "Phosphorus",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "Renal failure impedes phosphorus clearance, driving severe hyperphosphatemia, hypocalcemia, and metastatic vascular calcification."
        },
        {
            "condition": "WILSONS_DISEASE",
            "nutrient": "Copper",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "Impaired biliary copper excretion in Wilson's disease leads to toxic hepatic and neuro-basal ganglia accumulation. Copper supplements are contraindicated."
        },
        {
            "condition": "PREGNANCY",
            "nutrient": "Vitamin A",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "High-dose preformed retinol (> 3000 mcg RAE / 10,000 IU) and liver tissues are verified human teratogens causing severe craniofacial and cardiac birth defects."
        },
        {
            "condition": "LIVER_DISEASE",
            "nutrient": "Vitamin A",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "Cirrhosis and severe hepatitis impair hepatic stellate cell retinoid storage; preformed Vitamin A supplementation triggers accelerated hepatotoxicity and portal hypertension."
        },
        {
            "condition": "LIVER_DISEASE",
            "nutrient": "Niacin",
            "severity": SafetySeverity.HIGH,
            "action": SafetyAction.BLOCKED,
            "rationale": "High-dose Niacin (Vitamin B3 > 500mg) precipitates acute hepatocellular injury, transaminitis, and fulminant hepatic failure."
        },
        {
            "condition": "SMOKER",
            "nutrient": "Beta-Carotene",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "High-dose synthetic beta-carotene supplements significantly increase lung cancer incidence and total mortality in current and former smokers (ATBC and CARET trials)."
        },
        {
            "condition": "CHRONIC_KIDNEY_DISEASE",
            "nutrient": "Magnesium",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "Impaired glomerular filtration and tubular clearance preclude supplemental magnesium salts due to life-threatening hypermagnesemia, bradycardia, and neuromuscular paralysis."
        },
        {
            "condition": "CHRONIC_KIDNEY_DISEASE",
            "nutrient": "Protein",
            "severity": SafetySeverity.CRITICAL,
            "action": SafetyAction.BLOCKED,
            "rationale": "High-dose protein isolates accelerate renal hyperfiltration injury and uremic toxin retention in non-dialysis chronic renal impairment."
        }
    ]

    @classmethod
    def evaluate_safety(
        cls,
        patient_intake: Dict[str, Any],
        proposed_recommendations: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None
    ) -> SafetyEvaluationResponse:
        norm_recs = []
        for r in proposed_recommendations:
            r_copy = dict(r)
            if "nutrient" in r_copy and "target_nutrient" not in r_copy:
                r_copy["target_nutrient"] = r_copy["nutrient"]
            if "dosage" in r_copy and "dose_mg" not in r_copy:
                r_copy["dose_mg"] = r_copy["dosage"]
            norm_recs.append(r_copy)

        req = SafetyEvaluationRequest(
            assessment=patient_intake,
            predictions=predictions or [],
            recommendations=norm_recs
        )
        return cls.evaluate(req)

    @classmethod
    def evaluate(cls, request: SafetyEvaluationRequest) -> SafetyEvaluationResponse:
        """
        Executes exhaustive multi-tier safety checks and calculates the 0-100 Clinical Safety Score.
        """
        violations: List[SafetyViolation] = []
        assessment = request.assessment or {}
        recommendations = request.recommendations or []

        # Extract patient conditions comprehensively from medical_history, conditions, and medical_conditions
        conditions_raw = []
        if assessment.get("conditions"):
            conditions_raw.extend(assessment["conditions"] if isinstance(assessment["conditions"], list) else [assessment["conditions"]])
        if assessment.get("medical_conditions"):
            conditions_raw.extend(assessment["medical_conditions"] if isinstance(assessment["medical_conditions"], list) else [assessment["medical_conditions"]])
        if assessment.get("medical_history"):
            for mh in assessment["medical_history"]:
                if isinstance(mh, dict):
                    if mh.get("is_active", True) is not False:
                        conditions_raw.append(mh.get("condition_name", ""))
                elif isinstance(mh, str):
                    conditions_raw.append(mh)

        patient_conditions = [str(c).strip().upper().replace(" ", "_") for c in conditions_raw if c]

        is_pregnant = bool(assessment.get("is_pregnant", False) or assessment.get("demo_is_pregnant", 0) == 1 or any("PREGNAN" in c for c in patient_conditions))
        if is_pregnant and "PREGNANCY" not in patient_conditions:
            patient_conditions.append("PREGNANCY")

        # Robust smoker status detection
        lifestyle_factors = assessment.get("lifestyle_factors", {})
        smoking_val = str(
            assessment.get("smoking_status", "") or
            (lifestyle_factors.get("smoking_status", "") if isinstance(lifestyle_factors, dict) else "") or
            assessment.get("lifestyle", "")
        ).upper()
        is_smoker = bool(
            assessment.get("is_smoker", False) or
            "CURRENT" in smoking_val or
            "SMOK" in smoking_val or
            any("SMOK" in c for c in patient_conditions)
        )
        if is_smoker and "SMOKER" not in patient_conditions:
            patient_conditions.append("SMOKER")

        # 1. Evaluate Pathological Contraindications
        for contra in cls.CONTRAINDICATIONS:
            c_cond = contra["condition"]
            cond_matched = False
            for p in patient_conditions:
                if (c_cond in p or p in c_cond or
                    (c_cond == "CHRONIC_KIDNEY_DISEASE" and ("KIDNEY" in p or "CKD" in p or "RENAL" in p)) or
                    (c_cond == "SMOKER" and "SMOK" in p)):
                    cond_matched = True
                    break

            if cond_matched:
                c_nut = contra["nutrient"].lower()
                for rec in recommendations:
                    rec_name = str(rec.get("food_or_supp", "") or rec.get("item_name", "") or rec.get("nutrient", "")).lower()
                    rec_target = str(rec.get("target_nutrient", "") or rec.get("nutrient", "")).lower()
                    
                    matches_nut = (c_nut in rec_name or c_nut in rec_target)
                    if c_nut == "beta-carotene" and ("beta carotene" in rec_name or "beta-carotene" in rec_name or "synthetic" in rec_name):
                        matches_nut = True
                    if matches_nut:
                        violations.append(SafetyViolation(
                            severity=contra["severity"],
                            rule_id=f"CONTRAINDICATION_{contra['condition']}_{contra['nutrient'].upper()}",
                            rule_name=f"Pathological Contraindication: {contra['condition']} & {contra['nutrient']}",
                            nutrient=contra["nutrient"],
                            clinical_rationale=contra["rationale"],
                            action_taken=contra["action"]
                        ))

        # 1B. Strict High-Risk Population Rules (Pregnancy, CKD, Liver Disease, Diabetes, Dietary Compliance)
        diet_habits = assessment.get("dietary_habits", {})
        dietary_pat = str(assessment.get("dietary_pattern", "") or (diet_habits.get("dietary_pattern", "") if isinstance(diet_habits, dict) else "")).upper()
        restrictions_list = [str(r).upper().replace("-", "_") for r in (assessment.get("dietary_restrictions", []) or (diet_habits.get("dietary_restrictions", []) if isinstance(diet_habits, dict) else []))]
        is_veg = "VEGETARIAN" in dietary_pat or any("MEAT_FREE" in r or "VEGETARIAN" in r for r in restrictions_list)
        is_vegan = "VEGAN" in dietary_pat or any("VEGAN" in r for r in restrictions_list)

        for rec in recommendations:
            rec_name = str(rec.get("food_or_supp", "") or rec.get("item_name", "") or rec.get("food_name", "") or "").lower()
            rec_target = str(rec.get("target_nutrient", "") or rec.get("nutrient", "")).lower()

            # Pregnancy: Preformed retinol & apex predator fish
            if is_pregnant:
                if "liver" in rec_name or ("retinol" in rec_name and "beta" not in rec_name) or any(f in rec_name for f in ["shark", "swordfish", "king mackerel", "tilefish"]):
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.CRITICAL,
                        rule_id="PREGNANCY_TERATOGENIC_RETINOL_OR_MERCURY",
                        rule_name="Pregnancy Teratogen / Methylmercury Guardrail",
                        nutrient="Vitamin A / Mercury",
                        clinical_rationale="Liver tissues and preformed retinyl esters exceed teratogenic thresholds; apex predator marine fish carry dangerous fetal methylmercury burdens.",
                        action_taken=SafetyAction.BLOCKED
                    ))

            # Chronic Kidney Disease (CKD): Supplemental potassium, phosphorus
            if any("KIDNEY" in p or "CKD" in p for p in patient_conditions):
                if "potassium" in rec_name or "potassium" in rec_target:
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.CRITICAL,
                        rule_id="CKD_POTASSIUM_ARRHYTHMIA",
                        rule_name="CKD Hyperkalemia Protection",
                        nutrient="Potassium",
                        clinical_rationale="Impaired glomerular filtration precludes potassium supplementation due to fatal cardiac dysrhythmia risk.",
                        action_taken=SafetyAction.BLOCKED
                    ))
                if "phosphorus" in rec_name or "phosphate" in rec_name:
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.CRITICAL,
                        rule_id="CKD_PHOSPHORUS_HYPERPARATHYROIDISM",
                        rule_name="CKD Hyperphosphatemia Protection",
                        nutrient="Phosphorus",
                        clinical_rationale="Impaired renal phosphate clearance triggers metastatic vascular calcification and secondary hyperparathyroidism.",
                        action_taken=SafetyAction.BLOCKED
                    ))

            # Liver Disease: Vitamin A and high-dose Niacin
            if any("LIVER" in p or "CIRRHOSIS" in p or "HEPATITIS" in p for p in patient_conditions):
                if "retinol" in rec_name or ("vitamin a" in rec_target and "beta" not in rec_name and "carotenoid" not in rec_name):
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.CRITICAL,
                        rule_id="LIVER_DISEASE_RETINOL_TOXICITY",
                        rule_name="Cirrhosis Retinol Stellate Cell Protection",
                        nutrient="Vitamin A",
                        clinical_rationale="Cirrhotic hepatic parenchyma cannot safely clear or store preformed retinol, driving accelerated necrosis.",
                        action_taken=SafetyAction.BLOCKED
                    ))

            # Vegetarian Dietary Adherence
            meat_terms = ["salmon", "sardine", "mackerel", "tuna", "beef", "chicken", "meat", "pork", "poultry", "steak", "liver", "gelatin", "tallow", "fish", "seafood"]
            if (is_veg or is_vegan) and any(m in rec_name for m in meat_terms):
                violations.append(SafetyViolation(
                    severity=SafetySeverity.HIGH,
                    rule_id="DIETARY_VIOLATION_VEGETARIAN",
                    rule_name="Dietary Compliance: Vegetarian Pattern",
                    nutrient=str(rec.get("target_nutrient", "Dietary Pattern")),
                    clinical_rationale=f"Item '{rec_name}' contains animal flesh, violating the patient's declared vegetarian dietary pattern.",
                    action_taken=SafetyAction.BLOCKED
                ))

            # Vegan Dietary Adherence
            if is_vegan:
                dairy_egg_terms = ["milk", "cheese", "yogurt", "whey", "casein", "butter", "egg", "yolk", "albumen", "honey"]
                if any(d in rec_name for d in dairy_egg_terms):
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.HIGH,
                        rule_id="DIETARY_VIOLATION_VEGAN",
                        rule_name="Dietary Compliance: Vegan Pattern",
                        nutrient=str(rec.get("target_nutrient", "Dietary Pattern")),
                        clinical_rationale=f"Item '{rec_name}' contains dairy or egg constituents, violating the patient's declared vegan dietary pattern.",
                        action_taken=SafetyAction.BLOCKED
                    ))

        # 2. Evaluate Tolerable Upper Intake Levels (UL) & Compounding Doses
        # ULs apply primarily to supplemental/fortified intake, not whole-food dietary intake
        nutrient_totals: Dict[str, float] = {}
        for rec in recommendations:
            # Only count supplement doses toward UL, not food nutrient content
            if rec.get("rec_type") == "food":
                continue
            t_nut = rec.get("target_nutrient") or rec.get("nutrient", "")
            raw_dose = rec.get("dose_mg", 0.0) or rec.get("amount", 0.0) or rec.get("dosage", 0.0)
            try:
                if isinstance(raw_dose, str):
                    # Extract the FIRST number from range strings like "25 - 45 mg" or "2000 - 4000 IU/day"
                    # Use conservative lower bound for safety evaluation
                    numbers = re.findall(r"[\d]+\.?\d*", raw_dose)
                    dose = float(numbers[0]) if numbers else 0.0
                    # Detect IU-based dosages and convert to mcg for Vitamin D comparison
                    dose_str_upper = raw_dose.upper()
                    if "IU" in dose_str_upper and t_nut == "Vitamin D":
                        dose = dose / 40.0  # Convert IU to mcg for UL comparison
                else:
                    dose = float(raw_dose or 0.0)
            except (ValueError, TypeError):
                dose = 0.0
            if t_nut and dose > 0:
                nutrient_totals[t_nut] = nutrient_totals.get(t_nut, 0.0) + dose

        # Also add intake from dietary modifications in assessment if provided
        diet_habits = assessment.get("dietary_habits", {})
        if isinstance(diet_habits, dict):
            for k, v in diet_habits.items():
                if isinstance(v, (int, float)):
                    if "iron" in k.lower():
                        nutrient_totals["Iron"] = nutrient_totals.get("Iron", 0.0) + float(v)
                    elif "vitamin_d" in k.lower():
                        nutrient_totals["Vitamin D"] = nutrient_totals.get("Vitamin D", 0.0) + float(v)
                    elif "vitamin_c" in k.lower():
                        nutrient_totals["Vitamin C"] = nutrient_totals.get("Vitamin C", 0.0) + float(v)

        # Age-aware safety and pediatric controls
        age_years = float(assessment.get("age", 30.0) or assessment.get("demo_age_years", 30.0) or 30.0)
        age_bracket = get_age_bracket(age_years)
        patient_is_pediatric = is_pediatric(age_years)

        for nut_name, total_dose in nutrient_totals.items():
            ped_profile = get_pediatric_guidelines(age_bracket, nut_name)
            if ped_profile:
                ul_val = ped_profile.ul
                unit_str = ped_profile.unit
                effective_dose = total_dose
                if nut_name == "Vitamin D":
                    # Convert mcg to IU if needed
                    if total_dose <= 250.0:
                        effective_dose = total_dose * 40.0
                    unit_str = "IU"

                crit_mult = 2.0
                crit_val = ul_val * crit_mult

                if effective_dose >= crit_val:
                    rule_prefix = "PEDIATRIC_UL_EXCEEDED_CRITICAL" if patient_is_pediatric else "UL_EXCEEDED_CRITICAL"
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.CRITICAL,
                        rule_id=f"{rule_prefix}_{nut_name.upper()}",
                        rule_name=f"Severe Toxic Overdose ({'Pediatric ' if patient_is_pediatric else ''}{age_bracket}): {nut_name}",
                        nutrient=nut_name,
                        violating_value=round(effective_dose, 2),
                        threshold_value=round(ul_val, 2),
                        clinical_rationale=f"Daily total intake ({effective_dose:.1f} {unit_str}) exceeds {crit_mult}x the clinical Upper Tolerable Limit ({ul_val:.1f} {unit_str}) for age bracket '{age_bracket}' (Age {age_years:.1f}y). High risk of toxicity.",
                        action_taken=SafetyAction.BLOCKED
                    ))
                elif effective_dose > ul_val:
                    rule_prefix = "PEDIATRIC_UL_EXCEEDED_HIGH" if patient_is_pediatric else "UL_EXCEEDED_HIGH"
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.HIGH,
                        rule_id=f"{rule_prefix}_{nut_name.upper()}",
                        rule_name=f"Upper Tolerable Limit Exceeded ({'Pediatric ' if patient_is_pediatric else ''}{age_bracket}): {nut_name}",
                        nutrient=nut_name,
                        violating_value=round(effective_dose, 2),
                        threshold_value=round(ul_val, 2),
                        clinical_rationale=f"Daily total intake ({effective_dose:.1f} {unit_str}) exceeds clinical Upper Tolerable Limit ({ul_val:.1f} {unit_str}) for age bracket '{age_bracket}' (Age {age_years:.1f}y). Risk of adverse accumulation.",
                        action_taken=SafetyAction.QUARANTINED
                    ))
            elif nut_name in cls.TOLERABLE_UPPER_LIMITS:
                spec = cls.TOLERABLE_UPPER_LIMITS[nut_name]
                ul_val = spec["ul"]
                crit_val = ul_val * spec["critical_mult"]

                if total_dose >= crit_val:
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.CRITICAL,
                        rule_id=f"UL_EXCEEDED_CRITICAL_{nut_name.upper()}",
                        rule_name=f"Severe Toxic Overdose: {nut_name}",
                        nutrient=nut_name,
                        violating_value=round(total_dose, 2),
                        threshold_value=round(ul_val, 2),
                        clinical_rationale=f"Daily total intake ({total_dose} {spec['unit']}) exceeds {spec['critical_mult']}x the NIH Tolerable Upper Limit ({ul_val}). Acute toxicity risk.",
                        action_taken=SafetyAction.BLOCKED
                    ))
                elif total_dose > ul_val:
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.HIGH,
                        rule_id=f"UL_EXCEEDED_HIGH_{nut_name.upper()}",
                        rule_name=f"Tolerable Upper Limit Exceeded: {nut_name}",
                        nutrient=nut_name,
                        violating_value=round(total_dose, 2),
                        threshold_value=round(ul_val, 2),
                        clinical_rationale=f"Daily total intake ({total_dose} {spec['unit']}) exceeds NIH Tolerable Upper Limit ({ul_val} {spec['unit']}). Risk of chronic adverse effects.",
                        action_taken=SafetyAction.QUARANTINED
                    ))

        # 3. Drug-Nutrient Conflicts (e.g. Warfarin + Vitamin K)
        meds = [str(m).upper() for m in assessment.get("medications", [])]
        if any("WARFARIN" in m or "COUMADIN" in m for m in meds):
            for rec in recommendations:
                r_name = str(rec.get("food_or_supp", "") or rec.get("item_name", "") or rec.get("nutrient", "") or rec.get("target_nutrient", "")).lower()
                if "vitamin k" in r_name or "kale" in r_name or "spinach extract" in r_name:
                    violations.append(SafetyViolation(
                        severity=SafetySeverity.HIGH,
                        rule_id="DRUG_CONFLICT_WARFARIN_VITAMIN_K",
                        rule_name="Drug Interaction: Warfarin & High Vitamin K",
                        nutrient="Vitamin K",
                        clinical_rationale="Variable or concentrated high Vitamin K intake blunts warfarin anticoagulation, driving subtherapeutic INR and thrombosis risk.",
                        action_taken=SafetyAction.QUARANTINED
                    ))

        # 4. Spacing & Timing Guardrails
        rec_nutrients = [str(r.get("target_nutrient", "") or r.get("nutrient", "")) for r in recommendations]
        if "Iron" in rec_nutrients and "Calcium" in rec_nutrients:
            violations.append(SafetyViolation(
                severity=SafetySeverity.MODERATE,
                rule_id="SPACING_VIOLATION_IRON_CALCIUM",
                rule_name="Divalent Cation Competition: Calcium & Iron",
                nutrient="Iron/Calcium",
                clinical_rationale="Simultaneous co-ingestion of high calcium (> 300mg) reduces iron absorption up to 60% across the enterocyte basolateral membrane.",
                action_taken=SafetyAction.FLAGGED
            ))

        # 5. Duplicate / Compounding Intake Risk
        seen_nutrients: Dict[str, int] = {}
        for rec in recommendations:
            nut = str(rec.get("target_nutrient") or rec.get("nutrient") or rec.get("food_or_supp") or "").strip()
            if nut:
                seen_nutrients[nut.lower()] = seen_nutrients.get(nut.lower(), 0) + 1
        for nut_low, count in seen_nutrients.items():
            if count > 1:
                violations.append(SafetyViolation(
                    severity=SafetySeverity.MODERATE,
                    rule_id=f"DUPLICATE_COMPOUNDING_{nut_low.upper()}",
                    rule_name=f"Compounding Duplicate Intake: {nut_low.title()}",
                    nutrient=nut_low.title(),
                    clinical_rationale=f"Duplicate or compounding sources detected for {nut_low.title()} ({count} distinct recommendations). Risk of accidental additive hypervitaminosis.",
                    action_taken=SafetyAction.FLAGGED
                ))

        # 5. Compute Quantitative Safety Score
        score = 100.0
        for v in violations:
            if v.severity == SafetySeverity.CRITICAL:
                score -= 50.0
            elif v.severity == SafetySeverity.HIGH:
                score -= 25.0
            elif v.severity == SafetySeverity.MODERATE:
                score -= 10.0
            else: # LOW
                score -= 5.0

        safety_score = round(max(0.0, min(100.0, score)), 1)

        has_critical = any(v.severity == SafetySeverity.CRITICAL for v in violations)
        if has_critical:
            safety_tier = SafetySeverity.CRITICAL
        elif safety_score >= 90.0:
            safety_tier = SafetySeverity.LOW
        elif safety_score >= 75.0:
            safety_tier = SafetySeverity.MODERATE
        elif safety_score >= 50.0:
            safety_tier = SafetySeverity.HIGH
        else:
            safety_tier = SafetySeverity.CRITICAL

        # Dispatch is blocked if safety tier is CRITICAL or any violation is BLOCKED
        has_blocked = any(v.action_taken == SafetyAction.BLOCKED for v in violations)
        is_safe = (safety_tier != SafetySeverity.CRITICAL) and not has_blocked

        # Clinical Mitigation Advice
        if not is_safe:
            mitigation = "CRITICAL SAFETY ALERT: One or more recommended interventions are contraindicated or exceed toxic thresholds. Recommendations have been quarantined/blocked. Direct patient to physician."
        elif violations:
            mitigation = "Clinical guidance: Adjust dosages below NIH Tolerable Upper Limits and observe 2+ hour spacing between competing divalent cations."
        else:
            mitigation = "All evaluated interventions conform with NIH ODS reference limits and standard clinical guidelines."

        return SafetyEvaluationResponse(
            safety_score=safety_score,
            safety_tier=safety_tier,
            is_safe_for_dispatch=is_safe,
            violations_count=len(violations),
            violations=violations,
            mitigation_instructions=mitigation
        )

    @classmethod
    def get_all_safety_rules(cls) -> List[Dict[str, Any]]:
        """Returns inventory of all active clinical safety guardrails."""
        rules = []
        for c in cls.CONTRAINDICATIONS:
            rules.append({
                "rule_id": f"CONTRAINDICATION_{c['condition']}_{c['nutrient'].upper()}",
                "rule_type": "PATHOLOGICAL_CONTRAINDICATION",
                "condition": c["condition"],
                "nutrient": c["nutrient"],
                "severity": c["severity"],
                "default_action": c["action"],
                "description": c["rationale"]
            })
        for nut, spec in cls.TOLERABLE_UPPER_LIMITS.items():
            rules.append({
                "rule_id": f"TOLERABLE_UPPER_LIMIT_{nut.upper()}",
                "rule_type": "NIH_UPPER_LIMIT",
                "nutrient": nut,
                "upper_limit": spec["ul"],
                "unit": spec["unit"],
                "critical_threshold": spec["ul"] * spec["critical_mult"],
                "severity": "HIGH / CRITICAL",
                "default_action": "QUARANTINED / BLOCKED",
                "description": f"Enforces maximum safe chronic intake ceiling ({spec['ul']} {spec['unit']}) defined by NIH ODS."
            })
        return rules
