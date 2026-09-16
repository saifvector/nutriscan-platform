import React, { useState } from 'react'
import { FlaskConical, ChevronDown, ChevronUp, AlertCircle, CheckCircle2 } from 'lucide-react'

export interface BiomarkerItem {
  marker_name: string
  value: number
  unit: string
  reference_range: string
  status: string
}

interface LabHighlightsProps {
  biomarkers: BiomarkerItem[]
}

export default function LabHighlights({ biomarkers }: LabHighlightsProps) {
  const [showAll, setShowAll] = useState(false)

  // Filter abnormal or borderline markers first
  const abnormal = biomarkers.filter(b => b.status !== 'OPTIMAL' && b.status !== 'NORMAL')
  const optimal = biomarkers.filter(b => b.status === 'OPTIMAL' || b.status === 'NORMAL')

  const displayed = showAll ? [...abnormal, ...optimal] : abnormal.length > 0 ? abnormal : biomarkers.slice(0, 4)

  return (
    <div className="rounded-2xl bg-[#111827] border border-slate-800/80 p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <div className="flex items-center gap-1.5">
          <FlaskConical className="w-3.5 h-3.5 text-teal-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Lab Highlights
          </h3>
        </div>
        {abnormal.length > 0 ? (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
            {abnormal.length} Abnormal Flags
          </span>
        ) : (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20">
            All Optimal
          </span>
        )}
      </div>

      {/* Biomarker Compact Rows */}
      <div className="space-y-2">
        {displayed.map((lab, idx) => {
          const isLow = lab.status === 'LOW' || lab.status === 'DEFICIENT'
          const isBorderline = lab.status === 'BORDERLINE'
          const isNormal = !isLow && !isBorderline

          return (
            <div
              key={idx}
              className={`p-2.5 rounded-xl flex items-center justify-between gap-3 text-xs transition-colors ${
                isLow
                  ? 'bg-rose-500/5 border border-rose-500/20'
                  : isBorderline
                  ? 'bg-amber-500/5 border border-amber-500/20'
                  : 'bg-slate-900/40 border border-slate-800/50'
              }`}
            >
              <div className="min-w-0">
                <div className="font-medium text-slate-200 truncate">{lab.marker_name}</div>
                <div className="text-[10px] text-slate-400 font-mono">
                  Ref: {lab.reference_range}
                </div>
              </div>

              <div className="flex items-center gap-2.5 shrink-0 text-right">
                <div>
                  <span className="font-bold text-white font-mono">{lab.value}</span>
                  <span className="text-[10px] text-slate-400 ml-1 font-mono">{lab.unit}</span>
                </div>
                <span
                  className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                    isLow
                      ? 'bg-rose-500/15 text-rose-300'
                      : isBorderline
                      ? 'bg-amber-500/15 text-amber-300'
                      : 'bg-teal-500/15 text-teal-300'
                  }`}
                >
                  {lab.status}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Toggle View All */}
      {biomarkers.length > displayed.length && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full pt-1 text-[11px] text-slate-400 hover:text-white flex items-center justify-center gap-1 transition-colors"
        >
          <span>{showAll ? 'Show abnormal only' : `Show all ${biomarkers.length} biomarkers`}</span>
          {showAll ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      )}
    </div>
  )
}
