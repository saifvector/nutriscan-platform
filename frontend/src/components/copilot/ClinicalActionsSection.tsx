import React from 'react'
import { Zap, ArrowRight } from 'lucide-react'

export interface RecommendedActionItem {
  priority: string
  action: string
  rationale: string
}

export interface SupplementPlanItem {
  title: string
  dosage_or_serving: string
  frequency: string
  biochemical_mechanism: string
}

interface ClinicalActionsSectionProps {
  actions: RecommendedActionItem[]
  supplements?: SupplementPlanItem[]
}

export default function ClinicalActionsSection({
  actions,
  supplements = []
}: ClinicalActionsSectionProps) {
  // Combine top actions with supplement protocol for a unified, clear directives list
  const combinedActions = actions.length > 0
    ? actions.slice(0, 3)
    : supplements.slice(0, 3).map((s, i) => ({
        priority: `Step ${i + 1}`,
        action: `${s.title} (${s.dosage_or_serving}, ${s.frequency})`,
        rationale: s.biochemical_mechanism
      }))

  const stepColors = ['#14D9C4', '#38bdf8', '#a78bfa']

  return (
    <section
      className="rounded-2xl overflow-hidden bg-[#131B2B] border border-slate-800/60 shadow-sm"
      style={{
        animation: 'fadeSlideUp 0.55s ease-out 0.2s both',
      }}
    >
      {/* Section Header */}
      <div className="px-6 sm:px-8 pt-6 sm:pt-8 pb-4">
        <h3 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
          <Zap className="w-4 h-4 text-[#14D9C4] opacity-70" />
          Recommended Actions
        </h3>
        <p className="text-[11px] text-slate-500 mt-0.5">
          Targeted supplementation and dietary modifications
        </p>
      </div>

      {/* Action Items */}
      <div className="px-6 sm:px-8 pb-6 sm:pb-8 space-y-3">
        {combinedActions.map((item, idx) => {
          const color = stepColors[idx] || stepColors[0]

          return (
            <div
              key={idx}
              className="group relative p-4 sm:p-5 rounded-xl transition-all duration-200 bg-[#0B0F14] border border-slate-800/60 hover:border-slate-700/80 hover:bg-slate-900/50"
            >
              {/* Step number indicator */}
              <div className="flex items-start gap-4">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold"
                  style={{
                    background: `${color}10`,
                    color: color,
                    border: `1px solid ${color}20`,
                  }}
                >
                  {idx + 1}
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="text-sm font-medium text-white leading-snug">
                    {item.action}
                  </h4>
                  <p className="text-xs text-slate-400 leading-relaxed mt-1.5">
                    {item.rationale}
                  </p>
                </div>
                <ArrowRight
                  className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-400 shrink-0 mt-1 transition-colors"
                />
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
