"""
Database Migration Script: Upgrade Stored Predictions to AssessmentPredictionSnapshot
Migrates existing SQLite prediction records in nutriscan_persistence.db to the unified
authoritative ClinicalRiskEngine snapshot, guaranteeing logical consistency across Dashboard,
Reasoning, Evidence, and Recommendations.
"""

import sys
import os
import json
import uuid
import sqlite3

# Add project root and backend to path
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('backend'))

from backend.app.core.persistence import initialize_database, PersistenceRepository, get_connection
from backend.app.modules.prediction.service import PredictionService

def migrate_snapshots():
    print("=" * 70)
    print("MIGRATING PERSISTED ASSESSMENTS TO AUTHORITATIVE SNAPSHOTS")
    print("=" * 70)

    # 1. Ensure table schema is up to date
    initialize_database()

    # 2. Fetch all assessments
    assessments = PersistenceRepository.list_assessments(limit=1000)
    print(f"Found {len(assessments)} assessments in persistence layer.")

    migrated_count = 0
    already_up_to_date = 0

    for asmt_meta in assessments:
        asmt_id = asmt_meta["id"]
        payload = PersistenceRepository.get_assessment(asmt_id)
        if not payload:
            print(f"Skipping {asmt_id}: Payload not found.")
            continue

        existing_pred = PersistenceRepository.get_predictions(asmt_id)
        is_up_to_date = (
            existing_pred
            and isinstance(existing_pred, dict)
            and "health_score" in existing_pred
            and "explanations" in existing_pred
            and "evidence_catalog" in existing_pred
            and len(existing_pred.get("explanations", [])) > 0
        )

        try:
            asmt_uuid = uuid.UUID(asmt_id)
        except Exception:
            asmt_uuid = uuid.uuid4()

        if is_up_to_date:
            already_up_to_date += 1
            print(f"Assessment {asmt_id} is already up to date (Health Score: {existing_pred['health_score']}, Category: {existing_pred['category']}).")
        else:
            try:
                print(f"Migrating assessment {asmt_id}...")
                snapshot = PredictionService.predict_assessment(
                    assessment_payload=payload,
                    assessment_id=asmt_uuid,
                    compute_explainability=True
                )
                migrated_count += 1
                print(f"  -> SUCCESS! Health Score: {snapshot['health_score']}, Category: {snapshot['category']}, Risk Counts: {snapshot['risk_counts']}")
            except Exception as e:
                print(f"  -> ERROR migrating {asmt_id}: {e}")

    print("\n" + "=" * 70)
    print(f"MIGRATION COMPLETE: {migrated_count} migrated, {already_up_to_date} already up to date.")
    print("=" * 70)

if __name__ == "__main__":
    migrate_snapshots()
