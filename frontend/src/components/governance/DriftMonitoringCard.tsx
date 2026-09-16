import React, { useState, useEffect } from 'react'
import { Activity, AlertTriangle, CheckCircle, RefreshCw, Sliders } from 'lucide-react'

interface FeatureDrift {
  feature_name: string
  category: string
  psi: number
  ks_statistic: number | null
  ks_p_value: number | null
  status: 'STABLE' | 'MODERATE_SHIFT' | 'SIGNIFICANT_DRIFT'
  alert_triggered: boolean
}

interface TargetDrift {
  target: string
  target_name: string
  psi: number
  status: 'STABLE' | 'MODERATE_SHIFT' | 'SIGNIFICANT_DRIFT'
}

interface DriftReport {
  timestamp: string
  reference_sample_size: number
  evaluated_window_size: number
  overall_drift_status: 'STABLE' | 'MODERATE_SHIFT' | 'SIGNIFICANT_DRIFT'
  max_feature_psi: number
  features_evaluated: number
  drift_breakdown: FeatureDrift[]
  prediction_drift: TargetDrift[]
}

export default function DriftMonitoringCard() {
  const [report, setReport] = useState<DriftReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [driftFactor, setDriftFactor] = useState(0.0)

  useEffect(() => {
    fetchDrift(driftFactor)
  }, [driftFactor])

  const fetchDrift = async (factor: number) => {
    try {
      setLoading(true)
      const res = await fetch(`/api/v1/monitoring/drift?simulated_drift_factor=${factor}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setReport(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'STABLE':
        return { bg: '#ecfdf5', text: '#059669', border: '#a7f3d0' }
      case 'MODERATE_SHIFT':
        return { bg: '#fffbeb', text: '#d97706', border: '#fde68a' }
      case 'SIGNIFICANT_DRIFT':
        return { bg: '#fef2f2', text: '#dc2626', border: '#fecaca' }
      default:
        return { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' }
    }
  }

  const statusStyle = getStatusColor(report?.overall_drift_status || 'STABLE')

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
            background: 'linear-gradient(135deg, #6366f1, #4338ca)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff'
          }}>
            <Activity size={20} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: 'var(--c-text, #0f172a)' }}>
              Statistical Feature & Population Drift
            </h3>
            <p style={{ margin: 0, fontSize: '13px', color: 'var(--c-text-muted, #64748b)' }}>
              Two-Sample Kolmogorov-Smirnov & Population Stability Index (PSI) Telemetry
            </p>
          </div>
        </div>

        {/* Global Status Pill */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '8px',
          padding: '6px 14px', borderRadius: '20px',
          background: statusStyle.bg, border: `1px solid ${statusStyle.border}`,
          color: statusStyle.text, fontWeight: 700, fontSize: '13px'
        }}>
          {report?.overall_drift_status === 'STABLE' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
          Status: {report?.overall_drift_status?.replace('_', ' ')}
        </div>
      </div>

      {/* Simulator Control */}
      <div style={{
        marginBottom: '20px', padding: '12px 16px', borderRadius: '10px',
        background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sliders size={16} color="#6366f1" />
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--c-text, #0f172a)' }}>
            Simulate Production Drift:
          </span>
          <span style={{ fontSize: '12px', color: '#64748b' }}>
            +{Math.round(driftFactor * 100)}% shift
          </span>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {[0.0, 0.15, 0.35].map(f => (
            <button
              key={f}
              onClick={() => setDriftFactor(f)}
              style={{
                padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600,
                border: '1px solid',
                borderColor: driftFactor === f ? '#6366f1' : 'var(--c-border, #e2e8f0)',
                background: driftFactor === f ? '#6366f1' : 'transparent',
                color: driftFactor === f ? '#fff' : 'var(--c-text, #0f172a)',
                cursor: 'pointer'
              }}
            >
              {f === 0 ? 'Baseline (0%)' : `Shift +${Math.round(f * 100)}%`}
            </button>
          ))}
          <button
            onClick={() => fetchDrift(driftFactor)}
            style={{
              display: 'flex', alignItems: 'center', gap: '4px',
              padding: '4px 10px', borderRadius: '6px', fontSize: '11px',
              background: 'transparent', border: '1px solid var(--c-border, #e2e8f0)',
              cursor: 'pointer', color: 'var(--c-text-muted, #64748b)'
            }}
          >
            <RefreshCw size={12} /> Refresh
          </button>
        </div>
      </div>

      {loading && !report ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--c-text-muted)' }}>
          Computing distribution divergence metrics...
        </div>
      ) : (
        <>
          {/* Metrics summary */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '20px' }}>
            <div style={{ padding: '12px', borderRadius: '10px', background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)' }}>
              <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>MAX FEATURE PSI</div>
              <div style={{ fontSize: '20px', fontWeight: 800, color: report?.max_feature_psi && report.max_feature_psi >= 0.20 ? '#dc2626' : '#0f172a', margin: '4px 0' }}>
                {report?.max_feature_psi.toFixed(4)}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Threshold: &lt; 0.10 (Stable)</div>
            </div>

            <div style={{ padding: '12px', borderRadius: '10px', background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)' }}>
              <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>REFERENCE DATASET</div>
              <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {report?.reference_sample_size.toLocaleString()}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>NHANES 2017-2020 cycle</div>
            </div>

            <div style={{ padding: '12px', borderRadius: '10px', background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)' }}>
              <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>EVALUATION WINDOW</div>
              <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {report?.evaluated_window_size}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Production screening events</div>
            </div>

            <div style={{ padding: '12px', borderRadius: '10px', background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)' }}>
              <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>FEATURES TRACKED</div>
              <div style={{ fontSize: '20px', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {report?.features_evaluated}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Nutrients + Demographics</div>
            </div>
          </div>

          {/* Feature Drift Table */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--c-border, #e2e8f0)', textAlign: 'left', color: 'var(--c-text-muted, #64748b)' }}>
                  <th style={{ padding: '10px 8px' }}>Feature Name</th>
                  <th style={{ padding: '10px 8px' }}>Category</th>
                  <th style={{ padding: '10px 8px' }}>PSI (10 Bins)</th>
                  <th style={{ padding: '10px 8px' }}>KS Statistic</th>
                  <th style={{ padding: '10px 8px' }}>KS p-value</th>
                  <th style={{ padding: '10px 8px' }}>Stability Tier</th>
                </tr>
              </thead>
              <tbody>
                {report?.drift_breakdown.map((item, idx) => {
                  const s = getStatusColor(item.status)
                  return (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--c-border, #f1f5f9)' }}>
                      <td style={{ padding: '10px 8px', fontWeight: 600, color: 'var(--c-text, #0f172a)' }}>
                        {item.feature_name}
                      </td>
                      <td style={{ padding: '10px 8px', color: '#64748b', fontSize: '12px' }}>
                        {item.category}
                      </td>
                      <td style={{ padding: '10px 8px', fontWeight: 700, color: item.psi >= 0.20 ? '#dc2626' : item.psi >= 0.10 ? '#d97706' : '#059669' }}>
                        {item.psi.toFixed(4)}
                      </td>
                      <td style={{ padding: '10px 8px', color: '#64748b' }}>
                        {item.ks_statistic !== null ? item.ks_statistic.toFixed(4) : '—'}
                      </td>
                      <td style={{ padding: '10px 8px', color: item.ks_p_value && item.ks_p_value < 0.01 ? '#dc2626' : '#64748b' }}>
                        {item.ks_p_value !== null ? item.ks_p_value.toFixed(4) : '—'}
                      </td>
                      <td style={{ padding: '10px 8px' }}>
                        <span style={{
                          fontSize: '11px', fontWeight: 700, padding: '2px 8px', borderRadius: '4px',
                          background: s.bg, color: s.text, border: `1px solid ${s.border}`
                        }}>
                          {item.status.replace('_', ' ')}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
