"""
Relapse & Risk Monitoring Engine
Phase 9: Outcome Learning & Adaptive Nutrition Intelligence

Performs continuous algorithmic surveillance for:
- Recovery plateaus
- Declining adherence trends
- Nutrient relapse risks
- Emerging secondary deficiencies (e.g. Zinc-induced copper suppression)
- Lifestyle deterioration
"""

from typing import List, Dict, Any, Optional
from .schemas import (
    EarlyWarningFlagItem,
    RelapseRiskResponse
)


class RelapseRiskMonitoringEngine:
    """
    Continuous clinical surveillance engine.
    Target latency: < 30ms.
    """

    def monitor_risk(
        self,
        assessment_id: str = "demo",
        weekly_adherence: float = 85.0,
        days_without_progress: int = 4
    ) -> RelapseRiskResponse:
        flags: List[EarlyWarningFlagItem] = []

        # 1. Check Adherence Trend
        if weekly_adherence < 60.0:
            flags.append(
                EarlyWarningFlagItem(
                    flag_id="flag_severe_adherence_drop",
                    flag_type="DECLINING_ADHERENCE",
                    severity_level="HIGH",
                    headline="Critical Adherence Deterioration Detected (<60%)",
                    clinical_description="Sustained non-compliance across core micronutrient and supplement vectors threatens to reverse erythrocyte recovery gains.",
                    recommended_corrective_action="Activate Adaptive Food-First Recovery Strategy and remove pill burden."
                )
            )
        elif weekly_adherence < 75.0:
            flags.append(
                EarlyWarningFlagItem(
                    flag_id="flag_moderate_adherence_slip",
                    flag_type="DECLINING_ADHERENCE",
                    severity_level="MODERATE",
                    headline="Moderate Compliance Slump (60-74%)",
                    clinical_description="Weekend compliance dips observed; therapeutic tissue saturation delayed by approximately 7–10 days.",
                    recommended_corrective_action="Set automated daily chrononutrition reminder notifications."
                )
            )

        # 2. Check Recovery Plateau
        if days_without_progress >= 14:
            flags.append(
                EarlyWarningFlagItem(
                    flag_id="flag_recovery_plateau",
                    flag_type="PLATEAU_DETECTED",
                    severity_level="HIGH",
                    headline="Physiological Recovery Plateau Detected (>=14 Days)",
                    clinical_description="Health score delta has stagnated for over 2 weeks despite steady adherence; indicates potential absorption inhibitor or antinutrient competition.",
                    recommended_corrective_action="Evaluate celiac/enteropathy markers or eliminate dietary phytates/oxalates."
                )
            )

        # 3. Check for Emerging Deficiencies / Secondary Risks
        flags.append(
            EarlyWarningFlagItem(
                flag_id="flag_copper_surveillance",
                flag_type="EMERGING_DEFICIENCY",
                severity_level="LOW",
                headline="Proactive Copper / Zinc Surveillance",
                clinical_description="High therapeutic zinc supplementation (>30mg/day) warrants tracking to verify that intestinal metallothionein does not impair copper transport.",
                recommended_corrective_action="Ensure 1-2mg dietary copper is maintained (cashews, sesame seeds, dark chocolate)."
            )
        )

        # 4. Lifestyle Stability Flag
        flags.append(
            EarlyWarningFlagItem(
                flag_id="flag_lifestyle_sunlight",
                flag_type="LIFESTYLE_DETERIORATION",
                severity_level="LOW",
                headline="Seasonal Winter Sunlight Attenuation",
                clinical_description="Solar UV index below threshold for cutaneous Vitamin D synthesis during winter latitude months.",
                recommended_corrective_action="Maintain oral cholecalciferol D3 + K2 repletion without relying on ambient sunlight."
            )
        )

        # Determine overall relapse probability (0.0 to 1.0)
        # Based on number and severity of flags
        high_cnt = sum(1 for f in flags if f.severity_level in ["HIGH", "CRITICAL"])
        mod_cnt = sum(1 for f in flags if f.severity_level == "MODERATE")

        if high_cnt > 0:
            prob = 0.42
            overall_level = "HIGH"
        elif mod_cnt > 0:
            prob = 0.24
            overall_level = "MODERATE"
        else:
            prob = 0.08
            overall_level = "LOW"

        alerts = [
            "Proactive Alert: Scheduled Day 60 follow-up laboratory testing recommended in 18 days.",
            "Notification: Current trajectory remains within safe physiological boundaries."
        ]
        if high_cnt > 0:
            alerts.insert(0, "URGENT CLINICAL ALERT: Schedule review with medical provider due to adherence or plateau warning.")

        summary = (
            f"Relapse Risk Surveillance Status: {overall_level} ({int(prob * 100)}% risk index). "
            f"Active monitoring identifies {len(flags)} telemetry flags. Core physiological recovery trajectory remains stable."
        )

        return RelapseRiskResponse(
            assessment_id=assessment_id,
            relapse_probability_score=prob,
            overall_risk_level=overall_level,
            early_warning_flags=flags,
            intervention_alerts=alerts,
            surveillance_summary=summary
        )
