/* ═══════════════════════════════════════════════════════════════════════════
   NetworkToolbar.tsx — Phase 6.1 Enhanced Toolbar
   Multi-field search · Quick actions · Export · Fullscreen
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState, useRef, useEffect, useCallback, useMemo, memo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, X, Command, Maximize, Crosshair, Download, Image, RotateCcw,
  AlertTriangle, Utensils, Activity,
} from 'lucide-react'
import {
  PALETTE, RISK_COLORS, searchNodesRich, getAggregateStats, getFilteredNetworkData,
  type NutrientNode, type RiskLevel, type SearchResult,
} from './NetworkData'

/* ═══════════════════════════════════════════════════════════════════════════
   COMMAND PALETTE — Multi-Field Search
   ═══════════════════════════════════════════════════════════════════════════ */

export function CommandPalette({ isOpen, onClose, onSelect }: {
  isOpen: boolean
  onClose: () => void
  onSelect: (node: NutrientNode) => void
}) {
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const results = searchNodesRich(query)

  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  const [activeIndex, setActiveIndex] = useState(0)
  useEffect(() => setActiveIndex(0), [query])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIndex(i => Math.min(i + 1, results.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIndex(i => Math.max(i - 1, 0))
    } else if (e.key === 'Enter' && results[activeIndex]) {
      onSelect(results[activeIndex].node)
      onClose()
    } else if (e.key === 'Escape') {
      onClose()
    }
  }, [results, activeIndex, onSelect, onClose])

  if (!isOpen) return null

  const matchIcon = (type: SearchResult['matchType']) => {
    switch (type) {
      case 'symptom': return <AlertTriangle size={9} color={RISK_COLORS.MODERATE.primary} />
      case 'food': return <Utensils size={9} color={RISK_COLORS.LOW.primary} />
      case 'system': return <Activity size={9} color={PALETTE.accent} />
      default: return null
    }
  }

  const matchLabel = (r: SearchResult) => {
    if (r.matchType === 'name') return r.node.bodySystem
    return r.matchText
  }

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        transition={{ duration: 0.12 }}
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0, zIndex: 100,
          background: 'rgba(0,0,0,0.5)',
          backdropFilter: 'blur(4px)',
        }}
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, y: -20, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.98 }}
        transition={{ duration: 0.15, ease: 'easeOut' }}
        style={{
          position: 'fixed', top: '16%', left: '50%', transform: 'translateX(-50%)',
          zIndex: 101, width: 520, maxWidth: '90vw',
          background: PALETTE.surface,
          border: `1px solid ${PALETTE.border}`,
          borderRadius: 16,
          boxShadow: '0 24px 80px rgba(0,0,0,0.5)',
          overflow: 'hidden',
        }}
      >
        {/* Search Input */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '14px 18px',
          borderBottom: `1px solid ${PALETTE.border}`,
        }}>
          <Search size={16} color={PALETTE.textMuted} />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search nutrients, symptoms, foods..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{
              flex: 1, background: 'none', border: 'none', outline: 'none',
              fontSize: 14, color: PALETTE.text,
              fontFamily: 'Inter, system-ui, sans-serif',
            }}
          />
          <div style={{
            display: 'flex', alignItems: 'center', gap: 4,
            padding: '2px 8px', borderRadius: 5,
            background: PALETTE.card, border: `1px solid ${PALETTE.border}`,
            fontSize: 10, color: PALETTE.textDim, fontWeight: 600,
          }}>ESC</div>
        </div>

        {/* Results */}
        <div style={{ maxHeight: 360, overflowY: 'auto', padding: '6px 0' }}>
          {query && results.length === 0 && (
            <div style={{ padding: '20px 18px', textAlign: 'center', color: PALETTE.textDim, fontSize: 13 }}>
              No results for "{query}"
            </div>
          )}
          {results.map((r, i) => {
            const riskC = RISK_COLORS[r.node.risk]
            return (
              <div
                key={`${r.node.id}-${r.matchType}`}
                onClick={() => { onSelect(r.node); onClose() }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '10px 18px', cursor: 'pointer',
                  background: i === activeIndex ? PALETTE.card : 'transparent',
                  transition: 'background 0.1s',
                }}
                onMouseEnter={() => setActiveIndex(i)}
              >
                <div style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: riskC.bg, border: `1px solid ${riskC.primary}30`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 16,
                }}>{r.node.icon}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: PALETTE.text }}>{r.node.label}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10.5, color: PALETTE.textMuted }}>
                    {matchIcon(r.matchType)}
                    <span style={{
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                      maxWidth: 240,
                    }}>{matchLabel(r)}</span>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
                  <span style={{
                    fontSize: 11, fontWeight: 700, color: riskC.primary,
                    fontFamily: '"Inter Tight", Inter, sans-serif',
                  }}>{Math.round(r.node.probability * 100)}%</span>
                  <span style={{
                    fontSize: 8.5, fontWeight: 700, color: riskC.primary,
                    background: riskC.bg, padding: '2px 6px',
                    borderRadius: 3, textTransform: 'uppercase',
                  }}>{r.node.risk}</span>
                </div>
              </div>
            )
          })}
          {!query && (
            <div style={{ padding: '16px 18px', color: PALETTE.textDim, fontSize: 12 }}>
              <div style={{ textAlign: 'center', marginBottom: 8 }}>Search across nutrients, symptoms, and foods</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, justifyContent: 'center' }}>
                {['fatigue', 'spinach', 'iron', 'bone', 'thyroid'].map(ex => (
                  <button key={ex} onClick={() => setQuery(ex)} style={{
                    padding: '3px 10px', borderRadius: 5, fontSize: 10.5, fontWeight: 500,
                    background: PALETTE.card, border: `1px solid ${PALETTE.border}`,
                    color: PALETTE.textMuted, cursor: 'pointer',
                  }}>"{ex}"</button>
                ))}
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   TOP CONTROLS SECTION (Row 1: Intelligence, Search, Filters · Row 2: Tabs)
   ═══════════════════════════════════════════════════════════════════════════ */

export interface NetworkTopControlsProps {
  workspaceMode: 'biochemical' | 'knowledge'
  onWorkspaceModeChange: (mode: 'biochemical' | 'knowledge') => void
  onOpenSearch: () => void
  riskFilter: RiskLevel | null
  onRiskFilterChange: (risk: RiskLevel | null) => void
}

function NetworkToolbarInner({
  workspaceMode,
  onWorkspaceModeChange,
  onOpenSearch,
  riskFilter,
  onRiskFilterChange,
}: NetworkTopControlsProps) {
  const filteredData = useMemo(() => getFilteredNetworkData(riskFilter), [riskFilter])
  const stats = useMemo(
    () => getAggregateStats(filteredData.visibleNodes, filteredData.visibleEdges),
    [filteredData]
  )

  const riskFilters = [
    { value: null, label: 'All', color: '#19D3C5', activeBg: 'rgba(25, 211, 197, 0.12)', borderColor: 'rgba(25, 211, 197, 0.4)' },
    { value: 'HIGH' as RiskLevel, label: 'High', color: '#FF4D4D', activeBg: 'rgba(255, 77, 77, 0.12)', borderColor: 'rgba(255, 77, 77, 0.4)' },
    { value: 'MODERATE' as RiskLevel, label: 'Moderate', color: '#FFB020', activeBg: 'rgba(255, 176, 32, 0.12)', borderColor: 'rgba(255, 176, 32, 0.4)' },
    { value: 'LOW' as RiskLevel, label: 'Low', color: '#00D68F', activeBg: 'rgba(0, 214, 143, 0.12)', borderColor: 'rgba(0, 214, 143, 0.4)' },
  ]

  return (
    <header
      style={{
        width: '100%',
        padding: '14px 24px 12px 24px',
        background: 'rgba(6, 17, 31, 0.95)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        zIndex: 30,
        display: 'flex',
        flexDirection: 'column',
        gap: '16px', // 16px vertical spacing between row 1 and row 2
        flexShrink: 0,
        boxSizing: 'border-box',
      }}
    >
      {/* ── ROW 1: Left Intelligence Card · Center Search · Right Filters ── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '24px', // Minimum 24px gap between major sections
          width: '100%',
        }}
      >
        {/* Left: Intelligence Summary Card */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            background: '#0D1B2A',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
            padding: '6px 14px',
            gap: '14px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.25)',
            flexShrink: 0,
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              paddingRight: '12px',
              borderRight: '1px solid rgba(255, 255, 255, 0.08)',
            }}
          >
            <Activity size={13} style={{ color: '#19D3C5' }} />
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                letterSpacing: '0.06em',
                color: '#94A3B8',
                textTransform: 'uppercase',
                fontFamily: '"Inter Tight", Inter, sans-serif',
              }}
            >
              Intelligence
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
              <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>Nutrients:</span>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: '#E2E8F0',
                  fontFamily: '"Inter Tight", Inter, monospace',
                }}
              >
                {stats.totalNutrients}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
              <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>High Risk:</span>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: '#FF4D4D',
                  fontFamily: '"Inter Tight", Inter, monospace',
                }}
              >
                {stats.highRiskCount}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
              <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>Avg Risk:</span>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: '#FFB020',
                  fontFamily: '"Inter Tight", Inter, monospace',
                }}
              >
                {stats.avgRisk}%
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
              <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>Links:</span>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: '#19D3C5',
                  fontFamily: '"Inter Tight", Inter, monospace',
                }}
              >
                {stats.totalInteractions}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
              <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>Cascades:</span>
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: '#F59E0B',
                  fontFamily: '"Inter Tight", Inter, monospace',
                }}
              >
                {stats.criticalCascades}
              </span>
            </div>
          </div>
        </div>

        {/* Center: Large Search Bar occupying most available width */}
        <div
          onClick={onOpenSearch}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              onOpenSearch()
            }
          }}
          style={{
            flex: 1,
            minWidth: '280px',
            maxWidth: '740px',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '0 14px',
            background: '#0D1B2A',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.25)',
            outline: 'none',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'rgba(25, 211, 197, 0.35)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)'
          }}
        >
          <Search size={14} style={{ color: '#19D3C5', flexShrink: 0 }} />
          <span
            style={{
              flex: 1,
              fontSize: '12px',
              color: '#64748B',
              fontFamily: 'Inter, system-ui, sans-serif',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              userSelect: 'none',
            }}
          >
            Search nutrients, biomarkers, pathways, symptoms...
          </span>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '2px',
              padding: '2px 6px',
              borderRadius: '4px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              fontSize: '10px',
              fontWeight: 600,
              color: '#94A3B8',
              flexShrink: 0,
            }}
          >
            <Command size={10} />K
          </div>
        </div>

        {/* Right: Filter Pills */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 4px',
            borderRadius: '8px',
            background: '#0D1B2A',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.25)',
            flexShrink: 0,
          }}
        >
          {riskFilters.map(f => {
            const isSelected = riskFilter === f.value
            return (
              <button
                key={f.label}
                type="button"
                onClick={() => onRiskFilterChange(f.value)}
                style={{
                  padding: '5px 13px',
                  borderRadius: '6px',
                  fontSize: '11.5px',
                  fontWeight: 600,
                  background: isSelected ? f.activeBg : 'transparent',
                  color: isSelected ? f.color : '#94A3B8',
                  border: isSelected ? `1px solid ${f.borderColor}` : '1px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  fontFamily: '"Inter Tight", Inter, sans-serif',
                  whiteSpace: 'nowrap',
                }}
              >
                {f.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* ── ROW 2: Dedicated Segmented Control (Centered above network graph) ── */}
      <div
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center', // Centered above network graph
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            background: '#0D1B2A',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '8px',
            padding: '3px 4px',
            gap: '6px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.3)',
          }}
        >
          {/* Biochemical Interactions Tab */}
          <button
            type="button"
            onClick={() => onWorkspaceModeChange('biochemical')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '7px',
              padding: '6px 18px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              fontFamily: 'Inter, system-ui, sans-serif',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              background: workspaceMode === 'biochemical' ? 'rgba(25, 211, 197, 0.12)' : 'rgba(13, 27, 42, 0.6)',
              color: workspaceMode === 'biochemical' ? '#19D3C5' : '#94A3B8',
              border: workspaceMode === 'biochemical' ? '1px solid #19D3C5' : '1px solid rgba(255, 255, 255, 0.08)',
              boxShadow: workspaceMode === 'biochemical'
                ? '0 0 14px rgba(25, 211, 197, 0.22), inset 0 1px 0 rgba(25, 211, 197, 0.2)'
                : 'none',
            }}
          >
            <span style={{ fontSize: '13px' }}>⚛️</span>
            <span>Biochemical Interactions</span>
          </button>

          {/* Clinical Knowledge Graph Tab */}
          <button
            type="button"
            onClick={() => onWorkspaceModeChange('knowledge')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '7px',
              padding: '6px 18px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              fontFamily: 'Inter, system-ui, sans-serif',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              background: workspaceMode === 'knowledge' ? 'rgba(25, 211, 197, 0.12)' : 'rgba(13, 27, 42, 0.6)',
              color: workspaceMode === 'knowledge' ? '#19D3C5' : '#94A3B8',
              border: workspaceMode === 'knowledge' ? '1px solid #19D3C5' : '1px solid rgba(255, 255, 255, 0.08)',
              boxShadow: workspaceMode === 'knowledge'
                ? '0 0 14px rgba(25, 211, 197, 0.22), inset 0 1px 0 rgba(25, 211, 197, 0.2)'
                : 'none',
            }}
          >
            <span style={{ fontSize: '13px' }}>🧠</span>
            <span>Clinical Knowledge Graph</span>
          </button>
        </div>
      </div>
    </header>
  )
}

export const NetworkToolbar = memo(NetworkToolbarInner)

/* ═══════════════════════════════════════════════════════════════════════════
   GRAPH CONTROLS (Bottom Right: Quick Actions)
   ═══════════════════════════════════════════════════════════════════════════ */

function GraphControlsInner() {
  const handleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.()
    } else {
      document.exitFullscreen?.()
    }
  }, [])

  const handleExportPNG = useCallback(() => {
    const svg = document.querySelector('.nodes')?.closest('svg')
    if (!svg) return
    const serializer = new XMLSerializer()
    const svgStr = serializer.serializeToString(svg)
    const canvas = document.createElement('canvas')
    const rect = svg.getBoundingClientRect()
    const dpr = 2
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    const ctx = canvas.getContext('2d')!
    ctx.scale(dpr, dpr)
    const img = new window.Image()
    img.onload = () => {
      ctx.fillStyle = PALETTE.bg
      ctx.fillRect(0, 0, rect.width, rect.height)
      ctx.drawImage(img, 0, 0, rect.width, rect.height)
      const link = document.createElement('a')
      link.download = 'nutrient-network.png'
      link.href = canvas.toDataURL('image/png')
      link.click()
    }
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgStr)
  }, [])

  const handleExportSVG = useCallback(() => {
    const svg = document.querySelector('.nodes')?.closest('svg')
    if (!svg) return
    const serializer = new XMLSerializer()
    const svgStr = serializer.serializeToString(svg)
    const blob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' })
    const link = document.createElement('a')
    link.download = 'nutrient-network.svg'
    link.href = URL.createObjectURL(blob)
    link.click()
    URL.revokeObjectURL(link.href)
  }, [])

  const actions = [
    { icon: <Maximize size={13} />, tooltip: 'Fullscreen', onClick: handleFullscreen },
    { icon: <Crosshair size={13} />, tooltip: 'Center & fit network (85% viewport)', onClick: () => window.dispatchEvent(new CustomEvent('nutriscan:center-graph')) },
    { icon: <Image size={13} />, tooltip: 'Export PNG', onClick: handleExportPNG },
    { icon: <Download size={13} />, tooltip: 'Export SVG', onClick: handleExportSVG },
  ]

  return (
    <div style={{
      position: 'absolute', bottom: 16, right: 16, zIndex: 15,
      display: 'flex', flexDirection: 'column', gap: 2,
      padding: 4, borderRadius: 10,
      background: PALETTE.frostedBg,
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      border: `1px solid ${PALETTE.frostedBorder}`,
    }}>
      {actions.map(a => (
        <button
          key={a.tooltip}
          title={a.tooltip}
          onClick={a.onClick}
          style={{
            width: 32, height: 32, borderRadius: 7,
            background: 'transparent', border: 'none',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', color: PALETTE.textMuted,
            transition: 'all 0.15s ease',
          }}
        >{a.icon}</button>
      ))}
    </div>
  )
}

export const GraphControls = memo(GraphControlsInner)
