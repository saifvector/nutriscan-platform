import React, { useState, useMemo } from 'react'
import {
  Sparkles, AlertTriangle, ArrowDownUp, ChevronDown, ChevronUp,
  Brain, ShieldCheck, CheckCircle2, Utensils, Zap, Info, ArrowUpRight
} from 'lucide-react'
import { NUTRIENT_ICONS } from '../../lib/constants'
import { type DeficiencyItem, type ShapFeature } from './DeficiencyRiskChart'
import { type PrecisionFoodItem } from './PrecisionFoodGrid'

interface ClinicalReasoningCenterProps {
  overallStatus: 'CRITICAL' | 'HIGH_RISK' | 'MODERATE' | 'STABLE'
  patientName: string
  highPriorityFindings: string[]
  recommendedActions: Array<{
    priority: string
    action: string
    rationale: string
  }>
  deficiencies: DeficiencyItem[]
  shapFeatures?: ShapFeature[]
  precisionFoods?: PrecisionFoodItem[]
}

type SortMode = 'RISK_DESC' | 'CONFIDENCE' | 'ALPHA'

export default function ClinicalReasoningCenter({
  overallStatus,
  patientName,
  highPriorityFindings,
  recommendedActions,
  deficiencies,
  shapFeatures = [],
  precisionFoods = []
}: ClinicalReasoningCenterProps) {
  const [sortMode, setSortMode] = useState<SortMode>('RISK_DESC')
  const [showAll, setShowAll] = useState<boolean>(false)
  const [expandedNutrient, setExpandedNutrient] = useState<string | null>(
    deficiencies.length > 0 ? deficiencies[0].nutrient : null
  )

  const sortedDeficiencies = useMemo(() => {
    const list = [...deficiencies]
    switch (sortMode) {
      case 'RISK_DESC':
        return list.sort((a, b) => b.probability - a.probability)
      case 'CONFIDENCE':
        return list.sort((a, b) => b.confidence_score - a.confidence_score)
      case 'ALPHA':
        return list.sort((a, b) => a.nutrient.localeCompare(b.nutrient))
      default:
        return list
    }
  }, [deficiencies, sortMode])

  const toggleExpand = (nutrient: string) => {
    setExpandedNutrient(prev => (prev === nutrient ? null : nutrient))
  }

  const statusColor =
    overallStatus === 'CRITICAL'
      ? 'border-rose-500/30 bg-rose-500/5 text-rose-300'
      : overallStatus === 'HIGH_RISK'
      ? 'border-amber-500/30 bg-amber-500/5 text-amber-300'
      : 'border-cyan-500/30 bg-cyan-500/5 text-cyan-300'

  return (
    <div className="w-full space-y-5 font-sans">
      {/* ─── 1. Executive Clinical Synthesis Banner ─── */}
      <div className={`rounded-2xl border p-4.5 backdrop-blur-sm transition-all ${statusColor}`}>
        <div className="flex items-center justify-between gap-3 pb-3 border-b border-slate-800/60">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Executive Clinical Synthesis
            </span>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border bg-slate-950/60 font-mono">
            {overallStatus.replace('_', ' ')}
          </span>
        </div>

        {/* Primary Diagnosis & Findings */}
        <div className="pt-3 space-y-2">
          <p className="text-xs md:text-sm text-slate-200 font-medium leading-relaxed">
            Multivariate risk synthesis indicates primary deficiency clusters driven by dietary restrictions and metabolic load for <span className="text-white font-semibold">{patientName}</span>.
          </p>

          <div className="space-y-1.5 pt-1">
            {highPriorityFindings.slice(0, 3).map((finding, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                <span className="leading-snug">{finding}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Action Pills */}
        <div className="mt-3 pt-3 border-t border-slate-800/40 grid grid-cols-1 sm:grid-cols-2 gap-2">
          {recommendedActions.slice(0, 2).map((action, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800/50 text-xs"
            >
              <div className="flex items-center gap-1.5 font-semibold text-cyan-300 text-[11px]">
                <CheckCircle2 className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                <span>{action.priority}: {action.action.split(':')[0]}</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-tight">
                {action.rationale}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* ─── 2. Interactive Ranked Deficiency Risk Matrix ─── */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4.5 backdrop-blur-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3.5 border-b border-slate-800/60">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <AlertTriangle className="w-3.5 h-3.5" />
              </span>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Ranked Deficiency Risk Matrix
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Calibrated multi-target predictions with Platt scaling & TreeSHAP attributions
            </p>
          </div>

          {/* Sort Controls */}
          <div className="flex items-center gap-1 p-0.5 rounded-lg bg-slate-950/80 border border-slate-800 self-start sm:self-auto">
            <span className="text-[10px] uppercase font-bold text-slate-500 px-1.5 flex items-center gap-1">
              <ArrowDownUp className="w-2.5 h-2.5" /> Sort:
            </span>
            {[
              { id: 'RISK_DESC', label: 'Risk' },
              { id: 'CONFIDENCE', label: 'Conf' },
              { id: 'ALPHA', label: 'A–Z' },
            ].map(s => (
              <button
                key={s.id}
                onClick={() => setSortMode(s.id as SortMode)}
                className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-all ${
                  sortMode === s.id
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Matrix Rows */}
        <div className="space-y-2 mt-3.5">
          {(showAll ? sortedDeficiencies : sortedDeficiencies.slice(0, 6)).map((def, idx) => {
            const isExpanded = expandedNutrient === def.nutrient
            const probPct = Math.round(def.probability * 100)
            const confPct = Math.round(def.confidence_score * 100)
            const icon = NUTRIENT_ICONS[def.nutrient] || '💊'

            const riskBadgeStyle =
              def.risk_level === 'CRITICAL'
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                : def.risk_level === 'HIGH'
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : def.risk_level === 'MODERATE'
                ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40'
                : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'

            const barGradient =
              def.risk_level === 'CRITICAL'
                ? 'bg-rose-500'
                : def.risk_level === 'HIGH'
                ? 'bg-amber-500'
                : def.risk_level === 'MODERATE'
                ? 'bg-yellow-400'
                : 'bg-emerald-400'

            return (
              <div
                key={def.nutrient}
                className={`rounded-xl border transition-all overflow-hidden ${
                  isExpanded
                    ? 'bg-slate-950/80 border-cyan-500/40 shadow-lg'
                    : 'bg-slate-950/40 border-slate-800/60 hover:border-slate-700/80 hover:bg-slate-950/60'
                }`}
              >
                {/* Collapsible Row Header */}
                <div
                  onClick={() => toggleExpand(def.nutrient)}
                  className="p-3 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-2.5"
                >
                  <div className="flex items-center gap-2.5 min-w-[160px]">
                    <span className="text-xl p-1.5 rounded-lg bg-slate-900 border border-slate-800/80 shrink-0">
                      {icon}
                    </span>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-bold text-xs sm:text-sm text-white">
                          {def.nutrient}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          #{idx + 1}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span className={`text-[9px] px-1.5 py-0.2 rounded-full font-bold border ${riskBadgeStyle}`}>
                          {def.risk_level}
                        </span>
                        <span className="text-[10px] text-slate-400">
                          {confPct}% conf
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Center: Probability Bar */}
                  <div className="flex-1 max-w-sm px-2">
                    <div className="flex justify-between items-center text-[10px] mb-1 font-mono">
                      <span className="text-slate-400">Calibrated Risk</span>
                      <span className="font-bold text-white">{probPct}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-800/80 p-0.5">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${barGradient}`}
                        style={{ width: `${Math.max(6, probPct)}%` }}
                      />
                    </div>
                  </div>

                  {/* Right: Expand Toggle */}
                  <div className="flex items-center gap-2 self-end sm:self-auto text-xs text-slate-400">
                    <span className="text-[10px] text-cyan-400 hidden sm:inline">
                      {isExpanded ? 'Hide SHAP' : 'Explain'}
                    </span>
                    <div className="p-1 rounded-md bg-slate-900 border border-slate-800 text-slate-300">
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </div>
                  </div>
                </div>

                {/* TreeSHAP Feature Attribution Drawer */}
                {isExpanded && (
                  <div className="p-3.5 bg-slate-900/90 border-t border-slate-800/80 space-y-2.5 animate-in fade-in duration-200">
                    <div className="flex items-center justify-between text-xs pb-2 border-b border-slate-800/60">
                      <div className="flex items-center gap-1.5 font-bold text-cyan-400">
                        <Brain className="w-3.5 h-3.5" />
                        <span>TreeSHAP Feature Attributions</span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">
                        Additive Model Φ Values
                      </span>
                    </div>

                    <div className="space-y-1.5">
                      {shapFeatures.slice(0, 3).map((shap, sIdx) => {
                        const isPos = shap.shap_value > 0
                        return (
                          <div
                            key={sIdx}
                            className="flex items-center justify-between p-2 rounded-lg bg-slate-950/60 border border-slate-800/60 text-xs"
                          >
                            <div>
                              <div className="font-semibold text-slate-200 text-[11px]">{shap.feature}</div>
                              <div className="text-[10px] text-slate-400">{shap.description}</div>
                            </div>
                            <span className={`font-mono text-xs font-bold ${
                              isPos ? 'text-rose-400' : 'text-emerald-400'
                            }`}>
                              {isPos ? `+${shap.shap_value.toFixed(2)}` : shap.shap_value.toFixed(2)}
                            </span>
                          </div>
                        )
                      })}
                    </div>

                    {/* Primary Symptom Correlation Pills */}
                    {def.primary_symptom_matches.length > 0 && (
                      <div className="pt-2 flex items-center gap-1.5 flex-wrap">
                        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                          Correlated Symptoms:
                        </span>
                        {def.primary_symptom_matches.map((sym, symIdx) => (
                          <span
                            key={symIdx}
                            className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700 font-medium"
                          >
                            {sym}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {sortedDeficiencies.length > 6 && (
          <div className="pt-3 text-center border-t border-slate-800/40 mt-3">
            <button
              type="button"
              onClick={() => setShowAll(!showAll)}
              className="px-3.5 py-1.5 rounded-xl bg-slate-950/60 hover:bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white transition-all inline-flex items-center gap-1.5"
            >
              {showAll ? (
                <>
                  <span>Collapse to Top Priority Targets</span>
                  <ChevronUp className="w-3.5 h-3.5 text-cyan-400" />
                </>
              ) : (
                <>
                  <span>View All {sortedDeficiencies.length} Screened Nutrients</span>
                  <ChevronDown className="w-3.5 h-3.5 text-cyan-400" />
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* ─── 3. Targeted Precision Foods ─── */}
      {precisionFoods.length > 0 && (
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4.5 backdrop-blur-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
            <div className="flex items-center gap-2">
              <span className="p-1 rounded-md bg-teal-500/10 text-teal-400 border border-teal-500/20">
                <Utensils className="w-3.5 h-3.5" />
              </span>
              <h3 className="text-sm font-bold text-white tracking-tight">
                Targeted Whole Food Prescriptions
              </h3>
            </div>
            <span className="text-[10px] text-teal-400 font-mono font-medium">
              High Bioavailability Focus
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-3.5">
            {precisionFoods.slice(0, 4).map((food, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/60 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-xs font-bold text-slate-100">{food.title}</span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-teal-500/15 text-teal-300 font-mono">
                      {food.dosage_or_serving}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-tight">
                    {food.biochemical_mechanism}
                  </p>
                </div>
                <div className="mt-2 pt-2 border-t border-slate-800/40 flex justify-between items-center text-[10px] text-slate-400">
                  <span>Frequency: {food.frequency}</span>
                  <span className="text-teal-400 font-medium">Target Repletion</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
