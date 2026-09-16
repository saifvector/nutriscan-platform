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
      risk: p.risk_level || (p.probability >= 0.7 ? 'HIGH' : p.probability >= 0.4 ? 'MODERATE' : 'LOW'),
      confidence: p.confidence ?? 0.88,
      rank: p.priority_rank || i + 1,
    }))
  }
  if (Array.isArray(data.predictions) && data.predictions.length > 0) {
    return data.predictions.map((p: any, i: number) => {
      const cleanName = p.target_name.replace(/ Deficiency/i, '').replace(/ Insufficiency/i, '')
      const prob = p.calibrated_probability ?? p.probability ?? 0
      const risk = p.risk_tier || (prob >= 0.7 ? 'HIGH' : prob >= 0.4 ? 'MODERATE' : 'LOW')
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
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const activeSession = sessionManager.getActiveSession()
    const targetId = explicitId || activeSession?.active_assessment_id

    if (!targetId) {
      setPredictions([])
      return
    }

    const fetchPredictions = async () => {
      setLoading(true)
      try {
        const res = await fetch(`/api/v1/predictions/${targetId}`)
        if (res.ok) {
          const data = await res.json()
          const normalized = normalizePredictions(data)
          setPredictions(normalized)
          return
        }

        // Try dashboard bundle if direct predictions not present
        const dashRes = await fetch(`/api/v1/dashboard/${targetId}`)
        if (dashRes.ok) {
          const dashData = await dashRes.json()
          const normalized = normalizePredictions(dashData)
          setPredictions(normalized)
          return
        }

        setPredictions([])
      } catch (err) {
        console.error('Predictions fetch error:', err)
        setPredictions([])
      } finally {
        setLoading(false)
      }
    }

    fetchPredictions()
  }, [explicitId])

  return { predictions, loading }
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
          <span style={{ fontWeight: 700, color: 'var(--c-secondary)' }}>{Math.round(nutrient.probability * 100)}%</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-bar-fill"
            style={{
              width: `${Math.round(nutrient.probability * 100)}%`,
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
  const { predictions: nutrients, loading } = usePredictionData(effectiveId)
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
      <div className="flex flex-col items-center justify-center py-20 px-6 text-center max-w-2xl mx-auto rounded-3xl border border-slate-800 bg-slate-900/50 shadow-2xl my-12"
        style={{ background: 'var(--c-card, #0f172a)', borderColor: 'var(--c-border, #1e293b)' }}
      >
        <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center mb-6 shadow-xl shadow-teal-500/5">
          <Brain className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-100 mb-3 font-heading">
          No assessment available.
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mb-8 max-w-lg">
          No active clinical screening assessment is currently loaded to evaluate nutrient deficiency probabilities.
        </p>
        <div className="flex flex-col sm:flex-row items-center gap-3.5 w-full justify-center">
          <button
            onClick={() => navigate('/assessment')}
            className="w-full sm:w-auto px-7 py-3 rounded-xl font-semibold text-sm bg-teal-600 hover:bg-teal-500 text-white transition-all shadow-lg shadow-teal-900/30 flex items-center justify-center gap-2 active:scale-98"
          >
            <PlusCircle className="w-4 h-4" />
            Start Assessment
          </button>
          {storedPrevious?.id && (
            <button
              onClick={() => setShowResumeModal(true)}
              className="w-full sm:w-auto px-7 py-3 rounded-xl font-semibold text-sm bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center justify-center gap-2 active:scale-98"
            >
              <RotateCcw className="w-4 h-4" />
              Resume Previous Assessment
            </button>
          )}
        </div>

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

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger}>
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
