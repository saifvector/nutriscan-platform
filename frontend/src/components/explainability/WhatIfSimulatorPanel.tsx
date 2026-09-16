import React, { useState } from 'react'
import { Sliders, Play, RefreshCw, ArrowRight, CheckCircle2, AlertTriangle, Clock, Activity, ShieldCheck, Sparkles } from 'lucide-react'
import api from '../../lib/api'

export interface TargetSimulationComparison {
  target: string
  target_name: string
  baseline_probability: number
  simulated_probability: number
  probability_delta: number
  baseline_tier: string
  simulated_tier: string
  tier_improved: boolean
}

export interface WhatIfSimulationResponse {
  baseline_risk_score: float
  simulated_risk_score: float
  risk_score_delta: float
  deficiencies_resolved_count: number
  target_comparisons: TargetSimulationComparison[]
  projected_timeline: string
  summary_narrative: string
}

type float = number

interface WhatIfSimulatorPanelProps {
  initialTarget?: string
  onSimulationComplete?: (result: WhatIfSimulationResponse) => void
}

export const WhatIfSimulatorPanel: React.FC<WhatIfSimulatorPanelProps> = ({
  initialTarget = 'target_iron_deficiency',
  onSimulationComplete
}) => {
  const [selectedTarget, setSelectedTarget] = useState<string>(initialTarget)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [simulationResult, setSimulationResult] = useState<WhatIfSimulationResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Simulation Sliders / Controls
  const [dietaryIron, setDietaryIron] = useState<number>(18.0) // mg
  const [dietaryVitD, setDietaryVitD] = useState<number>(15.0) // mcg
  const [dietaryVitC, setDietaryVitC] = useState<number>(75.0) // mg
  const [dietaryMagnesium, setDietaryMagnesium] = useState<number>(320.0) // mg

  const [supplements, setSupplements] = useState<{ [key: string]: boolean }>({
    'Iron Bisglycinate (25mg)': true,
    'Vitamin D3 (2000 IU)': false,
    'Magnesium Glycinate (200mg)': false,
    'Vitamin C (Ascorbic Acid 250mg)': false,
    'Folate (Methylfolate 400mcg)': false
  })

  const [sunlightMinutes, setSunlightMinutes] = useState<number>(25)
  const [sleepHours, setSleepHours] = useState<number>(7.5)

  const targets = [
    { id: 'target_iron_deficiency', name: 'Iron Deficiency' },
    { id: 'target_iron_deficiency_anemia', name: 'Iron Deficiency Anemia' },
    { id: 'target_vitamin_d_deficiency', name: 'Vitamin D Deficiency' },
    { id: 'target_vitamin_d_insufficiency', name: 'Vitamin D Insufficiency' },
    { id: 'target_folate_deficiency', name: 'Folate Deficiency' },
    { id: 'target_magnesium_deficiency', name: 'Magnesium Deficiency' },
    { id: 'target_potassium_deficiency', name: 'Potassium Deficiency' },
    { id: 'target_calcium_deficiency', name: 'Calcium Deficiency' },
    { id: 'target_selenium_deficiency', name: 'Selenium Deficiency' }
  ]

  const toggleSupplement = (name: string) => {
    setSupplements(prev => ({ ...prev, [name]: !prev[name] }))
  }

  const handleRunSimulation = async () => {
    setIsLoading(true)
    setErrorMessage(null)

    const supplementMap: { [key: string]: number } = {}
    if (supplements['Iron Bisglycinate (25mg)']) supplementMap['supp_iron_mg'] = 25.0
    if (supplements['Vitamin D3 (2000 IU)']) supplementMap['supp_vitamin_d_mcg'] = 50.0
    if (supplements['Magnesium Glycinate (200mg)']) supplementMap['supp_magnesium_mg'] = 200.0
    if (supplements['Vitamin C (Ascorbic Acid 250mg)']) supplementMap['supp_vitamin_c_mg'] = 250.0
    if (supplements['Folate (Methylfolate 400mcg)']) supplementMap['supp_folate_mcg'] = 400.0

    const payload = {
      base_assessment: {
        age: 32,
        gender: "FEMALE",
        dietary_habits: {
          dietary_pattern: "VEGAN",
          daily_fruit_vegetable_servings: 2
        },
        lifestyle_factors: {
          activity_level: "LIGHTLY_ACTIVE",
          sunlight_exposure_min_per_day: 10,
          sleep_hours_per_night: 6.0
        },
        symptoms: {
          fatigue: 7,
          cold_sensitivity: 5
        }
      },
      dietary_modifications: {
        diet_iron_mg: dietaryIron,
        diet_vitamin_d_mcg: dietaryVitD,
        diet_vitamin_c_mg: dietaryVitC,
        diet_magnesium_mg: dietaryMagnesium
      },
      supplement_additions: supplementMap,
      lifestyle_modifications: {
        sunlight_exposure_min_per_day: sunlightMinutes,
        sleep_hours_per_night: sleepHours
      }
    }

    try {
      const response = await api.post('/explainability/what-if-simulation', payload)
      setSimulationResult(response.data)
      if (onSimulationComplete) {
        onSimulationComplete(response.data)
      }
    } catch (err: any) {
      const d = err?.response?.data?.detail
      const msg = typeof d === 'string' ? d : Array.isArray(d) ? d.map((x: any) => x.msg || JSON.stringify(x)).join(', ') : 'Simulation failed.'
      setErrorMessage(msg)
    } finally {
      setIsLoading(false)
    }
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'HIGH':
        return 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30'
      case 'MODERATE':
        return 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30'
      case 'LOW':
      default:
        return 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
    }
  }

  // Find target comparison for the currently selected target
  const activeComparison = simulationResult?.target_comparisons?.find(
    c => c.target === selectedTarget || c.target_name.toLowerCase().includes(selectedTarget.replace('target_', '').replace(/_/g, ' ').toLowerCase())
  ) || simulationResult?.target_comparisons?.[0]

  return (
    <div className="bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-teal-600 dark:text-teal-400" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              What-If Prospective Intervention Simulator
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Recompute 105 clinical biomarkers & calibrated champion model predictions under hypothetical dietary and supplement modifications.
          </p>
        </div>

        {/* Target Focus Dropdown */}
        <div className="min-w-[220px]">
          <select
            value={selectedTarget}
            onChange={e => setSelectedTarget(e.target.value)}
            className="w-full px-3 py-2 text-xs md:text-sm rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-teal-500 cursor-pointer"
          >
            {targets.map(t => (
              <option key={t.id} value={t.id}>
                Focus: {t.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Simulation Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          {/* Dietary Intake Sliders */}
          <div className="p-4 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60 space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Dietary Intake Adjustments
            </h4>

            {/* Dietary Iron */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium text-slate-700 dark:text-slate-300">Dietary Iron</span>
                <span className="font-bold text-teal-600 dark:text-teal-400">{dietaryIron} mg/day</span>
              </div>
              <input
                type="range"
                min="4.0"
                max="30.0"
                step="1.0"
                value={dietaryIron}
                onChange={e => setDietaryIron(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
                <span>4 mg (Low)</span>
                <span>RDA: 18 mg</span>
                <span>30 mg (High)</span>
              </div>
            </div>

            {/* Vitamin D */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium text-slate-700 dark:text-slate-300">Dietary Vitamin D</span>
                <span className="font-bold text-teal-600 dark:text-teal-400">{dietaryVitD} mcg/day</span>
              </div>
              <input
                type="range"
                min="2.0"
                max="30.0"
                step="1.0"
                value={dietaryVitD}
                onChange={e => setDietaryVitD(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
            </div>

            {/* Vitamin C */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium text-slate-700 dark:text-slate-300">Vitamin C (Synergy Booster)</span>
                <span className="font-bold text-teal-600 dark:text-teal-400">{dietaryVitC} mg/day</span>
              </div>
              <input
                type="range"
                min="20"
                max="200"
                step="5"
                value={dietaryVitC}
                onChange={e => setDietaryVitC(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
            </div>

            {/* Magnesium */}
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium text-slate-700 dark:text-slate-300">Dietary Magnesium</span>
                <span className="font-bold text-teal-600 dark:text-teal-400">{dietaryMagnesium} mg/day</span>
              </div>
              <input
                type="range"
                min="100"
                max="500"
                step="10"
                value={dietaryMagnesium}
                onChange={e => setDietaryMagnesium(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
            </div>
          </div>

          {/* Supplement Regimen Toggles */}
          <div className="p-4 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60 space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
              Prospective Supplement Additions
            </h4>
            {Object.keys(supplements).map(name => (
              <label
                key={name}
                className="flex items-center justify-between p-2 rounded-lg bg-white/80 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800/60 text-xs cursor-pointer hover:border-teal-500/40 transition-all"
              >
                <span className="font-medium text-slate-800 dark:text-slate-200">{name}</span>
                <input
                  type="checkbox"
                  checked={supplements[name]}
                  onChange={() => toggleSupplement(name)}
                  className="rounded text-teal-600 focus:ring-teal-500 w-4 h-4 cursor-pointer"
                />
              </label>
            ))}
          </div>

          {/* Lifestyle Modifiers */}
          <div className="p-4 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Lifestyle & Sunlight Factors
            </h4>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium text-slate-700 dark:text-slate-300">Daily Sunlight Exposure</span>
                <span className="font-bold text-teal-600 dark:text-teal-400">{sunlightMinutes} mins/day</span>
              </div>
              <input
                type="range"
                min="0"
                max="60"
                step="5"
                value={sunlightMinutes}
                onChange={e => setSunlightMinutes(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium text-slate-700 dark:text-slate-300">Nightly Sleep Duration</span>
                <span className="font-bold text-teal-600 dark:text-teal-400">{sleepHours} hrs/night</span>
              </div>
              <input
                type="range"
                min="4.0"
                max="10.0"
                step="0.5"
                value={sleepHours}
                onChange={e => setSleepHours(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
            </div>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={isLoading}
            className="w-full py-3 px-4 rounded-xl font-semibold text-sm text-white bg-teal-600 hover:bg-teal-700 active:bg-teal-800 transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Executing Calibration Pipeline...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Run Prospective Simulation
              </>
            )}
          </button>

          {errorMessage && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Right Side: Simulation Results & Trajectory (7 cols) */}
        <div className="lg:col-span-7">
          {!simulationResult ? (
            <div className="h-full min-h-[380px] flex flex-col items-center justify-center p-8 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 text-center text-slate-400">
              <Sparkles className="w-10 h-10 text-teal-500/40 mb-3" />
              <p className="font-medium text-sm text-slate-600 dark:text-slate-300">
                Ready to simulate intervention trajectory
              </p>
              <p className="text-xs text-slate-400 max-w-sm mt-1">
                Adjust dietary, supplement, or lifestyle parameters on the left and click "Run Prospective Simulation" to see calibrated risk mitigation across all 9 champion models.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Overall Risk Score Delta Banner */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Baseline Overall Score
                  </span>
                  <div className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                    {simulationResult.baseline_risk_score.toFixed(1)}
                  </div>
                  <span className="text-[10px] text-slate-500 block">Out of 100 max risk</span>
                </div>

                <div className="p-4 rounded-xl bg-teal-50/50 dark:bg-teal-950/20 border border-teal-500/30">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-teal-600 dark:text-teal-400">
                    Projected Post-Intervention
                  </span>
                  <div className="text-2xl font-black text-teal-700 dark:text-teal-300 mt-1">
                    {simulationResult.simulated_risk_score.toFixed(1)}
                  </div>
                  <span className="text-[10px] text-teal-600 dark:text-teal-400 font-medium">
                    {simulationResult.risk_score_delta < 0 ? `${simulationResult.risk_score_delta.toFixed(1)} score reduction` : 'No score change'}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-500/30">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                    Deficiencies Resolved
                  </span>
                  <div className="text-2xl font-black text-emerald-700 dark:text-emerald-300 mt-1">
                    {simulationResult.deficiencies_resolved_count}
                  </div>
                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">
                    Tiers reduced to LOW
                  </span>
                </div>
              </div>

              {/* Focus Target Card */}
              {activeComparison && (
                <div className="p-4 rounded-xl bg-white dark:bg-slate-800 border border-teal-500/40 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">
                      Focus Target: {activeComparison.target_name}
                    </span>
                    {activeComparison.tier_improved && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" /> Tier Improved!
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-1">
                    <div>
                      <span className="text-[11px] text-slate-400 block">Baseline Probability:</span>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-lg font-black text-slate-800 dark:text-slate-200">
                          {Math.round(activeComparison.baseline_probability * 100)}%
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getTierColor(activeComparison.baseline_tier)}`}>
                          {activeComparison.baseline_tier}
                        </span>
                      </div>
                    </div>

                    <div>
                      <span className="text-[11px] text-teal-600 dark:text-teal-400 font-medium block">Simulated Outcome:</span>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-lg font-black text-teal-700 dark:text-teal-300">
                          {Math.round(activeComparison.simulated_probability * 100)}%
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getTierColor(activeComparison.simulated_tier)}`}>
                          {activeComparison.simulated_tier}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Recovery Timeline */}
              <div className="p-4 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-500/20 flex items-start gap-3">
                <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <h5 className="text-xs font-bold text-blue-900 dark:text-blue-300 uppercase tracking-wide">
                    Projected Biological Timeline
                  </h5>
                  <p className="text-xs text-blue-800 dark:text-blue-200 mt-1 leading-relaxed">
                    {simulationResult.projected_timeline}
                  </p>
                </div>
              </div>

              {/* Summary Narrative */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-700/80">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-4 h-4 text-teal-600 dark:text-teal-400" />
                  <h5 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wide">
                    Clinical Synthesis of Simulated Trajectory
                  </h5>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  {simulationResult.summary_narrative}
                </p>
              </div>

              {/* All 9 Targets Breakdown Table */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-700/80">
                <h5 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2.5">
                  Multi-Target Trajectory Breakdown (9 Models)
                </h5>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-400 text-[11px]">
                        <th className="pb-2 font-medium">Target</th>
                        <th className="pb-2 font-medium text-center">Baseline</th>
                        <th className="pb-2 font-medium text-center">Simulated</th>
                        <th className="pb-2 font-medium text-right">Delta</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {simulationResult.target_comparisons.map(c => (
                        <tr key={c.target} className="hover:bg-slate-100/50 dark:hover:bg-slate-800/50">
                          <td className="py-1.5 font-medium text-slate-800 dark:text-slate-200">{c.target_name}</td>
                          <td className="py-1.5 text-center text-slate-600 dark:text-slate-400">{Math.round(c.baseline_probability * 100)}%</td>
                          <td className="py-1.5 text-center font-bold text-teal-600 dark:text-teal-400">{Math.round(c.simulated_probability * 100)}%</td>
                          <td className="py-1.5 text-right font-mono text-[11px]">
                            {c.probability_delta < 0 ? (
                              <span className="text-emerald-600 dark:text-emerald-400">{(c.probability_delta * 100).toFixed(1)}%</span>
                            ) : (
                              <span className="text-slate-400">0.0%</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
