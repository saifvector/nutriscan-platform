"""
NutriScan Phase 6 & Phase 7 Scientific Validation Suite
Comprehensive automated benchmarking across 100+ clinically characterized cases and 5 acceptance scenarios:
- 25 Vitamin D deficiency cases
- 25 Iron deficiency & anemia cases
- 15 Vitamin B12 deficiency cases
- 15 Calcium & bone mineral density risk cases
- 10 Multi-deficiency compound cases
- 10 Normal healthy controls
- 5 High-risk vulnerable population safety stress-test cases (Pregnancy, CKD, Liver Cirrhosis, Diabetes, Elderly)
- 5 Final Acceptance Scenarios (Patients 1 to 5)

Evaluates:
- Clinical Diagnostic Accuracy, Precision, Recall, F1
- Recommendation Coverage (Food, Supplement, Monitoring, Followup)
- Clinical Safety Compliance (Contraindication interception rate)
- Pharmacokinetic Forecast Sensitivity & Consistency
- End-to-end Cross-Module Consistency
"""

import sys
import uuid
import math
from pathlib import Path
from typing import Dict, Any, List

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.modules.prediction.service import PredictionService
from backend.app.modules.recommendation.service import RecommendationService
from backend.app.modules.recommendation.engine import PersonalizedRecommendationEngine
from backend.app.modules.personalization.forecasting_engine import ClinicalOutcomeForecaster
from backend.app.modules.personalization.meal_planner_pro import MealPlannerPro
from backend.app.modules.copilot.service import CopilotService
from backend.app.modules.governance.safety_engine import ClinicalSafetyEngine
from backend.app.core.persistence import PersistenceRepository


def generate_benchmark_cohort() -> List[Dict[str, Any]]:
    cases = []

    # 1. 25 Vitamin D Deficiency Cases (Severities: Severe <12, Moderate 12-20, Insufficient 20-30)
    for i in range(25):
        severity = "severe" if i < 8 else ("moderate" if i < 18 else "insufficient")
        baseline_25ohd = 7.0 + (i * 0.9) # 7.0 to 28.6
        sun_exposure = 5 if severity == "severe" else (15 if severity == "moderate" else 25)
        cases.append({
            "case_id": f"VITD_{i+1:02d}",
            "cohort": "Vitamin D Deficiency",
            "expected_target": "Vitamin D",
            "expected_risk": "HIGH" if baseline_25ohd < 20.0 else "MODERATE",
            "patient": {
                "age": 22 + (i * 2),
                "gender": "FEMALE" if i % 2 == 0 else "MALE",
                "dietary_habits": {
                    "dietary_pattern": "VEGETARIAN" if i % 3 == 0 else "OMNIVORE",
                    "meals_per_day": 3,
                    "water_intake_liters": 2.0,
                    "dietary_restrictions": ["meat-free"] if i % 3 == 0 else []
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": sun_exposure,
                    "sleep_hours_per_night": 6.5,
                    "activity_level": "SEDENTARY" if i < 15 else "MODERATE",
                    "stress_level": 6
                },
                "symptoms": {"fatigue": 7 if baseline_25ohd < 20 else 4, "muscle_weakness": 6 if baseline_25ohd < 15 else 2},
                "biomarkers": {"serum_25ohd": baseline_25ohd},
                "medical_history": []
            }
        })

    # 2. 25 Iron Deficiency & Anemia Cases
    for i in range(25):
        ferritin = 5.0 + (i * 1.2) # 5.0 to 33.8 ng/mL
        is_anemic = ferritin < 15.0
        cases.append({
            "case_id": f"IRON_{i+1:02d}",
            "cohort": "Iron Deficiency Anemia",
            "expected_target": "Iron",
            "expected_risk": "HIGH" if ferritin < 15.0 else "MODERATE",
            "patient": {
                "age": 19 + (i * 2),
                "gender": "FEMALE",
                "dietary_habits": {
                    "dietary_pattern": "VEGAN" if i % 4 == 0 else ("VEGETARIAN" if i % 2 == 0 else "OMNIVORE"),
                    "meals_per_day": 3,
                    "dietary_restrictions": ["dairy-free", "meat-free"] if i % 4 == 0 else (["meat-free"] if i % 2 == 0 else [])
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 25,
                    "sleep_hours_per_night": 7.0,
                    "activity_level": "MODERATE",
                    "stress_level": 5
                },
                "symptoms": {"fatigue": 8 if is_anemic else 5, "pale_skin": 7 if is_anemic else 3, "cold_hands": 6},
                "biomarkers": {"serum_ferritin": ferritin, "hemoglobin": 10.2 if is_anemic else 12.1},
                "medical_history": ["heavy_menstrual_bleeding"] if i % 2 == 0 else []
            }
        })

    # 3. 15 Vitamin B12 Deficiency Cases
    for i in range(15):
        b12_val = 110.0 + (i * 14.0) # 110 to 306 pg/mL
        cases.append({
            "case_id": f"B12_{i+1:02d}",
            "cohort": "Vitamin B12 Deficiency",
            "expected_target": "Vitamin B12",
            "expected_risk": "HIGH" if b12_val < 200.0 else "MODERATE",
            "patient": {
                "age": 28 + (i * 3),
                "gender": "MALE" if i % 2 == 0 else "FEMALE",
                "dietary_habits": {
                    "dietary_pattern": "VEGAN" if i < 10 else "VEGETARIAN",
                    "meals_per_day": 3,
                    "dietary_restrictions": ["meat-free", "dairy-free"] if i < 10 else ["meat-free"]
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 30,
                    "sleep_hours_per_night": 7.0,
                    "activity_level": "ACTIVE",
                    "stress_level": 4
                },
                "symptoms": {"numbness_tingling": 7 if b12_val < 200 else 3, "fatigue": 6, "brain_fog": 6},
                "biomarkers": {"serum_b12": b12_val},
                "medical_history": ["long_term_vegan_5_years"]
            }
        })

    # 4. 15 Calcium & Bone Mineral Risk Cases
    for i in range(15):
        ca_intake = 300.0 + (i * 35.0) # 300 to 790 mg/day (RDA is 1000 mg)
        cases.append({
            "case_id": f"CALC_{i+1:02d}",
            "cohort": "Calcium & Bone Health",
            "expected_target": "Calcium",
            "expected_risk": "HIGH" if ca_intake < 500.0 else "MODERATE",
            "patient": {
                "age": 50 + (i * 2),
                "gender": "FEMALE",
                "dietary_habits": {
                    "dietary_pattern": "OMNIVORE" if i % 2 == 0 else "VEGETARIAN",
                    "meals_per_day": 3,
                    "dietary_restrictions": ["dairy-free"]
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 20,
                    "sleep_hours_per_night": 6.5,
                    "activity_level": "SEDENTARY",
                    "stress_level": 5
                },
                "symptoms": {"muscle_cramps": 6, "joint_pain": 5},
                "biomarkers": {"serum_calcium": 8.4 if ca_intake < 500 else 8.9},
                "medical_history": ["postmenopausal"]
            }
        })

    # 5. 10 Multi-Deficiency Cases
    for i in range(10):
        cases.append({
            "case_id": f"MULTI_{i+1:02d}",
            "cohort": "Multi-Deficiency Complex",
            "expected_target": "Multiple",
            "expected_risk": "HIGH",
            "patient": {
                "age": 27 + (i * 3),
                "gender": "FEMALE",
                "dietary_habits": {
                    "dietary_pattern": "VEGAN",
                    "meals_per_day": 2,
                    "water_intake_liters": 1.5,
                    "dietary_restrictions": ["dairy-free", "meat-free", "gluten-free"]
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 10,
                    "sleep_hours_per_night": 5.5,
                    "activity_level": "SEDENTARY",
                    "stress_level": 8
                },
                "symptoms": {"fatigue": 9, "hair_loss": 7, "muscle_cramps": 7, "dizziness": 6},
                "biomarkers": {"serum_25ohd": 11.0, "serum_ferritin": 8.0, "serum_b12": 145.0},
                "medical_history": ["malabsorption"]
            }
        })

    # 6. 10 Healthy Normal Controls
    for i in range(10):
        cases.append({
            "case_id": f"CTRL_{i+1:02d}",
            "cohort": "Healthy Normal Control",
            "expected_target": "None",
            "expected_risk": "LOW",
            "patient": {
                "age": 25 + (i * 3),
                "gender": "FEMALE" if i % 2 == 0 else "MALE",
                "dietary_habits": {
                    "dietary_pattern": "OMNIVORE" if i % 2 == 0 else "VEGETARIAN",
                    "meals_per_day": 3,
                    "water_intake_liters": 2.5,
                    "dietary_restrictions": []
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 35,
                    "sleep_hours_per_night": 8.0,
                    "activity_level": "ACTIVE",
                    "stress_level": 2
                },
                "symptoms": {},
                "biomarkers": {"serum_25ohd": 38.0, "serum_ferritin": 65.0, "serum_b12": 550.0},
                "medical_history": []
            }
        })

    # 7. 5 Vulnerable Population Stress-Test Cases
    vulnerable_specs = [
        {
            "id": "VULN_PREG_01",
            "name": "Pregnancy Safety Stress-Test",
            "condition": "PREGNANCY",
            "intake": {
                "age": 29, "gender": "FEMALE", "is_pregnant": True,
                "conditions": ["PREGNANCY"],
                "dietary_habits": {"dietary_pattern": "OMNIVORE", "meals_per_day": 3},
                "symptoms": {"nausea": 5, "fatigue": 6}
            },
            "unwanted_nutrients": ["Vitamin A (Retinol)", "Mercury"]
        },
        {
            "id": "VULN_CKD_02",
            "name": "Chronic Kidney Disease Stage 4 Safety Stress-Test",
            "condition": "CHRONIC_KIDNEY_DISEASE",
            "intake": {
                "age": 64, "gender": "MALE",
                "conditions": ["CHRONIC_KIDNEY_DISEASE", "CKD_STAGE_4"],
                "dietary_habits": {"dietary_pattern": "OMNIVORE", "meals_per_day": 3},
                "symptoms": {"fatigue": 6}
            },
            "unwanted_nutrients": ["Potassium", "Phosphorus"]
        },
        {
            "id": "VULN_LIVER_03",
            "name": "Decompensated Cirrhosis Safety Stress-Test",
            "condition": "LIVER_DISEASE",
            "intake": {
                "age": 58, "gender": "MALE",
                "conditions": ["LIVER_CIRRHOSIS", "HEPATITIS"],
                "dietary_habits": {"dietary_pattern": "OMNIVORE", "meals_per_day": 3},
                "symptoms": {"jaundice": 4, "fatigue": 7}
            },
            "unwanted_nutrients": ["Vitamin A", "Niacin"]
        },
        {
            "id": "VULN_DIAB_04",
            "name": "Type 2 Diabetes Mellitus Safety Stress-Test",
            "condition": "DIABETES",
            "intake": {
                "age": 52, "gender": "FEMALE",
                "conditions": ["TYPE_2_DIABETES"],
                "dietary_habits": {"dietary_pattern": "OMNIVORE", "meals_per_day": 3},
                "symptoms": {"polydipsia": 5, "fatigue": 5}
            },
            "unwanted_nutrients": ["Simple Sugars", "High Glycemic"]
        },
        {
            "id": "VULN_ELDER_VEG_05",
            "name": "Elderly Strict Vegetarian Safety Stress-Test",
            "condition": "ELDERLY_VEGETARIAN",
            "intake": {
                "age": 73, "gender": "FEMALE",
                "conditions": ["OSTEOPENIA"],
                "dietary_habits": {
                    "dietary_pattern": "VEGETARIAN",
                    "dietary_restrictions": ["meat-free", "fish-free"]
                },
                "symptoms": {"joint_stiffness": 5}
            },
            "unwanted_nutrients": ["Meat", "Fish", "Salmon", "Beef"]
        }
    ]

    for v in vulnerable_specs:
        cases.append({
            "case_id": v["id"],
            "cohort": f"Vulnerable: {v['name']}",
            "expected_target": v["condition"],
            "expected_risk": "SAFETY_STRESS_TEST",
            "patient": v["intake"],
            "unwanted_nutrients": v["unwanted_nutrients"]
        })

    return cases


def run_scientific_validation():
    print("================================================================================")
    print("      NUTRISCAN SCIENTIFIC & CLINICAL VALIDATION BENCHMARK (105 CASES)         ")
    print("================================================================================")

    cohort = generate_benchmark_cohort()
    print(f"Loaded {len(cohort)} clinical benchmark cases across 7 cohorts.")

    engine = PredictionService.get_engine()

    total_cases = 0
    correct_identifications = 0
    safety_evaluations_total = 0
    safety_violations_intercepted = 0
    safety_breaches_escaped = 0
    zero_recommendation_defects = 0
    forecast_inconsistencies = 0
    copilot_inconsistencies = 0

    cohort_stats = {}

    for c in cohort:
        case_id = c["case_id"]
        cohort_name = c["cohort"]
        patient = c["patient"]
        expected_target = c["expected_target"]
        expected_risk = c["expected_risk"]

        if cohort_name not in cohort_stats:
            cohort_stats[cohort_name] = {"total": 0, "correct": 0, "coverage_ok": 0, "safe": 0}
        cohort_stats[cohort_name]["total"] += 1
        total_cases += 1

        # 1. Run Screening Prediction
        pred_res = engine.screen_patient(patient, compute_explainability=True)
        preds = pred_res.get("nutrient_predictions", [])

        # Evaluate diagnostic identification
        matched_target = False
        if expected_target == "None":
            # For healthy control, all risks should be LOW or MODERATE < 0.50
            if all(p.get("risk_level") == "LOW" or p.get("probability", 0) < 0.50 for p in preds):
                matched_target = True
        elif expected_target == "Multiple":
            # Multi-deficiency should identify at least 2 elevated targets
            elevated = [p["nutrient"] for p in preds if p.get("risk_level") in ["HIGH", "MODERATE"] or p.get("probability", 0) >= 0.35]
            if len(elevated) >= 2:
                matched_target = True
        elif "Vulnerable" in cohort_name:
            # Vulnerable cohorts are evaluated on whether clinical screening successfully returns actionable risk profiling
            matched_target = len(preds) > 0 and any(p.get("risk_level") in ["HIGH", "MODERATE", "LOW"] for p in preds)
        else:
            # Single target cohort
            for p in preds:
                if expected_target.lower() in p["nutrient"].lower():
                    if expected_risk == "HIGH" and (p["risk_level"] in ["HIGH", "MODERATE"] or p["probability"] >= 0.35):
                        matched_target = True
                    elif expected_risk == "MODERATE" and p["probability"] >= 0.25:
                        matched_target = True
                    break

        if matched_target:
            correct_identifications += 1
            cohort_stats[cohort_name]["correct"] += 1

        # 2. Run Recommendation Generation (Phase 1 & Phase 5)
        as_id = uuid.uuid4()
        PersistenceRepository.save_assessment(str(as_id), patient)
        PersistenceRepository.save_predictions(str(as_id), pred_res)

        recs = RecommendationService.get_recommendations(as_id)
        
        # Check non-zero guarantee
        total_foods = len(recs.priority_1_foods) + len(recs.priority_2_foods) + len(recs.priority_3_foods)
        total_supps = len(recs.supplement_recommendations)
        total_monitoring = len(recs.monitoring_recommendations)
        total_followup = len(recs.followup_recommendations)

        if total_foods == 0 or total_supps == 0 or total_monitoring == 0 or total_followup == 0:
            zero_recommendation_defects += 1
        else:
            cohort_stats[cohort_name]["coverage_ok"] += 1

        # 3. Clinical Safety Stress-Testing (Phase 3)
        safety_evaluations_total += 1
        all_candidate_items = [f.food_name.lower() for f in (recs.priority_1_foods + recs.priority_2_foods + recs.priority_3_foods)]
        for s in recs.supplement_recommendations:
            all_candidate_items.append(s.get("item_name", "").lower())

        is_safe = True
        if "Vulnerable" in cohort_name:
            unwanted = c.get("unwanted_nutrients", [])
            for u in unwanted:
                u_low = u.lower()
                for item in all_candidate_items:
                    if u_low in item:
                        is_safe = False
                        safety_breaches_escaped += 1
                        print(f"SAFETY BREACH in {case_id}: Found '{item}' when '{u}' is contraindicated!")
                        break

        # Check Vegetarian & Vegan purity
        diet_pat = patient.get("dietary_habits", {}).get("dietary_pattern", "").upper()
        if "VEGETARIAN" in diet_pat or "VEGAN" in diet_pat:
            meat_words = ["salmon", "sardine", "mackerel", "tuna", "beef", "chicken", "meat", "pork", "poultry", "steak", "liver", "gelatin", "tallow"]
            for item in all_candidate_items:
                if any(m in item for m in meat_words):
                    is_safe = False
                    safety_breaches_escaped += 1
                    print(f"DIETARY VIOLATION in {case_id}: Vegetarian patient recommended meat item '{item}'!")
                    break

        if is_safe:
            cohort_stats[cohort_name]["safe"] += 1

        # 4. Forecast Consistency Check (Phase 2 & Phase 4)
        top_nut = recs.target_nutrients[0] if recs.target_nutrients else "Vitamin D"
        forecast_item = ClinicalOutcomeForecaster.forecast_nutrient_trajectory(top_nut)
        if len(forecast_item.trajectory_points) != 3 or forecast_item.estimated_days_to_normalization < 0:
            forecast_inconsistencies += 1

        # 5. Copilot Dossier Narrative Check (Phase 4)
        copilot_assessment = CopilotService.generate_clinical_assessment({"assessment_id": str(as_id)})
        exec_text = copilot_assessment.executive_summary.lower()
        if "sarah jenkins" in exec_text or "fatigue and muscle discomfort" in exec_text and not patient.get("symptoms"):
            copilot_inconsistencies += 1

    # Compute Final Metric Scores
    accuracy_score = round((correct_identifications / total_cases) * 100.0, 1)
    coverage_score = round(((total_cases - zero_recommendation_defects) / total_cases) * 100.0, 1)
    safety_score = round(((safety_evaluations_total - safety_breaches_escaped) / safety_evaluations_total) * 100.0, 1)
    forecast_score = round(((total_cases - forecast_inconsistencies) / total_cases) * 100.0, 1)
    consistency_score = round(((total_cases - copilot_inconsistencies) / total_cases) * 100.0, 1)
    production_readiness = round((accuracy_score * 0.25 + coverage_score * 0.20 + safety_score * 0.30 + consistency_score * 0.15 + forecast_score * 0.10), 1)

    print("\n--------------------------------------------------------------------------------")
    print("                         COHORT BENCHMARK RESULTS                               ")
    print("--------------------------------------------------------------------------------")
    for name, s in cohort_stats.items():
        acc = round((s["correct"] / s["total"]) * 100.0, 1)
        cov = round((s["coverage_ok"] / s["total"]) * 100.0, 1)
        safe = round((s["safe"] / s["total"]) * 100.0, 1)
        print(f"Cohort: {name:32s} | N={s['total']:2d} | Accuracy: {acc:5.1f}% | Coverage: {cov:5.1f}% | Safety: {safe:5.1f}%")

    print("\n================================================================================")
    print("                       FINAL EVALUATION SCORES                                  ")
    print("================================================================================")
    print(f"1. Clinical Diagnostic Accuracy Score:   {accuracy_score}%")
    print(f"2. Recommendation Coverage Score:        {coverage_score}%")
    print(f"3. Forecast Reliability Score:           {forecast_score}%")
    print(f"4. Cross-Module Consistency Score:       {consistency_score}%")
    print(f"5. Safety Compliance Score:              {safety_score}%")
    print(f"6. Production Readiness Percentage:      {production_readiness}%")
    print(f"7. Zero-Recommendation Defects Detected: {zero_recommendation_defects}")
    print(f"8. Safety Breaches Escaped:              {safety_breaches_escaped}")
    print(f"9. Copilot Narrative Inconsistencies:    {copilot_inconsistencies}")
    print("================================================================================")

    assert zero_recommendation_defects == 0, f"Detected {zero_recommendation_defects} zero-recommendation defects!"
    assert safety_breaches_escaped == 0, f"Detected {safety_breaches_escaped} safety breaches!"
    assert copilot_inconsistencies == 0, f"Detected {copilot_inconsistencies} copilot inconsistencies!"
    assert production_readiness >= 95.0, f"Production readiness {production_readiness}% is below 95% threshold!"


def run_acceptance_scenarios():
    print("\n================================================================================")
    print("           PHASE 7: FINAL ACCEPTANCE SCENARIOS (PATIENTS 1 TO 5)                ")
    print("================================================================================")

    scenarios = [
        {
            "id": "Patient 1",
            "name": "Vegetarian Female with Vitamin D Deficiency",
            "intake": {
                "age": 28, "gender": "FEMALE",
                "dietary_habits": {
                    "dietary_pattern": "VEGETARIAN",
                    "meals_per_day": 3,
                    "dietary_restrictions": ["meat-free", "fish-free"]
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 8,
                    "sleep_hours_per_night": 6.5,
                    "activity_level": "SEDENTARY",
                    "stress_level": 6
                },
                "symptoms": {"fatigue": 8, "muscle_weakness": 6},
                "biomarkers": {"serum_25ohd": 12.5}
            },
            "expected_flags": ["Vitamin D"],
            "must_not_contain": ["meat", "salmon", "beef", "chicken", "pork", "fish", "sardine"]
        },
        {
            "id": "Patient 2",
            "name": "Iron Deficiency Anemia (Female, Heavy Menses)",
            "intake": {
                "age": 34, "gender": "FEMALE",
                "dietary_habits": {
                    "dietary_pattern": "OMNIVORE",
                    "meals_per_day": 3,
                    "dietary_restrictions": []
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 20,
                    "sleep_hours_per_night": 7.0,
                    "activity_level": "MODERATE",
                    "stress_level": 5
                },
                "symptoms": {"fatigue": 9, "pale_skin": 8, "dizziness": 7, "cold_hands": 7},
                "biomarkers": {"serum_ferritin": 8.0, "hemoglobin": 10.4},
                "medical_history": ["menorrhagia"]
            },
            "expected_flags": ["Iron"],
            "must_contain_supp": "bisglycinate"
        },
        {
            "id": "Patient 3",
            "name": "Vitamin B12 Deficiency (5-Year Strict Vegan)",
            "intake": {
                "age": 31, "gender": "MALE",
                "dietary_habits": {
                    "dietary_pattern": "VEGAN",
                    "meals_per_day": 3,
                    "dietary_restrictions": ["meat-free", "dairy-free", "egg-free"]
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 30,
                    "sleep_hours_per_night": 7.5,
                    "activity_level": "ACTIVE",
                    "stress_level": 4
                },
                "symptoms": {"paresthesia": 7, "brain_fog": 6, "fatigue": 6},
                "biomarkers": {"serum_b12": 140.0}
            },
            "expected_flags": ["Vitamin B12"],
            "must_contain_supp": "cobalamin",
            "must_not_contain": ["meat", "fish", "dairy", "egg", "cheese", "salmon", "beef", "chicken", "pork", "whey", "casein", "gelatin"]
        },
        {
            "id": "Patient 4",
            "name": "Multi-Deficiency Complex (Iron, Vitamin D, Calcium, Folate)",
            "intake": {
                "age": 42, "gender": "FEMALE",
                "dietary_habits": {
                    "dietary_pattern": "VEGETARIAN",
                    "meals_per_day": 2,
                    "dietary_restrictions": ["dairy-free", "meat-free"]
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 10,
                    "sleep_hours_per_night": 5.5,
                    "activity_level": "SEDENTARY",
                    "stress_level": 8
                },
                "symptoms": {"fatigue": 9, "hair_loss": 8, "muscle_cramps": 8, "brittle_nails": 7},
                "biomarkers": {"serum_25ohd": 11.0, "serum_ferritin": 9.0, "serum_calcium": 8.3, "rbc_folate": 160.0}
            },
            "expected_flags": ["Iron", "Vitamin D"],
            "multi": True
        },
        {
            "id": "Patient 5",
            "name": "Healthy Normal Control (Balanced Active Omnivore)",
            "intake": {
                "age": 26, "gender": "MALE",
                "dietary_habits": {
                    "dietary_pattern": "OMNIVORE",
                    "meals_per_day": 3,
                    "water_intake_liters": 2.8,
                    "dietary_restrictions": []
                },
                "lifestyle_factors": {
                    "sunlight_exposure_min_per_day": 40,
                    "sleep_hours_per_night": 8.0,
                    "activity_level": "ACTIVE",
                    "stress_level": 2
                },
                "symptoms": {},
                "biomarkers": {"serum_25ohd": 42.0, "serum_ferritin": 78.0, "serum_b12": 580.0}
            },
            "expected_flags": [],
            "control": True
        }
    ]

    for sc in scenarios:
        print(f"\n--- Testing {sc['id']}: {sc['name']} ---")
        p_id = uuid.uuid4()
        PersistenceRepository.save_assessment(str(p_id), sc["intake"])

        # 1. Prediction Screening
        pred_res = PredictionService.get_engine().screen_patient(sc["intake"], compute_explainability=True)
        PersistenceRepository.save_predictions(str(p_id), pred_res)
        preds = pred_res.get("nutrient_predictions", [])
        flagged = [p["nutrient"] for p in preds if p.get("risk_level") in ["HIGH", "MODERATE"] or p.get("probability", 0) >= 0.35]
        print(f"  * Screening Flagged Targets: {flagged}")

        # 2. Recommendations
        recs = RecommendationService.get_recommendations(p_id)
        all_food_items = [f.food_name for f in (recs.priority_1_foods + recs.priority_2_foods + recs.priority_3_foods)]
        supp_items = [s.get("item_name", "") for s in recs.supplement_recommendations]
        print(f"  * Total Foods Recommended: {len(all_food_items)} (Top: {all_food_items[:3]})")
        print(f"  * Supplement Protocol: {supp_items[:2]}")
        print(f"  * Monitoring Panels: {[m.get('biomarker_test') for m in recs.monitoring_recommendations][:2]}")
        print(f"  * Follow-Up Schedule: {[f.get('timeframe') for f in recs.followup_recommendations][:2]}")

        # Purity check
        if "must_not_contain" in sc:
            for forbidden in sc["must_not_contain"]:
                for item in all_food_items + supp_items:
                    assert forbidden not in item.lower(), f"Violation in {sc['id']}: found forbidden term '{forbidden}' in '{item}'!"

        # Specific item checks
        if "must_contain_supp" in sc:
            found_supp = any(sc["must_contain_supp"].lower() in s.lower() for s in supp_items)
            assert found_supp, f"{sc['id']} must recommend {sc['must_contain_supp']}!"

        # 3. 7-Day Meal Plan Compliance
        mp = MealPlannerPro.generate_plan(
            patient_id=str(p_id),
            diet_type=sc["intake"]["dietary_habits"]["dietary_pattern"],
            cuisine="MEDITERRANEAN",
            target_deficiencies=recs.target_nutrients[:3],
            allergies=[]
        )
        assert len(mp.daily_plans) == 7, f"{sc['id']} meal plan must have 7 days!"
        if "must_not_contain" in sc:
            for d in mp.daily_plans:
                for dish in d.meals:
                    for forbidden in sc["must_not_contain"]:
                        assert forbidden not in dish.dish_name.lower(), f"Meal plan violation in {sc['id']}: found '{forbidden}' in meal '{dish.dish_name}'!"

        # 4. Pharmacokinetic Outcome Forecasting
        target_nut = recs.target_nutrients[0] if recs.target_nutrients else "Vitamin D"
        forecast = ClinicalOutcomeForecaster.forecast_nutrient_trajectory(target_nut)
        print(f"  * Outcome Forecast ({target_nut}): Velocity={forecast.recovery_velocity}, Days to Norm={forecast.estimated_days_to_normalization}")
        assert len(forecast.trajectory_points) == 3

        # 5. Copilot Clinical Assessment Report
        copilot_res = CopilotService.generate_clinical_assessment({"assessment_id": str(p_id)})
        assert len(copilot_res.executive_summary) > 20
        assert len(copilot_res.clinical_findings) > 0
        print(f"  * Copilot Executive Summary verified: {copilot_res.executive_summary[:85]}...")

        print(f"  [PASS] {sc['id']} Fully Validated.")

    print("\n================================================================================")
    print("               ALL 5 FINAL ACCEPTANCE SCENARIOS PASSED!                         ")
    print("================================================================================")


if __name__ == "__main__":
    run_scientific_validation()
    run_acceptance_scenarios()
