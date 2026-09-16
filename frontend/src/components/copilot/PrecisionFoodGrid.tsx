import React from 'react'
import {
  Sparkles, DollarSign, Zap, CheckCircle2,
  Utensils, ArrowUpRight, Award, ShieldCheck
} from 'lucide-react'

export interface PrecisionFoodItem {
  title: string
  dosage_or_serving: string
  frequency: string
  biochemical_mechanism: string
  safety_notes?: string
}

interface PrecisionFoodGridProps {
  foods: PrecisionFoodItem[]
}

export default function PrecisionFoodGrid({ foods }: PrecisionFoodGridProps) {
  // Culinary icon & metadata mapping based on title or content
  const getFoodMeta = (title: string) => {
    const t = title.toLowerCase()
    if (t.includes('salmon') || t.includes('fish') || t.includes('mackerel') || t.includes('sardine')) {
      return {
        emoji: '🐟',
        category: 'Fatty Cold-Water Fish',
        bioavailability: '96% Bioavailable',
        cost: '$$ Moderate',
        nutrientTarget: 'Vitamin D3 & Omega-3 EPA/DHA'
      }
    }
    if (t.includes('liver') || t.includes('beef') || t.includes('meat')) {
      return {
        emoji: '🥩',
        category: 'Heme Protein & Organ Matrix',
        bioavailability: '98% Bioavailable (Heme Iron)',
        cost: '$$ Budget-Friendly',
        nutrientTarget: 'Heme Iron + Vitamin B12'
      }
    }
    if (t.includes('spinach') || t.includes('kale') || t.includes('leafy') || t.includes('greens')) {
      return {
        emoji: '🥬',
        category: 'Cruciferous & Leafy Matrix',
        bioavailability: '88% (6x with Vitamin C pairing)',
        cost: '$ Highly Accessible',
        nutrientTarget: 'Folate, Non-Heme Iron & Lutein'
      }
    }
    if (t.includes('egg') || t.includes('yolk')) {
      return {
        emoji: '🥚',
        category: 'Pasture-Raised Poultry',
        bioavailability: '94% Bioavailable',
        cost: '$ Accessible',
        nutrientTarget: 'Vitamin D3, Choline & B12'
      }
    }
    if (t.includes('lentil') || t.includes('bean') || t.includes('legume')) {
      return {
        emoji: '🌱',
        category: 'Sprouted Legume Matrix',
        bioavailability: '84% (Pre-soaked to reduce phytate)',
        cost: '$ Budget-Friendly',
        nutrientTarget: 'Folate (B9), Potassium & Fiber'
      }
    }
    if (t.includes('pumpkin') || t.includes('seed') || t.includes('nut') || t.includes('almond')) {
      return {
        emoji: '🌰',
        category: 'Whole Seed Lipid Matrix',
        bioavailability: '90% Bioavailable',
        cost: '$$ Moderate',
        nutrientTarget: 'Magnesium, Zinc & Vitamin E'
      }
    }
    return {
      emoji: '🥗',
      category: 'Targeted Whole Food Matrix',
      bioavailability: '92% Bioavailable',
      cost: '$$ Accessible',
      nutrientTarget: 'Synergistic Micronutrients'
    }
  }

  return (
    <div className="rounded-3xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-2xl p-6 md:p-8 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Utensils className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              USDA Foundation Precision Food Recommendations
            </h3>
            <p className="text-xs text-slate-400">
              Synergistic, whole-food dietary prescriptions optimized for maximum gut absorption and metabolic bioavailability.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
            Whole Food First Strategy
          </span>
        </div>
      </div>

      {/* Grid of Precision Food Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">
        {foods.map((food, idx) => {
          const meta = getFoodMeta(food.title)
          return (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-emerald-500/40 hover:bg-slate-950/80 transition-all flex flex-col justify-between group shadow-lg shadow-black/20"
            >
              <div>
                {/* Top Badge Row */}
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl p-2 rounded-xl bg-slate-900 border border-slate-800/80 shadow-inner">
                      {meta.emoji}
                    </span>
                    <div>
                      <h4 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
                        {food.title}
                      </h4>
                      <span className="text-xs text-slate-400 font-medium">
                        {meta.category}
                      </span>
                    </div>
                  </div>

                  {/* Cost Tier */}
                  <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                    {meta.cost}
                  </span>
                </div>

                {/* Target & Bioavailability Pills */}
                <div className="flex flex-wrap items-center gap-2 mb-3">
                  <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-lg bg-teal-500/15 text-teal-300 border border-teal-500/30">
                    Target: {meta.nutrientTarget}
                  </span>
                  <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <Zap className="w-3 h-3 text-emerald-400" />
                    {meta.bioavailability}
                  </span>
                </div>

                {/* Serving & Frequency */}
                <div className="text-xs font-semibold text-slate-300 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800/60 mb-3">
                  Serving: {food.dosage_or_serving} • Frequency: {food.frequency}
                </div>

                {/* Scientific & Biochemical Rationale */}
                <div className="text-xs text-slate-400 leading-relaxed pt-2 border-t border-slate-900">
                  <span className="font-semibold text-slate-300 block mb-0.5">
                    Clinical Mechanism:
                  </span>
                  {food.biochemical_mechanism}
                </div>
              </div>

              {food.safety_notes && (
                <div className="mt-3 pt-2 text-[11px] text-amber-300/80 italic">
                  Note: {food.safety_notes}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
