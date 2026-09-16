import { motion } from 'framer-motion'
import { Shield, Sparkles, Activity, AlertTriangle, CheckCircle, Flame } from 'lucide-react'

interface HealthScoreCardProps {
  score: number
  category: string
  breakdown?: {
    baseline_score: number
    nutrient_risk_deduction: number
    interaction_penalty: number
    lifestyle_modifier: number
    confidence_adjustment?: number
    deficiency_count?: number
    protective_factor_count?: number
    interpretation: string
  }
}

export default function HealthScoreCard({ score, category, breakdown }: HealthScoreCardProps) {
  // Category styling based on 5-tier standard
  const getCategoryConfig = (cat: string, scoreVal: number) => {
    if (scoreVal >= 90 || cat === 'EXCELLENT') {
      return {
        label: 'Excellent Status',
        color: 'var(--c-success)',
        bg: 'rgba(34, 197, 94, 0.12)',
        border: 'rgba(34, 197, 94, 0.25)',
        icon: CheckCircle
      }
    }
    if (scoreVal >= 75 || cat === 'GOOD') {
      return {
        label: 'Good Foundation',
        color: 'var(--c-primary)',
        bg: 'rgba(20, 184, 166, 0.12)',
        border: 'rgba(20, 184, 166, 0.25)',
        icon: Shield
      }
    }
    if (scoreVal >= 60 || cat === 'MODERATE_RISK') {
      return {
        label: 'Moderate Risk',
        color: 'var(--c-warning)',
        bg: 'rgba(245, 158, 11, 0.12)',
        border: 'rgba(245, 158, 11, 0.25)',
        icon: Activity
      }
    }
    if (scoreVal >= 40 || cat === 'HIGH_RISK') {
      return {
        label: 'High Risk',
        color: '#F97316',
        bg: 'rgba(249, 115, 22, 0.12)',
        border: 'rgba(249, 115, 22, 0.25)',
        icon: AlertTriangle
      }
    }
    return {
      label: 'Critical Deficiency',
      color: 'var(--c-danger)',
      bg: 'rgba(239, 68, 68, 0.12)',
      border: 'rgba(239, 68, 68, 0.25)',
      icon: Flame
    }
  }

  const config = getCategoryConfig(category, score)
  const CatIcon = config.icon

  // Radial progress calculations
  const radius = 54
  const strokeWidth = 8
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      style={{
        background: 'var(--c-card)',
        border: '1px solid var(--c-border)',
        borderRadius: 20,
        padding: '28px 32px',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: 'var(--c-shadow-sm)',
      }}
    >
      {/* Background glow */}
      <div style={{
        position: 'absolute',
        top: -60,
        right: -60,
        width: 180,
        height: 180,
        borderRadius: '50%',
        background: config.color,
        opacity: 0.05,
        filter: 'blur(40px)',
        pointerEvents: 'none',
      }} />

      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 24 }}>
        {/* Left: Score Gauge & Tier Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <div style={{ position: 'relative', width: 128, height: 128 }}>
            <svg width={128} height={128} style={{ transform: 'rotate(-90deg)' }}>
              {/* Background ring */}
              <circle
                cx={64}
                cy={64}
                r={radius}
                fill="none"
                stroke="var(--c-border-light)"
                strokeWidth={strokeWidth}
              />
              {/* Progress ring */}
              <circle
                cx={64}
                cy={64}
                r={radius}
                fill="none"
                stroke={config.color}
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 1s ease-out' }}
              />
            </svg>
            <div style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <span style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '2.25rem',
                fontWeight: 800,
                letterSpacing: '-0.03em',
                color: 'var(--c-text)',
                lineHeight: 1,
              }}>
                {score}
              </span>
              <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: 4 }}>
                / 100
              </span>
            </div>
          </div>

          <div>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '4px 12px',
              borderRadius: 20,
              background: config.bg,
              border: `1px solid ${config.border}`,
              marginBottom: 8,
            }}>
              <CatIcon size={14} color={config.color} />
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: config.color, letterSpacing: '0.02em' }}>
                {config.label}
              </span>
            </div>

            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--c-text)', marginBottom: 4 }}>
              Nutritional Health Score
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', maxWidth: 360, lineHeight: 1.5 }}>
              Standardized 0–100 composite synthesizing 11-nutrient biomarker risks, interaction multipliers, and protective lifestyle habits.
            </p>
          </div>
        </div>

        {/* Right: Breakdown Decomposition Bars */}
        {breakdown && (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            minWidth: 280,
            flex: 1,
            background: 'var(--c-surface-alt)',
            padding: '16px 20px',
            borderRadius: 14,
            border: '1px solid var(--c-border-light)',
          }}>
            <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 2 }}>
              Score Factor Decomposition
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--c-text-secondary)' }}>Baseline Optimal:</span>
              <span style={{ fontWeight: 600, color: 'var(--c-text)' }}>+100.0 pts</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--c-danger)' }}>Nutrient Deficiencies ({breakdown.deficiency_count || 1}):</span>
              <span style={{ fontWeight: 600, color: 'var(--c-danger)' }}>-{breakdown.nutrient_risk_deduction} pts</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: '#F97316' }}>Biochemical Interactions:</span>
              <span style={{ fontWeight: 600, color: '#F97316' }}>-{breakdown.interaction_penalty} pts</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--c-success)' }}>Protective Lifestyle ({breakdown.protective_factor_count || 4} habits):</span>
              <span style={{ fontWeight: 600, color: 'var(--c-success)' }}>+{breakdown.lifestyle_modifier} pts</span>
            </div>

            {breakdown.confidence_adjustment && breakdown.confidence_adjustment > 0 ? (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                <span style={{ color: 'var(--c-primary)' }}>Confidence Weighting:</span>
                <span style={{ fontWeight: 600, color: 'var(--c-primary)' }}>+{breakdown.confidence_adjustment} pts</span>
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Bottom Clinical Interpretation */}
      {breakdown?.interpretation && (
        <div style={{
          marginTop: 20,
          paddingTop: 16,
          borderTop: '1px solid var(--c-border-light)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: 10,
        }}>
          <Sparkles size={16} color="var(--c-primary)" style={{ flexShrink: 0, marginTop: 2 }} />
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.55, margin: 0 }}>
            {breakdown.interpretation}
          </p>
        </div>
      )}
    </motion.div>
  )
}
