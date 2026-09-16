import React, { useState, useEffect } from 'react'
import { ChevronDown, ChevronUp, User, Heart, Moon, Sun } from 'lucide-react'
import { type PatientProfile } from './PatientHeaderCard'

interface ExecutivePatientHeroProps {
  patient: PatientProfile
  compositeRiskScore: number
  overallStatus: string
  executiveSummary?: string
  symptoms?: Array<{
    symptom: string
    severity: number
  }>
  demographics?: {
    sleep_hours?: number
    sunlight_exposure_min?: number
    stress_level?: number
  }
}

export default function ExecutivePatientHero({
  patient,
  compositeRiskScore,
  overallStatus,
  executiveSummary,
  symptoms = [],
  demographics
}: ExecutivePatientHeroProps) {
  const [expanded, setExpanded] = useState(false)
  const [animatedScore, setAnimatedScore] = useState(0)

  // Animate risk score on mount
  useEffect(() => {
    const target = compositeRiskScore
    let current = 0
    const step = Math.max(1, Math.floor(target / 30))
    const timer = setInterval(() => {
      current = Math.min(current + step, target)
      setAnimatedScore(current)
      if (current >= target) clearInterval(timer)
    }, 25)
    return () => clearInterval(timer)
  }, [compositeRiskScore])

  // Calculate BMI
  const heightM = patient.height_cm / 100
  const bmiVal = heightM > 0 ? (patient.weight_kg / (heightM * heightM)).toFixed(1) : '22.0'
  const bmiNum = parseFloat(bmiVal)
  const bmiCategory = bmiNum < 18.5 ? 'Underweight' : bmiNum < 25 ? 'Normal' : bmiNum < 30 ? 'Overweight' : 'Obese'

  const sleepHours = demographics?.sleep_hours ?? 6.8
  const sunMin = demographics?.sunlight_exposure_min ?? (patient.diet === 'VEGAN' ? 10 : 20)

  // Risk status
  const isHighRisk = compositeRiskScore >= 60
  const isModerateRisk = compositeRiskScore >= 35 && compositeRiskScore < 60
  const riskStatusText = isHighRisk ? 'High Risk' : isModerateRisk ? 'Moderate Risk' : 'Low Risk'

  const riskColor = isHighRisk
    ? { ring: '#f43f5e', bg: 'rgba(244,63,94,0.08)', text: 'text-rose-300', border: 'border-rose-500/20' }
    : isModerateRisk
    ? { ring: '#f59e0b', bg: 'rgba(245,158,11,0.08)', text: 'text-amber-300', border: 'border-amber-500/20' }
    : { ring: '#14D9C4', bg: 'rgba(20,217,196,0.08)', text: 'text-[#14D9C4]', border: 'border-[#14D9C4]/20' }

  // Symptoms
  const activeSymptoms = symptoms.length > 0
    ? symptoms
    : Object.entries(patient.symptoms || {}).map(([symptom, severity]) => ({
        symptom,
        severity
      }))

  // Executive summary — truncate for glance
  const summaryText = executiveSummary || `Screening indicates an elevated nutritional risk profile driven primarily by ${patient.diet.toLowerCase()} dietary restrictions and reduced sunlight exposure. Immediate targeted repletion is recommended.`
  const isTruncatable = summaryText.length > 180
  const displaySummary = isTruncatable && !expanded ? summaryText.slice(0, 180) + '…' : summaryText

  // SVG ring params
  const ringSize = 120
  const strokeWidth = 6
  const radius = (ringSize - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const progress = Math.min(100, Math.max(0, animatedScore)) / 100
  const strokeDashoffset = circumference * (1 - progress)

  return (
    <section
      className="relative rounded-2xl overflow-hidden bg-[#131B2B] border border-slate-800/60 shadow-sm"
      style={{
        animation: 'fadeSlideUp 0.5s ease-out both',
      }}
    >

      <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-10 p-6 sm:p-8 items-center">
        {/* Left Side (8 Cols): Patient Identity + Clinical Synthesis */}
        <div className="lg:col-span-8 space-y-5">
          {/* Identity Row */}
          <div className="flex items-start gap-4">
            {/* Avatar */}
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0 bg-teal-500/10 border border-teal-500/20"
            >
              <User className="w-5 h-5 text-[#14D9C4]" />
            </div>

            <div className="min-w-0">
              <div className="flex items-center gap-3 flex-wrap">
                <h2 className="text-2xl font-semibold text-white tracking-tight leading-tight">
                  {patient.name}
                </h2>
                <span className="text-[11px] text-slate-500 font-mono">#{patient.id}</span>
              </div>

              {/* Demographic Pills */}
              <div className="flex items-center gap-2 mt-2 flex-wrap">
                {[
                  `${patient.age} yrs`,
                  patient.gender === 'MALE' ? 'Male' : 'Female',
                  `BMI ${bmiVal} · ${bmiCategory}`,
                ].map((label, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 rounded-lg text-[11px] font-medium text-slate-300 bg-slate-800/50 border border-slate-700/50"
                  >
                    {label}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Vitals Strip */}
          <div className="flex items-center gap-5 text-xs text-slate-400 flex-wrap">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#14D9C4]" />
              <strong className="text-slate-200 font-medium">Diet</strong> {patient.diet}
            </span>
            <span className="flex items-center gap-1.5">
              <Moon className="w-3 h-3 text-slate-500" />
              <strong className="text-slate-200 font-medium">Sleep</strong> {sleepHours} hrs
            </span>
            <span className="flex items-center gap-1.5">
              <Sun className="w-3 h-3 text-slate-500" />
              <strong className="text-slate-200 font-medium">Sunlight</strong> {sunMin} min/day
            </span>
          </div>

          {/* Executive Synthesis — readable paragraph */}
          <div>
            <p className="text-sm text-slate-300 leading-[1.7]">
              {displaySummary}
            </p>
            {isTruncatable && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="mt-1.5 text-[11px] text-[#14D9C4] hover:text-[#14D9C4]/80 font-medium inline-flex items-center gap-1 transition-colors"
              >
                {expanded ? (
                  <><span>Show less</span><ChevronUp className="w-3 h-3" /></>
                ) : (
                  <><span>Read full summary</span><ChevronDown className="w-3 h-3" /></>
                )}
              </button>
            )}
          </div>

          {/* Symptom Tags */}
          {activeSymptoms.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] text-slate-500 font-medium mr-1">Symptoms</span>
              {activeSymptoms.slice(0, 5).map((sym, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-lg text-[11px] text-slate-300 font-normal transition-colors hover:text-white bg-teal-500/5 border border-teal-500/10"
                >
                  {sym.symptom.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Right Side (4 Cols): Circular Risk Score */}
        <div className="lg:col-span-4 flex flex-col items-center lg:items-end">
          <div
            className="flex flex-col items-center gap-3 p-6 rounded-2xl bg-[#0B0F14] border border-slate-800/60 shadow-inner"
          >
            {/* Animated SVG Ring */}
            <div className="relative" style={{ width: ringSize, height: ringSize }}>
              <svg width={ringSize} height={ringSize} className="-rotate-90">
                {/* Background track */}
                <circle
                  cx={ringSize / 2}
                  cy={ringSize / 2}
                  r={radius}
                  fill="none"
                  stroke="rgba(30,41,59,0.6)"
                  strokeWidth={strokeWidth}
                />
                {/* Progress arc */}
                <circle
                  cx={ringSize / 2}
                  cy={ringSize / 2}
                  r={radius}
                  fill="none"
                  stroke={riskColor.ring}
                  strokeWidth={strokeWidth}
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  style={{ transition: 'stroke-dashoffset 0.8s ease-out' }}
                />
              </svg>
              {/* Center number */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-white font-mono tracking-tight leading-none">
                  {animatedScore}
                </span>
                <span className="text-[10px] text-slate-400 font-medium mt-0.5">/100</span>
              </div>
            </div>

            <div className="text-center">
              <div className="text-[11px] text-slate-400 font-medium">
                Nutritional Risk Score
              </div>
              <span
                className={`inline-block mt-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${riskColor.text} ${riskColor.border} border bg-[#131B2B]`}
              >
                {riskStatusText}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
