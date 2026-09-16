"""
NutriScan Adversarial Platform Breaking Test Harness
Simulates extreme edge cases, malformed payloads, security vulnerabilities,
concurrency race conditions, and mock fallbacks across all 11 phases.
"""

import sys
import os
import json
import uuid
import time
import concurrent.futures

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if os.path.dirname(backend_dir) not in sys.path:
    sys.path.insert(0, os.path.dirname(backend_dir))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.persistence import PersistenceRepository
from backend.app.modules.prediction.service import PredictionService
from backend.app.modules.recommendation.service import RecommendationService
from backend.app.modules.copilot.service import ClinicalCopilotService
from backend.app.modules.personalization.meal_planner_pro import IntelligentMealPlanner
from backend.app.modules.personalization.forecasting_engine import ClinicalOutcomeForecaster
from backend.app.modules.reporting.service import ReportingService

client = TestClient(app)

results = []

def record(test_name, status, details):
    results.append({"test": test_name, "status": status, "details": details})
    print(f"[{status}] {test_name}: {details}")

print("=" * 70)
print("RUNNING ADVERSARIAL STRESS TEST & BREAKING HARNESS")
print("=" * 70)

# --- 1. EDGE CASES ---
print("\n--- Phase 6: Edge Case Testing ---")

# Case 1: Age = 0
try:
    res = client.post("/api/v1/predict", json={"age": 0, "gender": "FEMALE", "dietary_pattern": "OMNIVORE"})
    record("Case 1 (Age = 0)", "PASS" if res.status_code == 200 else "FAIL", f"Status {res.status_code}: {res.text[:120]}")
except Exception as e:
    record("Case 1 (Age = 0)", "CRASH", str(e))

# Case 2: Age = 120
try:
    res = client.post("/api/v1/predict", json={"age": 120, "gender": "MALE", "dietary_pattern": "OMNIVORE"})
    record("Case 2 (Age = 120)", "PASS" if res.status_code == 200 else "FAIL", f"Status {res.status_code}: {res.text[:120]}")
except Exception as e:
    record("Case 2 (Age = 120)", "CRASH", str(e))

# Case 3: BMI = 10 (height 200cm, weight 40kg)
try:
    res = client.post("/api/v1/predict", json={"age": 25, "gender": "FEMALE", "height_cm": 200.0, "weight_kg": 40.0, "dietary_pattern": "OMNIVORE"})
    record("Case 3 (BMI = 10)", "PASS" if res.status_code == 200 else "FAIL", f"Status {res.status_code}: {res.text[:120]}")
except Exception as e:
    record("Case 3 (BMI = 10)", "CRASH", str(e))

# Case 4: BMI = 70 (height 150cm, weight 160kg)
try:
    res = client.post("/api/v1/predict", json={"age": 45, "gender": "FEMALE", "height_cm": 150.0, "weight_kg": 160.0, "dietary_pattern": "OMNIVORE"})
    record("Case 4 (BMI = 70)", "PASS" if res.status_code == 200 else "FAIL", f"Status {res.status_code}: {res.text[:120]}")
except Exception as e:
    record("Case 4 (BMI = 70)", "CRASH", str(e))

# Case 5: All biomarkers missing
try:
    res = client.post("/api/v1/predict", json={"age": 30, "gender": "FEMALE", "biomarkers": {}})
    record("Case 5 (Missing Biomarkers)", "PASS" if res.status_code == 200 else "FAIL", f"Status {res.status_code}: {res.text[:120]}")
except Exception as e:
    record("Case 5 (Missing Biomarkers)", "CRASH", str(e))

# Case 6: All biomarkers extremely low (0.0001)
try:
    res = client.post("/api/v1/predict", json={
        "age": 30, "gender": "FEMALE",
        "biomarkers": {"serum_25ohd": 0.0, "serum_ferritin": 0.0, "serum_b12": 0.0, "serum_calcium": 0.0, "rbc_folate": 0.0}
    })
    record("Case 6 (Extremely Low Biomarkers)", "PASS" if res.status_code == 200 else "FAIL", f"Status {res.status_code}: {res.text[:120]}")
except Exception as e:
    record("Case 6 (Extremely Low Biomarkers)", "CRASH", str(e))

# Case 7: All biomarkers extremely high
try:
    res = client.post("/api/v1/predict", json={
        "age": 30, "gender": "FEMALE",
        "biomarkers": {"serum_25ohd": 500.0, "serum_ferritin": 2500.0, "serum_b12": 3000.0, "serum_calcium": 20.0, "rbc_folate": 1500.0}
    })
    record("Case 7 (Extremely High Biomarkers)", "PASS" if res.status_code == 200 else "FAIL", f"Status {res.status_code}: {res.text[:120]}")
except Exception as e:
    record("Case 7 (Extremely High Biomarkers)", "CRASH", str(e))

# Case 8: Pregnant Vegan with CKD
try:
    p_ckd = {
        "age": 32, "gender": "FEMALE",
        "medical_history": ["PREGNANCY", "CHRONIC_KIDNEY_DISEASE_STAGE_4"],
        "dietary_habits": {"dietary_pattern": "VEGAN"},
        "biomarkers": {"serum_25ohd": 14.0, "serum_potassium": 5.9}
    }
    p_res = client.post("/api/v1/predict", json=p_ckd)
    as_id = p_res.json().get("assessment_id")
    rec_res = client.get(f"/api/v1/recommendations?assessment_id={as_id}")
    recs_json = rec_res.json()
    record("Case 8 (Pregnant Vegan with CKD)", "PASS" if rec_res.status_code == 200 else "FAIL", f"Status: {rec_res.status_code}")
except Exception as e:
    record("Case 8 (Pregnant Vegan with CKD)", "CRASH", str(e))

# Case 9: Diabetic Elderly Vegetarian
try:
    p_diab = {
        "age": 78, "gender": "MALE",
        "medical_history": ["TYPE_2_DIABETES_MELLITUS", "HYPERTENSION"],
        "dietary_habits": {"dietary_pattern": "VEGETARIAN"}
    }
    p_res = client.post("/api/v1/predict", json=p_diab)
    as_id = p_res.json().get("assessment_id")
    mp_res = client.post("/api/v1/meal-plans/weekly", json={"assessment_id": as_id, "dietary_pattern": "VEGETARIAN"})
    record("Case 9 (Diabetic Elderly Vegetarian Meal Plan)", "PASS" if mp_res.status_code == 200 else "FAIL", f"Status: {mp_res.status_code}")
except Exception as e:
    record("Case 9 (Diabetic Elderly Vegetarian Meal Plan)", "CRASH", str(e))

# Case 10: Conflicting / Impossible Inputs
try:
    p_bad = {
        "age": -50, "gender": "INVALID_GENDER",
        "height_cm": -180.0, "weight_kg": 0.0,
        "symptoms": {"non_existent_symptom": 9999}
    }
    bad_res = client.post("/api/v1/predict", json=p_bad)
    record("Case 10 (Negative Age/Height & Unknown Gender)", "STATUS_" + str(bad_res.status_code), f"Status: {bad_res.status_code}")
except Exception as e:
    record("Case 10 (Negative Age/Height & Unknown Gender)", "CRASH", str(e))

# --- 2. BACKEND CONCURRENCY & SQLITE LOCKING ---
print("\n--- Phase 4: SQLite Persistence Concurrency Test ---")
def concurrent_worker(i):
    test_id = f"conc-test-{i}-{uuid.uuid4()}"
    PersistenceRepository.save_assessment(test_id, {"age": 20 + i, "gender": "FEMALE"})
    saved = PersistenceRepository.get_assessment(test_id)
    return saved is not None

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(concurrent_worker, i) for i in range(25)]
    concurrent_passes = sum(1 for f in concurrent.futures.as_completed(futures) if f.result())
record("SQLite Concurrency (25 parallel writes/reads across 10 threads)", "PASS" if concurrent_passes == 25 else "FAIL", f"Passed {concurrent_passes}/25")

# --- 3. GET PREDICTION BY ID ENDPOINT TEST ---
print("\n--- Phase 3: Backend API Verification ---")
pred_fetch = client.get("/api/v1/predict/00000000-0000-0000-0000-000000000000")
record("GET /api/v1/predict/{id}", "INSPECT", f"Returned: {pred_fetch.json()}")

# --- 4. EXPLAINABILITY WITH EMPTY CACHE TEST ---
rand_uuid = str(uuid.uuid4())
exp_res = client.get(f"/api/v1/explainability/patient/{rand_uuid}")
record(f"GET /api/v1/explainability/patient/{rand_uuid}", "INSPECT", f"Status: {exp_res.status_code}, Keys: {list(exp_res.json().keys()) if exp_res.status_code == 200 else exp_res.text}")

print("\n" + "=" * 70)
print("ADVERSARIAL SUITE COMPLETED")
print("=" * 70)
