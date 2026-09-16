"""
Workflow Orchestration & Database Reconciliation Test
Phase 4: Data Coverage Audit
"""

import sys
import uuid
import sqlite3
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.core.persistence import PersistenceRepository, DB_PATH
from backend.app.core.workflow_orchestrator import ClinicalWorkflowOrchestrator

print("============================================================")
print("PHASE 4: WORKFLOW ORCHESTRATION & DATA COVERAGE RECONCILIATION")
print("============================================================")

# 1. Print current database counts
def get_db_counts():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    tables = ["assessments", "predictions", "recommendations", "meal_plans", "forecasts", "reports"]
    counts = {}
    for t in tables:
        try:
            counts[t] = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except Exception:
            counts[t] = 0
    conn.close()
    return counts

initial_counts = get_db_counts()
print(f"\n[Initial Database Table Counts]")
for t, c in initial_counts.items():
    print(f"  * {t:<16}: {c}")

# 2. Test Single New Patient Full Journey Orchestration
test_id = str(uuid.uuid4())
test_patient = {
    "age": 32,
    "gender": "FEMALE",
    "dietary_habits": {
        "dietary_pattern": "VEGETARIAN",
        "meals_per_day": 3,
        "dietary_restrictions": ["meat-free"]
    },
    "lifestyle_factors": {
        "sunlight_exposure_min_per_day": 10,
        "sleep_hours_per_night": 7.0,
        "activity_level": "MODERATE",
        "stress_level": 5
    },
    "symptoms": {"fatigue": 8, "muscle_weakness": 6},
    "biomarkers": {"serum_25ohd": 12.0, "serum_ferritin": 14.0},
    "medical_history": []
}

print(f"\n[Executing Full Journey for Test Patient: {test_id}]")
journey_result = ClinicalWorkflowOrchestrator.execute_full_journey(
    assessment_id=test_id,
    intake_payload=test_patient,
    force_regenerate=True
)
print(f"  Journey Status: {journey_result['status']}")
print(f"  Artifacts Generated: {journey_result['artifacts_generated']}")

# Verify all artifacts exist in SQLite
assert PersistenceRepository.get_assessment(test_id) is not None, "Assessment missing from DB!"
assert PersistenceRepository.get_predictions(test_id) is not None, "Prediction missing from DB!"
assert PersistenceRepository.get_recommendations(test_id) is not None, "Recommendation missing from DB!"
assert PersistenceRepository.get_meal_plan(test_id) is not None, "Meal Plan missing from DB!"
assert PersistenceRepository.get_forecast(test_id) is not None, "Forecast missing from DB!"
assert PersistenceRepository.get_report(test_id) is not None, "Report missing from DB!"

print("  -> All 6 clinical artifacts successfully verified in SQLite!")

# 3. Run Reconciliation across existing assessments to backfill
print(f"\n[Running Database Reconciliation across existing assessments...]")
reconcile_res = ClinicalWorkflowOrchestrator.reconcile_database_coverage(max_records=20)
print(f"  Scanned: {reconcile_res['scanned_assessments']}")
print(f"  Reconciled: {reconcile_res['reconciled_count']}")
if reconcile_res['errors']:
    print(f"  Errors: {len(reconcile_res['errors'])}")

updated_counts = get_db_counts()
print(f"\n[Updated Database Table Counts]")
for t, c in updated_counts.items():
    delta = c - initial_counts[t]
    print(f"  * {t:<16}: {c} (+{delta})")

assert updated_counts["meal_plans"] > initial_counts["meal_plans"], "Meal plans count did not increase!"
assert updated_counts["forecasts"] > initial_counts["forecasts"], "Forecasts count did not increase!"
assert updated_counts["reports"] > initial_counts["reports"], "Reports count did not increase!"

print("\n============================================================")
print("SUCCESS: PHASE 4 WORKFLOW ORCHESTRATION & COVERAGE PASSED!")
print("============================================================")
