"""
Phase 11: What-If Clinical Simulation Engine
Enables prospective clinical scenario testing:
- Perturbs baseline patient intake inputs (dietary intake, supplemental additions, lifestyle habits)
- Dynamically recomputes the 105-dimensional NHANES feature space through ClinicalFeaturePreprocessor
- Re-executes the 9 calibrated champion models through ClinicalRiskEngine
- Calculates delta probability reductions, risk score improvements, and tier transitions
- Synthesizes personalized recovery timelines and clinical guidance
"""

import copy
import logging
from typing import Dict, Any, List, Optional
import numpy as np

from ...schemas.phase11_explainability import (
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
    TargetSimulationComparison
)
from ..prediction.service import PredictionService
from ..prediction.registry import TARGET_DISPLAY_NAMES

logger = logging.getLogger(__name__)


class WhatIfSimulationEngine:
    """
    High-throughput What-If clinical simulation engine for prospective risk trajectory modeling.
    """

    @classmethod
    def run_simulation(cls, request: WhatIfSimulationRequest) -> WhatIfSimulationResponse:
        """
        Executes baseline vs simulated risk modeling and returns granular comparison metrics.
        Target execution latency: < 350 ms.
        """
        clinical_engine = PredictionService.get_clinical_engine()

        # Step 1: Baseline prediction
        baseline_resp = clinical_engine.predict_patient(request.base_assessment)

        # Step 2: Construct modified simulation payload
        sim_payload = copy.deepcopy(request.base_assessment)

        # Apply dietary modifications
        if request.dietary_modifications:
            diet_habits = sim_payload.setdefault("dietary_habits", {})
            for k, v in request.dietary_modifications.items():
                if isinstance(diet_habits, dict):
                    diet_habits[k] = v
                sim_payload[k] = v

        # Apply supplement additions
        if request.supplement_additions:
            supp_usage = sim_payload.setdefault("supplement_usage", [])
            for supp_name, amount in request.supplement_additions.items():
                # Update top-level supp field for NHANES preprocessor
                sim_payload[supp_name] = amount
                if isinstance(supp_usage, list):
                    supp_usage.append({"supplement_type": supp_name, "daily_dose": str(amount), "adherence": "ALWAYS"})

        # Apply lifestyle modifications
        if request.lifestyle_modifications:
            lifestyle = sim_payload.setdefault("lifestyle_factors", {})
            for k, v in request.lifestyle_modifications.items():
                if isinstance(lifestyle, dict):
                    lifestyle[k] = v
                sim_payload[k] = v

        # Step 3: Run simulated prediction
        simulated_resp = clinical_engine.predict_patient(sim_payload)

        # Step 4: Compute per-target comparisons
        base_map = {p.target: p for p in baseline_resp.predictions}
        sim_map = {p.target: p for p in simulated_resp.predictions}

        tier_severity = {"HIGH": 3, "MODERATE": 2, "LOW": 1}
        target_comparisons: List[TargetSimulationComparison] = []
        resolved_count = 0

        for target, base_p in base_map.items():
            sim_p = sim_map.get(target, base_p)
            prob_delta = round(sim_p.calibrated_probability - base_p.calibrated_probability, 4)
            
            b_tier = base_p.risk_tier.value
            s_tier = sim_p.risk_tier.value
            improved = tier_severity.get(s_tier, 1) < tier_severity.get(b_tier, 1) or prob_delta < -0.05

            if b_tier in ["HIGH", "MODERATE"] and s_tier == "LOW":
                resolved_count += 1

            disp_name = TARGET_DISPLAY_NAMES.get(target, target)
            target_comparisons.append(TargetSimulationComparison(
                target=target,
                target_name=disp_name,
                baseline_probability=base_p.calibrated_probability,
                simulated_probability=sim_p.calibrated_probability,
                probability_delta=prob_delta,
                baseline_tier=b_tier,
                simulated_tier=s_tier,
                tier_improved=improved
            ))

        # Order comparisons by greatest risk reduction first
        target_comparisons.sort(key=lambda x: x.probability_delta)

        # Step 5: Composite risk improvement calculation
        score_delta = round(simulated_resp.overall_risk_score - baseline_resp.overall_risk_score, 1)

        # Formulate clinical timeline and narrative
        if score_delta <= -20.0 or resolved_count >= 2:
            timeline = "4 to 6 weeks of consistent adherence"
            narrative = (
                f"Simulated intervention yields substantial risk reduction of {abs(score_delta)} points. "
                f"{resolved_count} deficiency risk{'s were' if resolved_count > 1 else ' was'} projected to normalize to LOW risk. "
                "Adhering to these dietary and supplement adjustments provides strong biological repletion."
            )
        elif score_delta < 0:
            timeline = "6 to 8 weeks with regular dietary maintenance"
            narrative = (
                f"Simulated adjustments provide favorable trajectory improvement (-{abs(score_delta)} composite risk points). "
                "Continued adherence is recommended to sustain cellular nutrient levels."
            )
        else:
            timeline = "8 to 12 weeks of structured clinical intervention"
            narrative = "Minor risk modulation observed. Consider increasing targeted bioavailable food density or reviewing supplement dosages."

        return WhatIfSimulationResponse(
            baseline_risk_score=baseline_resp.overall_risk_score,
            simulated_risk_score=simulated_resp.overall_risk_score,
            risk_score_delta=score_delta,
            deficiencies_resolved_count=resolved_count,
            target_comparisons=target_comparisons,
            projected_timeline=timeline,
            summary_narrative=narrative
        )
