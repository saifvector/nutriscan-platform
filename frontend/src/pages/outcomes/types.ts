/* ═══════════════════════════════════════════════════════════════════════════
   Phase 9: Outcome Learning & Adaptive Nutrition Intelligence
   Exact TypeScript Interfaces matching Backend Pydantic Schemas
   ═══════════════════════════════════════════════════════════════════════════ */

export interface MissedItem {
  type?: string;
  name?: string;
  nutrient_impact?: string;
  intervention_type?: string;
  reason?: string;
  deficiency_risk?: string;
}

export interface AdherenceLogItem {
  id: string;
  assessment_id: string;
  log_date: string;
  daily_adherence_score: number;
  adherence_tier: string;
  meal_adherence_pct: number;
  supplement_adherence_pct: number;
  lifestyle_adherence_pct: number;
  hydration_liters: number;
  sunlight_minutes: number;
  sleep_hours: number;
  exercise_minutes: number;
  missed_items: string[];
  recovery_impact_estimate: string;
}

export interface AdherenceSummaryResponse {
  assessment_id: string;
  daily_adherence_score: number;
  weekly_adherence_score: number;
  monthly_adherence_score: number;
  overall_adherence_tier: string;
  compliance_breakdown: Record<string, number>;
  missed_interventions: string[];
  adherence_trend_analysis: string;
  recovery_impact_estimation: string;
  recent_logs: AdherenceLogItem[];
  // Support both property names for safety
  overall_adherence_score?: number;
  adherence_tier?: 'OPTIMAL' | 'MODERATE' | 'POOR';
  meal_plan_adherence_pct?: number;
  supplement_adherence_pct?: number;
  lifestyle_adherence_pct?: number;
  hydration_compliance_pct?: number;
  sunlight_compliance_pct?: number;
  sleep_compliance_pct?: number;
  projected_delay_days?: number;
  streak_days?: number;
}

export interface SymptomProgressItem {
  symptom_name: string;
  baseline_severity: number;
  current_severity: number;
  delta_change: number;
  percentage_improvement: number;
  status: string;
  weekly_recovery_velocity: number;
  forecast_days_to_resolution?: number | null;
}

export interface SymptomTimelineResponse {
  assessment_id: string;
  overall_symptom_score: number;
  symptom_recovery_score: number;
  symptoms_tracked_count: number;
  improving_count: number;
  resolved_count: number;
  symptom_progress: SymptomProgressItem[];
  clinical_summary: string;
  historical_curve_points: Array<Record<string, any>>;
}

export interface BiomarkerComparisonItem {
  biomarker_name: string;
  unit: string;
  baseline_value: number;
  current_value: number;
  optimal_range: string;
  delta_value: number;
  percentage_change: number;
  status: string;
  clinical_significance: string;
}

export interface LabTrackingResponse {
  assessment_id: string;
  test_date: string;
  biomarkers: BiomarkerComparisonItem[];
  overall_lab_adequacy_score: number;
  clinical_interpretation: string;
}

export interface RecoveryStatusResponse {
  assessment_id: string;
  baseline_health_score: number;
  current_health_score: number;
  health_score_delta: number;
  recovery_velocity_pts_per_week: number;
  recovery_status: string;
  days_in_protocol: number;
  projected_full_recovery_date: string;
  overall_improvement_percentage: number;
  clinical_progress_summary: string;
}

export interface InterventionEffectivenessItem {
  intervention_id: string;
  intervention_type: 'FOOD' | 'SUPPLEMENT' | 'LIFESTYLE';
  name: string;
  target_deficiency: string;
  effectiveness_score: number;
  clinical_impact_score: number;
  recovery_contribution_score: number;
  adherence_rate: number;
  response_rate: string;
  classification: 'ACCELERATOR' | 'EFFECTIVE' | 'NEUTRAL' | 'BOTTLENECK';
}

export interface EffectivenessResponse {
  assessment_id: string;
  overall_effectiveness_score: number;
  top_effective_foods: InterventionEffectivenessItem[];
  top_effective_supplements: InterventionEffectivenessItem[];
  top_effective_lifestyle: InterventionEffectivenessItem[];
  recovery_accelerators: InterventionEffectivenessItem[];
  recovery_bottlenecks: InterventionEffectivenessItem[];
  intervention_response_summary: string;
}

export interface AdaptiveRecommendationItem {
  adaptation_id: string;
  scenario_category: string;
  trigger_reason: string;
  original_guidance: string;
  adapted_guidance: string;
  alternative_interventions: string[];
  adaptation_logic: string;
  expected_recovery_acceleration: string;
  is_active: boolean;
}

export interface AdaptivePlanResponse {
  assessment_id: string;
  has_active_adaptations: boolean;
  adaptation_event_count: number;
  active_adaptations: AdaptiveRecommendationItem[];
  updated_recovery_plan: Record<string, any>;
  adaptation_audit_log: Array<Record<string, any>>;
}

export interface MilestoneAccuracyItem {
  milestone_day: number;
  predicted_health_score: number;
  actual_health_score: number;
  absolute_error: number;
  accuracy_percentage: number;
  within_confidence_band: boolean;
}

export interface PredictionAccuracyResponse {
  assessment_id: string;
  overall_prediction_accuracy_pct: number;
  projection_mean_absolute_error: number;
  confidence_calibration_score: number;
  model_reliability_score: number;
  calibration_status: string;
  milestone_evaluations: MilestoneAccuracyItem[];
  clinical_model_report: string;
}

export interface EarlyWarningFlagItem {
  flag_id: string;
  flag_type: string;
  severity_level: string;
  headline: string;
  clinical_description: string;
  recommended_corrective_action: string;
}

export interface RelapseRiskResponse {
  assessment_id: string;
  relapse_probability_score: number;
  overall_risk_level: string;
  early_warning_flags: EarlyWarningFlagItem[];
  intervention_alerts: string[];
  surveillance_summary: string;
}

export interface AdherenceLogPayload {
  assessment_id: string;
  log_date?: string;
  meal_adherence_pct: number;
  supplement_adherence_pct: number;
  lifestyle_adherence_pct: number;
  hydration_liters?: number;
  sunlight_minutes?: number;
  sleep_hours?: number;
  exercise_minutes?: number;
  missed_items?: string[];
  logged_items?: string[];
  notes?: string;
}

export interface SymptomLogPayload {
  assessment_id: string;
  recorded_date?: string;
  symptoms: Record<string, number>;
  notes?: string;
}
