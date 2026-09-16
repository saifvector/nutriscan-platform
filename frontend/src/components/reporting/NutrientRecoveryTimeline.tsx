import { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, Clock, AlertTriangle, ArrowDownRight, ArrowRight, ArrowUpRight, Filter } from 'lucide-react'

export interface NutrientRecoveryItemData {
  nutrient: string
  initial_risk_score: number
  current_risk_score: number
  improvement_percentage: number
  recovery_trend: string
  recovery_status: string
  initial_risk_level?: string
  current_risk_level?: string
  recommended_action?: string
}

interface NutrientRecoveryTimelineProps {
  items: NutrientRecoveryItemData[]
}

export default function NutrientRecoveryTimeline({ items }: NutrientRecoveryTimelineProps) {
  const [filter, setFilter] = useState<'ALL' | 'IMPROVING' | 'RESOLVED' | 'ATTENTION'>('ALL')

  const getTrendBadge = (trend: string) => {
    switch (trend) {
      case 'Improving':
        return { color: 'var(--c-success)', bg: 'rgba(34, 197, 94, 0.12)', icon: ArrowDownRight }
      case 'Stable':
        return { color: 'var(--c-muted)', bg: 'var(--c-surface-alt)', icon: ArrowRight }
      case 'Critical':
        return { color: 'var(--c-danger)', bg: 'rgba(239, 68, 68, 0.12)', icon: AlertTriangle }
      default:
        return { color: '#F97316', bg: 'rgba(249, 115, 22, 0.12)', icon: ArrowUpRight }
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Resolved':
        return { color: 'var(--c-success)', border: 'rgba(34, 197, 94, 0.3)', bg: 'rgba(34, 197, 94, 0.08)' }
      case 'On Track':
        return { color: 'var(--c-primary)', border: 'rgba(20, 184, 166, 0.3)', bg: 'rgba(20, 184, 166, 0.08)' }
      case 'Action Required':
        return { color: 'var(--c-danger)', border: 'rgba(239, 68, 68, 0.3)', bg: 'rgba(239, 68, 68, 0.08)' }
      default:
        return { color: 'var(--c-warning)', border: 'rgba(245, 158, 11, 0.3)', bg: 'rgba(245, 158, 11, 0.08)' }
    }
  }

  const filteredItems = items.filter(item => {
    if (filter === 'IMPROVING') return item.recovery_trend === 'Improving'
    if (filter === 'RESOLVED') return item.recovery_status === 'Resolved'
    if (filter === 'ATTENTION') return item.recovery_status === 'Needs Attention' || item.recovery_status === 'Action Required'
    return true
  })

  return (
    <div style={{
      background: 'var(--c-card)',
      border: '1px solid var(--c-border)',
      borderRadius: 20,
      padding: '24px 28px',
      boxShadow: 'var(--c-shadow-sm)',
    }}>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        marginBottom: 20,
        paddingBottom: 16,
        borderBottom: '1px solid var(--c-border-light)',
      }}>
        <div>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-text)', margin: 0 }}>
            Nutrient Recovery Tracker
          </h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', margin: '4px 0 0' }}>
            Biomarker resolution velocity, trend states, and clinical protocol actions across all 11 monitored nutrients.
          </p>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {[
            { id: 'ALL', label: 'All Nutrients (11)' },
            { id: 'IMPROVING', label: 'Improving' },
            { id: 'RESOLVED', label: 'Resolved' },
            { id: 'ATTENTION', label: 'Needs Focus' },
          ].map(btn => (
            <button
              key={btn.id}
              onClick={() => setFilter(btn.id as any)}
              style={{
                padding: '5px 12px',
                borderRadius: 20,
                fontSize: '0.75rem',
                fontWeight: 600,
                border: filter === btn.id ? '1px solid var(--c-primary)' : '1px solid var(--c-border-light)',
                background: filter === btn.id ? 'var(--c-selection-bg)' : 'transparent',
                color: filter === btn.id ? 'var(--c-primary)' : 'var(--c-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {filteredItems.map((item, index) => {
          const trendConfig = getTrendBadge(item.recovery_trend)
          const statusConfig = getStatusBadge(item.recovery_status)
          const TrendIcon = trendConfig.icon

          return (
            <motion.div
              key={item.nutrient}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: index * 0.03 }}
              style={{
                padding: '16px 20px',
                borderRadius: 14,
                background: 'var(--c-surface-alt)',
                border: '1px solid var(--c-border-light)',
                display: 'flex',
                flexWrap: 'wrap',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 16,
              }}
            >
              {/* Nutrient and status */}
              <div style={{ minWidth: 200 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span style={{ fontFamily: 'var(--font-heading)', fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-text)' }}>
                    {item.nutrient}
                  </span>
                  <span style={{
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 12,
                    background: statusConfig.bg,
                    border: `1px solid ${statusConfig.border}`,
                    color: statusConfig.color,
                  }}>
                    {item.recovery_status}
                  </span>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', margin: 0, lineHeight: 1.4 }}>
                  {item.recommended_action || 'Continue optimal whole food rotation and sunlight habits.'}
                </p>
              </div>

              {/* Progress Bar & Scores */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 20, flex: 1, minWidth: 220, maxWidth: 400 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 4 }}>
                    <span style={{ color: 'var(--c-muted)' }}>Initial: <b style={{ color: 'var(--c-text-secondary)' }}>{item.initial_risk_score}%</b></span>
                    <span style={{ color: 'var(--c-muted)' }}>Current: <b style={{ color: item.current_risk_score > 60 ? 'var(--c-danger)' : 'var(--c-text)' }}>{item.current_risk_score}%</b></span>
                  </div>
                  {/* Progress bar */}
                  <div style={{ height: 6, borderRadius: 3, background: 'var(--c-bar-track)', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${item.current_risk_score}%`,
                      borderRadius: 3,
                      background: item.current_risk_score >= 65 ? 'var(--c-danger)' : (item.current_risk_score >= 40 ? 'var(--c-warning)' : 'var(--c-success)'),
                      transition: 'width 0.8s ease-out',
                    }} />
                  </div>
                </div>

                {/* Delta Badge */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  padding: '4px 10px',
                  borderRadius: 8,
                  background: trendConfig.bg,
                  color: trendConfig.color,
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  whiteSpace: 'nowrap',
                }}>
                  <TrendIcon size={13} />
                  {item.improvement_percentage > 0 ? `-${item.improvement_percentage}%` : `+${Math.abs(item.improvement_percentage)}%`}
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
