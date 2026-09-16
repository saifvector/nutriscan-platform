import React, { useState } from 'react'
import { Utensils, Pill, Activity, CheckCircle2, ChevronRight } from 'lucide-react'

export interface PrecisionFood {
  title: string
  dosage_or_serving: string
  frequency: string
  biochemical_mechanism: string
}

export interface SupplementItem {
  title: string
  dosage_or_serving: string
  frequency: string
  biochemical_mechanism: string
}

export interface BiomarkerTarget {
  biomarker: string
  baseline: string
  target: string
  evaluation_window: string
}

interface NutritionPlanProps {
  foods: PrecisionFood[]
  supplements: SupplementItem[]
  biomarkerTargets: BiomarkerTarget[]
  followUpRecommendations?: string[]
}

export default function NutritionPlan({
  foods,
  supplements,
  biomarkerTargets,
  followUpRecommendations = []
}: NutritionPlanProps) {
  const [activeSubTab, setActiveSubTab] = useState<'foods' | 'supplements' | 'monitoring'>('foods')

  return (
    <section className="space-y-4">
      {/* Header & Sub-Tab Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-1">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Targeted Nutrition & Repletion Plan
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Prescribed therapeutic foods, micronutrient protocols, and biomarker milestones
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-[#111827] border border-slate-800/80 self-start sm:self-auto">
          {[
            { id: 'foods', label: 'Precision Foods', icon: Utensils, count: foods.length },
            { id: 'supplements', label: 'Supplements', icon: Pill, count: supplements.length },
            { id: 'monitoring', label: 'Monitoring', icon: Activity, count: biomarkerTargets.length },
          ].map(tab => {
            const Icon = tab.icon
            const isActive = activeSubTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-teal-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
                <span className={`text-[10px] font-mono px-1 rounded ${
                  isActive ? 'bg-teal-700 text-teal-100' : 'bg-slate-800 text-slate-400'
                }`}>
                  {tab.count}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Panels */}
      {/* 1. Precision Foods */}
      {activeSubTab === 'foods' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {foods.slice(0, 6).map((food, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl bg-[#111827] border border-slate-800/80 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-semibold text-white leading-snug">
                    {food.title}
                  </h4>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 shrink-0">
                    {food.frequency}
                  </span>
                </div>
                <div className="text-xs font-mono text-slate-400 mt-1">
                  Serving: {food.dosage_or_serving}
                </div>
                <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                  {food.biochemical_mechanism}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 2. Supplements */}
      {activeSubTab === 'supplements' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {supplements.slice(0, 6).map((supp, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl bg-[#111827] border border-slate-800/80 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-sm font-semibold text-white leading-snug">
                    {supp.title}
                  </h4>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 shrink-0">
                    {supp.frequency}
                  </span>
                </div>
                <div className="text-xs font-mono text-slate-400 mt-1">
                  Dosage: {supp.dosage_or_serving}
                </div>
                <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                  {supp.biochemical_mechanism}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 3. Monitoring Plan & Targets */}
      {activeSubTab === 'monitoring' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Biomarker Targets */}
          <div className="rounded-2xl bg-[#111827] border border-slate-800/80 p-5 space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-teal-400 flex items-center gap-2">
              <Activity className="w-3.5 h-3.5" />
              <span>Quantitative Biomarker Targets</span>
            </h4>
            <div className="space-y-2">
              {biomarkerTargets.map((bt, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-center justify-between text-xs"
                >
                  <div>
                    <div className="font-semibold text-white">{bt.biomarker}</div>
                    <div className="text-[11px] text-slate-400">Baseline: {bt.baseline} · Window: {bt.evaluation_window}</div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold font-mono text-teal-400 block">{bt.target}</span>
                    <span className="text-[10px] text-slate-400">Target Range</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Follow-Up Recommendations */}
          <div className="rounded-2xl bg-[#111827] border border-slate-800/80 p-5 space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
              <span>Clinical Follow-Up Directives</span>
            </h4>
            <div className="space-y-2">
              {followUpRecommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-start gap-2.5 text-xs text-slate-300"
                >
                  <ChevronRight className="w-4 h-4 text-teal-400 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
