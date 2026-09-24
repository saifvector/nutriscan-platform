"""
Automated Integration Tests for Enterprise-Grade "Delete All Patients" Feature
Validates:
1. DELETE /api/v1/patients/all endpoint functionality:
   - Atomic transactional deletion of all patients, assessments, predictions, reports, forecasts, meal plans, etc.
   - Deletion of child tables before parent tables.
   - Response payload structure:
     {
       "success": True,
       "deleted_patients": N,
       "deleted_assessments": N,
       "deleted_predictions": N,
       "deleted_reports": N,
       "message": "All patient data deleted successfully"
     }
2. Transaction safety and atomic rollback on simulated database failure.
3. Cryptographic audit event logging with action 'ALL_PATIENTS_DELETED' and severity 'CRITICAL'.
4. Prevention of accidental data loss via isolated test database.
"""

import os
import uuid
import tempfile
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

import backend.app.core.persistence as persistence
from backend.app.core.persistence import PersistenceRepository, get_connection
from backend.app.main import app

client = TestClient(app)


@pytest.fixture(autouse=False)
def isolated_test_db(monkeypatch):
    """
    Creates an isolated temporary SQLite database so test deletion
    never touches production or local developmental database records.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name

    monkeypatch.setattr(persistence, "DB_PATH", temp_db_path)
    persistence.initialize_database()

    yield temp_db_path

    try:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
    except Exception:
        pass


def seed_test_database():
    """Seeds test database with 2 patients, 3 assessments, predictions, reports, and meal plans."""
    conn = get_connection()
    try:
        with conn:
            # Insert 2 patients
            conn.execute(
                """
                INSERT INTO patients (id, name, gender, current_age, height_cm, weight_kg, dietary_pattern, created_at, updated_at)
                VALUES ('p-101', 'Alice Johnson', 'FEMALE', 34, 168.0, 62.0, 'BALANCED', datetime('now'), datetime('now')),
                       ('p-102', 'Bob Smith', 'MALE', 45, 180.0, 85.0, 'MEDITERRANEAN', datetime('now'), datetime('now'))
                """
            )

            # Insert 3 assessments
            assessments = [
                ('a-101', 'p-101', 'Alice Johnson'),
                ('a-102', 'p-101', 'Alice Johnson'),
                ('a-103', 'p-102', 'Bob Smith')
            ]
            for aid, pid, pname in assessments:
                conn.execute(
                    """
                    INSERT INTO assessments (id, created_at, age, gender, dietary_pattern, payload_json, patient_id, patient_name)
                    VALUES (?, datetime('now'), 40, 'OTHER', 'BALANCED', '{}', ?, ?)
                    """,
                    (aid, pid, pname)
                )
                conn.execute(
                    """
                    INSERT INTO predictions (assessment_id, created_at, overall_risk, overall_risk_score, predictions_json)
                    VALUES (?, datetime('now'), 'LOW', 20.0, '[]')
                    """,
                    (aid,)
                )
                conn.execute(
                    """
                    INSERT INTO recommendations (assessment_id, created_at, safety_score, safety_tier, recommendations_json)
                    VALUES (?, datetime('now'), 95.0, 'OPTIMAL', '{}')
                    """,
                    (aid,)
                )
                conn.execute(
                    """
                    INSERT INTO meal_plans (assessment_id, created_at, dietary_pattern, plan_json)
                    VALUES (?, datetime('now'), 'BALANCED', '{}')
                    """,
                    (aid,)
                )
                conn.execute(
                    """
                    INSERT INTO forecasts (assessment_id, created_at, forecast_json)
                    VALUES (?, datetime('now'), '{}')
                    """,
                    (aid,)
                )
                conn.execute(
                    """
                    INSERT INTO reports (id, assessment_id, created_at, report_title, report_json)
                    VALUES (?, ?, datetime('now'), 'Clinical Screening Report', '{}')
                    """,
                    (f"rep-{aid}", aid)
                )
                conn.execute(
                    """
                    INSERT INTO ground_truth_outcomes (id, assessment_id, patient_id, followup_day, nutrient, predicted_value, actual_lab_value, delta, concordance_pct, created_at)
                    VALUES (?, ?, ?, 30, 'Iron', 15.0, 16.0, 1.0, 95.0, datetime('now'))
                    """,
                    (f"gt-{aid}", aid, pid)
                )
                conn.execute(
                    """
                    INSERT INTO clinician_reviews (id, assessment_id, clinician_id, clinician_name, license_number, decision, overrides_json, created_at)
                    VALUES (?, ?, 'doc-1', 'Dr. Smith', 'MD-999', 'APPROVED', '{}', datetime('now'))
                    """,
                    (f"cr-{aid}", aid)
                )
    finally:
        conn.close()


def test_delete_all_patients_endpoint(isolated_test_db):
    """
    Verifies DELETE /api/v1/patients/all removes all records across all tables
    and returns exact required deletion summary.
    """
    seed_test_database()

    # Verify data exists before deletion
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM patients")
        assert cur.fetchone()[0] == 2
        cur.execute("SELECT COUNT(*) FROM assessments")
        assert cur.fetchone()[0] == 3
        cur.execute("SELECT COUNT(*) FROM predictions")
        assert cur.fetchone()[0] == 3
        cur.execute("SELECT COUNT(*) FROM reports")
        assert cur.fetchone()[0] == 3
    finally:
        conn.close()

    # Execute DELETE /api/v1/patients/delete-all (Option B primary endpoint)
    response = client.delete("/api/v1/patients/delete-all")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["success"] is True
    assert data["deleted_patients"] == 2
    assert data["deleted_assessments"] == 3
    assert data["deleted_predictions"] == 3
    assert data["deleted_reports"] == 3
    assert data["message"] == "All patient data deleted successfully"

    # Verify tables are completely empty
    conn = get_connection()
    try:
        cur = conn.cursor()
        for table in [
            "patients",
            "assessments",
            "predictions",
            "recommendations",
            "meal_plans",
            "forecasts",
            "reports",
            "clinician_reviews",
            "ground_truth_outcomes",
        ]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            assert count == 0, f"Table {table} must be empty after delete_all, found {count}"

        # Verify audit log entry was created
        cur.execute("SELECT * FROM audit_events WHERE action = 'ALL_PATIENTS_DELETED'")
        log_entry = cur.fetchone()
        assert log_entry is not None, "Audit event for ALL_PATIENTS_DELETED must be logged"
        assert log_entry["severity"] == "CRITICAL"
        assert "ALL_PATIENTS_DELETED" in log_entry["details_json"]
    finally:
        conn.close()


def test_delete_all_patients_alias_endpoint(isolated_test_db):
    """
    Verifies that DELETE /api/v1/patients/all works properly and does NOT
    get routed to /{patient_id} returning 'Patient with identifier all was not found'.
    """
    seed_test_database()
    response = client.delete("/api/v1/patients/all")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert data["deleted_patients"] == 2
    assert "detail" not in data or "not found" not in str(data["detail"]).lower()


def test_delete_all_patients_rollback_on_failure(isolated_test_db):
    """
    Verifies that if an unexpected error occurs during deletion,
    the entire transaction is rolled back and no records are deleted.
    """
    seed_test_database()

    # Create an abort trigger in SQLite on predictions to simulate a database failure during cascade
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TRIGGER abort_delete_predictions
            BEFORE DELETE ON predictions
            BEGIN
                SELECT RAISE(ABORT, 'Simulated Database Failure During Cascade');
            END;
            """
        )
    finally:
        conn.close()

    # Attempt to delete all patients - should fail and roll back atomically
    with pytest.raises(Exception, match="Simulated Database Failure"):
        PersistenceRepository.delete_all_patients(deleted_by="test_admin")

    # Verify transaction rollback: all patients, assessments, and predictions must still exist!
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM patients")
        assert cur.fetchone()[0] == 2, "Patients must not be deleted if transaction fails"
        cur.execute("SELECT COUNT(*) FROM assessments")
        assert cur.fetchone()[0] == 3, "Assessments must not be deleted if transaction fails"
        cur.execute("SELECT COUNT(*) FROM predictions")
        assert cur.fetchone()[0] == 3, "Predictions must not be deleted if transaction fails"
    finally:
        conn.close()
