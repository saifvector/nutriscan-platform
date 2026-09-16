"""
NutriScan Automated Backup & Disaster Recovery Manager
Phase 7: Enterprise Automated Backup, Retention Policy & Verification

Features:
- Online non-blocking database backup for dual-engine (PostgreSQL & SQLite)
- Gzip compression with SHA-256 integrity sidecar and manifest.json
- Automated retention policy enforcement (configurable days, default 30)
- Verified point-in-time restore with tamper detection
- CLI and programmatic API
"""

import os
import sys
import time
import gzip
import shutil
import hashlib
import json
import argparse
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Ensure project root and backend are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

try:
    from app.core.config import settings
    from app.core.persistence import PersistenceRepository, DB_PATH, get_active_engine
    import app.core.persistence as persistence_mod
except ImportError:
    from backend.app.core.config import settings
    from backend.app.core.persistence import PersistenceRepository, DB_PATH, get_active_engine
    import backend.app.core.persistence as persistence_mod

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nutriscan.backup_manager")


class BackupManager:
    """
    Automated backup orchestrator for NutriScan clinical persistence data.
    """

    def __init__(self, backup_dir: Optional[str] = None, retention_days: Optional[int] = None):
        self.backup_dir = os.path.abspath(backup_dir or getattr(settings, "BACKUP_DIR", "backups"))
        self.retention_days = retention_days or getattr(settings, "BACKUP_RETENTION_DAYS", 30)
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, compress: bool = True) -> Dict[str, Any]:
        """
        Creates an online, restart-safe snapshot of persistence data with SHA-256 validation.
        """
        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        engine_type = get_active_engine()
        
        base_name = f"nutriscan_backup_{engine_type}_{timestamp_str}"
        temp_raw_path = os.path.join(self.backup_dir, f"{base_name}.db")
        final_backup_path = os.path.join(self.backup_dir, f"{base_name}.db.gz" if compress else f"{base_name}.db")
        manifest_path = os.path.join(self.backup_dir, f"{base_name}_manifest.json")

        logger.info(f"Starting automated backup (engine: {engine_type}) to {final_backup_path}...")

        # 1. Take raw snapshot using persistence layer
        PersistenceRepository.backup_database(temp_raw_path, create_checksum=False)

        # 2. Extract entity counts from the snapshot
        entity_counts = self._count_entities_in_db(temp_raw_path)

        # 3. Compress if requested, else move
        if compress:
            with open(temp_raw_path, "rb") as f_in, gzip.open(final_backup_path, "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
            if os.path.exists(temp_raw_path):
                os.remove(temp_raw_path)
        else:
            final_backup_path = temp_raw_path

        # 4. Calculate SHA-256 of final backup artifact
        sha256_hash = self._compute_sha256(final_backup_path)
        sha256_file = f"{final_backup_path}.sha256"
        with open(sha256_file, "w", encoding="utf-8") as f:
            f.write(f"{sha256_hash}  {os.path.basename(final_backup_path)}\n")

        # 5. Build and write manifest metadata
        file_size = os.path.getsize(final_backup_path)
        manifest = {
            "version": "1.0.0",
            "backup_id": base_name,
            "timestamp": now.isoformat(),
            "engine": engine_type,
            "compressed": compress,
            "file_name": os.path.basename(final_backup_path),
            "file_size_bytes": file_size,
            "sha256": sha256_hash,
            "entities": entity_counts,
            "retention_days": self.retention_days
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Backup completed successfully: {os.path.basename(final_backup_path)} ({file_size} bytes, SHA256: {sha256_hash[:12]}...)")
        return manifest

    def restore_backup(self, backup_file_path: str, target_db_path: Optional[str] = None) -> bool:
        """
        Restores database from a compressed or raw backup after verifying SHA-256 checksum.
        """
        target_path = target_db_path or persistence_mod.DB_PATH
        full_path = os.path.abspath(backup_file_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Backup file not found: {full_path}")

        logger.info(f"Verifying backup integrity for {full_path} prior to restore...")

        # 1. Verify SHA-256 sidecar if present
        sha256_file = f"{full_path}.sha256"
        if os.path.exists(sha256_file):
            with open(sha256_file, "r", encoding="utf-8") as f:
                expected_sha = f.read().split()[0].strip()
            actual_sha = self._compute_sha256(full_path)
            if actual_sha != expected_sha:
                err_msg = f"SECURITY ALERT: SHA-256 checksum mismatch! Expected: {expected_sha}, Got: {actual_sha}"
                logger.critical(err_msg)
                raise ValueError(err_msg)
            logger.info("SHA-256 integrity verified successfully.")

        # 2. Decompress or copy to target DB
        is_gz = full_path.endswith(".gz")
        temp_restore = f"{target_path}.restoring_tmp"

        if is_gz:
            with gzip.open(full_path, "rb") as f_in, open(temp_restore, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(full_path, temp_restore)

        # 3. Verify SQLite integrity on restored temp file
        import sqlite3
        conn = sqlite3.connect(temp_restore)
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            res = cursor.fetchone()
            if not res or res[0] != "ok":
                raise RuntimeError(f"Database integrity check failed: {res}")
        finally:
            conn.close()

        # 4. Atomic swap to target path
        if os.path.exists(target_path):
            backup_existing = f"{target_path}.prev_bak"
            if os.path.exists(backup_existing):
                os.remove(backup_existing)
            os.replace(target_path, backup_existing)

        os.replace(temp_restore, target_path)
        logger.info(f"Database restored successfully into {target_path}")
        return True

    def prune_retention(self) -> List[str]:
        """
        Prunes backup files and manifests older than retention_days.
        """
        now = time.time()
        retention_seconds = self.retention_days * 86400
        pruned_files = []

        if not os.path.exists(self.backup_dir):
            return []

        for fname in os.listdir(self.backup_dir):
            fpath = os.path.join(self.backup_dir, fname)
            if os.path.isfile(fpath) and (fname.endswith(".gz") or fname.endswith(".db") or fname.endswith(".json") or fname.endswith(".sha256")):
                mtime = os.path.getmtime(fpath)
                if now - mtime > retention_seconds:
                    try:
                        os.remove(fpath)
                        pruned_files.append(fname)
                        logger.info(f"Pruned expired backup file: {fname}")
                    except Exception as e:
                        logger.warning(f"Failed to prune {fname}: {e}")

        logger.info(f"Retention pruning complete. {len(pruned_files)} files pruned.")
        return pruned_files

    def list_backups(self) -> List[Dict[str, Any]]:
        """Lists all existing backup archives and metadata."""
        backups = []
        if not os.path.exists(self.backup_dir):
            return []

        for fname in sorted(os.listdir(self.backup_dir), reverse=True):
            if fname.endswith("_manifest.json"):
                mpath = os.path.join(self.backup_dir, fname)
                try:
                    with open(mpath, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    backups.append(manifest)
                except Exception:
                    pass
        return backups

    def _compute_sha256(self, filepath: str) -> str:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _count_entities_in_db(self, db_file: str) -> Dict[str, int]:
        import sqlite3
        counts = {}
        tables = ["assessments", "predictions", "recommendations", "meal_plans", "forecasts", "reports"]
        conn = sqlite3.connect(db_file)
        try:
            cursor = conn.cursor()
            for t in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {t};")
                    counts[t] = cursor.fetchone()[0]
                except Exception:
                    counts[t] = 0
        finally:
            conn.close()
        return counts


# Singleton instance
backup_manager = BackupManager()


def main():
    parser = argparse.ArgumentParser(description="NutriScan Automated Backup & Disaster Recovery Manager")
    parser.add_argument("--backup", action="store_true", help="Create an automated backup")
    parser.add_argument("--no-compress", action="store_true", help="Do not gzip compress the backup")
    parser.add_argument("--restore", type=str, help="Restore database from backup file path")
    parser.add_argument("--list", action="store_true", help="List all backups and manifests")
    parser.add_argument("--prune", action="store_true", help="Prune backups exceeding retention policy")

    args = parser.parse_args()

    if args.backup:
        manifest = backup_manager.create_backup(compress=not args.no_compress)
        print(json.dumps(manifest, indent=2))
    elif args.restore:
        backup_manager.restore_backup(args.restore)
        print(f"Restore of {args.restore} completed successfully.")
    elif args.prune:
        pruned = backup_manager.prune_retention()
        print(f"Pruned {len(pruned)} expired files.")
    elif args.list:
        backups = backup_manager.list_backups()
        print(json.dumps(backups, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
