"""
Comprehensive Backup & Restore Validation Test Suite for NutriScan.
Phase 3 Hardening:
- Automated Online Backup with SHA-256 Checksum Verification
- Tamper / Checksum Mismatch Detection
- Database Restoration Integrity Check
- Disaster Recovery Simulation:
  1. Record creation in isolated primary DB
  2. Snapshot online backup with SHA-256 sidecar
  3. Simulate primary DB file corruption
  4. Detect database corruption via verify_database_integrity()
  5. Restore from verified snapshot
  6. Verify low-level SQLite integrity and clinical data recovery
  7. Generate and certify Disaster Recovery (DR) audit report
"""

import os
import time
import uuid
import pytest

from app.core.persistence import PersistenceRepository, get_connection
import app.core.persistence as persistence_mod


@pytest.fixture
def recovery_env(tmp_path, monkeypatch):
    """Sets up an isolated database and backup directory for disaster recovery testing."""
    test_db = str(tmp_path / f"test_persistence_{uuid.uuid4().hex[:8]}.db")
    backup_dir = str(tmp_path / "backups")
    os.makedirs(backup_dir, exist_ok=True)

    monkeypatch.setattr(persistence_mod, "DB_PATH", test_db)
    persistence_mod.initialize_database()

    # Pre-populate with sample clinical assessment
    aid = f"asmt_{uuid.uuid4().hex[:8]}"
    now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO assessments (id, created_at, age, gender, dietary_pattern, payload_json)
                VALUES (?, ?, 35, 'FEMALE', 'VEGAN', '{}')
                """,
                (aid, now_str)
            )
    finally:
        conn.close()

    yield {"db_path": test_db, "backup_dir": backup_dir, "assessment_id": aid}


class TestBackupChecksumAndIntegrity:
    """Validates SHA-256 checksum generation, sidecar verification, and tamper detection."""

    def test_backup_generates_valid_sha256_sidecar(self, recovery_env):
        backup_path = os.path.join(recovery_env["backup_dir"], "valid_test_backup.db")
        created_path = PersistenceRepository.backup_database(backup_path, create_checksum=True)

        assert os.path.exists(created_path)
        sidecar_path = f"{created_path}.sha256"
        assert os.path.exists(sidecar_path)

        with open(sidecar_path, "r", encoding="utf-8") as f:
            stored_hash = f.read().strip()

        assert len(stored_hash) == 64  # SHA-256 hex length
        is_valid, computed, expected = PersistenceRepository.verify_backup_checksum(created_path)
        assert is_valid is True
        assert computed == stored_hash
        assert expected == stored_hash

    def test_tampered_backup_fails_checksum_verification(self, recovery_env):
        backup_path = os.path.join(recovery_env["backup_dir"], "tampered_backup.db")
        created_path = PersistenceRepository.backup_database(backup_path, create_checksum=True)

        # Tamper with backup file by appending corrupting bytes
        with open(created_path, "ab") as f:
            f.write(b"\x00\xFF\xDE\xAD\xBE\xEF_TAMPERED_DATA")

        is_valid, computed, expected = PersistenceRepository.verify_backup_checksum(created_path)
        assert is_valid is False
        assert computed != expected

        # Attempting to restore tampered backup MUST raise a ValueError
        with pytest.raises(ValueError) as exc_info:
            PersistenceRepository.restore_database(created_path, verify_checksum=True)
        assert "integrity failure" in str(exc_info.value).lower()


class TestDisasterRecoverySimulation:
    """Simulates primary database corruption and automated disaster recovery workflow."""

    def test_full_dr_lifecycle_and_data_preservation(self, recovery_env):
        db_path = recovery_env["db_path"]
        aid = recovery_env["assessment_id"]

        # 1. Take online backup with SHA-256
        backup_path = os.path.join(recovery_env["backup_dir"], "production_snapshot.db")
        PersistenceRepository.backup_database(backup_path, create_checksum=True)

        # 2. Simulate disastrous primary database truncation / corruption
        with open(db_path, "r+b") as f:
            f.seek(16)
            f.write(b"\x00\x00\x00\x00" * 32)

        # 3. Verify detection of corruption
        integrity_status = PersistenceRepository.verify_database_integrity()
        assert not integrity_status.get("is_healthy") or "ok" not in integrity_status.get("integrity_check", [])

        # 4. Execute disaster recovery restoration from verified backup
        start_restore = time.perf_counter()
        restored = PersistenceRepository.restore_database(backup_path, verify_checksum=True)
        restore_duration_ms = (time.perf_counter() - start_restore) * 1000.0

        assert restored is True
        assert restore_duration_ms < 5000.0  # RTO must be well under 5 seconds

        # 5. Verify restored database integrity
        post_restore_integrity = PersistenceRepository.verify_database_integrity()
        assert post_restore_integrity["is_healthy"] is True
        assert post_restore_integrity["integrity_check"] == ["ok"]
        assert post_restore_integrity["fk_violations_count"] == 0

        # 6. Verify recovered patient assessment data
        rec_conn = get_connection()
        try:
            cur = rec_conn.cursor()
            cur.execute("SELECT id, age, gender, dietary_pattern FROM assessments WHERE id = ?", (aid,))
            row = cur.fetchone()
            assert row is not None
            assert row["id"] == aid
            assert row["age"] == 35
            assert row["dietary_pattern"] == "VEGAN"
        finally:
            rec_conn.close()

        # 7. Compile Disaster Recovery (DR) report
        dr_report = PersistenceRepository.generate_disaster_recovery_report({
            "restore_duration_ms": restore_duration_ms,
            "data_loss_window_seconds": 0.0,
            "checksum_verified": True
        })
        assert dr_report["disaster_recovery_certified"] is True
        assert dr_report["achieved_rto_ms"] < 5000.0
        assert dr_report["sha256_checksum_verified"] is True
        assert dr_report["table_record_inventory"]["assessments"] >= 1
        assert "HIPAA" in dr_report["audit_compliance_standard"]
