/**
 * Patient API Client
 * Provides typed endpoints for patient roster search, timeline retrieval, and transactional deletion.
 */

import api from '../lib/api'

export interface PatientSummary {
  id: string
  name: string
  gender: string | null
  age: number | null
  height_cm: number | null
  weight_kg: number | null
  bmi: number | null
  dietary_pattern: string | null
  created_at: string
  updated_at: string
  assessment_count: number
  latest_assessment_date: string | null
  latest_assessment_id: string | null
  latest_risk_score: number | null
  latest_risk_level: string | null
  flagged_nutrients_count: number
}

export interface DeficiencyItem {
  nutrient: string
  risk_level: string
  probability: number
  confidence: number
  status: string
}

export interface TreatmentItem {
  type: string
  title: string
  reason: string
}

export interface TimelineEntry {
  assessment_id: string
  date: string
  formatted_date: string
  age_at_assessment: number
  risk_score: number
  risk_level: string
  flagged_deficiencies: DeficiencyItem[]
  flagged_count: number
  treatments: TreatmentItem[]
}

export interface PatientTimelineData {
  patient: {
    id: string
    name: string
    gender: string | null
    age: number | null
    height_cm: number | null
    weight_kg: number | null
    bmi: number | null
    dietary_pattern: string | null
    created_at: string
    updated_at: string
  }
  summary: {
    total_screenings: number
    latest_risk_score: number | null
    latest_risk_level: string
    active_deficiencies_count: number
    trajectory: string
  }
  trends: {
    dates: string[]
    risk_scores: number[]
  }
  timeline: TimelineEntry[]
}

export interface DeletePatientResponse {
  success: boolean
  patient_id: string
  patient_name: string
  deleted_assessments_count: number
  message: string
}

export interface DeleteAllPatientsResponse {
  success: boolean
  deleted_patients: number
  deleted_assessments: number
  deleted_predictions: number
  deleted_reports: number
  message: string
}

export const patientApi = {
  /**
   * Search and list patients in the registry.
   */
  async getPatients(search?: string, limit = 100, offset = 0): Promise<PatientSummary[]> {
    const res = await api.get<PatientSummary[]>('/patients', {
      params: { search: search || undefined, limit, offset },
    })
    return res.data
  },

  /**
   * Retrieve longitudinal timeline for a specific patient.
   */
  async getPatientTimeline(patientId: string): Promise<PatientTimelineData> {
    const res = await api.get<PatientTimelineData>(`/patients/${patientId}/timeline`)
    return res.data
  },

  /**
   * Transactionally delete patient and all associated clinical history.
   */
  async deletePatient(patientId: string): Promise<DeletePatientResponse> {
    const res = await api.delete<DeletePatientResponse>(`/patients/${patientId}`)
    return res.data
  },

  /**
   * Transactionally delete ALL patients, assessments, predictions, reports, and clinical records.
   */
  async deleteAllPatients(): Promise<DeleteAllPatientsResponse> {
    const res = await api.delete<DeleteAllPatientsResponse>('/patients/delete-all')
    return res.data
  },
}

export default patientApi
