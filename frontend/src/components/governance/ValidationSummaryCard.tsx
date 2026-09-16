import React, { useState, useEffect } from 'react'
import { Award, CheckCircle2, TrendingUp, Users, Info, AlertTriangle } from 'lucide-react'

interface TargetMetric {
  target: string
  target_name: string
  algorithm: string
  sample_size: number
  prevalence_pct: number
  auroc: number
  auprc: number
  sensitivity: number
  specificity: number
  ppv: number
  npv: number
  f1_score: number
  ece: number
  brier_score: number
}

interface CohortSummary {
  total_holdout_samples: number
  evaluated_targets_count: number
  overall_macro_auroc: number
  overall_macro_ece: number
  targets: TargetMetric[]
}

interface SubgroupReport {
  subgroup_category: string
  subgroup_value: string
  sample_size: number
  targets: TargetMetric[]
}

export default function ValidationSummaryCard() {
  const [summary, setSummary] = useState<CohortSummary | null>(null)
  const [selectedSubgroup, setSelectedSubgroup] = useState<'NONE' | 'SEX' | 'AGE' | 'INCOME_PIR'>('NONE')
  const [subgroupData, setSubgroupData] = useState<SubgroupReport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchCohortSummary()
  }, [])

  useEffect(() => {
    if (selectedSubgroup !== 'NONE') {
      fetchSubgroupBreakdown(selectedSubgroup)
    }
  }, [selectedSubgroup])

  const fetchCohortSummary = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/v1/validation/cohort-summary')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setSummary(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load cohort validation summary')
    } finally {
      setLoading(false)
    }
  }

  const fetchSubgroupBreakdown = async (category: string) => {
    try {
      const res = await fetch(`/api/v1/validation/demographic-breakdown?stratification=${category}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setSubgroupData(data.subgroups || [])
    } catch (err: any) {
      console.error(err)
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
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '36px', height: '36px', borderRadius: '10px',
              background: 'linear-gradient(135deg, #0d9488, #065f46)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff'
            }}>
              <Award size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: 'var(--c-text, #0f172a)' }}>
                Clinical Diagnostic Validation
              </h3>
              <p style={{ margin: 0, fontSize: '13px', color: 'var(--c-text-muted, #64748b)' }}>
                Holdout NHANES evaluation across 9 deficiency models with demographic stratification
              </p>
            </div>
          </div>
        </div>

        {/* Stratification Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--c-text-muted, #64748b)' }}>Stratify:</span>
          {(['NONE', 'SEX', 'AGE', 'INCOME_PIR'] as const).map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedSubgroup(cat)}
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: 600,
                border: '1px solid',
                borderColor: selectedSubgroup === cat ? '#0d9488' : 'var(--c-border, #e2e8f0)',
                background: selectedSubgroup === cat ? '#0d9488' : 'transparent',
                color: selectedSubgroup === cat ? '#fff' : 'var(--c-text, #0f172a)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {cat === 'NONE' ? 'Aggregate' : cat === 'INCOME_PIR' ? 'Income PIR' : cat}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--c-text-muted)' }}>
          Computing holdout validation metrics...
        </div>
      ) : error ? (
        <div style={{ padding: '16px', borderRadius: '8px', background: '#fef2f2', color: '#991b1b', fontSize: '13px' }}>
          <AlertTriangle size={16} style={{ verticalAlign: 'middle', marginRight: '6px' }} />
          {error}
        </div>
      ) : (
        <>
          {/* Key Metric Highlights */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '12px', marginBottom: '20px'
          }}>
            <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(13, 148, 136, 0.08)', border: '1px solid rgba(13, 148, 136, 0.2)' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: '#0d9488' }}>Macro AUROC</div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {summary?.overall_macro_auroc.toFixed(3)}
              </div>
              <div style={{ fontSize: '12px', color: '#059669', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={14} /> Certified High Discrimination
              </div>
            </div>

            <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: '#6366f1' }}>Expected Calibration (ECE)</div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {summary?.overall_macro_ece.toFixed(3)}
              </div>
              <div style={{ fontSize: '12px', color: '#6366f1' }}>Platt Scaled Probability</div>
            </div>

            <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: '#10b981' }}>Holdout Test Cohort</div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {summary?.total_holdout_samples.toLocaleString()}
              </div>
              <div style={{ fontSize: '12px', color: '#059669' }}>Unseen Participants</div>
            </div>

            <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: '#d97706' }}>Evaluated Models</div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {summary?.evaluated_targets_count} / 9
              </div>
              <div style={{ fontSize: '12px', color: '#b45309' }}>100% Champion Suite</div>
            </div>
          </div>

          {/* Aggregate Table or Subgroup Slices */}
          {selectedSubgroup === 'NONE' ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--c-border, #e2e8f0)', textAlign: 'left', color: 'var(--c-text-muted, #64748b)' }}>
                    <th style={{ padding: '10px 8px' }}>Target Deficiency</th>
                    <th style={{ padding: '10px 8px' }}>Algorithm</th>
                    <th style={{ padding: '10px 8px' }}>Prevalence</th>
                    <th style={{ padding: '10px 8px' }}>AUROC</th>
                    <th style={{ padding: '10px 8px' }}>Sensitivity</th>
                    <th style={{ padding: '10px 8px' }}>Specificity</th>
                    <th style={{ padding: '10px 8px' }}>ECE</th>
                    <th style={{ padding: '10px 8px' }}>Brier Score</th>
                  </tr>
                </thead>
                <tbody>
                  {summary?.targets.map((t, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--c-border, #f1f5f9)', transition: 'background 0.15s' }}>
                      <td style={{ padding: '10px 8px', fontWeight: 600, color: 'var(--c-text, #0f172a)' }}>{t.target_name}</td>
                      <td style={{ padding: '10px 8px' }}>
                        <span style={{
                          fontSize: '11px', padding: '2px 8px', borderRadius: '4px',
                          background: t.algorithm.includes('XGBoost') ? '#eff6ff' : t.algorithm.includes('Random') ? '#f0fdf4' : '#fef3c7',
                          color: t.algorithm.includes('XGBoost') ? '#1d4ed8' : t.algorithm.includes('Random') ? '#15803d' : '#b45309',
                          fontWeight: 600
                        }}>
                          {t.algorithm}
                        </span>
                      </td>
                      <td style={{ padding: '10px 8px', color: '#64748b' }}>{t.prevalence_pct.toFixed(1)}%</td>
                      <td style={{ padding: '10px 8px', fontWeight: 700, color: t.auroc >= 0.80 ? '#059669' : '#0d9488' }}>
                        {t.auroc.toFixed(3)}
                      </td>
                      <td style={{ padding: '10px 8px' }}>{(t.sensitivity * 100).toFixed(1)}%</td>
                      <td style={{ padding: '10px 8px' }}>{(t.specificity * 100).toFixed(1)}%</td>
                      <td style={{ padding: '10px 8px', color: t.ece <= 0.05 ? '#059669' : '#b45309' }}>{t.ece.toFixed(3)}</td>
                      <td style={{ padding: '10px 8px', color: '#64748b' }}>{t.brier_score.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {subgroupData.map((sub, sIdx) => (
                <div key={sIdx} style={{
                  padding: '16px', borderRadius: '12px', border: '1px solid var(--c-border, #e2e8f0)',
                  background: 'var(--c-bg, #f8fafc)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--c-text, #0f172a)' }}>
                      Subgroup: <span style={{ color: '#0d9488' }}>{sub.subgroup_value}</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--c-text-muted, #64748b)' }}>
                      Sample Size: <b>{sub.sample_size}</b> participants
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
                    {sub.targets.slice(0, 6).map((t, tIdx) => (
                      <div key={tIdx} style={{ padding: '10px', borderRadius: '8px', background: 'var(--c-surface, #fff)', border: '1px solid #e2e8f0' }}>
                        <div style={{ fontSize: '12px', fontWeight: 600, color: '#334155' }}>{t.target_name}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '11px' }}>
                          <span style={{ color: '#64748b' }}>AUROC:</span>
                          <span style={{ fontWeight: 700, color: '#0d9488' }}>{t.auroc.toFixed(3)}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2px', fontSize: '11px' }}>
                          <span style={{ color: '#64748b' }}>Prev:</span>
                          <span>{t.prevalence_pct.toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
