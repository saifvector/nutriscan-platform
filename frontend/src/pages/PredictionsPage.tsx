import { useMemo, useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { Brain, ChevronRight, FileText, PlusCircle, RotateCcw } from 'lucide-react'
import { NUTRIENT_ICONS } from '../lib/constants'
import { useTheme } from '../lib/theme'
import { sessionManager } from '../lib/sessionManager'
import { ResumeAssessmentModal } from '../components/session/ResumeAssessmentModal'
import { AssessmentRequiredState } from '../components/common/AssessmentRequiredState'
import { PediatricSafetyBanner } from '../components/safety/PediatricSafetyBanner'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.05 } } }

function useChartColors() {
  const { resolved } = useTheme()
  return useMemo(() => ({
    grid: resolved === 'dark' ? '#293548' : '#E5E7EB',
    tick: resolved === 'dark' ? '#64748B' : '#9CA3AF',
    label: resolved === 'dark' ? '#94A3B8' : '#4B5563',
    primary: resolved === 'dark' ? '#14B8A6' : '#0F766E',
    primaryFill: resolved === 'dark' ? 'rgba(20,184,166,0.15)' : 'rgba(15,118,110,0.15)',
    success: resolved === 'dark' ? '#22C55E' : '#16A34A',
    warning: resolved === 'dark' ? '#F59E0B' : '#F59E0B',
    danger: resolved === 'dark' ? '#EF4444' : '#DC2626',
    tooltipBg: resolved === 'dark' ? '#1E293B' : '#FFFFFF',
    tooltipBorder: resolved === 'dark' ? '#293548' : '#E5E7EB',
  }), [resolved])
}

function normalizePredictions(data: any): any[] {
  if (!data) return []
  if (Array.isArray(data.nutrient_predictions) && data.nutrient_predictions.length > 0) {
    return data.nutrient_predictions.map((p: any, i: number) => ({
      name: p.nutrient,
      code: p.nutrient_code || p.nutrient.toUpperCase().replace(/\s+/g, '_'),
      probability: p.probability ?? 0,
      risk: p.risk_level || 'LOW',
      confidence: p.confidence ?? 0.88,
      rank: p.priority_rank || i + 1,
    }))
  }
  if (Array.isArray(data.predictions) && data.predictions.length > 0) {
    return data.predictions.map((p: any, i: number) => {
      const cleanName = p.target_name.replace(/ Deficiency/i, '').replace(/ Insufficiency/i, '')
      const prob = p.calibrated_probability ?? p.probability ?? 0
      const risk = p.risk_tier || p.risk_level || 'LOW'
      return {
        name: cleanName,
        code: cleanName.toUpperCase().replace(/\s+/g, '_'),
        probability: prob,
        risk: risk,
        confidence: p.confidence_score ?? 0.89,
        rank: i + 1,
      }
    }).sort((a: any, b: any) => b.probability - a.probability)
      .map((item: any, idx: number) => ({ ...item, rank: idx + 1 }))
  }
  return []
}

function usePredictionData(explicitId?: string) {
  const [predictions, setPredictions] = useState<any[]>([])
  const [safety, setSafety] = useState<{ patientAge?: number; safetyWarnings?: any[]; quarantinedItems?: string[] }>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const activeSession = sessionManager.getActiveSession()
    const targetId = explicitId || activeSession?.active_assessment_id

    if (!targetId) {
      setPredictions([])
      setSafety({})
      return
    }

    const fetchPredictions = async () => {
      setLoading(true)
      try {
        const [predRes, dashRes] = await Promise.allSettled([
          fetch(`/api/v1/predictions/${targetId}`),
          fetch(`/api/v1/dashboard/${targetId}`)
        ])

        const data = predRes.status === 'fulfilled' && predRes.value.ok ? await predRes.value.json() : null
        const dashData = dashRes.status === 'fulfilled' && dashRes.value.ok ? await dashRes.value.json() : null

        const normalized = normalizePredictions(data || dashData)
        setPredictions(normalized)

        const age = data?.demographics?.age ?? dashData?.demographics?.age ?? data?.age ?? dashData?.age
        const warnings = [
          ...(data?.safety_warnings || []),
          ...(data?.safety_violations || []),
          ...(dashData?.nutrient_interaction_alerts || [])
        ]
        const quarantined = data?.quarantined_items || []
        setSafety({ patientAge: age, safetyWarnings: warnings, quarantinedItems: quarantined })
      } catch (err) {
        console.error('Predictions fetch error:', err)
        setPredictions([])
        setSafety({})
      } finally {
        setLoading(false)
      }
    }

    fetchPredictions()
  }, [explicitId])

  return { predictions, safety, loading }
}

function NutrientCard({ nutrient }: { nutrient: any }) {
  return (
    <div className="card card-hover" style={{ padding: 20, cursor: 'default' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 18 }}>{NUTRIENT_ICONS[nutrient.name] || '💊'}</span>
          <div>
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{nutrient.name}</div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Rank #{nutrient.rank}</div>
          </div>
        </div>
        <span className={`badge badge-${nutrient.risk.toLowerCase()}`}>
          {nutrient.risk}
        </span>
      </div>

      <div style={{ marginBottom: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 4 }}>
          <span style={{ color: 'var(--c-muted)' }}>Deficiency Probability</span>
          <span style={{ fontWeight: 700, color: 'var(--c-secondary)' }}>
            {nutrient.probability < 0.01 && nutrient.probability > 0 ? '<1%' : `${Math.round(nutrient.probability * 100)}%`}
          </span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-bar-fill"
            style={{
              width: `${Math.max(nutrient.risk === 'LOW' ? 2 : 5, Math.round(nutrient.probability * 100))}%`,
              background: nutrient.risk === 'HIGH' ? 'var(--c-danger)' : nutrient.risk === 'MODERATE' ? 'var(--c-warning)' : 'var(--c-success)',
            }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
        <span>Confidence</span>
        <span style={{ fontWeight: 600 }}>{Math.round(nutrient.confidence * 100)}%</span>
      </div>
    </div>
  )
}

export default function PredictionsPage() {
  const { assessmentId: urlParamId } = useParams()
  const navigate = useNavigate()

  const [activeSession, setActiveSession] = useState(() => sessionManager.getActiveSession())
  const [showResumeModal, setShowResumeModal] = useState(false)
  const storedPrevious = useMemo(() => sessionManager.getStoredPreviousAssessment(), [])

  useEffect(() => {
    if (urlParamId && urlParamId !== 'demo') {
      sessionManager.setActiveSession(urlParamId, new Date().toISOString(), 'completed')
      setActiveSession(sessionManager.getActiveSession())
    }
  }, [urlParamId])

  const effectiveId = activeSession?.active_assessment_id || (urlParamId !== 'demo' ? urlParamId : undefined)
  const { predictions: nutrients, safety, loading } = usePredictionData(effectiveId)
  const cc = useChartColors()

  const radarData = nutrients.map((n: any) => ({
    nutrient: n.name.replace('Vitamin ', 'Vit '),
    probability: Math.round(n.probability * 100),
    fullMark: 100,
  }))

  const barData = [...nutrients].sort((a: any, b: any) => b.probability - a.probability).map((n: any) => ({
    name: n.name, probability: Math.round(n.probability * 100), risk: n.risk,
  }))

  const getRiskFill = (risk: string) => risk === 'HIGH' ? cc.danger : risk === 'MODERATE' ? cc.warning : cc.success

  const handleConfirmResume = () => {
    if (storedPrevious?.id) {
      sessionManager.setActiveSession(storedPrevious.id, storedPrevious.createdAt, 'completed')
      setActiveSession(sessionManager.getActiveSession())
    }
    setShowResumeModal(false)
  }

  const handleConfirmStartNew = () => {
    sessionManager.clearActiveSession()
    setActiveSession(null)
    setShowResumeModal(false)
    navigate('/assessment')
  }

  if (loading) {
    return (
      <div style={{ padding: 60, textAlign: 'center' }}>
        <p style={{ color: 'var(--c-muted)', fontSize: '0.875rem' }}>Analyzing clinical screening parameters and computing multi-nutrient probabilities...</p>
      </div>
    )
  }

  if (!effectiveId || nutrients.length === 0) {
    return (
      <>
        <AssessmentRequiredState
          title="Nutritional Assessment Required"
          description="No active assessment is currently available to evaluate multi-nutrient deficiency probabilities. Complete an assessment to generate your personalized clinical risk predictions."
          actionLabel="Start Assessment"
          secondaryActionLabel={storedPrevious?.id ? 'Resume Previous Assessment' : undefined}
          onSecondaryAction={storedPrevious?.id ? () => setShowResumeModal(true) : undefined}
          icon={Brain}
        />

        <ResumeAssessmentModal
          isOpen={showResumeModal}
          assessmentId={storedPrevious?.id || ''}
          date={storedPrevious?.createdAt || ''}
          onResume={handleConfirmResume}
          onStartNew={handleConfirmStartNew}
          onClose={() => setShowResumeModal(false)}
        />
      </>
    )
  }

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger}>
      <PediatricSafetyBanner
        patientAge={safety?.patientAge}
        safetyWarnings={safety?.safetyWarnings}
        quarantinedItems={safety?.quarantinedItems}
      />

      <motion.div variants={fadeUp} style={{ marginBottom: 32 }}>
        <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 6 }}>Nutrient Predictions</h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)' }}>AI-powered deficiency probability scores across 11 essential nutrients.</p>
      </motion.div>

      <motion.div variants={fadeUp} style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
        {nutrients.map((n: any) => <NutrientCard key={n.code} nutrient={n} />)}
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 32 }}>
        <motion.div variants={fadeUp} className="card" style={{ padding: 24 }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 16 }}>Risk Radar Overview</div>
          <ResponsiveContainer width="100%" height={320}>
            <RadarChart data={radarData}>
              <PolarGrid stroke={cc.grid} />
              <PolarAngleAxis dataKey="nutrient" tick={{ fontSize: 10, fill: cc.label }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9, fill: cc.tick }} />
              <Radar name="Risk" dataKey="probability" stroke={cc.primary} fill={cc.primary} fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div variants={fadeUp} className="card" style={{ padding: 24 }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 16 }}>Priority Risk Ranking</div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={barData} layout="vertical" margin={{ left: 70, right: 20, top: 5, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={cc.grid} horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10, fill: cc.tick }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: cc.label }} width={65} />
              <Tooltip contentStyle={{ borderRadius: 8, border: `1px solid ${cc.tooltipBorder}`, fontSize: 12, boxShadow: 'var(--c-shadow-md)', background: cc.tooltipBg, color: 'var(--c-text)' }} formatter={(value: any) => [`${value}%`, 'Probability']} />
              <Bar dataKey="probability" radius={[0, 4, 4, 0]} barSize={14}>
                {barData.map((entry) => <Cell key={entry.name} fill={getRiskFill(entry.risk)} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      <motion.div variants={fadeUp}>
        <Link to={`/explainability/${effectiveId}`} className="btn-primary" style={{ padding: '10px 24px', fontSize: '0.8125rem' }}>
          <Brain size={14} /> View Explainability <ChevronRight size={14} />
        </Link>
      </motion.div>
    </motion.div>
  )
}
