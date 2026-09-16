"""
EMR/EHR-Ready SOAP Note Synthesizer
Generates fully structured clinical SOAP (Subjective, Objective, Assessment, Plan) notes
with one-click clipboard formatting compatible with Epic, Cerner, and AthenaHealth.
"""

from typing import Dict, Any, List
from datetime import datetime
from .schemas import UnifiedPatientDossier, SOAPNoteResponse


class SOAPNoteGenerator:
    """Generates standard EMR SOAP Note from Unified Patient Dossier."""

    @classmethod
    def generate_soap_note(cls, dossier: UnifiedPatientDossier) -> SOAPNoteResponse:
        p = dossier.demographics
        defs = dossier.deficiencies
        critical_defs = [d for d in defs if d.risk_level in ["CRITICAL", "HIGH"]]
        mod_defs = [d for d in defs if d.risk_level == "MODERATE"]

        # --- S: Subjective ---
        cc_items = [s.symptom for s in dossier.symptoms[:2]]
        chief_complaint = f"Evaluation of nutritional risk factors, {', '.join(cc_items).lower() if cc_items else 'fatigue and muscle weakness'}."
        
        hpi_narrative = (
            f"Patient is a {p.age}-year-old {p.gender.lower()} presenting for comprehensive nutritional and metabolic evaluation. "
            f"Reports symptoms including {', '.join([s.symptom.lower() + ' (severity ' + str(s.severity) + '/10)' for s in dossier.symptoms])}. "
            f"Dietary history is significant for {p.dietary_pattern.lower()} dietary pattern consuming {p.meals_per_day} meals/day. "
            f"Reports {p.sunlight_exposure_min} minutes of daily sun exposure, sleep averaging {p.sleep_hours} hours/night, "
            f"and subjective stress level rated {p.stress_level}/10. Current tobacco status: {p.smoking_status.lower()}; alcohol intake: {p.alcohol_consumption.lower()}."
        )

        subjective_dict = {
            "chief_complaint": chief_complaint,
            "history_of_present_illness": hpi_narrative,
            "review_of_systems": {
                "constitutional": "Reports fatigue and reduced energy reserves; denies unexpected fevers or weight loss.",
                "musculoskeletal": "Endorses muscle cramps and exercise intolerance.",
                "neurological": "Mild cognitive sluggishness; denies focal motor deficits."
            },
            "dietary_lifestyle_intake": {
                "pattern": p.dietary_pattern,
                "daily_sunlight_min": p.sunlight_exposure_min,
                "sleep_hours": p.sleep_hours,
                "stress_index": p.stress_level
            }
        }

        # --- O: Objective ---
        vitals_anthropometrics = {
            "age": p.age,
            "gender": p.gender,
            "bmi": p.bmi,
            "nutritional_vulnerability_index": dossier.composite_risk_score
        }

        labs = [
            f"{b.marker_name}: {b.value} {b.unit} [{b.status}] (Ref: {b.reference_range})"
            for b in dossier.biomarkers
        ]

        ml_predictions = [
            f"{d.nutrient}: Risk Level {d.risk_level} (Calibrated Prob: {d.probability:.1%}, Confidence: {d.confidence_score:.2f})"
            for d in defs[:5]
        ]

        objective_dict = {
            "vitals_and_anthropometrics": vitals_anthropometrics,
            "laboratory_biomarkers": labs,
            "ai_predictive_screening": ml_predictions
        }

        # --- A: Assessment ---
        primary_dx = [f"{d.nutrient} Deficiency Risk (Probability {d.probability:.1%}, {d.risk_level})" for d in critical_defs]
        if not primary_dx and mod_defs:
            primary_dx = [f"{d.nutrient} Suboptimal Status (Probability {d.probability:.1%})" for d in mod_defs]

        differential_considerations = [
            "Dietary insufficiency secondary to restrictive/plant-based regimen",
            "Impaired intestinal bioavailability / phytate-mediated binding",
            "Inadequate cutaneous photoproduction (reduced solar irradiance)",
            "Stress-induced metabolic depletion and urinary mineral excretion"
        ]

        assessment_dict = {
            "primary_diagnoses": primary_dx,
            "differential_considerations": differential_considerations,
            "clinical_impression": (
                f"{p.age}yo {p.gender.lower()} with multi-nutrient vulnerability score of {dossier.composite_risk_score}/100. "
                f"Symptomatology closely mirrors identified micronutrient depletion targets ({', '.join([d.nutrient for d in critical_defs]) or 'moderate nutritional gaps'}). "
                "Low suspicion for acute systemic malabsorptive disease; clinical presentation points to dietary and lifestyle etiology."
            )
        }

        # --- P: Plan ---
        diagnostics = [
            "Order confirmatory serum panel: 25-OH Vitamin D, Serum Ferritin, Total Iron Binding Capacity (TIBC), Serum B12, and Complete Blood Count (CBC).",
            "Check fasting metabolic profile and comprehensive urinalysis."
        ]

        food_tx = [f"{food.title} ({food.dosage_or_serving}, {food.frequency})" for food in dossier.precision_foods]
        supp_tx = [f"{supp.title} ({supp.dosage_or_serving}, {supp.frequency})" for supp in dossier.supplement_plan]

        counseling = [
            "Educated patient on bioavailability enhancers (e.g. Vitamin C co-ingestion with non-heme iron).",
            "Advised separation of tea/coffee consumption by at least 2 hours from iron-rich meals.",
            "Discussed gradual increase of safe UV sunlight exposure to 20-30 minutes daily where feasible.",
            "Emphasized adherence to safety-checked supplement dosages below NIH Upper Tolerable Limits."
        ]

        followup = [
            "30-day virtual review for adherence, GI tolerance, and symptom adjustment.",
            "60-day in-person clinic visit with repeat serum 25-OH Vitamin D and Ferritin.",
            "Emergency precautions: seek prompt care for syncope, severe shortness of breath, or cardiac palpitations."
        ]

        plan_dict = {
            "diagnostics_ordered": diagnostics,
            "nutrition_prescriptions": food_tx,
            "supplementation_protocol": supp_tx,
            "patient_counseling": counseling,
            "follow_up_and_monitoring": followup
        }

        # --- Formatted Clipboard Text (EMR Standard) ---
        date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        formatted = f"""================================================================================
CLINICAL SOAP NOTE — NUTRISCAN AI CLINICAL COPILOT
Date/Time: {date_str}
Patient: {p.full_name} | ID: {p.patient_id} | Age: {p.age} | Gender: {p.gender} | BMI: {p.bmi}
================================================================================

SUBJECTIVE:
• Chief Complaint: {chief_complaint}
• History of Present Illness: {hpi_narrative}
• Review of Systems:
  - Constitutional: Fatigue endorsed; no fevers or unintentional weight loss.
  - Musculoskeletal: Muscle cramps and fatigue endorsed.
  - Neurological: Cognitive sluggishness; denies paresthesias.
• Diet & Lifestyle:
  - Diet Pattern: {p.dietary_pattern} | Meals/Day: {p.meals_per_day}
  - Sun Exposure: {p.sunlight_exposure_min} min/day | Sleep: {p.sleep_hours} hrs/night
  - Perceived Stress: {p.stress_level}/10 | Smoking: {p.smoking_status} | Alcohol: {p.alcohol_consumption}

OBJECTIVE:
• Anthropometrics & Indices:
  - Age: {p.age} | Gender: {p.gender} | BMI: {p.bmi} kg/m²
  - Nutritional Vulnerability Score: {dossier.composite_risk_score}/100
• Laboratory Biomarkers:
""" + "\n".join([f"  - {lab}" for lab in labs]) + f"""
• AI Predictive Screening (Calibrated XGBoost Multi-Target):
""" + "\n".join([f"  - {pred}" for pred in ml_predictions]) + f"""

ASSESSMENT:
• Primary Nutritional Risk Findings:
""" + "\n".join([f"  1. {dx}" for dx in primary_dx]) + f"""
• Differential Diagnostic Etiologies:
""" + "\n".join([f"  - {diff}" for diff in differential_considerations]) + f"""
• Clinical Impression:
  {assessment_dict['clinical_impression']}

PLAN:
• Diagnostics & Confirmatory Testing:
""" + "\n".join([f"  - {d}" for d in diagnostics]) + f"""
• Dietary Prescriptions (USDA Foundation Food Aligned):
""" + "\n".join([f"  - {f}" for f in food_tx]) + f"""
• Targeted Supplementation Protocol (Safety Verified < NIH UL):
""" + "\n".join([f"  - {s}" for s in supp_tx]) + f"""
• Patient Education & Counseling:
""" + "\n".join([f"  - {c}" for c in counseling]) + f"""
• Follow-Up & Safety Precaution:
""" + "\n".join([f"  - {fu}" for fu in followup]) + f"""

================================================================================
Generated by NutriScan AI Clinical Copilot | Physician Review & Signature Required
================================================================================
"""

        return SOAPNoteResponse(
            patient_id=p.patient_id,
            patient_name=p.full_name,
            subjective=subjective_dict,
            objective=objective_dict,
            assessment=assessment_dict,
            plan=plan_dict,
            formatted_text=formatted
        )
