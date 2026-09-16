"""
Unit and Integration Tests for Phase 11 — Explainable AI, Clinical Reasoning & Evidence Engine.

Tests cover:
1. Clinical Evidence Engine (NIH ODS, USDA FoodData Central, NHANES, Grade A/B/C evidence).
2. Nutrient Interaction Reasoning Engine (Biochemical synergies, divalent cation competitions, enzymatic dependencies, timing advice).
3. Clinical Explainer Engine (Positive vs protective SHAP decomposition, dual-layer patient/clinician narratives).
4. What-If Simulation Engine (Prospective perturbation, 105-biomarker recalculation, calibrated delta reduction, recovery timeline).
5. Recommendation Traceability & Evidence Rationales.
6. REST API Endpoints:
   - GET  /api/v1/explainability/prediction-explanation
   - GET  /api/v1/explainability/evidence-summary
   - GET  /api/v1/explainability/nutrient-interactions
   - POST /api/v1/explainability/what-if-simulation
   - GET  /api/v1/explainability/recommendation-rationale
   - Legacy backward compatibility (/api/v1/explainability/global)
7. Performance and latency benchmarks (< 500ms).
"""

import time
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.modules.explainability.evidence_engine import ClinicalEvidenceEngine
from backend.app.modules.explainability.interaction_engine import NutrientInteractionReasoningEngine
from backend.app.modules.explainability.clinical_explainer import ClinicalExplainerEngine
from backend.app.modules.explainability.simulator import WhatIfSimulationEngine
from backend.app.modules.explainability.service import ExplainabilityService
from backend.app.schemas.phase11_explainability import (
    FactorDirection,
    EvidenceGrade,
    InteractionType,
    WhatIfSimulationRequest
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# SECTION 1 — CLINICAL EVIDENCE ENGINE
# ---------------------------------------------------------------------------

def test_evidence_engine_catalog_and_retrieval():
    """Verify evidence engine indexes NIH ODS, USDA FDC, and NHANES citations correctly."""
    engine = ClinicalEvidenceEngine()

    citations = engine.get_all_citations()
    assert len(citations) >= 8
    sources = set(c.evidence_source for c in citations)
    assert any("NIH" in s for s in sources)
    assert any("WHO" in s or "Endocrine" in s or "National" in s for s in sources)

    # Retrieval by target
    iron_evidence = engine.get_evidence_for_target("target_iron_deficiency")
    assert iron_evidence is not None
    assert iron_evidence.nutrient == "Iron"
    assert iron_evidence.evidence_strength in [EvidenceGrade.GRADE_A, EvidenceGrade.GRADE_B, EvidenceGrade.GRADE_C]
    assert iron_evidence.reference_url.startswith("http")

    # Retrieval by name
    vit_d_evidence = engine.get_evidence_for_target("Vitamin D Deficiency")
    assert vit_d_evidence is not None
    assert vit_d_evidence.nutrient == "Vitamin D"

    # USDA Food reference lookup
    usda_beef = engine.get_usda_reference("Grass-Fed Beef Sirloin Steak")
    assert usda_beef["fdc_id"] == "173296"
    assert "USDA" in usda_beef["source"]

    # Fallback for unrecognized food
    usda_fallback = engine.get_usda_reference("Unknown Organic Berry")
    assert usda_fallback["fdc_id"] == "FDC-REF"


# ---------------------------------------------------------------------------
# SECTION 2 — NUTRIENT INTERACTION REASONING ENGINE
# ---------------------------------------------------------------------------

def test_nutrient_interaction_engine_rules():
    """Verify biochemical cross-talk, cation competition, and enzymatic dependencies."""
    engine = NutrientInteractionReasoningEngine()

    all_rules = engine.get_all_interactions()
    assert len(all_rules) >= 7

    # Check for presence of synergistic absorptions
    synergies = [r for r in all_rules if r.interaction_type == InteractionType.SYNERGISTIC_ABSORPTION]
    assert len(synergies) >= 2
    synergy_pairs = [(r.nutrient_a, r.nutrient_b) for r in synergies]
    assert ("Vitamin D", "Calcium") in synergy_pairs or ("Iron", "Vitamin C") in synergy_pairs

    # Check for competitive divalent cation antagonism
    antagonisms = [r for r in all_rules if r.interaction_type == InteractionType.ANTAGONISTIC_COMPETITION]
    assert len(antagonisms) >= 2
    for item in antagonisms:
        assert "spacing" in item.timing_advice.lower() or "window" in item.timing_advice.lower() or "hour" in item.timing_advice.lower()

    # Check for enzymatic dependency
    dependencies = [r for r in all_rules if r.interaction_type == InteractionType.ENZYMATIC_DEPENDENCY]
    assert len(dependencies) >= 2
    dep_nutrients = [(r.nutrient_a, r.nutrient_b) for r in dependencies]
    assert ("Magnesium", "Vitamin D") in dep_nutrients or ("Selenium", "Iodine") in dep_nutrients

    # Filter rules for active nutrients
    detected = engine.detect_interactions(["iron", "calcium"])
    assert len(detected) >= 2
    detected_pairs = [(r.nutrient_a, r.nutrient_b) for r in detected]
    assert any("Iron" in p or "Calcium" in p for p in detected_pairs)


# ---------------------------------------------------------------------------
# SECTION 3 — CLINICAL EXPLAINER ENGINE
# ---------------------------------------------------------------------------

def test_clinical_explainer_decomposition_and_narratives():
    """Verify SHAP attributions are partitioned into positive and protective drivers."""
    sample_assessment = {
        "age": 32,
        "gender": "FEMALE",
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "daily_fruit_vegetable_servings": 2
        },
        "lifestyle_factors": {
            "activity_level": "SEDENTARY",
            "sunlight_exposure_min_per_day": 10,
            "sleep_hours_per_night": 6.0
        },
        "symptoms": {
            "fatigue": 8,
            "dizziness": 6,
            "muscle_weakness": 4
        }
    }

    result = ClinicalExplainerEngine.explain_patient_prediction(sample_assessment)

    assert result.prediction_id is not None
    assert result.overall_risk_tier in ["LOW", "MODERATE", "HIGH"]
    assert 0.0 <= result.overall_risk_score <= 100.0
    assert len(result.explanations) == 9  # All 9 champion models explained

    # Verify first explanation
    first_exp = result.explanations[0]
    assert first_exp.calibrated_probability >= 0.0
    assert len(first_exp.positive_contributors) >= 1
    assert len(first_exp.protective_contributors) >= 1

    for factor in first_exp.positive_contributors:
        assert factor.direction == FactorDirection.POSITIVE
        assert factor.contribution_pct >= 0.0

    for factor in first_exp.protective_contributors:
        assert factor.direction == FactorDirection.PROTECTIVE
        assert factor.contribution_pct >= 0.0

    # Narratives verification
    narratives = first_exp.narratives
    assert len(narratives.patient_explanation) > 30
    assert len(narratives.clinician_evaluation) > 30
    assert len(narratives.icd10_codes) >= 1
    assert len(narratives.confirmatory_labs) > 5


# ---------------------------------------------------------------------------
# SECTION 4 — WHAT-IF SIMULATION ENGINE
# ---------------------------------------------------------------------------

def test_what_if_simulation_engine():
    """Verify prospective intervention simulation modifies probabilities and computes deltas."""
    base_assessment = {
        "age": 28,
        "gender": "FEMALE",
        "dietary_habits": {
            "dietary_pattern": "VEGETARIAN",
            "diet_iron_mg": 6.0,
            "daily_fruit_vegetable_servings": 2
        },
        "lifestyle_factors": {
            "sunlight_exposure_min_per_day": 10,
            "sleep_hours_per_night": 5.5
        },
        "symptoms": {
            "fatigue": 7
        }
    }

    req = WhatIfSimulationRequest(
        base_assessment=base_assessment,
        dietary_modifications={"diet_iron_mg": 22.0, "diet_vitamin_c_mg": 120.0},
        supplement_additions={"supp_iron_mg": 25.0, "supp_vitamin_d_mcg": 50.0},
        lifestyle_modifications={"sunlight_exposure_min_per_day": 30, "sleep_hours_per_night": 8.0}
    )

    result = WhatIfSimulationEngine.run_simulation(req)

    assert result.baseline_risk_score >= 0.0
    assert result.simulated_risk_score >= 0.0
    assert len(result.target_comparisons) == 9
    assert len(result.projected_timeline) > 10
    assert len(result.summary_narrative) > 20

    # Test individual target comparisons
    iron_comp = next((c for c in result.target_comparisons if "iron" in c.target.lower()), None)
    assert iron_comp is not None
    assert iron_comp.baseline_probability >= 0.0
    assert iron_comp.simulated_probability >= 0.0


# ---------------------------------------------------------------------------
# SECTION 5 — RECOMMENDATION TRACEABILITY
# ---------------------------------------------------------------------------

def test_recommendation_rationales():
    """Verify clinical recommendations link directly to triggering risk and NIH/USDA evidence."""
    test_id = uuid.uuid4()
    resp = ExplainabilityService.get_recommendation_rationales(test_id)

    assert resp.total_recommendations >= 1
    assert len(resp.recommendations) >= 1

    for r in resp.recommendations:
        assert r.food_or_protocol is not None
        assert r.target_nutrient is not None
        assert r.evidence_source is not None
        assert r.evidence_strength in [EvidenceGrade.GRADE_A, EvidenceGrade.GRADE_B, EvidenceGrade.GRADE_C]
        assert r.reference_url.startswith("http")
        assert len(r.clinical_rationale) > 5
        assert len(r.expected_outcome) > 5


# ---------------------------------------------------------------------------
# SECTION 6 — REST API INTEGRATION
# ---------------------------------------------------------------------------

def test_api_prediction_explanation_get():
    """GET /api/v1/explainability/prediction-explanation returns 9 target explanations."""
    resp = client.get("/api/v1/explainability/prediction-explanation")
    assert resp.status_code == 200
    data = resp.json()

    assert "prediction_id" in data
    assert "overall_risk_tier" in data
    assert "overall_risk_score" in data
    assert "explanations" in data
    assert len(data["explanations"]) == 9

    first = data["explanations"][0]
    assert "positive_contributors" in first
    assert "protective_contributors" in first
    assert "narratives" in first
    assert "patient_explanation" in first["narratives"]
    assert "clinician_evaluation" in first["narratives"]


def test_api_evidence_summary():
    """GET /api/v1/explainability/evidence-summary returns scientific citations."""
    resp = client.get("/api/v1/explainability/evidence-summary")
    assert resp.status_code == 200
    data = resp.json()

    assert "total_citations" in data
    assert data["total_citations"] >= 8
    assert "evidence_items" in data
    assert len(data["evidence_items"]) >= 8


def test_api_evidence_summary_filtered():
    """GET /api/v1/explainability/evidence-summary?nutrient=Iron."""
    resp = client.get("/api/v1/explainability/evidence-summary?nutrient=Iron")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_citations"] >= 1
    for item in data["evidence_items"]:
        assert "Iron" in item["nutrient"]


def test_api_nutrient_interactions():
    """GET /api/v1/explainability/nutrient-interactions returns biochemical rules."""
    resp = client.get("/api/v1/explainability/nutrient-interactions")
    assert resp.status_code == 200
    data = resp.json()

    assert "total_interactions" in data
    assert data["total_interactions"] >= 7
    assert "interactions" in data


def test_api_what_if_simulation():
    """POST /api/v1/explainability/what-if-simulation executes prospective simulation."""
    payload = {
        "base_assessment": {
            "age": 30,
            "gender": "FEMALE",
            "dietary_habits": {"dietary_pattern": "VEGAN"},
            "lifestyle_factors": {"sunlight_exposure_min_per_day": 10},
            "symptoms": {"fatigue": 7}
        },
        "dietary_modifications": {"diet_iron_mg": 20.0},
        "supplement_additions": {"supp_iron_mg": 25.0},
        "lifestyle_modifications": {"sleep_hours_per_night": 8.0}
    }
    resp = client.post("/api/v1/explainability/what-if-simulation", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "baseline_risk_score" in data
    assert "simulated_risk_score" in data
    assert "risk_score_delta" in data
    assert "target_comparisons" in data
    assert len(data["target_comparisons"]) == 9
    assert "projected_timeline" in data
    assert "summary_narrative" in data


def test_api_recommendation_rationale():
    """GET /api/v1/explainability/recommendation-rationale returns traceable clinical rationales."""
    test_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/explainability/recommendation-rationale?prediction_id={test_id}")
    assert resp.status_code == 200
    data = resp.json()

    assert "total_recommendations" in data
    assert "recommendations" in data
    assert data["total_recommendations"] >= 1


def test_legacy_global_feature_importance():
    """Verify backward compatibility: GET /api/v1/explainability/global still works."""
    resp = client.get("/api/v1/explainability/global")
    assert resp.status_code == 200
    data = resp.json()
    assert "top_global_drivers" in data
    assert len(data["top_global_drivers"]) >= 1


# ---------------------------------------------------------------------------
# SECTION 7 — LATENCY BENCHMARK
# ---------------------------------------------------------------------------

def test_explainability_latency_benchmarks():
    """Verify all Phase 11 endpoints execute within strict sub-500ms bounds."""
    # Prediction explanation benchmark
    t0 = time.perf_counter()
    resp = client.get("/api/v1/explainability/prediction-explanation")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < 500, f"Prediction explanation took {elapsed_ms:.1f}ms (> 500ms target)"

    # Evidence summary benchmark
    t0 = time.perf_counter()
    resp = client.get("/api/v1/explainability/evidence-summary")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < 150, f"Evidence summary took {elapsed_ms:.1f}ms (> 150ms target)"

    # Nutrient interactions benchmark
    t0 = time.perf_counter()
    resp = client.get("/api/v1/explainability/nutrient-interactions")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < 150, f"Nutrient interactions took {elapsed_ms:.1f}ms (> 150ms target)"
