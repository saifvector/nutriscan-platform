import { useState, useEffect, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import {
  ArrowRight, Sparkles, TrendingUp, TrendingDown, AlertTriangle,
  Shield, Zap, Utensils, Brain, FileText, ChevronRight,
  Activity, Heart, Clock, Sun, Droplets, Moon, PlusCircle, RotateCcw, X
} from 'lucide-react'
import { useTheme } from '../lib/theme'
import { sessionManager, type ClinicalSession } from '../lib/sessionManager'
import { ResumeAssessmentModal } from '../components/session/ResumeAssessmentModal'
import { AssessmentRequiredState } from '../components/common/AssessmentRequiredState'
import { PediatricSafetyBanner } from '../components/safety/PediatricSafetyBanner'

/* ─── Animations ─── */
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.5, delay: i * 0.06, ease: 'easeOut' },
  }),
}

/* ─── Nutrient Metadata (icons & body area mappings) ─── */
const NUTRIENT_META: Record<string, { icon: string; bodyArea: string; bodyLabel: string }> = {
  'Vitamin D': { icon: '☀️', bodyArea: 'bones', bodyLabel: 'Bone & Muscle Pain' },
  'Iron': { icon: '🩸', bodyArea: 'blood', bodyLabel: 'Fatigue & Pale Skin' },
  'Vitamin B12': { icon: '🧠', bodyArea: 'brain', bodyLabel: 'Cognitive Fog' },
  'Folate': { icon: '🧬', bodyArea: 'cells', bodyLabel: 'Cell Regeneration' },
  'Potassium': { icon: '🥔', bodyArea: 'heart', bodyLabel: 'Electrolyte Balance' },
  'Calcium': { icon: '🦴', bodyArea: 'bones', bodyLabel: 'Bone Density' },
  'Iodine': { icon: '🧂', bodyArea: 'thyroid', bodyLabel: 'Thyroid Function' },
  'Zinc': { icon: '🛡️', bodyArea: 'immune', bodyLabel: 'Immune Defense' },
  'Vitamin B6': { icon: '🍌', bodyArea: 'brain', bodyLabel: 'Neurotransmitter Synthesis' },
  'Magnesium': { icon: '💤', bodyArea: 'nerves', bodyLabel: 'Sleep & Recovery' },
  'Vitamin B1': { icon: '🌾', bodyArea: 'brain', bodyLabel: 'Nerve Energy Metabolism' },
  'Selenium': { icon: '🌰', bodyArea: 'immune', bodyLabel: 'Antioxidant & Thyroid' },
  'Vitamin C': { icon: '🍊', bodyArea: 'skin', bodyLabel: 'Skin & Healing' },
  'Vitamin B2': { icon: '🥛', bodyArea: 'skin', bodyLabel: 'Cellular Repair' },
  'Vitamin A': { icon: '👁️', bodyArea: 'eyes', bodyLabel: 'Vision Health' },
  'Vitamin B3': { icon: '🍄', bodyArea: 'skin', bodyLabel: 'Cellular Vitality' },
  'Protein': { icon: '💪', bodyArea: 'muscle', bodyLabel: 'Muscle Mass' },
  'Vitamin E': { icon: '✨', bodyArea: 'skin', bodyLabel: 'Antioxidant Shield' },
}

/* ─── Data Hook: Exclusively loads for real active assessment session ─── */
function useDashboardData(activeAssessmentId: string | null) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    if (!activeAssessmentId) {
      setData(null)
      return
    }

    let isMounted = true
    const load = async () => {
      setLoading(true)
      try {
        // Fetch explicit dashboard data for the active assessment
        const [dashRes, predRes] = await Promise.allSettled([
          fetch(`/api/v1/dashboard/${activeAssessmentId}`),
          fetch(`/api/v1/predictions/${activeAssessmentId}`),
        ])

        let assessmentDashboard = dashRes.status === 'fulfilled' && dashRes.value.ok ? await dashRes.value.json() : null
        let predictionPayload = predRes.status === 'fulfilled' && predRes.value.ok ? await predRes.value.json() : null

        // Check if backend returned empty indicator
        if (assessmentDashboard?.hasAssessment === false || (!assessmentDashboard && !predictionPayload)) {
          if (isMounted) setData(null)
          return
        }

        const preds = assessmentDashboard?.predictions || 
                      assessmentDashboard?.deficiency_priority_ranking ||
                      predictionPayload?.predictions || 
                      predictionPayload?.nutrient_predictions || 
                      []

        if (!preds.length && !assessmentDashboard) {
          if (isMounted) setData(null)
          return
        }

        const rawNutrients = preds.map((p: any, idx: number) => {
          const rawName = p.target_name || p.nutrient || 'Nutrient'
          const cleanName = rawName.replace(/ Deficiency/i, '').replace(/ Insufficiency/i, '')
          const prob = p.calibrated_probability ?? p.probability ?? 0
          const risk = p.risk_tier || p.risk_level || 'LOW'
          return {
            name: cleanName,
            probability: prob,
            risk,
            rank: p.priority_rank || idx + 1,
            risk_factors: (p.top_predictors || p.risk_factors || []).map((tp: any) => ({
              feature_name: tp.feature_name || tp.feature || 'Biomarker',
              impact_score: Math.abs(tp.shap_value ?? tp.impact ?? 0.1) * 100,
              direction: (tp.shap_value ?? 0) >= 0 ? 'RISK' : 'PROTECTIVE',
              category: 'Clinical Biomarker',
            })),
          }
        })

        const nutrients = rawNutrients.map((n: any) => {
          const meta = NUTRIENT_META[n.name] || { icon: '💊', bodyArea: 'body', bodyLabel: n.name }
          return { ...n, ...meta }
        }).sort((a: any, b: any) => b.probability - a.probability)

        // Derive health score directly from assessment or real predictions
        let calculatedScore = assessmentDashboard?.overall_health_score ?? assessmentDashboard?.health_score?.score ?? assessmentDashboard?.health_score
        if (calculatedScore == null && nutrients.length > 0) {
          const avgRiskProb = nutrients.slice(0, 5).reduce((sum: number, n: any) => sum + n.probability, 0) / Math.min(5, nutrients.length)
          calculatedScore = Math.max(20, Math.min(95, Math.round(100 - avgRiskProb * 80)))
        }

        const calculatedRisk = assessmentDashboard?.overall_risk_classification ?? (calculatedScore >= 75 ? 'LOW' : calculatedScore >= 50 ? 'MODERATE' : 'HIGH')

        // Real Risk Counts directly from authoritative snapshot or verified predictions
        const riskCounts = {
          high: assessmentDashboard?.nutrient_risk_distribution?.HIGH ?? nutrients.filter((n: any) => n.risk === 'HIGH').length,
          moderate: assessmentDashboard?.nutrient_risk_distribution?.MODERATE ?? nutrients.filter((n: any) => n.risk === 'MODERATE').length,
          low: assessmentDashboard?.nutrient_risk_distribution?.LOW ?? nutrients.filter((n: any) => n.risk === 'LOW').length,
        }

        // Real Top Risk Factors
        let topRiskFactors: any[] = []
        nutrients.forEach((n: any) => {
          if (n.risk_factors?.length) {
            n.risk_factors.forEach((rf: any) => {
              topRiskFactors.push({
                name: `${n.name}: ${rf.feature_name.replace(/_/g, ' ')}`,
                impact: rf.impact_score || 15,
                type: (rf.direction || '').toLowerCase().includes('risk') ? 'risk' : 'protective',
                category: rf.category || 'Clinical Factor',
              })
            })
          }
        })

        // Real Priority Foods mapped from actual elevated deficiencies
        const topDeficiencies = nutrients.filter((n: any) => n.risk === 'HIGH' || n.risk === 'MODERATE').slice(0, 3).map((n: any) => n.name)
        const priorityFoods: any[] = []
        topDeficiencies.forEach((defName: string) => {
          if (defName.includes('Vitamin D')) {
            priorityFoods.push({ name: 'UV-Exposed Portobello Mushrooms', target: 'Vitamin D2', density: 'High', emoji: '🍄', tip: 'Sunlight-activated ergocalciferol matrix' })
          } else if (defName.includes('Iron')) {
            priorityFoods.push({ name: 'Cooked Green Lentils & Spinach', target: 'Iron + Vitamin C', density: 'Synergy', emoji: '🌱', tip: 'Ascorbic acid multiplies non-heme absorption by 6x' })
          } else if (defName.includes('Folate')) {
            priorityFoods.push({ name: 'Steamed Asparagus & Edamame', target: 'Folate (B9)', density: 'Very High', emoji: '🥦', tip: 'Bioavailable folate with active co-factors' })
          } else if (defName.includes('Calcium')) {
            priorityFoods.push({ name: 'Calcium-Set Nigari Tofu', target: 'Calcium + Magnesium', density: 'Exceptional', emoji: '🥢', tip: 'Provides elemental calcium with balanced mineral absorption' })
          } else if (defName.includes('Magnesium')) {
            priorityFoods.push({ name: 'Raw Sprouted Pumpkin Seeds', target: 'Magnesium & Zinc', density: 'Very High', emoji: '🎃', tip: 'Dense intracellular magnesium source' })
          }
        })

        const highestDef = nutrients[0]?.name || 'Target Micronutrient'
        const assessmentDateStr = assessmentDashboard?.generated_at || assessmentDashboard?.created_at || new Date().toISOString()
        let formattedDate = 'Recent'
        try {
          formattedDate = new Date(assessmentDateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
        } catch {
          formattedDate = 'Recent'
        }

        if (isMounted) {
          setData({
            healthScore: calculatedScore ?? 70,
            overallRisk: calculatedRisk,
            scoreChange: assessmentDashboard?.health_score_delta ?? 0,
            assessmentDate: formattedDate,
            nutrients,
            riskCounts,
            aiInsight: {
              headline: nutrients.length > 0 && (nutrients[0].risk === 'HIGH' || (nutrients[0].risk === 'MODERATE' && nutrients[0].probability >= 0.4))
                ? `Primary deficiency alert: ${nutrients[0].name} (${Math.round(nutrients[0].probability * 100)}% risk)`
                : 'Nutritional profile within optimal bounds.',
              body: assessmentDashboard?.summary || (
                nutrients.length > 0 && nutrients[0].risk !== 'LOW'
                  ? `Clinical AI detected significant risk indicators in ${highestDef}. Personalized dietary and replenishment protocols have been synthesized.`
                  : 'Clinical AI evaluated all nutritional biomarkers. All monitored nutrients are within healthy ranges with no immediate replenishment required.'
              ),
              actionable: assessmentDashboard?.critical_actions?.[0] || (
                nutrients.length > 0 && nutrients[0].risk !== 'LOW'
                  ? `Prioritize targeted repletion of ${highestDef} with bioavailable dietary co-factors.`
                  : 'Maintain current balanced dietary pattern and healthy lifestyle practices.'
              ),
            },
            topRiskFactors: topRiskFactors.slice(0, 5),
            priorityFoods: priorityFoods.slice(0, 4),
            timeline: [
              { time: 'Day 1', event: 'Health assessment completed', type: 'assessment', detail: `${nutrients.length} biomarkers evaluated` },
              { time: 'Day 1', event: 'Clinical AI analysis synthesized', type: 'insight', detail: `Identified ${highestDef} prioritization` },
              { time: 'Week 1', event: 'Begin targeted dietary protocol', type: 'action', detail: 'Implement priority whole food pairings' },
              { time: 'Week 4', event: 'Follow-up assessment checkpoint', type: 'milestone', detail: 'Re-evaluate biomarker risk trajectories' },
            ],
            recovery: [
              { phase: 1, label: 'Phase 1', title: 'Acute Repletion', status: 'active', tasks: [`Target ${highestDef} replenishment`, 'Incorporate priority nutrient pairs', 'Eliminate absorption inhibitors'] },
              { phase: 2, label: 'Phase 2', title: 'Homeostatic Balance', status: 'upcoming', tasks: ['Full dietary rotation active', 'Lifestyle factor optimization', 'Midpoint symptom check'] },
              { phase: 3, label: 'Phase 3', title: 'Long-Term Resilience', status: 'upcoming', tasks: ['Biomarker validation', 'Maintenance protocol', 'Sustained nutritional health'] },
            ],
            patientAge: assessmentDashboard?.demographics?.age ?? predictionPayload?.demographics?.age ?? assessmentDashboard?.age ?? predictionPayload?.age,
            safetyWarnings: [
              ...(assessmentDashboard?.nutrient_interaction_alerts || []),
              ...(predictionPayload?.safety_warnings || []),
              ...(predictionPayload?.safety_violations || [])
            ],
            quarantinedItems: predictionPayload?.quarantined_items || [],
          })
        }
      } catch (err) {
        console.error('Dashboard data load error:', err)
        if (isMounted) setData(null)
      } finally {
        if (isMounted) setLoading(false)
      }
    }

    load()
    return () => { isMounted = false }
  }, [activeAssessmentId])

  return { data, loading }
}


/* ═══════════════════════════════════════════
   §1 — HERO HEALTH SCORE
   ═══════════════════════════════════════════ */
function HeroScore({
  score,
  risk,
  change,
  date,
  riskCounts,
  onReset
}: {
  score: number
  risk: string
  change: number
  date: string
  riskCounts: { high: number; moderate: number; low: number }
  onReset?: () => void
}) {
  const circumference = 2 * Math.PI * 68
  const offset = circumference - (score / 100) * circumference
  const scoreColor = score >= 85 ? 'var(--c-success)' : score >= 70 ? 'var(--c-primary)' : score >= 50 ? 'var(--c-warning)' : 'var(--c-danger)'
  const category = score >= 85 ? 'Excellent' : score >= 70 ? 'Good' : score >= 50 ? 'Moderate Risk' : 'High Risk'

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      style={{
        padding: '48px 56px', borderRadius: 24,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
        display: 'flex', alignItems: 'center', gap: 56,
        marginBottom: 24, position: 'relative', overflow: 'hidden',
      }}
    >
      <div style={{
        position: 'absolute', top: -100, right: -100, width: 300, height: 300,
        background: 'radial-gradient(circle, var(--c-surface-tint) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Score Ring */}
      <div style={{ position: 'relative', width: 160, height: 160, flexShrink: 0 }}>
        <svg width={160} height={160} viewBox="0 0 160 160">
          <circle cx={80} cy={80} r={68} fill="none" stroke="var(--c-border)" strokeWidth={6} />
          <circle
            cx={80} cy={80} r={68} fill="none"
            stroke={scoreColor} strokeWidth={6} strokeLinecap="round"
            strokeDasharray={circumference} strokeDashoffset={offset}
            transform="rotate(-90 80 80)"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
          <circle cx={80} cy={80} r={56} fill="none" stroke={scoreColor} strokeWidth={1} opacity={0.15} />
        </svg>
        <div style={{
          position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{
            fontFamily: 'var(--font-heading)', fontSize: 52, fontWeight: 800,
            color: scoreColor, letterSpacing: '-0.04em', lineHeight: 1,
          }}>{score}</span>
          <span style={{ fontSize: 11, color: 'var(--c-muted)', fontWeight: 500, marginTop: 4 }}>of 100</span>
        </div>
      </div>

      {/* Score Details */}
      <div style={{ flex: 1, position: 'relative', zIndex: 1 }}>
        <div style={{
          fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
          textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8,
        }}>
          Nutritional Health Score
        </div>
        <h1 style={{
          fontFamily: 'var(--font-heading)', fontSize: 'clamp(1.75rem, 3vw, 2.25rem)',
          fontWeight: 800, letterSpacing: '-0.03em', color: 'var(--c-secondary)',
          marginBottom: 12, lineHeight: 1.1,
        }}>
          {category}
        </h1>
        <p style={{ fontSize: '0.9375rem', color: 'var(--c-text-secondary)', lineHeight: 1.6, maxWidth: 440, marginBottom: 20 }}>
          Based on verified nutrient predictions, dietary analysis, lifestyle factors, and biochemical interaction modeling.
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px',
            borderRadius: 8, background: 'var(--c-success-bg)',
          }}>
            <TrendingUp size={14} color="var(--c-success)" />
            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-success-text)' }}>
              {change >= 0 ? `+${change}` : change} pts
            </span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>Assessed {date}</span>
          {onReset && (
            <button
              onClick={onReset}
              id="hero-reset-assessment-btn"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 12px',
                borderRadius: 8,
                fontSize: '0.75rem',
                fontWeight: 600,
                background: 'rgba(239, 68, 68, 0.08)',
                color: '#ef4444',
                border: '1px solid rgba(239, 68, 68, 0.2)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              className="hover:bg-red-500/15 hover:border-red-500/40"
              title="Remove current assessment and start new"
            >
              <RotateCcw size={12} />
              Reset & Start New
            </button>
          )}
        </div>
      </div>

      {/* Real Risk Counts */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, flexShrink: 0 }}>
        {[
          { label: 'High Risk', value: riskCounts.high, color: 'var(--c-danger)' },
          { label: 'Moderate', value: riskCounts.moderate, color: 'var(--c-warning)' },
          { label: 'Low Risk', value: riskCounts.low, color: 'var(--c-success)' },
        ].map(m => (
          <div key={m.label} style={{
            display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px',
            borderRadius: 12, border: '1px solid var(--c-border-light)',
            background: 'var(--c-bg)',
          }}>
            <div style={{ width: 8, height: 8, borderRadius: 4, background: m.color, flexShrink: 0 }} />
            <span style={{ fontSize: '1.25rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: m.color, width: 24 }}>
              {m.value}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)', fontWeight: 500 }}>{m.label}</span>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §2 — AI HEALTH INSIGHT
   ═══════════════════════════════════════════ */
function AIInsight({ insight }: { insight: { headline: string; body: string; actionable: string } }) {
  return (
    <motion.div custom={1} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
        position: 'relative', overflow: 'hidden',
      }}
    >
      <div style={{
        position: 'absolute', top: -60, left: -60, width: 180, height: 180,
        background: 'radial-gradient(circle, var(--c-surface-tint) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 8, background: 'var(--c-surface-tint)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Sparkles size={14} color="var(--c-primary)" />
          </div>
          <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            AI Health Intelligence
          </span>
        </div>
        <h3 style={{
          fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700,
          color: 'var(--c-secondary)', marginBottom: 12, letterSpacing: '-0.02em', lineHeight: 1.3,
        }}>
          {insight.headline}
        </h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.7, marginBottom: 16 }}>
          {insight.body}
        </p>
        <div style={{
          padding: '12px 16px', borderRadius: 12, background: 'var(--c-surface-tint)',
          border: '1px solid var(--c-border)',
        }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-accent)', marginBottom: 4 }}>
            Recommended Action
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-secondary)', lineHeight: 1.6 }}>
            {insight.actionable}
          </p>
        </div>
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §3 — DEFICIENCY RISK MAP
   ═══════════════════════════════════════════ */
function NutrientHeatmap({ nutrients }: { nutrients: any[] }) {
  return (
    <motion.div custom={2} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
            Deficiency Risk Map
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            {nutrients.length} nutrients · Darker = higher risk
          </div>
        </div>
        <Link to="/predictions" style={{ fontSize: '0.75rem', color: 'var(--c-primary)', display: 'flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
          View all <ChevronRight size={14} />
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
        {nutrients.slice(0, 12).map(n => {
          const pct = Math.round(n.probability * 100)
          const isHigh = n.risk === 'HIGH'
          const isMod = n.risk === 'MODERATE'
          const bg = isHigh ? 'rgba(239, 68, 68, 0.12)' : isMod ? 'rgba(245, 158, 11, 0.10)' : 'rgba(34, 197, 94, 0.08)'
          const border = isHigh ? 'rgba(239, 68, 68, 0.3)' : isMod ? 'rgba(245, 158, 11, 0.25)' : 'rgba(34, 197, 94, 0.2)'
          const textColor = isHigh ? 'var(--c-danger)' : isMod ? 'var(--c-warning)' : 'var(--c-success)'

          return (
            <div key={n.name} style={{
              padding: '12px 10px', borderRadius: 12, background: bg, border: `1px solid ${border}`,
              textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
            }}>
              <span style={{ fontSize: 18 }}>{n.icon}</span>
              <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%' }}>
                {n.name}
              </span>
              <span style={{ fontSize: '0.875rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: textColor }}>
                {n.probability < 0.01 && n.probability > 0 ? '<1%' : `${pct}%`}
              </span>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §4 — BODY AREA MAPPING
   ═══════════════════════════════════════════ */
function BodyVisualization({ nutrients }: { nutrients: any[] }) {
  const areas = useMemo(() => {
    const map: Record<string, { label: string; count: number; highCount: number; nutrients: string[] }> = {}
    nutrients.forEach(n => {
      const area = n.bodyArea || 'other'
      if (!map[area]) map[area] = { label: n.bodyLabel || area, count: 0, highCount: 0, nutrients: [] }
      map[area].count++
      if (n.risk === 'HIGH') map[area].highCount++
      map[area].nutrients.push(n.name)
    })
    return Object.entries(map).map(([key, val]) => ({ key, ...val }))
  }, [nutrients])

  return (
    <motion.div custom={3} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
        Body Impact Analysis
      </div>
      <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 20 }}>
        Symptom correlation by physiological system
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {areas.slice(0, 5).map(a => (
          <div key={a.key} style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '10px 14px', borderRadius: 12, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)',
          }}>
            <div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>{a.label}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{a.nutrients.join(', ')}</div>
            </div>
            <div style={{
              padding: '4px 8px', borderRadius: 6,
              background: a.highCount > 0 ? 'rgba(239, 68, 68, 0.12)' : 'var(--c-surface-tint)',
              color: a.highCount > 0 ? 'var(--c-danger)' : 'var(--c-primary)',
              fontSize: '0.6875rem', fontWeight: 700,
            }}>
              {a.highCount > 0 ? `${a.highCount} high risk` : 'Monitored'}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §5 — RISK FACTORS WATERFALL
   ═══════════════════════════════════════════ */
function RiskFactorWaterfall({ factors }: { factors: any[] }) {
  return (
    <motion.div custom={4} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
        Predictive Risk Drivers
      </div>
      <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 20 }}>
        SHAP feature impact on deficiency predictions
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {factors.map((f, i) => (
          <div key={i}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 4 }}>
              <span style={{ fontWeight: 600, color: 'var(--c-secondary)' }}>{f.name}</span>
              <span style={{ color: f.type === 'risk' ? 'var(--c-danger)' : 'var(--c-success)', fontWeight: 700 }}>
                {f.type === 'risk' ? `+${f.impact}%` : `-${f.impact}%`}
              </span>
            </div>
            <div style={{ height: 6, borderRadius: 3, background: 'var(--c-border-light)', overflow: 'hidden' }}>
              <div style={{
                height: '100%', borderRadius: 3,
                width: `${Math.min(100, f.impact * 2)}%`,
                background: f.type === 'risk' ? 'var(--c-danger)' : 'var(--c-success)',
              }} />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §6 — PRIORITY FOODS
   ═══════════════════════════════════════════ */
function PriorityFoods({ foods }: { foods: any[] }) {
  if (!foods || foods.length === 0) return null

  return (
    <motion.div custom={5} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
            Targeted Nutritional Interventions
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            High nutrient-density foods matching detected deficiencies
          </div>
        </div>
        <Link to="/recommendations" style={{ fontSize: '0.75rem', color: 'var(--c-primary)', display: 'flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
          View food protocols <ChevronRight size={14} />
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
        {foods.map(f => (
          <div key={f.name} style={{
            padding: 16, borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)', display: 'flex', flexDirection: 'column', gap: 8,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <span style={{ fontSize: 24 }}>{f.emoji}</span>
              <span style={{
                fontSize: '0.625rem', fontWeight: 700, padding: '2px 8px', borderRadius: 4,
                background: 'var(--c-surface-tint)', color: 'var(--c-primary)',
              }}>
                {f.density}
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{f.name}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--c-primary)', fontWeight: 600 }}>Targets: {f.target}</div>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.4 }}>{f.tip}</div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §7 — RECOVERY ROADMAP
   ═══════════════════════════════════════════ */
function RecoveryRoadmap({ phases }: { phases: any[] }) {
  if (!phases || phases.length === 0) return null

  return (
    <motion.div custom={6} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
        Replenishment Horizon
      </div>
      <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 24 }}>
        Structured stages toward clinical homeostasis
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {phases.map((p, i) => (
          <div key={i} style={{
            padding: 20, borderRadius: 16, background: 'var(--c-bg)',
            border: p.status === 'active' ? '1px solid var(--c-primary)' : '1px solid var(--c-border-light)',
            position: 'relative',
          }}>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 700, color: p.status === 'active' ? 'var(--c-primary)' : 'var(--c-muted)',
              marginBottom: 6, textTransform: 'uppercase',
            }}>
              {p.label}
            </div>
            <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 12 }}>
              {p.title}
            </div>
            <ul style={{ paddingLeft: 16, margin: 0, fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.6 }}>
              {p.tasks.map((t: string, ti: number) => (
                <li key={ti}>{t}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §8 — HEALTH TIMELINE
   ═══════════════════════════════════════════ */
function HealthTimeline({ events }: { events: any[] }) {
  return (
    <motion.div custom={7} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20, flex: 1,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
        Clinical Assessment Trajectory
      </div>
      <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 20 }}>
        Chronological milestones for active assessment
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {events.map((e, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
            <div style={{
              width: 10, height: 10, borderRadius: 5, marginTop: 4, flexShrink: 0,
              background: e.type === 'assessment' ? 'var(--c-primary)' : e.type === 'action' ? 'var(--c-warning)' : 'var(--c-accent)',
            }} />
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>{e.event}</span>
                <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{e.time}</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 2 }}>{e.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §9 — QUICK ACTIONS
   ═══════════════════════════════════════════ */
function QuickActions({ assessmentId }: { assessmentId?: string }) {
  const actions = [
    { label: 'Predictions', path: assessmentId ? `/predictions/${assessmentId}` : '/predictions', icon: Brain, desc: '9 ML targets & SHAP' },
    { label: 'Precision Foods', path: assessmentId ? `/recommendations/${assessmentId}` : '/recommendations', icon: Utensils, desc: 'Targeted diet repletion' },
    { label: 'Biochemical Network', path: assessmentId ? `/network/${assessmentId}` : '/network', icon: Activity, desc: 'Nutrient synergies' },
    { label: 'Clinical Report', path: assessmentId ? `/reports/${assessmentId}` : '/reports', icon: FileText, desc: 'Exportable PDF dossier' },
  ]

  return (
    <motion.div custom={8} variants={fadeUp} initial="hidden" animate="visible"
      style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}
    >
      {actions.map(a => (
        <Link key={a.label} to={a.path} style={{ textDecoration: 'none' }}>
          <div style={{
            padding: 20, borderRadius: 16, background: 'var(--c-card)',
            border: '1px solid var(--c-border)', display: 'flex', alignItems: 'center', gap: 14,
            transition: 'all 0.2s ease', cursor: 'pointer',
          }}
            onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--c-primary)'}
            onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--c-border)'}
          >
            <div style={{
              width: 40, height: 40, borderRadius: 12, background: 'var(--c-surface-tint)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <a.icon size={20} color="var(--c-primary)" />
            </div>
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{a.label}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{a.desc}</div>
            </div>
          </div>
        </Link>
      ))}
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   MAIN DASHBOARD PAGE COMPONENT
   ═══════════════════════════════════════════ */
export default function DashboardPage() {
  const { assessmentId: urlParamId } = useParams<{ assessmentId?: string }>()
  const navigate = useNavigate()

  const [activeSession, setActiveSession] = useState<ClinicalSession | null>(() => sessionManager.getActiveSession())
  const [showResumeModal, setShowResumeModal] = useState<boolean>(false)
  const [showResetConfirm, setShowResetConfirm] = useState<boolean>(false)
  const storedPrevious = useMemo(() => sessionManager.getStoredPreviousAssessment(), [])

  // Sync session if URL explicitly specifies an assessment
  useEffect(() => {
    if (urlParamId && urlParamId !== 'demo') {
      sessionManager.setActiveSession(urlParamId, new Date().toISOString(), 'completed')
      setActiveSession(sessionManager.getActiveSession())
    }
  }, [urlParamId])

  // On initial mount, if NO active session is running, but previous assessment exists in storage, show modal!
  useEffect(() => {
    if (!urlParamId && !activeSession?.active_assessment_id && storedPrevious?.id) {
      setShowResumeModal(true)
    }
  }, [urlParamId, activeSession, storedPrevious])

  const effectiveAssessmentId = activeSession?.active_assessment_id || urlParamId || null
  const { data, loading } = useDashboardData(effectiveAssessmentId)

  const handleConfirmResume = () => {
    if (storedPrevious?.id) {
      sessionManager.setActiveSession(storedPrevious.id, storedPrevious.createdAt, 'completed')
      setActiveSession(sessionManager.getActiveSession())
    }
    setShowResumeModal(false)
  }

  const handleConfirmStartNew = () => {
    sessionManager.clearAllStoredAssessments()
    setActiveSession(null)
    setShowResumeModal(false)
    setShowResetConfirm(false)
    navigate('/assessment')
  }

  const handleOpenResume = () => {
    if (storedPrevious?.id) {
      setShowResumeModal(true)
    } else {
      navigate('/assessment')
    }
  }

  // FIRST VISIT / NO ACTIVE SESSION: Render clean, professional empty state!
  if (!effectiveAssessmentId || !data) {
    return (
      <div>
        <AssessmentRequiredState
          title="Nutritional Assessment Required"
          description="No active assessment is currently loaded. Complete an assessment to generate personalized nutritional predictions, deficiency analysis, food recommendations, meal plans, forecasting insights, and clinical reports."
          actionLabel="Start Assessment"
          onAction={() => navigate('/assessment')}
          secondaryActionLabel={storedPrevious?.id ? 'Resume Previous Assessment' : undefined}
          onSecondaryAction={handleOpenResume}
          icon={Sparkles}
        />

        <ResumeAssessmentModal
          isOpen={showResumeModal}
          assessmentId={storedPrevious?.id || ''}
          date={storedPrevious?.createdAt || ''}
          onResume={handleConfirmResume}
          onStartNew={handleConfirmStartNew}
          onClose={() => setShowResumeModal(false)}
        />
      </div>
    )
  }

  // ACTIVE SESSION POPULATED DASHBOARD
  return (
    <div>
      {/* Resume Modal (in case triggered manually) */}
      <ResumeAssessmentModal
        isOpen={showResumeModal}
        assessmentId={storedPrevious?.id || ''}
        date={storedPrevious?.createdAt || ''}
        onResume={handleConfirmResume}
        onStartNew={handleConfirmStartNew}
        onClose={() => setShowResumeModal(false)}
      />

      {/* Reset Assessment Confirmation Modal */}
      <AnimatePresence>
        {showResetConfirm && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 16,
              background: 'rgba(0, 0, 0, 0.75)',
              backdropFilter: 'blur(6px)',
            }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              style={{
                width: '100%',
                maxWidth: 480,
                borderRadius: 20,
                background: 'var(--c-card)',
                border: '1px solid var(--c-border)',
                padding: '28px 24px',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 42,
                    height: 42,
                    borderRadius: 12,
                    background: 'rgba(239, 68, 68, 0.12)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ef4444',
                    flexShrink: 0,
                  }}>
                    <RotateCcw size={20} />
                  </div>
                  <div>
                    <h3 style={{
                      fontFamily: 'var(--font-heading)',
                      fontSize: '1.25rem',
                      fontWeight: 700,
                      color: 'var(--c-secondary)',
                      margin: 0,
                    }}>
                      Reset Assessment Session?
                    </h3>
                    <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', margin: 0 }}>
                      Remove loaded clinical session & start fresh
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setShowResetConfirm(false)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--c-muted)',
                    cursor: 'pointer',
                    padding: 6,
                    borderRadius: 6,
                  }}
                  className="hover:text-white hover:bg-slate-800"
                  aria-label="Close dialog"
                >
                  <X size={18} />
                </button>
              </div>

              <div style={{
                padding: '14px 16px',
                borderRadius: 12,
                background: 'var(--c-bg)',
                border: '1px solid var(--c-border-light)',
                marginBottom: 20,
              }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--c-text-secondary)', lineHeight: 1.5, margin: 0 }}>
                  This action will remove the current assessment (<span style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--c-primary)' }}>{effectiveAssessmentId ? `${effectiveAssessmentId.slice(0, 16)}...` : 'Active'}</span>) and clear cached prediction results from your browser session. You will be redirected to the assessment intake form to begin a new evaluation.
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12 }}>
                <button
                  type="button"
                  onClick={() => setShowResetConfirm(false)}
                  style={{
                    padding: '9px 18px',
                    borderRadius: 10,
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    background: 'transparent',
                    color: 'var(--c-muted)',
                    border: '1px solid var(--c-border)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  className="hover:bg-slate-800 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  id="confirm-reset-btn"
                  onClick={handleConfirmStartNew}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '9px 18px',
                    borderRadius: 10,
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    background: '#dc2626',
                    color: '#ffffff',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  className="hover:bg-red-700 active:scale-98"
                >
                  <RotateCcw size={15} />
                  Reset & Start New
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Top Session Status & Reset Action Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 12,
        marginBottom: 16,
        padding: '12px 20px',
        borderRadius: 16,
        background: 'var(--c-card)',
        border: '1px solid var(--c-border)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            borderRadius: 6,
            background: 'var(--c-surface-tint)',
            fontSize: '0.6875rem',
            fontWeight: 700,
            color: 'var(--c-primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
          }}>
            <Activity size={12} /> Active Assessment
          </span>
          <span style={{
            fontFamily: 'monospace',
            fontSize: '0.8125rem',
            fontWeight: 600,
            color: 'var(--c-secondary)',
          }}>
            ID: {effectiveAssessmentId}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            ({data.assessmentDate})
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={() => setShowResetConfirm(true)}
            id="top-reset-assessment-btn"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '8px 16px',
              borderRadius: 10,
              fontSize: '0.8125rem',
              fontWeight: 600,
              background: 'rgba(239, 68, 68, 0.09)',
              color: '#ef4444',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            className="hover:bg-red-500/15 hover:border-red-500/40 active:scale-98"
            title="Remove current assessment and start new"
          >
            <RotateCcw size={14} />
            Reset & Start New
          </button>
        </div>
      </div>

      {/* Pediatric Safety & Clinical Contraindication Alert */}
      <PediatricSafetyBanner
        patientAge={data.patientAge}
        safetyWarnings={data.safetyWarnings}
        quarantinedItems={data.quarantinedItems}
      />

      {/* §1 — Hero Health Score */}
      <HeroScore
        score={data.healthScore}
        risk={data.overallRisk}
        change={data.scoreChange}
        date={data.assessmentDate}
        riskCounts={data.riskCounts}
        onReset={() => setShowResetConfirm(true)}
      />

      {/* §2-3 — AI Insight + Nutrient Heatmap (Bento Row) */}
      <div style={{ display: 'grid', gridTemplateColumns: '5fr 7fr', gap: 16, marginBottom: 16 }}>
        <AIInsight insight={data.aiInsight} />
        <NutrientHeatmap nutrients={data.nutrients} />
      </div>

      {/* §4-5 — Body Map + Risk Factors (Bento Row) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <BodyVisualization nutrients={data.nutrients} />
        <RiskFactorWaterfall factors={data.topRiskFactors} />
      </div>

      {/* §6 — Priority Foods (Full Width) */}
      <div style={{ marginBottom: 16 }}>
        <PriorityFoods foods={data.priorityFoods} />
      </div>

      {/* §7 — Recovery Roadmap (Full Width) */}
      <div style={{ marginBottom: 16 }}>
        <RecoveryRoadmap phases={data.recovery} />
      </div>

      {/* §8 — Health Timeline + Actions (Bento Row) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <HealthTimeline events={data.timeline} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <motion.div custom={7} variants={fadeUp} initial="hidden" animate="visible"
            style={{
              padding: 24, borderRadius: 20, flex: 1,
              background: 'var(--c-card)', border: '1px solid var(--c-border)',
            }}
          >
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
              Assessment Lifecycle
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px',
                borderRadius: 10, background: 'var(--c-bg)', border: '1px solid var(--c-border-light)',
              }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>Session ID</span>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-primary)', fontFamily: 'monospace' }}>
                  {effectiveAssessmentId.slice(0, 18)}...
                </span>
              </div>
              <button
                onClick={() => setShowResetConfirm(true)}
                id="lifecycle-reset-assessment-btn"
                className="w-full py-2 px-3 rounded-lg text-xs font-semibold bg-red-950/20 hover:bg-red-900/30 text-red-400 border border-red-800/40 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Reset & Start New Assessment
              </button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* §9 — Quick Actions */}
      <QuickActions assessmentId={effectiveAssessmentId} />
    </div>
  )
}
