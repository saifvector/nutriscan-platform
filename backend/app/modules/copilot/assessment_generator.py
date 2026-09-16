"""
Clinical Assessment Generator
Produces a structured 7-part narrative clinical assessment report:
1. Executive Summary
2. Clinical Findings
3. Deficiency Risk Summary
4. Contributing Factors (dietary gaps, absorption inhibitors, genetics)
5. Recommended Actions (prioritized by urgency)
6. Monitoring Plan (concrete lab targets)
7. Follow-Up Recommendations
"""

from typing import Dict, Any, List
from .schemas import UnifiedPatientDossier, ClinicalAssessmentReport


class AssessmentGenerator:
    """Generates structured 7-part narrative clinical assessment."""

    @classmethod
    def generate_assessment(cls, dossier: UnifiedPatientDossier) -> ClinicalAssessmentReport:
        patient = dossier.demographics
        deficiencies = dossier.deficiencies
        top_deficiencies = [d for d in deficiencies if d.probability >= 0.40]
        if not top_deficiencies and deficiencies:
            top_deficiencies = deficiencies[:3]
        critical_defs = [d for d in deficiencies if d.risk_level in ["CRITICAL", "HIGH"]]

        # 1. Executive Summary
        sym_desc = (
            f"reported symptoms of {', '.join([s.symptom for s in dossier.symptoms if s.severity >= 3][:3])}"
            if any(s.severity >= 3 for s in dossier.symptoms)
            else "presenting without acute symptomatic complaints"
        )
        if critical_defs:
            risk_desc = f"identified elevated clinical deficiency risks for: {', '.join([d.nutrient for d in critical_defs])}"
        elif any(d.risk_level == "MODERATE" for d in deficiencies):
            mod_defs = [d.nutrient for d in deficiencies if d.risk_level == "MODERATE"]
            risk_desc = f"identified moderate nutritional insufficiency indicators for: {', '.join(mod_defs)}"
        else:
            risk_desc = "identified favorable baseline micronutrient sufficiency with no acute high-risk deficiencies"

        exec_summary = (
            f"Patient {patient.full_name}, a {patient.age}-year-old {patient.gender.lower()} presenting with a "
            f"dietary profile of {patient.dietary_pattern.lower()} and {sym_desc}. "
            f"Machine learning screening integrated with biochemical profiling {risk_desc}. "
            f"Overall nutritional vulnerability index is computed at {dossier.composite_risk_score}/100. "
            f"Targeted dietary modulation, bioavailable micronutrient optimization below NIH Upper Tolerable Limits, "
            f"and scheduled surveillance are recommended to sustain metabolic equilibrium."
        )

        # 2. Clinical Findings
        findings = []
        for bio in dossier.biomarkers:
            if bio.status in ["LOW", "BORDERLINE"]:
                findings.append(f"Depleted {bio.marker_name}: {bio.value} {bio.unit} (Reference: {bio.reference_range}, Status: {bio.status}).")
            elif bio.status == "HIGH":
                findings.append(f"Elevated {bio.marker_name}: {bio.value} {bio.unit} (Reference: {bio.reference_range}).")
        
        for sym in dossier.symptoms:
            if sym.severity >= 5:
                findings.append(f"Significant symptomatic burden: {sym.symptom} rated {sym.severity}/10 (duration ~{sym.duration_weeks or 'N/A'} weeks).")

        findings.append(f"Lifestyle biomarker correlates: Sunlight exposure restricted to {patient.sunlight_exposure_min} min/day; average sleep {patient.sleep_hours} hrs/night with perceived stress index {patient.stress_level}/10.")

        # 3. Deficiency Risk Summary
        risk_summary = {
            "critical_risk_count": len([d for d in deficiencies if d.risk_level == "CRITICAL"]),
            "high_risk_count": len([d for d in deficiencies if d.risk_level == "HIGH"]),
            "moderate_risk_count": len([d for d in deficiencies if d.risk_level == "MODERATE"]),
            "low_risk_count": len([d for d in deficiencies if d.risk_level == "LOW"]),
            "primary_targets": [
                {
                    "nutrient": d.nutrient,
                    "probability": d.probability,
                    "risk_level": d.risk_level,
                    "confidence": d.confidence_score,
                    "percentile_rank": d.percentile
                }
                for d in top_deficiencies
            ]
        }

        # 4. Contributing Factors
        is_plant_based = any(t in patient.dietary_pattern.upper() for t in ["VEGAN", "VEGETARIAN"])
        diet_impact = (
            "Excludes or limits key animal-derived micronutrients including bioavailable heme iron, cholecalciferol, and cobalamin; targeted plant-pairing and supplementation essential."
            if is_plant_based
            else "Balanced omnivorous intake; micronutrient density depends on consistent daily consumption of colorful whole vegetables, pulses, and lean proteins."
        )
        contributing_factors = [
            {
                "category": "Dietary Pattern",
                "factor": f"{patient.dietary_pattern.title()} nutritional framework",
                "impact": diet_impact
            },
            {
                "category": "Environmental Exposure",
                "factor": f"Cutaneous sun exposure ({patient.sunlight_exposure_min} min/day)",
                "impact": "Low solar exposure reduces UVB photon flux for dermal 7-dehydrocholesterol conversion to pre-vitamin D3." if patient.sunlight_exposure_min < 20 else "Adequate ambient solar exposure supports cutaneous vitamin D pre-synthesis."
            },
            {
                "category": "Metabolic & Lifestyle Demand",
                "factor": f"Chronic stress rating ({patient.stress_level}/10)",
                "impact": "Sustained cortisol elevation accelerates urinary magnesium excretion and peripheral cellular micronutrient turnover." if patient.stress_level >= 6 else "Moderate stress levels are unlikely to exacerbate acute renal micronutrient wasting."
            }
        ]

        # 5. Recommended Actions (Prioritized)
        recommended_actions = [
            {
                "priority": "Tier 1 - Immediate (Within 48 hours)",
                "action": "Initiate daily targeted supplementation protocol as outlined in the safety-verified care plan.",
                "rationale": "Arrests micro-nutrient depletion and prevents progression to overt clinical deficiency manifestations."
            },
            {
                "priority": "Tier 2 - Dietary Incorporation (Week 1)",
                "action": "Integrate USDA-curated precision food items into regular meal cadence.",
                "rationale": "Supplies whole-food biochemical co-factors (e.g. bioflavonoids, peptides) maximizing micronutrient assimilation."
            },
            {
                "priority": "Tier 3 - Confirmatory Laboratory Orders (Week 2-3)",
                "action": "Order comprehensive serum panel: 25-OH Vitamin D, Ferritin, TIBC, Methylmalonic acid, and Serum Folate.",
                "rationale": "Establishes definitive baseline for objective therapeutic titration and differential diagnosis confirmation."
            }
        ]

        # 6. Monitoring Plan
        monitoring_plan = {
            "biomarker_targets": [
                {"biomarker": "25-OH Vitamin D", "baseline": "Depleted", "target": "40 - 60 ng/mL", "evaluation_window": "60 days"},
                {"biomarker": "Serum Ferritin", "baseline": "Depleted/Borderline", "target": "50 - 100 ng/mL", "evaluation_window": "60-90 days"},
                {"biomarker": "Serum B12", "baseline": "Low/Borderline", "target": "> 450 pg/mL", "evaluation_window": "60 days"}
            ],
            "symptom_tracking_frequency": "Weekly self-reported symptom journal in NutriScan AI portal",
            "adherence_threshold_goal": ">= 85% compliance with food and supplement recommendations"
        }

        # 7. Follow-Up Recommendations
        follow_up_recommendations = [
            "Schedule 30-Day Virtual Nutritional Check-in to review adherence and GI tolerance.",
            "Schedule 60-Day Midpoint Comprehensive Review with repeat serum 25-OH Vitamin D and Ferritin.",
            "Schedule 90-Day Outcome Validation and maintenance tapering assessment.",
            "Instruct patient to seek immediate clinical evaluation if sudden presyncope, severe palpitations, or neurologic tingling occurs."
        ]

        return ClinicalAssessmentReport(
            patient_id=patient.patient_id,
            executive_summary=exec_summary,
            clinical_findings=findings,
            deficiency_risk_summary=risk_summary,
            contributing_factors=contributing_factors,
            recommended_actions=recommended_actions,
            monitoring_plan=monitoring_plan,
            follow_up_recommendations=follow_up_recommendations
        )
