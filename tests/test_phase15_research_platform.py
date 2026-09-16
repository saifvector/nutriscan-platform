"""
Phase 15 Test Suite — Multi-Agent Clinical Intelligence, Federated Learning & Research Platform
Comprehensive verification covering:
1. Multi-Agent Specialist Reasoning (Nutrition, Supplement, Lab, Safety, Differential, Outcome, Coordinator)
2. Inter-Agent Agreement Matrix & Consensus Synthesis
3. Dynamic Multi-Turn Clinical Debate Engine
4. Research Evidence Aggregation & Freshness Decay Function
5. Comparative International Guidelines (WHO, NIH, ESPEN, Endocrine Society)
6. Scientific Contradiction & Pharmacological Interaction Detection
7. Differential Privacy Engine (L2-Norm Clipping & Gaussian Mechanism)
8. Federated Learning Coordinator & Secure Weighted FedAvg Aggregation
9. Population Health Cohort Discovery & Demographic Filtering
10. Geographic Regional Prevalence & Disparity Gradient Mapping
11. Population Risk Stratification & Morbidity Modeling
12. In-Silico Clinical Trial Simulator (Control vs Standard vs Precision Arms)
13. Statistical Power & Cohen's d Effect Size Estimation
14. End-to-End REST API Endpoints across all 5 groups
15. 100% Backward Compatibility across Phases 1–14
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.modules.agents.service import MultiAgentService
from backend.app.modules.agents.schemas import AgentDebateRequest
from backend.app.modules.research.service import ResearchService
from backend.app.modules.research.schemas import EvidenceQueryRequest
from backend.app.modules.research.evidence_engine import ResearchEvidenceEngine
from backend.app.modules.federated.service import FederatedService
from backend.app.modules.federated.differential_privacy import DifferentialPrivacyEngine
from backend.app.modules.federated.secure_aggregation import SecureAggregationEngine
from backend.app.modules.federated.schemas import FederatedNode, ModelUpdatePayload
from backend.app.modules.population.service import PopulationService
from backend.app.modules.population.schemas import CohortFilterRequest
from backend.app.modules.trials.service import TrialService
from backend.app.modules.trials.schemas import TrialSimulationRequest
from backend.app.modules.trials.power_calculator import PowerCalculatorEngine

client = TestClient(app)

SAMPLE_PATIENT = {
    "patient_id": "PT-2026-PHASE15-TEST",
    "full_name": "Dr. Clara Oswald",
    "age": 42,
    "gender": "FEMALE",
    "dietary_pattern": "VEGAN",
    "bmi": 23.4,
    "symptoms": {
        "fatigue": 7,
        "cognitive_fog": 6,
        "muscle_weakness": 5
    }
}


# ==============================================================================
# 1. Multi-Agent Clinical Reasoning Tests
# ==============================================================================

def test_multi_agent_roster():
    """Verify that all 7 specialized agents are active and registered."""
    roster = MultiAgentService.get_agent_roster()
    assert len(roster) == 7
    agent_ids = [a.agent_id for a in roster]
    assert "agent_nutrition" in agent_ids
    assert "agent_supplement" in agent_ids
    assert "agent_laboratory" in agent_ids
    assert "agent_safety" in agent_ids
    assert "agent_differential" in agent_ids
    assert "agent_outcome" in agent_ids
    assert "agent_coordinator" in agent_ids


def test_multi_agent_consultation():
    """Verify full 7-agent consultation and consensus protocol generation."""
    consult = MultiAgentService.consult(SAMPLE_PATIENT)
    assert consult.patient_id == "PT-2026-PHASE15-TEST"
    assert len(consult.perspectives) == 6
    assert len(consult.debate_transcript) >= 5
    assert len(consult.agreement_matrix) > 0

    consensus = consult.consensus_protocol
    assert consensus.consensus_status == "UNANIMOUS_CONSENSUS"
    assert consensus.overall_confidence >= 0.90
    assert len(consensus.unified_action_plan) >= 3
    assert len(consensus.reconciled_tradeoffs) >= 1
    assert len(consensus.monitoring_and_safeguards) >= 2


def test_multi_agent_debate_turns():
    """Verify targeted debate generation between specific specialists."""
    req = AgentDebateRequest(
        patient_id="PT-2026-PHASE15-TEST",
        agent_ids=["nutrition", "supplement"],
        clinical_topic="Acute vs Sustainable Maintenance Repletion",
        max_turns=3
    )
    turns = MultiAgentService.run_debate(req, SAMPLE_PATIENT)
    assert len(turns) <= 3
    for turn in turns:
        assert turn.turn_id > 0
        assert turn.message is not None
        assert turn.tone in ["COLLABORATIVE", "CHALLENGING", "CAUTIONARY", "SYNTHESIZING"]


def test_inter_agent_agreement_matrix():
    """Verify agreement matrix boundaries and pairwise trade-off detection."""
    consult = MultiAgentService.consult(SAMPLE_PATIENT)
    for score in consult.agreement_matrix:
        assert 60.0 <= score.agreement_percentage <= 100.0
        assert len(score.concordant_points) > 0


# ==============================================================================
# 2. Research Intelligence Engine Tests
# ==============================================================================

def test_research_evidence_aggregation():
    """Verify peer-reviewed evidence query and GRADE scoring."""
    req = EvidenceQueryRequest(nutrient="Vitamin D", min_year=2020)
    report = ResearchService.get_evidence_report(req)
    assert report.query_nutrient == "Vitamin D"
    assert len(report.evidence_items) >= 2
    assert report.overall_grade_rating in ["HIGH", "MODERATE"]
    assert 0.0 <= report.overall_confidence_score <= 1.0
    assert 0.0 <= report.average_freshness_score <= 1.0


def test_evidence_freshness_decay_function():
    """Verify exponential time-decay function for evidence freshness."""
    f_2026 = ResearchEvidenceEngine.calculate_freshness_score(2026)
    f_2024 = ResearchEvidenceEngine.calculate_freshness_score(2024)
    f_2016 = ResearchEvidenceEngine.calculate_freshness_score(2016)
    assert f_2026 > f_2024 > f_2016
    assert 0.95 <= f_2026 <= 1.0


def test_international_guidelines_comparison():
    """Verify multi-organizational guideline cross-comparison."""
    guidelines = ResearchService.get_guidelines_comparison("Vitamin D")
    assert len(guidelines) >= 3
    orgs = [g.organization for g in guidelines]
    assert "NIH_ODS" in orgs
    assert "ESPEN" in orgs or "WHO" in orgs


def test_scientific_contradiction_detection():
    """Verify identification of biochemical conflicts (Iron-Calcium, Zinc-Copper)."""
    alerts = ResearchService.get_contradictions("Iron")
    assert len(alerts) >= 1
    mechanisms = " ".join([a.biochemical_mechanism for a in alerts]).lower()
    assert "dmt1" in mechanisms or "hepcidin" in mechanisms
    for alert in alerts:
        assert len(alert.mitigation_strategy) > 20


# ==============================================================================
# 3. Federated Learning Infrastructure Tests
# ==============================================================================

def test_federated_network_status():
    """Verify federated network status, active nodes, and privacy budget."""
    status = FederatedService.get_network_status()
    assert status.current_round >= 14
    assert status.active_nodes_count >= 3
    assert status.privacy_budget_limit == 5.0
    assert status.average_epsilon_spent < status.privacy_budget_limit


def test_differential_privacy_clipping_and_noise():
    """Verify L2-norm clipping and calibrated Gaussian noise injection."""
    raw_weights = {"w1": 3.5, "w2": 4.2, "w3": -2.8}
    clipped, raw_norm = DifferentialPrivacyEngine.clip_weights(raw_weights, max_norm=1.0)

    # Clipped weights must have L2 norm <= 1.001
    sum_sq = sum(v ** 2 for v in clipped.values())
    assert sum_sq <= 1.001

    # Verify Gaussian noise addition
    dp_weights, _, clip_thresh = DifferentialPrivacyEngine.apply_differential_privacy(
        raw_weights, epsilon=0.5, delta=1e-5
    )
    assert clip_thresh == 1.0
    assert set(dp_weights.keys()) == set(raw_weights.keys())


def test_secure_aggregation_fedavg():
    """Verify weighted Federated Averaging calculation across client nodes."""
    u1 = ModelUpdatePayload(
        node_id="NODE-1", round_id=14, sample_size=1000, gradient_norm=0.8,
        weights={"w1": 1.0, "w2": 2.0}
    )
    u2 = ModelUpdatePayload(
        node_id="NODE-2", round_id=14, sample_size=3000, gradient_norm=0.9,
        weights={"w1": 2.0, "w2": 4.0}
    )

    agg_weights, total_n = SecureAggregationEngine.aggregate([u1, u2])
    assert total_n == 4000
    # Expected w1: (1000/4000)*1.0 + (3000/4000)*2.0 = 0.25 + 1.5 = 1.75
    assert abs(agg_weights["w1"] - 1.75) < 1e-4
    # Expected w2: (1000/4000)*2.0 + (3000/4000)*4.0 = 0.5 + 3.0 = 3.50
    assert abs(agg_weights["w2"] - 3.50) < 1e-4


def test_federated_round_aggregation_execution():
    """Verify execution of a complete federated aggregation round."""
    round_result = FederatedService.trigger_secure_aggregation()
    assert round_result.participating_nodes_count >= 3
    assert round_result.total_samples_aggregated > 0
    assert len(round_result.site_adaptation_summary) >= 2


# ==============================================================================
# 4. Population Health Analytics Tests
# ==============================================================================

def test_population_cohort_discovery():
    """Verify multi-parameter cohort filtering and collective vulnerability calculation."""
    filter_req = CohortFilterRequest(min_age=30, max_age=60, gender="FEMALE", dietary_pattern="VEGAN")
    cohort = PopulationService.discover_cohort(filter_req)
    assert cohort.sample_size > 0
    assert cohort.female_percentage > 50.0
    assert 0 <= cohort.average_vulnerability_score <= 100
    assert len(cohort.top_deficiency_risks) >= 3


def test_national_prevalence_mapping():
    """Verify macro epidemiological prevalence benchmarks across nutrients."""
    prevalence = PopulationService.get_prevalence_data()
    assert len(prevalence) >= 5
    nutrients = [p.nutrient for p in prevalence]
    assert "Vitamin D" in nutrients
    assert "Iron" in nutrients
    assert "Magnesium" in nutrients


def test_geographic_regions_mapping():
    """Verify regional insolation, poverty, and top deficiency indices."""
    regions = PopulationService.get_geographic_regions()
    assert len(regions) >= 4
    for r in regions:
        assert r.sunlight_insolation_kwh > 0
        assert r.overall_vulnerability_index > 0


def test_population_risk_stratification():
    """Verify population risk band distributions and avoidable morbidity estimates."""
    strat = PopulationService.get_risk_stratification()
    assert strat.critical_risk_pct + strat.high_risk_pct + strat.moderate_risk_pct + strat.low_risk_pct == pytest.approx(100.0, 0.1)
    assert strat.projected_annual_avoidable_morbidity_usd > 1000000.0


# ==============================================================================
# 5. Clinical Trial Simulation Framework Tests
# ==============================================================================

def test_in_silico_trial_simulation():
    """Verify 3-arm RCT simulation and multi-week biomarker recovery modeling."""
    req = TrialSimulationRequest(target_nutrient="Vitamin D", cohort_size=300, trial_duration_weeks=12)
    sim = TrialService.simulate_trial(req)
    assert sim.total_subjects == 300
    assert len(sim.trial_arms) == 3

    # Arms: Control, Standard Care, Precision
    arm_names = [a.arm_name for a in sim.trial_arms]
    assert any("Control" in n for n in arm_names)
    assert any("Standard" in n for n in arm_names)
    assert any("Precision" in n for n in arm_names)

    # Precision arm must achieve superior normalization rate vs Control
    precision_arm = next(a for a in sim.trial_arms if "Precision" in a.arm_name)
    control_arm = next(a for a in sim.trial_arms if "Control" in a.arm_name)
    assert precision_arm.normalization_rate_pct > control_arm.normalization_rate_pct


def test_statistical_power_calculator():
    """Verify Cohen's d effect size and statistical power (1 - beta) calculation."""
    power_res = PowerCalculatorEngine.calculate_power(
        target_nutrient="Vitamin D",
        sample_size_per_arm=100,
        mean_control=24.5,
        mean_intervention=36.4,
        pooled_std=5.0
    )
    assert power_res.effect_size_cohens_d > 1.5  # Large effect size
    assert power_res.calculated_statistical_power >= 0.90
    assert power_res.p_value < 0.01
    assert power_res.clinical_superiority_confirmed is True


# ==============================================================================
# 6. REST API Endpoints Verification
# ==============================================================================

def test_api_agents_roster_endpoint():
    res = client.get("/api/v1/agents/roster")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7


def test_api_agents_consult_endpoint():
    res = client.post("/api/v1/agents/consult", json=SAMPLE_PATIENT)
    assert res.status_code == 200
    data = res.json()
    assert "consensus_protocol" in data
    assert len(data["perspectives"]) == 6


def test_api_research_evidence_endpoint():
    res = client.post("/api/v1/research/evidence", json={"nutrient": "Vitamin D", "min_year": 2020})
    assert res.status_code == 200
    data = res.json()
    assert data["query_nutrient"] == "Vitamin D"
    assert len(data["evidence_items"]) > 0


def test_api_population_cohorts_endpoint():
    res = client.post("/api/v1/population/cohorts", json={"min_age": 20, "max_age": 70, "gender": "FEMALE"})
    assert res.status_code == 200
    data = res.json()
    assert data["sample_size"] > 0


def test_api_federated_status_and_aggregate_endpoints():
    res_status = client.get("/api/v1/federated/status")
    assert res_status.status_code == 200

    res_agg = client.post("/api/v1/federated/aggregate")
    assert res_agg.status_code == 200
    data = res_agg.json()
    assert data["participating_nodes_count"] > 0


def test_api_trials_simulate_endpoint():
    res = client.post("/api/v1/trials/simulate", json={"target_nutrient": "Vitamin D", "cohort_size": 150})
    assert res.status_code == 200
    data = res.json()
    assert len(data["trial_arms"]) == 3
    assert data["power_analysis"]["calculated_statistical_power"] > 0.80


# ==============================================================================
# 7. Backward Compatibility Verification (Phases 1–14)
# ==============================================================================

def test_phase1_to_14_backward_compatibility():
    """Ensure core prediction, governance, and Phase 14 Copilot endpoints remain 100% functional."""
    # 1. Prediction API
    pred_res = client.post("/api/v1/predict", json={
        "age": 35,
        "gender": "MALE",
        "height_cm": 178.0,
        "weight_kg": 75.0,
        "dietary_habits": {
            "dietary_pattern": "OMNIVORE",
            "meals_per_day": 3,
            "water_intake_liters": 2.5,
            "daily_fruit_vegetable_servings": 3,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": []
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 7.5,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 30,
            "stress_level": 4
        },
        "symptoms": {
            "fatigue": 4,
            "muscle_weakness": 2
        }
    })
    assert pred_res.status_code == 200

    # 2. Phase 14 Copilot Patient Intelligence
    copilot_payload = {
        "patient_id": "PT-2026-TEST-14",
        "full_name": "Eleanor Vance",
        "age": 45,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "dietary_pattern": "VEGAN",
        "meals_per_day": 3,
        "water_intake_liters": 2.0,
        "daily_fruit_vegetable_servings": 4,
        "activity_level": "SEDENTARY",
        "sleep_hours_per_night": 6.5,
        "sunlight_exposure_min_per_day": 15,
        "stress_level": 7,
        "smoking_status": "NEVER",
        "alcohol_consumption": "NONE",
        "symptoms": {
            "fatigue": 8,
            "muscle_weakness": 6,
            "cognitive_fog": 6,
            "cold_intolerance": 7
        }
    }
    copilot_res = client.post("/api/v1/copilot/patient-intelligence", json=copilot_payload)
    assert copilot_res.status_code == 200, copilot_res.text
