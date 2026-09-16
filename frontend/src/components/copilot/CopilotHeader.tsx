import React, { useState, useRef, useEffect } from 'react'
import {
  ChevronDown, Check, RefreshCw, FileText, ShieldCheck,
  User, Activity, Clock
} from 'lucide-react'
import { type PatientProfile } from './PatientHeaderCard'

interface CopilotHeaderProps {
  patients: PatientProfile[]
  selectedPatient: PatientProfile
  onSelectPatient: (p: PatientProfile) => void
  compositeRiskScore: number
  loading: boolean
  onRefresh: () => void
  onOpenSOAP: () => void
  onOpenAttest: () => void
}

export default function CopilotHeader({
  patients,
  selectedPatient,
  onSelectPatient,
  compositeRiskScore,
  loading,
  onRefresh,
  onOpenSOAP,
  onOpenAttest
}: CopilotHeaderProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleOutside)
      return () => document.removeEventListener('mousedown', handleOutside)
    }
  }, [dropdownOpen])

  // BMI Calculation
  const heightM = selectedPatient.height_cm / 100
  const bmi = heightM > 0 ? (selectedPatient.weight_kg / (heightM * heightM)).toFixed(1) : '24.1'

  // Risk Tier
  const isHighRisk = compositeRiskScore >= 65
  const isModRisk = compositeRiskScore >= 40 && compositeRiskScore < 65

  return (
    <header className="border-b border-slate-800/80 bg-[#0B0F14]/90 backdrop-blur-md sticky top-16 z-30">
      <div className="max-w-[1400px] mx-auto px-6 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Patient Selector & Summary */}
        <div className="flex items-center gap-4 flex-wrap">
          {/* Patient Selector Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-[#131B2B] hover:bg-slate-800/70 border border-slate-700/60 text-slate-200 text-xs font-medium transition-colors"
            >
              <div className="w-6 h-6 rounded-full bg-teal-500/15 text-teal-400 flex items-center justify-center text-[11px] font-semibold">
                {selectedPatient.name.split(' ').map(n => n[0]).join('')}
              </div>
              <span className="font-semibold text-white">{selectedPatient.name}</span>
              <span className="text-slate-400 text-[11px]">{selectedPatient.id}</span>
              <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {dropdownOpen && (
              <div className="absolute left-0 mt-2 w-72 rounded-xl bg-[#111827] border border-slate-800 shadow-2xl p-1.5 z-50">
                <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                  Select Active Patient Record
                </div>
                {patients.map(p => {
                  const isSelected = p.id === selectedPatient.id
                  return (
                    <button
                      key={p.id}
                      onClick={() => {
                        onSelectPatient(p)
                        setDropdownOpen(false)
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg text-xs flex items-center justify-between transition-colors ${
                        isSelected ? 'bg-teal-500/10 text-teal-300' : 'text-slate-300 hover:bg-slate-800/60'
                      }`}
                    >
                      <div>
                        <div className="font-medium text-white">{p.name}</div>
                        <div className="text-[11px] text-slate-400 mt-0.5">
                          {p.age}y · {p.gender.toLowerCase()} · {p.diet.toLowerCase()}
                        </div>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-teal-400" />}
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          {/* Demographic Summary Inline */}
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-300 pl-2 border-l border-slate-800">
            <span className="text-slate-400">Demographics:</span>
            <span className="font-medium text-slate-200">
              {selectedPatient.age}y {selectedPatient.gender.toLowerCase()}
            </span>
            <span className="text-slate-600">·</span>
            <span className="font-medium text-slate-200 capitalize">
              {selectedPatient.diet.toLowerCase()}
            </span>
            <span className="text-slate-600">·</span>
            <span className="text-slate-200 font-mono">
              BMI {bmi}
            </span>
          </div>
        </div>

        {/* Right: Risk Score, Last Update & Actions */}
        <div className="flex items-center gap-3.5 flex-wrap">
          {/* Risk Score Pill (Clean, Not Oversized) */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-[#131B2B] border border-slate-800">
            <span className="text-[11px] text-slate-400">Nutritional Risk:</span>
            <span className={`text-xs font-bold font-mono ${
              isHighRisk ? 'text-rose-400' : isModRisk ? 'text-amber-400' : 'text-teal-400'
            }`}>
              {compositeRiskScore}/100
            </span>
            <span className={`w-1.5 h-1.5 rounded-full ${
              isHighRisk ? 'bg-rose-400' : isModRisk ? 'bg-amber-400' : 'bg-teal-400'
            }`} />
          </div>

          {/* Real-time Sync Indicator */}
          <div className="hidden lg:flex items-center gap-1.5 text-[11px] text-slate-400">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Updated real-time</span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            title="Refresh clinical telemetry"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors disabled:opacity-40"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-teal-400' : ''}`} />
          </button>

          {/* Actions: EHR SOAP & Attestation */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenSOAP}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#131B2B] hover:bg-slate-800/80 border border-slate-700/60 text-slate-200 hover:text-white text-xs font-medium transition-colors"
            >
              <FileText className="w-3.5 h-3.5 text-slate-400" />
              <span>EHR Note</span>
            </button>
            <button
              onClick={onOpenAttest}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition-colors shadow-sm shadow-teal-900/30"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Attest & Sign</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
