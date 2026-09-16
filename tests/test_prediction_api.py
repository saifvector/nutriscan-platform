"""
API Integration Tests for Multi-Nutrient Prediction Engine (Phase 3)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"


def test_predict_endpoint_latency_and_schema():
    sample_payload = {
        "age": 32,
        "gender": "FEMALE",
        "height_cm": 164.0,
        "weight_kg": 53.0,
        "dietary_habits": {
            "dietary_pattern": "VEGAN",
            "meals_per_day": 2,
            "water_intake_liters": 2.0,
            "daily_fruit_vegetable_servings": 3,
            "junk_food_frequency": "RARELY",
            "dietary_restrictions": ["dairy-free", "meat-free"]
        },
        "lifestyle_factors": {
            "activity_level": "MODERATELY_ACTIVE",
            "sleep_hours_per_night": 6.5,
            "smoking_status": "NEVER",
            "alcohol_consumption": "NONE",
            "sunlight_exposure_min_per_day": 10,
            "stress_level": 7
        },
        "symptoms": {
            "fatigue": 8,
            "pale_skin": 7,
            "hair_loss": 6,
            "brittle_nails": 6,
            "brain_fog": 5
        },
        "medical_history": [],
        "supplement_usage": []
    }

    response = client.post("/api/v1/predict", json=sample_payload)
    assert response.status_code == 200
    data = response.json()

    # Verify overall risk and latency
    assert "overall_risk" in data
    assert data["overall_risk"] in ["LOW", "MODERATE", "HIGH"]
    assert "inference_latency_ms" in data
    assert data["inference_latency_ms"] < 500.0, f"Latency {data['inference_latency_ms']} ms exceeded 500ms limit!"

    # Verify all 18 target nutrients are present
    assert len(data["nutrient_predictions"]) == 18
    
    for item in data["nutrient_predictions"]:
        assert "nutrient" in item
        assert "risk_level" in item
        assert item["risk_level"] in ["LOW", "MODERATE", "HIGH"]
        assert "probability" in item
        assert 0.0 <= item["probability"] <= 1.0
        assert "confidence" in item
        assert 0.0 <= item["confidence"] <= 1.0
        assert "confidence_level" in item
        assert item["confidence_level"] in ["High Confidence", "Medium Confidence", "Low Confidence"]
        assert "priority_rank" in item

    # Verify priority ranking
    assert "priority_ranking" in data
    assert len(data["priority_ranking"]) == 18
    assert data["priority_ranking"][0] == data["nutrient_predictions"][0]["nutrient"]


def test_batch_prediction_endpoint():
    patient_a = {
        "age": 25, "gender": "MALE", "height_cm": 178.0, "weight_kg": 75.0,
        "dietary_pattern": "OMNIVORE", "meals_per_day": 3, "water_intake_liters": 2.5,
        "daily_fruit_vegetable_servings": 4, "food_restrictions": [],
        "activity_level": "MODERATELY_ACTIVE", "sleep_hours_per_night": 7.5,
        "sunlight_exposure_min_per_day": 45, "stress_level": 3,
        "smoking_status": "NEVER", "alcohol_consumption": "NONE",
        "symptoms": {}
    }
    patient_b = {
        "age": 45, "gender": "FEMALE", "height_cm": 160.0, "weight_kg": 78.0,
        "dietary_pattern": "VEGAN", "meals_per_day": 2, "water_intake_liters": 1.5,
        "daily_fruit_vegetable_servings": 2, "food_restrictions": ["meat-free", "dairy-free"],
        "activity_level": "SEDENTARY", "sleep_hours_per_night": 5.5,
        "sunlight_exposure_min_per_day": 10, "stress_level": 8,
        "smoking_status": "CURRENT", "alcohol_consumption": "MODERATE",
        "symptoms": {"fatigue": 9, "hair_loss": 7, "bone_pain": 6}
    }

    batch_payload = {"assessments": [patient_a, patient_b]}
    response = client.post("/api/v1/predict/batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 2
    assert len(data["results"]) == 2
    assert data["batch_latency_ms"] < 1000.0


def test_interaction_rules_endpoint():
    response = client.get("/api/v1/predictions/rules/interactions")
    assert response.status_code == 200
    data = response.json()
    assert data["total_rules"] >= 5
    assert len(data["interaction_catalog"]) >= 5
