/* ═══════════════════════════════════════════════════════════════════════════
   SystemImpactPanel.tsx — Phase 7B Biological System Impact Breakdown
   Linear/Arc-style cards breaking down organ systems and nutrient contributions
   ═══════════════════════════════════════════════════════════════════════════ */

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Brain, Activity, Heart, Flame, Dna, ChevronRight, Check } from 'lucide-react'
import { PALETTE } from './NetworkData'

export interface SystemContributionItem {
  nutrient_id: string
  nutrient_name: string
  contribution_percentage: number
  role: string
}

export interface SystemImpactResponse {
  system_id: string
  system_name: string
  description: string
  total_connected_nutrients: number
  total_associated_symptoms: number
  key_nutrients: SystemContributionItem[]
  associated_symptoms: string[]
  physiological_mechanisms: string[]
}

const SYSTEMS_CATALOG = [
  { id: 'SYSTEM_IMMUNE', name: 'Immune & Defense', icon: Shield, color: '#3FB950' },
  { id: 'SYSTEM_NEUROLOGICAL', name: 'Neurological & Cognitive', icon: Brain, color: '#58A6FF' },
  { id: 'SYSTEM_MUSCULOSKELETAL', name: 'Musculoskeletal', icon: Activity, color: '#FFCF5C' },
  { id: 'SYSTEM_CARDIOVASCULAR', name: 'Cardiovascular & Blood', icon: Heart, color: '#FF7B72' },
  { id: 'SYSTEM_ENDOCRINE', name: 'Endocrine & Hormonal', icon: Flame, color: '#D2A8FF' },
  { id: 'SYSTEM_METABOLIC', name: 'Metabolic & ATP', icon: Dna, color: '#38BDF8' }
]

export default function SystemImpactPanel() {
  const [selectedSystemId, setSelectedSystemId] = useState<string>('SYSTEM_IMMUNE')
  const [systemData, setSystemData] = useState<SystemImpactResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/v1/knowledge-graph/systems/${selectedSystemId}`)
      .then(res => res.json())
      .then(json => {
        setSystemData(json)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load system impact:', err)
        setLoading(false)
      })
  }, [selectedSystemId])

  const activeMeta = SYSTEMS_CATALOG.find(s => s.id === selectedSystemId) || SYSTEMS_CATALOG[0]
  const ActiveIcon = activeMeta.icon

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', gap: 14,
      background: PALETTE.card, borderRadius: 14,
      border: `1px solid ${PALETTE.border}`,
      padding: '20px 24px',
      color: PALETTE.text,
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: `${activeMeta.color}20`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: activeMeta.color
          }}>
            <ActiveIcon size={18} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, letterSpacing: '-0.02em', color: PALETTE.text }}>
              Biological System Impact Analysis
            </h3>
            <span style={{ fontSize: 12, color: PALETTE.textMuted }}>
              Evaluate physiological dependency and nutrient contribution percentages
            </span>
          </div>
        </div>
      </div>

      {/* Systems Selector Tabs */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 6,
        background: 'rgba(0, 0, 0, 0.25)', padding: 4, borderRadius: 10,
        border: `1px solid ${PALETTE.borderLight}`
      }}>
        {SYSTEMS_CATALOG.map(sys => {
          const isSelected = sys.id === selectedSystemId
          const Icon = sys.icon

          return (
            <button
              key={sys.id}
              onClick={() => setSelectedSystemId(sys.id)}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                padding: '8px 10px', borderRadius: 7,
                background: isSelected ? PALETTE.card : 'transparent',
                color: isSelected ? sys.color : PALETTE.textMuted,
                border: isSelected ? `1px solid ${sys.color}40` : '1px solid transparent',
                fontSize: 11.5, fontWeight: 600, cursor: 'pointer',
                transition: 'all 0.15s ease', whiteSpace: 'nowrap'
              }}
            >
              <Icon size={14} color={isSelected ? sys.color : PALETTE.textDim} />
              <span>{sys.name}</span>
            </button>
          )
        })}
      </div>

      {/* Content Body */}
      {loading ? (
        <div style={{ padding: 24, textAlign: 'center', color: PALETTE.textMuted, fontSize: 13 }}>
          Loading system impact calculations...
        </div>
      ) : systemData ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 16 }}>
          {/* Left Column: Key Nutrients with Contribution Percentages */}
          <div style={{
            display: 'flex', flexDirection: 'column', gap: 10,
            background: 'rgba(255, 255, 255, 0.015)',
            border: `1px solid ${PALETTE.borderLight}`,
            borderRadius: 10, padding: 14
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 12, fontWeight: 700, color: PALETTE.text, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Nutrient Contribution Breakdown
              </span>
              <span style={{ fontSize: 11, color: activeMeta.color, fontWeight: 600 }}>
                {systemData.total_connected_nutrients} Key Determinants
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {systemData.key_nutrients.map((item, idx) => (
                <div key={item.nutrient_id} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12 }}>
                    <span style={{ fontWeight: 600, color: PALETTE.text }}>
                      {item.nutrient_name}
                    </span>
                    <strong style={{ color: activeMeta.color, fontWeight: 700 }}>
                      {item.contribution_percentage}%
                    </strong>
                  </div>

                  {/* Progress bar */}
                  <div style={{
                    height: 6, width: '100%', background: 'rgba(255, 255, 255, 0.06)',
                    borderRadius: 3, overflow: 'hidden'
                  }}>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.contribution_percentage}%` }}
                      transition={{ duration: 0.5, delay: idx * 0.05 }}
                      style={{
                        height: '100%',
                        background: activeMeta.color,
                        borderRadius: 3
                      }}
                    />
                  </div>

                  <span style={{ fontSize: 10.5, color: PALETTE.textDim, fontStyle: 'italic' }}>
                    {item.role}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Symptoms & Biological Mechanisms */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* System Description */}
            <div style={{
              fontSize: 12.5, color: '#C9D1D9', lineHeight: 1.5,
              background: 'rgba(255, 255, 255, 0.02)', padding: 12, borderRadius: 8,
              border: `1px solid ${PALETTE.borderLight}`
            }}>
              {systemData.description}
            </div>

            {/* Associated Symptoms */}
            <div style={{
              display: 'flex', flexDirection: 'column', gap: 8,
              background: 'rgba(255, 255, 255, 0.015)',
              border: `1px solid ${PALETTE.borderLight}`,
              borderRadius: 10, padding: 12
            }}>
              <span style={{ fontSize: 11.5, fontWeight: 700, color: PALETTE.textMuted, textTransform: 'uppercase' }}>
                Associated Clinical Symptoms ({systemData.total_associated_symptoms})
              </span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {systemData.associated_symptoms.map(sym => (
                  <span
                    key={sym}
                    style={{
                      fontSize: 11, fontWeight: 600, padding: '3px 8px', borderRadius: 5,
                      background: 'rgba(255, 77, 77, 0.08)', color: '#FFA198',
                      border: '1px solid rgba(255, 77, 77, 0.2)'
                    }}
                  >
                    {sym}
                  </span>
                ))}
              </div>
            </div>

            {/* Core Mechanisms */}
            {systemData.physiological_mechanisms.length > 0 && (
              <div style={{
                display: 'flex', flexDirection: 'column', gap: 6,
                background: 'rgba(255, 255, 255, 0.015)',
                border: `1px solid ${PALETTE.borderLight}`,
                borderRadius: 10, padding: 12
              }}>
                <span style={{ fontSize: 11.5, fontWeight: 700, color: PALETTE.textMuted, textTransform: 'uppercase' }}>
                  Core Physiological Mechanisms
                </span>
                <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11.5, color: PALETTE.textMuted, lineHeight: 1.4 }}>
                  {systemData.physiological_mechanisms.map((mech, i) => (
                    <li key={i} style={{ marginBottom: 4 }}>{mech}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  )
}
