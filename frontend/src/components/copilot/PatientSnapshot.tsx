import React from 'react'
import { User, Sun, Moon, Zap, Heart, Scale } from 'lucide-react'
import { type PatientProfile } from './PatientHeaderCard'

interface PatientSnapshotProps {
  patient: PatientProfile
  demographics?: {
    sleep_hours?: number
    sunlight_exposure_min?: number
    stress_level?: number
    activity_level?: string
  }
}

export default function PatientSnapshot({
  patient,
  demographics
}: PatientSnapshotProps) {
  // Calculate BMI
  const heightM = patient.height_cm / 100
  const bmiNum = heightM > 0 ? patient.weight_kg / (heightM * heightM) : 24.1
  const bmi = bmiNum.toFixed(1)
  const bmiCategory =
    bmiNum < 18.5
      ? 'Underweight'
      : bmiNum < 25
      ? 'Normal weight'
      : bmiNum < 30
      ? 'Overweight'
      : 'Obese'

  const sleepHours = demographics?.sleep_hours ?? 6.8
  const sunlightMin = demographics?.sunlight_exposure_min ?? (patient.diet === 'VEGAN' ? 10 : 20)
  const stress = demographics?.stress_level ?? 6

  return (
    <div className="rounded-2xl bg-[#111827] border border-slate-800/80 p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <User className="w-3.5 h-3.5 text-teal-400" />
          <span>Patient Snapshot</span>
        </h3>
        <span className="text-[11px] font-mono text-slate-400">{patient.id}</span>
      </div>

      {/* Primary Anthropometrics Grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
          <div className="text-[10px] uppercase font-semibold text-slate-400">Demographics</div>
          <div className="text-sm font-semibold text-white mt-1">
            {patient.age}y · {patient.gender.toLowerCase() === 'female' ? 'Female' : 'Male'}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            {patient.height_cm} cm / {patient.weight_kg} kg
          </div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
          <div className="text-[10px] uppercase font-semibold text-slate-400">Dietary Pattern</div>
          <div className="text-sm font-semibold text-white mt-1 capitalize">
            {patient.diet.toLowerCase()}
          </div>
          <div className="text-[11px] text-teal-400 mt-0.5 font-medium">Primary driver</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
          <div className="text-[10px] uppercase font-semibold text-slate-400">Body Mass Index</div>
          <div className="text-sm font-semibold text-white mt-1 font-mono">
            {bmi} <span className="text-xs font-normal text-slate-400">kg/m²</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">{bmiCategory}</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60">
          <div className="text-[10px] uppercase font-semibold text-slate-400">Lifestyle Vitals</div>
          <div className="text-sm font-semibold text-white mt-1">
            {sleepHours}h <span className="text-xs font-normal text-slate-400">sleep</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            {sunlightMin}m sun · {stress}/10 stress
          </div>
        </div>
      </div>

      {/* Reported Symptoms Tags */}
      {patient.symptoms && Object.keys(patient.symptoms).length > 0 && (
        <div className="pt-2 border-t border-slate-800/60">
          <div className="text-[10px] uppercase font-semibold text-slate-400 mb-2">
            Active Reported Symptoms
          </div>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(patient.symptoms).map(([symptom, severity]) => (
              <span
                key={symptom}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-slate-800/60 border border-slate-700/50 text-slate-300"
              >
                <span className="capitalize">{symptom.replace(/_/g, ' ')}</span>
                <span className="font-mono text-[10px] text-amber-400">({severity}/10)</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
