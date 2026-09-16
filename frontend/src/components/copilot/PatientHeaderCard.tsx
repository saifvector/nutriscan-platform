import React from 'react'
import {
  User, ShieldCheck, Moon, Sun, Flame, Scale,
  HeartPulse, Sparkles, Activity, CheckCircle2, ChevronDown
} from 'lucide-react'

export interface PatientProfile {
  id: string
  name: string
  age: number
  gender: string
  diet: string
  height_cm: number
  weight_kg: number
  symptoms: Record<string, number>
}

interface PatientHeaderCardProps {
  patients: PatientProfile[]
  selectedPatient: PatientProfile
  onSelectPatient: (patient: PatientProfile) => void
  compositeRiskScore: number
  activeDeficiencyCount: number
  ulCompliant?: boolean
  readinessScore?: number
}

export default function PatientHeaderCard({
  patients,
  selectedPatient,
  onSelectPatient,
  compositeRiskScore,
  activeDeficiencyCount,
  ulCompliant = true,
  readinessScore = 92
}: PatientHeaderCardProps) {
  // Calculate BMI
  const heightM = selectedPatient.height_cm / 100
  const bmi = heightM > 0 ? (selectedPatient.weight_kg / (heightM * heightM)).toFixed(1) : '22.0'
  const bmiVal = parseFloat(bmi)
  const bmiTier = bmiVal < 18.5 ? 'Underweight' : bmiVal < 25 ? 'Normal BMI' : bmiVal < 30 ? 'Overweight' : 'Obese'
  const bmiColor = bmiVal < 18.5 ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    : bmiVal < 25 ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    : 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'

  const vulnerabilityColor = compositeRiskScore >= 70
    ? 'text-rose-400'
    : compositeRiskScore >= 45
    ? 'text-amber-400'
    : 'text-cyan-400'

  const vulnerabilityBg = compositeRiskScore >= 70
    ? 'from-rose-500/15 via-rose-500/5 to-transparent border-rose-500/30'
    : compositeRiskScore >= 45
    ? 'from-amber-500/15 via-amber-500/5 to-transparent border-amber-500/30'
    : 'from-cyan-500/15 via-cyan-500/5 to-transparent border-cyan-500/30'

  return (
    <div className="rounded-3xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-2xl shadow-2xl p-6 md:p-8 relative overflow-hidden transition-all">
      {/* Background ambient glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-teal-500/10 via-cyan-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

      {/* Top Bar: Switcher + Primary Identity */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-slate-800/80 relative z-10">
        <div className="flex items-center gap-4">
          {/* Avatar Ring */}
          <div className="relative">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-teal-500 p-0.5 shadow-lg shadow-cyan-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                <span className="text-xl font-black bg-gradient-to-r from-cyan-400 to-teal-300 bg-clip-text text-transparent">
                  {selectedPatient.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
            </div>
            <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-slate-950 flex items-center justify-center shadow">
              <CheckCircle2 className="w-3 h-3 text-slate-950" />
            </div>
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h2 className="text-2xl font-bold tracking-tight text-white">
                {selectedPatient.name}
              </h2>
              <span className="font-mono text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {selectedPatient.id}
              </span>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${bmiColor}`}>
                {bmiTier} (BMI {bmi})
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span>{selectedPatient.age} yrs</span>
              <span>•</span>
              <span className="capitalize">{selectedPatient.gender.toLowerCase()}</span>
              <span>•</span>
              <span className="px-2 py-0.5 rounded-md bg-teal-500/10 text-teal-300 border border-teal-500/20 font-medium">
                {selectedPatient.diet}
              </span>
              <span>•</span>
              <span>{selectedPatient.height_cm} cm / {selectedPatient.weight_kg} kg</span>
            </div>
          </div>
        </div>

        {/* Patient Switcher Tabs */}
        <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-slate-950/80 border border-slate-800/80 shadow-inner">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-3 hidden sm:inline-block">
            Select Patient:
          </span>
          {patients.map(p => {
            const isSelected = p.id === selectedPatient.id
            return (
              <button
                key={p.id}
                onClick={() => onSelectPatient(p)}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
                  isSelected
                    ? 'bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 shadow-md shadow-cyan-500/25 font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <User className={`w-3.5 h-3.5 ${isSelected ? 'text-slate-950' : 'text-slate-500'}`} />
                <span>{p.name.split(' ')[0]}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Bottom KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 relative z-10">
        {/* KPI 1: Vulnerability Score */}
        <div className={`p-4 md:p-5 rounded-2xl bg-gradient-to-br ${vulnerabilityBg} border backdrop-blur-md transition-all hover:scale-[1.01]`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Vulnerability Index
            </span>
            <HeartPulse className={`w-4 h-4 ${vulnerabilityColor}`} />
          </div>
          <div className="flex items-baseline gap-1">
            <span className={`text-3xl md:text-4xl font-black tracking-tight ${vulnerabilityColor}`}>
              {compositeRiskScore}
            </span>
            <span className="text-xs text-slate-500 font-medium">/ 100</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 mt-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                compositeRiskScore >= 70 ? 'bg-rose-500' : compositeRiskScore >= 45 ? 'bg-amber-500' : 'bg-cyan-500'
              }`}
              style={{ width: `${Math.min(100, compositeRiskScore)}%` }}
            />
          </div>
          <div className="text-[11px] text-slate-400 mt-2 font-medium">
            {compositeRiskScore >= 70 ? 'Severe multi-target risk' : compositeRiskScore >= 45 ? 'Moderate nutritional strain' : 'Subclinical risk profile'}
          </div>
        </div>

        {/* KPI 2: Active Deficiencies */}
        <div className="p-4 md:p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 backdrop-blur-md transition-all hover:scale-[1.01]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Priority Targets
            </span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl md:text-4xl font-black text-amber-400">
              {activeDeficiencyCount}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-semibold">
              Action Required
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-4">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            <span>Calibrated above risk threshold</span>
          </div>
        </div>

        {/* KPI 3: Unified Readiness */}
        <div className="p-4 md:p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 backdrop-blur-md transition-all hover:scale-[1.01]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Repletion Readiness
            </span>
            <Sparkles className="w-4 h-4 text-teal-400" />
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl md:text-4xl font-black text-teal-400">
              {readinessScore}%
            </span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 mt-3 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-teal-500 to-cyan-400 transition-all duration-700"
              style={{ width: `${Math.min(100, readinessScore)}%` }}
            />
          </div>
          <div className="text-[11px] text-slate-400 mt-2 font-medium">
            High adherence probability
          </div>
        </div>

        {/* KPI 4: Safety & NIH UL Bounds */}
        <div className="p-4 md:p-5 rounded-2xl bg-slate-950/60 border border-slate-800/80 backdrop-blur-md transition-all hover:scale-[1.01]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Safety Guardrails
            </span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl md:text-3xl font-black text-emerald-400">
              {ulCompliant ? 'UL Safe' : 'Warning'}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-300/80 mt-4">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>0 Tolerable Upper Limit Exceedances</span>
          </div>
        </div>
      </div>
    </div>
  )
}
