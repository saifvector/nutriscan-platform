import React, { useState } from 'react'
import { Zap, AlertTriangle, Cpu, Activity, Clock, ShieldCheck, ArrowRightLeft, Sparkles } from 'lucide-react'

export interface NutrientInteractionItem {
  id: string
  primary_nutrient: string
  secondary_nutrient: string
  interaction_type: 'SYNERGISTIC' | 'ANTAGONISTIC' | 'ENZYMATIC_DEPENDENCY' | 'HOMEOSTATIC_BALANCE'
  effect_summary: string
  biochemical_mechanism: string
  clinical_guidance: string
  timing_spacing_hours?: number
  evidence_grade: 'GRADE_A' | 'GRADE_B' | 'GRADE_C'
  source_reference: string
}

interface NutrientInteractionExplorerProps {
  interactions: NutrientInteractionItem[]
  activeNutrients?: string[]
}

export const NutrientInteractionExplorer: React.FC<NutrientInteractionExplorerProps> = ({
  interactions,
  activeNutrients = []
}) => {
  const [filterType, setFilterType] = useState<string>('ALL')
  const [selectedPair, setSelectedPair] = useState<NutrientInteractionItem | null>(null)

  const filteredInteractions = interactions.filter(item => {
    if (filterType === 'ALL') return true
    return item.interaction_type === filterType
  })

  const getTypeStyle = (type: string) => {
    switch (type) {
      case 'SYNERGISTIC':
        return {
          badge: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20',
          icon: <Zap className="w-3.5 h-3.5 text-emerald-500" />,
          label: 'Synergistic Absorption'
        }
      case 'ANTAGONISTIC':
        return {
          badge: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />,
          label: 'Competitive Inhibition'
        }
      case 'ENZYMATIC_DEPENDENCY':
        return {
          badge: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
          icon: <Cpu className="w-3.5 h-3.5 text-purple-500" />,
          label: 'Enzymatic Co-Factor'
        }
      case 'HOMEOSTATIC_BALANCE':
      default:
        return {
          badge: 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20',
          icon: <Activity className="w-3.5 h-3.5 text-sky-500" />,
          label: 'Homeostatic Axis'
        }
    }
  }

  return (
    <div className="bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5 text-teal-600 dark:text-teal-400" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              Nutrient Interaction & Biochemical Synergy Engine
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Biochemical cross-talk, divalent cation competition, and absorption synchronizations governed by NIH ODS standards.
          </p>
        </div>

        {/* Interaction Type Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl">
          {[
            { id: 'ALL', label: 'All Rules' },
            { id: 'SYNERGISTIC', label: 'Synergies' },
            { id: 'ANTAGONISTIC', label: 'Inhibitions' },
            { id: 'ENZYMATIC_DEPENDENCY', label: 'Co-Factors' },
            { id: 'HOMEOSTATIC_BALANCE', label: 'Homeostasis' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                filterType === tab.id
                  ? 'bg-white dark:bg-slate-700 text-teal-700 dark:text-teal-300 shadow-sm font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Interactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredInteractions.map(item => {
          const typeStyle = getTypeStyle(item.interaction_type)
          const isSelected = selectedPair?.id === item.id

          return (
            <div
              key={item.id}
              onClick={() => setSelectedPair(isSelected ? null : item)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isSelected
                  ? 'border-teal-500 bg-teal-50/20 dark:bg-teal-950/20 ring-2 ring-teal-500/20'
                  : 'border-slate-200/80 dark:border-slate-800/80 bg-slate-50/40 dark:bg-slate-800/20 hover:border-slate-300 dark:hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-900 dark:text-white">
                    {item.primary_nutrient}
                  </span>
                  <span className="text-slate-400 text-xs">↔</span>
                  <span className="font-bold text-sm text-slate-900 dark:text-white">
                    {item.secondary_nutrient}
                  </span>
                </div>
                <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${typeStyle.badge}`}>
                  {typeStyle.icon}
                  {typeStyle.label}
                </span>
              </div>

              <p className="text-xs text-slate-700 dark:text-slate-300 font-medium mb-2">
                {item.effect_summary}
              </p>

              <div className="p-2.5 rounded-lg bg-white/70 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800/60 text-xs text-slate-600 dark:text-slate-400 space-y-1.5 mb-3">
                <div className="flex items-start gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-teal-600 dark:text-teal-400 shrink-0 mt-0.5" />
                  <span><strong>Mechanism:</strong> {item.biochemical_mechanism}</span>
                </div>
                <div className="flex items-start gap-1.5 text-slate-700 dark:text-slate-300">
                  <ShieldCheck className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                  <span><strong>Clinical Protocol:</strong> {item.clinical_guidance}</span>
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 dark:border-slate-800/80 text-[11px] text-slate-500">
                {item.timing_spacing_hours ? (
                  <span className="inline-flex items-center gap-1 font-semibold text-amber-600 dark:text-amber-400">
                    <Clock className="w-3 h-3" /> Space intake by {item.timing_spacing_hours}+ hours
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold">
                    <Zap className="w-3 h-3" /> Co-administration Recommended
                  </span>
                )}
                <span className="text-[10px] text-slate-400 truncate max-w-[200px]">
                  Ref: {item.source_reference}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
