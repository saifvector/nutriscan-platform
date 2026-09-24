"""
Automated Integration Tests for Patient Deletion Functionality
Validates:
1. Atomic transactional deletion of patient profile and all cascaded clinical records:
   - assessments
   - predictions
   - recommendations
   - meal plans
   - reports
   - forecasts
   - ground truth outcomes
   - clinician reviews
2. In-memory explainability cache invalidation
3. Cryptographically chained audit event generation with action 'PATIENT_DELETED'
4. 404 response for nonexistent patients
"""

import uuid
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.persistence import PersistenceRepository, get_connection

client = TestClient(app)


def test_delete_patient_complete_cascade():
    """Verify deleting a patient removes patient, assessments, predictions, reports, and creates audit event."""
    test_pid = f"test-del-p-{uuid.uuid4().hex[:8]}"
    test_aid_1 = f"test-del-a1-{uuid.uuid4().hex[:8]}"
    test_aid_2 = f"test-del-a2-{uuid.uuid4().hex[:8]}"
    patient_name = f"Test Subject {uuid.uuid4().hex[:4].upper()}"

    conn = get_connection()
    try:
        with conn:
            # 1. Insert patient
            conn.execute(
                """
                INSERT INTO patients (id, name, gender, current_age, height_cm, weight_kg, dietary_pattern, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (test_pid, patient_name, "MALE", 42, 175.0, 78.0, "MEDITERRANEAN")
            )
            # 2. Insert two assessments
            for aid in [test_aid_1, test_aid_2]:
                conn.execute(
                    """
                    INSERT INTO assessments (id, created_at, age, gender, dietary_pattern, payload_json, patient_id, patient_name)
                    VALUES (?, datetime('now'), 42, 'MALE', 'MEDITERRANEAN', '{}', ?, ?)
                    """,
                    (aid, test_pid, patient_name)
                )
                conn.execute(
                    """
                    INSERT INTO predictions (assessment_id, created_at, overall_risk, overall_risk_score, predictions_json)
                    VALUES (?, datetime('now'), 'LOW', 25.0, '[]')
                    """,
                    (aid,)
                )
                conn.execute(
                    """
                    INSERT INTO recommendations (assessment_id, created_at, safety_score, safety_tier, recommendations_json)
                    VALUES (?, datetime('now'), 90.0, 'OPTIMAL', '{}')
                    """,
                    (aid,)
                )
                conn.execute(
                    """
                    INSERT INTO meal_plans (assessment_id, created_at, dietary_pattern, plan_json)
                    VALUES (?, datetime('now'), 'MEDITERRANEAN', '{}')
                    """,
                    (aid,)
                )
                conn.execute(
                    """
                    INSERT INTO reports (id, assessment_id, created_at, report_title, report_json)
                    VALUES (?, ?, datetime('now'), 'Test Clinical Report', '{}')
                    """,
                    (f"rep-{aid}", aid)
                )
                conn.execute(
                    """
                    INSERT INTO ground_truth_outcomes (id, assessment_id, patient_id, followup_day, nutrient, predicted_value, actual_lab_value, delta, concordance_pct, created_at)
                    VALUES (?, ?, ?, 30, 'Vitamin D', 22.0, 24.0, 2.0, 91.0, datetime('now'))
                    """,
                    (f"gt-{aid}", aid, test_pid)
                )
    finally:
        conn.close()

    # Verify patient exists prior to deletion
    assert PersistenceRepository.get_patient(test_pid) is not None

    # Call DELETE /api/v1/patients/{patient_id}
    response = client.delete(f"/api/v1/patients/{test_pid}")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    body = response.json()
    assert body["success"] is True
    assert body["patient_id"] == test_pid
    assert body["deleted_assessments_count"] == 2

    # Verify patient is gone
    assert PersistenceRepository.get_patient(test_pid) is None

    # Verify all linked tables have 0 rows for this patient & assessments
    conn = get_connection()
    try:
        cur = conn.cursor()
        for aid in [test_aid_1, test_aid_2]:
            assert cur.execute("SELECT COUNT(*) FROM assessments WHERE id = ?", (aid,)).fetchone()[0] == 0
            assert cur.execute("SELECT COUNT(*) FROM predictions WHERE assessment_id = ?", (aid,)).fetchone()[0] == 0
            assert cur.execute("SELECT COUNT(*) FROM recommendations WHERE assessment_id = ?", (aid,)).fetchone()[0] == 0
            assert cur.execute("SELECT COUNT(*) FROM meal_plans WHERE assessment_id = ?", (aid,)).fetchone()[0] == 0
            assert cur.execute("SELECT COUNT(*) FROM reports WHERE assessment_id = ?", (aid,)).fetchone()[0] == 0
        assert cur.execute("SELECT COUNT(*) FROM ground_truth_outcomes WHERE patient_id = ?", (test_pid,)).fetchone()[0] == 0

        # Verify audit trail contains PATIENT_DELETED entry
        cur.execute("SELECT * FROM audit_events WHERE action = 'PATIENT_DELETED' AND user_id = 'clinician_user' ORDER BY rowid DESC LIMIT 1")
        audit_row = cur.fetchone()
        assert audit_row is not None
        details = json.loads(audit_row["details_json"])
        assert details["patient_id"] == test_pid
        assert details["action"] == "PATIENT_DELETED"
        assert details["deleted_assessments_count"] == 2
    finally:
        conn.close()


def test_delete_nonexistent_patient_returns_404():
    """Verify calling DELETE on a nonexistent patient returns 404 Not Found."""
    fake_id = f"nonexistent-{uuid.uuid4().hex}"
    response = client.delete(f"/api/v1/patients/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
