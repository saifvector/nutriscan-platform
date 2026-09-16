import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import {
  ArrowRight, Sparkles, TrendingUp, TrendingDown, AlertTriangle,
  Shield, Zap, Utensils, Brain, FileText, ChevronRight,
  Activity, Heart, Clock, Sun, Droplets, Moon
} from 'lucide-react'
import { useTheme } from '../lib/theme'

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

/* ─── Data ─── */
function useDashboardData(assessmentId?: string) {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    const load = async () => {
      try {
        // 1. Check for session storage prediction result from Assessment
        let sessionPrediction: any = null
        try {
          const raw = sessionStorage.getItem('prediction_result')
          if (raw) sessionPrediction = JSON.parse(raw)
        } catch { /* ignore parse error */ }

        // 2. Fetch baseline health score and progress analytics
        const [hsRes, progRes] = await Promise.allSettled([
          fetch('/api/v1/analytics/health-score'),
          fetch('/api/v1/progress/summary'),
        ])
        const healthScore = hsRes.status === 'fulfilled' && hsRes.value.ok ? await hsRes.value.json() : null
        const progress = progRes.status === 'fulfilled' && progRes.value.ok ? await progRes.value.json() : null

        // 3. Process nutrients from session prediction or progress tracking
        let rawNutrients: any[] = []
        if (sessionPrediction?.nutrient_predictions?.length) {
          rawNutrients = sessionPrediction.nutrient_predictions.map((p: any, idx: number) => ({
            name: p.nutrient,
            probability: p.probability ?? 0,
            risk: p.risk_level || (p.probability >= 0.7 ? 'HIGH' : p.probability >= 0.4 ? 'MODERATE' : 'LOW'),
            rank: p.priority_rank || idx + 1,
            risk_factors: p.risk_factors || [],
          }))
        } else if (sessionPrediction?.predictions?.length) {
          rawNutrients = sessionPrediction.predictions.map((p: any, idx: number) => {
            const cleanName = p.target_name.replace(/ Deficiency/i, '').replace(/ Insufficiency/i, '')
            const prob = p.calibrated_probability ?? p.probability ?? 0
            const risk = p.risk_tier || (prob >= 0.7 ? 'HIGH' : prob >= 0.4 ? 'MODERATE' : 'LOW')
            return {
              name: cleanName,
              probability: prob,
              risk,
              rank: idx + 1,
              risk_factors: (p.top_predictors || []).map((tp: any) => ({
                feature_name: tp.feature_name,
                impact_score: Math.abs(tp.shap_value ?? tp.impact ?? 0.1) * 100,
                direction: (tp.shap_value ?? 0) >= 0 ? 'RISK' : 'PROTECTIVE',
                category: 'Clinical Biomarker',
              })),
            }
          })
        } else if (progress?.nutrient_recovery_tracking?.length) {
          rawNutrients = progress.nutrient_recovery_tracking.map((n: any, idx: number) => {
            const prob = (n.current_risk_score || 0) / 100.0
            return {
              name: n.nutrient,
              probability: prob,
              risk: prob >= 0.7 ? 'HIGH' : prob >= 0.4 ? 'MODERATE' : 'LOW',
              rank: idx + 1,
              risk_factors: [],
            }
          })
        }

        const nutrients = rawNutrients.map((n: any) => {
          const meta = NUTRIENT_META[n.name] || { icon: '💊', bodyArea: 'body', bodyLabel: n.name }
          return { ...n, ...meta }
        }).sort((a: any, b: any) => b.probability - a.probability)

        // Compute overall health score and risk category
        let calculatedScore = 74
        let calculatedRisk = 'MODERATE'

        if (sessionPrediction?.overall_risk_score != null) {
          calculatedScore = Math.max(15, Math.min(98, Math.round(100 - sessionPrediction.overall_risk_score)))
          calculatedRisk = sessionPrediction.overall_risk || (calculatedScore >= 75 ? 'LOW' : calculatedScore >= 50 ? 'MODERATE' : 'HIGH')
        } else if (healthScore?.current_score != null || healthScore?.health_score != null) {
          calculatedScore = healthScore.current_score ?? healthScore.health_score
          calculatedRisk = healthScore.category || 'MODERATE'
        } else if (nutrients.length > 0) {
          const avgRiskProb = nutrients.slice(0, 5).reduce((sum, n) => sum + n.probability, 0) / Math.min(5, nutrients.length)
          calculatedScore = Math.max(20, Math.min(95, Math.round(100 - avgRiskProb * 80)))
          calculatedRisk = calculatedScore >= 75 ? 'LOW' : calculatedScore >= 50 ? 'MODERATE' : 'HIGH'
        }

        // Derive top risk factors from predictions or nutrients
        let topRiskFactors: any[] = []
        nutrients.forEach(n => {
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

        if (topRiskFactors.length === 0) {
          topRiskFactors = nutrients
            .filter((n: any) => n.probability > 0.35)
            .slice(0, 5)
            .map((n: any) => ({
              name: n.name,
              impact: Math.round(n.probability * 60),
              type: n.probability > 0.5 ? 'risk' : 'protective',
              category: 'Nutritional Biomarker',
            }))
        }

        // Tailor priority foods dynamically to top deficiencies and patient dietary pattern
        let isVegetarian = false
        let isVegan = false
        try {
          const rawActive = localStorage.getItem('nutriscan_active_assessment')
          if (rawActive) {
            const parsed = JSON.parse(rawActive)
            const pat = (parsed.dietary_pattern || parsed.dietaryPattern || '').toLowerCase()
            if (pat.includes('vegan')) {
              isVegan = true
              isVegetarian = true
            } else if (pat.includes('veg')) {
              isVegetarian = true
            }
          }
        } catch { /* ignore */ }

        const topNutrientNames = nutrients.slice(0, 3).map(n => n.name)
        const priorityFoods: any[] = []

        if (isVegetarian) {
          if (topNutrientNames.includes('Vitamin D') || topNutrientNames.some(n => n.includes('D'))) {
            priorityFoods.push({ name: 'UV-Exposed Maitake Mushrooms', target: 'Vitamin D2', density: 'High', emoji: '🍄', tip: 'Sunlight-activated ergocalciferol matrix' })
            if (!isVegan) {
              priorityFoods.push({ name: 'Pasture-Raised Organic Egg Yolks', target: 'Vitamin D3 + B12', density: 'High', emoji: '🥚', tip: 'Free-range provides 4-6x more bioactive D3' })
            } else {
              priorityFoods.push({ name: 'Fortified Organic Soy Milk', target: 'Vitamin D3 & Calcium', density: 'High', emoji: '🥛', tip: 'Delivers 25% DV Vitamin D with plant lipid carriers' })
            }
          }
          if (topNutrientNames.includes('Iron') || topNutrientNames.some(n => n.includes('Anemia') || n.includes('Iron'))) {
            priorityFoods.push({ name: 'Pre-Soaked Brown Lentils & Quinoa', target: 'Non-Heme Iron', density: 'High', emoji: '🌱', tip: 'Soaking deactivates phytate binding complexes' })
            priorityFoods.push({ name: 'Baby Spinach + Lemon Juice', target: 'Iron + Vitamin C', density: 'Synergy', emoji: '🥬', tip: 'Ascorbic acid multiplies non-heme absorption by 6x' })
          }
          if (topNutrientNames.includes('Folate')) {
            priorityFoods.push({ name: 'Steamed Asparagus & Edamame', target: 'Folate (B9)', density: 'Very High', emoji: '🌱', tip: 'Cooked legumes provide high bioavailable folate' })
          }
          if (topNutrientNames.includes('Magnesium')) {
            priorityFoods.push({ name: 'Raw Sprouted Pumpkin Seeds', target: 'Magnesium & Zinc', density: 'Very High', emoji: '🎃', tip: '150mg Mg per ounce, supports sleep & nerves' })
          }
          if (topNutrientNames.includes('Calcium')) {
            priorityFoods.push({ name: 'Calcium-Set Nigari Tofu', target: 'Calcium + Magnesium', density: 'Exceptional', emoji: '🥢', tip: 'Delivers 350-430mg bioavailable elemental calcium' })
            priorityFoods.push({ name: 'Crushed White Sesame & Tahini', target: 'Calcium & Zinc', density: 'High', emoji: '🫓', tip: 'Dense mineral source without animal saturated fat' })
          }
          if (topNutrientNames.includes('Vitamin B12') || topNutrientNames.some(n => n.includes('B12'))) {
            priorityFoods.push({ name: 'Fortified Nutritional Yeast Flakes', target: 'Vitamin B12', density: 'Exceptional', emoji: '✨', tip: '2 tbsp delivers 300%+ daily methylcobalamin' })
          }
          if (priorityFoods.length < 4) {
            const vegDefaults = [
              { name: 'Calcium-Set Tofu', target: 'Calcium + Iron', density: 'High', emoji: '🥢', tip: 'Pan-sear with garlic & ginger' },
              { name: 'Spinach + Lemon', target: 'Iron + Vit C', density: 'Synergy', emoji: '🥬', tip: 'Ascorbic acid unlocks plant iron' },
              { name: 'Sprouted Pumpkin Seeds', target: 'Magnesium + Zinc', density: 'Very High', emoji: '🎃', tip: 'High cellular magnesium density' },
              { name: 'Fortified Nutritional Yeast', target: 'Vitamin B12', density: 'Exceptional', emoji: '✨', tip: 'Complete bioactive B-complex' },
            ]
            vegDefaults.forEach(d => {
              if (priorityFoods.length < 4 && !priorityFoods.some(p => p.name === d.name)) {
                priorityFoods.push(d)
              }
            })
          }
        } else {
          // Standard Omnivore recommendations
          if (topNutrientNames.includes('Vitamin D') || topNutrientNames.some(n => n.includes('D'))) {
            priorityFoods.push({ name: 'Wild Sockeye Salmon', target: 'Vitamin D', density: 'Very High', emoji: '🐟', tip: '988 IU per 3.5oz serving' })
            priorityFoods.push({ name: 'Pasture-Raised Egg Yolks', target: 'Vitamin D + B12', density: 'High', emoji: '🥚', tip: 'Free-range provides 4-6x more D3' })
          }
          if (topNutrientNames.includes('Iron') || topNutrientNames.some(n => n.includes('Anemia') || n.includes('Iron'))) {
            priorityFoods.push({ name: 'Beef Liver / Organ Meats', target: 'Heme Iron + B12', density: 'Exceptional', emoji: '🥩', tip: 'Highest bioavailability iron source' })
            priorityFoods.push({ name: 'Baby Spinach + Lemon Juice', target: 'Iron + Vitamin C', density: 'Synergy', emoji: '🥬', tip: 'Ascorbic acid multiplies non-heme absorption by 6x' })
          }
          if (topNutrientNames.includes('Folate')) {
            priorityFoods.push({ name: 'Steamed Asparagus & Lentils', target: 'Folate (B9)', density: 'Very High', emoji: '🌱', tip: 'Cooked lentils provide 90% daily value per cup' })
          }
          if (topNutrientNames.includes('Magnesium')) {
            priorityFoods.push({ name: 'Raw Pumpkin Seeds', target: 'Magnesium', density: 'Very High', emoji: '🎃', tip: '150mg Mg per ounce, supports sleep & nerves' })
          }
          if (topNutrientNames.includes('Calcium')) {
            priorityFoods.push({ name: 'Wild Sardines with Bones', target: 'Calcium + D', density: 'High', emoji: '🥫', tip: '325mg bioavailable calcium per tin' })
          }
          if (priorityFoods.length < 4) {
            const defaults = [
              { name: 'Wild Salmon', target: 'Vitamin D', density: 'Very High', emoji: '🐟', tip: 'Bake at 400°F for 12 min' },
              { name: 'Beef Liver', target: 'Iron + B12', density: 'Exceptional', emoji: '🥩', tip: 'Pan-fry with onions' },
              { name: 'Spinach + Lemon', target: 'Iron + Vit C', density: 'Synergy', emoji: '🥬', tip: '6x iron absorption boost' },
              { name: 'Egg Yolks', target: 'Vitamin D + B12', density: 'High', emoji: '🥚', tip: 'Free-range = 3-6x more Vit D' },
            ]
            defaults.forEach(d => {
              if (priorityFoods.length < 4 && !priorityFoods.some(p => p.name === d.name)) {
                priorityFoods.push(d)
              }
            })
          }
        }

        const highestDef = nutrients[0]?.name || 'Vitamin D'

        setData({
          healthScore: calculatedScore,
          overallRisk: calculatedRisk,
          scoreChange: progress?.health_score_delta ?? (sessionPrediction ? +4 : 0),
          assessmentDate: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
          nutrients,
          aiInsight: {
            headline: nutrients.length > 0 && nutrients[0].probability > 0.5
              ? `Primary deficiency alert: ${nutrients[0].name} (${Math.round(nutrients[0].probability * 100)}% risk)`
              : progress?.fastest_recovery_trend
              ? `Recovery progress detected: ${progress.fastest_recovery_trend}`
              : 'Your nutritional profile is actively monitored.',
            body: sessionPrediction?.screening_metadata?.summary || healthScore?.breakdown?.interpretation || `Clinical AI detected significant risk indicators in ${highestDef}. Personalized dietary and replenishment protocols have been synthesized.`,
            actionable: sessionPrediction?.priority_ranking?.length
              ? `Prioritize targeted repletion of ${sessionPrediction.priority_ranking.slice(0, 3).join(', ')} with paired bioavailable co-factors.`
              : progress?.lifestyle_improvements?.join('. ') || 'Follow the personalized nutrition protocol recommended by the clinical AI.',
          },
          topRiskFactors: topRiskFactors.slice(0, 5),
          priorityFoods: priorityFoods.slice(0, 4),
          timeline: [
            { time: 'Today', event: 'Health assessment completed', type: 'assessment', detail: `${nutrients.length || 11} biomarkers screened` },
            { time: 'Today', event: 'AI analysis generated', type: 'insight', detail: `Identified ${highestDef} prioritization` },
            { time: 'Recommended', event: 'Begin targeted supplementation', type: 'action', detail: `Focus on ${highestDef}` },
            { time: 'Week 1', event: 'Start recovery diet protocol', type: 'action', detail: 'Incorporate priority nutrient pairs' },
            { time: 'Week 4', event: 'Follow-up assessment', type: 'milestone', detail: 'Re-evaluate biomarker trajectories' },
          ],
          recovery: [
            { phase: 1, label: 'Now', title: 'Acute Replenishment', status: 'active', tasks: [`Target ${highestDef} replenishment`, 'Add priority synergy foods daily', 'Eliminate absorption inhibitors'] },
            { phase: 2, label: 'Week 2', title: 'Consolidation', status: 'upcoming', tasks: ['Full dietary rotation active', 'Lifestyle factor optimization', 'Symptom checkpoint check'] },
            { phase: 3, label: 'Week 4+', title: 'Systemic Resilience', status: 'upcoming', tasks: ['Biomarker re-test validation', 'Maintenance protocol', 'Long-term nutritional stability'] },
          ],
        })
      } catch (err) {
        console.error('Dashboard data load error:', err)
      }
    }
    load()
  }, [assessmentId])

  return data || {
    healthScore: 0, overallRisk: 'LOADING', scoreChange: 0,
    assessmentDate: '—', nutrients: [], aiInsight: { headline: 'Loading...', body: '', actionable: '' },
    topRiskFactors: [], priorityFoods: [], timeline: [], recovery: [],
  }
}

/* ═══════════════════════════════════════════
   §1 — HERO HEALTH SCORE
   ═══════════════════════════════════════════ */
function HeroScore({ score, risk, change, date }: { score: number; risk: string; change: number; date: string }) {
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
      {/* Subtle gradient accent */}
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
          {/* Inner glow */}
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
          Based on 11 nutrient predictions, dietary analysis, lifestyle factors, and biochemical interaction modeling.
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px',
            borderRadius: 8, background: 'var(--c-success-bg)',
          }}>
            <TrendingUp size={14} color="var(--c-success)" />
            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-success-text)' }}>+{change} pts</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>Assessed {date}</span>
        </div>
      </div>

      {/* Right Metrics */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, flexShrink: 0 }}>
        {[
          { label: 'High Risk', value: '2', color: 'var(--c-danger)' },
          { label: 'Moderate', value: '4', color: 'var(--c-warning)' },
          { label: 'Low Risk', value: '5', color: 'var(--c-success)' },
        ].map(m => (
          <div key={m.label} style={{
            display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px',
            borderRadius: 12, border: '1px solid var(--c-border-light)',
            background: 'var(--c-bg)',
          }}>
            <div style={{ width: 8, height: 8, borderRadius: 4, background: m.color, flexShrink: 0 }} />
            <span style={{ fontSize: '1.25rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: m.color, width: 20 }}>{m.value}</span>
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
            ⚡ Recommended Action
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
   §3 — NUTRIENT RISK HEATMAP
   ═══════════════════════════════════════════ */
function NutrientHeatmap({ nutrients }: { nutrients: any[] }) {
  const [hovered, setHovered] = useState<string | null>(null)
  const { resolved } = useTheme()

  return (
    <motion.div custom={2} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
        Deficiency Risk Map
      </div>
      <div style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', marginBottom: 20 }}>
        11 nutrients · Darker = higher risk
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
        {nutrients.map(n => {
          const intensity = n.probability
          const riskColor = n.risk === 'HIGH'
            ? (resolved === 'dark' ? `rgba(239,68,68,${0.3 + intensity * 0.5})` : `rgba(220,38,38,${0.15 + intensity * 0.4})`)
            : n.risk === 'MODERATE'
            ? (resolved === 'dark' ? `rgba(245,158,11,${0.2 + intensity * 0.4})` : `rgba(245,158,11,${0.1 + intensity * 0.3})`)
            : (resolved === 'dark' ? `rgba(34,197,94,${0.1 + intensity * 0.3})` : `rgba(22,163,74,${0.08 + intensity * 0.2})`)

          const isHovered = hovered === n.name

          return (
            <div
              key={n.name}
              onMouseEnter={() => setHovered(n.name)}
              onMouseLeave={() => setHovered(null)}
              style={{
                padding: '14px 12px', borderRadius: 12, cursor: 'default',
                background: riskColor,
                border: `1px solid ${isHovered ? 'var(--c-primary)' : 'transparent'}`,
                transform: isHovered ? 'scale(1.04)' : 'scale(1)',
                transition: 'all 0.2s ease',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: 20, marginBottom: 6 }}>{n.icon}</div>
              <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-secondary)', marginBottom: 2 }}>
                {n.name}
              </div>
              <div style={{
                fontSize: '1rem', fontWeight: 800, fontFamily: 'var(--font-heading)',
                color: n.risk === 'HIGH' ? 'var(--c-danger)' : n.risk === 'MODERATE' ? 'var(--c-warning)' : 'var(--c-success)',
              }}>
                {Math.round(n.probability * 100)}%
              </div>
              {isHovered && (
                <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', marginTop: 4 }}>
                  {n.bodyLabel}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 20, marginTop: 16 }}>
        {['HIGH', 'MODERATE', 'LOW'].map(level => (
          <div key={level} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{
              width: 10, height: 10, borderRadius: 3,
              background: level === 'HIGH' ? 'var(--c-danger)' : level === 'MODERATE' ? 'var(--c-warning)' : 'var(--c-success)',
            }} />
            <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 500 }}>{level}</span>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §4 — BODY VISUALIZATION
   ═══════════════════════════════════════════ */
function BodyVisualization({ nutrients }: { nutrients: any[] }) {
  const highRisk = nutrients.filter(n => n.risk === 'HIGH')
  const modRisk = nutrients.filter(n => n.risk === 'MODERATE').slice(0, 3)

  const bodyAreas = [
    { area: 'Brain & Cognition', y: 0, nutrients: nutrients.filter(n => n.bodyArea === 'brain'), icon: '🧠' },
    { area: 'Vision', y: 1, nutrients: nutrients.filter(n => n.bodyArea === 'eyes'), icon: '👁️' },
    { area: 'Skin & Healing', y: 2, nutrients: nutrients.filter(n => n.bodyArea === 'skin'), icon: '✨' },
    { area: 'Thyroid & Endocrine', y: 3, nutrients: nutrients.filter(n => n.bodyArea === 'thyroid'), icon: '🦋' },
    { area: 'Cardiovascular', y: 4, nutrients: nutrients.filter(n => n.bodyArea === 'heart'), icon: '❤️' },
    { area: 'Immune System', y: 5, nutrients: nutrients.filter(n => n.bodyArea === 'immune'), icon: '🛡️' },
    { area: 'Blood & Energy', y: 6, nutrients: nutrients.filter(n => n.bodyArea === 'blood'), icon: '🩸' },
    { area: 'Bones & Joints', y: 7, nutrients: nutrients.filter(n => n.bodyArea === 'bones'), icon: '🦴' },
    { area: 'Muscles', y: 8, nutrients: nutrients.filter(n => n.bodyArea === 'muscle'), icon: '💪' },
    { area: 'Nervous System', y: 9, nutrients: nutrients.filter(n => n.bodyArea === 'nerves'), icon: '💤' },
  ]

  return (
    <motion.div custom={3} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
        Body Impact Mapping
      </div>
      <div style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', marginBottom: 20 }}>
        Where your deficiencies manifest
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {bodyAreas.filter(b => b.nutrients.length > 0).map(area => {
          const maxRisk = area.nutrients.reduce((max: number, n: any) => Math.max(max, n.probability), 0)
          const hasHighRisk = area.nutrients.some((n: any) => n.risk === 'HIGH')

          return (
            <div key={area.area} style={{
              display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
              borderRadius: 10, background: 'var(--c-bg)', border: '1px solid var(--c-border-light)',
            }}>
              <span style={{ fontSize: 18 }}>{area.icon}</span>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>{area.area}</span>
                  {hasHighRisk && <AlertTriangle size={12} color="var(--c-danger)" />}
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 2 }}>
                  {area.nutrients.map((n: any) => n.name).join(', ')}
                </div>
              </div>
              <div style={{
                height: 6, width: 60, background: 'var(--c-bar-track)', borderRadius: 3,
              }}>
                <div style={{
                  width: `${maxRisk * 100}%`, height: '100%', borderRadius: 3,
                  background: hasHighRisk ? 'var(--c-danger)' : 'var(--c-warning)',
                  transition: 'width 0.6s ease',
                }} />
              </div>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §5 — RISK FACTOR WATERFALL
   ═══════════════════════════════════════════ */
function RiskFactorWaterfall({ factors }: { factors: any[] }) {
  const maxImpact = Math.max(...factors.map(f => f.impact))

  return (
    <motion.div custom={4} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
        <Brain size={14} color="var(--c-primary)" />
        <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          What's Driving Your Risk
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {factors.map(f => (
          <div key={f.name} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ width: 100, flexShrink: 0 }}>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>{f.name}</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)' }}>{f.category}</div>
            </div>

            {/* Bar */}
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ flex: 1, height: 8, background: 'var(--c-bar-track)', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{
                  width: `${(f.impact / maxImpact) * 100}%`, height: '100%', borderRadius: 4,
                  background: f.type === 'risk' ? 'var(--c-danger)' : 'var(--c-success)',
                  transition: 'width 0.6s ease',
                }} />
              </div>
              <span style={{
                fontSize: '0.75rem', fontWeight: 700, width: 48, textAlign: 'right',
                color: f.type === 'risk' ? 'var(--c-danger-text)' : 'var(--c-success-text)',
              }}>
                {f.type === 'risk' ? '+' : '−'}{f.impact}%
              </span>
            </div>

            {/* Icon */}
            {f.type === 'risk'
              ? <TrendingUp size={14} color="var(--c-danger)" />
              : <TrendingDown size={14} color="var(--c-success)" />
            }
          </div>
        ))}
      </div>

      <Link to="/explainability/demo" style={{
        display: 'flex', alignItems: 'center', gap: 6, marginTop: 16,
        fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-primary)', textDecoration: 'none',
      }}>
        View Full SHAP Analysis <ArrowRight size={12} />
      </Link>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §6 — PRIORITY FOODS
   ═══════════════════════════════════════════ */
function PriorityFoods({ foods }: { foods: any[] }) {
  return (
    <motion.div custom={5} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
            Priority Nutrition
          </div>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
            Your Top 4 Recovery Foods
          </div>
        </div>
        <Link to="/recommendations/demo" style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-primary)', textDecoration: 'none' }}>
          See all <ChevronRight size={12} />
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {foods.map(f => (
          <div key={f.name} style={{
            display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px',
            borderRadius: 14, background: 'var(--c-bg)', border: '1px solid var(--c-border-light)',
            transition: 'border-color 0.15s, transform 0.15s',
            cursor: 'default',
          }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--c-primary)'; e.currentTarget.style.transform = 'translateY(-2px)' }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--c-border-light)'; e.currentTarget.style.transform = 'translateY(0)' }}
          >
            <span style={{ fontSize: 28 }}>{f.emoji}</span>
            <div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 2 }}>{f.name}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--c-primary)', fontWeight: 600 }}>for {f.target}</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--c-muted)', marginTop: 4 }}>{f.tip}</div>
            </div>
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
  return (
    <motion.div custom={6} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
        <Zap size={14} color="var(--c-accent)" />
        <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-accent)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Recovery Roadmap
        </span>
      </div>

      <div style={{ display: 'flex', gap: 16 }}>
        {phases.map((p, i) => (
          <div key={p.phase} style={{ flex: 1, position: 'relative' }}>
            {/* Connector */}
            {i < phases.length - 1 && (
              <div style={{
                position: 'absolute', top: 16, left: 'calc(50% + 20px)', right: -16,
                height: 2, background: p.status === 'active' ? 'var(--c-primary)' : 'var(--c-border)',
                zIndex: 0,
              }} />
            )}

            <div style={{
              padding: '16px', borderRadius: 14,
              background: p.status === 'active' ? 'var(--c-surface-tint)' : 'var(--c-bg)',
              border: `1px solid ${p.status === 'active' ? 'var(--c-primary)' : 'var(--c-border-light)'}`,
              position: 'relative', zIndex: 1,
            }}>
              {/* Phase number */}
              <div style={{
                width: 32, height: 32, borderRadius: 10,
                background: p.status === 'active' ? 'var(--c-primary)' : 'var(--c-border)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.875rem', fontWeight: 800, color: 'white',
                fontFamily: 'var(--font-heading)', marginBottom: 12,
              }}>{p.phase}</div>

              <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', marginBottom: 4 }}>{p.label}</div>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 12, letterSpacing: '-0.01em' }}>{p.title}</div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {p.tasks.map((t: string, j: number) => (
                  <div key={j} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                    <div style={{
                      width: 14, height: 14, borderRadius: 4, marginTop: 2, flexShrink: 0,
                      border: `2px solid ${p.status === 'active' ? 'var(--c-primary)' : 'var(--c-border)'}`,
                    }} />
                    <span style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.4 }}>{t}</span>
                  </div>
                ))}
              </div>
            </div>
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
  const typeConfig: Record<string, { icon: any; color: string }> = {
    assessment: { icon: Activity, color: 'var(--c-primary)' },
    insight: { icon: Sparkles, color: 'var(--c-accent)' },
    action: { icon: Zap, color: 'var(--c-warning)' },
    milestone: { icon: Heart, color: 'var(--c-success)' },
  }

  return (
    <motion.div custom={7} variants={fadeUp} initial="hidden" animate="visible"
      style={{
        padding: 28, borderRadius: 20,
        background: 'var(--c-card)', border: '1px solid var(--c-border)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
        <Clock size={14} color="var(--c-primary)" />
        <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Health Timeline
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {events.map((e, i) => {
          const config = typeConfig[e.type] || typeConfig.assessment
          const Icon = config.icon
          return (
            <div key={i} style={{ display: 'flex', gap: 16 }}>
              {/* Vertical line + dot */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 24 }}>
                <div style={{
                  width: 24, height: 24, borderRadius: 8, flexShrink: 0,
                  background: 'var(--c-bg)', border: `2px solid ${config.color}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Icon size={10} color={config.color} />
                </div>
                {i < events.length - 1 && (
                  <div style={{ width: 1, flex: 1, minHeight: 20, background: 'var(--c-border)' }} />
                )}
              </div>

              {/* Content */}
              <div style={{ paddingBottom: 20, flex: 1 }}>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 500, marginBottom: 2 }}>{e.time}</div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)', marginBottom: 2 }}>{e.event}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)' }}>{e.detail}</div>
              </div>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}

/* ═══════════════════════════════════════════
   §9 — QUICK ACTIONS
   ═══════════════════════════════════════════ */
function QuickActions({ assessmentId }: { assessmentId?: string }) {
  const currentId = assessmentId || 'demo'
  const actions = [
    { label: 'View Predictions', desc: '11-nutrient analysis', icon: Activity, to: `/predictions/${currentId}`, color: 'var(--c-primary)' },
    { label: 'SHAP Analysis', desc: 'Explainable AI', icon: Brain, to: `/explainability/${currentId}`, color: 'var(--c-accent)' },
    { label: 'Food Guide', desc: 'Personalized diet', icon: Utensils, to: `/recommendations/${currentId}`, color: 'var(--c-success)' },
    { label: 'Download Report', desc: 'Clinical PDF', icon: FileText, to: `/reports/${currentId}`, color: 'var(--c-muted)' },
  ]

  return (
    <motion.div custom={8} variants={fadeUp} initial="hidden" animate="visible"
      style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}
    >
      {actions.map(a => (
        <Link key={a.label} to={a.to} style={{
          padding: '20px 18px', borderRadius: 16, textDecoration: 'none',
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
          display: 'flex', flexDirection: 'column', gap: 12,
          transition: 'border-color 0.15s, transform 0.15s',
        }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = a.color; e.currentTarget.style.transform = 'translateY(-2px)' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--c-border)'; e.currentTarget.style.transform = 'translateY(0)' }}
        >
          <div style={{
            width: 36, height: 36, borderRadius: 10, background: 'var(--c-bg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <a.icon size={18} color={a.color} />
          </div>
          <div>
            <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 2 }}>{a.label}</div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{a.desc}</div>
          </div>
        </Link>
      ))}
    </motion.div>
  )
}

/* ═══════════════════════════════════════════════════
   DASHBOARD PAGE — BENTO GRID ASSEMBLY
   ═══════════════════════════════════════════════════ */
export default function DashboardPage() {
  const { assessmentId } = useParams<{ assessmentId?: string }>()
  const data = useDashboardData(assessmentId)

  return (
    <div>
      {/* §1 — Hero Health Score */}
      <HeroScore
        score={data.healthScore}
        risk={data.overallRisk}
        change={data.scoreChange}
        date={data.assessmentDate}
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
          {/* Lifestyle Snapshot */}
          <motion.div custom={7} variants={fadeUp} initial="hidden" animate="visible"
            style={{
              padding: 24, borderRadius: 20, flex: 1,
              background: 'var(--c-card)', border: '1px solid var(--c-border)',
            }}
          >
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16 }}>
              Lifestyle Priorities
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { icon: Sun, label: 'Sunlight Exposure', current: '< 15 min/day', target: '30 min/day', urgency: 'high' },
                { icon: Droplets, label: 'Hydration', current: '2.0L/day', target: '2.5L/day', urgency: 'low' },
                { icon: Moon, label: 'Sleep Duration', current: '7 hrs', target: '7-8 hrs', urgency: 'low' },
              ].map(l => (
                <div key={l.label} style={{
                  display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
                  borderRadius: 10, background: 'var(--c-bg)', border: '1px solid var(--c-border-light)',
                }}>
                  <l.icon size={16} color={l.urgency === 'high' ? 'var(--c-warning)' : 'var(--c-success)'} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>{l.label}</div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{l.current} → {l.target}</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* §9 — Quick Actions */}
      <QuickActions assessmentId={assessmentId} />
    </div>
  )
}
