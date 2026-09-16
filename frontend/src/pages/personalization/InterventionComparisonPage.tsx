import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Layers, 
  Sparkles, 
  Check, 
  X, 
  Clock, 
  DollarSign, 
  Activity, 
  ShieldCheck, 
  Award,
  Zap,
  ArrowRight
} from 'lucide-react'

interface InterventionOption {
  id: string
  title: string
  category: string
  badge: string
  badgeColor: string
  uisScore: number
  recoveryDays: number
  weeklyCost: number
  burden: string
  adherence: number
  pros: string[]
  cons: string[]
  bestFor: string
}

export default function InterventionComparisonPage() {
  const [selectedTarget, setSelectedTarget] = useState('Iron & Vitamin D')
  const [apiData, setApiData] = useState<any>(null)

  // Fetch live comparison from backend
  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const res = await fetch('/api/v1/personalization/compare', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            patient_id: 'PT-2026-8891',
            target_nutrients: selectedTarget.split(' & '),
            candidate_options: ['FOOD_ONLY', 'FOOD_PLUS_SUPPLEMENT', 'LIFESTYLE_FIRST'],
          })
        })
        if (res.ok) {
          const data = await res.json()
          setApiData(data)
        }
      } catch (err) {
        console.error('Comparison fetch error:', err)
      }
    }
    fetchComparison()
  }, [selectedTarget])

  // Map API response to UI format, with hardcoded fallback
  const badgeColors: Record<string, string> = {
    'FOOD_ONLY': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'FOOD_PLUS_SUPPLEMENT': 'bg-teal-500/10 text-teal-300 border-teal-500/40 ring-1 ring-teal-500/30',
    'LIFESTYLE_FIRST': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  }

  const options: InterventionOption[] = apiData?.comparison_table?.length
    ? apiData.comparison_table.map((item: any): InterventionOption => ({
        id: item.option_id || item.id,
        title: item.title,
        category: item.category || 'Clinical Strategy',
        badge: item.badge || (item.option_id === apiData.recommended_option ? 'Highest Efficacy (Recommended)' : ''),
        badgeColor: badgeColors[item.option_id] || 'bg-slate-500/10 text-slate-400 border-slate-500/30',
        uisScore: item.unified_score ?? item.uis_score ?? 0,
        recoveryDays: item.estimated_recovery_days ?? item.recovery_days ?? 30,
        weeklyCost: item.weekly_cost_usd ?? item.weekly_cost ?? 0,
        burden: item.burden || 'MODERATE',
        adherence: item.adherence_probability ?? item.adherence ?? 80,
        pros: item.pros || item.advantages || [],
        cons: item.cons || item.disadvantages || [],
        bestFor: item.best_for || item.ideal_for || '',
      }))
    : [
    {
      id: 'FOOD_ONLY',
      title: 'Whole-Food Only Optimization',
      category: 'Dietary Strategy',
      badge: 'Natural & Sustainable',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      uisScore: 86.5,
      recoveryDays: 45,
      weeklyCost: 14.50,
      burden: 'MODERATE',
      adherence: 84,
      pros: ['Zero pharmaceutical gastrointestinal distress', 'Supplies complex dietary fiber and antioxidant cofactors', 'Establishes lifelong culinary and metabolic resilience'],
      cons: ['Slower serum biomarker saturation than clinical supplements', 'Requires regular home cooking and grocery planning'],
      bestFor: 'Mild-to-moderate suboptimal status and preventative long-term wellness.'
    },
    {
      id: 'FOOD_PLUS_SUPPLEMENT',
      title: 'Integrated Food + Micro-Supplement',
      category: 'Hybrid Clinical Protocol',
      badge: 'Highest Efficacy (Recommended)',
      badgeColor: 'bg-teal-500/10 text-teal-300 border-teal-500/40 ring-1 ring-teal-500/30',
      uisScore: 93.8,
      recoveryDays: 21,
      weeklyCost: 18.20,
      burden: 'LOW',
      adherence: 91,
      pros: ['Fastest biomarker normalization (Day 21)', 'Guarantees daily elemental RDA therapeutic threshold', 'Buffered by whole-food digestion maximizing absorption'],
      cons: ['Slightly higher initial financial investment (+$3.70/week)', 'Requires habit anchoring for daily supplement timing'],
      bestFor: 'Moderate-to-severe verified clinical deficiencies needing fast resolution.'
    },
    {
      id: 'LIFESTYLE_FIRST',
      title: 'Lifestyle & Circadian Adaptation',
      category: 'Behavioral Strategy',
      badge: 'Zero Cost',
      badgeColor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
      uisScore: 78.2,
      recoveryDays: 60,
      weeklyCost: 0.00,
      burden: 'VERY LOW',
      adherence: 75,
      pros: ['Zero out-of-pocket financial expense ($0.00)', 'Natural biological autoregulation preventing toxicity', 'Improves circadian sleep architecture and mental focus'],
      cons: ['Heavily dependent on weather, season, and latitude', 'Cannot compensate for deep structural dietary deficits'],
      bestFor: 'Supportive circadian optimization paired with primary nutritional plans.'
    }
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 text-xs font-semibold rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" />
                Intervention Decision Matrix
              </span>
              <span className="px-2.5 py-0.5 text-xs font-mono rounded bg-slate-800 text-slate-300">
                Unified Scoring Engine
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-teal-400 via-emerald-300 to-cyan-400 bg-clip-text text-transparent">
              Intervention Comparison Center
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl">
              Compare competing nutritional intervention archetypes side-by-side across clinical recovery velocity, burden, financial cost, and adherence likelihood.
            </p>
          </div>
        </div>

        {/* Target Deficiency Filter */}
        <div className="flex items-center gap-3 mt-6">
          <span className="text-xs text-slate-400 font-medium">Target Context:</span>
          {['Iron & Vitamin D', 'Folate & Magnesium', 'Calcium & Vitamin D'].map((target) => (
            <button
              key={target}
              onClick={() => setSelectedTarget(target)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                selectedTarget === target
                  ? 'bg-emerald-500 text-slate-950 font-bold shadow-lg shadow-emerald-500/20'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {target}
            </button>
          ))}
        </div>
      </div>

      {/* 3-Column Comparative Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        {options.map((opt, idx) => (
          <motion.div
            key={opt.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`p-6 rounded-2xl bg-slate-900/60 border backdrop-blur-sm flex flex-col justify-between transition-all ${
              opt.id === 'FOOD_PLUS_SUPPLEMENT'
                ? 'border-teal-500/50 shadow-xl shadow-teal-500/10 relative'
                : 'border-slate-800 hover:border-slate-700'
            }`}
          >
            {opt.id === 'FOOD_PLUS_SUPPLEMENT' && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-teal-500 text-slate-950 shadow-md">
                Recommended Choice
              </div>
            )}

            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs font-mono text-slate-400">{opt.category}</span>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${opt.badgeColor}`}>
                  {opt.badge}
                </span>
              </div>

              <h3 className="text-lg font-bold text-slate-100 mb-4">
                {opt.title}
              </h3>

              {/* Score Hero */}
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-900 mb-6 text-center">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Unified Intervention Score (UIS)
                </div>
                <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-1">
                  {opt.uisScore} <span className="text-xs font-normal text-slate-500">/ 100</span>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {opt.bestFor}
                </div>
              </div>

              {/* Core Metrics Table */}
              <div className="space-y-2.5 text-xs mb-6">
                <div className="flex justify-between pb-2 border-b border-slate-800/60">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-cyan-400" />
                    Recovery Horizon:
                  </span>
                  <span className="font-bold text-slate-200 font-mono">~{opt.recoveryDays} Days</span>
                </div>
                <div className="flex justify-between pb-2 border-b border-slate-800/60">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <DollarSign className="w-3.5 h-3.5 text-amber-400" />
                    Estimated Cost:
                  </span>
                  <span className="font-bold text-slate-200 font-mono">${opt.weeklyCost.toFixed(2)} / wk</span>
                </div>
                <div className="flex justify-between pb-2 border-b border-slate-800/60">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-emerald-400" />
                    Preparation Burden:
                  </span>
                  <span className="font-bold text-slate-200">{opt.burden}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-teal-400" />
                    Adherence Likelihood:
                  </span>
                  <span className="font-bold text-emerald-400 font-mono">{opt.adherence}%</span>
                </div>
              </div>

              {/* Pros & Cons */}
              <div className="space-y-3 mb-6">
                <div>
                  <div className="text-[11px] font-bold uppercase text-emerald-400 mb-1.5">Clinical Advantages</div>
                  <ul className="space-y-1">
                    {opt.pros.map((p, i) => (
                      <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="text-[11px] font-bold uppercase text-amber-400 mb-1.5">Considerations</div>
                  <ul className="space-y-1">
                    {opt.cons.map((c, i) => (
                      <li key={i} className="text-xs text-slate-400 flex items-start gap-1.5">
                        <X className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                        <span>{c}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <button
              onClick={() => alert(`Selected ${opt.title} as your primary clinical protocol.`)}
              className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                opt.id === 'FOOD_PLUS_SUPPLEMENT'
                  ? 'bg-teal-500 hover:bg-teal-400 text-slate-950 shadow-lg shadow-teal-500/20'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
              }`}
            >
              <span>Activate This Strategy</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
