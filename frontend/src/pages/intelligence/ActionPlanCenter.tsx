import React from 'react'
import { motion, type Variants } from 'framer-motion'
import { Target, Zap, Clock, ShieldAlert, CheckCircle2, FlaskConical, Sun, Utensils, BookOpen, AlertCircle } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface ClinicalActionItem {
  priority_level: number
  action_type: 'DIETARY' | 'SUPPLEMENT' | 'LAB_TEST' | 'LIFESTYLE'
  headline: string
  rationale: string
  expected_impact_delta: number
  implementation_timeframe: string
  clinical_guideline_source: string
}

interface Props {
  actionPlanData: {
    clinical_priority_score: number
    highest_impact_intervention: ClinicalActionItem
    fastest_recovery_action: ClinicalActionItem
    ranked_action_plan: ClinicalActionItem[]
    lifestyle_priorities: string[]
    food_priorities: string[]
    laboratory_testing_priorities: Array<{ test_name: string; clinical_indication: string }>
  }
}

export default function ActionPlanCenter({ actionPlanData }: Props) {
  const getActionBadge = (type: string) => {
    switch (type) {
      case 'SUPPLEMENT':
        return { label: 'Supplement Protocol', bg: 'rgba(56, 139, 253, 0.15)', text: '#388bfd' }
      case 'DIETARY':
        return { label: 'Dietary Intervention', bg: 'rgba(63, 185, 80, 0.15)', text: '#3fb950' }
      case 'LAB_TEST':
        return { label: 'Diagnostic Testing', bg: 'rgba(163, 113, 247, 0.15)', text: '#a371f7' }
      case 'LIFESTYLE':
        return { label: 'Lifestyle Modulation', bg: 'rgba(227, 179, 65, 0.15)', text: '#e3b341' }
      default:
        return { label: type, bg: 'rgba(139, 148, 158, 0.15)', text: '#8b949e' }
    }
  }

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Top Banner: Clinical Priority Score & Dual Spotlight Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(240px, 1fr) minmax(280px, 1.3fr) minmax(280px, 1.3fr)',
        gap: 16
      }}>
        {/* Clinical Priority Urgency Score */}
        <div className="card" style={{
          padding: 22,
          background: 'rgba(22, 27, 34, 0.85)',
          border: '1px solid rgba(48, 54, 61, 0.7)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Clinical Priority Index
          </div>
          <div style={{
            fontSize: '2.5rem',
            fontWeight: 900,
            color: actionPlanData.clinical_priority_score >= 70 ? '#f85149' : (actionPlanData.clinical_priority_score >= 45 ? '#d29922' : '#3fb950'),
            margin: '6px 0 2px 0'
          }}>
            {Math.round(actionPlanData.clinical_priority_score)}
          </div>
          <span style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            color: actionPlanData.clinical_priority_score >= 70 ? '#f85149' : '#d29922',
            background: actionPlanData.clinical_priority_score >= 70 ? 'rgba(248, 81, 73, 0.12)' : 'rgba(210, 153, 34, 0.12)',
            padding: '2px 8px',
            borderRadius: 4
          }}>
            {actionPlanData.clinical_priority_score >= 70 ? 'High Clinical Urgency' : 'Moderate Priority'}
          </span>
          <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', marginTop: 8 }}>
            Ranked by multi-nutrient risk & graph centrality
          </div>
        </div>

        {/* Highest Impact Spotlight Card */}
        <div className="card" style={{
          padding: 22,
          background: 'linear-gradient(135deg, rgba(56, 139, 253, 0.12) 0%, rgba(13, 17, 23, 0.9) 100%)',
          border: '1px solid rgba(56, 139, 253, 0.4)',
          display: 'flex',
          flexDirection: 'column',
          gap: 10
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: 800, color: 'var(--c-primary)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Target size={14} /> Highest-Impact Intervention
            </span>
            <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#3fb950', background: 'rgba(63, 185, 80, 0.15)', padding: '2px 6px', borderRadius: 4 }}>
              +{actionPlanData.highest_impact_intervention.expected_impact_delta}% Health Delta
            </span>
          </div>
          <h4 style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--c-secondary)', margin: 0, lineHeight: 1.3 }}>
            {actionPlanData.highest_impact_intervention.headline}
          </h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', margin: 0, lineHeight: 1.45 }}>
            {actionPlanData.highest_impact_intervention.rationale}
          </p>
          <div style={{ marginTop: 'auto', fontSize: '0.6875rem', color: 'var(--c-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Clock size={12} /> {actionPlanData.highest_impact_intervention.implementation_timeframe}
          </div>
        </div>

        {/* Fastest Recovery Spotlight Card */}
        <div className="card" style={{
          padding: 22,
          background: 'linear-gradient(135deg, rgba(227, 179, 65, 0.12) 0%, rgba(13, 17, 23, 0.9) 100%)',
          border: '1px solid rgba(227, 179, 65, 0.4)',
          display: 'flex',
          flexDirection: 'column',
          gap: 10
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: 800, color: '#e3b341', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Zap size={14} /> Fastest Recovery Action
            </span>
            <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: '#e3b341', background: 'rgba(227, 179, 65, 0.15)', padding: '2px 6px', borderRadius: 4 }}>
              Acute Symptom Relief
            </span>
          </div>
          <h4 style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--c-secondary)', margin: 0, lineHeight: 1.3 }}>
            {actionPlanData.fastest_recovery_action.headline}
          </h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', margin: 0, lineHeight: 1.45 }}>
            {actionPlanData.fastest_recovery_action.rationale}
          </p>
          <div style={{ marginTop: 'auto', fontSize: '0.6875rem', color: 'var(--c-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Clock size={12} /> {actionPlanData.fastest_recovery_action.implementation_timeframe}
          </div>
        </div>
      </div>

      {/* Main Section: Ranked Action Plan (Priority 1 through 5) */}
      <div className="card" style={{ padding: 24, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.65)' }}>
        <div style={{ fontSize: '0.875rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 16 }}>
          Sequenced Clinical Action Roadmap (Priority 1 – 5)
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {actionPlanData.ranked_action_plan.map(act => {
            const badge = getActionBadge(act.action_type)
            return (
              <div
                key={act.priority_level}
                style={{
                  padding: '16px 18px',
                  borderRadius: 8,
                  background: 'rgba(13, 17, 23, 0.6)',
                  border: '1px solid rgba(48, 54, 61, 0.5)',
                  display: 'flex',
                  gap: 16,
                  alignItems: 'flex-start'
                }}
              >
                {/* Priority Rank Indicator */}
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  background: act.priority_level === 1 ? '#f85149' : (act.priority_level === 2 ? '#d29922' : 'var(--c-primary)'),
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.875rem',
                  fontWeight: 800,
                  flexShrink: 0
                }}>
                  #{act.priority_level}
                </div>

                {/* Content */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: badge.text, background: badge.bg, padding: '2px 7px', borderRadius: 4 }}>
                        {badge.label}
                      </span>
                      <span style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                        {act.headline}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#3fb950' }}>
                      +{act.expected_impact_delta}% Impact
                    </span>
                  </div>

                  <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', margin: 0, lineHeight: 1.5 }}>
                    {act.rationale}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 4, flexWrap: 'wrap', gap: 8 }}>
                    <span><Clock size={11} style={{ verticalAlign: -1, marginRight: 4 }} /> Timeline: <strong>{act.implementation_timeframe}</strong></span>
                    <span><BookOpen size={11} style={{ verticalAlign: -1, marginRight: 4 }} /> Source: <em>{act.clinical_guideline_source}</em></span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* 3 Column Priority Breakdown: Lifestyle, Food, Diagnostic Labs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
        {/* Lifestyle Priorities */}
        <div className="card" style={{ padding: 20, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.6)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <Sun size={18} color="#e3b341" />
            <span style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
              Lifestyle Priorities
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {actionPlanData.lifestyle_priorities.map((item, idx) => (
              <div key={idx} style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.45, display: 'flex', gap: 8 }}>
                <span style={{ color: '#e3b341', fontWeight: 800 }}>•</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Food Priorities */}
        <div className="card" style={{ padding: 20, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.6)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <Utensils size={18} color="#3fb950" />
            <span style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
              Core Food Priorities
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {actionPlanData.food_priorities.map((item, idx) => (
              <div key={idx} style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.45, display: 'flex', gap: 8 }}>
                <span style={{ color: '#3fb950', fontWeight: 800 }}>•</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Diagnostic Laboratory Testing */}
        <div className="card" style={{ padding: 20, background: 'rgba(22, 27, 34, 0.85)', border: '1px solid rgba(48, 54, 61, 0.6)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <FlaskConical size={18} color="#a371f7" />
            <span style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
              Confirmatory Lab Panels
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {actionPlanData.laboratory_testing_priorities.map((item, idx) => (
              <div key={idx} style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.4 }}>
                <div style={{ fontWeight: 700, color: 'var(--c-secondary)' }}>{item.test_name}</div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 2 }}>{item.clinical_indication}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
