import React from 'react'
import { Sparkles, ArrowUpRight } from 'lucide-react'

interface ExecutiveSummaryProps {
  summary: string
  patientName: string
  topDeficiencies: Array<{
    nutrient: string
    risk_level: string
    probability: number
  }>
}

export default function ExecutiveSummary({
  summary,
  patientName,
  topDeficiencies
}: ExecutiveSummaryProps) {
  // Extract high-probability deficiency names for key finding highlights
  const criticalNutrients = topDeficiencies
    .filter(d => d.risk_level === 'CRITICAL' || d.risk_level === 'HIGH' || d.probability >= 0.6)
    .map(d => d.nutrient)

  const formattedSummary = summary || `${patientName}'s clinical assessment demonstrates significant biomarker and dietary indicators of nutritional insufficiency. Key risk clusters center around ${criticalNutrients.slice(0, 2).join(' and ')}, exacerbated by restrictive dietary intake and diminished metabolic reserves. Immediate targeted repletion alongside confirmatory laboratory evaluation is advised to restore homeostatic balance.`

  return (
    <section className="p-6 rounded-2xl bg-[#111827] border border-slate-800/80">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-teal-400">
            Executive Clinical Summary
          </span>
          <span className="w-1 h-1 rounded-full bg-slate-600" />
          <span className="text-[11px] text-slate-400 font-medium">Physician Briefing</span>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">Evidence Grade: High (AHA/NIH)</span>
      </div>

      {/* Narrative Body */}
      <p className="text-sm md:text-[15px] text-slate-200 leading-relaxed font-normal">
        {formattedSummary}
      </p>

      {/* Inline Highlights (Quick-Scan tags) */}
      {criticalNutrients.length > 0 && (
        <div className="mt-4 pt-3.5 border-t border-slate-800/60 flex items-center gap-2 flex-wrap">
          <span className="text-[11px] text-slate-400">Primary Targets:</span>
          {topDeficiencies.slice(0, 3).map(def => {
            const isHigh = def.risk_level === 'CRITICAL' || def.risk_level === 'HIGH' || def.probability >= 0.65
            return (
              <span
                key={def.nutrient}
                className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-medium ${
                  isHigh
                    ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                    : 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isHigh ? 'bg-rose-400' : 'bg-amber-400'}`} />
                <span>{def.nutrient}</span>
                <span className="font-mono text-[10px] opacity-80">{Math.round(def.probability * 100)}%</span>
              </span>
            )
          })}
        </div>
      )}
    </section>
  )
}
