import React, { useState } from 'react'
import { X, Copy, Check, ShieldCheck, Send, Terminal, Clock, AlertTriangle } from 'lucide-react'

interface SOAPNote {
  formatted_text: string
  subjective?: any
  objective?: any
  assessment?: any
  plan?: any
}

interface AuditRecord {
  review_id: string
  timestamp: string
  clinician_name: string
  clinician_role: string
  decision: string
  target_category: string
  rationale: string
  audit_hash: string
  escalation_specialty?: string
}

interface ClinicalNoteModalProps {
  isOpen: boolean
  onClose: () => void
  initialTab?: 'soap' | 'attest'
  soapNote: SOAPNote | null
  patientId: string
  patientName: string
  auditTrail: AuditRecord[]
  onSubmitReview: (decision: string, clinicianName: string, rationale: string, specialty?: string) => Promise<void>
  loading: boolean
}

export default function ClinicalNoteModal({
  isOpen,
  onClose,
  initialTab = 'soap',
  soapNote,
  patientId,
  patientName,
  auditTrail,
  onSubmitReview,
  loading
}: ClinicalNoteModalProps) {
  const [activeTab, setActiveTab] = useState<'soap' | 'attest'>(initialTab)
  const [copied, setCopied] = useState(false)

  // Review Form State
  const [clinicianName, setClinicianName] = useState('Dr. Meredith Gray, MD')
  const [decision, setDecision] = useState<'APPROVE' | 'MODIFY' | 'ESCALATE' | 'REJECT'>('APPROVE')
  const [rationale, setRationale] = useState('Clinical evaluation aligns with dietary patterns. Supplement regimen safe within NIH UL thresholds.')
  const [escalationSpecialty, setEscalationSpecialty] = useState('HEMATOLOGY')
  const [submitted, setSubmitted] = useState(false)

  if (!isOpen) return null

  const handleCopy = () => {
    if (soapNote?.formatted_text) {
      navigator.clipboard.writeText(soapNote.formatted_text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleSign = async () => {
    await onSubmitReview(
      decision,
      clinicianName,
      rationale,
      decision === 'ESCALATE' ? escalationSpecialty : undefined
    )
    setSubmitted(true)
    setTimeout(() => {
      setSubmitted(false)
      onClose()
    }, 1500)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl bg-[#0F172A] border border-slate-700/80 shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-[#111827]">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-900 border border-slate-800">
              <button
                onClick={() => setActiveTab('soap')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'soap' ? 'bg-teal-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                EHR SOAP Note
              </button>
              <button
                onClick={() => setActiveTab('attest')}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  activeTab === 'attest' ? 'bg-teal-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Clinician Sign-Off
              </button>
            </div>
            <span className="text-xs text-slate-400 font-mono hidden sm:inline">
              Patient: {patientName} ({patientId})
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {activeTab === 'soap' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-white">Synthesized EHR Documentation</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Compatible with Epic, Cerner, and AthenaHealth</p>
                </div>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy Note'}</span>
                </button>
              </div>

              {/* Formatted SOAP Quadrants */}
              {soapNote ? (
                <div className="space-y-3">
                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                    <span className="font-bold text-teal-400 uppercase tracking-wider block mb-1">Subjective (S)</span>
                    <p className="text-slate-300 leading-relaxed">
                      {soapNote.subjective?.chief_complaint || 'Chief complaint and reported symptomatic history.'}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                    <span className="font-bold text-teal-400 uppercase tracking-wider block mb-1">Objective (O)</span>
                    <p className="text-slate-300 leading-relaxed">
                      Vitals: Age {soapNote.objective?.vitals_and_anthropometrics?.age}, BMI {soapNote.objective?.vitals_and_anthropometrics?.bmi}.
                      Biomarkers: {(soapNote.objective?.laboratory_biomarkers || []).join('; ')}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                    <span className="font-bold text-teal-400 uppercase tracking-wider block mb-1">Assessment (A)</span>
                    <p className="text-slate-300 leading-relaxed">
                      Primary diagnoses: {(soapNote.assessment?.primary_diagnoses || []).join(', ')}.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
                    <span className="font-bold text-teal-400 uppercase tracking-wider block mb-1">Plan (P)</span>
                    <p className="text-slate-300 leading-relaxed">
                      Prescribed foods: {(soapNote.plan?.nutrition_prescriptions || []).join(', ')}.
                      Supplements: {(soapNote.plan?.supplementation_protocol || []).join(', ')}.
                    </p>
                  </div>

                  {/* Raw plaintext stream */}
                  <div className="pt-2">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5 flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5" />
                      <span>EMR Plaintext Stream</span>
                    </span>
                    <pre className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] text-slate-300 font-mono whitespace-pre overflow-x-auto leading-relaxed max-h-48">
                      {soapNote.formatted_text}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-500 text-xs">
                  Generating clinical SOAP note...
                </div>
              )}
            </div>
          )}

          {activeTab === 'attest' && (
            <div className="space-y-5">
              <div>
                <h3 className="text-sm font-semibold text-white">Cryptographic Review & Attestation</h3>
                <p className="text-xs text-slate-400 mt-0.5">Commits decision with SHA-256 digital signature to clinical audit trail.</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Attending Clinician</label>
                  <input
                    type="text"
                    value={clinicianName}
                    onChange={e => setClinicianName(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1.5">Action Decision</label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {[
                      { id: 'APPROVE', label: 'Approve Plan' },
                      { id: 'MODIFY', label: 'Modify Regimen' },
                      { id: 'ESCALATE', label: 'Escalate' },
                      { id: 'REJECT', label: 'Reject' }
                    ].map(btn => (
                      <button
                        key={btn.id}
                        type="button"
                        onClick={() => setDecision(btn.id as any)}
                        className={`py-2 px-2.5 rounded-lg text-xs font-medium border transition-colors ${
                          decision === btn.id
                            ? 'bg-teal-600 text-white border-teal-500'
                            : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                        }`}
                      >
                        {btn.label}
                      </button>
                    ))}
                  </div>
                </div>

                {decision === 'ESCALATE' && (
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Escalation Specialty</label>
                    <select
                      value={escalationSpecialty}
                      onChange={e => setEscalationSpecialty(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500"
                    >
                      <option value="HEMATOLOGY">Hematology (Severe Anemia / Iron Studies)</option>
                      <option value="GASTROENTEROLOGY">Gastroenterology (Malabsorption / Celiac)</option>
                      <option value="ENDOCRINOLOGY">Endocrinology (Metabolic / Parathyroid)</option>
                      <option value="NEPHROLOGY">Nephrology (Renal / Electrolytes)</option>
                    </select>
                  </div>
                )}

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Clinical Rationale & Notes</label>
                  <textarea
                    rows={3}
                    value={rationale}
                    onChange={e => setRationale(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-teal-500 leading-relaxed"
                  />
                </div>

                <button
                  onClick={handleSign}
                  disabled={loading}
                  className="w-full py-2.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-semibold text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Sign & Record in Audit Log</span>
                </button>

                {submitted && (
                  <div className="p-3 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-300 text-xs font-medium flex items-center gap-2">
                    <Check className="w-4 h-4 text-teal-400 shrink-0" />
                    <span>Attestation recorded with SHA-256 signature.</span>
                  </div>
                )}
              </div>

              {/* Prior Audit Log */}
              {auditTrail.length > 0 && (
                <div className="pt-4 border-t border-slate-800/80">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Prior Attestations ({auditTrail.length})</span>
                  </span>
                  <div className="space-y-2 max-h-36 overflow-y-auto">
                    {auditTrail.map((rec, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60 text-xs flex justify-between items-center">
                        <div>
                          <div className="font-semibold text-white">{rec.clinician_name}</div>
                          <div className="text-[11px] text-slate-400">{rec.rationale}</div>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-300 uppercase font-mono">
                            {rec.decision}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
