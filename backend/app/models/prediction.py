import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .user import Base


class NutrientPrediction(Base):
    __tablename__ = "nutrient_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("health_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    nutrient_code = Column(String(50), nullable=False, index=True)
    nutrient_name = Column(String(100), nullable=False)
    probability_score = Column(Numeric(5, 4), nullable=False)
    confidence_score = Column(Numeric(5, 4), default=0.8500, nullable=False)
    confidence_level = Column(String(30), default="High Confidence", nullable=False)
    predicted_risk_level = Column(String(20), nullable=False, index=True)
    priority_rank = Column(Integer, nullable=True)
    confidence_interval_low = Column(Numeric(5, 4), nullable=True)
    confidence_interval_high = Column(Numeric(5, 4), nullable=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    inference_latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    assessment = relationship("HealthAssessment", back_populates="predictions")
    risk_factors = relationship("RiskFactor", back_populates="prediction", cascade="all, delete-orphan")
    food_recommendations = relationship("FoodRecommendation", back_populates="prediction", cascade="all, delete-orphan")


class RiskFactor(Base):
    __tablename__ = "risk_factors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("nutrient_predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    factor_category = Column(String(100), nullable=False, index=True)
    factor_name = Column(String(150), nullable=False)
    factor_description = Column(Text, nullable=False)
    impact_score = Column(Numeric(5, 4), nullable=False)
    impact_magnitude = Column(String(20), nullable=False)
    evidence_reference = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    prediction = relationship("NutrientPrediction", back_populates="risk_factors")
