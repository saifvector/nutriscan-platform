import React from 'react'
import {
  Stethoscope, Activity, Sparkles, FileText, AlertTriangle,
  UserCheck, Calendar, RefreshCw, ChevronDown, User, ShieldCheck, Zap
} from 'lucide-react'
import { type PatientProfile } from './PatientHeaderCard'

interface CopilotWorkspaceHeaderProps {
  patients: PatientProfile[]
  selectedPatient: PatientProfile
  onSelectPatient: (patient: PatientProfile) => void
  activeTab: 'dossier' | 'assessment' | 'soap' | 'differential' | 'review' | 'followup'
  setActiveTab: (tab: 'dossier' | 'assessment' | 'soap' | 'differential' | 'review' | 'followup') => void
  loading: boolean
  onRefresh: () => void
  compositeRiskScore: number
  differentialCount?: number
  auditCount?: number
  followUpCount?: number
}

export default function CopilotWorkspaceHeader({
  patients,
  selectedPatient,
  onSelectPatient,
  activeTab,
  setActiveTab,
  loading,
  onRefresh,
  compositeRiskScore,
  differentialCount,
  auditCount,
  followUpCount
}: CopilotWorkspaceHeaderProps) {
  const [dropdownOpen, setDropdownOpen] = React.useState(false)

  const tabs = [
    { id: 'dossier', label: 'Dossier', icon: Activity, count: null },
    { id: 'assessment', label: 'Assessment', icon: Sparkles, count: '7-Part' },
    { id: 'soap', label: 'EMR SOAP', icon: FileText, count: null },
    { id: 'differential', label: 'Differential', icon: AlertTriangle, count: differentialCount ? `${differentialCount}` : null },
    { id: 'review', label: 'Sign-Off', icon: UserCheck, count: auditCount ? `${auditCount}` : null },
    { id: 'followup', label: 'Follow-Up', icon: Calendar, count: followUpCount ? `${followUpCount}` : null }
  ] as const

  const riskLabel = compositeRiskScore >= 70 ? 'High' : compositeRiskScore >= 45 ? 'Moderate' : 'Low'
  const riskColor = compositeRiskScore >= 70
    ? 'text-rose-400 bg-rose-500/10 border-rose-500/20'
    : compositeRiskScore >= 45
    ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    : 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20'

  return (
    <header className="sticky top-16 z-30 w-full bg-slate-950/90 backdrop-blur-xl border-b border-slate-800/80 px-4 lg:px-6 py-2.5 transition-all">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-2.5 max-w-[1920px] mx-auto min-h-[52px]">
        {/* Left: Product branding + Patient Selector */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-sm">
              <Stethoscope className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 leading-none">
                <span className="text-sm font-bold text-white tracking-tight">Clinical Copilot</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                  v2.4
                </span>
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
              </div>
            </div>
          </div>

          <div className="h-5 w-[1px] bg-slate-800 hidden sm:block" />

          {/* 1-Click Patient Switcher Capsule */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 text-xs font-semibold text-slate-200 transition-all shadow-sm"
              title="Switch Active Patient Cohort"
            >
              <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-cyan-500 to-teal-400 flex items-center justify-center text-[10px] font-bold text-slate-950">
                {selectedPatient.name.charAt(0)}
              </div>
              <span className="text-slate-100 font-medium">{selectedPatient.name}</span>
              <span className="text-[11px] text-slate-400 font-normal">
                {selectedPatient.age}y • {selectedPatient.gender.charAt(0)} • {selectedPatient.diet}
              </span>
              <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {dropdownOpen && (
              <div className="absolute left-0 mt-2 w-72 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-100">
                <div className="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Select Clinical Case
                </div>
                <div className="space-y-1">
                  {patients.map(p => {
                    const isSelected = p.id === selectedPatient.id
                    return (
                      <button
                        key={p.id}
                        onClick={() => {
                          onSelectPatient(p)
                          setDropdownOpen(false)
                        }}
                        className={`w-full text-left px-2.5 py-2 rounded-xl text-xs flex items-center justify-between transition-colors ${
                          isSelected
                            ? 'bg-cyan-500/15 text-cyan-300 font-semibold border border-cyan-500/30'
                            : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
                            isSelected ? 'bg-cyan-400 text-slate-950' : 'bg-slate-800 text-slate-300'
                          }`}>
                            {p.name.charAt(0)}
                          </div>
                          <div>
                            <div className="text-xs">{p.name}</div>
                            <div className="text-[10px] text-slate-400">{p.diet} • {p.age}y</div>
                          </div>
                        </div>
                        {isSelected && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
                            Active
                          </span>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Center: Segment Tab Switcher */}
        <nav className="flex items-center gap-1 p-1 rounded-xl bg-slate-900/90 border border-slate-800/80 overflow-x-auto no-scrollbar">
          {tabs.map(tab => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white font-semibold shadow-sm border border-slate-700/60'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {tab.count && (
                  <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${
                    isActive ? 'bg-cyan-500/20 text-cyan-300' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Right: Operational Telemetry & Refresh */}
        <div className="flex items-center gap-2.5 self-end lg:self-auto">
          <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono font-semibold ${riskColor}`}>
            <span className="text-[10px] uppercase font-sans font-bold text-slate-400">Risk:</span>
            <span>{compositeRiskScore}/100 {riskLabel}</span>
          </div>

          <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-400">
            <Zap className="w-3 h-3 text-cyan-400" />
            <span>18ms SHAP</span>
          </div>

          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 active:scale-95 border border-slate-800 text-slate-300 hover:text-white text-xs font-medium transition-all disabled:opacity-50"
            title="Refresh clinical telemetry and inference models"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : 'text-slate-400'}`} />
            <span className="hidden sm:inline">{loading ? 'Syncing...' : 'Sync Telemetry'}</span>
          </button>
        </div>
      </div>
    </header>
  )
}
