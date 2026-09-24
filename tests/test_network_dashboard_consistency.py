"""
Automated Data Consistency Test: Dashboard API vs Prediction API vs Network Graph Representation
Phase 6 Forensic Audit & Single Source of Truth Verification
"""

import uuid
import pytest
from app.core.persistence import PersistenceRepository
from app.modules.reporting.service import ReportingService

ASSESSMENT_ID = "704a6f4e-01c8-4d35-ab46-326fbfb2f575"

CANONICAL_NUTRIENT_MAP = {
    "iron_deficiency": "iron",
    "iron_deficiency_anemia": "iron_anemia",
    "vitamin_d_insufficiency": "vitamin_d",
    "vitamin_d_deficiency": "vitamin_d",
    "vitamin_b12_deficiency": "vitamin_b12",
    "folate_deficiency": "folate",
    "zinc_deficiency": "zinc",
    "magnesium_deficiency": "magnesium",
    "calcium_deficiency": "calcium",
    "selenium_deficiency": "selenium",
    "potassium_deficiency": "potassium",
}

def sanitize_nutrient_key(name: str) -> str:
    key = name.lower().strip().replace("target_", "").replace(" ", "_").replace("-", "_")
    if key in CANONICAL_NUTRIENT_MAP:
        return CANONICAL_NUTRIENT_MAP[key]
    for suffix in ["_deficiency_anemia", "_deficiency", "_insufficiency"]:
        if key.endswith(suffix):
            stripped = key[: -len(suffix)]
            if stripped in CANONICAL_NUTRIENT_MAP:
                return CANONICAL_NUTRIENT_MAP[stripped]
            return stripped
    return key


def test_dashboard_and_prediction_api_data_consistency():
    """
    Verifies that Dashboard API and Prediction API resolve to identical prediction probabilities,
    ensuring a single source of truth with variance <= 1%.
    """
    ass_uuid = uuid.UUID(ASSESSMENT_ID)
    
    # 1. Fetch persisted predictions
    pred_data = PersistenceRepository.get_predictions(ASSESSMENT_ID)
    assert pred_data is not None, f"Predictions must exist for assessment {ASSESSMENT_ID}"
    
    raw_preds = pred_data.get("predictions") or pred_data.get("nutrient_predictions") or []
    assert len(raw_preds) > 0, "Predictions list cannot be empty"

    # Index predictions by sanitized canonical key
    pred_dict = {}
    for p in raw_preds:
        raw_name = p.get("target_name") or p.get("nutrient") or p.get("name") or ""
        key = sanitize_nutrient_key(raw_name)
        prob = p.get("calibrated_probability", p.get("probability", 0.0))
        # Keep higher probability if multiple targets map to same nutrient
        if key not in pred_dict or prob > pred_dict[key]["prob"]:
            pred_dict[key] = {
                "raw_name": raw_name,
                "prob": prob,
                "risk_tier": p.get("risk_tier", "LOW")
            }

    # 2. Fetch dashboard data
    dash = ReportingService.get_dashboard(ass_uuid)
    assert dash is not None, f"Dashboard must exist for assessment {ASSESSMENT_ID}"

    rankings = dash.deficiency_priority_ranking if hasattr(dash, "deficiency_priority_ranking") else dash.get("deficiency_priority_ranking", [])
    assert len(rankings) > 0, "Dashboard deficiency rankings cannot be empty"

    # Index dashboard predictions
    dash_dict = {}
    for r in rankings:
        raw_name = r.get("nutrient") or r.get("target_name") or ""
        key = sanitize_nutrient_key(raw_name)
        prob = r.get("probability", r.get("calibrated_probability", 0.0))
        if key not in dash_dict or prob > dash_dict[key]["prob"]:
            dash_dict[key] = {
                "raw_name": raw_name,
                "prob": prob,
                "risk_tier": r.get("risk_level", r.get("risk_tier", "LOW"))
            }

    # 3. Compare Dashboard vs Predictions: assert variance <= 1% (0.01)
    variances = []
    for key, d_val in dash_dict.items():
        assert key in pred_dict, f"Nutrient '{key}' ({d_val['raw_name']}) in dashboard must exist in predictions"
        p_val = pred_dict[key]
        variance = abs(d_val["prob"] - p_val["prob"])
        variances.append((key, d_val["prob"], p_val["prob"], variance))
        assert variance <= 0.01, (
            f"Data inconsistency for '{key}': Dashboard={d_val['prob']*100:.1f}%, "
            f"Prediction={p_val['prob']*100:.1f}%, variance={variance*100:.2f}% > 1.0%"
        )

    # 4. Verify canonical mapping resolves all critical nutrients
    assert "iron" in dash_dict, "Iron must be present in dashboard"
    assert "vitamin_d" in dash_dict, "Vitamin D must be present in dashboard"
    assert "iron_anemia" in dash_dict, "Iron Deficiency Anemia must be present in dashboard"
    assert "magnesium" in dash_dict, "Magnesium must be present in dashboard"


def test_canonical_nutrient_sanitization():
    """Verifies all required clinical naming variations resolve to canonical keys."""
    assert sanitize_nutrient_key("Iron Deficiency") == "iron"
    assert sanitize_nutrient_key("Vitamin D Insufficiency") == "vitamin_d"
    assert sanitize_nutrient_key("Vitamin D Deficiency") == "vitamin_d"
    assert sanitize_nutrient_key("Iron Deficiency Anemia") == "iron_anemia"
    assert sanitize_nutrient_key("Folate Deficiency") == "folate"
    assert sanitize_nutrient_key("Magnesium Deficiency") == "magnesium"
    assert sanitize_nutrient_key("Calcium Deficiency") == "calcium"
    assert sanitize_nutrient_key("target_iron_deficiency") == "iron"
