import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  AlertTriangle, ShieldAlert, ChevronDown, ChevronUp,
  AlertOctagon, CheckCircle2, Lock
} from 'lucide-react'

export interface SafetyViolationItem {
  rule_id?: string
  rule_name?: string
  nutrient?: string
  severity?: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW' | string
  action_taken?: 'BLOCKED' | 'MODIFIED' | 'FLAGGED' | 'QUARANTINED' | string
  clinical_rationale?: string
  message?: string
}

export interface PediatricSafetyBannerProps {
  patientAge?: number
  pediatricBracket?: string
  safetyWarnings?: Array<string | SafetyViolationItem>
  quarantinedItems?: string[]
  className?: string
}

export function PediatricSafetyBanner({
  patientAge,
  pediatricBracket,
  safetyWarnings = [],
  quarantinedItems = [],
  className = '',
}: PediatricSafetyBannerProps) {
  const [expanded, setExpanded] = useState(true)

  const isPediatric = typeof patientAge === 'number' && patientAge < 18
  const hasWarnings = safetyWarnings.length > 0 || quarantinedItems.length > 0

  // Only render if patient is under 18 or safety warnings exist
  if (!isPediatric && !hasWarnings) {
    return null
  }

  // Derive bracket if not explicitly provided
  const derivedBracket = pediatricBracket || (
    patientAge !== undefined
      ? patientAge < 0.5
        ? '0–6 Months (Infant)'
        : patientAge < 1
        ? '7–12 Months (Older Infant)'
        : patientAge <= 3
        ? '1–3 Years (Toddler)'
        : patientAge <= 8
        ? '4–8 Years (Young Child)'
        : patientAge <= 13
        ? '9–13 Years (Early Adolescent)'
        : patientAge < 18
        ? '14–18 Years (Adolescent)'
        : 'Adult'
      : 'Pediatric'
  )

  const isCritical = safetyWarnings.some(w =>
    typeof w === 'object' && (w.severity === 'CRITICAL' || w.action_taken === 'BLOCKED')
  ) || quarantinedItems.length > 0

  const borderColor = isCritical ? 'rgba(239, 68, 68, 0.4)' : 'rgba(245, 158, 11, 0.4)'
  const bgColor = isCritical ? 'rgba(239, 68, 68, 0.08)' : 'rgba(245, 158, 11, 0.08)'
  const badgeColor = isCritical ? 'var(--c-danger, #ef4444)' : 'var(--c-warning, #f59e0b)'

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={className}
      style={{
        borderRadius: 12,
        border: `1.5px solid ${borderColor}`,
        background: bgColor,
        backdropFilter: 'blur(8px)',
        padding: '14px 18px',
        marginBottom: 20,
        boxShadow: isCritical
          ? '0 4px 18px rgba(239, 68, 68, 0.12)'
          : '0 4px 18px rgba(245, 158, 11, 0.08)',
      }}
      role="alert"
      aria-live="assertive"
    >
      {/* Top Banner Row */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: 14,
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `${badgeColor}22`,
            border: `1px solid ${badgeColor}44`,
            color: badgeColor,
            flexShrink: 0,
          }}>
            {isCritical ? <AlertOctagon size={20} /> : <AlertTriangle size={20} />}
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '0.9375rem',
                fontWeight: 700,
                color: badgeColor,
                letterSpacing: '-0.01em',
              }}>
                {isPediatric ? 'PEDIATRIC CLINICAL SAFETY PROTOCOL ACTIVE' : 'CLINICAL SAFETY ALERT'}
              </span>

              {isPediatric && (
                <span style={{
                  fontSize: '0.6875rem',
                  fontWeight: 600,
                  padding: '2px 8px',
                  borderRadius: 6,
                  background: `${badgeColor}22`,
                  color: badgeColor,
                  border: `1px solid ${badgeColor}44`,
                  textTransform: 'uppercase',
                }}>
                  Age {patientAge} · {derivedBracket}
                </span>
              )}

              {isCritical && (
                <span style={{
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: 6,
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: 'var(--c-danger, #ef4444)',
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                }}>
                  CRITICAL QUARANTINE
                </span>
              )}
            </div>

            <p style={{
              margin: '4px 0 0 0',
              fontSize: '0.8125rem',
              color: 'var(--c-secondary, #94a3b8)',
              lineHeight: 1.4,
            }}>
              {isPediatric
                ? `American Academy of Pediatrics (AAP) & IOM Upper Tolerable Intake Level (UL) rules enforced. Adult supplement dosages are quarantined pending pediatric clinician review.`
                : `Clinical safety contraindications or dose limits detected for this patient record.`}
            </p>
          </div>
        </div>

        {/* Toggle details button */}
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--c-border, rgba(255,255,255,0.1))',
            borderRadius: 6,
            padding: '4px 10px',
            fontSize: '0.75rem',
            color: 'var(--c-muted, #64748b)',
            cursor: 'pointer',
            fontWeight: 500,
          }}
          aria-expanded={expanded}
        >
          <span>{expanded ? 'Hide Safety Details' : 'View Safety Details'}</span>
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* Expandable Safety Details */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            style={{ overflow: 'hidden', marginTop: 14 }}
          >
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: 12,
              paddingTop: 12,
              borderTop: `1px solid ${borderColor}`,
            }}>
              {/* Box 1: Toxicity & Tolerable Upper Limits */}
              <div style={{
                background: 'var(--c-surface, rgba(15, 23, 42, 0.6))',
                borderRadius: 8,
                padding: '10px 14px',
                border: '1px solid var(--c-border, rgba(255,255,255,0.08))',
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--c-primary, #38bdf8)',
                  marginBottom: 6,
                }}>
                  <ShieldAlert size={14} />
                  <span>Pediatric Upper Limit (UL) Guardrails</span>
                </div>
                <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--c-secondary, #94a3b8)', lineHeight: 1.4 }}>
                  {isPediatric
                    ? `Dosing thresholds restricted to pediatric bracket (${derivedBracket}). High-potency adult formulas are suppressed to prevent hypervitaminosis and mineral accumulation.`
                    : `Safety framework monitors cumulative daily intake across all dietary and supplemental sources.`}
                </p>
              </div>

              {/* Box 2: Quarantine & Blocked Interventions */}
              <div style={{
                background: 'var(--c-surface, rgba(15, 23, 42, 0.6))',
                borderRadius: 8,
                padding: '10px 14px',
                border: '1px solid var(--c-border, rgba(255,255,255,0.08))',
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: badgeColor,
                  marginBottom: 6,
                }}>
                  <Lock size={14} />
                  <span>Dosage Quarantine & Auto-Blocking</span>
                </div>
                {quarantinedItems.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: 16, fontSize: '0.75rem', color: 'var(--c-danger, #ef4444)' }}>
                    {quarantinedItems.map((item, idx) => (
                      <li key={idx}><strong>Quarantined:</strong> {item}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--c-secondary, #94a3b8)', lineHeight: 1.4 }}>
                    Automated safety filters actively block any recommendation exceeding safe physiological intake or contraindicated by clinical history.
                  </p>
                )}
              </div>

              {/* Box 3: Mandatory Clinician Review */}
              <div style={{
                background: 'var(--c-surface, rgba(15, 23, 42, 0.6))',
                borderRadius: 8,
                padding: '10px 14px',
                border: '1px solid var(--c-border, rgba(255,255,255,0.08))',
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: 'var(--c-warning, #f59e0b)',
                  marginBottom: 6,
                }}>
                  <CheckCircle2 size={14} />
                  <span>Mandatory Clinician Sign-Off</span>
                </div>
                <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--c-secondary, #94a3b8)', lineHeight: 1.4 }}>
                  All AI-suggested regimens for patients under 18 require affirmative physician or registered dietitian validation prior to dispensing or patient communication.
                </p>
              </div>
            </div>

            {/* List of active warnings/violations if any */}
            {safetyWarnings.length > 0 && (
              <div style={{ marginTop: 12 }}>
                <div style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: badgeColor,
                  marginBottom: 6,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}>
                  Active Safety Flags ({safetyWarnings.length}):
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {safetyWarnings.map((w, idx) => {
                    const isObj = typeof w === 'object' && w !== null
                    const ruleName = isObj ? (w.rule_name || w.rule_id || 'Safety Flag') : 'Safety Notice'
                    const rationale = isObj ? (w.clinical_rationale || w.message || '') : w
                    const action = isObj ? w.action_taken : null

                    return (
                      <div
                        key={idx}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 8,
                          fontSize: '0.75rem',
                          background: 'rgba(0,0,0,0.2)',
                          padding: '6px 10px',
                          borderRadius: 6,
                          borderLeft: `3px solid ${badgeColor}`,
                        }}
                      >
                        <span style={{ fontWeight: 600, color: badgeColor }}>[{ruleName}]</span>
                        <span style={{ color: 'var(--c-secondary, #cbd5e1)', flex: 1 }}>{rationale}</span>
                        {action && (
                          <span style={{
                            fontSize: '0.6875rem',
                            fontWeight: 700,
                            padding: '1px 6px',
                            borderRadius: 4,
                            background: action === 'BLOCKED' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                            color: action === 'BLOCKED' ? 'var(--c-danger, #ef4444)' : 'var(--c-warning, #f59e0b)',
                          }}>
                            {action}
                          </span>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
export default PediatricSafetyBanner
