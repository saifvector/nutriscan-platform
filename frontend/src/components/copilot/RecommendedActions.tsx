import React from 'react'
import { CheckCircle2, ArrowRight } from 'lucide-react'

export interface RecommendedAction {
  priority: string
  action: string
  rationale: string
}

interface RecommendedActionsProps {
  actions: RecommendedAction[]
}

export default function RecommendedActions({ actions }: RecommendedActionsProps) {
  if (!actions || actions.length === 0) return null

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
          Recommended Actions
        </h2>
        <span className="text-xs text-slate-400 font-medium">Physician-directed timeline</span>
      </div>

      <div className="rounded-2xl bg-[#111827] border border-slate-800/80 p-5 space-y-4">
        {actions.map((act, idx) => {
          const isImmediate = idx === 0 || act.priority.toLowerCase().includes('immediate') || act.priority.toLowerCase().includes('1')

          return (
            <div
              key={idx}
              className={`flex items-start gap-4 pb-4 ${
                idx !== actions.length - 1 ? 'border-b border-slate-800/60' : ''
              }`}
            >
              {/* Step / Priority Indicator */}
              <div className="flex flex-col items-center shrink-0">
                <span
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold font-mono ${
                    isImmediate
                      ? 'bg-teal-500/15 text-teal-400 border border-teal-500/30'
                      : 'bg-slate-800 text-slate-400 border border-slate-700/50'
                  }`}
                >
                  {idx + 1}
                </span>
              </div>

              {/* Action Details */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded uppercase tracking-wider ${
                      isImmediate
                        ? 'bg-teal-500/10 text-teal-300 border border-teal-500/20'
                        : 'bg-slate-800/80 text-slate-400 border border-slate-700/40'
                    }`}
                  >
                    {act.priority || `Priority ${idx + 1}`}
                  </span>
                </div>
                <h3 className="text-sm font-medium text-white leading-snug">
                  {act.action}
                </h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  {act.rationale}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
