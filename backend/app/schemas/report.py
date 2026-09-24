"""
Report & Dashboard Schemas
Phase 6: Comprehensive Nutritional Report Generation and Health Dashboard

Defines Pydantic V2 models for:
- Overall Nutritional Health Score (0-100) and category breakdown
- Assessment summary and key clinical findings
- 11-nutrient prediction summary
- Nutrient interaction reporting and actionable alerts
- Dashboard visualization contracts and SVG charts (Radar, Bar, Priority, SHAP, Graph, Timeline)
- Generated report responses and PDF download endpoints
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class HealthScoreCategoryEnum(str, Enum):
    EXCELLENT = "EXCELLENT"          # 90 - 100
    GOOD = "GOOD"                    # 75 - 89
    MODERATE_RISK = "MODERATE_RISK"  # 60 - 74
    HIGH_RISK = "HIGH_RISK"          # 40 - 59
    CRITICAL = "CRITICAL"            # 0 - 39


class HealthScoreBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    baseline_score: float = Field(default=100.0, description="Theoretical optimal baseline score")
    nutrient_risk_deduction: float = Field(..., description="Points deducted for predicted nutrient deficiencies")
    interaction_penalty: float = Field(..., description="Compounding penalty from active biochemical interactions")
    lifestyle_modifier: float = Field(..., description="Positive/negative net adjustment for lifestyle & dietary habits")
    confidence_adjustment: float = Field(default=0.0, description="Deduction moderation based on model confidence")
    deficiency_count: int = Field(default=0, description="Count of identified nutrient deficiencies")
    protective_factor_count: int = Field(default=0, description="Count of active protective lifestyle factors")
    final_score: int = Field(..., ge=0, le=100, description="Overall Nutritional Health Score (0-100)")
    category: HealthScoreCategoryEnum = Field(..., description="Clinical health score category tier")
    interpretation: str = Field(..., description="Actionable clinical interpretation of the score")


class AssessmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assessment_date: datetime = Field(..., description="Timestamp of the screening assessment")
    user_profile: Dict[str, Any] = Field(..., description="Summary of user demographics, BMI, dietary pattern")
    key_findings: List[str] = Field(..., description="Bullet point clinical highlights")
    top_risk_nutrients: List[str] = Field(..., description="Primary flagged nutrient deficiencies")
    protective_factors: List[str] = Field(..., description="Positive dietary/lifestyle habits counteracting risk")
    critical_lifestyle_factors: List[str] = Field(..., description="Behavioral bottlenecks requiring intervention")
    executive_summary_text: str = Field(..., description="Comprehensive clinical narrative for patient/practitioner")


class PredictionSummaryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nutrient: str = Field(..., description="Target nutrient name")
    probability: float = Field(..., ge=0.0, le=1.0, description="Predicted probability of deficiency")
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH, or SEVERE")
    confidence_level: str = Field(..., description="Model prediction confidence assessment (HIGH, MEDIUM, LOW)")
    clinical_implication: str = Field(..., description="Clinical physiological relevance")


class NutrientInteractionReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nutrients: List[str] = Field(..., description="Interacting nutrient pair, e.g. ['Vitamin D', 'Calcium']")
    interaction_type: str = Field(..., description="SYNERGISTIC, COMPETITIVE, INHIBITORY, CO-FACTOR")
    clinical_relevance: str = Field(..., description="Biochemical mechanism of action")
    impact_level: str = Field(..., description="HIGH, MODERATE, or MILD")
    suggested_action: str = Field(..., description="Concrete clinical / dietary recommendation")


class DashboardVisualizationsBundle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    radar_chart: Dict[str, Any] = Field(..., description="Nutrient Risk Radar Chart (data coordinates + SVG)")
    bar_chart: Dict[str, Any] = Field(..., description="Nutrient Risk Bar Chart (data coordinates + SVG)")
    priority_ranking_chart: Dict[str, Any] = Field(..., description="Deficiency Priority Ranking Chart (data + SVG)")
    shap_importance_chart: Dict[str, Any] = Field(..., description="SHAP Feature Importance Chart (data + SVG)")
    interaction_graph: Dict[str, Any] = Field(..., description="Nutrient Interaction Network Graph (nodes, edges + SVG)")
    recovery_timeline: Dict[str, Any] = Field(..., description="Recovery Progress Timeline (milestones + SVG)")


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assessment_id: Union[uuid.UUID, str] = Field(..., description="Assessment identifier")
    user_id: Optional[Union[uuid.UUID, str]] = Field(default=None, description="User identifier if authenticated")
    overall_health_score: int = Field(..., ge=0, le=100, description="Nutritional Health Score (0-100)")
    health_score_category: HealthScoreCategoryEnum = Field(..., description="Category tier")
    score_breakdown: HealthScoreBreakdown = Field(..., description="Component breakdown of health score")
    overall_risk_classification: str = Field(..., description="Overall risk status (LOW, MODERATE, HIGH, SEVERE)")
    nutrient_risk_distribution: Dict[str, int] = Field(..., description="Counts of nutrients in LOW, MODERATE, HIGH, SEVERE")
    deficiency_priority_ranking: List[Dict[str, Any]] = Field(..., description="Ordered list of nutrients by priority")
    nutrient_interaction_alerts: List[NutrientInteractionReportItem] = Field(..., description="Active interaction alerts")
    recovery_progress_indicators: Dict[str, Any] = Field(..., description="Indicators for 7, 14, 30-day goals")
    visualizations: DashboardVisualizationsBundle = Field(..., description="Interactive chart contracts and SVGs")
    predictions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Per-nutrient predictions")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class GenerateReportRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assessment_id: Union[uuid.UUID, str] = Field(..., description="Assessment ID to generate the report from")
    report_title: Optional[str] = Field(default="Comprehensive Nutritional Assessment Report", description="Custom title")
    export_pdf: bool = Field(default=True, description="Whether to pre-generate downloadable PDF export")


class GeneratedReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Generated Report UUID")
    user_id: uuid.UUID = Field(..., description="Owner User UUID")
    assessment_id: uuid.UUID = Field(..., description="Linked Health Assessment UUID")
    report_title: str = Field(..., description="Report title")
    status: str = Field(default="COMPLETED", description="Report status: PENDING, COMPLETED, FAILED")
    overall_health_score: int = Field(..., ge=0, le=100, description="Score 0-100")
    health_score_category: str = Field(..., description="Score Category")
    summary_text: str = Field(..., description="Executive summary text")
    report_summary: Optional[str] = Field(default=None, description="Alias for summary_text")
    pdf_file_url: Optional[str] = Field(default=None, description="API endpoint URL to download PDF")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    report_payload: Dict[str, Any] = Field(..., description="Full JSON snapshot of the report")


# =============================================================================
# Phase 6: Longitudinal Progress Tracking, Recovery & Analytics Schemas
# =============================================================================

class RecoveryTrendEnum(str, Enum):
    IMPROVING = "Improving"
    STABLE = "Stable"
    DECLINING = "Declining"
    CRITICAL = "Critical"


class RecoveryStatusEnum(str, Enum):
    RESOLVED = "Resolved"
    ON_TRACK = "On Track"
    NEEDS_ATTENTION = "Needs Attention"
    ACTION_REQUIRED = "Action Required"


class NutrientRecoveryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nutrient: str = Field(..., description="Nutrient name")
    initial_risk_score: float = Field(..., description="Baseline risk score (0-100%)")
    current_risk_score: float = Field(..., description="Current evaluated risk score (0-100%)")
    improvement_percentage: float = Field(..., description="Percentage improvement relative to baseline")
    recovery_trend: str = Field(..., description="Improving, Stable, Declining, Critical")
    recovery_status: str = Field(..., description="Resolved, On Track, Needs Attention, Action Required")
    initial_risk_level: str = Field(default="HIGH", description="Initial risk level category")
    current_risk_level: str = Field(default="MODERATE", description="Current risk level category")
    recommended_action: str = Field(default="", description="Clinical guidance or dietary adjustment")


class AssessmentHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="History record UUID")
    assessment_id: uuid.UUID = Field(..., description="Linked health assessment UUID")
    assessment_number: int = Field(..., description="Sequential assessment sequence (1, 2, 3...)")
    date: str = Field(..., description="ISO formatted assessment date")
    version: str = Field(default="v1.0", description="Assessment version")
    health_score: int = Field(..., ge=0, le=100, description="Overall health score (0-100)")
    health_category: str = Field(..., description="Health category tier")
    risk_distribution: Dict[str, int] = Field(default_factory=dict, description="Risk level counts")
    deficiency_count: int = Field(default=0, description="Number of active deficiencies")
    status: str = Field(default="COMPLETED", description="Assessment status")
    pdf_file_url: Optional[str] = Field(default=None, description="Download URL for historical report")


class AssessmentHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(..., description="User UUID")
    total_assessments: int = Field(..., description="Total historical screenings recorded")
    history: List[AssessmentHistoryItem] = Field(default_factory=list, description="Ordered assessment history")


class ProgressSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(..., description="User UUID")
    current_health_score: int = Field(..., ge=0, le=100)
    baseline_health_score: int = Field(default=0, ge=0, le=100)
    health_score_delta: int = Field(..., description="Point change from baseline assessment")
    health_score_improvement_pct: float = Field(..., description="Percentage improvement")
    recovery_velocity_pts_per_week: float = Field(..., description="Velocity of health score recovery per week")
    deficiencies_resolved_count: int = Field(..., description="Number of previously deficient nutrients now restored")
    emerging_risks_count: int = Field(..., description="Number of new nutrients with rising risk")
    most_improved_nutrient: str = Field(..., description="Nutrient with highest percentage risk reduction")
    highest_risk_nutrient: str = Field(..., description="Nutrient currently possessing highest risk score")
    fastest_recovery_trend: str = Field(..., description="Nutrient with most rapid improvement curve")
    newly_emerging_risks: List[str] = Field(default_factory=list, description="List of nutrients requiring preventive focus")
    lifestyle_improvements: List[str] = Field(default_factory=list, description="Positive behavioral improvements tracked")
    nutrient_recovery_tracking: List[NutrientRecoveryItem] = Field(default_factory=list, description="Per-nutrient recovery monitoring")


class ProgressTrendsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(..., description="User UUID")
    historical_timeline: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological trend points")
    nutrient_trajectories: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict, description="Time series per nutrient")


class AssessmentComparisonItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nutrient: str = Field(..., description="Target nutrient")
    base_probability: float = Field(..., description="Baseline assessment probability")
    base_risk_score: int = Field(..., description="Baseline risk score (e.g. 87%)")
    target_probability: float = Field(..., description="Current/Comparison assessment probability")
    target_risk_score: int = Field(..., description="Current/Comparison risk score (e.g. 52%)")
    absolute_change: int = Field(..., description="Risk point delta (e.g. -35%)")
    relative_change_pct: float = Field(..., description="Relative percentage change")
    trend: str = Field(..., description="Improving, Stable, Declining, Critical")
    status: str = Field(..., description="Status summary")


class AssessmentComparisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(..., description="User identifier")
    base_assessment_id: uuid.UUID = Field(..., description="Earlier comparison baseline UUID")
    base_date: str = Field(..., description="Baseline screening date")
    base_health_score: int = Field(..., description="Baseline overall health score")
    target_assessment_id: uuid.UUID = Field(..., description="Current/Target assessment UUID")
    target_date: str = Field(..., description="Target screening date")
    target_health_score: int = Field(..., description="Target overall health score")
    overall_score_delta: int = Field(..., description="Health score improvement points")
    nutrient_comparisons: List[AssessmentComparisonItem] = Field(default_factory=list, description="Side-by-side nutrient differences")
    key_health_insights: List[str] = Field(default_factory=list, description="AI-generated clinical progress highlights")
    improvement_summary: str = Field(..., description="Executive narrative of recovery journey")


class AnalyticsHealthScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(..., description="User UUID")
    current_score: int = Field(..., ge=0, le=100)
    health_score: Optional[int] = Field(default=None, description="Direct alias for current_score for frontend consistency")
    category: str = Field(..., description="Health score category")
    breakdown: HealthScoreBreakdown = Field(..., description="Detailed score component breakdown")
    historical_scores: List[Dict[str, Any]] = Field(default_factory=list, description="Historical score entries")
    lifestyle_influence_score: float = Field(default=0.0, description="Net lifestyle habit contribution")
    has_assessment: bool = Field(default=True, description="Indicates whether an assessment was evaluated")
    hasAssessment: Optional[bool] = Field(default=True, description="CamelCase alias for frontend compatibility")


class AnalyticsRecoveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(..., description="User UUID")
    average_recovery_rate: float = Field(..., description="Mean improvement across all monitored nutrients")
    recovery_velocity_weekly: float = Field(..., description="Points improved per week")
    deficiencies_resolved: int = Field(..., description="Count of resolved deficiencies")
    active_recovery_plans_count: int = Field(default=1)
    nutrient_recovery_list: List[NutrientRecoveryItem] = Field(default_factory=list)


class AnalyticsNutrientTrendsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(..., description="User UUID")
    nutrients_monitored: List[str] = Field(default_factory=list)
    trends: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Summary stats and trends per nutrient")

