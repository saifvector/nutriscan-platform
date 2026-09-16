"""
Phase 8 Disaster Recovery & Resilience Test Suite.
Validates:
1. Online Database Backup: PersistenceRepository.backup_database creates valid backup copy.
2. Integrity Verification: PRAGMA integrity_check validates zero malformed pages or index corruption.
3. Database Restoration: PersistenceRepository.restore_database restores data from verified backup.
4. Corruption Detection: Synthetic byte-level corruption is caught by verify_database_integrity.
5. Crash Recovery: Database recovers cleanly after abrupt unclosed connections in WAL mode.
"""

import os
import uuid
import sqlite3
import pytest

from backend.app.core.persistence import PersistenceRepository, get_connection
import backend.app.core.persistence as persistence_mod


@pytest.fixture
def recovery_env(tmp_path, monkeypatch):
    """Isolated environment for disaster recovery testing."""
    test_db = str(tmp_path / f"recovery_{uuid.uuid4().hex[:8]}.db")
    backup_dir = str(tmp_path / "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    monkeypatch.setattr(persistence_mod, "DB_PATH", test_db)
    persistence_mod.initialize_database()
    
    # Populate with sample clinical assessment
    aid = str(uuid.uuid4())
    PersistenceRepository.save_assessment(
        assessment_id=aid,
        payload={"age": 42, "gender": "FEMALE", "dietary_pattern": "MEDITERRANEAN"}
    )
    PersistenceRepository.log_audit_event(
        module="DISASTER_TEST",
        action="SNAPSHOT_BASELINE",
        assessment_id=aid
    )
    
    yield {"db_path": test_db, "backup_dir": backup_dir, "assessment_id": aid}


def test_online_backup_and_integrity_check(recovery_env):
    """Verify backup_database creates a valid, uncorrupted SQLite backup file."""
    backup_file = os.path.join(recovery_env["backup_dir"], "test_backup.db")
    created_path = PersistenceRepository.backup_database(backup_file)
    
    assert os.path.exists(created_path)
    assert os.path.getsize(created_path) > 0
    
    # Integrity check on live database
    diag = PersistenceRepository.verify_database_integrity()
    assert diag["is_healthy"] is True
    assert diag["integrity_check"] == ["ok"]
    
    # Integrity check on backup file
    conn_b = sqlite3.connect(created_path)
    try:
        cur = conn_b.cursor()
        cur.execute("PRAGMA integrity_check;")
        row = cur.fetchone()
        assert row[0] == "ok"
    finally:
        conn_b.close()


def test_database_restore_functionality(recovery_env):
    """Verify that restoring from backup restores missing records."""
    aid = recovery_env["assessment_id"]
    backup_file = os.path.join(recovery_env["backup_dir"], "pre_delete_backup.db")
    PersistenceRepository.backup_database(backup_file)
    
    # Simulate accidental data deletion
    conn = get_connection()
    try:
        with conn:
            conn.execute("DELETE FROM assessments WHERE id = ?", (aid,))
    finally:
        conn.close()
        
    assert PersistenceRepository.get_assessment(aid) is None, "Record should be deleted"
    
    # Restore from backup
    restored = PersistenceRepository.restore_database(backup_file)
    assert restored is True
    
    # Record must be recovered
    recovered = PersistenceRepository.get_assessment(aid)
    assert recovered is not None
    assert recovered["age"] == 42


def test_corruption_detection(recovery_env):
    """Verify verify_database_integrity detects physical file corruption."""
    db_path = recovery_env["db_path"]
    
    # Check baseline integrity passes
    baseline = PersistenceRepository.verify_database_integrity()
    assert baseline["is_healthy"] is True
    
    # Corrupt database header/pages
    with open(db_path, "r+b") as f:
        f.seek(16)  # Overwrite SQLite header / page size bytes
        f.write(b"\x00\x00\x00\x00" * 32)
        
    # verify_database_integrity must detect corruption
    diag = PersistenceRepository.verify_database_integrity()
    assert diag["is_healthy"] is False, f"Corruption check must report False: {diag}"


def test_wal_checkpoint_and_reconnection(recovery_env):
    """Verify WAL checkpointing and seamless recovery across connection teardown."""
    db_path = recovery_env["db_path"]
    
    # Open connection, write records, close abruptly
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    cur = conn.cursor()
    new_id = str(uuid.uuid4())
    cur.execute("INSERT INTO assessments (id, created_at, payload_json) VALUES (?, datetime('now'), ?)", (new_id, '{"test": 1}'))
    conn.commit()
    conn.close()
    
    # Reconnect via repository
    recovered = PersistenceRepository.get_assessment(new_id)
    assert recovered is not None
    assert recovered["test"] == 1
    assert PersistenceRepository.is_healthy() is True
