import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .user import Base


class FoodRecommendation(Base):
    __tablename__ = "food_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("nutrient_predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    nutrient_name = Column(String(100), nullable=True, index=True)
    food_name = Column(String(150), nullable=False)
    food_group = Column(String(100), nullable=False, index=True)
    priority_rank = Column(Integer, default=1, nullable=True)
    recommendation_score = Column(Numeric(5, 2), nullable=True)
    serving_size = Column(String(100), nullable=False)
    nutrient_density_mg = Column(Numeric(8, 2), nullable=False)
    unit = Column(String(20), default="mg", nullable=False)
    dietary_compatibility = Column(String(50), nullable=False)
    rationale = Column(Text, nullable=True)
    preparation_tips = Column(Text, nullable=True)
    contraindications = Column(Text, nullable=True)
    evidence_source = Column(String(100), default="USDA FoodData Central / NIH ODS", nullable=True)
    evidence_strength = Column(String(20), default="Grade A", nullable=True)
    evidence_reference_url = Column(Text, default="https://ods.od.nih.gov/", nullable=True)
    triggering_risk_score = Column(Numeric(5, 2), nullable=True)
    expected_outcome = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    prediction = relationship("NutrientPrediction", back_populates="food_recommendations")
