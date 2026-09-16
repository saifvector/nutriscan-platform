"""
Follow-Up Scheduling Engine
Generates severity-gated milestone follow-up schedules:
- 30-day follow-up: Early tolerance, acute compliance, high-risk screening
- 60-day follow-up: Mid-interval laboratory biomarker re-testing
- 90-day follow-up: Long-term outcome validation and maintenance titration
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from .schemas import (
    UnifiedPatientDossier,
    FollowUpSchedulePlan,
    FollowUpMilestone
)


class FollowUpEngine:
    """Generates severity-gated follow-up scheduling protocols."""

    @classmethod
    def schedule_followups(cls, dossier: UnifiedPatientDossier) -> FollowUpSchedulePlan:
        defs = dossier.deficiencies
        critical_defs = [d for d in defs if d.risk_level in ["CRITICAL", "HIGH"]]
        mod_defs = [d for d in defs if d.risk_level == "MODERATE"]

        if critical_defs:
            highest_sev = "CRITICAL" if any(d.risk_level == "CRITICAL" for d in critical_defs) else "HIGH"
        elif mod_defs:
            highest_sev = "MODERATE"
        else:
            highest_sev = "ROUTINE"

        today = datetime.utcnow()
        milestones: List[FollowUpMilestone] = []

        # 30-Day Milestone
        date_30 = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        labs_30 = ["Basic Metabolic Panel (BMP)"] if highest_sev in ["CRITICAL", "HIGH"] else []
        milestones.append(FollowUpMilestone(
            milestone_days=30,
            target_date=date_30,
            severity_tier=highest_sev,
            clinical_objective="Assess gastrointestinal tolerance to supplemental regimens, verify food plan adherence, and screen for early symptom remission.",
            labs_to_retest=labs_30,
            symptom_checkpoints=[
                "Assess fatigue index reduction",
                "Evaluate resolution of muscular cramps/spasms",
                "Inquire regarding dyspepsia or constipation from oral iron"
            ],
            escalation_triggers=[
                "Intolerable GI distress or persistent nausea",
                "Worsening exertional dyspnea or presyncopal episodes"
            ]
        ))

        # 60-Day Milestone (Biomarker Re-testing)
        date_60 = (today + timedelta(days=60)).strftime("%Y-%m-%d")
        labs_60 = ["Serum 25-OH Vitamin D", "Serum Ferritin", "Complete Blood Count (CBC)"]
        if any(d.nutrient == "Vitamin B12" for d in critical_defs + mod_defs):
            labs_60.append("Serum Methylmalonic Acid (MMA)")
        if any(d.nutrient == "Magnesium" for d in critical_defs + mod_defs):
            labs_60.append("RBC Magnesium")

        milestones.append(FollowUpMilestone(
            milestone_days=60,
            target_date=date_60,
            severity_tier=highest_sev,
            clinical_objective="Formal mid-intervention biomarker reassessment. Quantify serum nutrient recovery and verify normalization trajectory.",
            labs_to_retest=labs_60,
            symptom_checkpoints=[
                "Compare 60-day symptom scores against baseline",
                "Audit digital meal logger compliance rate",
                "Review sleep and stress biomarker correlations"
            ],
            escalation_triggers=[
                "Failure of serum ferritin to increase by >= 15 ng/mL despite compliance",
                "Serum 25-OH Vitamin D remaining below 25 ng/mL",
                "Emergence of new neurological numbness or burning paresthesias"
            ]
        ))

        # 90-Day Milestone (Maintenance & Outcome Validation)
        date_90 = (today + timedelta(days=90)).strftime("%Y-%m-%d")
        labs_90 = ["Comprehensive Metabolic Panel (CMP)", "Serum 25-OH Vitamin D", "Serum Ferritin", "Lipid & HbA1c Panel"]
        milestones.append(FollowUpMilestone(
            milestone_days=90,
            target_date=date_90,
            severity_tier=highest_sev,
            clinical_objective="Validate full resolution of deficiency state, titrate therapeutic supplementation down to long-term dietary maintenance, and lock in outcome improvements.",
            labs_to_retest=labs_90,
            symptom_checkpoints=[
                "Confirm sustained absence of primary complaints",
                "Calculate total composite health score delta vs baseline",
                "Establish self-sustaining whole-food dietary routine"
            ],
            escalation_triggers=[
                "Recurrence of symptoms upon dose reduction",
                "Paradoxical elevation in inflammatory or liver enzyme markers"
            ]
        ))

        directive = (
            f"Patient classified under {highest_sev} severity tier. Recommended monitoring encompasses 30-day acute tolerance check, "
            "60-day serum biomarker validation, and 90-day maintenance titration."
        )

        return FollowUpSchedulePlan(
            patient_id=dossier.demographics.patient_id,
            highest_severity=highest_sev,
            milestones=milestones,
            summary_directive=directive
        )
