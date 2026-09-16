"""
SQLAlchemy Models for Phase 9: Outcome Learning & Adaptive Nutrition Intelligence
Defines:
- adherence_logs
- symptom_journals
- lab_results
- outcome_metrics
- adaptive_recommendations
- prediction_validation
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, Date, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base


class AdherenceLog(Base):
    __tablename__ = "adherence_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_id = Column(String(100), nullable=False, index=True)
    log_date = Column(Date, default=date.today, nullable=False, index=True)

    meal_adherence_pct = Column(Float, default=100.0, nullable=False)
    supplement_adherence_pct = Column(Float, default=100.0, nullable=False)
    lifestyle_adherence_pct = Column(Float, default=100.0, nullable=False)

    hydration_liters = Column(Float, default=2.5, nullable=False)
    sunlight_minutes = Column(Integer, default=20, nullable=False)
    sleep_hours = Column(Float, default=8.0, nullable=False)
    exercise_minutes = Column(Integer, default=30, nullable=False)

    daily_adherence_score = Column(Float, nullable=False)
    adherence_tier = Column(String(50), nullable=False)  # EXCELLENT, GOOD, MODERATE, POOR

    missed_items = Column(JSONB, default=list, nullable=False)
    logged_items = Column(JSONB, default=list, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class SymptomJournal(Base):
    __tablename__ = "symptom_journals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_id = Column(String(100), nullable=False, index=True)
    recorded_date = Column(Date, default=date.today, nullable=False, index=True)

    # Symptom ratings on 0-10 severity scale stored in JSONB for extensibility
    symptom_scores = Column(JSONB, default=dict, nullable=False)
    overall_symptom_score = Column(Float, nullable=False)  # Average severity 0-10
    symptom_recovery_score = Column(Float, nullable=False)  # 0-100 where 100 is symptom-free

    clinical_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_id = Column(String(100), nullable=False, index=True)
    test_date = Column(Date, default=date.today, nullable=False, index=True)
    lab_provider = Column(String(150), default="Certified Clinical Laboratory", nullable=False)

    # Dictionary of tested biomarkers and values
    biomarkers = Column(JSONB, default=dict, nullable=False)
    clinical_interpretation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class OutcomeMetric(Base):
    __tablename__ = "outcome_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_id = Column(String(100), nullable=False, index=True)
    evaluation_date = Column(Date, default=date.today, nullable=False, index=True)

    baseline_health_score = Column(Float, nullable=False)
    current_health_score = Column(Float, nullable=False)
    health_score_delta = Column(Float, nullable=False)
    recovery_velocity = Column(Float, default=0.0, nullable=False)

    adherence_score_avg = Column(Float, nullable=False)
    effectiveness_scores = Column(JSONB, default=dict, nullable=False)
    relapse_risk_score = Column(Float, default=0.0, nullable=False)
    recovery_status = Column(String(50), default="IMPROVING", nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class AdaptiveRecommendation(Base):
    __tablename__ = "adaptive_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_id = Column(String(100), nullable=False, index=True)
    adaptation_date = Column(Date, default=date.today, nullable=False, index=True)

    trigger_reason = Column(String(150), nullable=False)  # e.g. FISH_AVOIDANCE, LOW_SUNLIGHT, SUPPLEMENT_RESISTANCE
    scenario_category = Column(String(50), nullable=False)
    original_interventions = Column(JSONB, default=list, nullable=False)
    adapted_interventions = Column(JSONB, default=list, nullable=False)
    adaptation_rationale = Column(Text, nullable=False)

    is_active = Column(String(20), default="ACTIVE", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class PredictionValidation(Base):
    __tablename__ = "prediction_validation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    assessment_id = Column(String(100), nullable=False, index=True)
    evaluation_date = Column(Date, default=date.today, nullable=False, index=True)

    milestone_day = Column(Integer, nullable=False)  # 30, 60, 90
    predicted_score = Column(Float, nullable=False)
    actual_score = Column(Float, nullable=False)
    projection_error = Column(Float, nullable=False)
    accuracy_pct = Column(Float, nullable=False)
    calibration_status = Column(String(50), default="CALIBRATED", nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
