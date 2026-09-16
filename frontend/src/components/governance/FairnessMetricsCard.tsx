import React, { useState, useEffect } from 'react'
import { Scale, CheckCircle2, AlertCircle, Info } from 'lucide-react'

interface DemographicParity {
  attribute: string
  baseline_group: string
  comparison_group: string
  baseline_positive_rate: number
  comparison_positive_rate: number
  disparity_ratio: number
  compliant_with_80_pct_rule: boolean
}

interface EqualOpportunity {
  attribute: string
  baseline_group: string
  comparison_group: string
  baseline_tpr: number
  comparison_tpr: number
  tpr_difference: number
  within_tolerance: boolean
}

interface FairnessReport {
  timestamp: string
  overall_fairness_status: string
  attributes_evaluated: string[]
  demographic_parity: Record<string, DemographicParity>
  equal_opportunity: Record<string, EqualOpportunity>
  subgroup_positive_rates: Record<string, Record<string, number>>
}

export default function FairnessMetricsCard() {
  const [report, setReport] = useState<FairnessReport | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchFairness()
  }, [])

  const fetchFairness = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/v1/fairness/report')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setReport(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      background: 'var(--c-surface, #ffffff)',
      borderRadius: '16px',
      border: '1px solid var(--c-border, #e2e8f0)',
      padding: '24px',
      boxShadow: '0 4px 20px -2px rgba(0,0,0,0.05)'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff'
          }}>
            <Scale size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: 'var(--c-text, #0f172a)' }}>
              Demographic Fairness & Parity Auditing
            </h3>
            <p style={{ margin: 0, fontSize: '13px', color: 'var(--c-text-muted, #64748b)' }}>
              EEOC Four-Fifths (80%) Rule Compliance & Equal Opportunity Verification
            </p>
          </div>
        </div>

        <div style={{
          padding: '6px 14px', borderRadius: '20px',
          background: report?.overall_fairness_status.includes('COMPLIANT') ? '#ecfdf5' : '#fffbeb',
          border: `1px solid ${report?.overall_fairness_status.includes('COMPLIANT') ? '#a7f3d0' : '#fde68a'}`,
          color: report?.overall_fairness_status.includes('COMPLIANT') ? '#059669' : '#d97706',
          fontWeight: 700, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px'
        }}>
          {report?.overall_fairness_status.includes('COMPLIANT') ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          {report?.overall_fairness_status?.replace(/_/g, ' ')}
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--c-text-muted)' }}>
          Auditing algorithmic fairness across protected classes...
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Attributes breakdown grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {Object.entries(report?.demographic_parity || {}).map(([key, dp]) => {
              const eo = report?.equal_opportunity[key]
              const attributeName = dp.attribute === 'SEX' ? 'Sex (Male vs Female)' : dp.attribute === 'AGE' ? 'Age (Young vs Older)' : 'Income PIR (Low vs High)'
              return (
                <div key={key} style={{
                  padding: '16px', borderRadius: '12px',
                  background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--c-text, #0f172a)' }}>
                      {attributeName}
                    </div>
                    <span style={{
                      fontSize: '11px', fontWeight: 700, padding: '2px 8px', borderRadius: '4px',
                      background: dp.compliant_with_80_pct_rule ? '#ecfdf5' : '#fef2f2',
                      color: dp.compliant_with_80_pct_rule ? '#059669' : '#dc2626'
                    }}>
                      {dp.compliant_with_80_pct_rule ? '80% RULE PASS' : 'FLAGGED'}
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ color: '#64748b' }}>Disparity Ratio:</span>
                      <span style={{ fontWeight: 700, color: dp.disparity_ratio >= 0.80 ? '#059669' : '#d97706' }}>
                        {(dp.disparity_ratio * 100).toFixed(1)}%
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ color: '#64748b' }}>{dp.baseline_group} Acceptance:</span>
                      <span>{(dp.baseline_positive_rate * 100).toFixed(1)}%</span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #f1f5f9' }}>
                      <span style={{ color: '#64748b' }}>{dp.comparison_group} Acceptance:</span>
                      <span>{(dp.comparison_positive_rate * 100).toFixed(1)}%</span>
                    </div>

                    {eo && (
                      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                        <span style={{ color: '#64748b' }}>Equal Opportunity Diff (TPR):</span>
                        <span style={{ fontWeight: 700, color: eo.within_tolerance ? '#059669' : '#d97706' }}>
                          {(eo.tpr_difference * 100).toFixed(1)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '12px 14px', borderRadius: '8px', background: 'rgba(139, 92, 246, 0.08)',
            border: '1px solid rgba(139, 92, 246, 0.2)', fontSize: '12px', color: '#5b21b6'
          }}>
            <Info size={16} style={{ flexShrink: 0 }} />
            <span>
              <b>Regulatory Standard:</b> EEOC 29 CFR &sect; 1607.4. Disparate impact is assessed on calibrated risk tiers with adjusted clinical tolerance for known biological epidemiology.
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
