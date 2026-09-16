import { useMemo, useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { Brain, ChevronRight } from 'lucide-react'
import { NUTRIENT_ICONS } from '../lib/constants'
import { useTheme } from '../lib/theme'

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

const FALLBACK_PREDICTIONS = [
  { name: 'Vitamin D', code: 'VITAMIN_D', probability: 0.87, risk: 'HIGH', confidence: 0.92, rank: 1 },
  { name: 'Iron', code: 'IRON', probability: 0.74, risk: 'HIGH', confidence: 0.88, rank: 2 },
  { name: 'Vitamin B12', code: 'VITAMIN_B12', probability: 0.62, risk: 'MODERATE', confidence: 0.85, rank: 3 },
  { name: 'Folate', code: 'FOLATE', probability: 0.55, risk: 'MODERATE', confidence: 0.81, rank: 4 },
  { name: 'Potassium', code: 'POTASSIUM', probability: 0.52, risk: 'MODERATE', confidence: 0.84, rank: 5 },
  { name: 'Calcium', code: 'CALCIUM', probability: 0.48, risk: 'MODERATE', confidence: 0.79, rank: 6 },
  { name: 'Iodine', code: 'IODINE', probability: 0.45, risk: 'MODERATE', confidence: 0.82, rank: 7 },
  { name: 'Zinc', code: 'ZINC', probability: 0.42, risk: 'MODERATE', confidence: 0.83, rank: 8 },
  { name: 'Vitamin B6', code: 'VITAMIN_B6', probability: 0.39, risk: 'LOW', confidence: 0.86, rank: 9 },
  { name: 'Magnesium', code: 'MAGNESIUM', probability: 0.38, risk: 'LOW', confidence: 0.86, rank: 10 },
  { name: 'Vitamin B1', code: 'VITAMIN_B1', probability: 0.35, risk: 'LOW', confidence: 0.88, rank: 11 },
  { name: 'Selenium', code: 'SELENIUM', probability: 0.33, risk: 'LOW', confidence: 0.85, rank: 12 },
  { name: 'Vitamin C', code: 'VITAMIN_C', probability: 0.31, risk: 'LOW', confidence: 0.90, rank: 13 },
  { name: 'Vitamin B2', code: 'VITAMIN_B2', probability: 0.28, risk: 'LOW', confidence: 0.87, rank: 14 },
  { name: 'Vitamin A', code: 'VITAMIN_A', probability: 0.25, risk: 'LOW', confidence: 0.87, rank: 15 },
  { name: 'Vitamin B3', code: 'VITAMIN_B3', probability: 0.22, risk: 'LOW', confidence: 0.89, rank: 16 },
  { name: 'Protein', code: 'PROTEIN', probability: 0.18, risk: 'LOW', confidence: 0.91, rank: 17 },
  { name: 'Vitamin E', code: 'VITAMIN_E', probability: 0.14, risk: 'LOW', confidence: 0.89, rank: 18 },
]

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

function usePredictionData() {
  const [predictions, setPredictions] = useState<any[]>(() => {
    try {
      const stored = sessionStorage.getItem('prediction_result')
      if (stored) {
        const parsed = JSON.parse(stored)
        if (!parsed.mock) {
          const normalized = normalizePredictions(parsed)
          if (normalized.length > 0) return normalized
        }
      }
    } catch { /* fallback */ }
    return []
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchPredictions = async () => {
      // 1. Check if valid predictions exist in sessionStorage
      try {
        const stored = sessionStorage.getItem('prediction_result')
        if (stored) {
          const parsed = JSON.parse(stored)
          if (!parsed.mock) {
            const normalized = normalizePredictions(parsed)
            if (normalized.length > 0) {
              setPredictions(normalized)
              return
            }
          }
        }
      } catch { /* ignore */ }

      // 2. Check if active patient assessment payload exists in localStorage
      let assessmentPayload: any = null
      try {
        const localAsmnt = localStorage.getItem('nutriscan_active_assessment')
        if (localAsmnt) {
          assessmentPayload = JSON.parse(localAsmnt)
        }
      } catch { /* ignore */ }

      if (assessmentPayload) {
        try {
          setLoading(true)
          const res = await fetch('/api/v1/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(assessmentPayload)
          })
          if (res.ok) {
            const data = await res.json()
            sessionStorage.setItem('prediction_result', JSON.stringify(data))
            const normalized = normalizePredictions(data)
            if (normalized.length > 0) {
              setPredictions(normalized)
              return
            }
          }
        } catch (err) {
          console.error('Predictions fetch error with active assessment:', err)
        } finally {
          setLoading(false)
        }
      }

      // 3. Fallback to latest persisted assessment report
      try {
        const res = await fetch('/api/v1/reports/history')
        if (res.ok) {
          const history = await res.json()
          if (Array.isArray(history) && history.length > 0) {
            const latest = history[0]
            if (latest.report_payload?.nutrient_predictions) {
              const normalized = normalizePredictions(latest.report_payload)
              if (normalized.length > 0) {
                setPredictions(normalized)
                return
              }
            }
          }
        }
      } catch (err) {
        console.error('Historical prediction fetch note:', err)
      }
    }
    fetchPredictions()
  }, [])

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
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Priority #{nutrient.rank}</div>
          </div>
        </div>
        <span className={`risk-badge risk-badge-${nutrient.risk.toLowerCase()}`}>{nutrient.risk}</span>
      </div>
      <div style={{ marginBottom: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Deficiency Probability</span>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{Math.round(nutrient.probability * 100)}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${Math.round(nutrient.probability * 100)}%`, background: nutrient.risk === 'HIGH' ? 'var(--c-danger)' : nutrient.risk === 'MODERATE' ? 'var(--c-warning)' : 'var(--c-success)' }} />
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
  const { assessmentId } = useParams()
  const { predictions: nutrients, loading } = usePredictionData()
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

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <p style={{ color: 'var(--c-muted)', fontSize: '0.875rem' }}>Analyzing clinical screening parameters and computing multi-nutrient probabilities...</p>
      </div>
    )
  }

  if (nutrients.length === 0) {
    return (
      <div style={{ maxWidth: 640, margin: '60px auto', textAlign: 'center' }} className="card">
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 8 }}>No Active Assessment Data</h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 24 }}>
          Please complete the clinical screening questionnaire to generate personalized multi-nutrient predictions.
        </p>
        <Link to="/assessment" className="btn-primary" style={{ display: 'inline-flex', padding: '10px 24px' }}>
          Start New Assessment <ChevronRight size={14} />
        </Link>
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
        <Link to={`/explainability/${assessmentId}`} className="btn-primary" style={{ padding: '10px 24px', fontSize: '0.8125rem' }}>
          <Brain size={14} /> View Explainability <ChevronRight size={14} />
        </Link>
      </motion.div>
    </motion.div>
  )
}
