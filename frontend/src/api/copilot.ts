import api from '../lib/api'

export interface PatientDemographics {
  patient_id: string
  full_name: string
  age: number
  gender: string
  bmi: number
  dietary_pattern: string
  meals_per_day: number
  activity_level: string
  sunlight_exposure_min: number
  sleep_hours: number
  stress_level: number
  smoking_status: string
  alcohol_consumption: string
}

export interface DeficiencyItem {
  nutrient: string
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL'
  probability: number
  percentile: number
  confidence_score: number
  primary_symptom_matches: string[]
}

export interface BiomarkerItem {
  marker_name: string
  value: number
  unit: string
  reference_range: string
  status: 'LOW' | 'OPTIMAL' | 'HIGH' | 'BORDERLINE'
}

export interface SymptomItem {
  symptom: string
  severity: number
  duration_weeks?: number
  affected_systems: string[]
}

export interface OutcomeTrajectory {
  baseline_health_score: number
  current_health_score: number
  adherence_percentage: number
  projected_recovery_weeks: number
  trajectory_status: 'IMPROVING' | 'STABLE' | 'DECLINING'
}

export interface PrecisionIntervention {
  category: 'FOOD' | 'SUPPLEMENT' | 'LIFESTYLE'
  title: string
  dosage_or_serving: string
  frequency: string
  biochemical_mechanism: string
  safety_notes?: string
}

export interface UnifiedPatientDossier {
  dossier_id: string
  generated_at: string
  demographics: PatientDemographics
  deficiencies: DeficiencyItem[]
  biomarkers: BiomarkerItem[]
  symptoms: SymptomItem[]
  outcomes: OutcomeTrajectory
  precision_foods: PrecisionIntervention[]
  supplement_plan: PrecisionIntervention[]
  composite_risk_score: number
  top_shap_features: Array<{ feature: string; attribution: number; interpretation?: string }>
  safety_governance_alerts: string[]
}

export interface ClinicalAssessmentReport {
  assessment_id: string
  patient_id: string
  created_at: string
  executive_summary: string
  clinical_findings: string[]
  deficiency_risk_summary: Record<string, any>
  contributing_factors: Array<{ factor: string; details: string; impact: string }>
  recommended_actions: Array<{ action: string; priority: string; rationale: string }>
  monitoring_plan: Record<string, any>
  follow_up_recommendations: string[]
  is_signed_off: boolean
  reviewer_notes?: string
}

export interface SOAPNoteResponse {
  note_id: string
  patient_id: string
  patient_name: string
  created_at: string
  subjective: Record<string, any>
  objective: Record<string, any>
  assessment: Record<string, any>
  plan: Record<string, any>
  formatted_text: string
}

export interface CompetingCause {
  etiology: string
  likelihood: 'HIGH' | 'MODERATE' | 'LOW'
  clinical_rationale: string
  distinguishing_features: string
}

export interface DifferentialReasoningItem {
  nutrient: string
  predicted_probability: number
  confidence_score: number
  uncertainty_interval: [number, number]
  primary_suspected_cause: string
  competing_causes: CompetingCause[]
  confirmatory_diagnostics: Array<{ lab_test: string; clinical_purpose: string; target_cutoff: string }>
  clinical_uncertainty_explanation: string
}

export interface DifferentialDiagnosticReport {
  report_id: string
  patient_id: string
  generated_at: string
  differential_evaluations: DifferentialReasoningItem[]
}

export interface ClinicianReviewRecord {
  id: string
  assessment_id: string
  clinician_id: string
  clinician_name: string
  license_number: string
  decision: 'APPROVED' | 'MODIFIED' | 'REJECTED'
  notes?: string
  signed_at: string
}

async function withRetry<T>(fn: () => Promise<T>, retries = 2, delayMs = 600): Promise<T> {
  let lastError: any
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn()
    } catch (err: any) {
      lastError = err
      if (attempt < retries && (!err.response || err.response.status >= 500)) {
        await new Promise(res => setTimeout(res, delayMs * Math.pow(2, attempt)))
      } else {
        break
      }
    }
  }
  throw lastError
}

export const copilotApi = {
  getPatientIntelligence: async (payload: Record<string, any>): Promise<UnifiedPatientDossier> => {
    return withRetry(async () => {
      const res = await api.post<UnifiedPatientDossier>('/copilot/patient-intelligence', payload)
      return res.data
    })
  },

  generateClinicalAssessment: async (payload: Record<string, any>): Promise<ClinicalAssessmentReport> => {
    return withRetry(async () => {
      const res = await api.post<ClinicalAssessmentReport>('/copilot/clinical-assessment', payload)
      return res.data
    })
  },

  generateSOAPNote: async (payload: Record<string, any>): Promise<SOAPNoteResponse> => {
    return withRetry(async () => {
      const res = await api.post<SOAPNoteResponse>('/copilot/soap-note', payload)
      return res.data
    })
  },

  getDifferentialReasoning: async (payload: Record<string, any>): Promise<DifferentialDiagnosticReport> => {
    return withRetry(async () => {
      const res = await api.post<DifferentialDiagnosticReport>('/copilot/differential-reasoning', payload)
      return res.data
    })
  },

  submitClinicianSignOff: async (payload: {
    assessment_id: string
    clinician_name: string
    license_number: string
    decision: 'APPROVED' | 'MODIFIED' | 'REJECTED'
    notes?: string
  }): Promise<ClinicianReviewRecord> => {
    const res = await api.post<ClinicianReviewRecord>('/copilot/sign-off', payload)
    return res.data
  },

  getClinicianReviews: async (assessmentId: string): Promise<ClinicianReviewRecord[]> => {
    const res = await api.get<ClinicianReviewRecord[]>(`/copilot/reviews/${assessmentId}`)
    return res.data
  },
}
