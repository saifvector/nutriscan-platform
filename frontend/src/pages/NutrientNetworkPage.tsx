/* ═══════════════════════════════════════════════════════════════════════════
   NutrientNetworkPage.tsx — Phase 6.1 Fullscreen Intelligence Workspace
   Immersive canvas · Floating controls · Diagnostics · Collapsible legend
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState, useEffect, useCallback, useRef, useMemo, memo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Info, ChevronDown, ChevronUp, Gauge, Network, PlusCircle, RotateCcw } from 'lucide-react'
import NetworkGraph from './network/NetworkGraph'
import { HoverCard, NodeDetailPanel, EdgeDetailPanel } from './network/NetworkPanel'
import { CommandPalette, NetworkToolbar, GraphControls } from './network/NetworkToolbar'
import KnowledgeGraphExplorer from './network/KnowledgeGraphExplorer'
import { PALETTE, RISK_COLORS, type NutrientNode, type NutrientEdge, type RiskLevel } from './network/NetworkData'
import { sessionManager } from '../lib/sessionManager'
import { ResumeAssessmentModal } from '../components/session/ResumeAssessmentModal'
import { AssessmentRequiredState } from '../components/common/AssessmentRequiredState'

export default function NutrientNetworkPage() {
  const navigate = useNavigate()
  const [activeSession, setActiveSession] = useState(() => sessionManager.getActiveSession())
  const [showResumeModal, setShowResumeModal] = useState(false)
  const storedPrevious = useMemo(() => sessionManager.getStoredPreviousAssessment(), [])

  /* ─── State ─── */
  const [selectedNode, setSelectedNode] = useState<NutrientNode | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<NutrientEdge | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [hoveredNode, setHoveredNode] = useState<NutrientNode | null>(null)
  const [hoverPos, setHoverPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 })
  const [searchOpen, setSearchOpen] = useState(false)
  const [riskFilter, setRiskFilter] = useState<RiskLevel | null>(null)
  const [showDiagnostics, setShowDiagnostics] = useState(false)
  const [workspaceMode, setWorkspaceMode] = useState<'biochemical' | 'knowledge'>('biochemical')

  /* ─── State Refs for Stable Callbacks ─── */
  const selectedIdRef = useRef<string | null>(null)
  selectedIdRef.current = selectedId
  const selectedNodeRef = useRef<NutrientNode | null>(null)
  selectedNodeRef.current = selectedNode

  /* ─── Handlers (Strictly Stable: Zero Dependency Invalidation) ─── */
  const handleNodeClick = useCallback((node: NutrientNode) => {
    setSelectedEdge(null)
    setHoveredNode(null)
    if (selectedIdRef.current === node.id) {
      setSelectedNode(null)
      setSelectedId(null)
    } else {
      setSelectedNode(node)
      setSelectedId(node.id)
    }
  }, [])

  const handleNodeHover = useCallback((node: NutrientNode | null, event?: MouseEvent) => {
    if (selectedNodeRef.current) return
    setHoveredNode(prev => (prev?.id === node?.id ? prev : node))
    if (node && event) {
      setHoverPos({ x: event.clientX, y: event.clientY })
    }
  }, [])

  const handleEdgeClick = useCallback((edge: NutrientEdge) => {
    setSelectedNode(null)
    setSelectedId(null)
    setHoveredNode(null)
    setSelectedEdge(edge)
  }, [])

  const handleClose = useCallback(() => {
    setSelectedNode(null)
    setSelectedEdge(null)
    setSelectedId(null)
  }, [])

  const handleSearchSelect = useCallback((node: NutrientNode) => {
    setSelectedEdge(null)
    setHoveredNode(null)
    setSelectedNode(node)
    setSelectedId(node.id)
  }, [])

  const handleOpenSearch = useCallback(() => setSearchOpen(true), [])

  /* ─── Keyboard Shortcuts ─── */
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (searchOpen) setSearchOpen(false)
        else handleClose()
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(prev => !prev)
      }
      // Ctrl+Shift+P → diagnostics
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        e.preventDefault()
        setShowDiagnostics(prev => !prev)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [searchOpen, handleClose])

  if (!activeSession?.active_assessment_id) {
    return (
      <>
        <AssessmentRequiredState
          title="Nutritional Assessment Required"
          description="The nutrient interaction graph requires an active assessment to project individual micronutrient interactions, absorption synergies, and metabolic competitions. Complete an assessment to explore your personalized metabolic network."
          actionLabel="Start Assessment"
          secondaryActionLabel={storedPrevious ? 'Resume Previous Assessment' : undefined}
          onSecondaryAction={storedPrevious ? () => setShowResumeModal(true) : undefined}
          icon={Network}
        />

        {storedPrevious && (
          <ResumeAssessmentModal
            isOpen={showResumeModal}
            assessmentId={storedPrevious.id}
            assessmentDate={storedPrevious.date}
            onResume={() => {
              sessionManager.setActiveSession(storedPrevious.id, storedPrevious.date, 'completed')
              setActiveSession(sessionManager.getActiveSession())
              setShowResumeModal(false)
            }}
            onStartNew={() => {
              sessionManager.clearActiveSession()
              setActiveSession(null)
              setShowResumeModal(false)
              navigate('/assessment')
            }}
          />
        )}
      </>
    )
  }

  return (
    <div style={{
      width: '100%',
      height: 'calc(100vh - 64px)',
      display: 'flex', flexDirection: 'column',
      background: PALETTE.bg,
      overflow: 'hidden',
      position: 'relative',
    }}>
      {/* ═══ REDESIGNED TOP CONTROL SECTION (ROW 1: Intelligence, Search, Filters · ROW 2: Tabs) ═══ */}
      <NetworkToolbar
        workspaceMode={workspaceMode}
        onWorkspaceModeChange={setWorkspaceMode}
        onOpenSearch={handleOpenSearch}
        riskFilter={riskFilter}
        onRiskFilterChange={setRiskFilter}
      />

      {workspaceMode === 'knowledge' ? (
        <div style={{ flex: 1, minHeight: 0, position: 'relative', overflow: 'hidden' }}>
          <KnowledgeGraphExplorer />
        </div>
      ) : (
        /* Full-bleed graph workspace — legend and quick actions overlay */
        <div style={{ flex: 1, minHeight: 0, position: 'relative', overflow: 'hidden' }}>
          {/* Graph Canvas (100% of space) */}
          <NetworkGraph
            selectedId={selectedId}
            hoveredId={hoveredNode?.id ?? null}
            onNodeClick={handleNodeClick}
            onNodeHover={handleNodeHover}
            onEdgeClick={handleEdgeClick}
          />

          {/* Quick Actions (bottom-right) */}
          <GraphControls />

          {/* Collapsible Legend (bottom-left) */}
          <CollapsibleLegend selectedId={selectedId} onClear={handleClose} />

          {/* Hint (bottom-center) */}
          <div style={{
            position: 'absolute', bottom: 12, left: '50%', transform: 'translateX(-50%)',
            zIndex: 5, padding: '5px 12px', borderRadius: 7,
            background: PALETTE.frostedBg,
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: `1px solid ${PALETTE.frostedBorder}`,
            fontSize: 10.5, color: PALETTE.textDim, fontWeight: 500,
            fontFamily: 'Inter, system-ui, sans-serif',
            whiteSpace: 'nowrap',
          }}>
            Scroll to zoom · Drag to rearrange · Double-click to fit · Esc to clear
          </div>

          {/* Hover Card */}
          <AnimatePresence>
            {hoveredNode && !selectedNode && (
              <HoverCard key={`hover-${hoveredNode.id}`} node={hoveredNode} position={hoverPos} />
            )}
          </AnimatePresence>

          {/* Detail Panels */}
          <AnimatePresence>
            {selectedNode && (
              <NodeDetailPanel key={`node-${selectedNode.id}`} node={selectedNode} onClose={handleClose} />
            )}
            {selectedEdge && (
              <EdgeDetailPanel key={`edge-${selectedEdge.id}`} edge={selectedEdge} onClose={handleClose} />
            )}
          </AnimatePresence>

          {/* Developer Diagnostics (Ctrl+Shift+P) */}
          <AnimatePresence>
            {showDiagnostics && <DiagnosticsPanel onClose={() => setShowDiagnostics(false)} />}
          </AnimatePresence>
        </div>
      )}

      {/* Command Palette */}
      <AnimatePresence>
        {searchOpen && (
          <CommandPalette
            isOpen={searchOpen}
            onClose={() => setSearchOpen(false)}
            onSelect={handleSearchSelect}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════
   COLLAPSIBLE LEGEND (Bottom Left)
   ═══════════════════════════════════════════════════════════════════════════ */

const CollapsibleLegend = memo(function CollapsibleLegend({
  selectedId, onClear,
}: {
  selectedId: string | null; onClear: () => void
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div style={{
      position: 'absolute', bottom: 12, left: 12, zIndex: 15,
    }}>
      {/* Selection indicator (always visible when selected) */}
      {selectedId && (
        <div style={{
          marginBottom: 4, padding: '4px 10px', borderRadius: 7,
          background: PALETTE.frostedBg,
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: `1px solid ${PALETTE.frostedBorder}`,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <div style={{
              width: 5, height: 5, borderRadius: 3, background: PALETTE.accent,
              animation: 'stats-pulse 1.5s infinite',
            }} />
            <span style={{ fontSize: 10, fontWeight: 700, color: PALETTE.accent }}>Node Selected</span>
          </div>
          <button onClick={onClear} style={{
            fontSize: 9, fontWeight: 600, color: PALETTE.textDim,
            background: PALETTE.card, border: `1px solid ${PALETTE.border}`,
            padding: '2px 7px', borderRadius: 4, cursor: 'pointer',
          }}>Clear</button>
        </div>
      )}

      {/* Collapsed pill / Expanded legend */}
      <button
        onClick={() => setExpanded(e => !e)}
        style={{
          display: 'flex', alignItems: 'center', gap: 5,
          padding: '5px 10px', borderRadius: 8, cursor: 'pointer',
          background: PALETTE.frostedBg,
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: `1px solid ${PALETTE.frostedBorder}`,
          color: PALETTE.textMuted, fontSize: 10, fontWeight: 600,
          fontFamily: '"Inter Tight", Inter, sans-serif',
        }}
      >
        <Info size={10} />
        Legend
        {expanded ? <ChevronDown size={10} /> : <ChevronUp size={10} />}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            style={{
              marginTop: 4, padding: '10px 14px', borderRadius: 10,
              background: PALETTE.frostedBg,
              backdropFilter: 'blur(16px)',
              WebkitBackdropFilter: 'blur(16px)',
              border: `1px solid ${PALETTE.frostedBorder}`,
              maxWidth: 200,
            }}
          >
            <div style={{ fontSize: 9, fontWeight: 700, color: PALETTE.textMuted, marginBottom: 5, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Interaction Types
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 3, marginBottom: 8 }}>
              {[
                { color: '#3FB950', label: 'Synergistic', desc: 'Enhances' },
                { color: '#D29922', label: 'Supportive', desc: 'Enables' },
                { color: '#F85149', label: 'Competitive', desc: 'Inhibits', dashed: true },
              ].map(item => (
                <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{
                    width: 14, height: 2, borderRadius: 1, flexShrink: 0,
                    background: item.dashed ? 'none' : item.color,
                    ...(item.dashed ? {
                      backgroundImage: `repeating-linear-gradient(90deg, ${item.color} 0px, ${item.color} 4px, transparent 4px, transparent 7px)`,
                    } as any : {}),
                  }} />
                  <span style={{ fontSize: 10, fontWeight: 600, color: PALETTE.text }}>{item.label}</span>
                  <span style={{ fontSize: 9, color: PALETTE.textDim }}>· {item.desc}</span>
                </div>
              ))}
            </div>

            <div style={{ fontSize: 9, fontWeight: 700, color: PALETTE.textMuted, marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Node Size = Risk
            </div>
            <div style={{ display: 'flex', gap: 6 }}>
              {[
                { c: '#FF4D4D', l: 'High', r: 7 },
                { c: '#FFB020', l: 'Med', r: 5 },
                { c: '#00D68F', l: 'Low', r: 4 },
              ].map(i => (
                <div key={i.l} style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                  <div style={{ width: i.r * 2, height: i.r * 2, borderRadius: i.r, border: `1.5px solid ${i.c}`, background: `${i.c}15` }} />
                  <span style={{ fontSize: 9.5, color: PALETTE.textDim, fontWeight: 500 }}>{i.l}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
})

/* ═══════════════════════════════════════════════════════════════════════════
   DEVELOPER DIAGNOSTICS PANEL (Ctrl+Shift+P)
   ═══════════════════════════════════════════════════════════════════════════ */

function DiagnosticsPanel({ onClose }: { onClose: () => void }) {
  const [fps, setFps] = useState(0)
  const [frameTime, setFrameTime] = useState(0)

  useEffect(() => {
    let frames = 0
    let lastTime = performance.now()
    let raf: number

    const tick = (now: number) => {
      frames++
      const delta = now - lastTime
      if (delta >= 1000) {
        setFps(Math.round((frames * 1000) / delta))
        setFrameTime(Math.round(delta / frames * 100) / 100)
        frames = 0
        lastTime = now
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  const metrics = [
    { label: 'FPS', value: `${fps}`, color: fps >= 55 ? '#3FB950' : fps >= 30 ? '#FFB020' : '#FF4D4D' },
    { label: 'Frame Time', value: `${frameTime}ms`, color: PALETTE.accent },
    { label: 'Nodes', value: '18', color: PALETTE.textMuted },
    { label: 'Edges', value: '15', color: PALETTE.textMuted },
    { label: 'Renderer', value: 'SVG+Canvas', color: PALETTE.textMuted },
    { label: 'Particles', value: 'Canvas 2D', color: PALETTE.textMuted },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.15 }}
      style={{
        position: 'absolute', top: 12, right: 12, zIndex: 30,
        padding: 12, borderRadius: 10, width: 180,
        background: 'rgba(6, 9, 15, 0.9)',
        backdropFilter: 'blur(12px)',
        border: `1px solid ${PALETTE.border}`,
        fontFamily: '"SF Mono", "Fira Code", monospace',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <Gauge size={11} color={PALETTE.accent} />
          <span style={{ fontSize: 9, fontWeight: 700, color: PALETTE.accent, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Diagnostics</span>
        </div>
        <button onClick={onClose} style={{
          fontSize: 9, color: PALETTE.textDim, background: 'none', border: 'none', cursor: 'pointer',
        }}>✕</button>
      </div>

      {metrics.map(m => (
        <div key={m.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
          <span style={{ fontSize: 9.5, color: PALETTE.textDim }}>{m.label}</span>
          <span style={{ fontSize: 9.5, fontWeight: 700, color: m.color }}>{m.value}</span>
        </div>
      ))}

      <div style={{ marginTop: 6, fontSize: 8.5, color: PALETTE.textDim, textAlign: 'center', opacity: 0.6 }}>
        Ctrl+Shift+P to toggle
      </div>
    </motion.div>
  )
}
