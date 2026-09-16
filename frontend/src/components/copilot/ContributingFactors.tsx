import React from 'react'
import { Layers, ArrowRight } from 'lucide-react'

export interface ContributingFactorItem {
  category: string
  factor: string
  impact: string
}

interface ContributingFactorsProps {
  factors: ContributingFactorItem[]
}

export default function ContributingFactors({ factors }: ContributingFactorsProps) {
  if (!factors || factors.length === 0) return null

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Layers className="w-4 h-4 text-teal-400" />
          <span>Contributing Etiological Factors</span>
        </h2>
        <span className="text-xs text-slate-400 font-medium">Multifactorial driver analysis</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {factors.map((item, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-[#111827] border border-slate-800/80 flex flex-col justify-between"
          >
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20">
                {item.category}
              </span>
              <h4 className="text-sm font-semibold text-white mt-2.5 leading-snug">
                {item.factor}
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                {item.impact}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
