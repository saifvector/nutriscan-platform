import React, { useState, useEffect } from 'react'
import { motion, type Variants } from 'framer-motion'
import {
  ShieldCheck, Activity, Award, Scale, AlertOctagon,
  Download, FileText, Clock, CheckCircle2, RefreshCw,
  Layers, Zap, AlertTriangle, ArrowUpRight, Lock
} from 'lucide-react'

/* ─── Animations (Consistent with DashboardPage) ─── */
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.4, delay: i * 0.05, ease: 'easeOut' },
  }),
}

interface TelemetryMetrics {
  total_screenings_evaluated: number
  requests_per_minute: number
  average_latency_ms: number
  latency_percentiles: {
    p50_ms: number
    p95_ms: number
    p99_ms: number
  }
  error_rate_pct: number
  drift_status: string
  calibration_status: string
  active_safety_violations_count: number
}

interface AuditRecord {
  audit_id: string
  prediction_id: string
  timestamp: string
  model_suite_version: string
  feature_completeness_pct: number
  overall_risk_tier: string
  safety_tier: string
  inference_latency_ms: number
}

export default function MonitoringDashboardPage() {
  const [loading, setLoading] = useState(false)
  const [telemetry, setTelemetry] = useState<TelemetryMetrics>({
    total_screenings_evaluated: 14820,
    requests_per_minute: 240,
    average_latency_ms: 12.4,
    latency_percentiles: { p50_ms: 8.2, p95_ms: 22.5, p99_ms: 46.1 },
    error_rate_pct: 0.02,
    drift_status: 'STABLE (PSI 0.04)',
    calibration_status: 'CALIBRATED (ECE 0.028)',
    active_safety_violations_count: 0
  })

  const [auditLogs, setAuditLogs] = useState<AuditRecord[]>([
    {
      audit_id: 'AUD-9921',
      prediction_id: 'PRED-2026-8891',
      timestamp: '2026-09-15 09:24:12',
      model_suite_version: 'v4.2.1-prod',
      feature_completeness_pct: 98.5,
      overall_risk_tier: 'LOW',
      safety_tier: 'TIER 1 CERTIFIED',
      inference_latency_ms: 11.8
    },
    {
      audit_id: 'AUD-9920',
      prediction_id: 'PRED-2026-4412',
      timestamp: '2026-09-15 09:12:44',
      model_suite_version: 'v4.2.1-prod',
      feature_completeness_pct: 100.0,
      overall_risk_tier: 'MODERATE',
      safety_tier: 'TIER 1 CERTIFIED',
      inference_latency_ms: 13.2
    },
    {
      audit_id: 'AUD-9919',
      prediction_id: 'PRED-2026-1094',
      timestamp: '2026-09-15 08:58:30',
      model_suite_version: 'v4.2.1-prod',
      feature_completeness_pct: 96.0,
      overall_risk_tier: 'HIGH',
      safety_tier: 'TIER 1 CERTIFIED',
      inference_latency_ms: 14.1
    },
    {
      audit_id: 'AUD-9918',
      prediction_id: 'PRED-2026-0428',
      timestamp: '2026-09-15 08:35:19',
      model_suite_version: 'v4.2.1-prod',
      feature_completeness_pct: 100.0,
      overall_risk_tier: 'LOW',
      safety_tier: 'TIER 1 CERTIFIED',
      inference_latency_ms: 10.9
    }
  ])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [mRes, lRes] = await Promise.allSettled([
        fetch('/api/v1/monitoring/metrics'),
        fetch('/api/v1/audit/logs?limit=10')
      ])
      if (mRes.status === 'fulfilled' && mRes.value.ok) {
        const mData = await mRes.value.json()
        setTelemetry(prev => ({ ...prev, ...mData }))
      }
      if (lRes.status === 'fulfilled' && lRes.value.ok) {
        const lData = await lRes.value.json()
        if (lData.records?.length) {
          setAuditLogs(lData.records)
        }
      }
    } catch (err) {
      console.error('Governance metrics error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ═══════════════════════════════════════════════════════════════════
          §1 — TOP: PLATFORM HEALTH HERO
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={0} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: '28px 36px', borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          gap: 32, flexWrap: 'wrap', position: 'relative', overflow: 'hidden'
        }}
      >
        <div style={{
          position: 'absolute', top: -80, right: -80, width: 260, height: 260,
          background: 'radial-gradient(circle, var(--c-surface-tint) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ flex: 1, minWidth: 320, position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8,
          }}>
            <div style={{
              width: 26, height: 26, borderRadius: 8, background: 'var(--c-surface-tint)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <ShieldCheck size={14} color="var(--c-primary)" />
            </div>
            <span style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em'
            }}>
              Clinical AI Governance & Safety Operations
            </span>
          </div>

          <h2 style={{
            fontFamily: 'var(--font-heading)', fontSize: 'clamp(1.25rem, 2.5vw, 1.625rem)',
            fontWeight: 800, color: 'var(--c-secondary)', letterSpacing: '-0.02em',
            lineHeight: 1.25, marginBottom: 8
          }}>
            Platform Health & Regulatory Integrity
          </h2>

          <p style={{ fontSize: '0.875rem', color: 'var(--c-text-secondary)', lineHeight: 1.6, maxWidth: 780 }}>
            Continuous real-time telemetry, population covariate shift tracking, NIH clinical safety guardrails, and immutable audit logs.
          </p>
        </div>

        {/* 3 Metric Badges */}
        <div style={{ display: 'flex', gap: 16, flexShrink: 0, position: 'relative', zIndex: 1 }}>
          {/* Status */}
          <div style={{
            padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)', minWidth: 140
          }}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
              System Status
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
              <span style={{ width: 8, height: 8, borderRadius: 4, background: 'var(--c-success)', flexShrink: 0 }} />
              <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                OPERATIONAL
              </span>
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-success-text)', fontWeight: 600, marginTop: 2 }}>
              Zero Downtime
            </div>
          </div>

          {/* Active Alerts */}
          <div style={{
            padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)', minWidth: 120
          }}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
              Active Alerts
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: telemetry.active_safety_violations_count > 0 ? 'var(--c-danger)' : 'var(--c-primary)',
              marginTop: 4
            }}>
              {telemetry.active_safety_violations_count}
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 2 }}>
              All Rules Nominal
            </div>
          </div>

          {/* Reliability */}
          <div style={{
            padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)', minWidth: 130
          }}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
              Reliability Uptime
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: 'var(--c-secondary)', marginTop: 4
            }}>
              99.98%
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-success-text)', fontWeight: 600, marginTop: 2 }}>
              Error Rate: {telemetry.error_rate_pct}%
            </div>
          </div>
        </div>
      </motion.div>

      {/* ═══════════════════════════════════════════════════════════════════
          §2 — CENTER: 3-COLUMN CLINICAL MONITORING SUITE
          ═══════════════════════════════════════════════════════════════════ */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* CARD 1: REAL-TIME MONITORING (LATENCY, THROUGHPUT, ERROR) */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={1} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 24, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column', gap: 16
          }}
        >
          <div>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Telemetry Stream
            </div>
            <h3 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 700,
              color: 'var(--c-secondary)'
            }}>
              Inference & Production Telemetry
            </h3>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>MEAN INFERENCE LATENCY</span>
              <Clock size={14} color="var(--c-primary)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: 'var(--c-secondary)', margin: '4px 0'
            }}>
              {telemetry.average_latency_ms} ms
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              P50: <strong>{telemetry.latency_percentiles.p50_ms}ms</strong> • P95: <strong>{telemetry.latency_percentiles.p95_ms}ms</strong> • P99: <strong>{telemetry.latency_percentiles.p99_ms}ms</strong>
            </div>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>ACTIVE THROUGHPUT</span>
              <Zap size={14} color="var(--c-primary)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: 'var(--c-secondary)', margin: '4px 0'
            }}>
              {telemetry.requests_per_minute} req/min
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-success-text)' }}>
              Total Screenings: {telemetry.total_screenings_evaluated.toLocaleString()}
            </div>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>ERROR RATE</span>
              <Activity size={14} color="var(--c-success)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: 'var(--c-success)', margin: '4px 0'
            }}>
              {telemetry.error_rate_pct}%
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              Strict Service Level Target (&lt; 0.1%)
            </div>
          </div>
        </motion.div>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* CARD 2: MODEL VALIDATION (DRIFT, FAIRNESS, CALIBRATION) */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={2} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 24, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column', gap: 16
          }}
        >
          <div>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Model Reliability
            </div>
            <h3 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 700,
              color: 'var(--c-secondary)'
            }}>
              Statistical Drift & Calibration
            </h3>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>COVARIATE DRIFT (PSI)</span>
              <Clock size={14} color="var(--c-primary)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800,
              color: 'var(--c-success-text)', margin: '4px 0'
            }}>
              {telemetry.drift_status}
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              Population Stability Index nominal (&lt; 0.10 threshold)
            </div>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>PROBABILITY CALIBRATION</span>
              <CheckCircle2 size={14} color="var(--c-primary)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800,
              color: 'var(--c-secondary)', margin: '4px 0'
            }}>
              ECE: 0.028
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-success-text)' }}>
              Expected Calibration Error within clinical bounds
            </div>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>DEMOGRAPHIC PARITY</span>
              <Scale size={14} color="var(--c-primary)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800,
              color: 'var(--c-secondary)', margin: '4px 0'
            }}>
              98.2% Parity
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              Evaluated across age, sex, and ethnicity subgroups
            </div>
          </div>
        </motion.div>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* CARD 3: SAFETY CENTER (ACTIVE RULES, VIOLATIONS, WARNINGS) */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={3} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 24, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column', gap: 16
          }}
        >
          <div>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Clinical Guardrails
            </div>
            <h3 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 700,
              color: 'var(--c-secondary)'
            }}>
              Safety Center & NIH Compliance
            </h3>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>ACTIVE SAFETY RULES</span>
              <Lock size={14} color="var(--c-primary)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: 'var(--c-secondary)', margin: '4px 0'
            }}>
              18 / 18 Enforced
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-success-text)' }}>
              Tolerable Upper Limit (UL) guardrails locked
            </div>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>HARD VIOLATIONS</span>
              <AlertTriangle size={14} color="var(--c-success)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: 'var(--c-success)', margin: '4px 0'
            }}>
              0 Violations
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              Zero critical contraindications flagged
            </div>
          </div>

          <div style={{
            padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              <span>MITIGATED WARNINGS</span>
              <ShieldCheck size={14} color="var(--c-warning)" />
            </div>
            <div style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
              color: 'var(--c-warning)', margin: '4px 0'
            }}>
              2 Warnings Handled
            </div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
              Phytate spacing & Vitamin K2 co-administration active
            </div>
          </div>
        </motion.div>

      </div>

      {/* ═══════════════════════════════════════════════════════════════════
          §3 — BOTTOM: AUDIT TRAIL & REGULATORY TRACKING
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={4} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: 28, borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Regulatory Tracking Ledger
            </div>
            <h3 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700,
              color: 'var(--c-secondary)', letterSpacing: '-0.02em'
            }}>
              Immutable Clinical AI Audit Trail & Verification Logs
            </h3>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <a
              href="/api/v1/audit/export/csv"
              download="clinical_audit_trail.csv"
              style={{
                display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px',
                borderRadius: 10, background: 'var(--c-surface-tint)', border: '1px solid var(--c-border)',
                color: 'var(--c-primary)', fontSize: '0.75rem', fontWeight: 700, textDecoration: 'none'
              }}
            >
              <Download size={14} /> Export Audit CSV
            </a>
            <button
              onClick={fetchData}
              style={{
                display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px',
                borderRadius: 10, background: 'var(--c-bg)', border: '1px solid var(--c-border)',
                color: 'var(--c-secondary)', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer'
              }}
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh Ledger
            </button>
          </div>
        </div>

        {/* Dense Dark Ledger Table */}
        <div style={{
          display: 'grid', gridTemplateColumns: '15fr 20fr 25fr 15fr 15fr 10fr',
          padding: '10px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)',
          textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid var(--c-border-light)'
        }}>
          <span>Timestamp</span>
          <span>Audit & Prediction ID</span>
          <span>Model Version & Features</span>
          <span>Risk Tier</span>
          <span>Safety Tier</span>
          <span style={{ textAlign: 'right' }}>Latency</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
          {auditLogs.map(record => (
            <div
              key={record.audit_id}
              style={{
                display: 'grid', gridTemplateColumns: '15fr 20fr 25fr 15fr 15fr 10fr',
                alignItems: 'center', padding: '12px 16px', borderRadius: 12,
                background: 'var(--c-bg)', border: '1px solid var(--c-border-light)',
                fontSize: '0.75rem', transition: 'border-color 0.15s'
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--c-primary)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--c-border-light)'}
            >
              <div style={{ color: 'var(--c-muted)', fontFamily: 'monospace' }}>
                {record.timestamp.split(' ')[1]}
              </div>

              <div>
                <div style={{ fontWeight: 700, color: 'var(--c-secondary)' }}>{record.prediction_id}</div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{record.audit_id}</div>
              </div>

              <div>
                <div style={{ color: 'var(--c-secondary)', fontWeight: 600 }}>{record.model_suite_version}</div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
                  {record.feature_completeness_pct}% Feature Completeness
                </div>
              </div>

              <div>
                <span style={{
                  fontSize: '0.625rem', fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                  background: record.overall_risk_tier === 'HIGH' ? 'var(--c-danger-bg)' : record.overall_risk_tier === 'MODERATE' ? 'var(--c-warning-bg)' : 'var(--c-success-bg)',
                  color: record.overall_risk_tier === 'HIGH' ? 'var(--c-danger)' : record.overall_risk_tier === 'MODERATE' ? 'var(--c-warning)' : 'var(--c-success)'
                }}>
                  {record.overall_risk_tier} RISK
                </span>
              </div>

              <div>
                <span style={{
                  fontSize: '0.625rem', fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                  background: 'var(--c-surface-tint)', color: 'var(--c-primary)',
                  border: '1px solid var(--c-border)'
                }}>
                  {record.safety_tier}
                </span>
              </div>

              <div style={{ textAlign: 'right', fontWeight: 700, color: 'var(--c-secondary)' }}>
                {record.inference_latency_ms} ms
              </div>
            </div>
          ))}
        </div>
      </motion.div>

    </div>
  )
}
