import React from 'react'
import {
  User, ShieldAlert, Activity, Heart, Moon, Sun, Flame,
  CheckCircle2, AlertCircle, AlertTriangle, ArrowUpRight, Scale
} from 'lucide-react'
import { type PatientProfile } from './PatientHeaderCard'

interface PatientRiskSidebarProps {
  patient: PatientProfile
  compositeRiskScore: number
  activeDeficiencyCount: number
  readinessScore?: number
  symptoms?: Array<{
    symptom: string
    severity: number
    duration_weeks?: number
  }>
  demographics?: {
    sleep_hours?: number
    sunlight_exposure_min?: number
    stress_level?: number
    activity_level?: string
  }
}

export default function PatientRiskSidebar({
  patient,
  compositeRiskScore,
  activeDeficiencyCount,
  readinessScore = 94,
  symptoms = [],
  demographics
}: PatientRiskSidebarProps) {
  // Calculate BMI
  const heightM = patient.height_cm / 100
  const bmiVal = heightM > 0 ? (patient.weight_kg / (heightM * heightM)).toFixed(1) : '22.0'
  const bmiNum = parseFloat(bmiVal)
  const bmiTier = bmiNum < 18.5 ? 'Underweight' : bmiNum < 25 ? 'Normal BMI' : bmiNum < 30 ? 'Overweight' : 'Obese'
  const bmiColor = bmiNum < 18.5 ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    : bmiNum < 25 ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    : 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'

  const vulnerabilityLevel = compositeRiskScore >= 70 ? 'High Vulnerability' : compositeRiskScore >= 45 ? 'Moderate Vulnerability' : 'Low Vulnerability'
  const vulnerabilityColor = compositeRiskScore >= 70
    ? 'text-rose-400'
    : compositeRiskScore >= 45
    ? 'text-amber-400'
    : 'text-cyan-400'

  const sleepHours = demographics?.sleep_hours ?? 6.8
  const sunMin = demographics?.sunlight_exposure_min ?? (patient.diet === 'VEGAN' ? 10 : 20)
  const stress = demographics?.stress_level ?? 6

  // Fallback symptoms from patient record if not passed as array
  const activeSymptoms = symptoms.length > 0
    ? symptoms
    : Object.entries(patient.symptoms || {}).map(([symptom, severity]) => ({
        symptom,
        severity
      }))

  return (
    <aside className="w-full space-y-4 font-sans">
      {/* ─── 1. Patient Profile Card ─── */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4 backdrop-blur-sm">
        <div className="flex items-start justify-between gap-3 pb-3 border-b border-slate-800/60">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-teal-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-300 font-bold text-base shadow-sm">
              {patient.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h2 className="text-sm font-bold text-white tracking-tight">{patient.name}</h2>
                <span className="text-[10px] font-mono text-slate-400">#{patient.id}</span>
              </div>
              <p className="text-xs text-slate-400">
                {patient.age} yrs • {patient.gender === 'MALE' ? 'Male' : 'Female'}
              </p>
            </div>
          </div>
          <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${bmiColor}`}>
            {bmiVal} {bmiTier}
          </span>
        </div>

        {/* Demographics / Lifestyle Metrics */}
        <div className="grid grid-cols-2 gap-2 pt-3 text-xs">
          <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800/40">
            <div className="text-[10px] text-slate-400 flex items-center gap-1">
              <Scale className="w-3 h-3 text-teal-400" /> Diet Pattern
            </div>
            <div className="font-semibold text-slate-200 mt-0.5">{patient.diet}</div>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800/40">
            <div className="text-[10px] text-slate-400 flex items-center gap-1">
              <Moon className="w-3 h-3 text-indigo-400" /> Sleep Duration
            </div>
            <div className="font-semibold text-slate-200 mt-0.5">{sleepHours} hrs/night</div>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800/40">
            <div className="text-[10px] text-slate-400 flex items-center gap-1">
              <Sun className="w-3 h-3 text-amber-400" /> Sunlight Exp.
            </div>
            <div className="font-semibold text-slate-200 mt-0.5">{sunMin} min/day</div>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800/40">
            <div className="text-[10px] text-slate-400 flex items-center gap-1">
              <Flame className="w-3 h-3 text-rose-400" /> Stress Index
            </div>
            <div className="font-semibold text-slate-200 mt-0.5">Level {stress} / 10</div>
          </div>
        </div>
      </div>

      {/* ─── 2. Clinical Vulnerability Index ─── */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <ShieldAlert className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-slate-200">Vulnerability Index</span>
          </div>
          <span className={`text-[10px] font-bold uppercase tracking-wider ${vulnerabilityColor}`}>
            {vulnerabilityLevel}
          </span>
        </div>

        <div className="flex items-end justify-between gap-4 mb-2">
          <div>
            <div className="text-3xl font-black tracking-tight text-white font-mono">
              {compositeRiskScore}
              <span className="text-sm font-medium text-slate-500">/100</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">Calibrated ML Risk Composite</p>
          </div>

          <div className="text-right">
            <div className="text-sm font-bold text-emerald-400 font-mono">{readinessScore}%</div>
            <p className="text-[10px] text-slate-400">Intervention Readiness</p>
          </div>
        </div>

        {/* Progress Bar with Color Thresholds */}
        <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800/60 p-0.5">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              compositeRiskScore >= 70
                ? 'bg-gradient-to-r from-amber-500 to-rose-500'
                : compositeRiskScore >= 45
                ? 'bg-gradient-to-r from-teal-500 to-amber-500'
                : 'bg-gradient-to-r from-emerald-500 to-teal-500'
            }`}
            style={{ width: `${Math.min(100, Math.max(5, compositeRiskScore))}%` }}
          />
        </div>

        {/* Vulnerability factors breakdown */}
        <div className="mt-3 pt-3 border-t border-slate-800/40 space-y-1.5 text-[11px]">
          <div className="flex justify-between text-slate-400">
            <span>Dietary Exclusion Impact</span>
            <span className="font-semibold text-rose-400">+34 pts</span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Photoperiod/Sunlight Deficit</span>
            <span className="font-semibold text-amber-400">+22 pts</span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Symptom Intensity Load</span>
            <span className="font-semibold text-amber-400">+12 pts</span>
          </div>
        </div>
      </div>

      {/* ─── 3. Priority Targets & Urgency Triage ─── */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-4 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-slate-200">Urgency Triage</span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30 font-bold">
            {activeDeficiencyCount} Actionable Targets
          </span>
        </div>

        <div className="space-y-2">
          {activeSymptoms.map((sym, idx) => {
            const isHigh = sym.severity >= 3
            return (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/40 border border-slate-800/40 text-xs"
              >
                <div className="flex items-center gap-2">
                  <span className={`w-1.5 h-1.5 rounded-full ${isHigh ? 'bg-rose-400' : 'bg-amber-400'}`} />
                  <span className="text-slate-200 font-medium capitalize">
                    {sym.symptom.replace(/_/g, ' ')}
                  </span>
                </div>
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                  isHigh ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                }`}>
                  Sev {sym.severity}/5
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </aside>
  )
}
