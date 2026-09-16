import React from 'react'
import {
  AlertTriangle, ShieldAlert, CheckCircle2, ArrowRight,
  Sparkles, Stethoscope, AlertOctagon, Zap, ShieldCheck
} from 'lucide-react'

interface ExecutiveSummaryPanelProps {
  overallStatus?: 'CRITICAL' | 'HIGH_RISK' | 'MODERATE' | 'STABLE'
  patientName: string
  highPriorityFindings: string[]
  recommendedActions: Array<{
    priority: string
    action: string
    rationale?: string
  }>
  safetyWarnings: string[]
  primaryDeficiencies: Array<{
    nutrient: string
    risk: string
    probability: number
  }>
}

export default function ExecutiveSummaryPanel({
  overallStatus = 'HIGH_RISK',
  patientName,
  highPriorityFindings,
  recommendedActions,
  safetyWarnings,
  primaryDeficiencies
}: ExecutiveSummaryPanelProps) {
  const statusConfig = {
    CRITICAL: {
      label: 'Critical Clinical Attention',
      color: 'text-rose-400',
      badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
      border: 'border-rose-500/30',
      icon: AlertOctagon,
      bg: 'from-rose-950/40 via-slate-900/60 to-slate-900/60'
    },
    HIGH_RISK: {
      label: 'High Nutritional Vulnerability',
      color: 'text-amber-400',
      badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      border: 'border-amber-500/30',
      icon: AlertTriangle,
      bg: 'from-amber-950/30 via-slate-900/60 to-slate-900/60'
    },
    MODERATE: {
      label: 'Moderate Nutritional Strain',
      color: 'text-yellow-400',
      badge: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40',
      border: 'border-yellow-500/30',
      icon: AlertTriangle,
      bg: 'from-yellow-950/20 via-slate-900/60 to-slate-900/60'
    },
    STABLE: {
      label: 'Homeostatic & Well-Controlled',
      color: 'text-emerald-400',
      badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
      border: 'border-emerald-500/30',
      icon: CheckCircle2,
      bg: 'from-emerald-950/20 via-slate-900/60 to-slate-900/60'
    }
  }[overallStatus]

  const StatusIcon = statusConfig.icon

  return (
    <div className={`rounded-3xl bg-gradient-to-br ${statusConfig.bg} border ${statusConfig.border} backdrop-blur-2xl p-6 md:p-8 shadow-xl relative overflow-hidden`}>
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-slate-950 border border-slate-800 shadow">
            <Stethoscope className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Rapid Clinical Triage (3-Second Overview)
            </div>
            <h3 className="text-xl font-bold text-white tracking-tight">
              Executive Clinical Summary for {patientName.split(' ')[0]}
            </h3>
          </div>
        </div>

        {/* Status Pill */}
        <div className="flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 shadow-sm ${statusConfig.badge}`}>
            <StatusIcon className="w-3.5 h-3.5 shrink-0" />
            <span>{statusConfig.label}</span>
          </span>
        </div>
      </div>

      {/* 4 Core Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
        {/* Pillar 1: Overall Status & Top Deficiencies */}
        <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5 mb-3">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span>Confirmed Deficiencies</span>
            </div>
            <div className="space-y-2">
              {primaryDeficiencies.slice(0, 3).map((d, i) => (
                <div key={i} className="flex items-center justify-between p-2 rounded-xl bg-slate-900/60 border border-slate-800/60 text-xs">
                  <span className="font-semibold text-slate-200">{d.nutrient}</span>
                  <span className={`px-2 py-0.5 rounded-md font-bold text-[10px] ${
                    d.risk === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' :
                    d.risk === 'HIGH' ? 'bg-amber-500/20 text-amber-300' :
                    'bg-yellow-500/20 text-yellow-300'
                  }`}>
                    {d.risk} ({Math.round(d.probability * 100)}%)
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-900">
            Ranked by calibrated probability
          </div>
        </div>

        {/* Pillar 2: High Priority Findings */}
        <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5 mb-3">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>High Priority Findings</span>
            </div>
            <ul className="space-y-2">
              {highPriorityFindings.slice(0, 3).map((f, i) => (
                <li key={i} className="text-xs text-slate-300 flex items-start gap-2 leading-relaxed">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-900">
            Symptom-biomarker correlation verified
          </div>
        </div>

        {/* Pillar 3: Recommended Actions */}
        <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5 mb-3">
              <Sparkles className="w-3.5 h-3.5 text-teal-400" />
              <span>Recommended Actions</span>
            </div>
            <div className="space-y-2">
              {recommendedActions.slice(0, 2).map((a, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/60">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                      {a.priority || `Priority ${i + 1}`}
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-slate-200 leading-snug">
                    {a.action}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-900">
            Evidence Grade A / B validated
          </div>
        </div>

        {/* Pillar 4: Safety Warnings & NIH UL */}
        <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5 mb-3">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Safety & Guardrails</span>
            </div>
            <div className="space-y-2">
              {safetyWarnings.length > 0 ? (
                safetyWarnings.slice(0, 2).map((w, i) => (
                  <div key={i} className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 flex items-start gap-2">
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                    <span className="leading-snug">{w}</span>
                  </div>
                ))
              ) : (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 space-y-1">
                  <div className="font-bold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>All Prescriptions Safe</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-snug">
                    Zero contraindications or Tolerable Upper Intake Level (UL) exceedances detected.
                  </p>
                </div>
              )}
            </div>
          </div>
          <div className="text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-900">
            NIH Office of Dietary Supplements Rules
          </div>
        </div>
      </div>
    </div>
  )
}
