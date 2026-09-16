"""
Phase 12: SQLAlchemy Models for Clinical Audit, Safety Events, Drift Snapshots, and Monitoring Alerts.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from .user import Base


class ClinicalAuditRecord(Base):
    __tablename__ = "clinical_audit_records"

    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    model_suite_version = Column(String(50), nullable=False)
    feature_completeness_pct = Column(Numeric(5, 2), nullable=False)
    total_features_evaluated = Column(Integer, nullable=False)
    observed_features_count = Column(Integer, nullable=False)
    overall_risk_tier = Column(String(20), nullable=False, index=True)
    overall_risk_score = Column(Numeric(5, 2), nullable=False)
    safety_score = Column(Numeric(5, 2), nullable=False)
    safety_tier = Column(String(20), nullable=False, index=True)
    predictions_json = Column(JSON, nullable=False)
    top_predictors_json = Column(JSON, nullable=False)
    recommendation_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    evidence_ids = Column(ARRAY(String), nullable=True)
    safety_flags_json = Column(JSON, nullable=True)
    inference_latency_ms = Column(Numeric(7, 2), nullable=False)
    client_ip = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ClinicalSafetyEvent(Base):
    __tablename__ = "clinical_safety_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("clinical_audit_records.audit_id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True) # LOW, MODERATE, HIGH, CRITICAL
    rule_id = Column(String(100), nullable=False, index=True)
    rule_name = Column(String(255), nullable=False)
    nutrient = Column(String(100), nullable=True)
    violating_value = Column(Numeric(10, 2), nullable=True)
    threshold_value = Column(Numeric(10, 2), nullable=True)
    clinical_rationale = Column(Text, nullable=False)
    action_taken = Column(String(50), nullable=False) # FLAGGED, QUARANTINED, BLOCKED, OVERRIDDEN
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class ModelDriftSnapshot(Base):
    __tablename__ = "model_drift_snapshots"

    snapshot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    target_or_feature = Column(String(100), nullable=False, index=True)
    drift_category = Column(String(50), nullable=False) # FEATURE, POPULATION, PREDICTION, NUTRIENT_INTAKE
    metric_type = Column(String(20), nullable=False) # PSI, KS_2SAMPLE, WASSERSTEIN
    metric_value = Column(Numeric(8, 5), nullable=False)
    p_value = Column(Numeric(8, 5), nullable=True)
    drift_status = Column(String(20), nullable=False, index=True) # STABLE, MODERATE_SHIFT, SIGNIFICANT_DRIFT
    alert_triggered = Column(Boolean, default=False, nullable=False)
    sample_size = Column(Integer, nullable=False)


class ValidationBenchmark(Base):
    __tablename__ = "validation_benchmarks"

    benchmark_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target = Column(String(100), nullable=False, index=True)
    subgroup_category = Column(String(50), nullable=False, index=True) # AGE, SEX, RACE_ETHNICITY, INCOME_PIR
    subgroup_value = Column(String(100), nullable=False)
    sample_size = Column(Integer, nullable=False)
    prevalence_pct = Column(Numeric(5, 2), nullable=False)
    auroc = Column(Numeric(5, 4), nullable=False)
    auprc = Column(Numeric(5, 4), nullable=False)
    sensitivity = Column(Numeric(5, 4), nullable=False)
    specificity = Column(Numeric(5, 4), nullable=False)
    ppv = Column(Numeric(5, 4), nullable=False)
    npv = Column(Numeric(5, 4), nullable=False)
    f1_score = Column(Numeric(5, 4), nullable=False)
    calibrated_ece = Column(Numeric(6, 4), nullable=False)
    brier_score = Column(Numeric(6, 4), nullable=False)
    evaluated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class MonitoringAlert(Base):
    __tablename__ = "monitoring_alerts"

    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False) # DRIFT_ALERT, CALIBRATION_DEGRADATION, SAFETY_VIOLATION, etc.
    severity = Column(String(20), nullable=False, index=True) # INFO, WARNING, CRITICAL
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    is_acknowledged = Column(Boolean, default=False, nullable=False, index=True)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
