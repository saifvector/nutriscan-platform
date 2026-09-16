import React from 'react'
import { Activity } from 'lucide-react'

interface RiskOverviewProps {
  compositeScore: number
  deficiencies: Array<{
    nutrient: string
    risk_level: string
    probability: number
  }>
}

export default function RiskOverview({
  compositeScore,
  deficiencies
}: RiskOverviewProps) {
  const criticalCount = deficiencies.filter(d => d.risk_level === 'CRITICAL' || d.probability >= 0.75).length
  const highCount = deficiencies.filter(d => (d.risk_level === 'HIGH' || (d.probability >= 0.55 && d.probability < 0.75))).length
  const modCount = deficiencies.filter(d => d.risk_level === 'MODERATE' || (d.probability >= 0.35 && d.probability < 0.55)).length
  const lowCount = Math.max(0, 11 - (criticalCount + highCount + modCount))

  const total = 11
  const critPct = (criticalCount / total) * 100
  const highPct = (highCount / total) * 100
  const modPct = (modCount / total) * 100
  const lowPct = (lowCount / total) * 100

  return (
    <div className="rounded-2xl bg-[#111827] border border-slate-800/80 p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <div className="flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-teal-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Risk Distribution
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">11 Evaluated</span>
      </div>

      {/* Concise Stacked Distribution Bar */}
      <div className="space-y-1.5">
        <div className="h-2.5 w-full rounded-full bg-slate-800 overflow-hidden flex">
          {critPct > 0 && <div style={{ width: `${critPct}%` }} className="bg-rose-500" title={`Critical: ${criticalCount}`} />}
          {highPct > 0 && <div style={{ width: `${highPct}%` }} className="bg-rose-400" title={`High: ${highCount}`} />}
          {modPct > 0 && <div style={{ width: `${modPct}%` }} className="bg-amber-400" title={`Moderate: ${modCount}`} />}
          {lowPct > 0 && <div style={{ width: `${lowPct}%` }} className="bg-teal-500" title={`Optimal: ${lowCount}`} />}
        </div>

        {/* Legend / Counter Row */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            <span>High: <strong className="text-rose-300">{criticalCount + highCount}</strong></span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span>Mod: <strong className="text-amber-300">{modCount}</strong></span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-500" />
            <span>Opt: <strong className="text-teal-300">{lowCount}</strong></span>
          </div>
        </div>
      </div>

      {/* Summary Stat */}
      <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
        <span className="text-slate-400">Composite Vulnerability</span>
        <span className="font-bold text-white font-mono">{compositeScore}/100</span>
      </div>
    </div>
  )
}
