import React, { useState } from 'react'
import { motion, type Variants } from 'framer-motion'
import { ArrowRight, RefreshCw, CheckCircle, AlertCircle, ChefHat, Sparkles, ShieldCheck } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface NutrientDeltaItem {
  nutrient_name: string
  original_value: number
  substitute_value: number
  delta_value: number
  percentage_change: number
  unit: string
  clinical_interpretation: string
}

interface FoodSubstitutionItem {
  substitution_id: string
  original_food: string
  substitute_food: string
  primary_purpose: string
  macronutrient_differences: Record<string, string>
  nutrient_deltas: NutrientDeltaItem[]
  bioavailability_change_description: string
  bioavailability_multiplier_delta: number
  clinical_tradeoffs: string[]
  culinary_preparation_tips: string
  recommended_for_deficiencies: string[]
}

interface Props {
  substitutions: FoodSubstitutionItem[]
}

export default function FoodSwapExplorer({ substitutions }: Props) {
  const [selectedId, setSelectedId] = useState<string>(
    substitutions[0]?.substitution_id || 'spinach_to_kale'
  )

  const activeSwap = substitutions.find(s => s.substitution_id === selectedId) || substitutions[0]

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Horizontal Swap Selector Pill Carousel */}
      <div style={{
        display: 'flex',
        gap: 10,
        overflowX: 'auto',
        paddingBottom: 4
      }}>
        {substitutions.map(swap => {
          const isSelected = swap.substitution_id === selectedId
          return (
            <button
              key={swap.substitution_id}
              onClick={() => setSelectedId(swap.substitution_id)}
              style={{
                padding: '10px 16px',
                borderRadius: 8,
                border: isSelected ? '1px solid var(--c-primary)' : '1px solid rgba(48, 54, 61, 0.6)',
                background: isSelected ? 'rgba(56, 139, 253, 0.15)' : 'rgba(22, 27, 34, 0.75)',
                color: isSelected ? 'var(--c-secondary)' : 'var(--c-muted)',
                cursor: 'pointer',
                textAlign: 'left',
                minWidth: 200,
                display: 'flex',
                flexDirection: 'column',
                gap: 4,
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', fontWeight: 700, color: isSelected ? 'var(--c-primary)' : 'var(--c-secondary)' }}>
                <span>{swap.original_food.split('/')[0].split('(')[0]}</span>
                <ArrowRight size={12} />
                <span>{swap.substitute_food.split('&')[0].split('(')[0]}</span>
              </div>
              <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {swap.primary_purpose}
              </div>
            </button>
          )
        })}
      </div>

      {activeSwap && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(340px, 1.2fr) minmax(300px, 1fr)', gap: 20 }}>
          {/* Left Column: Side-by-Side Comparison & Nutrient Deltas */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Header Box */}
            <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)' }}>
              <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
                Smart Clinical Substitution
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-secondary)', margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: 10 }}>
                <span>{activeSwap.original_food}</span>
                <ArrowRight size={18} color="var(--c-primary)" />
                <span style={{ color: '#3fb950' }}>{activeSwap.substitute_food}</span>
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', margin: 0, lineHeight: 1.5 }}>
                {activeSwap.primary_purpose}
              </p>

              {/* Recommended Deficiencies Badges */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 14 }}>
                <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', alignSelf: 'center', marginRight: 4 }}>Target Deficits:</span>
                {activeSwap.recommended_for_deficiencies.map(nut => (
                  <span
                    key={nut}
                    style={{
                      fontSize: '0.625rem',
                      fontWeight: 700,
                      color: '#a371f7',
                      background: 'rgba(163, 113, 247, 0.12)',
                      border: '1px solid rgba(163, 113, 247, 0.3)',
                      padding: '2px 7px',
                      borderRadius: 4
                    }}
                  >
                    {nut}
                  </span>
                ))}
              </div>
            </div>

            {/* Macronutrient Comparison Row */}
            <div className="card" style={{ padding: 18, background: 'rgba(13, 17, 23, 0.75)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 12 }}>
                Macronutrient Differentials
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
                {Object.entries(activeSwap.macronutrient_differences).map(([macro, val]) => (
                  <div key={macro} style={{ padding: '8px 12px', background: 'rgba(22, 27, 34, 0.8)', borderRadius: 6, border: '1px solid rgba(48, 54, 61, 0.5)' }}>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', textTransform: 'capitalize' }}>
                      {macro.replace('_', ' ')}
                    </div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-secondary)', marginTop: 2 }}>
                      {val}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Micronutrient Deltas Detail List */}
            <div className="card" style={{ padding: 20, background: 'rgba(22, 27, 34, 0.85)' }}>
              <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 14 }}>
                Micronutrient & Antinutrient Differentials
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {activeSwap.nutrient_deltas.map(delta => {
                  const isPositive = delta.delta_value > 0
                  const isAntinutrient = delta.nutrient_name.toLowerCase().includes('oxalic') || delta.nutrient_name.toLowerCase().includes('metal') || delta.nutrient_name.toLowerCase().includes('mercury')
                  const isFavorable = isAntinutrient ? !isPositive : isPositive

                  return (
                    <div
                      key={delta.nutrient_name}
                      style={{
                        padding: '12px 14px',
                        background: 'rgba(13, 17, 23, 0.6)',
                        borderRadius: 8,
                        border: '1px solid rgba(48, 54, 61, 0.5)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                        <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                          {delta.nutrient_name}
                        </span>
                        <span style={{
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          color: isFavorable ? '#3fb950' : '#f85149',
                          background: isFavorable ? 'rgba(63, 185, 80, 0.12)' : 'rgba(248, 81, 73, 0.12)',
                          padding: '2px 8px',
                          borderRadius: 4
                        }}>
                          {isPositive ? `+${delta.percentage_change}%` : `${delta.percentage_change}%`}
                        </span>
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)', marginBottom: 6 }}>
                        <span>Original: <strong>{delta.original_value} {delta.unit}</strong></span>
                        <span>Substitute: <strong style={{ color: 'var(--c-secondary)' }}>{delta.substitute_value} {delta.unit}</strong></span>
                        <span>Net Delta: <strong>{delta.delta_value > 0 ? `+${delta.delta_value}` : delta.delta_value} {delta.unit}</strong></span>
                      </div>

                      <div style={{ fontSize: '0.6875rem', color: 'var(--c-text-secondary)', lineHeight: 1.4 }}>
                        {delta.clinical_interpretation}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Bioavailability Shifts, Clinical Tradeoffs & Culinary Preparation */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Bioavailability Shift Banner */}
            <div className="card" style={{
              padding: 22,
              background: 'linear-gradient(135deg, rgba(56, 139, 253, 0.1) 0%, rgba(13, 17, 23, 0.8) 100%)',
              border: '1px solid rgba(56, 139, 253, 0.4)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <Sparkles size={18} color="var(--c-primary)" />
                <span style={{ fontSize: '0.875rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                  Intestinal Bioavailability Dynamics
                </span>
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.5, margin: 0 }}>
                {activeSwap.bioavailability_change_description}
              </p>
            </div>

            {/* Clinical Tradeoffs */}
            <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
                <ShieldCheck size={18} color="#3fb950" />
                <span style={{ fontSize: '0.875rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                  Clinical Evaluation & Tradeoffs
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {activeSwap.clinical_tradeoffs.map((tradeoff, idx) => {
                  const isPro = tradeoff.includes('Clinical Pro')
                  return (
                    <div
                      key={idx}
                      style={{
                        padding: '10px 12px',
                        background: isPro ? 'rgba(63, 185, 80, 0.08)' : 'rgba(210, 153, 34, 0.08)',
                        borderLeft: isPro ? '3px solid #3fb950' : '3px solid #d29922',
                        borderRadius: '0 6px 6px 0',
                        fontSize: '0.75rem',
                        color: 'var(--c-secondary)',
                        lineHeight: 1.45
                      }}
                    >
                      {tradeoff}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Culinary Preparation Tips */}
            <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <ChefHat size={18} color="#e3b341" />
                <span style={{ fontSize: '0.875rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                  Culinary Preparation Guidelines
                </span>
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.55, margin: 0 }}>
                {activeSwap.culinary_preparation_tips}
              </p>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}
