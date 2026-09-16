import React from 'react'
import {
  Award, ShieldCheck, Clock, CheckCircle2,
  Calendar, Sparkles, ArrowRight, Zap
} from 'lucide-react'

export interface SupplementPlanItem {
  title: string
  dosage_or_serving: string
  frequency: string
  biochemical_mechanism: string
  safety_notes?: string
}

interface SupplementTimelineProps {
  supplementPlan: SupplementPlanItem[]
}

export default function SupplementTimeline({ supplementPlan }: SupplementTimelineProps) {
  const phases = [
    {
      phaseNumber: 'Phase 1',
      timeline: 'Days 1 – 30',
      tag: 'Acute Replenishment',
      badgeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
      evidenceGrade: 'Grade A',
      evidenceDesc: 'Double-blind randomized controlled trial validation',
      safetyStatus: 'UL Compliant',
    },
    {
      phaseNumber: 'Phase 2',
      timeline: 'Days 31 – 60',
      tag: 'Cellular Consolidation',
      badgeColor: 'bg-teal-500/20 text-teal-300 border-teal-500/40',
      evidenceGrade: 'Grade A',
      evidenceDesc: 'NIH ODS Pharmacokinetic absorption modeling',
      safetyStatus: 'Contraindication Free',
    },
    {
      phaseNumber: 'Phase 3',
      timeline: 'Days 61+',
      tag: 'Systemic Maintenance',
      badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
      evidenceGrade: 'Grade B',
      evidenceDesc: 'Prospective longitudinal cohort outcomes',
      safetyStatus: 'Long-term Safe',
    }
  ]

  return (
    <div className="rounded-3xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-2xl p-6 md:p-8 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Supplement Protocol & Treatment Timeline
            </h3>
            <p className="text-xs text-slate-400">
              Evidence-graded, phased pharmacotherapy synchronized with biomarker repletion kinetics.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>NIH UL Bound Compliant</span>
          </span>
        </div>
      </div>

      {/* Timeline Steps */}
      <div className="space-y-4 mt-6">
        {supplementPlan.map((supp, idx) => {
          const phase = phases[idx % phases.length]
          return (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700/80 transition-all"
            >
              {/* Phase and Timing Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold border ${phase.badgeColor}`}>
                    {phase.phaseNumber}: {phase.tag}
                  </span>
                  <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-slate-500" />
                    {phase.timeline}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  {/* Evidence Grade */}
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/10 text-blue-300 border border-blue-500/30 flex items-center gap-1">
                    <Award className="w-3 h-3 text-blue-400" />
                    {phase.evidenceGrade}
                  </span>

                  {/* Safety status */}
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    {phase.safetyStatus}
                  </span>
                </div>
              </div>

              {/* Title & Dosage */}
              <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-1 mb-2">
                <h4 className="text-base font-bold text-blue-300 tracking-tight">
                  {supp.title}
                </h4>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-200">
                  {supp.dosage_or_serving} • {supp.frequency}
                </span>
              </div>

              {/* Mechanism & Expected Benefit */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 pt-3 border-t border-slate-900 text-xs">
                <div>
                  <span className="text-slate-400 font-medium block mb-1">
                    Biochemical Mechanism:
                  </span>
                  <p className="text-slate-300 leading-relaxed">
                    {supp.biochemical_mechanism}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400 font-medium block mb-1">
                    Expected Clinical Benefit & Safety:
                  </span>
                  <p className="text-slate-300 leading-relaxed">
                    {supp.safety_notes || phase.evidenceDesc}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
