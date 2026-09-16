/* ═══════════════════════════════════════════════════════════════════════════
   ClinicalPathViewer.tsx — Phase 7B Causal Path Intelligence
   Linear/Arc-style dark glassmorphism interface tracing biochemical causality
   ═══════════════════════════════════════════════════════════════════════════ */

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  GitCommit, ArrowRight, BookOpen, AlertCircle,
  Sparkles, CheckCircle2, ChevronRight, Activity, Zap
} from 'lucide-react'
import { PALETTE } from './NetworkData'

export interface PathHop {
  step: number
  source_id: string
  source_name: string
  source_type: string
  target_id: string
  target_name: string
  target_type: string
  relationship_type: string
  mechanism: string
  citation?: string
}

export interface ShortestPathResponse {
  source_id: string
  source_name: string
  target_id: string
  target_name: string
  path_length: number
  exists: boolean
  hops: PathHop[]
  node_sequence: string[]
  clinical_summary: string
}

const PRESET_PATHWAYS = [
  {
    label: 'Low Sun ➔ Bone Pain',
    source: 'LIFESTYLE_LOW_SUN',
    target: 'SYMPTOM_BONE_PAIN',
    category: 'Musculoskeletal'
  },
  {
    label: 'Vegan Diet ➔ Tingling / Paresthesia',
    source: 'LIFESTYLE_STRICT_VEGAN',
    target: 'SYMPTOM_TINGLING_NUMBNESS',
    category: 'Neurological'
  },
  {
    label: 'Celiac Disease ➔ Fatigue',
    source: 'CONDITION_CELIAC',
    target: 'SYMPTOM_FATIGUE',
    category: 'Hematological'
  },
  {
    label: 'Alcohol ➔ Muscle Weakness',
    source: 'LIFESTYLE_ALCOHOL',
    target: 'SYMPTOM_MUSCLE_WEAKNESS',
    category: 'Metabolic'
  },
  {
    label: 'Smoking ➔ Slow Wound Healing',
    source: 'LIFESTYLE_SMOKING',
    target: 'SYMPTOM_SLOW_WOUND_HEALING',
    category: 'Integumentary'
  }
]

const REL_BADGE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  CAUSES: { bg: 'rgba(255, 77, 77, 0.15)', text: '#FF6B6B', border: 'rgba(255, 77, 77, 0.3)' },
  CONTRIBUTES_TO: { bg: 'rgba(255, 176, 32, 0.15)', text: '#FFCF5C', border: 'rgba(255, 176, 32, 0.3)' },
  ASSOCIATED_WITH: { bg: 'rgba(88, 166, 255, 0.15)', text: '#79C0FF', border: 'rgba(88, 166, 255, 0.3)' },
  IMPACTS: { bg: 'rgba(187, 128, 255, 0.15)', text: '#D2A8FF', border: 'rgba(187, 128, 255, 0.3)' },
  REQUIRES: { bg: 'rgba(56, 189, 248, 0.15)', text: '#38BDF8', border: 'rgba(56, 189, 248, 0.3)' },
  SUPPORTS: { bg: 'rgba(63, 185, 80, 0.15)', text: '#56D364', border: 'rgba(63, 185, 80, 0.3)' },
  INHIBITS: { bg: 'rgba(248, 81, 73, 0.15)', text: '#FFA198', border: 'rgba(248, 81, 73, 0.3)' },
  ENHANCES: { bg: 'rgba(46, 160, 67, 0.15)', text: '#3FB950', border: 'rgba(46, 160, 67, 0.3)' },
  CONFIRMS: { bg: 'rgba(163, 113, 247, 0.15)', text: '#BC8CFF', border: 'rgba(163, 113, 247, 0.3)' },
  AFFECTS: { bg: 'rgba(210, 153, 34, 0.15)', text: '#E3B341', border: 'rgba(210, 153, 34, 0.3)' }
}

export default function ClinicalPathViewer() {
  const [sourceId, setSourceId] = useState<string>('LIFESTYLE_LOW_SUN')
  const [targetId, setTargetId] = useState<string>('SYMPTOM_BONE_PAIN')
  const [pathData, setPathData] = useState<ShortestPathResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [entities, setEntities] = useState<{ id: string; name: string; entity_type: string }[]>([])

  // Load available entities for dropdown selector
  useEffect(() => {
    fetch('/api/v1/knowledge-graph/entities')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setEntities(data)
        }
      })
      .catch(err => console.error('Failed to load knowledge graph entities:', err))
  }, [])

  // Execute path query
  const fetchPath = async (src: string, tgt: string) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/v1/knowledge-graph/path?source=${encodeURIComponent(src)}&target=${encodeURIComponent(tgt)}`)
      if (!res.ok) throw new Error(`HTTP error ${res.status}`)
      const json: ShortestPathResponse = await res.json()
      setPathData(json)
    } catch (e: any) {
      setError(e.message || 'Failed to resolve clinical pathway')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPath(sourceId, targetId)
  }, [sourceId, targetId])

  const handleSelectPreset = (p: typeof PRESET_PATHWAYS[0]) => {
    setSourceId(p.source)
    setTargetId(p.target)
  }

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', gap: 16,
      background: PALETTE.card, borderRadius: 14,
      border: `1px solid ${PALETTE.border}`,
      padding: '20px 24px',
      color: PALETTE.text,
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'rgba(88, 166, 255, 0.12)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: PALETTE.accent
          }}>
            <GitCommit size={18} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, letterSpacing: '-0.02em', color: PALETTE.text }}>
              Clinical Causal Path Viewer
            </h3>
            <span style={{ fontSize: 12, color: PALETTE.textMuted }}>
              Trace biomedical etiology from upstream drivers through nutrient interactions to clinical endpoints
            </span>
          </div>
        </div>

        {/* Preset Pathways */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 11, color: PALETTE.textDim, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Clinical Presets:
          </span>
          {PRESET_PATHWAYS.map(p => {
            const isActive = sourceId === p.source && targetId === p.target
            return (
              <button
                key={p.label}
                onClick={() => handleSelectPreset(p)}
                style={{
                  fontSize: 11, fontWeight: 600,
                  padding: '4px 10px', borderRadius: 6,
                  background: isActive ? PALETTE.accentGlow : 'rgba(255, 255, 255, 0.03)',
                  color: isActive ? PALETTE.accent : PALETTE.textMuted,
                  border: `1px solid ${isActive ? PALETTE.accent : PALETTE.borderLight}`,
                  cursor: 'pointer', transition: 'all 0.15s ease'
                }}
              >
                {p.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Selectors */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr auto 1fr',
        alignItems: 'center', gap: 12,
        background: 'rgba(0, 0, 0, 0.25)', padding: '12px 16px', borderRadius: 10,
        border: `1px solid ${PALETTE.borderLight}`
      }}>
        {/* Source Selector */}
        <div>
          <label style={{ display: 'block', fontSize: 10.5, fontWeight: 700, color: PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 4 }}>
            Upstream Driver (Source)
          </label>
          <select
            value={sourceId}
            onChange={e => setSourceId(e.target.value)}
            style={{
              width: '100%', background: PALETTE.surface, color: PALETTE.text,
              border: `1px solid ${PALETTE.border}`, borderRadius: 6,
              padding: '6px 10px', fontSize: 13, fontWeight: 500, outline: 'none'
            }}
          >
            {entities.map(e => (
              <option key={`src-${e.id}`} value={e.id}>
                [{e.entity_type}] {e.name}
              </option>
            ))}
          </select>
        </div>

        {/* Transition Arrow */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: PALETTE.accent, marginTop: 14 }}>
          <ArrowRight size={20} />
        </div>

        {/* Target Selector */}
        <div>
          <label style={{ display: 'block', fontSize: 10.5, fontWeight: 700, color: PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 4 }}>
            Clinical Manifestation (Target)
          </label>
          <select
            value={targetId}
            onChange={e => setTargetId(e.target.value)}
            style={{
              width: '100%', background: PALETTE.surface, color: PALETTE.text,
              border: `1px solid ${PALETTE.border}`, borderRadius: 6,
              padding: '6px 10px', fontSize: 13, fontWeight: 500, outline: 'none'
            }}
          >
            {entities.map(e => (
              <option key={`tgt-${e.id}`} value={e.id}>
                [{e.entity_type}] {e.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Path Results */}
      {loading && (
        <div style={{ padding: 24, textAlign: 'center', color: PALETTE.textMuted, fontSize: 13 }}>
          Computing shortest biochemical causal trajectory...
        </div>
      )}

      {error && (
        <div style={{
          padding: 12, borderRadius: 8, background: 'rgba(255, 77, 77, 0.1)',
          border: '1px solid rgba(255, 77, 77, 0.3)', color: '#FF7B72', fontSize: 12.5,
          display: 'flex', alignItems: 'center', gap: 8
        }}>
          <AlertCircle size={16} /> {error}
        </div>
      )}

      {!loading && pathData && pathData.exists && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Pathway Header Metrics */}
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            background: 'rgba(88, 166, 255, 0.05)', padding: '10px 14px', borderRadius: 8,
            border: '1px solid rgba(88, 166, 255, 0.2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <CheckCircle2 size={16} color="#3FB950" />
              <span style={{ fontSize: 13, fontWeight: 600, color: PALETTE.text }}>
                Causal Path Established: <strong style={{ color: PALETTE.accent }}>{pathData.path_length} Hops</strong>
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              {pathData.node_sequence.map((n, i) => (
                <React.Fragment key={n}>
                  <span style={{
                    fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 4,
                    background: PALETTE.surface, border: `1px solid ${PALETTE.borderLight}`
                  }}>
                    {n.replace(/^(NUTRIENT_|SYMPTOM_|LIFESTYLE_|CONDITION_|LAB_|SYSTEM_|FOOD_)/, '')}
                  </span>
                  {i < pathData.node_sequence.length - 1 && (
                    <ChevronRight size={13} color={PALETTE.textDim} />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Sequential Hops */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {pathData.hops.map((hop, idx) => {
              const relStyle = REL_BADGE_COLORS[hop.relationship_type] || {
                bg: 'rgba(255, 255, 255, 0.05)',
                text: PALETTE.text,
                border: PALETTE.borderLight
              }

              return (
                <motion.div
                  key={`hop-${hop.step}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.08 }}
                  style={{
                    display: 'flex', flexDirection: 'column', gap: 8,
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: `1px solid ${PALETTE.borderLight}`,
                    borderRadius: 10, padding: '12px 16px'
                  }}
                >
                  {/* Step Header */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{
                        width: 20, height: 20, borderRadius: 10,
                        background: PALETTE.accentGlow, color: PALETTE.accent,
                        fontSize: 10.5, fontWeight: 800, display: 'flex',
                        alignItems: 'center', justifyContent: 'center'
                      }}>
                        {hop.step}
                      </span>
                      <span style={{ fontSize: 13, fontWeight: 700, color: PALETTE.text }}>
                        {hop.source_name}
                      </span>
                      <span style={{
                        fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                        padding: '2px 6px', borderRadius: 4,
                        background: relStyle.bg, color: relStyle.text, border: `1px solid ${relStyle.border}`
                      }}>
                        {hop.relationship_type}
                      </span>
                      <ChevronRight size={14} color={PALETTE.textMuted} />
                      <span style={{ fontSize: 13, fontWeight: 700, color: PALETTE.accent }}>
                        {hop.target_name}
                      </span>
                    </div>

                    <span style={{ fontSize: 10.5, color: PALETTE.textDim, fontWeight: 600 }}>
                      [{hop.source_type} ➔ {hop.target_type}]
                    </span>
                  </div>

                  {/* Mechanism Details */}
                  <div style={{ fontSize: 12.5, color: '#C9D1D9', lineHeight: 1.5, paddingLeft: 28 }}>
                    {hop.mechanism}
                  </div>

                  {/* Clinical Citation */}
                  {hop.citation && (
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: 6,
                      fontSize: 11, color: PALETTE.textDim, fontStyle: 'italic', paddingLeft: 28
                    }}>
                      <BookOpen size={12} color={PALETTE.textDim} />
                      <span>{hop.citation}</span>
                    </div>
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>
      )}

      {!loading && pathData && !pathData.exists && (
        <div style={{
          padding: 16, textAlign: 'center', color: PALETTE.textMuted,
          fontSize: 13, background: 'rgba(255, 255, 255, 0.02)', borderRadius: 8
        }}>
          {pathData.clinical_summary}
        </div>
      )}
    </div>
  )
}
