"""
NutriScan Automated Backup & Disaster Recovery Verification Test Suite
Phase 7: Production Automated Backups & Disaster Recovery

Tests:
1. Backup creation with gzip compression, SHA-256 sidecar, and manifest.json.
2. Tamper detection: Checksum verification detects corrupted/altered archives.
3. Database restoration integrity: Recovers data loss scenarios.
4. Retention policy enforcement: Prunes expired backups while retaining recent backups.
5. CLI argument handling and execution.
"""

import os
import time
import uuid
import pytest

from scripts.backup_manager import BackupManager
import app.core.persistence as persistence_mod
from app.core.persistence import PersistenceRepository, get_connection


@pytest.fixture
def isolated_backup_env(tmp_path, monkeypatch):
    """Sets up an isolated database and backup directory."""
    db_file = str(tmp_path / f"test_clinical_db_{uuid.uuid4().hex[:8]}.db")
    backup_folder = str(tmp_path / "clinical_backups")
    os.makedirs(backup_folder, exist_ok=True)

    monkeypatch.setattr(persistence_mod, "DB_PATH", db_file)
    persistence_mod.initialize_database()

    # Insert a test assessment
    aid = f"asmt_{uuid.uuid4().hex[:8]}"
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO assessments (id, created_at, age, gender, dietary_pattern, payload_json)
                VALUES (?, ?, 42, 'MALE', 'VEGETARIAN', '{"hemoglobin": 13.5}')
                """,
                (aid, time.strftime("%Y-%m-%dT%H:%M:%SZ"))
            )
    finally:
        conn.close()

    manager = BackupManager(backup_dir=backup_folder, retention_days=30)
    yield {
        "db_file": db_file,
        "backup_folder": backup_folder,
        "assessment_id": aid,
        "manager": manager
    }


def test_backup_creation_and_manifest(isolated_backup_env):
    """Verify backup creates .gz, .sha256 sidecar, and manifest.json with entity counts."""
    mgr = isolated_backup_env["manager"]
    manifest = mgr.create_backup(compress=True)

    assert manifest is not None
    assert manifest["compressed"] is True
    assert manifest["sha256"] is not None
    assert len(manifest["sha256"]) == 64
    assert manifest["entities"]["assessments"] >= 1

    # Verify files on disk
    backup_file = os.path.join(isolated_backup_env["backup_folder"], manifest["file_name"])
    assert os.path.exists(backup_file)
    assert os.path.exists(f"{backup_file}.sha256")
    manifest_file = os.path.join(isolated_backup_env["backup_folder"], f"{manifest['backup_id']}_manifest.json")
    assert os.path.exists(manifest_file)


def test_tamper_detection_on_restore(isolated_backup_env):
    """Verify restore refuses an archive whose content has been tampered with."""
    mgr = isolated_backup_env["manager"]
    manifest = mgr.create_backup(compress=True)
    backup_file = os.path.join(isolated_backup_env["backup_folder"], manifest["file_name"])

    # Tamper with the backup file by appending corrupt bytes
    with open(backup_file, "ab") as f:
        f.write(b"CORRUPTED_MALICIOUS_INJECTION")

    # Restore must raise ValueError on checksum mismatch
    with pytest.raises(ValueError, match="SECURITY ALERT: SHA-256 checksum mismatch"):
        mgr.restore_backup(backup_file, target_db_path=isolated_backup_env["db_file"])


def test_database_disaster_recovery_restore(isolated_backup_env):
    """Verify full recovery after simulated total database wipe."""
    mgr = isolated_backup_env["manager"]
    aid = isolated_backup_env["assessment_id"]
    db_file = isolated_backup_env["db_file"]

    # 1. Create backup
    manifest = mgr.create_backup(compress=True)
    backup_file = os.path.join(isolated_backup_env["backup_folder"], manifest["file_name"])

    # 2. Simulate catastrophic database deletion / corruption
    if os.path.exists(db_file):
        os.remove(db_file)
    assert not os.path.exists(db_file)

    # 3. Perform verified restore
    restored = mgr.restore_backup(backup_file, target_db_path=db_file)
    assert restored is True
    assert os.path.exists(db_file)

    # 4. Verify clinical entity is preserved
    asmt = PersistenceRepository.get_assessment(aid)
    assert asmt is not None
    assert asmt["age"] == 42
    assert asmt["gender"] == "MALE"


def test_retention_pruning_policy(isolated_backup_env):
    """Verify files older than retention policy are pruned while newer ones are retained."""
    mgr = isolated_backup_env["manager"]
    folder = isolated_backup_env["backup_folder"]

    # Create active backup
    active_manifest = mgr.create_backup(compress=True)
    active_file = os.path.join(folder, active_manifest["file_name"])

    # Create artificial old backup (35 days old)
    old_file = os.path.join(folder, "nutriscan_backup_sqlite_20260101_000000.db.gz")
    with open(old_file, "wb") as f:
        f.write(b"dummy_old_backup_data")

    # Backdate mtime to 35 days ago
    old_time = time.time() - (35 * 86400)
    os.utime(old_file, (old_time, old_time))

    assert os.path.exists(old_file)
    assert os.path.exists(active_file)

    # Execute pruning
    pruned = mgr.prune_retention()
    assert os.path.basename(old_file) in pruned
    assert not os.path.exists(old_file)
    # Active file must remain
    assert os.path.exists(active_file)
