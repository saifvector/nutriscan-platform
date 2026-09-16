import React, { useState } from 'react'
import { motion, type Variants } from 'framer-motion'
import { TrendingUp, Activity, CheckCircle2, AlertCircle, Clock, ShieldCheck, HelpCircle } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface RecoveryMilestone {
  day: number
  milestone_name: string
  biological_mechanism: string
  expected_symptom_relief: string[]
  health_score_target: number
}

interface RecoveryTrajectoryPoint {
  day: number
  projected_health_score: number
  confidence_lower_bound: number
  confidence_upper_bound: number
  adherence_assumption_pct: number
}

interface NutrientRecoveryProbability {
  nutrient_code: string
  common_name: string
  day_30_probability: number
  day_60_probability: number
  day_90_probability: number
  primary_limiting_factor: string
}

interface Props {
  projectionData: {
    baseline_health_score: number
    projected_30_day_score: number
    projected_60_day_score: number
    projected_90_day_score: number
    overall_recovery_probability_90d: number
    risk_reduction_trajectory: RecoveryTrajectoryPoint[]
    milestones: RecoveryMilestone[]
    nutrient_probabilities: NutrientRecoveryProbability[]
  }
}

export default function RecoverySimulator({ projectionData }: Props) {
  const [selectedMilestone, setSelectedMilestone] = useState<number>(30)

  // SVG Chart Dimensions
  const chartWidth = 640
  const chartHeight = 220
  const padding = { top: 20, right: 30, bottom: 35, left: 45 }

  const minDay = 0
  const maxDay = 90
  const minScore = 30
  const maxScore = 100

  const scaleX = (day: number) =>
    padding.left + ((day - minDay) / (maxDay - minDay)) * (chartWidth - padding.left - padding.right)

  const scaleY = (score: number) =>
    chartHeight - padding.bottom - ((score - minScore) / (maxScore - minScore)) * (chartHeight - padding.top - padding.bottom)

  // Construct SVG Path for Main Trajectory Line
  const points = projectionData.risk_reduction_trajectory
  const lineD = points.reduce((acc, pt, idx) => {
    const x = scaleX(pt.day)
    const y = scaleY(pt.projected_health_score)
    return idx === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`
  }, '')

  // Construct SVG Area for Confidence Band (Upper forward, Lower backward)
  const upperPoints = points.map(pt => `${scaleX(pt.day)},${scaleY(pt.confidence_upper_bound)}`)
  const lowerPoints = [...points].reverse().map(pt => `${scaleX(pt.day)},${scaleY(pt.confidence_lower_bound)}`)
  const areaD = `M ${upperPoints.join(' L ')} L ${lowerPoints.join(' L ')} Z`

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Top Overview Cards: Milestones Summary */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 14
      }}>
        <div className="card" style={{ padding: 18, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.6)' }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase' }}>Baseline Status</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f85149', marginTop: 4 }}>
            {Math.round(projectionData.baseline_health_score)}%
          </div>
          <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 2 }}>Current Health Score (Day 0)</div>
        </div>

        <div className="card" style={{ padding: 18, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.6)' }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase' }}>30-Day Milestone</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#e3b341', marginTop: 4 }}>
            {Math.round(projectionData.projected_30_day_score)}%
          </div>
          <div style={{ fontSize: '0.6875rem', color: '#3fb950', marginTop: 2, fontWeight: 600 }}>
            +{Math.round(projectionData.projected_30_day_score - projectionData.baseline_health_score)}% Improvement
          </div>
        </div>

        <div className="card" style={{ padding: 18, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.6)' }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase' }}>60-Day Milestone</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#388bfd', marginTop: 4 }}>
            {Math.round(projectionData.projected_60_day_score)}%
          </div>
          <div style={{ fontSize: '0.6875rem', color: '#3fb950', marginTop: 2, fontWeight: 600 }}>
            +{Math.round(projectionData.projected_60_day_score - projectionData.baseline_health_score)}% Improvement
          </div>
        </div>

        <div className="card" style={{ padding: 18, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.6)' }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#3fb950', textTransform: 'uppercase' }}>90-Day Full Recovery</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#3fb950', marginTop: 4 }}>
            {Math.round(projectionData.projected_90_day_score)}%
          </div>
          <div style={{ fontSize: '0.6875rem', color: '#3fb950', marginTop: 2, fontWeight: 600 }}>
            {Math.round(projectionData.overall_recovery_probability_90d * 100)}% Overall Probability
          </div>
        </div>
      </div>

      {/* Main Trajectory Chart & Confidence Band */}
      <div className="card" style={{ padding: 24, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.65)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <TrendingUp size={20} color="var(--c-primary)" />
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--c-secondary)', margin: 0 }}>
                90-Day Recovery Trajectory & Physiological Saturation Curve
              </h3>
              <p style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', margin: '2px 0 0 0' }}>
                Mathematical model calibrated on erythrocyte half-life (120d) and tissue repletion kinetics.
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 14, height: 3, background: 'var(--c-primary)' }} />
              Expected Trajectory
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 14, height: 10, background: 'rgba(56, 139, 253, 0.18)', borderRadius: 2 }} />
              &plusmn;7.5% Confidence Band
            </span>
          </div>
        </div>

        {/* Responsive SVG Chart */}
        <div style={{ width: '100%', overflowX: 'auto' }}>
          <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: '100%', maxHeight: 240, overflow: 'visible' }}>
            <defs>
              <linearGradient id="confidenceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#388bfd" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#388bfd" stopOpacity="0.05" />
              </linearGradient>
            </defs>

            {/* Horizontal Grid lines */}
            {[40, 60, 80, 100].map(val => (
              <g key={val}>
                <line
                  x1={padding.left}
                  y1={scaleY(val)}
                  x2={chartWidth - padding.right}
                  y2={scaleY(val)}
                  stroke="rgba(48, 54, 61, 0.4)"
                  strokeDasharray="4 4"
                />
                <text
                  x={padding.left - 8}
                  y={scaleY(val) + 4}
                  fill="var(--c-muted)"
                  fontSize="10"
                  textAnchor="end"
                >
                  {val}%
                </text>
              </g>
            ))}

            {/* Vertical Day Grid lines */}
            {[0, 14, 30, 60, 90].map(day => (
              <g key={day}>
                <line
                  x1={scaleX(day)}
                  y1={padding.top}
                  x2={scaleX(day)}
                  y2={chartHeight - padding.bottom}
                  stroke="rgba(48, 54, 61, 0.4)"
                />
                <text
                  x={scaleX(day)}
                  y={chartHeight - padding.bottom + 16}
                  fill="var(--c-muted)"
                  fontSize="10"
                  textAnchor="middle"
                >
                  Day {day}
                </text>
              </g>
            ))}

            {/* Shaded Confidence Band */}
            <path d={areaD} fill="url(#confidenceGrad)" />

            {/* Main Trajectory Line */}
            <path d={lineD} fill="none" stroke="var(--c-primary)" strokeWidth="3" strokeLinecap="round" />

            {/* Trajectory Points */}
            {points.map(pt => (
              <circle
                key={pt.day}
                cx={scaleX(pt.day)}
                cy={scaleY(pt.projected_health_score)}
                r="4.5"
                fill="var(--c-primary)"
                stroke="var(--c-bg-primary)"
                strokeWidth="2"
              />
            ))}
          </svg>
        </div>
      </div>

      {/* Physiological Milestones & Nutrient Probability Matrix */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(300px, 1fr)', gap: 20 }}>
        {/* Left Column: 4 Milestone Checkpoints */}
        <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)' }}>
          <div style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 14 }}>
            Physiological Milestone Checkpoints
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {projectionData.milestones.map(m => {
              const isSelected = selectedMilestone === m.day
              return (
                <div
                  key={m.day}
                  onClick={() => setSelectedMilestone(m.day)}
                  style={{
                    padding: '14px 16px',
                    borderRadius: 8,
                    background: isSelected ? 'rgba(56, 139, 253, 0.12)' : 'rgba(13, 17, 23, 0.6)',
                    border: isSelected ? '1px solid var(--c-primary)' : '1px solid rgba(48, 54, 61, 0.5)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{
                        fontSize: '0.6875rem',
                        fontWeight: 800,
                        color: 'white',
                        background: 'var(--c-primary)',
                        padding: '2px 8px',
                        borderRadius: 4
                      }}>
                        Day {m.day}
                      </span>
                      <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                        {m.milestone_name}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#3fb950' }}>
                      {Math.round(m.health_score_target)}% Score
                    </span>
                  </div>

                  <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', margin: '0 0 8px 0', lineHeight: 1.4 }}>
                    {m.biological_mechanism}
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    {m.expected_symptom_relief.map((s, idx) => (
                      <div key={idx} style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <CheckCircle2 size={12} color="#3fb950" />
                        <span>{s}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Column: Per-Nutrient Recovery Probability */}
        <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)', display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
            Per-Nutrient Recovery Probability (30d / 60d / 90d)
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {projectionData.nutrient_probabilities.map(np => (
              <div
                key={np.nutrient_code}
                style={{
                  padding: '12px 14px',
                  background: 'rgba(13, 17, 23, 0.6)',
                  borderRadius: 8,
                  border: '1px solid rgba(48, 54, 61, 0.4)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                    {np.common_name}
                  </span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#3fb950' }}>
                    {Math.round(np.day_90_probability * 100)}% 90d
                  </span>
                </div>

                {/* 3 Step Probability Bars */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginBottom: 8 }}>
                  <div style={{ padding: '6px 8px', background: 'rgba(22, 27, 34, 0.8)', borderRadius: 4, textAlign: 'center' }}>
                    <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)' }}>30 Days</div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                      {Math.round(np.day_30_probability * 100)}%
                    </div>
                  </div>
                  <div style={{ padding: '6px 8px', background: 'rgba(22, 27, 34, 0.8)', borderRadius: 4, textAlign: 'center' }}>
                    <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)' }}>60 Days</div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                      {Math.round(np.day_60_probability * 100)}%
                    </div>
                  </div>
                  <div style={{ padding: '6px 8px', background: 'rgba(22, 27, 34, 0.8)', borderRadius: 4, textAlign: 'center' }}>
                    <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)' }}>90 Days</div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#3fb950' }}>
                      {Math.round(np.day_90_probability * 100)}%
                    </div>
                  </div>
                </div>

                <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', lineHeight: 1.4 }}>
                  <strong>Rate-Limiting Factor:</strong> {np.primary_limiting_factor}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
