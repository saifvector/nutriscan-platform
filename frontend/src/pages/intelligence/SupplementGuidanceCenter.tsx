import React from 'react'
import { motion, type Variants } from 'framer-motion'
import { Pill, Clock, AlertTriangle, ShieldCheck, Info, Sparkles, BookOpen } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface SupplementRecommendationItem {
  nutrient_code: string
  nutrient_name: string
  suggested_form: string
  therapeutic_dosage_range: string
  maintenance_dosage_range: string
  optimal_timing: string
  timing_category: 'MORNING_WITH_FAT' | 'MORNING_EMPTY_STOMACH' | 'EVENING_BEFORE_BED' | 'WITH_MAIN_MEAL'
  food_interaction_warnings: string[]
  nutrient_interaction_warnings: string[]
  nih_dsid_reference: string
  contraindications: string[]
  urgency_tier: 'HIGH' | 'MODERATE' | 'LOW'
}

interface Props {
  supplementData: {
    disclaimer: string
    recommended_supplements: SupplementRecommendationItem[]
    general_cautions: string[]
  }
}

export default function SupplementGuidanceCenter({ supplementData }: Props) {
  const getTimingBadge = (cat: string) => {
    switch (cat) {
      case 'MORNING_WITH_FAT':
        return { label: 'Morning with Healthy Fat', bg: 'rgba(227, 179, 65, 0.15)', text: '#e3b341' }
      case 'MORNING_EMPTY_STOMACH':
        return { label: 'Morning on Empty Stomach', bg: 'rgba(56, 139, 253, 0.15)', text: '#388bfd' }
      case 'EVENING_BEFORE_BED':
        return { label: 'Evening (60m Before Bed)', bg: 'rgba(163, 113, 247, 0.15)', text: '#a371f7' }
      case 'WITH_MAIN_MEAL':
        return { label: 'With Substantial Meal', bg: 'rgba(63, 185, 80, 0.15)', text: '#3fb950' }
      default:
        return { label: 'As Directed', bg: 'rgba(139, 148, 158, 0.15)', text: '#8b949e' }
    }
  }

  const getUrgencyBadge = (tier: string) => {
    switch (tier) {
      case 'HIGH':
        return { label: 'High Priority', bg: 'rgba(248, 81, 73, 0.15)', text: '#f85149' }
      case 'MODERATE':
        return { label: 'Moderate Priority', bg: 'rgba(210, 153, 34, 0.15)', text: '#d29922' }
      default:
        return { label: 'Maintenance Support', bg: 'rgba(56, 139, 253, 0.15)', text: '#388bfd' }
    }
  }

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Educational & Non-Prescription Guidance Banner */}
      <div className="card" style={{
        padding: '16px 20px',
        background: 'rgba(56, 139, 253, 0.08)',
        border: '1px solid rgba(56, 139, 253, 0.3)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 14
      }}>
        <Info size={22} color="var(--c-primary)" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <div style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 4, letterSpacing: '0.02em' }}>
            Clinical Decision Support & Educational Guidance Only
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.5, margin: 0 }}>
            {supplementData.disclaimer} Always review therapeutic protocols with a licensed medical practitioner and verify baseline serum levels via certified laboratory testing.
          </p>
        </div>
      </div>

      {/* Supplement Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
        gap: 18
      }}>
        {supplementData.recommended_supplements.map(supp => {
          const timing = getTimingBadge(supp.timing_category)
          const urgency = getUrgencyBadge(supp.urgency_tier)

          return (
            <div
              key={supp.nutrient_code}
              className="card card-hover"
              style={{
                padding: 22,
                background: 'rgba(22, 27, 34, 0.85)',
                border: '1px solid rgba(48, 54, 61, 0.65)',
                display: 'flex',
                flexDirection: 'column',
                gap: 14
              }}
            >
              {/* Header: Name + Priority */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 8,
                    background: 'rgba(56, 139, 253, 0.12)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <Pill size={18} color="var(--c-primary)" />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--c-secondary)', margin: 0 }}>
                      {supp.nutrient_name}
                    </h3>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 2 }}>
                      Form: <strong style={{ color: 'var(--c-secondary)' }}>{supp.suggested_form}</strong>
                    </div>
                  </div>
                </div>
                <span style={{
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  color: urgency.text,
                  background: urgency.bg,
                  padding: '2px 8px',
                  borderRadius: 4
                }}>
                  {urgency.label}
                </span>
              </div>

              {/* Timing Badge */}
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                fontSize: '0.75rem',
                fontWeight: 600,
                color: timing.text,
                background: timing.bg,
                padding: '6px 12px',
                borderRadius: 6,
                width: 'fit-content'
              }}>
                <Clock size={13} />
                <span>{timing.label}</span>
              </div>

              {/* Dosage Boxes */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
                <div style={{ padding: '10px 12px', background: 'rgba(13, 17, 23, 0.6)', borderRadius: 6 }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 600 }}>Therapeutic Range</div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f85149', marginTop: 3 }}>
                    {supp.therapeutic_dosage_range}
                  </div>
                </div>
                <div style={{ padding: '10px 12px', background: 'rgba(13, 17, 23, 0.6)', borderRadius: 6 }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 600 }}>Maintenance Range</div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#3fb950', marginTop: 3 }}>
                    {supp.maintenance_dosage_range}
                  </div>
                </div>
              </div>

              {/* Interaction Warnings */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {supp.food_interaction_warnings.map((warn, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '8px 10px',
                      background: 'rgba(210, 153, 34, 0.08)',
                      borderLeft: '3px solid #d29922',
                      borderRadius: '0 4px 4px 0',
                      fontSize: '0.6875rem',
                      color: 'var(--c-text-secondary)',
                      lineHeight: 1.4
                    }}
                  >
                    <strong>Food Interaction:</strong> {warn}
                  </div>
                ))}
                {supp.nutrient_interaction_warnings.map((warn, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '8px 10px',
                      background: 'rgba(248, 81, 73, 0.08)',
                      borderLeft: '3px solid #f85149',
                      borderRadius: '0 4px 4px 0',
                      fontSize: '0.6875rem',
                      color: 'var(--c-text-secondary)',
                      lineHeight: 1.4
                    }}
                  >
                    <strong>Nutrient Competition:</strong> {warn}
                  </div>
                ))}
              </div>

              {/* Footer: NIH Citation & Contraindications */}
              <div style={{ marginTop: 'auto', paddingTop: 10, borderTop: '1px solid rgba(48, 54, 61, 0.5)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.625rem', color: 'var(--c-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <BookOpen size={11} /> {supp.nih_dsid_reference.split(';')[0]}
                </span>
                <span style={{ fontSize: '0.625rem', color: '#a371f7', fontWeight: 600 }}>
                  {supp.contraindications.length} Contraindication alerts
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* General Clinical Safeguards */}
      <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <ShieldCheck size={18} color="#3fb950" />
          <span style={{ fontSize: '0.875rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
            General Clinical Micronutrient Safeguards
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {supplementData.general_cautions.map((caution, idx) => (
            <div
              key={idx}
              style={{
                fontSize: '0.75rem',
                color: 'var(--c-text-secondary)',
                lineHeight: 1.45,
                display: 'flex',
                alignItems: 'flex-start',
                gap: 8
              }}
            >
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--c-primary)', marginTop: 6, flexShrink: 0 }} />
              <span>{caution}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
