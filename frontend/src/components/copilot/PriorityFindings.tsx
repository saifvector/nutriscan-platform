import React, { useState } from 'react'
import { ChevronDown, ChevronUp, AlertTriangle, Activity, FlaskConical, Stethoscope } from 'lucide-react'

export interface PriorityFindingItem {
  nutrient: string
  risk_level: string
  probability: number
  primary_symptom_matches?: string[]
  driver?: string
  competing_causes?: Array<{
    etiology: string
    likelihood: string
    clinical_rationale: string
    distinguishing_features: string
  }>
  confirmatory_diagnostics?: Array<{
    test: string
    purpose: string
    cutoff: string
  }>
}

interface PriorityFindingsProps {
  findings: PriorityFindingItem[]
  dietaryPattern: string
}

export default function PriorityFindings({
  findings,
  dietaryPattern
}: PriorityFindingsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0) // First item open by default

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx)
  }

  // Helper driver description if none provided
  const getDriver = (item: PriorityFindingItem) => {
    if (item.driver) return item.driver
    const symptoms = (item.primary_symptom_matches || []).join(', ')
    const diet = dietaryPattern.toLowerCase()
    switch (item.nutrient.toLowerCase()) {
      case 'vitamin d':
        return `Suboptimal dermal synthesis combined with strict ${diet} intake; strongly correlates with reported fatigue and musculoskeletal sensitivity.`
      case 'vitamin b12':
        return `Restricted cobalamin bioavailability typical of ${diet} diets; correlates with neurological fatigue and cognitive sluggishness.`
      case 'iron':
        return `Low non-heme iron absorption efficiency resulting in depleted ferritin stores and low cellular energy output.`
      case 'calcium':
        return `Dietary avoidance of dairy without adequate fortified calcium substitutes, impacting bone mineral turnover.`
      case 'magnesium':
        return `Elevated metabolic turnover and suboptimal leafy green consumption driving neuromuscular excitability.`
      default:
        return `Strong clinical correlation with reported ${symptoms || 'symptoms'} under current ${diet} profile.`
    }
  }

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <span>Priority Findings</span>
            <span className="text-xs font-normal text-slate-400 font-mono">({findings.length} targets)</span>
          </h2>
        </div>
        <span className="text-xs text-slate-400 font-medium">Ranked by calibrated probability</span>
      </div>

      <div className="space-y-2">
        {findings.map((item, idx) => {
          const isExpanded = expandedIndex === idx
          const isCritical = item.risk_level === 'CRITICAL' || item.probability >= 0.75
          const isHigh = item.risk_level === 'HIGH' || (item.probability >= 0.55 && item.probability < 0.75)
          const isModerate = !isCritical && !isHigh

          const probPercent = Math.round(item.probability * 100)
          const driverText = getDriver(item)

          return (
            <div
              key={item.nutrient}
              className={`rounded-xl transition-all duration-150 border ${
                isExpanded
                  ? 'bg-[#111827] border-slate-700/80 shadow-md'
                  : 'bg-[#111827]/60 hover:bg-[#111827] border-slate-800/70'
              }`}
            >
              {/* Row Header */}
              <button
                onClick={() => toggleExpand(idx)}
                className="w-full text-left p-4 flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  {/* Rank number */}
                  <span className="text-xs font-mono font-medium text-slate-400 w-4 text-center shrink-0">
                    0{idx + 1}
                  </span>

                  {/* Severity Dot Indicator */}
                  <span
                    className={`w-2 h-2 rounded-full shrink-0 ${
                      isCritical ? 'bg-rose-500' : isHigh ? 'bg-rose-400' : 'bg-amber-400'
                    }`}
                  />

                  {/* Nutrient Title & Primary Symptom */}
                  <div className="min-w-0">
                    <div className="flex items-center gap-2.5">
                      <span className="text-sm font-semibold text-white tracking-tight">
                        {item.nutrient} Deficiency
                      </span>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded uppercase tracking-wider ${
                          isCritical
                            ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                            : isHigh
                            ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                            : 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                        }`}
                      >
                        {item.risk_level}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right: Probability & Chevron */}
                <div className="flex items-center gap-4 shrink-0">
                  <div className="text-right">
                    <span className="text-sm font-bold font-mono text-white">
                      {probPercent}%
                    </span>
                    <span className="text-[10px] text-slate-400 block font-mono">calibrated</span>
                  </div>
                  <div className="p-1 text-slate-400 hover:text-white">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </div>
              </button>

              {/* Expandable Details Drawer */}
              {isExpanded && (
                <div className="px-5 pb-5 pt-1 border-t border-slate-800/60 text-xs space-y-4">
                  {/* Clinical Etiology */}
                  <div>
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                      Pathophysiological Etiology
                    </span>
                    <p className="text-slate-300 leading-relaxed text-xs">
                      {driverText}
                    </p>
                  </div>

                  {/* Symptom Correlation */}
                  {item.primary_symptom_matches && item.primary_symptom_matches.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[11px] text-slate-400">Symptom matches:</span>
                      {item.primary_symptom_matches.map(s => (
                        <span key={s} className="px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 text-[11px]">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Competing Non-Dietary Etiologies (from Differential) */}
                  {item.competing_causes && item.competing_causes.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/40">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                        Competing Pathologies Evaluated
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {item.competing_causes.slice(0, 2).map((cc, i) => (
                          <div key={i} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
                            <div className="flex justify-between items-center text-[11px] mb-1">
                              <span className="font-semibold text-slate-200">{cc.etiology}</span>
                              <span className={`px-1.5 py-0.2 rounded text-[10px] ${
                                cc.likelihood === 'HIGH' ? 'text-rose-300 bg-rose-500/10' : 'text-amber-300 bg-amber-500/10'
                              }`}>
                                {cc.likelihood}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-400 leading-normal">{cc.clinical_rationale}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Confirmatory Lab Diagnostics Orders */}
                  {item.confirmatory_diagnostics && item.confirmatory_diagnostics.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/40">
                      <span className="text-[11px] font-semibold text-teal-400 uppercase tracking-wider block mb-2 flex items-center gap-1.5">
                        <FlaskConical className="w-3.5 h-3.5" />
                        <span>Confirmatory Lab Orders</span>
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {item.confirmatory_diagnostics.map((cd, i) => (
                          <div key={i} className="flex justify-between items-center p-2 rounded-lg bg-slate-900/40 border border-slate-800/60">
                            <div>
                              <span className="font-medium text-slate-200 block text-xs">{cd.test}</span>
                              <span className="text-[10px] text-slate-400">{cd.purpose}</span>
                            </div>
                            <span className="font-mono text-xs text-teal-400 font-semibold shrink-0 ml-2">{cd.cutoff}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
