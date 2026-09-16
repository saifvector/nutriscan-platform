"""
NutriScan Production Core Domain Exception Hierarchy.
Provides typed, structured, and observable domain exceptions for all subsystems:
- Clinical Safety
- Biomarker Validation
- ML Inference
- Persistence & Database Integrity
- Governance Audit Chaining
"""

from typing import Dict, Any, Optional


class NutriScanException(Exception):
    """Base domain exception for NutriScan clinical platform."""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ClinicalSafetyException(NutriScanException):
    """Raised when clinical safety guardrails, upper tolerable limits, or contraindications are breached."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="CLINICAL_SAFETY_VIOLATION",
            details=details
        )


class BiomarkerValidationException(NutriScanException):
    """Raised when biomarker, demographic, or physiological inputs violate physical/biological limits."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_BIOMARKER_INPUT",
            details=details
        )


class ModelInferenceException(NutriScanException):
    """Raised when ML champion models fail to infer or calibrate probabilities."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="MODEL_INFERENCE_FAILURE",
            details=details
        )


class PersistenceException(NutriScanException):
    """Raised when persistent SQLite storage or transaction fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="PERSISTENCE_TRANSACTION_FAILED",
            details=details
        )


class DatabaseIntegrityException(NutriScanException):
    """Raised when database corruption or check failure is detected."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_INTEGRITY_COMPROMISED",
            details=details
        )


class AuditTrailIntegrityException(NutriScanException):
    """Raised when audit trail forward SHA-256 hash verification fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="AUDIT_TRAIL_TAMPERED",
            details=details
        )
