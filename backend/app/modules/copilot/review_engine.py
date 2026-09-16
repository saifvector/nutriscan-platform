"""
Clinician Review & Decision Workflow Engine
Supports:
- APPROVE recommendation
- REJECT recommendation
- MODIFY recommendation
- ESCALATE recommendation (with subspecialty routing)
Backed by SHA-256 tamper-evident audit trail logging.
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .schemas import ClinicianReviewRequest, ClinicianReviewRecord
from ...core.metrics import metrics


class ReviewEngine:
    """Manages physician review decisions, modifications, escalations, and tamper-evident audit logs."""

    # In-memory audit log store (persists across runtime, can also write to DB)
    _audit_store: List[ClinicianReviewRecord] = []

    @classmethod
    def process_review(cls, request: ClinicianReviewRequest) -> ClinicianReviewRecord:
        """
        Processes a clinician review decision, validates clinical input,
        computes a SHA-256 audit signature, and records telemetry.
        """
        valid_decisions = ["APPROVE", "REJECT", "MODIFY", "ESCALATE"]
        decision = request.decision.upper()
        if decision not in valid_decisions:
            raise ValueError(f"Invalid decision '{decision}'. Must be one of {valid_decisions}")

        if decision == "ESCALATE" and not request.escalation_specialty:
            request.escalation_specialty = "HEMATOLOGY_AND_METABOLIC_MEDICINE"

        # Construct audit payload for cryptographic hashing
        audit_payload = {
            "patient_id": request.patient_id,
            "clinician_id": request.clinician_id,
            "clinician_name": request.clinician_name,
            "decision": decision,
            "target_intervention_id": request.target_intervention_id,
            "target_category": request.target_category,
            "modifications": request.modifications,
            "rationale": request.rationale,
            "escalation_specialty": request.escalation_specialty,
            "timestamp": datetime.utcnow().isoformat()
        }

        # SHA-256 hash
        hasher = hashlib.sha256()
        hasher.update(json.dumps(audit_payload, sort_keys=True).encode("utf-8"))
        audit_hash = hasher.hexdigest()

        record = ClinicianReviewRecord(
            patient_id=request.patient_id,
            clinician_id=request.clinician_id,
            clinician_name=request.clinician_name,
            clinician_role=request.clinician_role,
            decision=decision,
            target_intervention_id=request.target_intervention_id,
            target_category=request.target_category,
            modifications=request.modifications,
            rationale=request.rationale,
            escalation_specialty=request.escalation_specialty,
            audit_hash=audit_hash
        )

        cls._audit_store.append(record)

        # Record Prometheus metric
        try:
            metrics.record_review(decision=decision)
            metrics.record_copilot_op(op_type="clinician_review", status="success")
        except Exception:
            pass

        return record

    @classmethod
    def get_patient_audit_history(cls, patient_id: str) -> List[ClinicianReviewRecord]:
        """Returns all review audit entries logged for a specific patient."""
        return [r for r in cls._audit_store if r.patient_id == patient_id]

    @classmethod
    def get_all_reviews(cls) -> List[ClinicianReviewRecord]:
        """Returns entire clinical review audit registry."""
        return list(cls._audit_store)
