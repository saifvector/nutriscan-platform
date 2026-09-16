import React, { useState, useRef, useEffect } from 'react'
import { ChevronDown, RefreshCw, Check } from 'lucide-react'
import { type PatientProfile } from './PatientHeaderCard'

interface CleanCopilotHeaderProps {
  patients: PatientProfile[]
  selectedPatient: PatientProfile
  onSelectPatient: (patient: PatientProfile) => void
  activeTab: 'dossier' | 'soap' | 'differential' | 'review'
  setActiveTab: (tab: any) => void
  loading: boolean
  onRefresh: () => void
}

export default function CleanCopilotHeader({
  patients,
  selectedPatient,
  onSelectPatient,
  activeTab,
  setActiveTab,
  loading,
  onRefresh
}: CleanCopilotHeaderProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [dropdownOpen])

  const tabs = [
    { id: 'dossier', label: 'Executive Overview' },
    { id: 'soap', label: 'EMR SOAP Note' },
    { id: 'differential', label: 'Differential' },
    { id: 'review', label: 'Review & Sign-Off' }
  ] as const

  return (
    <div
      className="w-full sticky top-16 z-30"
      style={{
        background: 'rgba(11,17,32,0.92)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(51,65,85,0.15)',
      }}
    >
      <div className="max-w-6xl mx-auto px-6 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Left: Title & Patient Selector */}
        <div className="flex items-center gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-semibold text-white tracking-tight">
                Clinical Copilot
              </h1>
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  background: '#14D9C4',
                  boxShadow: '0 0 6px rgba(20,217,196,0.4)',
                }}
              />
            </div>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Precision screening and evidence-based decision support
            </p>
          </div>

          {/* Patient Selector Pill */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-all"
              style={{
                background: dropdownOpen ? 'rgba(30,41,59,0.9)' : 'rgba(30,41,59,0.5)',
                border: `1px solid ${dropdownOpen ? 'rgba(20,217,196,0.2)' : 'rgba(51,65,85,0.3)'}`,
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: '#14D9C4' }}
              />
              <span className="font-medium text-white">{selectedPatient.name}</span>
              <span className="text-slate-400">{selectedPatient.age}y · {selectedPatient.diet}</span>
              <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {dropdownOpen && (
              <div
                className="absolute left-0 mt-2 w-64 rounded-xl p-1.5 z-50 shadow-2xl"
                style={{
                  background: 'rgba(15,23,42,0.98)',
                  border: '1px solid rgba(51,65,85,0.3)',
                  backdropFilter: 'blur(20px)',
                }}
              >
                <div className="px-2.5 py-1.5 text-[10px] font-medium text-slate-500 uppercase tracking-wider">
                  Select Patient
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
                      className="w-full text-left px-2.5 py-2.5 rounded-lg text-xs flex items-center justify-between transition-all"
                      style={{
                        background: isSelected ? 'rgba(20,217,196,0.06)' : 'transparent',
                        color: isSelected ? '#14D9C4' : '#cbd5e1',
                      }}
                      onMouseEnter={e => {
                        if (!isSelected) (e.currentTarget as HTMLElement).style.background = 'rgba(30,41,59,0.5)'
                      }}
                      onMouseLeave={e => {
                        if (!isSelected) (e.currentTarget as HTMLElement).style.background = 'transparent'
                      }}
                    >
                      <div>
                        <div className="font-medium">{p.name}</div>
                        <div className="text-[10px] text-slate-500 mt-0.5">{p.age} yrs · {p.diet}</div>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-[#14D9C4]" />}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right: Tab Switcher + Refresh */}
        <div className="flex items-center gap-2.5 self-end md:self-auto">
          <nav
            className="flex items-center gap-0.5 p-1 rounded-lg"
            style={{ background: 'rgba(30,41,59,0.4)', border: '1px solid rgba(51,65,85,0.2)' }}
          >
            {tabs.map(tab => {
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className="relative px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
                  style={{
                    color: isActive ? '#fff' : '#64748b',
                    background: isActive ? 'rgba(51,65,85,0.5)' : 'transparent',
                    boxShadow: isActive ? '0 1px 3px rgba(0,0,0,0.2)' : 'none',
                  }}
                >
                  {tab.label}
                </button>
              )
            })}
          </nav>

          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 rounded-lg transition-all disabled:opacity-40"
            style={{ color: loading ? '#14D9C4' : '#64748b' }}
            title="Refresh clinical data"
            onMouseEnter={e => {
              if (!loading) (e.currentTarget as HTMLElement).style.color = '#fff'
            }}
            onMouseLeave={e => {
              if (!loading) (e.currentTarget as HTMLElement).style.color = '#64748b'
            }}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </div>
  )
}
