/**
 * NutriScan Clinical Session Manager
 * Enforces explicit clinical session lifecycle:
 * - Stores strictly: active_assessment_id, assessment_created_at, assessment_status
 * - Prohibits automatic fallback to old assessments or mock data on refresh
 * - Provides clean workflow reset on "Start New Assessment"
 */

export interface ClinicalSession {
  active_assessment_id: string | null
  active_patient_name?: string | null
  assessment_created_at: string | null
  assessment_status: 'draft' | 'completed' | 'archived' | null
}

const STORAGE_KEYS = {
  ACTIVE_ID: 'nutriscan_active_assessment_id',
  ACTIVE_PATIENT_NAME: 'nutriscan_active_patient_name',
  ACTIVE_CREATED_AT: 'nutriscan_assessment_created_at',
  ACTIVE_STATUS: 'nutriscan_assessment_status',
  LAST_KNOWN_ID: 'nutriscan_last_known_assessment_id',
  LAST_KNOWN_DATE: 'nutriscan_last_known_assessment_date',
} as const

class SessionManager {
  /**
   * Retrieves current active assessment session, or null if no active session is loaded.
   */
  getActiveSession(): ClinicalSession | null {
    try {
      const activeId = sessionStorage.getItem(STORAGE_KEYS.ACTIVE_ID)
      if (!activeId) return null

      return {
        active_assessment_id: activeId,
        active_patient_name: sessionStorage.getItem(STORAGE_KEYS.ACTIVE_PATIENT_NAME),
        assessment_created_at: sessionStorage.getItem(STORAGE_KEYS.ACTIVE_CREATED_AT),
        assessment_status: (sessionStorage.getItem(STORAGE_KEYS.ACTIVE_STATUS) as ClinicalSession['assessment_status']) || 'completed',
      }
    } catch {
      return null
    }
  }

  /**
   * Sets the active assessment session and persists to last-known historical record.
   */
  setActiveSession(id: string, createdAt?: string, status: ClinicalSession['assessment_status'] = 'completed', patientName?: string | null): void {
    try {
      const dateStr = createdAt || new Date().toISOString()
      sessionStorage.setItem(STORAGE_KEYS.ACTIVE_ID, id)
      sessionStorage.setItem(STORAGE_KEYS.ACTIVE_CREATED_AT, dateStr)
      sessionStorage.setItem(STORAGE_KEYS.ACTIVE_STATUS, status || 'completed')

      if (patientName && patientName.trim()) {
        sessionStorage.setItem(STORAGE_KEYS.ACTIVE_PATIENT_NAME, patientName.trim())
      }

      // Store in localStorage purely as a historical pointer for "Resume Previous Assessment"
      localStorage.setItem(STORAGE_KEYS.LAST_KNOWN_ID, id)
      localStorage.setItem(STORAGE_KEYS.LAST_KNOWN_DATE, dateStr)
      // Clean legacy keys that may contain mock data
      this.cleanLegacyStorage()
    } catch (e) {
      console.error('Failed to set active clinical session:', e)
    }
  }

  /**
   * Checks if a previous assessment exists in storage without activating it.
   */
  getStoredPreviousAssessment(): { id: string; date: string; createdAt: string } | null {
    try {
      const id = localStorage.getItem(STORAGE_KEYS.LAST_KNOWN_ID)
      if (!id) return null
      const date = localStorage.getItem(STORAGE_KEYS.LAST_KNOWN_DATE) || new Date().toISOString()
      return { id, date, createdAt: date }
    } catch {
      return null
    }
  }

  /**
   * Clears the active session and workflow state (e.g., when user selects "Start New Assessment").
   */
  clearActiveSession(): void {
    try {
      sessionStorage.removeItem(STORAGE_KEYS.ACTIVE_ID)
      sessionStorage.removeItem(STORAGE_KEYS.ACTIVE_PATIENT_NAME)
      sessionStorage.removeItem(STORAGE_KEYS.ACTIVE_CREATED_AT)
      sessionStorage.removeItem(STORAGE_KEYS.ACTIVE_STATUS)
      sessionStorage.removeItem('prediction_result')
      this.cleanLegacyStorage()
    } catch (e) {
      console.error('Failed to clear active session:', e)
    }
  }

  /**
   * Wipes all historical assessment pointers completely.
   */
  clearAllStoredAssessments(): void {
    this.clearActiveSession()
    try {
      localStorage.removeItem(STORAGE_KEYS.LAST_KNOWN_ID)
      localStorage.removeItem(STORAGE_KEYS.LAST_KNOWN_DATE)
      this.cleanLegacyStorage()
    } catch (e) {
      console.error('Failed to clear all stored assessments:', e)
    }
  }

  /**
   * Clean out legacy storage keys that previously carried hardcoded/mock assessment data.
   */
  private cleanLegacyStorage(): void {
    try {
      localStorage.removeItem('nutriscan_active_assessment')
      localStorage.removeItem('nutriscan_assessment_id')
      localStorage.removeItem('active_assessment')
      sessionStorage.removeItem('active_assessment')
    } catch {
      // ignore
    }
  }
}

export const sessionManager = new SessionManager()
