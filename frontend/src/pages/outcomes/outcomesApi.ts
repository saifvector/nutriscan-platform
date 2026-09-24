/* ═══════════════════════════════════════════════════════════════════════════
   Phase 9: Outcome Learning & Adaptive Nutrition Intelligence
   API Service for Outcome Tracking, Adherence, Effectiveness & Adaptation
   ═══════════════════════════════════════════════════════════════════════════ */

import type {
  AdherenceSummaryResponse,
  SymptomTimelineResponse,
  LabTrackingResponse,
  RecoveryStatusResponse,
  EffectivenessResponse,
  AdaptivePlanResponse,
  PredictionAccuracyResponse,
  RelapseRiskResponse,
  AdherenceLogPayload,
  SymptomLogPayload,
} from './types';

const API_BASE = '/api/v1/outcomes';

export const outcomesApi = {
  async getAdherence(assessmentId: string, period: string = 'weekly'): Promise<AdherenceSummaryResponse> {
    const res = await fetch(`${API_BASE}/adherence?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load adherence: ${res.statusText}`);
    return res.json();
  },

  async logAdherence(payload: AdherenceLogPayload): Promise<any> {
    const res = await fetch(`${API_BASE}/log-adherence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Failed to log adherence: ${res.statusText}`);
    return res.json();
  },

  async getSymptoms(assessmentId: string): Promise<SymptomTimelineResponse> {
    const res = await fetch(`${API_BASE}/symptoms?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load symptoms: ${res.statusText}`);
    return res.json();
  },

  async logSymptoms(payload: SymptomLogPayload): Promise<SymptomTimelineResponse> {
    const res = await fetch(`${API_BASE}/log-symptoms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Failed to log symptoms: ${res.statusText}`);
    return res.json();
  },

  async getLabs(assessmentId: string): Promise<LabTrackingResponse> {
    const res = await fetch(`${API_BASE}/labs?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load labs: ${res.statusText}`);
    return res.json();
  },

  async getRecovery(assessmentId: string): Promise<RecoveryStatusResponse> {
    const res = await fetch(`${API_BASE}/recovery?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load recovery: ${res.statusText}`);
    return res.json();
  },

  async getEffectiveness(assessmentId: string): Promise<EffectivenessResponse> {
    const res = await fetch(`${API_BASE}/effectiveness?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load effectiveness: ${res.statusText}`);
    return res.json();
  },

  async getAdaptivePlans(assessmentId: string): Promise<AdaptivePlanResponse> {
    const res = await fetch(`${API_BASE}/adaptive-plans?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load adaptive plans: ${res.statusText}`);
    return res.json();
  },

  async generateAdaptation(assessmentId: string, scenario?: string, reason?: string): Promise<AdaptivePlanResponse> {
    const res = await fetch(`${API_BASE}/generate-adaptation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        assessment_id: assessmentId,
        force_scenario: scenario,
        user_feedback_notes: reason,
      }),
    });
    if (!res.ok) throw new Error(`Failed to generate adaptation: ${res.statusText}`);
    return res.json();
  },

  async getPredictionAccuracy(assessmentId: string): Promise<PredictionAccuracyResponse> {
    const res = await fetch(`${API_BASE}/prediction-accuracy?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load prediction accuracy: ${res.statusText}`);
    return res.json();
  },

  async getRiskMonitoring(assessmentId: string): Promise<RelapseRiskResponse> {
    const res = await fetch(`${API_BASE}/risk-monitoring?assessment_id=${encodeURIComponent(assessmentId)}`);
    if (!res.ok) throw new Error(`Failed to load risk monitoring: ${res.statusText}`);
    return res.json();
  },
};
