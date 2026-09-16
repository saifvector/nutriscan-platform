import React, { useState } from 'react'
import { motion, type Variants } from 'framer-motion'
import { AlertTriangle, CheckCircle2, ShieldAlert, Sparkles, TrendingDown, Layers, PieChart } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface NutrientGapItem {
  nutrient_code: string
  common_name: string
  category: string
  unit: string
  estimated_daily_intake: number
  rda_target: number
  adequacy_percentage: number
  deficit_gap: number
  classification: 'SEVERE_DEFICIT' | 'MODERATE_DEFICIT' | 'OPTIMAL' | 'EXCESS_RISK'
  clinical_urgency_weight: number
  severity_rank: number
  key_dietary_sources: string[]
}

interface DailySummaryItem {
  category: string
  total_nutrients_monitored: number
  optimal_count: number
  moderate_deficit_count: number
  severe_deficit_count: number
  excess_risk_count: number
  average_adequacy_pct: number
}

interface Props {
  gapsData: {
    nutrient_gap_score: number
    status_summary: string
    total_nutrients_evaluated: number
    severe_deficits: NutrientGapItem[]
    moderate_deficits: NutrientGapItem[]
    optimal_nutrients: NutrientGapItem[]
    excess_risk_nutrients: NutrientGapItem[]
    all_gaps: NutrientGapItem[]
    daily_intake_summary: DailySummaryItem[]
  }
}

export default function NutrientGapDashboard({ gapsData }: Props) {
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'SEVERE' | 'MODERATE' | 'OPTIMAL'>('ALL')
  const [selectedNutrient, setSelectedNutrient] = useState<NutrientGapItem | null>(
    gapsData.severe_deficits[0] || gapsData.all_gaps[0] || null
  )

  const filteredGaps = gapsData.all_gaps.filter(g => {
    if (activeFilter === 'SEVERE') return g.classification === 'SEVERE_DEFICIT'
    if (activeFilter === 'MODERATE') return g.classification === 'MODERATE_DEFICIT'
    if (activeFilter === 'OPTIMAL') return g.classification === 'OPTIMAL'
    return true
  })

  const getStatusColor = (cls: string) => {
    switch (cls) {
      case 'SEVERE_DEFICIT': return '#f85149'
      case 'MODERATE_DEFICIT': return '#d29922'
      case 'OPTIMAL': return '#3fb950'
      case 'EXCESS_RISK': return '#a371f7'
      default: return '#8b949e'
    }
  }

  const getStatusBadge = (cls: string) => {
    switch (cls) {
      case 'SEVERE_DEFICIT': return { label: 'Severe Deficit', bg: 'rgba(248, 81, 73, 0.15)', text: '#f85149', icon: AlertTriangle }
      case 'MODERATE_DEFICIT': return { label: 'Moderate Deficit', bg: 'rgba(210, 153, 34, 0.15)', text: '#d29922', icon: TrendingDown }
      case 'OPTIMAL': return { label: 'Optimal Intake', bg: 'rgba(63, 185, 80, 0.15)', text: '#3fb950', icon: CheckCircle2 }
      case 'EXCESS_RISK': return { label: 'Excess Risk', bg: 'rgba(163, 113, 247, 0.15)', text: '#a371f7', icon: ShieldAlert }
      default: return { label: cls, bg: 'rgba(139, 148, 158, 0.15)', text: '#8b949e', icon: Sparkles }
    }
  }

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Top Banner: Score Gauge & Executive Metrics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: 16,
      }}>
        {/* Score Card */}
        <div className="card" style={{
          padding: 24,
          background: 'linear-gradient(135deg, rgba(22, 27, 34, 0.85) 0%, rgba(13, 17, 23, 0.95) 100%)',
          border: '1px solid rgba(48, 54, 61, 0.7)',
          display: 'flex',
          alignItems: 'center',
          gap: 20
        }}>
          <div style={{ position: 'relative', width: 92, height: 92, flexShrink: 0 }}>
            <svg width="92" height="92" viewBox="0 0 92 92">
              <circle cx="46" cy="46" r="38" fill="none" stroke="rgba(48, 54, 61, 0.5)" strokeWidth="8" />
              <circle
                cx="46" cy="46" r="38" fill="none"
                stroke={gapsData.nutrient_gap_score >= 80 ? '#3fb950' : (gapsData.nutrient_gap_score >= 60 ? '#d29922' : '#f85149')}
                strokeWidth="8"
                strokeDasharray={`${(gapsData.nutrient_gap_score / 100) * 238.76} 238.76`}
                strokeLinecap="round"
                transform="rotate(-90 46 46)"
              />
            </svg>
            <div style={{
              position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center'
            }}>
              <span style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                {Math.round(gapsData.nutrient_gap_score)}
              </span>
              <span style={{ fontSize: '0.625rem', color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                / 100
              </span>
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
              Nutrient Sufficiency Index
            </div>
            <div style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 6 }}>
              {gapsData.nutrient_gap_score >= 80 ? 'Optimal Sufficiency' : (gapsData.nutrient_gap_score >= 60 ? 'Moderate Adequacy' : 'Significant Deficit Gaps')}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.4, margin: 0 }}>
              {gapsData.status_summary}
            </p>
          </div>
        </div>

        {/* Severity Metrics Breakdown */}
        <div className="card" style={{
          padding: 24,
          background: 'rgba(22, 27, 34, 0.8)',
          border: '1px solid rgba(48, 54, 61, 0.7)',
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 12,
          alignItems: 'center'
        }}>
          <div style={{ textAlign: 'center', padding: '12px 8px', background: 'rgba(248, 81, 73, 0.08)', borderRadius: 8, border: '1px solid rgba(248, 81, 73, 0.2)' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f85149' }}>
              {gapsData.severe_deficits.length}
            </div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#f85149', marginTop: 2 }}>
              Severe Deficits
            </div>
            <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', marginTop: 2 }}>&lt;50% RDA</div>
          </div>

          <div style={{ textAlign: 'center', padding: '12px 8px', background: 'rgba(210, 153, 34, 0.08)', borderRadius: 8, border: '1px solid rgba(210, 153, 34, 0.2)' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#d29922' }}>
              {gapsData.moderate_deficits.length}
            </div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#d29922', marginTop: 2 }}>
              Moderate Deficits
            </div>
            <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', marginTop: 2 }}>50-80% RDA</div>
          </div>

          <div style={{ textAlign: 'center', padding: '12px 8px', background: 'rgba(63, 185, 80, 0.08)', borderRadius: 8, border: '1px solid rgba(63, 185, 80, 0.2)' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#3fb950' }}>
              {gapsData.optimal_nutrients.length}
            </div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: '#3fb950', marginTop: 2 }}>
              Optimal Target
            </div>
            <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', marginTop: 2 }}>&ge;80% RDA</div>
          </div>
        </div>
      </div>

      {/* Category Summaries */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 12
      }}>
        {gapsData.daily_intake_summary.map(cat => (
          <div key={cat.category} className="card" style={{ padding: '14px 18px', background: 'rgba(13, 17, 23, 0.65)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{cat.category}</span>
              <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: cat.average_adequacy_pct >= 80 ? '#3fb950' : '#d29922' }}>
                {cat.average_adequacy_pct}% Adequacy
              </span>
            </div>
            <div style={{ height: 6, width: '100%', background: 'rgba(48, 54, 61, 0.5)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${Math.min(100, cat.average_adequacy_pct)}%`,
                background: cat.average_adequacy_pct >= 80 ? '#3fb950' : (cat.average_adequacy_pct >= 50 ? '#d29922' : '#f85149'),
                borderRadius: 3
              }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.625rem', color: 'var(--c-muted)', marginTop: 6 }}>
              <span>{cat.total_nutrients_monitored} monitored</span>
              <span>{cat.severe_deficit_count > 0 ? `${cat.severe_deficit_count} severe` : 'All safe'}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Analysis Section: Filter + List + Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.4fr) minmax(280px, 1fr)', gap: 16 }}>
        {/* Left Column: Intake vs RDA List */}
        <div className="card" style={{ padding: 20, background: 'rgba(22, 27, 34, 0.85)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Layers size={18} color="var(--c-primary)" />
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                Intake vs. Recommended Allowance (RDA)
              </span>
            </div>
            {/* Filter Pills */}
            <div style={{ display: 'flex', gap: 4, background: 'rgba(13, 17, 23, 0.7)', padding: 3, borderRadius: 6 }}>
              {(['ALL', 'SEVERE', 'MODERATE', 'OPTIMAL'] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setActiveFilter(f)}
                  style={{
                    padding: '3px 8px',
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    borderRadius: 4,
                    border: 'none',
                    background: activeFilter === f ? 'var(--c-primary)' : 'transparent',
                    color: activeFilter === f ? '#ffffff' : 'var(--c-muted)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {f === 'ALL' ? 'All (18)' : f.charAt(0) + f.slice(1).toLowerCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Nutrient Rows */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 520, overflowY: 'auto', paddingRight: 4 }}>
            {filteredGaps.map(item => {
              const badge = getStatusBadge(item.classification)
              const isSelected = selectedNutrient?.nutrient_code === item.nutrient_code
              const pctClamped = Math.min(100, item.adequacy_percentage)

              return (
                <div
                  key={item.nutrient_code}
                  onClick={() => setSelectedNutrient(item)}
                  style={{
                    padding: '12px 14px',
                    borderRadius: 8,
                    background: isSelected ? 'rgba(56, 139, 253, 0.12)' : 'rgba(13, 17, 23, 0.5)',
                    border: isSelected ? '1px solid rgba(56, 139, 253, 0.4)' : '1px solid rgba(48, 54, 61, 0.4)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <div>
                      <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                        {item.common_name}
                      </span>
                      <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginLeft: 8 }}>
                        Rank #{item.severity_rank}
                      </span>
                    </div>
                    <span style={{
                      fontSize: '0.6875rem',
                      fontWeight: 600,
                      color: badge.text,
                      background: badge.bg,
                      padding: '2px 7px',
                      borderRadius: 4,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4
                    }}>
                      <badge.icon size={11} /> {badge.label}
                    </span>
                  </div>

                  {/* Visual Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ flex: 1, height: 8, background: 'rgba(48, 54, 61, 0.6)', borderRadius: 4, overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${pctClamped}%`,
                        background: getStatusColor(item.classification),
                        borderRadius: 4,
                        transition: 'width 0.4s ease'
                      }} />
                    </div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: getStatusColor(item.classification), minWidth: 42, textAlign: 'right' }}>
                      {item.adequacy_percentage}%
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 6 }}>
                    <span>Estimated Intake: <strong>{item.estimated_daily_intake} {item.unit}</strong></span>
                    <span>Target RDA: <strong>{item.rda_target} {item.unit}</strong></span>
                    {item.deficit_gap > 0 && (
                      <span style={{ color: '#f85149', fontWeight: 600 }}>Gap: -{item.deficit_gap} {item.unit}</span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Column: Selected Nutrient Deep Inspector */}
        <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)', display: 'flex', flexDirection: 'column', gap: 16 }}>
          {selectedNutrient ? (
            <>
              <div style={{ borderBottom: '1px solid rgba(48, 54, 61, 0.6)', paddingBottom: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase' }}>
                      {selectedNutrient.category}
                    </span>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-secondary)', margin: '2px 0 0 0' }}>
                      {selectedNutrient.common_name}
                    </h3>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: getStatusColor(selectedNutrient.classification) }}>
                      {selectedNutrient.adequacy_percentage}%
                    </div>
                    <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)' }}>Adequacy Ratio</div>
                  </div>
                </div>
              </div>

              {/* Stat Matrix */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
                <div style={{ padding: '10px 12px', background: 'rgba(13, 17, 23, 0.6)', borderRadius: 6 }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Estimated Daily Intake</div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginTop: 2 }}>
                    {selectedNutrient.estimated_daily_intake} {selectedNutrient.unit}
                  </div>
                </div>
                <div style={{ padding: '10px 12px', background: 'rgba(13, 17, 23, 0.6)', borderRadius: 6 }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Recommended RDA</div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginTop: 2 }}>
                    {selectedNutrient.rda_target} {selectedNutrient.unit}
                  </div>
                </div>
                <div style={{ padding: '10px 12px', background: 'rgba(13, 17, 23, 0.6)', borderRadius: 6 }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Deficit Gap</div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: selectedNutrient.deficit_gap > 0 ? '#f85149' : '#3fb950', marginTop: 2 }}>
                    {selectedNutrient.deficit_gap > 0 ? `-${selectedNutrient.deficit_gap} ${selectedNutrient.unit}` : 'Zero Gap'}
                  </div>
                </div>
                <div style={{ padding: '10px 12px', background: 'rgba(13, 17, 23, 0.6)', borderRadius: 6 }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Clinical Urgency Weight</div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginTop: 2 }}>
                    {Math.round(selectedNutrient.clinical_urgency_weight * 100)}%
                  </div>
                </div>
              </div>

              {/* Key Food Replenishment Sources */}
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Sparkles size={13} color="var(--c-primary)" />
                  Top USDA FoodData Central Sources
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {selectedNutrient.key_dietary_sources.map((src, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '8px 12px',
                        background: 'rgba(13, 17, 23, 0.5)',
                        borderRadius: 6,
                        border: '1px solid rgba(48, 54, 61, 0.4)',
                        fontSize: '0.75rem',
                        color: 'var(--c-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8
                      }}
                    >
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--c-primary)' }} />
                      {src}
                    </div>
                  ))}
                </div>
              </div>

              <div style={{
                marginTop: 'auto',
                padding: '10px 12px',
                background: 'rgba(56, 139, 253, 0.08)',
                border: '1px solid rgba(56, 139, 253, 0.25)',
                borderRadius: 6,
                fontSize: '0.6875rem',
                color: 'var(--c-muted)',
                lineHeight: 1.4
              }}>
                <strong>Clinical Note:</strong> RDA represents the average daily dietary intake level sufficient to meet the nutrient requirements of 97–98% of healthy individuals (NIH ODS Reference).
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--c-muted)', padding: 40 }}>
              Select a nutrient from the left to view detailed clinical gap analysis.
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
