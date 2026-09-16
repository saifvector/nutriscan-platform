import React from 'react'
import {
  Activity, ArrowUp, ArrowDown, Minus, CheckCircle,
  AlertTriangle, Flame, Info
} from 'lucide-react'

export interface BiomarkerItem {
  marker_name: string
  value: number
  unit: string
  reference_range: string
  status: string
}

interface BiomarkerPanelProps {
  biomarkers: BiomarkerItem[]
}

export default function BiomarkerPanel({ biomarkers }: BiomarkerPanelProps) {
  // Helper to parse reference range string like "30.0 - 100.0 ng/mL" or "12 - 150"
  const parseRange = (refStr: string, currentVal: number) => {
    const nums = refStr.match(/(\d+(\.\d+)?)/g)
    if (nums && nums.length >= 2) {
      const min = parseFloat(nums[0])
      const max = parseFloat(nums[1])
      // Scale min and max for display context
      const visualMin = Math.max(0, min * 0.5)
      const visualMax = max * 1.3
      const pct = visualMax > visualMin ? Math.min(100, Math.max(0, ((currentVal - visualMin) / (visualMax - visualMin)) * 100)) : 50
      const normalStartPct = ((min - visualMin) / (visualMax - visualMin)) * 100
      const normalEndPct = ((max - visualMin) / (visualMax - visualMin)) * 100
      return { min, max, pct, normalStartPct, normalEndPct }
    }
    return { min: 20, max: 80, pct: 50, normalStartPct: 30, normalEndPct: 70 }
  }

  return (
    <div className="rounded-3xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-2xl p-6 md:p-8 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Clinical Biomarker & Laboratory Correlates
            </h3>
            <p className="text-xs text-slate-400">
              Serum and cellular assays with dynamic reference range placement and homeostatic trend indicators.
            </p>
          </div>
        </div>
      </div>

      {/* Grid of Biomarker Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        {biomarkers.map(bio => {
          const isLow = bio.status === 'LOW' || bio.status === 'DEFICIENT'
          const isBorderline = bio.status === 'BORDERLINE'
          const isElevated = bio.status === 'ELEVATED' || bio.status === 'HIGH'
          const isNormal = !isLow && !isBorderline && !isElevated

          const statusBadge = isLow
            ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
            : isBorderline
            ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
            : isElevated
            ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40'
            : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'

          const TrendIcon = isLow ? ArrowDown : isElevated ? ArrowUp : Minus
          const trendColor = isLow ? 'text-rose-400' : isElevated ? 'text-yellow-400' : 'text-emerald-400'

          const { min, max, pct, normalStartPct, normalEndPct } = parseRange(bio.reference_range, bio.value)

          return (
            <div
              key={bio.marker_name}
              className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700/80 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Header: Title & Value */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h4 className="text-sm font-bold text-white leading-tight">
                      {bio.marker_name}
                    </h4>
                    <span className="text-[11px] text-slate-500 font-mono">
                      Ref: {bio.reference_range}
                    </span>
                  </div>

                  {/* Value and Status Chip */}
                  <div className="text-right">
                    <div className="flex items-center justify-end gap-1.5 font-mono">
                      <span className="text-base font-black text-white">
                        {bio.value}
                      </span>
                      <span className="text-xs text-slate-400 font-sans">
                        {bio.unit}
                      </span>
                      <TrendIcon className={`w-4 h-4 ${trendColor}`} />
                    </div>
                    <span className={`inline-block mt-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${statusBadge}`}>
                      {bio.status}
                    </span>
                  </div>
                </div>

                {/* Visual Reference Range Bar */}
                <div className="mt-4 mb-2">
                  <div className="relative w-full h-3 bg-slate-900 rounded-full border border-slate-800 overflow-hidden">
                    {/* Normal Target Range Highlight Zone */}
                    <div
                      className="absolute top-0 bottom-0 bg-emerald-500/25 border-x border-emerald-500/40"
                      style={{
                        left: `${Math.max(5, normalStartPct)}%`,
                        width: `${Math.max(20, normalEndPct - normalStartPct)}%`
                      }}
                    />

                    {/* Patient Position Marker */}
                    <div
                      className={`absolute top-0 bottom-0 w-2.5 rounded-full transform -translate-x-1/2 shadow-md ${
                        isLow ? 'bg-rose-500 shadow-rose-500/50' :
                        isElevated ? 'bg-yellow-400 shadow-yellow-400/50' :
                        isBorderline ? 'bg-amber-400 shadow-amber-400/50' :
                        'bg-emerald-400 shadow-emerald-400/50'
                      }`}
                      style={{ left: `${pct}%` }}
                    />
                  </div>

                  {/* Range Labels */}
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1 px-1">
                    <span>Low (&lt;{min})</span>
                    <span className="text-emerald-400/90 font-medium">Optimal ({min}–{max})</span>
                    <span>High (&gt;{max})</span>
                  </div>
                </div>
              </div>

              {/* Status Clinical Commentary */}
              <div className="mt-3 pt-2.5 border-t border-slate-900 flex items-center justify-between text-[11px] text-slate-400">
                <span>
                  {isLow
                    ? 'Replenishment protocol activated'
                    : isBorderline
                    ? 'Preventive dietary escalation recommended'
                    : isElevated
                    ? 'Monitor for potential upper-bound accumulation'
                    : 'Within target physiological range'}
                </span>
                <span className="text-[10px] font-mono text-cyan-400/90">
                  {Math.round(pct)}th pctl
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
