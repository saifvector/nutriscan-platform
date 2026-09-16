import { useState, useMemo, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import {
  Utensils, Leaf, Dumbbell, Moon, Sun, Droplets, Heart,
  FileText, ChevronRight, Zap, PlusCircle, RotateCcw
} from 'lucide-react'
import { sessionManager } from '../lib/sessionManager'
import { ResumeAssessmentModal } from '../components/session/ResumeAssessmentModal'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.05 } } }

function getFoodEmoji(name: string, group?: string): string {
  const n = (name + ' ' + (group || '')).toLowerCase()
  if (n.includes('mushroom')) return '🍄'
  if (n.includes('lentil') || n.includes('bean') || n.includes('chickpea')) return '🫘'
  if (n.includes('yeast')) return '🧀'
  if (n.includes('spinach') || n.includes('kale') || n.includes('green') || n.includes('chard')) return '🥬'
  if (n.includes('tofu') || n.includes('soy') || n.includes('tempeh')) return '🧊'
  if (n.includes('pumpkin') || n.includes('seed')) return '🎃'
  if (n.includes('nut') || n.includes('almond') || n.includes('walnut')) return '🌰'
  if (n.includes('pepper')) return '🫑'
  if (n.includes('potato')) return '🍠'
  if (n.includes('yogurt') || n.includes('milk')) return '🥛'
  if (n.includes('egg')) return '🥚'
  if (n.includes('citrus') || n.includes('orange') || n.includes('lemon')) return '🍋'
  if (n.includes('avocado')) return '🥑'
  if (n.includes('berry') || n.includes('blueberr')) return '🫐'
  return '🥗'
}

function useRecommendationData(assessmentId: string | null) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!assessmentId) {
      setData(null)
      return
    }

    const fetchRecs = async () => {
      setLoading(true)
      try {
        const res = await fetch(`/api/v1/recommendations/${assessmentId}`)
        if (res.ok) {
          const apiData = await res.json()
          
          let p1: any[] = []
          let p2: any[] = []
          let p3: any[] = []

          if (Array.isArray(apiData.food_recommendations) && apiData.food_recommendations.length > 0) {
            apiData.food_recommendations.forEach((f: any) => {
              const mapped = {
                name: f.food_name,
                nutrient: f.target_nutrient,
                serving: f.serving_size,
                density: `${f.nutrient_density} ${f.unit || ''}`.trim(),
                tip: f.preparation_tips || f.rationale || 'Targeted functional nutrient source.',
                emoji: getFoodEmoji(f.food_name, f.food_group),
              }
              if (f.priority_tier === 'PRIORITY_1') p1.push(mapped)
              else if (f.priority_tier === 'PRIORITY_2') p2.push(mapped)
              else p3.push(mapped)
            })
            if (p1.length === 0 && p2.length === 0) {
              const allMapped = apiData.food_recommendations.map((f: any) => ({
                name: f.food_name,
                nutrient: f.target_nutrient,
                serving: f.serving_size,
                density: `${f.nutrient_density} ${f.unit || ''}`.trim(),
                tip: f.preparation_tips || f.rationale || 'Targeted functional nutrient source.',
                emoji: getFoodEmoji(f.food_name, f.food_group),
              }))
              p1 = allMapped.slice(0, 3)
              p2 = allMapped.slice(3, 7)
              p3 = allMapped.slice(7)
            }
          }

          const synergies = Array.isArray(apiData.synergistic_pairings) && apiData.synergistic_pairings.length > 0
            ? apiData.synergistic_pairings.map((s: any) => ({
                pair: [s.primary_nutrient, s.synergistic_nutrient],
                mechanism: s.biochemical_mechanism,
                foods: s.meal_concept || `${s.primary_food} + ${s.enhancer_food}`,
                icon: '⚡'
              }))
            : []

          const recovery = Array.isArray(apiData.recovery_milestones) && apiData.recovery_milestones.length > 0
            ? apiData.recovery_milestones.map((m: any, idx: number) => ({
                phase: idx + 1,
                label: m.day_range,
                title: m.phase_title,
                milestones: m.daily_action_checklist && m.daily_action_checklist.length > 0
                  ? m.daily_action_checklist
                  : [m.clinical_focus, m.primary_dietary_strategy].filter(Boolean)
              }))
            : []

          const lifestyle = Array.isArray(apiData.lifestyle_modifications) && apiData.lifestyle_modifications.length > 0
            ? apiData.lifestyle_modifications.map((l: any) => ({
                category: l.category || 'General Lifestyle',
                icon: Sun,
                actions: Array.isArray(l.action_items) ? l.action_items : [l.recommendation || 'Maintain regular lifestyle habits']
              }))
            : []

          setData({
            foods: {
              priority1: p1,
              priority2: p2,
              priority3: p3,
            },
            synergies,
            lifestyle,
            recovery,
          })
        }
      } catch (err) {
        console.error('Recommendations fetch error:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchRecs()
  }, [assessmentId])

  return { data, loading }
}

function FoodCard({ food }: { food: any }) {
  return (
    <div className="card card-hover" style={{ padding: 20, cursor: 'default' }}>
      <div style={{ display: 'flex', gap: 14 }}>
        <span style={{ fontSize: 28 }}>{food.emoji}</span>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 2 }}>{food.name}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--c-primary)', fontWeight: 600 }}>for {food.nutrient}</div>
            </div>
            <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-accent)', background: 'var(--c-warning-bg)', padding: '2px 8px', borderRadius: 4 }}>{food.density}</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 8 }}><strong>Serving:</strong> {food.serving}</div>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.5, marginTop: 6 }}>{food.tip}</p>
        </div>
      </div>
    </div>
  )
}

export default function RecommendationsPage() {
  const { assessmentId } = useParams()
  const navigate = useNavigate()
  const [activeSession, setActiveSession] = useState(() => sessionManager.getActiveSession())
  const [showResumeModal, setShowResumeModal] = useState(false)
  const storedPrevious = useMemo(() => sessionManager.getStoredPreviousAssessment(), [])

  const effectiveId = activeSession?.active_assessment_id || (assessmentId && assessmentId !== 'demo' ? assessmentId : null)
  const { data, loading } = useRecommendationData(effectiveId)
  const [activeTab, setActiveTab] = useState<'foods' | 'lifestyle' | 'recovery'>('foods')

  const tabs = [
    { key: 'foods' as const, label: 'Food Recommendations', icon: Utensils },
    { key: 'lifestyle' as const, label: 'Lifestyle Interventions', icon: Leaf },
    { key: 'recovery' as const, label: 'Recovery Roadmap', icon: Zap },
  ]

  if (!effectiveId || (!loading && !data)) {
    return (
      <div style={{ maxWidth: 840, margin: '60px auto', padding: '0 24px' }}>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            background: 'var(--c-card)',
            border: '1px solid var(--c-border)',
            borderRadius: 20,
            padding: '56px 40px',
            textAlign: 'center',
            boxShadow: '0 12px 36px rgba(0, 0, 0, 0.04)'
          }}
        >
          <div style={{
            width: 72,
            height: 72,
            borderRadius: '50%',
            background: 'rgba(37, 99, 235, 0.08)',
            color: 'var(--c-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px'
          }}>
            <Utensils size={36} />
          </div>

          <h2 style={{
            fontSize: '1.65rem',
            fontWeight: 800,
            color: 'var(--c-text)',
            marginBottom: 12,
            letterSpacing: '-0.02em'
          }}>
            Generate recommendations after assessment.
          </h2>

          <p style={{
            fontSize: '1rem',
            color: 'var(--c-secondary)',
            lineHeight: 1.6,
            maxWidth: 580,
            margin: '0 auto 36px'
          }}>
            Personalized food recommendations, synergistic nutrient pairings, and therapeutic recovery roadmaps require an active clinical assessment to match your metabolic needs. Complete an assessment to generate clinical dietary interventions.
          </p>

          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate('/assessment')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                background: 'var(--c-primary)',
                color: '#fff',
                padding: '12px 24px',
                borderRadius: 10,
                fontWeight: 600,
                fontSize: '0.92rem',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 4px 14px rgba(37, 99, 235, 0.25)',
                transition: 'all 0.15s ease'
              }}
            >
              <PlusCircle size={16} />
              Start Assessment
            </button>

            {storedPrevious && (
              <button
                onClick={() => setShowResumeModal(true)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'var(--c-card)',
                  color: 'var(--c-text)',
                  border: '1px solid var(--c-border)',
                  padding: '12px 24px',
                  borderRadius: 10,
                  fontWeight: 600,
                  fontSize: '0.92rem',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                <RotateCcw size={16} />
                Resume Previous Assessment
              </button>
            )}
          </div>
        </motion.div>

        {storedPrevious && (
          <ResumeAssessmentModal
            isOpen={showResumeModal}
            assessmentId={storedPrevious.id}
            assessmentDate={storedPrevious.date}
            onResume={() => {
              sessionManager.setActiveSession(storedPrevious.id, storedPrevious.date, 'completed')
              setActiveSession(sessionManager.getActiveSession())
              setShowResumeModal(false)
            }}
            onStartNew={() => {
              sessionManager.clearActiveSession()
              setActiveSession(null)
              setShowResumeModal(false)
              navigate('/assessment')
            }}
          />
        )}
      </div>
    )
  }

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger}>
      <motion.div variants={fadeUp} style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 6 }}>Personalized Recommendations</h1>
            <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)' }}>Evidence-based dietary guidance, lifestyle interventions, and structured recovery plans.</p>
          </div>
          <Link
            to={`/intelligence/${assessmentId || 'demo'}`}
            className="card card-hover"
            style={{
              padding: '10px 16px',
              background: 'linear-gradient(135deg, rgba(56, 139, 253, 0.15) 0%, rgba(22, 27, 34, 0.8) 100%)',
              border: '1px solid rgba(56, 139, 253, 0.4)',
              color: 'var(--c-secondary)',
              textDecoration: 'none',
              fontSize: '0.8125rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              borderRadius: 8
            }}
          >
            <Zap size={15} color="var(--c-primary)" />
            <span>Launch Nutrition Intelligence Center &rarr;</span>
          </Link>
        </div>
      </motion.div>

      <motion.div variants={fadeUp} style={{ display: 'flex', gap: 4, marginBottom: 24, background: 'var(--c-bg-secondary)', padding: 4, borderRadius: 10, border: '1px solid var(--c-border)', width: 'fit-content' }}>
        {tabs.map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)} style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 8, border: 'none',
            background: activeTab === tab.key ? 'var(--c-primary)' : 'transparent',
            color: activeTab === tab.key ? 'white' : 'var(--c-muted)',
            fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'var(--font-body)', transition: 'all 0.15s',
          }}>
            <tab.icon size={14} /> {tab.label}
          </button>
        ))}
      </motion.div>

      {activeTab === 'foods' && (
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          {[
            { label: 'Priority 1 — Critical', desc: 'Address immediately for highest-risk nutrients', foods: data.foods.priority1, color: 'var(--c-danger)' },
            { label: 'Priority 2 — Important', desc: 'Add to weekly meal rotation', foods: data.foods.priority2, color: 'var(--c-warning)' },
            { label: 'Priority 3 — Maintenance', desc: 'Include regularly for overall balance', foods: data.foods.priority3, color: 'var(--c-success)' },
          ].map((section: any) => (
            <motion.div key={section.label} variants={fadeUp} style={{ marginBottom: 28 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <div style={{ width: 4, height: 20, borderRadius: 2, background: section.color }} />
                <div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{section.label}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>{section.desc}</div>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
                {section.foods.map((f: any) => <FoodCard key={f.name} food={f} />)}
              </div>
            </motion.div>
          ))}
          <motion.div variants={fadeUp} style={{ marginBottom: 28 }}>
            <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 14 }}>Nutrient Synergy Pairings</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              {data.synergies.map((s: any) => (
                <div key={s.pair.join('-')} className="card" style={{ padding: 20 }}>
                  <div style={{ fontSize: 20, marginBottom: 10 }}>{s.icon}</div>
                  <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-primary)', marginBottom: 6 }}>{s.pair.join(' + ')}</div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.5, marginBottom: 8 }}>{s.mechanism}</p>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-text-secondary)', fontWeight: 500 }}><strong>Try:</strong> {s.foods}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}

      {activeTab === 'lifestyle' && (
        <motion.div initial="hidden" animate="visible" variants={stagger} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {data.lifestyle.map((cat: any) => (
            <motion.div key={cat.category} variants={fadeUp} className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--c-surface-tint)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <cat.icon size={18} color="var(--c-primary)" />
                </div>
                <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{cat.category}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {cat.actions.map((action: any, i: number) => (
                  <div key={i} style={{ display: 'flex', gap: 10 }}>
                    <div style={{ width: 5, height: 5, borderRadius: 3, background: 'var(--c-primary)', marginTop: 6, flexShrink: 0 }} />
                    <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>{action}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {activeTab === 'recovery' && (
        <motion.div initial="hidden" animate="visible" variants={stagger} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {data.recovery.map((phase: any, i: number) => (
            <motion.div key={phase.phase} variants={fadeUp} className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 20 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 14, flexShrink: 0,
                  background: i === 0 ? 'var(--c-primary)' : i === 1 ? 'var(--c-accent)' : 'var(--c-border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.125rem', fontWeight: 800, color: 'white', fontFamily: 'var(--font-heading)',
                }}>{phase.phase}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>{phase.label}</div>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 12, letterSpacing: '-0.01em' }}>{phase.title}</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {phase.milestones.map((m: any, j: number) => (
                      <div key={j} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <div style={{ width: 18, height: 18, borderRadius: 4, flexShrink: 0, marginTop: 1, border: '2px solid var(--c-border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }} />
                        <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>{m}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      <motion.div variants={fadeUp} style={{ marginTop: 24 }}>
        <Link to={`/reports/${assessmentId}`} className="btn-primary" style={{ padding: '10px 24px', fontSize: '0.8125rem' }}>
          <FileText size={14} /> Generate Report <ChevronRight size={14} />
        </Link>
      </motion.div>
    </motion.div>
  )
}
