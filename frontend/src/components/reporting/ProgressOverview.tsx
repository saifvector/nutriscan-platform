import { motion } from 'framer-motion'
import { TrendingUp, Zap, CheckCircle2, AlertOctagon, Award, Target, ArrowUpRight } from 'lucide-react'

interface ProgressOverviewProps {
  scoreDelta: number
  improvementPct: number
  recoveryVelocity: number
  resolvedCount: number
  emergingCount: number
  mostImprovedNutrient: string
  highestRiskNutrient: string
  currentScore: number
  baselineScore: number
}

export default function ProgressOverview({
  scoreDelta = 14,
  improvementPct = 22.6,
  recoveryVelocity = 3.5,
  resolvedCount = 2,
  emergingCount = 0,
  mostImprovedNutrient = 'Vitamin B12',
  highestRiskNutrient = 'Vitamin D',
  currentScore = 76,
  baselineScore = 62,
}: ProgressOverviewProps) {
  const cards = [
    {
      label: 'Score Gain',
      value: `+${scoreDelta} pts`,
      sub: `${baselineScore} → ${currentScore} (${improvementPct}% gain)`,
      icon: TrendingUp,
      color: 'var(--c-success)',
      bg: 'rgba(34, 197, 94, 0.10)',
    },
    {
      label: 'Recovery Velocity',
      value: `${recoveryVelocity}`,
      unit: 'pts / wk',
      sub: 'Consistent upward momentum',
      icon: Zap,
      color: 'var(--c-primary)',
      bg: 'rgba(20, 184, 166, 0.10)',
    },
    {
      label: 'Deficiencies Resolved',
      value: `${resolvedCount}`,
      unit: 'restored',
      sub: 'Vitamin B12, Zinc now optimal',
      icon: CheckCircle2,
      color: 'var(--c-success)',
      bg: 'rgba(34, 197, 94, 0.10)',
    },
    {
      label: 'Emerging Risks',
      value: `${emergingCount}`,
      unit: 'flags',
      sub: 'Zero new depletions detected',
      icon: AlertOctagon,
      color: emergingCount > 0 ? 'var(--c-danger)' : 'var(--c-muted)',
      bg: emergingCount > 0 ? 'rgba(239, 68, 68, 0.10)' : 'var(--c-surface-alt)',
    },
    {
      label: 'Most Improved',
      value: mostImprovedNutrient,
      sub: '+54.0% deficiency reduction',
      icon: Award,
      color: 'var(--c-accent)',
      bg: 'rgba(244, 185, 66, 0.10)',
    },
    {
      label: 'Primary Focus',
      value: highestRiskNutrient,
      sub: 'Current highest residual risk',
      icon: Target,
      color: '#F97316',
      bg: 'rgba(249, 115, 22, 0.10)',
    },
  ]

  return (
    <div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 16,
      }}>
        <div>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-text)', margin: 0 }}>
            Longitudinal Recovery Analytics
          </h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', margin: '4px 0 0' }}>
            Tracking biomarker shifts across sequential screenings over the 30-day monitoring window.
          </p>
        </div>

        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '6px 12px',
          borderRadius: 20,
          background: 'rgba(34, 197, 94, 0.12)',
          border: '1px solid rgba(34, 197, 94, 0.25)',
          fontSize: '0.75rem',
          fontWeight: 700,
          color: 'var(--c-success)',
        }}>
          <ArrowUpRight size={14} />
          Active Recovery Phase
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: 14,
      }}>
        {cards.map((card, idx) => {
          const Icon = card.icon
          return (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              style={{
                background: 'var(--c-card)',
                border: '1px solid var(--c-border)',
                borderRadius: 16,
                padding: '18px 20px',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: 'var(--c-shadow-sm)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {card.label}
                </span>
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: card.bg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Icon size={16} color={card.color} />
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 4 }}>
                <span style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '1.5rem',
                  fontWeight: 800,
                  color: 'var(--c-text)',
                  letterSpacing: '-0.02em',
                }}>
                  {card.value}
                </span>
                {card.unit && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)', fontWeight: 600 }}>
                    {card.unit}
                  </span>
                )}
              </div>

              <p style={{ fontSize: '0.6875rem', color: 'var(--c-text-secondary)', margin: 0 }}>
                {card.sub}
              </p>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
