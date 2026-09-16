import React, { useState } from 'react'
import { ChevronDown, ChevronUp, AlertTriangle, TrendingUp } from 'lucide-react'

export interface DeficiencyData {
  nutrient: string
  risk_level: string
  probability: number
  confidence_score: number
  primary_symptom_matches: string[]
}

interface TopDeficienciesSectionProps {
  deficiencies: DeficiencyData[]
  dietaryPattern?: string
}

export default function TopDeficienciesSection({
  deficiencies,
  dietaryPattern = 'VEGAN'
}: TopDeficienciesSectionProps) {
  const [showAll, setShowAll] = useState(false)

  // Sort by probability descending
  const sorted = [...deficiencies].sort((a, b) => b.probability - a.probability)
  const topThree = sorted.slice(0, 3)
  const displayed = showAll ? sorted : topThree

  // Helper to generate clear, plain-English clinical driver description
  const getClinicalDriver = (nutrient: string, symptoms: string[]) => {
    const symList = symptoms.length > 0 ? symptoms.slice(0, 2).join(' and ') : 'reported fatigue'
    const lowerDiet = dietaryPattern.toLowerCase()

    switch (nutrient.toLowerCase()) {
      case 'vitamin d':
        return `Driven by limited sunlight exposure and lack of fortified dietary sources; strongly correlates with ${symList}.`
      case 'vitamin b12':
        return `Commonly depleted in ${lowerDiet} diets due to minimal animal products; correlates with ${symList}.`
      case 'iron':
        return `Non-heme iron absorption constraints in plant-based diets contribute to marginal reserves and ${symList}.`
      case 'calcium':
        return `Lower dairy/calcium intake combined with marginal Vitamin D absorption.`
      case 'magnesium':
        return `Suboptimal leafy greens and nut intake coupled with elevated metabolic stress.`
      default:
        return `Correlates with ${symList} and current dietary pattern.`
    }
  }

  return (
    <section
      className="rounded-2xl overflow-hidden bg-[#131B2B] border border-slate-800/60 shadow-sm"
      style={{
        animation: 'fadeSlideUp 0.55s ease-out 0.1s both',
      }}
    >
      {/* Section Header */}
      <div className="px-6 sm:px-8 pt-6 sm:pt-8 pb-4 flex items-baseline justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[#14D9C4] opacity-70" />
            Top Priority Deficiencies
          </h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Ranked by calibrated probability and symptomatic impact
          </p>
        </div>
        <span className="text-[11px] text-slate-500 font-mono tabular-nums">
          {displayed.length} of {deficiencies.length}
        </span>
      </div>

      {/* Deficiency Items */}
      <div className="px-6 sm:px-8 pb-6 sm:pb-8 space-y-3">
        {displayed.map((def, idx) => {
          const probPct = Math.round(def.probability * 100)
          const isHigh = def.risk_level === 'CRITICAL' || def.risk_level === 'HIGH'
          const isMod = def.risk_level === 'MODERATE'

          const accentColor = isHigh ? '#f43f5e' : isMod ? '#f59e0b' : '#14D9C4'
          const badgeBg = isHigh
            ? 'rgba(244,63,94,0.08)'
            : isMod
            ? 'rgba(245,158,11,0.08)'
            : 'rgba(20,217,196,0.08)'
          const badgeText = isHigh ? 'text-rose-300' : isMod ? 'text-amber-300' : 'text-emerald-300'

          return (
            <div
              key={def.nutrient}
              className="group relative p-4 sm:p-5 rounded-xl transition-all duration-200 cursor-default bg-[#0B0F14] border border-slate-800/60 hover:border-slate-700/80 hover:bg-slate-900/50"
            >
              {/* Left accent line */}
              <div
                className="absolute left-0 top-3 bottom-3 w-[3px] rounded-full"
                style={{ background: accentColor, opacity: 0.6 }}
              />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 ml-3">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-sm font-semibold text-white whitespace-nowrap">
                    {def.nutrient}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-md text-[10px] font-semibold ${badgeText}`}
                    style={{ background: badgeBg }}
                  >
                    {isHigh ? 'HIGH' : def.risk_level}
                  </span>
                </div>

                {/* Probability display with bar */}
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs text-slate-400 font-mono tabular-nums">
                    <strong className="text-white font-semibold">{probPct}%</strong> risk
                  </span>
                  <div className="w-20 h-1.5 bg-slate-800/60 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${Math.max(8, probPct)}%`,
                        background: accentColor,
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Clinical rationale */}
              <p className="text-xs text-slate-400 leading-relaxed mt-2.5 ml-3">
                {getClinicalDriver(def.nutrient, def.primary_symptom_matches)}
              </p>
            </div>
          )
        })}
      </div>

      {/* Expand toggle */}
      {sorted.length > 3 && (
        <div className="px-6 sm:px-8 pb-5">
          <button
            onClick={() => setShowAll(!showAll)}
            className="w-full py-2.5 rounded-xl text-[11px] font-medium text-slate-400 hover:text-slate-200 transition-all flex items-center justify-center gap-1.5"
            style={{
              background: 'rgba(2,6,23,0.3)',
              border: '1px solid rgba(51,65,85,0.2)',
            }}
          >
            {showAll ? (
              <>
                <span>Show top 3 only</span>
                <ChevronUp className="w-3 h-3" />
              </>
            ) : (
              <>
                <span>View all {sorted.length} nutrients</span>
                <ChevronDown className="w-3 h-3" />
              </>
            )}
          </button>
        </div>
      )}
    </section>
  )
}
