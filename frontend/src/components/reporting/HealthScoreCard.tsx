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
  // Validate whether score has been computed (> 0 and valid number)
  const isScoreValid = typeof score === 'number' && !isNaN(score) && score > 0
  const effectiveScore = isScoreValid ? Math.min(100, Math.max(0, Math.round(score))) : 0

  // Category styling based on 5-tier standard, strictly synchronized with score
  const getCategoryConfig = (cat: string, scoreVal: number, valid: boolean) => {
    // Uninitialized / missing score handling
    if (!valid || scoreVal <= 0) {
      return {
        label: 'Awaiting Calculation',
        color: 'var(--c-muted)',
        bg: 'rgba(148, 163, 184, 0.12)',
        border: 'rgba(148, 163, 184, 0.25)',
        icon: Activity,
      }
    }

    const normCat = (cat || '').toUpperCase()

    // 5-tier standard synchronized with OverallNutritionalHealthScorer:
    // 90 - 100: EXCELLENT
    // 70 - 89:  GOOD
    // 50 - 69:  MODERATE_RISK
    // 30 - 49:  HIGH_RISK
    // < 30:     CRITICAL
    if (scoreVal >= 90 || (normCat === 'EXCELLENT' && scoreVal >= 85)) {
      return {
        label: 'Excellent Status',
        color: 'var(--c-success)',
        bg: 'rgba(34, 197, 94, 0.12)',
        border: 'rgba(34, 197, 94, 0.25)',
        icon: CheckCircle
      }
    }
    if (scoreVal >= 70 || (normCat === 'GOOD' && scoreVal >= 65)) {
      return {
        label: 'Good Foundation',
        color: 'var(--c-primary)',
        bg: 'rgba(20, 184, 166, 0.12)',
        border: 'rgba(20, 184, 166, 0.25)',
        icon: Shield
      }
    }
    if (scoreVal >= 50 || (normCat === 'MODERATE_RISK' && scoreVal >= 45)) {
      return {
        label: 'Moderate Risk',
        color: 'var(--c-warning)',
        bg: 'rgba(245, 158, 11, 0.12)',
        border: 'rgba(245, 158, 11, 0.25)',
        icon: Activity
      }
    }
    if (scoreVal >= 30 || (normCat === 'HIGH_RISK' && scoreVal >= 25)) {
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

  const config = getCategoryConfig(category, effectiveScore, isScoreValid)
  const CatIcon = config.icon

  // Radial progress calculations
  const radius = 54
  const strokeWidth = 8
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = isScoreValid
    ? circumference - (effectiveScore / 100) * circumference
    : circumference

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
                fontSize: isScoreValid ? '2.25rem' : '1.75rem',
                fontWeight: 800,
                letterSpacing: '-0.03em',
                color: isScoreValid ? 'var(--c-text)' : 'var(--c-muted)',
                lineHeight: 1,
              }}>
                {isScoreValid ? effectiveScore : '—'}
              </span>
              <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: 4 }}>
                {isScoreValid ? '/ 100' : 'PENDING'}
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
        {isScoreValid && breakdown ? (
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
              <span style={{ color: 'var(--c-danger)' }}>Nutrient Deficiencies ({breakdown.deficiency_count ?? 0}):</span>
              <span style={{ fontWeight: 600, color: 'var(--c-danger)' }}>-{Math.abs(breakdown.nutrient_risk_deduction ?? 0).toFixed(1)} pts</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: '#F97316' }}>Biochemical Interactions:</span>
              <span style={{ fontWeight: 600, color: '#F97316' }}>-{Math.abs(breakdown.interaction_penalty ?? 0).toFixed(1)} pts</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--c-success)' }}>Protective Lifestyle ({breakdown.protective_factor_count ?? 0} habits):</span>
              <span style={{ fontWeight: 600, color: 'var(--c-success)' }}>
                {(breakdown.lifestyle_modifier ?? 0) >= 0 ? '+' : ''}{(breakdown.lifestyle_modifier ?? 0).toFixed(1)} pts
              </span>
            </div>

            {breakdown.confidence_adjustment && breakdown.confidence_adjustment > 0 ? (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                <span style={{ color: 'var(--c-primary)' }}>Confidence Weighting:</span>
                <span style={{ fontWeight: 600, color: 'var(--c-primary)' }}>+{breakdown.confidence_adjustment.toFixed(1)} pts</span>
              </div>
            ) : null}
          </div>
        ) : (
          !isScoreValid && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              minWidth: 280,
              flex: 1,
              background: 'var(--c-surface-alt)',
              padding: '16px 20px',
              borderRadius: 14,
              border: '1px dashed var(--c-border-light)',
            }}>
              <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', margin: 0, textAlign: 'center', lineHeight: 1.5 }}>
                Nutritional scoring engine waiting for assessment screening data. Complete or select an active assessment to view factor decomposition.
              </p>
            </div>
          )
        )}
      </div>

      {/* Bottom Clinical Interpretation */}
      {isScoreValid && breakdown?.interpretation && (
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
