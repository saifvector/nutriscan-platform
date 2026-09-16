import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base


class HealthAssessment(Base):
    __tablename__ = "health_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_version = Column(String(20), default="v1.0", nullable=False)
    
    # 10 core clinical input fields
    age_at_assessment = Column(Integer, nullable=False)
    height_cm = Column(Numeric(5, 2), nullable=False)
    weight_kg = Column(Numeric(5, 2), nullable=False)
    bmi = Column(Numeric(4, 1), nullable=False)
    
    dietary_pattern = Column(String(50), nullable=False)
    meals_per_day = Column(Integer, nullable=False)
    water_intake_liters = Column(Numeric(3, 1), nullable=False)
    daily_fruit_vegetable_servings = Column(Integer, default=0, nullable=False)
    junk_food_frequency = Column(String(50), nullable=True)
    dietary_restrictions = Column(JSONB, default=list, nullable=False)
    
    activity_level = Column(String(50), nullable=False)
    sleep_hours_per_night = Column(Numeric(3, 1), nullable=False)
    smoking_status = Column(String(50), nullable=False)
    alcohol_consumption = Column(String(50), nullable=False)
    sunlight_exposure_min_per_day = Column(Integer, default=15, nullable=False)
    stress_level = Column(Integer, nullable=False)
    
    symptoms = Column(JSONB, default=dict, nullable=False) # GIN indexed in schema.sql
    medical_history = Column(JSONB, default=list, nullable=False)
    supplement_usage = Column(JSONB, default=list, nullable=False)
    
    feature_vector = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="assessments")
    predictions = relationship("NutrientPrediction", back_populates="assessment", cascade="all, delete-orphan")
    reports = relationship("GeneratedReport", back_populates="assessment", cascade="all, delete-orphan")
