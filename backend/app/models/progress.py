import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base


class AssessmentHistory(Base):
    __tablename__ = "assessment_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("health_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_number = Column(Integer, nullable=False, default=1)
    version_tag = Column(String(50), nullable=False, default="v1.0")
    health_score = Column(Integer, nullable=False)
    health_category = Column(String(50), nullable=False)
    risk_distribution = Column(JSONB, default=dict, nullable=False)
    deficiencies_identified = Column(JSONB, default=list, nullable=False)
    snapshot_data = Column(JSONB, default=dict, nullable=False)
    clinical_notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", backref="assessment_history_records")
    assessment = relationship("HealthAssessment", backref="history_entries")


class HealthScoreRecord(Base):
    __tablename__ = "health_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("health_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    baseline_score = Column(Numeric(5, 2), default=100.0, nullable=False)
    nutrient_risk_deduction = Column(Numeric(5, 2), default=0.0, nullable=False)
    interaction_penalty = Column(Numeric(5, 2), default=0.0, nullable=False)
    lifestyle_modifier = Column(Numeric(5, 2), default=0.0, nullable=False)
    confidence_adjustment = Column(Numeric(5, 2), default=0.0, nullable=False)
    deficiency_count = Column(Integer, default=0, nullable=False)
    protective_factor_count = Column(Integer, default=0, nullable=False)
    interpretation = Column(Text, nullable=False)
    breakdown_json = Column(JSONB, default=dict, nullable=False)
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="health_score_records")
    assessment = relationship("HealthAssessment", backref="health_score_entries")


class ProgressMetric(Base):
    __tablename__ = "progress_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    current_assessment_id = Column(UUID(as_uuid=True), ForeignKey("health_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    baseline_assessment_id = Column(UUID(as_uuid=True), ForeignKey("health_assessments.id", ondelete="SET NULL"), nullable=True)
    previous_assessment_id = Column(UUID(as_uuid=True), ForeignKey("health_assessments.id", ondelete="SET NULL"), nullable=True)
    health_score_delta = Column(Integer, default=0, nullable=False)
    recovery_velocity = Column(Numeric(5, 2), default=0.0, nullable=False)
    deficiencies_resolved = Column(Integer, default=0, nullable=False)
    emerging_risks = Column(Integer, default=0, nullable=False)
    most_improved_nutrient = Column(String(100), nullable=True)
    highest_risk_nutrient = Column(String(100), nullable=True)
    fastest_recovery_nutrient = Column(String(100), nullable=True)
    nutrient_progress = Column(JSONB, default=dict, nullable=False)
    lifestyle_progress = Column(JSONB, default=dict, nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="progress_metric_records")
    current_assessment = relationship("HealthAssessment", foreign_keys=[current_assessment_id], backref="current_progress_metrics")
