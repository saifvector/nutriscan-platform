import { motion } from 'framer-motion'
import { GitCompare, ArrowRight, TrendingUp, CheckCircle, Sparkles, ArrowDownRight, Award } from 'lucide-react'

export interface NutrientComparisonItemData {
  nutrient: string
  base_risk_score: number
  target_risk_score: number
  absolute_change: number
  relative_change_pct: number
  trend: string
  status: string
}

interface ComparisonDashboardProps {
  baseDate?: string
  baseScore?: number
  targetDate?: string
  targetScore?: number
  scoreDelta?: number
  comparisons?: NutrientComparisonItemData[]
  keyInsights?: string[]
  summaryText?: string
}

export default function ComparisonDashboard({
  baseDate = '2026-08-10',
  baseScore = 62,
  targetDate = '2026-09-10',
  targetScore = 76,
  scoreDelta = 14,
  comparisons = [
    { nutrient: 'Vitamin D', base_risk_score: 87, target_risk_score: 52, absolute_change: -35, relative_change_pct: 40.2, trend: 'Improving', status: 'Reduced by 35%' },
    { nutrient: 'Iron', base_risk_score: 71, target_risk_score: 43, absolute_change: -28, relative_change_pct: 39.4, trend: 'Improving', status: 'Reduced by 28%' },
    { nutrient: 'Vitamin B12', base_risk_score: 63, target_risk_score: 29, absolute_change: -34, relative_change_pct: 54.0, trend: 'Improving', status: 'Resolved / Normal' },
    { nutrient: 'Calcium', base_risk_score: 60, target_risk_score: 44, absolute_change: -16, relative_change_pct: 26.7, trend: 'Improving', status: 'Reduced by 16%' },
    { nutrient: 'Magnesium', base_risk_score: 54, target_risk_score: 38, absolute_change: -16, relative_change_pct: 29.6, trend: 'Improving', status: 'Reduced by 16%' },
    { nutrient: 'Folate', base_risk_score: 48, target_risk_score: 32, absolute_change: -16, relative_change_pct: 33.3, trend: 'Improving', status: 'Reduced by 16%' },
    { nutrient: 'Zinc', base_risk_score: 45, target_risk_score: 31, absolute_change: -14, relative_change_pct: 31.1, trend: 'Improving', status: 'Reduced by 14%' },
  ],
  keyInsights = [
    'Overall health score advanced by +14 points (62 → 76, Good category).',
    'Vitamin D deficiency probability experienced steep recovery from 87% to 52%.',
    'Iron risk dropped from 71% to 43% under synergistic Vitamin C food pairings.',
    'Vitamin B12 achieved clinical resolution (63% → 29%), restoring neural methylation cofactor capacity.'
  ],
  summaryText = 'Longitudinal comparison confirms significant therapeutic progress across all primary biomarker targets. Compounding risks from multi-deficiency interactions have been attenuated.',
}: ComparisonDashboardProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Top Banner: Side-by-Side Session Delta */}
      <div style={{
        background: 'var(--c-card)',
        border: '1px solid var(--c-border)',
        borderRadius: 20,
        padding: '24px 28px',
        boxShadow: 'var(--c-shadow-sm)',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 14,
            background: 'var(--c-surface-tint)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <GitCompare size={24} color="var(--c-primary)" />
          </div>
          <div>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--c-text)', margin: 0 }}>
              Side-by-Side Assessment Comparison
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', margin: '4px 0 0' }}>
              Direct before-and-after comparison evaluating clinical efficacy of dietary & lifestyle interventions.
            </p>
          </div>
        </div>

        {/* Score Progression Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 16,
          padding: '12px 20px',
          borderRadius: 14,
          background: 'var(--c-surface-alt)',
          border: '1px solid var(--c-border-light)',
        }}>
          <div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase' }}>Baseline ({baseDate})</div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-text)' }}>{baseScore} pts</div>
          </div>

          <ArrowRight size={18} color="var(--c-muted)" />

          <div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase' }}>Current ({targetDate})</div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-primary)' }}>{targetScore} pts</div>
          </div>

          <div style={{
            padding: '4px 10px',
            borderRadius: 20,
            background: 'rgba(34, 197, 94, 0.12)',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            fontSize: '0.8125rem',
            fontWeight: 800,
            color: 'var(--c-success)',
          }}>
            +{scoreDelta} pts
          </div>
        </div>
      </div>

      {/* Grid of Side-by-Side Comparisons */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: 14,
      }}>
        {comparisons.map((c, idx) => (
          <motion.div
            key={c.nutrient}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: idx * 0.04 }}
            style={{
              background: 'var(--c-card)',
              border: '1px solid var(--c-border)',
              borderRadius: 16,
              padding: '18px 20px',
              boxShadow: 'var(--c-shadow-sm)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <span style={{ fontFamily: 'var(--font-heading)', fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-text)' }}>
                {c.nutrient}
              </span>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4,
                padding: '3px 8px',
                borderRadius: 8,
                background: 'rgba(34, 197, 94, 0.12)',
                color: 'var(--c-success)',
                fontSize: '0.75rem',
                fontWeight: 700,
              }}>
                <ArrowDownRight size={12} />
                {c.absolute_change}%
              </span>
            </div>

            {/* Visual Risk Transition */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <div style={{ textAlign: 'left' }}>
                <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', display: 'block' }}>Baseline</span>
                <span style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '1.25rem',
                  fontWeight: 800,
                  color: c.base_risk_score >= 65 ? 'var(--c-danger)' : '#F97316',
                }}>
                  {c.base_risk_score}%
                </span>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '4px 10px',
                borderRadius: 20,
                background: 'var(--c-surface-alt)',
                border: '1px solid var(--c-border-light)',
                fontSize: '0.6875rem',
                color: 'var(--c-muted)',
              }}>
                <ArrowRight size={12} />
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', display: 'block' }}>Current</span>
                <span style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '1.25rem',
                  fontWeight: 800,
                  color: c.target_risk_score < 35 ? 'var(--c-success)' : 'var(--c-primary)',
                }}>
                  {c.target_risk_score}%
                </span>
              </div>
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.4 }}>
              Status: <b style={{ color: 'var(--c-text-secondary)' }}>{c.status}</b>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Automated AI Health Insights Box */}
      <div style={{
        background: 'var(--c-card)',
        border: '1px solid var(--c-border)',
        borderRadius: 20,
        padding: '24px 28px',
        boxShadow: 'var(--c-shadow-sm)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <Sparkles size={18} color="var(--c-primary)" />
          <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1rem', fontWeight: 700, color: 'var(--c-text)', margin: 0 }}>
            Automated Clinical Health Insights
          </h4>
        </div>

        <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.6, marginBottom: 16 }}>
          {summaryText}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 10 }}>
          {keyInsights.map((insight, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 10,
                padding: '12px 16px',
                borderRadius: 12,
                background: 'var(--c-surface-alt)',
                border: '1px solid var(--c-border-light)',
              }}
            >
              <CheckCircle size={15} color="var(--c-success)" style={{ flexShrink: 0, marginTop: 2 }} />
              <span style={{ fontSize: '0.75rem', color: 'var(--c-text)', lineHeight: 1.45 }}>
                {insight}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
