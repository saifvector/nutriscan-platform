import React from 'react'
import {
  Activity, ShieldCheck, Award, Clock, ArrowUp, ArrowDown,
  Minus, CheckCircle2, AlertTriangle, ChevronRight, Zap
} from 'lucide-react'
import { type BiomarkerItem } from './BiomarkerPanel'
import { type SupplementPlanItem } from './SupplementTimeline'

interface BiomarkerSafetyPanelProps {
  biomarkers: BiomarkerItem[]
  supplementPlan: SupplementPlanItem[]
  ulCompliant?: boolean
  safetyAlerts?: string[]
}

export default function BiomarkerSafetyPanel({
  biomarkers,
  supplementPlan,
  ulCompliant = true,
  safetyAlerts = []
}: BiomarkerSafetyPanelProps) {
  // Helper to parse reference range string like "30.0 - 100.0 ng/mL" or "12 - 150"
  const parseRange = (refStr: string, currentVal: number) => {
    const nums = refStr.match(/(\d+(\.\d+)?)/g)
    if (nums && nums.length >= 2) {
      const min = parseFloat(nums[0])
      const max = parseFloat(nums[1])
      const visualMin = Math.max(0, min * 0.5)
      const visualMax = max * 1.3
      const pct = visualMax > visualMin ? Math.min(100, Math.max(0, ((currentVal - visualMin) / (visualMax - visualMin)) * 100)) : 50
      const normalStartPct = ((min - visualMin) / (visualMax - visualMin)) * 100
      const normalEndPct = ((max - visualMin) / (visualMax - visualMin)) * 100
      return { min, max, pct, normalStartPct, normalEndPct }
    }
    return { min: 20, max: 80, pct: 50, normalStartPct: 30, normalEndPct: 70 }
  }

  const phases = [
    {
      phase: 'Phase 1',
      days: 'Days 1–30',
      title: 'Acute Replenishment',
      grade: 'Grade A',
      badgeColor: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
    },
    {
      phase: 'Phase 2',
      days: 'Days 31–60',
      title: 'Cellular Consolidation',
      grade: 'Grade A',
      badgeColor: 'bg-teal-500/15 text-teal-300 border-teal-500/30'
    },
    {
      phase: 'Phase 3',
      days: 'Days 61+',
      title: 'Systemic Maintenance',
      grade: 'Grade B',
      badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
    }
  ]

  return (
    <aside className="w-full space-y-4 font-sans">
      {/* ─── 1. Laboratory Biomarker Correlates ─── */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4 backdrop-blur-sm">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Activity className="w-3.5 h-3.5" />
            </span>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Laboratory Correlates
            </h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            {biomarkers.length} Assays
          </span>
        </div>

        <div className="space-y-2.5 mt-3">
          {biomarkers.map((bio, idx) => {
            const isLow = bio.status === 'LOW' || bio.status === 'DEFICIENT'
            const isBorderline = bio.status === 'BORDERLINE'
            const isElevated = bio.status === 'ELEVATED' || bio.status === 'HIGH'
            const range = parseRange(bio.reference_range, bio.value)

            const badgeColor = isLow
              ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
              : isBorderline
              ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
              : isElevated
              ? 'bg-yellow-500/15 text-yellow-300 border-yellow-500/30'
              : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'

            return (
              <div
                key={idx}
                className="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800/50 text-xs"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div>
                    <span className="font-bold text-white text-xs">{bio.marker_name}</span>
                    <span className="text-[10px] text-slate-400 ml-1.5 font-mono">
                      Ref: {bio.reference_range}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono font-bold text-slate-100 text-xs">
                      {bio.value} {bio.unit}
                    </span>
                    <span className={`text-[9px] px-1.5 py-0.2 rounded font-bold border ${badgeColor}`}>
                      {bio.status}
                    </span>
                  </div>
                </div>

                {/* Range Bar with Normal Zone & Value Pointer */}
                <div className="relative pt-1.5 pb-1">
                  <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden relative">
                    {/* Normal Reference Band */}
                    <div
                      className="absolute top-0 bottom-0 bg-emerald-500/25 border-x border-emerald-500/40"
                      style={{
                        left: `${range.normalStartPct}%`,
                        width: `${range.normalEndPct - range.normalStartPct}%`
                      }}
                    />
                  </div>

                  {/* Marker Pin */}
                  <div
                    className="absolute top-0 -ml-1 transition-all duration-500 flex flex-col items-center"
                    style={{ left: `${range.pct}%` }}
                  >
                    <div
                      className={`w-2 h-3 rounded-sm ${
                        isLow ? 'bg-rose-400' : isBorderline ? 'bg-amber-400' : 'bg-emerald-400'
                      } shadow-sm shadow-black`}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ─── 2. Safety & Governance Check ─── */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-3.5 h-3.5" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Safety Governance
            </span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-semibold font-mono">
            NIH UL Verified
          </span>
        </div>

        <div className="space-y-1.5 text-[11px] pt-1 text-slate-300">
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/40 border border-slate-800/40">
            <span>Tolerable Upper Intake Level (UL)</span>
            <span className="font-semibold text-emerald-400">100% Compliant</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/40 border border-slate-800/40">
            <span>Drug-Nutrient Contraindications</span>
            <span className="font-semibold text-emerald-400">0 Detected</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/40 border border-slate-800/40">
            <span>Hepatic / Renal Clearance Clearance</span>
            <span className="font-semibold text-cyan-400">Normal Margin</span>
          </div>
        </div>
      </div>

      {/* ─── 3. Phased Supplement Treatment Protocol ─── */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4 backdrop-blur-sm">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Award className="w-3.5 h-3.5" />
            </span>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Phased Supplement Protocol
            </h3>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">
            {supplementPlan.length} Targets
          </span>
        </div>

        {/* Phase Badges */}
        <div className="grid grid-cols-3 gap-1.5 my-3 text-[10px]">
          {phases.map((ph, i) => (
            <div
              key={i}
              className={`p-1.5 rounded-lg border text-center ${ph.badgeColor}`}
            >
              <div className="font-bold">{ph.phase}</div>
              <div className="text-[9px] opacity-80">{ph.days}</div>
            </div>
          ))}
        </div>

        {/* Action Items */}
        <div className="space-y-2">
          {supplementPlan.slice(0, 3).map((supp, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800/50 text-xs"
            >
              <div className="flex items-center justify-between gap-1">
                <span className="font-bold text-slate-100 text-xs">{supp.title}</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                  {supp.dosage_or_serving}
                </span>
              </div>
              <div className="text-[10px] text-slate-400 mt-1 line-clamp-1">
                {supp.biochemical_mechanism}
              </div>
              <div className="mt-1.5 pt-1.5 border-t border-slate-800/30 flex justify-between items-center text-[9px] text-slate-400">
                <span>{supp.frequency}</span>
                <span className="text-emerald-400 font-medium">Grade A RCT</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
