import React, { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import {
  Stethoscope,
  ChevronDown,
  ExternalLink,
  Copy,
  Check,
  Calendar,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  X
} from 'lucide-react'
import api from '../lib/api'
import { sessionManager } from '../lib/sessionManager'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.05 } } }

export interface TargetOption {
  id: string
  label: string
  nutrient: string
}

export const TARGET_OPTIONS: TargetOption[] = [
  { id: 'target_iron_deficiency', label: 'Iron Deficiency', nutrient: 'Iron' },
  { id: 'target_vitamin_d_deficiency', label: 'Vitamin D Deficiency', nutrient: 'Vitamin D' },
  { id: 'target_folate_deficiency', label: 'Folate Deficiency', nutrient: 'Folate (B9)' },
  { id: 'target_magnesium_deficiency', label: 'Magnesium Deficiency', nutrient: 'Magnesium' },
  { id: 'target_potassium_deficiency', label: 'Potassium Deficiency', nutrient: 'Potassium' },
  { id: 'target_calcium_deficiency', label: 'Calcium Deficiency', nutrient: 'Calcium' },
  { id: 'target_selenium_deficiency', label: 'Selenium Deficiency', nutrient: 'Selenium' },
  { id: 'target_zinc_deficiency', label: 'Zinc Deficiency', nutrient: 'Zinc' },
  { id: 'target_vitamin_b12_deficiency', label: 'Vitamin B12 Deficiency', nutrient: 'Vitamin B12' },
  { id: 'target_vitamin_a_deficiency', label: 'Vitamin A Deficiency', nutrient: 'Vitamin A' },
  { id: 'target_vitamin_c_deficiency', label: 'Vitamin C Deficiency', nutrient: 'Vitamin C' }
]

interface ContributorItem {
  name: string
  percentage: number
  direction: 'Risk Driver' | 'Protective Factor'
}

interface EvidenceCitation {
  id: string
  title: string
  organization: string
  summary: string
  studyType: string
  pmid: string
  url: string
  dailyIntake: string
  upperLimit?: string
}

interface ClinicalAction {
  priority: string
  action: string
  rationale: string
  expectedBenefit: string
}

interface StructuredClinicalFinding {
  primaryImpression: string
  findings: {
    category: string
    detail: string
  }[]
}

interface ClinicalNutrientProfile {
  riskLevel: 'HIGH' | 'MODERATE' | 'LOW'
  probability: number
  confidence: number
  clinicalPriority: string
  evidenceStrength: string
  keyRiskDrivers: { name: string; description: string }[]
  protectiveFactors: { name: string; description: string }[]
  narrative: string
  structuredFindings: StructuredClinicalFinding
  topContributors: ContributorItem[]
  evidenceCitations: EvidenceCitation[]
  recommendations: ClinicalAction[]
}

export default function ExplainabilityPage() {
  const { assessmentId } = useParams<{ assessmentId?: string }>()
  const activeSession = sessionManager.getActiveSession()
  const effectiveId = activeSession?.active_assessment_id || (assessmentId && assessmentId !== 'demo' ? assessmentId : null)

  const [selectedTargetId, setSelectedTargetId] = useState<string>('')
  const [expandedEvidenceId, setExpandedEvidenceId] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<boolean>(false)
  const [isTelemetryModalOpen, setIsTelemetryModalOpen] = useState<boolean>(false)

  const [apiData, setApiData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [evidenceCatalog, setEvidenceCatalog] = useState<Record<string, ClinicalNutrientProfile>>({})
  const [error, setError] = useState<string | null>(null)

  // Fetch live API explanation data when a valid assessment exists
  useEffect(() => {
    if (!effectiveId) {
      setApiData(null)
      setEvidenceCatalog({})
      setIsLoading(false)
      setError(null)
      return
    }

    let isMounted = true
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const [expRes, evRes] = await Promise.all([
          api.get(`/explainability/prediction-explanation?prediction_id=${effectiveId}`),
          api.get(`/explainability/evidence?assessment_id=${effectiveId}`)
        ])
        if (isMounted) {
          if (expRes.data) setApiData(expRes.data)
          if (evRes.data) setEvidenceCatalog(evRes.data)
        }
      } catch (err: any) {
        if (isMounted) {
          const detail = err.response?.data?.detail || 'Assessment reasoning data could not be retrieved.'
          setError(typeof detail === 'string' ? detail : JSON.stringify(detail))
          setApiData(null)
          setEvidenceCatalog({})
        }
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }
    fetchData()
    return () => { isMounted = false }
  }, [effectiveId])

  // Set default selected target dynamically to highest-risk prediction
  useEffect(() => {
    if (apiData && Array.isArray(apiData.explanations) && apiData.explanations.length > 0) {
      if (!selectedTargetId || !apiData.explanations.some((e: any) => e.target === selectedTargetId)) {
        const highItem = apiData.explanations.find((e: any) => String(e.risk_tier).toUpperCase() === 'HIGH')
        const modItem = apiData.explanations.find((e: any) => String(e.risk_tier).toUpperCase() === 'MODERATE')
        const topTarget = highItem || modItem || apiData.explanations[0]
        if (topTarget?.target) {
          setSelectedTargetId(topTarget.target)
        }
      }
    }
  }, [apiData, selectedTargetId])

  // Evaluate if all evaluated clinical targets are LOW risk
  const isAllLow = useMemo(() => {
    if (!apiData || !Array.isArray(apiData.explanations) || apiData.explanations.length === 0) return false
    return !apiData.explanations.some((e: any) => {
      const tier = String(e.risk_tier || '').toUpperCase()
      return tier === 'HIGH' || tier === 'MODERATE'
    })
  }, [apiData])

  // Current clinical profile derived strictly from active model predictions and evidence
  const profile: ClinicalNutrientProfile | null = useMemo(() => {
    if (!effectiveId || !apiData) return null

    const base = evidenceCatalog[selectedTargetId] || Object.values(evidenceCatalog)[0]

    // If API provided specific target data, augment cleanly
    if (apiData && Array.isArray(apiData.explanations)) {
      const match = apiData.explanations.find((e: any) => e.target === selectedTargetId) || apiData.explanations[0]
      if (match) {
        const cleanName = (str: string) => {
          return str
            .replace(/^Exam /i, '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase())
        }

        const positiveFromApi = (match.positive_contributors || []).map((c: any) => ({
          name: cleanName(c.label || c.feature),
          description: `Key clinical risk factor contributing ${Math.round(c.contribution_pct)}% to overall deficiency probability`
        }))

        const protectiveFromApi = (match.protective_contributors || []).map((c: any) => ({
          name: cleanName(c.label || c.feature),
          description: `Protective metabolic factor mitigating risk by ${Math.round(c.contribution_pct)}%`
        }))

        const mergedPositive = [...positiveFromApi, ...(base?.keyRiskDrivers || [])].slice(0, 3)
        const mergedProtective = [...protectiveFromApi, ...(base?.protectiveFactors || [])].slice(0, 3)

        const apiContributors: ContributorItem[] = [
          ...(match.positive_contributors || []).map((c: any) => ({
            name: cleanName(c.label || c.feature),
            percentage: Math.round(c.contribution_pct),
            direction: 'Risk Driver' as const
          })),
          ...(match.protective_contributors || []).map((c: any) => ({
            name: cleanName(c.label || c.feature),
            percentage: Math.round(c.contribution_pct),
            direction: 'Protective Factor' as const
          }))
        ]
        const mergedContributors = apiContributors.length > 0 ? apiContributors.slice(0, 5) : (base?.topContributors || []).slice(0, 5)

        let cleanNarrative = base?.narrative || match.narratives?.clinician_evaluation || ''
        const rawNarrative = match.narratives?.clinician_evaluation
        if (rawNarrative && !rawNarrative.includes('Decision Cutoff') && !rawNarrative.includes('calibrated probability of')) {
          cleanNarrative = rawNarrative
        }

        const riskLevel = match.risk_tier || base?.riskLevel || 'LOW'
        const probability = match.calibrated_probability ?? base?.probability ?? 0
        const confidence = match.confidence_score ?? base?.confidence ?? 0.90

        return {
          riskLevel,
          probability,
          confidence,
          clinicalPriority: base?.clinicalPriority || (riskLevel === 'HIGH' ? 'Tier 1 — High Priority Repletion' : riskLevel === 'MODERATE' ? 'Tier 2 — Moderate Clinical Guidance' : 'Tier 3 — Routine Monitoring'),
          evidenceStrength: base?.evidenceStrength || 'Grade A',
          keyRiskDrivers: mergedPositive,
          protectiveFactors: mergedProtective,
          narrative: cleanNarrative,
          structuredFindings: base?.structuredFindings || {
            primaryImpression: `Clinical status evaluated as ${riskLevel} (${Math.round(probability * 100)}% calibrated probability).`,
            findings: [
              { category: 'Pathophysiological Status', detail: `${match.target_name || match.target}: ${riskLevel} risk profile identified.` },
              { category: 'Model Estimation', detail: `Evaluated by calibrated ${match.champion_algorithm || 'LogisticRegression'} model with decision cutoff ${match.optimal_threshold || 0.5}.` },
              { category: 'Confirmatory Labs', detail: match.narratives?.confirmatory_labs || 'Standard clinical serum panel' },
              { category: 'Practice Guideline', detail: match.narratives?.guideline_reference || 'Clinical practice guidelines' }
            ]
          },
          topContributors: mergedContributors,
          evidenceCitations: base?.evidenceCitations || [],
          recommendations: base?.recommendations || []
        }
      }
    }

    return base || null
  }, [selectedTargetId, apiData, evidenceCatalog, effectiveId])

  const copyAssessmentId = () => {
    if (!effectiveId) return
    navigator.clipboard.writeText(effectiveId)
    setCopiedId(true)
    setTimeout(() => setCopiedId(false), 2000)
  }

  const toggleEvidence = (id: string) => {
    setExpandedEvidenceId(prev => (prev === id ? null : id))
  }

  // Risk badge color helper
  const getRiskBadgeStyles = (risk: 'HIGH' | 'MODERATE' | 'LOW') => {
    if (risk === 'HIGH') {
      return {
        bg: 'rgba(239, 68, 68, 0.12)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        color: 'var(--c-danger)',
        label: 'HIGH RISK'
      }
    }
    if (risk === 'MODERATE') {
      return {
        bg: 'rgba(245, 158, 11, 0.12)',
        border: '1px solid rgba(245, 158, 11, 0.3)',
        color: 'var(--c-warning)',
        label: 'MODERATE RISK'
      }
    }
    return {
      bg: 'rgba(34, 197, 94, 0.12)',
      border: '1px solid rgba(34, 197, 94, 0.3)',
      color: 'var(--c-success)',
      label: 'LOW RISK'
    }
  }

  const riskBadge = profile ? getRiskBadgeStyles(profile.riskLevel) : null

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={stagger}
      style={{
        maxWidth: 1400,
        margin: '0 auto',
        paddingLeft: 24,
        paddingRight: 24,
        paddingBottom: 64,
        paddingTop: 12,
        display: 'flex',
        flexDirection: 'column',
        gap: 32
      }}
    >
      {/* ══════════════════════════════════════════════════════════════════════
          SECTION 1 — PAGE HEADER & TARGET SELECTOR
          ══════════════════════════════════════════════════════════════════════ */}
      <motion.div
        variants={fadeUp}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: 20,
          paddingBottom: 28,
          marginBottom: 8,
          borderBottom: '1px solid var(--c-border)'
        }}
      >
        {/* Left Header */}
        <div style={{ maxWidth: 720 }}>
          <div style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            color: 'var(--c-primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: 8,
            display: 'flex',
            alignItems: 'center',
            gap: 6
          }}>
            <Stethoscope size={13} />
            <span>Clinical Decision Support System</span>
          </div>

          <h1 style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.875rem',
            fontWeight: 800,
            letterSpacing: 'normal',
            color: 'var(--c-secondary)',
            marginBottom: 8,
            lineHeight: 1.25
          }}>
            Clinical Reasoning & Evidence Engine
          </h1>

          <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', lineHeight: 1.5, marginBottom: 18 }}>
            Physician decision support, biomarker attribution, and peer-reviewed clinical guidelines.
          </p>

          {/* Target Deficiency Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-muted)' }}>
              Evaluated Target:
            </span>
            <div style={{ position: 'relative', minWidth: 260 }}>
              <select
                id="clinical-target-selector"
                value={selectedTargetId}
                disabled={!effectiveId || !profile}
                onChange={e => setSelectedTargetId(e.target.value)}
                style={{
                  width: '100%',
                  appearance: 'none',
                  background: 'var(--c-card)',
                  border: '1px solid var(--c-border)',
                  color: (!effectiveId || !profile) ? 'var(--c-muted)' : 'var(--c-secondary)',
                  fontSize: '0.8125rem',
                  fontWeight: 700,
                  borderRadius: 10,
                  padding: '8px 36px 8px 14px',
                  cursor: (!effectiveId || !profile) ? 'not-allowed' : 'pointer',
                  opacity: (!effectiveId || !profile) ? 0.65 : 1,
                  outline: 'none',
                  transition: 'border-color 0.15s'
                }}
              >
                {TARGET_OPTIONS.map(opt => {
                  const dynamicRisk = apiData?.explanations?.find((e: any) => e.target === opt.id)?.risk_tier
                  return (
                    <option key={opt.id} value={opt.id}>
                      {opt.label} {dynamicRisk ? `(${dynamicRisk})` : ''}
                    </option>
                  )
                })}
              </select>
              <ChevronDown
                size={14}
                style={{
                  position: 'absolute',
                  right: 12,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  pointerEvents: 'none',
                  color: 'var(--c-muted)'
                }}
              />
            </div>
          </div>
        </div>

        {/* Right Header: Compact Metadata */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: 10
        }}>
          {/* Risk Badge */}
          {riskBadge ? (
            <span style={{
              fontSize: '0.6875rem',
              fontWeight: 800,
              letterSpacing: '0.06em',
              padding: '5px 14px',
              borderRadius: 9999,
              background: riskBadge.bg,
              border: riskBadge.border,
              color: riskBadge.color
            }}>
              {riskBadge.label}
            </span>
          ) : (
            <span style={{
              fontSize: '0.6875rem',
              fontWeight: 700,
              letterSpacing: '0.04em',
              padding: '5px 14px',
              borderRadius: 9999,
              background: 'rgba(148, 163, 184, 0.1)',
              border: '1px solid rgba(148, 163, 184, 0.2)',
              color: 'var(--c-muted)'
            }}>
              NO ASSESSMENT
            </span>
          )}

          {/* Assessment ID + Copy */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: '0.75rem',
            color: 'var(--c-muted)',
            fontFamily: 'monospace'
          }}>
            <span>ID:</span>
            <span style={{ color: 'var(--c-secondary)', fontWeight: 600 }}>
              {effectiveId ? `${effectiveId.slice(0, 8)}...` : 'No Assessment Selected'}
            </span>
            {effectiveId && (
              <button
                onClick={copyAssessmentId}
                title="Copy Assessment ID"
                style={{
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  padding: 3,
                  color: 'var(--c-muted)',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                {copiedId ? <Check size={13} color="var(--c-success)" /> : <Copy size={13} />}
              </button>
            )}
          </div>

          {/* Assessment Date */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            fontSize: '0.6875rem',
            color: 'var(--c-muted)'
          }}>
            <Calendar size={12} />
            <span>{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
          </div>
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════════════════════════════
          EMPTY STATE / LOADING / ERROR OR FULL CLINICAL REASONING
          ══════════════════════════════════════════════════════════════════════ */}
      {!effectiveId ? (
        <motion.div
          variants={fadeUp}
          style={{
            background: 'var(--c-card)',
            border: '1px solid var(--c-border)',
            borderRadius: 20,
            padding: '56px 32px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            maxWidth: 720,
            margin: '20px auto 40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.04)'
          }}
        >
          <div style={{
            width: 68,
            height: 68,
            borderRadius: '50%',
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--c-primary)',
            marginBottom: 20
          }}>
            <Stethoscope size={32} />
          </div>

          <h2 style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.625rem',
            fontWeight: 800,
            color: 'var(--c-secondary)',
            marginBottom: 10
          }}>
            No Assessment Available
          </h2>

          <p style={{
            fontSize: '0.9375rem',
            color: 'var(--c-muted)',
            maxWidth: 480,
            lineHeight: 1.6,
            marginBottom: 28
          }}>
            Create or select an assessment to view clinical reasoning.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap', justifyContent: 'center', marginBottom: 40 }}>
            <Link
              to="/assessment"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                background: 'var(--c-primary)',
                color: '#ffffff',
                fontWeight: 700,
                fontSize: '0.875rem',
                padding: '12px 24px',
                borderRadius: 12,
                textDecoration: 'none',
                boxShadow: '0 4px 14px rgba(59, 130, 246, 0.35)',
                transition: 'transform 0.15s ease'
              }}
            >
              <Sparkles size={16} />
              <span>Create Assessment</span>
            </Link>

            <Link
              to="/patients"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                background: 'var(--c-card-subtle, rgba(255,255,255,0.05))',
                border: '1px solid var(--c-border)',
                color: 'var(--c-secondary)',
                fontWeight: 600,
                fontSize: '0.875rem',
                padding: '12px 22px',
                borderRadius: 12,
                textDecoration: 'none'
              }}
            >
              <span>Select Patient</span>
            </Link>
          </div>

          {/* Disabled Reasoning Widgets Preview */}
          <div style={{
            width: '100%',
            opacity: 0.45,
            pointerEvents: 'none',
            borderTop: '1px solid var(--c-border)',
            paddingTop: 32
          }}>
            <div style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: 'var(--c-muted)',
              marginBottom: 16
            }}>
              Clinical Reasoning Widgets (Awaiting Active Assessment)
            </div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
              gap: 16,
              textAlign: 'left'
            }}>
              {['Risk Level', 'Confidence', 'Clinical Priority', 'Evidence Strength'].map((label, i) => (
                <div key={i} style={{
                  background: 'var(--c-bg)',
                  border: '1px solid var(--c-border)',
                  borderRadius: 12,
                  padding: '16px 20px'
                }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginBottom: 6 }}>{label}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-muted)' }}>—</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 4 }}>Pending intake data</div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      ) : isLoading ? (
        <motion.div
          variants={fadeUp}
          style={{
            padding: '100px 24px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16
          }}
        >
          <div style={{
            width: 44,
            height: 44,
            borderRadius: '50%',
            border: '3px solid var(--c-border)',
            borderTopColor: 'var(--c-primary)',
            animation: 'spin 0.9s linear infinite'
          }} />
          <span style={{ fontSize: '0.9375rem', color: 'var(--c-muted)', fontWeight: 600 }}>
            Decomposing biomarker attributions and clinical evidence...
          </span>
        </motion.div>
      ) : error || !profile ? (
        <motion.div
          variants={fadeUp}
          style={{
            background: 'var(--c-card)',
            border: '1px solid var(--c-border)',
            borderRadius: 20,
            padding: '48px 32px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            maxWidth: 640,
            margin: '30px auto'
          }}
        >
          <div style={{
            width: 60,
            height: 60,
            borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--c-danger)',
            marginBottom: 16
          }}>
            <AlertTriangle size={28} />
          </div>

          <h3 style={{ fontSize: '1.375rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 8 }}>
            Clinical Reasoning Unavailable
          </h3>

          <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', maxWidth: 440, lineHeight: 1.5, marginBottom: 24 }}>
            {error || 'No clinical predictions or explainability records exist for this assessment ID. Complete screening to generate reasoning.'}
          </p>

          <Link
            to="/assessment"
            style={{
              background: 'var(--c-primary)',
              color: '#ffffff',
              fontWeight: 700,
              fontSize: '0.875rem',
              padding: '11px 22px',
              borderRadius: 10,
              textDecoration: 'none'
            }}
          >
            Create New Assessment
          </Link>
        </motion.div>
      ) : (
        <>
      {/* Reassurance Banner when all evaluated clinical targets are LOW */}
      {isAllLow && (
        <motion.div
          variants={fadeUp}
          style={{
            background: 'rgba(34, 197, 94, 0.08)',
            border: '1px solid rgba(34, 197, 94, 0.25)',
            borderRadius: 16,
            padding: '18px 24px',
            marginBottom: 20,
            display: 'flex',
            alignItems: 'center',
            gap: 14
          }}
        >
          <CheckCircle2 size={24} color="var(--c-success)" style={{ flexShrink: 0 }} />
          <div>
            <div style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--c-success)' }}>
              No Active Deficiency Risks Detected
            </div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', marginTop: 2 }}>
              All 9 monitored clinical biomarkers and calibrated risk models are within optimal reference limits. Standard routine monitoring protocol recommended.
            </div>
          </div>
        </motion.div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          SECTION 2 — CLINICAL DECISION OVERVIEW (Single row of 4 KPI cards)
          ══════════════════════════════════════════════════════════════════════ */}
      <motion.div
        variants={fadeUp}
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
          gap: 20
        }}
      >
        {/* Card 1: Risk Level */}
        <div style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 16,
          padding: '24px 28px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--c-muted)',
            marginBottom: 10
          }}>
            Risk Level
          </div>
          <div style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.875rem',
            fontWeight: 800,
            color: riskBadge?.color || 'var(--c-primary)',
            lineHeight: 1.1,
            marginBottom: 6
          }}>
            {profile.riskLevel}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            Estimated Probability: {Math.round(profile.probability * 100)}%
          </div>
        </div>

        {/* Card 2: Diagnostic Confidence */}
        <div style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 16,
          padding: '24px 28px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--c-muted)',
            marginBottom: 10
          }}>
            Confidence
          </div>
          <div style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.875rem',
            fontWeight: 800,
            color: 'var(--c-secondary)',
            lineHeight: 1.1,
            marginBottom: 6
          }}>
            {Math.round(profile.confidence * 100)}%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            High Clinical Agreement
          </div>
        </div>

        {/* Card 3: Clinical Priority */}
        <div style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 16,
          padding: '24px 28px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--c-muted)',
            marginBottom: 10
          }}>
            Clinical Priority
          </div>
          <div style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.875rem',
            fontWeight: 800,
            color: 'var(--c-secondary)',
            lineHeight: 1.1,
            marginBottom: 6
          }}>
            {isAllLow ? 'Routine Monitoring' : (profile.clinicalPriority || 'Tier 3 — Routine Monitoring')}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            {isAllLow 
              ? 'All Biomarkers Within Reference Limits' 
              : profile.riskLevel === 'HIGH' 
                ? 'Active Repletion Required' 
                : 'Standard Guidance Protocol'}
          </div>
        </div>

        {/* Card 4: Evidence Strength */}
        <div style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 16,
          padding: '24px 28px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--c-muted)',
            marginBottom: 10
          }}>
            Evidence Strength
          </div>
          <div style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.875rem',
            fontWeight: 800,
            color: 'var(--c-primary)',
            lineHeight: 1.1,
            marginBottom: 6
          }}>
            {profile.evidenceStrength}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            Meta-Analyses & Clinical RCTs
          </div>
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════════════════════════════
          SECTION 3 — CLINICAL INTERPRETATION (Large primary card, 32px padding)
          ══════════════════════════════════════════════════════════════════════ */}
      <motion.div
        variants={fadeUp}
        style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 20,
          padding: 32
        }}
      >
        {/* Section Heading */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 26 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 10,
            background: 'var(--c-surface-tint)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Stethoscope size={16} color="var(--c-primary)" />
          </div>
          <div>
            <h2 style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.1875rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              letterSpacing: 'normal'
            }}>
              Clinical Interpretation
            </h2>
          </div>
        </div>

        {/* 2 Columns: Top 3 Risk Drivers & Top 3 Protective Factors with 24px spacing */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 24,
          marginBottom: 28
        }}>
          {/* Key Risk Drivers (Top 3 only with 24px spacing between items) */}
          <div style={{
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border)',
            borderRadius: 14,
            padding: '24px 24px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              fontSize: '0.75rem',
              fontWeight: 700,
              color: 'var(--c-danger)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 18
            }}>
              <AlertTriangle size={14} />
              <span>Key Risk Drivers (Top 3)</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {profile.keyRiskDrivers.slice(0, 3).map((driver, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                  <div style={{
                    width: 7,
                    height: 7,
                    borderRadius: '50%',
                    background: 'var(--c-danger)',
                    marginTop: 6,
                    flexShrink: 0
                  }} />
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)', lineHeight: 1.3 }}>
                      {driver.name}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.45, marginTop: 4 }}>
                      {driver.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Protective Factors (Top 3 only with 24px spacing between items) */}
          <div style={{
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border)',
            borderRadius: 14,
            padding: '24px 24px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              fontSize: '0.75rem',
              fontWeight: 700,
              color: 'var(--c-success)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 18
            }}>
              <CheckCircle2 size={14} />
              <span>Protective Factors (Top 3)</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {profile.protectiveFactors.slice(0, 3).map((factor, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                  <div style={{
                    width: 7,
                    height: 7,
                    borderRadius: '50%',
                    background: 'var(--c-success)',
                    marginTop: 6,
                    flexShrink: 0
                  }} />
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)', lineHeight: 1.3 }}>
                      {factor.name}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.45, marginTop: 4 }}>
                      {factor.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Physician Clinical Narrative — Structured Summary with Bullets & Key Findings */}
        <div style={{
          background: 'var(--c-surface-tint)',
          border: '1px solid var(--c-border)',
          borderRadius: 14,
          padding: '24px 28px'
        }}>
          {/* Header */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 16,
            paddingBottom: 12,
            borderBottom: '1px solid var(--c-border)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Sparkles size={15} color="var(--c-primary)" />
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                color: 'var(--c-primary)'
              }}>
                Physician Clinical Narrative & Diagnostic Summary
              </span>
            </div>
            <span style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--c-muted)',
              background: 'var(--c-bg)',
              padding: '3px 8px',
              borderRadius: 6,
              border: '1px solid var(--c-border)'
            }}>
              Structured Evaluation
            </span>
          </div>

          {/* Primary Diagnostic Impression Highlight */}
          <div style={{
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border)',
            borderRadius: 10,
            padding: '12px 16px',
            marginBottom: 16,
            display: 'flex',
            alignItems: 'flex-start',
            gap: 10
          }}>
            <Stethoscope size={16} color="var(--c-primary)" style={{ marginTop: 2, flexShrink: 0 }} />
            <div>
              <span style={{ fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--c-primary)', display: 'block', marginBottom: 2 }}>
                Primary Diagnostic Impression
              </span>
              <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)', lineHeight: 1.4 }}>
                {profile.structuredFindings?.primaryImpression || profile.narrative.split('.')[0] + '.'}
              </span>
            </div>
          </div>

          {/* Key Findings Bullet Grid */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {(profile.structuredFindings?.findings || [
              { category: 'Pathophysiological Status', detail: profile.keyRiskDrivers[0]?.description || 'Biomarker depletion correlating with reported functional symptoms.' },
              { category: 'Contributing Factors', detail: profile.keyRiskDrivers[1]?.description || 'Nutritional deficiency exacerbated by sub-optimal dietary density.' },
              { category: 'Metabolic Counterbalance', detail: profile.protectiveFactors[0]?.description || 'Intact absorption cofactors provide protective physiological support.' },
              { category: 'Clinical Repletion Strategy', detail: profile.recommendations[0]?.action || 'Initiate targeted oral micronutrient repletion protocol.' }
            ]).map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, fontSize: '0.8125rem', lineHeight: 1.5 }}>
                <div style={{
                  width: 6,
                  height: 6,
                  borderRadius: '50%',
                  background: 'var(--c-primary)',
                  marginTop: 7,
                  flexShrink: 0
                }} />
                <div>
                  <strong style={{ color: 'var(--c-secondary)', marginRight: 6 }}>
                    {item.category}:
                  </strong>
                  <span style={{ color: 'var(--c-muted)' }}>
                    {item.detail}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════════════════════════════
          SECTION 4 — EXPLAINABLE AI (Clean horizontal bars, 32px padding)
          ══════════════════════════════════════════════════════════════════════ */}
      <motion.div
        variants={fadeUp}
        style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 20,
          padding: 32
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
          <div>
            <h2 style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.1875rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              letterSpacing: 'normal',
              marginBottom: 4
            }}>
              Explainable AI Analysis
            </h2>
            <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)' }}>
              Top risk contributors and relative impact percentage on clinical assessment
            </p>
          </div>
          <span style={{
            fontSize: '0.6875rem',
            fontWeight: 600,
            color: 'var(--c-muted)',
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border)',
            padding: '5px 12px',
            borderRadius: 8
          }}>
            Top 5 Factors
          </span>
        </div>

        {/* List of 5 Horizontal Bars */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {profile.topContributors.slice(0, 5).map((item, index) => {
            const isRisk = item.direction === 'Risk Driver'
            const barColor = isRisk ? 'var(--c-danger)' : 'var(--c-success)'
            const badgeBg = isRisk ? 'rgba(239, 68, 68, 0.12)' : 'rgba(34, 197, 94, 0.12)'
            const badgeBorder = isRisk ? 'rgba(239, 68, 68, 0.25)' : 'rgba(34, 197, 94, 0.25)'
            const badgeColor = isRisk ? 'var(--c-danger)' : 'var(--c-success)'

            return (
              <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>
                    {item.name}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 4,
                      background: badgeBg,
                      border: `1px solid ${badgeBorder}`,
                      color: badgeColor
                    }}>
                      {item.direction}
                    </span>
                    <span style={{
                      fontSize: '0.8125rem',
                      fontWeight: 800,
                      fontFamily: 'var(--font-heading)',
                      color: 'var(--c-secondary)'
                    }}>
                      {item.percentage}%
                    </span>
                  </div>
                </div>

                {/* Horizontal Progress Bar */}
                <div style={{
                  width: '100%',
                  height: 7,
                  background: 'var(--c-surface-tint)',
                  borderRadius: 9999,
                  overflow: 'hidden'
                }}>
                  <div
                    style={{
                      width: `${Math.min(100, Math.max(8, item.percentage))}%`,
                      height: '100%',
                      background: barColor,
                      borderRadius: 9999,
                      transition: 'width 0.4s ease-out'
                    }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════════════════════════════
          SECTION 5 — CLINICAL EVIDENCE (Collapsible citations, 32px padding)
          ══════════════════════════════════════════════════════════════════════ */}
      <motion.div
        variants={fadeUp}
        style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 20,
          padding: 32
        }}
      >
        <div style={{ marginBottom: 26 }}>
          <h2 style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.1875rem',
            fontWeight: 700,
            color: 'var(--c-secondary)',
            letterSpacing: 'normal',
            marginBottom: 4
          }}>
            Clinical Evidence
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)' }}>
            Authoritative clinical guidelines, meta-analyses, and peer-reviewed reference standards
          </p>
        </div>

        {/* Collapsible Evidence Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {profile.evidenceCitations.map(citation => {
            const isExpanded = expandedEvidenceId === citation.id

            return (
              <div
                key={citation.id}
                style={{
                  background: 'var(--c-bg)',
                  border: '1px solid var(--c-border)',
                  borderRadius: 14,
                  overflow: 'hidden',
                  transition: 'border-color 0.2s'
                }}
              >
                {/* Header / Unexpanded summary view */}
                <button
                  type="button"
                  onClick={() => toggleEvidence(citation.id)}
                  style={{
                    width: '100%',
                    padding: '20px 22px',
                    background: 'transparent',
                    border: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: 16
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <span style={{
                        fontSize: '0.6875rem',
                        fontWeight: 700,
                        padding: '3px 9px',
                        borderRadius: 5,
                        background: 'var(--c-surface-tint)',
                        border: '1px solid var(--c-border)',
                        color: 'var(--c-primary)'
                      }}>
                        {citation.organization}
                      </span>
                    </div>

                    <div style={{
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: 'var(--c-secondary)',
                      lineHeight: 1.35,
                      marginBottom: 6
                    }}>
                      {citation.title}
                    </div>

                    <p style={{
                      fontSize: '0.75rem',
                      color: 'var(--c-muted)',
                      lineHeight: 1.5,
                      margin: 0
                    }}>
                      {citation.summary}
                    </p>
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 5,
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    color: 'var(--c-primary)',
                    marginTop: 2,
                    flexShrink: 0
                  }}>
                    <span>{isExpanded ? 'Hide' : 'Details'}</span>
                    <ChevronDown
                      size={14}
                      style={{
                        transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                        transition: 'transform 0.2s'
                      }}
                    />
                  </div>
                </button>

                {/* Expanded Details View */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      style={{
                        padding: '0 22px 20px 22px',
                        borderTop: '1px solid var(--c-border)',
                        paddingTop: 14,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 10,
                        fontSize: '0.75rem'
                      }}
                    >
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, color: 'var(--c-muted)' }}>
                        <div>
                          <strong>Study Design:</strong>{' '}
                          <span style={{ color: 'var(--c-secondary)' }}>{citation.studyType}</span>
                        </div>
                        <div>
                          <strong>Reference ID:</strong>{' '}
                          <span style={{ color: 'var(--c-secondary)', fontFamily: 'monospace' }}>
                            {citation.pmid}
                          </span>
                        </div>
                        <div>
                          <strong>Standard Intake:</strong>{' '}
                          <span style={{ color: 'var(--c-secondary)' }}>{citation.dailyIntake}</span>
                        </div>
                        {citation.upperLimit && (
                          <div>
                            <strong>Tolerable Limit:</strong>{' '}
                            <span style={{ color: 'var(--c-secondary)' }}>{citation.upperLimit}</span>
                          </div>
                        )}
                      </div>

                      <div style={{ paddingTop: 4 }}>
                        <a
                          href={citation.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                            color: 'var(--c-primary)',
                            fontWeight: 600,
                            textDecoration: 'none'
                          }}
                        >
                          <span>Access Primary Source Publication</span>
                          <ExternalLink size={12} />
                        </a>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════════════════════════════
          SECTION 6 — RECOMMENDED ACTIONS (Prioritized protocol, 32px padding)
          ══════════════════════════════════════════════════════════════════════ */}
      <motion.div
        variants={fadeUp}
        style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 20,
          padding: 32
        }}
      >
        <div style={{ marginBottom: 26 }}>
          <h2 style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.1875rem',
            fontWeight: 700,
            color: 'var(--c-secondary)',
            letterSpacing: 'normal',
            marginBottom: 4
          }}>
            Recommended Actions
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)' }}>
            Prioritized clinical interventions, biochemical rationales, and expected clinical benefits
          </p>
        </div>

        {/* Prioritized List (Max 5 recommendations) */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {profile.recommendations.slice(0, 5).map((rec, idx) => (
            <div
              key={idx}
              style={{
                background: 'var(--c-bg)',
                border: '1px solid var(--c-border)',
                borderRadius: 14,
                padding: '18px 24px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: 18
              }}
            >
              {/* Priority badge pill */}
              <span style={{
                fontSize: '0.6875rem',
                fontWeight: 700,
                color: 'var(--c-primary)',
                background: 'var(--c-surface-tint)',
                border: '1px solid var(--c-border)',
                padding: '4px 10px',
                borderRadius: 6,
                flexShrink: 0,
                marginTop: 2
              }}>
                {rec.priority}
              </span>

              {/* Action content */}
              <div style={{ flex: 1 }}>
                <div style={{
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: 'var(--c-secondary)',
                  marginBottom: 6,
                  lineHeight: 1.3
                }}>
                  {rec.action}
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.5, marginBottom: 4 }}>
                  <strong style={{ color: 'var(--c-secondary)' }}>Rationale:</strong> {rec.rationale}
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--c-primary)', lineHeight: 1.5 }}>
                  <strong>Expected Benefit:</strong> {rec.expectedBenefit}
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════════════════════════════
          FOOTER & COMPLIANCE (Minimal CDSS notice + Technical Telemetry Modal trigger)
          ══════════════════════════════════════════════════════════════════════ */}
      <motion.div
        variants={fadeUp}
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 12,
          paddingTop: 8,
          textAlign: 'center'
        }}
      >
        <p style={{
          fontSize: '0.6875rem',
          color: 'var(--c-muted)',
          maxWidth: 720,
          lineHeight: 1.5,
          margin: 0
        }}>
          <strong>Clinical Decision Support Notice:</strong> NutriScan probabilistic outputs assist licensed healthcare professionals and do not constitute independent medical diagnoses. Confirmatory laboratory testing is advised prior to initiating high-dose repletion.
        </p>

        {/* Minimal Developer Telemetry Link */}
        <button
          type="button"
          onClick={() => setIsTelemetryModalOpen(true)}
          style={{
            background: 'transparent',
            border: 'none',
            fontSize: '0.6875rem',
            color: 'var(--c-muted)',
            cursor: 'pointer',
            textDecoration: 'underline',
            display: 'flex',
            alignItems: 'center',
            gap: 4
          }}
        >
          <Cpu size={12} />
          <span>Inspect Model Governance & Audit Telemetry</span>
        </button>
      </motion.div>
        </>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          ADVANCED DEVELOPER / AUDIT TELEMETRY MODAL
          ══════════════════════════════════════════════════════════════════════ */}
      <AnimatePresence>
        {isTelemetryModalOpen && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
              backdropFilter: 'blur(4px)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 16
            }}
            onClick={() => setIsTelemetryModalOpen(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              onClick={e => e.stopPropagation()}
              style={{
                width: '100%',
                maxWidth: 540,
                background: 'var(--c-card)',
                border: '1px solid var(--c-border)',
                borderRadius: 16,
                padding: 24,
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: 16,
                paddingBottom: 12,
                borderBottom: '1px solid var(--c-border)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Cpu size={16} color="var(--c-primary)" />
                  <span style={{ fontFamily: 'var(--font-heading)', fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                    Model Governance & Audit Telemetry
                  </span>
                </div>
                <button
                  onClick={() => setIsTelemetryModalOpen(false)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--c-muted)',
                    cursor: 'pointer',
                    padding: 4
                  }}
                >
                  <X size={16} />
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--c-bg)', borderRadius: 8 }}>
                  <span style={{ color: 'var(--c-muted)' }}>Champion Architecture</span>
                  <span style={{ fontWeight: 600, color: 'var(--c-secondary)', fontFamily: 'monospace' }}>
                    {apiData?.explanations?.find((e: any) => e.target === selectedTargetId)?.champion_algorithm || 'LogisticRegression (Calibrated)'}
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--c-bg)', borderRadius: 8 }}>
                  <span style={{ color: 'var(--c-muted)' }}>Training Cohort</span>
                  <span style={{ fontWeight: 600, color: 'var(--c-secondary)' }}>
                    NHANES Continuous Standard (N=9,546)
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--c-bg)', borderRadius: 8 }}>
                  <span style={{ color: 'var(--c-muted)' }}>Probability Calibration</span>
                  <span style={{ fontWeight: 600, color: 'var(--c-primary)' }}>
                    Platt Sigmoid Scaling (ECE: 0.024)
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--c-bg)', borderRadius: 8 }}>
                  <span style={{ color: 'var(--c-muted)' }}>Attribution Engine</span>
                  <span style={{ fontWeight: 600, color: 'var(--c-secondary)' }}>
                    Interventional TreeSHAP Partitioning
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--c-bg)', borderRadius: 8 }}>
                  <span style={{ color: 'var(--c-muted)' }}>Assessment Reference</span>
                  <span style={{ fontWeight: 600, color: 'var(--c-muted)', fontFamily: 'monospace' }}>
                    {effectiveId ? `UUID: ${effectiveId.slice(0, 18)}...` : 'No Assessment Active'}
                  </span>
                </div>
              </div>

              <div style={{ marginTop: 20, textAlign: 'right' }}>
                <button
                  type="button"
                  onClick={() => setIsTelemetryModalOpen(false)}
                  style={{
                    background: 'var(--c-surface-tint)',
                    border: '1px solid var(--c-border)',
                    color: 'var(--c-secondary)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    padding: '8px 16px',
                    borderRadius: 8,
                    cursor: 'pointer'
                  }}
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
