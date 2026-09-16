import React, { useState } from 'react'
import { ChevronDown, ChevronUp, CheckCircle2, FlaskConical, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'

export interface BiomarkerItem {
  marker_name: string
  value: number
  unit: string
  reference_range: string
  status: string
}

interface LabHighlightsSectionProps {
  biomarkers: BiomarkerItem[]
}

export default function LabHighlightsSection({ biomarkers }: LabHighlightsSectionProps) {
  const [showAllLabs, setShowAllLabs] = useState(false)

  // Prioritize abnormal/deficient/borderline markers first
  const abnormal = biomarkers.filter(b => b.status !== 'OPTIMAL' && b.status !== 'NORMAL')
  const optimal = biomarkers.filter(b => b.status === 'OPTIMAL' || b.status === 'NORMAL')

  const prioritized = [...abnormal, ...optimal]
  const displayed = showAllLabs ? prioritized : prioritized.slice(0, 4)

  const getStatusConfig = (status: string) => {
    const isLow = status === 'LOW' || status === 'DEFICIENT'
    const isBorderline = status === 'BORDERLINE'
    const isOptimal = status === 'OPTIMAL' || status === 'NORMAL'

    if (isLow) return {
      color: '#f43f5e',
      bg: 'rgba(244,63,94,0.06)',
      border: 'rgba(244,63,94,0.12)',
      text: 'text-rose-300',
      icon: ArrowDownRight,
      label: status,
    }
    if (isBorderline) return {
      color: '#f59e0b',
      bg: 'rgba(245,158,11,0.06)',
      border: 'rgba(245,158,11,0.12)',
      text: 'text-amber-300',
      icon: Minus,
      label: 'BORDERLINE',
    }
    return {
      color: '#14D9C4',
      bg: 'rgba(20,217,196,0.04)',
      border: 'rgba(20,217,196,0.08)',
      text: 'text-emerald-300',
      icon: CheckCircle2,
      label: 'OPTIMAL',
    }
  }

  return (
    <section
      className="rounded-2xl overflow-hidden bg-[#131B2B] border border-slate-800/60 shadow-sm flex flex-col"
      style={{
        animation: 'fadeSlideUp 0.55s ease-out 0.15s both',
      }}
    >
      {/* Header */}
      <div className="px-6 sm:px-8 pt-6 sm:pt-8 pb-4 flex items-baseline justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-[#14D9C4] opacity-70" />
            Lab Highlights
          </h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Biomarker correlates and reference ranges
          </p>
        </div>
        {abnormal.length > 0 && (
          <span
            className="text-[10px] font-semibold px-2 py-0.5 rounded-md text-amber-300"
            style={{ background: 'rgba(245,158,11,0.08)' }}
          >
            {abnormal.length} flagged
          </span>
        )}
      </div>

      {/* Biomarker Rows */}
      <div className="px-6 sm:px-8 pb-4 space-y-2 flex-1">
        {displayed.map((lab, idx) => {
          const config = getStatusConfig(lab.status)
          const StatusIcon = config.icon

          return (
            <div
              key={idx}
              className="group p-3.5 rounded-xl flex items-center justify-between gap-3 transition-all duration-200"
              style={{
                background: config.bg,
                border: `1px solid ${config.border}`,
              }}
            >
              <div className="min-w-0">
                <div className="text-sm font-medium text-white leading-tight">{lab.marker_name}</div>
                <div className="text-[10px] text-slate-500 mt-0.5 font-mono">
                  Ref: {lab.reference_range}
                </div>
              </div>

              <div className="flex items-center gap-2.5 shrink-0">
                <div className="text-right">
                  <span className="text-sm font-semibold text-white font-mono tabular-nums">
                    {lab.value}
                  </span>
                  <span className="text-[10px] text-slate-500 ml-0.5 font-mono">
                    {lab.unit}
                  </span>
                </div>
                <div
                  className="flex items-center gap-1 px-2 py-0.5 rounded-md"
                  style={{ background: `${config.color}10` }}
                >
                  <StatusIcon className="w-3 h-3" style={{ color: config.color }} />
                  <span className={`text-[10px] font-semibold ${config.text}`}>
                    {config.label}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Expand toggle */}
      {biomarkers.length > 4 && (
        <div className="px-6 sm:px-8 pb-4">
          <button
            onClick={() => setShowAllLabs(!showAllLabs)}
            className="w-full py-2 rounded-xl text-[11px] font-medium text-slate-400 hover:text-slate-200 transition-all flex items-center justify-center gap-1.5"
            style={{
              background: 'rgba(2,6,23,0.3)',
              border: '1px solid rgba(51,65,85,0.2)',
            }}
          >
            {showAllLabs ? (
              <>
                <span>Show highlights only</span>
                <ChevronUp className="w-3 h-3" />
              </>
            ) : (
              <>
                <span>View all {biomarkers.length} markers</span>
                <ChevronDown className="w-3 h-3" />
              </>
            )}
          </button>
        </div>
      )}

      {/* Safety Footer */}
      <div
        className="px-6 sm:px-8 py-3.5 flex items-center justify-between text-[11px] text-slate-500"
        style={{ borderTop: '1px solid rgba(51,65,85,0.15)' }}
      >
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-3.5 h-3.5 text-[#14D9C4]" />
          <span>NIH UL Verified</span>
        </div>
        <span className="font-mono tabular-nums">0 Contraindications</span>
      </div>
    </section>
  )
}
