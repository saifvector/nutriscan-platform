import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .user import Base


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("health_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    report_title = Column(String(255), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    summary_text = Column(Text, nullable=True)
    overall_health_score = Column(Integer, nullable=True)
    report_payload = Column(JSONB, default=dict, nullable=False)
    pdf_file_url = Column(String(500), nullable=True)
    generated_by = Column(String(100), default="AI_PIPELINE_ENGINE", nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reports")
    assessment = relationship("HealthAssessment", back_populates="reports")

    @property
    def report_summary(self):
        return self.summary_text

    @property
    def generated_at(self):
        return self.created_at
