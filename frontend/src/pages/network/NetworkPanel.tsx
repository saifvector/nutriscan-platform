/* ═══════════════════════════════════════════════════════════════════════════
   NetworkPanel.tsx — Phase 6.1 Bloomberg-style Panels + Cascade Explorer
   Frosted-glass hover cards · Tabbed detail panel · Cascade path explorer
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState, useMemo, memo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, AlertTriangle, ShieldCheck, Utensils, Activity, Zap, TrendingUp,
  ArrowRightLeft, Sparkles, Eye, ChevronRight, Heart, Brain, GitBranch,
} from 'lucide-react'
import {
  NODES, EDGES, PALETTE, RISK_COLORS, EDGE_COLORS,
  getNodeEdges, getEdgePartner, getCascadeChains,
  type NutrientNode, type NutrientEdge,
} from './NetworkData'

/* ═══════════════════════════════════════════════════════════════════════════
   BLOOMBERG-STYLE HOVER CARD (Frosted Glass)
   ═══════════════════════════════════════════════════════════════════════════ */

function HoverCardInner({ node, position }: {
  node: NutrientNode
  position: { x: number; y: number }
}) {
  const riskC = RISK_COLORS[node.risk]
  const connectedCount = EDGES.filter(e => e.source === node.id || e.target === node.id).length

  // Clamp position to viewport
  const x = Math.min(position.x + 16, window.innerWidth - 310)
  const y = Math.min(position.y - 20, window.innerHeight - 260)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.92, y: 6 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 4 }}
      transition={{ duration: 0.15, ease: 'easeOut' }}
      style={{
        position: 'fixed', left: x, top: y, zIndex: 50,
        width: 280, padding: 16, borderRadius: 14,
        background: PALETTE.frostedBg,
        backdropFilter: 'blur(16px) saturate(180%)',
        WebkitBackdropFilter: 'blur(16px) saturate(180%)',
        border: `1px solid ${PALETTE.frostedBorder}`,
        boxShadow: '0 8px 32px rgba(0,0,0,0.4), 0 0 1px rgba(255,255,255,0.1)',
        pointerEvents: 'none',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: riskC.bg,
          border: `1.5px solid ${riskC.primary}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 18,
        }}>{node.icon}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: PALETTE.text, fontFamily: '"Inter Tight", Inter, sans-serif', letterSpacing: '-0.01em' }}>{node.label}</div>
          <div style={{ fontSize: 10.5, color: PALETTE.textMuted }}>{node.bodySystem}</div>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 12 }}>
        <MetricPill label="Risk" value={`${Math.round(node.probability * 100)}%`} color={riskC.primary} />
        <MetricPill label="Confidence" value={`${Math.round(node.confidence * 100)}%`} color={PALETTE.accent} />
        <MetricPill label="Links" value={`${connectedCount}`} color={PALETTE.textMuted} />
      </div>

      {/* Mini Risk Gauge */}
      <div style={{ marginBottom: 10 }}>
        <div style={{
          height: 4, borderRadius: 2, background: 'rgba(48, 54, 61, 0.5)',
          overflow: 'hidden', position: 'relative',
        }}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${node.probability * 100}%` }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            style={{
              height: '100%', borderRadius: 2,
              background: `linear-gradient(90deg, ${riskC.primary}, ${riskC.secondary})`,
            }}
          />
        </div>
      </div>

      {/* Top 2 Symptoms */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginBottom: 10 }}>
        {node.symptoms.slice(0, 2).map(s => (
          <div key={s} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 3, height: 3, borderRadius: 2, background: riskC.primary, flexShrink: 0 }} />
            <span style={{ fontSize: 10.5, color: PALETTE.textMuted, lineHeight: 1.3 }}>{s}</span>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: PALETTE.accent, fontSize: 10.5, fontWeight: 600 }}>
        <span>Click for details</span>
        <ChevronRight size={11} />
      </div>
    </motion.div>
  )
}

function MetricPill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{
      padding: '6px 0', textAlign: 'center', borderRadius: 8,
      background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(48,54,61,0.3)',
    }}>
      <div style={{ fontSize: 9, color: PALETTE.textDim, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 800, color, fontFamily: '"Inter Tight", Inter, sans-serif' }}>{value}</div>
    </div>
  )
}

export const HoverCard = memo(HoverCardInner)

/* ═══════════════════════════════════════════════════════════════════════════
   FULL DETAIL PANEL (Slide-Out, Tabbed)
   ═══════════════════════════════════════════════════════════════════════════ */

type DetailTab = 'overview' | 'symptoms' | 'foods' | 'connections'

function NodeDetailPanelInner({ node, onClose }: {
  node: NutrientNode
  onClose: () => void
}) {
  const [tab, setTab] = useState<DetailTab>('overview')
  const riskC = RISK_COLORS[node.risk]
  const edges = getNodeEdges(node.id)

  const tabs: { key: DetailTab; label: string; icon: React.ReactNode }[] = [
    { key: 'overview', label: 'Overview', icon: <Activity size={12} /> },
    { key: 'symptoms', label: 'Symptoms', icon: <AlertTriangle size={12} /> },
    { key: 'foods', label: 'Foods', icon: <Utensils size={12} /> },
    { key: 'connections', label: 'Links', icon: <Brain size={12} /> },
  ]

  return (
    <motion.div
      initial={{ x: 420, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 420, opacity: 0 }}
      transition={{ type: 'spring', damping: 34, stiffness: 420, mass: 0.75 }}
      style={{
        position: 'absolute', top: 0, right: 0, bottom: 0, width: 400,
        background: PALETTE.surface,
        borderLeft: `1px solid ${PALETTE.border}`,
        overflowY: 'auto', zIndex: 20,
        boxShadow: '-8px 0 32px rgba(0,0,0,0.35)',
        display: 'flex', flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div style={{ padding: '20px 24px 0', flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 48, height: 48, borderRadius: 14,
              background: riskC.bg,
              border: `2px solid ${riskC.primary}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 24,
            }}>{node.icon}</div>
            <div>
              <h2 style={{
                fontFamily: '"Inter Tight", Inter, sans-serif', fontSize: '1.2rem',
                fontWeight: 800, color: PALETTE.text, letterSpacing: '-0.02em', margin: 0,
              }}>{node.label}</h2>
              <div style={{ fontSize: 11, color: PALETTE.textMuted }}>{node.bodySystem}</div>
            </div>
          </div>
          <button onClick={onClose} style={{
            width: 30, height: 30, borderRadius: 8,
            border: `1px solid ${PALETTE.border}`,
            background: PALETTE.card, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', color: PALETTE.textMuted,
          }}><X size={14} /></button>
        </div>

        {/* Risk + Confidence Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 16 }}>
          <div style={{ padding: '14px 16px', borderRadius: 12, background: riskC.bg, border: `1px solid ${riskC.primary}30` }}>
            <div style={{ fontSize: 10, fontWeight: 600, color: riskC.primary, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>Risk Score</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
              <span style={{ fontFamily: '"Inter Tight", Inter, sans-serif', fontSize: '1.6rem', fontWeight: 800, color: riskC.primary }}>{Math.round(node.probability * 100)}</span>
              <span style={{ fontSize: 13, fontWeight: 600, color: riskC.secondary }}>%</span>
            </div>
            {/* Animated gauge bar */}
            <div style={{ height: 3, borderRadius: 2, background: `${riskC.primary}20`, marginTop: 6, overflow: 'hidden' }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${node.probability * 100}%` }}
                transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
                style={{ height: '100%', borderRadius: 2, background: `linear-gradient(90deg, ${riskC.primary}, ${riskC.secondary})` }}
              />
            </div>
          </div>
          <div style={{ padding: '14px 16px', borderRadius: 12, background: `${PALETTE.accent}08`, border: `1px solid ${PALETTE.accent}20` }}>
            <div style={{ fontSize: 10, fontWeight: 600, color: PALETTE.accent, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>Confidence</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
              <span style={{ fontFamily: '"Inter Tight", Inter, sans-serif', fontSize: '1.6rem', fontWeight: 800, color: PALETTE.accent }}>{Math.round(node.confidence * 100)}</span>
              <span style={{ fontSize: 13, fontWeight: 600, color: `${PALETTE.accent}99` }}>%</span>
            </div>
            <div style={{ height: 3, borderRadius: 2, background: `${PALETTE.accent}15`, marginTop: 6, overflow: 'hidden' }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${node.confidence * 100}%` }}
                transition={{ duration: 0.6, delay: 0.3, ease: 'easeOut' }}
                style={{ height: '100%', borderRadius: 2, background: `linear-gradient(90deg, ${PALETTE.accent}, ${PALETTE.accent}CC)` }}
              />
            </div>
          </div>
        </div>

        {/* Tab Bar */}
        <div style={{ display: 'flex', gap: 2, borderBottom: `1px solid ${PALETTE.border}`, marginLeft: -24, marginRight: -24, paddingLeft: 24, paddingRight: 24 }}>
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              style={{
                display: 'flex', alignItems: 'center', gap: 5,
                padding: '8px 12px', fontSize: 11, fontWeight: 600,
                color: tab === t.key ? PALETTE.accent : PALETTE.textMuted,
                background: 'none', border: 'none', cursor: 'pointer',
                borderBottom: tab === t.key ? `2px solid ${PALETTE.accent}` : '2px solid transparent',
                transition: 'all 0.15s ease',
                fontFamily: '"Inter Tight", Inter, sans-serif',
              }}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px 24px' }}>
        <AnimatePresence mode="wait">
          {tab === 'overview' && <OverviewTab key="overview" node={node} />}
          {tab === 'symptoms' && <SymptomsTab key="symptoms" node={node} />}
          {tab === 'foods' && <FoodsTab key="foods" node={node} />}
          {tab === 'connections' && <ConnectionsTab key="connections" node={node} edges={edges} />}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

/* ─── Tab: Overview ─── */
function OverviewTab({ node }: { node: NutrientNode }) {
  const riskC = RISK_COLORS[node.risk]
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
    >
      {/* Influences */}
      <SectionHeader icon={<Zap size={12} />} label="Physiological Influences" color={PALETTE.accent} />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 18 }}>
        {node.influences.map(inf => (
          <span key={inf} style={{
            padding: '4px 10px', borderRadius: 6, fontSize: 10.5, fontWeight: 600,
            background: `${PALETTE.accent}0A`, border: `1px solid ${PALETTE.accent}20`,
            color: PALETTE.text,
          }}>{inf}</span>
        ))}
      </div>

      {/* Description */}
      <SectionHeader icon={<Heart size={12} />} label="Clinical Overview" color={RISK_COLORS.LOW.primary} />
      <p style={{ fontSize: 12.5, color: PALETTE.textMuted, lineHeight: 1.7, marginBottom: 18 }}>{node.description}</p>

      {/* Top Contributors */}
      <SectionHeader icon={<TrendingUp size={12} />} label="Top Risk Contributors" color={riskC.primary} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {node.topContributors.map(c => (
          <div key={c.name} style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '8px 12px', borderRadius: 8,
            background: PALETTE.card, border: `1px solid ${PALETTE.borderLight}`,
          }}>
            <div style={{
              width: 5, height: 5, borderRadius: 3, flexShrink: 0,
              background: c.direction === 'risk' ? RISK_COLORS.HIGH.primary : RISK_COLORS.LOW.primary,
            }} />
            <span style={{ fontSize: 12, fontWeight: 500, color: PALETTE.text, flex: 1 }}>{c.name}</span>
            <span style={{
              fontSize: 11, fontWeight: 700,
              color: c.direction === 'risk' ? RISK_COLORS.HIGH.primary : RISK_COLORS.LOW.primary,
            }}>
              {c.direction === 'risk' ? '+' : '−'}{c.impact}%
            </span>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

/* ─── Tab: Symptoms ─── */
function SymptomsTab({ node }: { node: NutrientNode }) {
  const riskC = RISK_COLORS[node.risk]
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
    >
      <SectionHeader icon={<AlertTriangle size={12} />} label="Deficiency Symptoms" color={RISK_COLORS.MODERATE.primary} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {node.symptoms.map((s, i) => (
          <motion.div
            key={s}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.06, duration: 0.2 }}
            style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 14px', borderRadius: 10,
              background: PALETTE.card, border: `1px solid ${PALETTE.borderLight}`,
            }}
          >
            <div style={{
              width: 24, height: 24, borderRadius: 7,
              background: `${riskC.primary}12`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <AlertTriangle size={12} color={riskC.primary} />
            </div>
            <span style={{ fontSize: 12.5, color: PALETTE.text, lineHeight: 1.4 }}>{s}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

/* ─── Tab: Foods ─── */
function FoodsTab({ node }: { node: NutrientNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
    >
      <SectionHeader icon={<Utensils size={12} />} label="Recommended Foods" color={RISK_COLORS.LOW.primary} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {node.foods.map((f, i) => (
          <motion.div
            key={f}
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.06, duration: 0.2 }}
            style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 14px', borderRadius: 10,
              background: PALETTE.card, border: `1px solid ${PALETTE.borderLight}`,
            }}
          >
            <div style={{
              width: 24, height: 24, borderRadius: 7,
              background: `${RISK_COLORS.LOW.primary}12`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <ShieldCheck size={12} color={RISK_COLORS.LOW.primary} />
            </div>
            <span style={{ fontSize: 12.5, color: PALETTE.text, lineHeight: 1.4 }}>{f}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

/* ─── Tab: Connections + Cascade Explorer ─── */
function ConnectionsTab({ node, edges }: { node: NutrientNode; edges: NutrientEdge[] }) {
  const cascades = useMemo(() => getCascadeChains(node.id), [node.id])

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
    >
      {/* ── Cascade Path Explorer ── */}
      {cascades.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <SectionHeader icon={<GitBranch size={12} />} label="Deficiency Cascade Pathways" color={RISK_COLORS.MODERATE.primary} />
          <div style={{
            padding: 14, borderRadius: 12,
            background: `${RISK_COLORS.MODERATE.primary}06`,
            border: `1px solid ${RISK_COLORS.MODERATE.primary}15`,
          }}>
            {cascades.map((chain, ci) => (
              <div key={ci} style={{ marginBottom: ci < cascades.length - 1 ? 14 : 0 }}>
                {/* Start node */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <div style={{
                    width: 24, height: 24, borderRadius: 7,
                    background: RISK_COLORS[node.risk].bg,
                    border: `1px solid ${RISK_COLORS[node.risk].primary}30`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 12,
                  }}>{node.icon}</div>
                  <span style={{ fontSize: 11.5, fontWeight: 700, color: PALETTE.text }}>{node.label}</span>
                </div>

                {/* Chain steps */}
                {chain.map((step, si) => (
                  <motion.div
                    key={step.nodeId}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: ci * 0.1 + si * 0.12, duration: 0.25 }}
                  >
                    {/* Arrow connector */}
                    <div style={{ display: 'flex', alignItems: 'stretch', gap: 0, marginLeft: 11 }}>
                      <div style={{
                        width: 2, minHeight: 20,
                        background: `linear-gradient(180deg, ${RISK_COLORS.MODERATE.primary}40, ${RISK_COLORS.MODERATE.primary}15)`,
                      }} />
                      <div style={{
                        marginLeft: 10, padding: '3px 0',
                        fontSize: 9.5, color: RISK_COLORS.MODERATE.primary, fontWeight: 600,
                        fontStyle: 'italic',
                      }}>{step.edgeLabel}</div>
                    </div>

                    {/* Step node */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 0 }}>
                      <div style={{
                        width: 6, height: 6, borderRadius: 3,
                        background: RISK_COLORS.MODERATE.primary,
                        border: `2px solid ${PALETTE.bg}`,
                        marginLeft: 8,
                      }} />
                      <span style={{ fontSize: 13 }}>{step.icon}</span>
                      <span style={{ fontSize: 11.5, fontWeight: 600, color: PALETTE.text }}>{step.label}</span>
                    </div>
                  </motion.div>
                ))}

                {ci < cascades.length - 1 && (
                  <div style={{ height: 1, background: PALETTE.border, margin: '10px 0', opacity: 0.4 }} />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Connected Nutrients ── */}
      <SectionHeader icon={<Activity size={12} />} label="Connected Nutrients" color={PALETTE.accent} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {edges.map((edge, i) => {
          const partner = getEdgePartner(edge, node.id)
          if (!partner) return null
          const edgeC = EDGE_COLORS[edge.type]
          return (
            <motion.div
              key={edge.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06, duration: 0.2 }}
              style={{
                padding: 14, borderRadius: 12,
                background: PALETTE.card, border: `1px solid ${PALETTE.borderLight}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 16 }}>{partner.icon}</span>
                  <div>
                    <div style={{ fontSize: 12.5, fontWeight: 600, color: PALETTE.text }}>{partner.label}</div>
                    <div style={{ fontSize: 10, color: PALETTE.textMuted }}>{edge.label}</div>
                  </div>
                </div>
                <span style={{
                  fontSize: 9, fontWeight: 700, color: edgeC.stroke,
                  background: `${edgeC.stroke}15`, padding: '3px 8px',
                  borderRadius: 4, textTransform: 'uppercase', letterSpacing: '0.04em',
                }}>{edge.type}</span>
              </div>
              {/* Trace Impact */}
              <div style={{
                padding: '8px 10px', borderRadius: 8,
                background: `${PALETTE.accent}06`, border: `1px solid ${PALETTE.accent}15`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                  <Eye size={9} color={PALETTE.accent} />
                  <span style={{ fontSize: 9, fontWeight: 700, color: PALETTE.accent, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Trace Impact</span>
                </div>
                <p style={{ fontSize: 11, color: PALETTE.textMuted, lineHeight: 1.5, margin: 0 }}>{edge.traceImpact}</p>
              </div>
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}

export const NodeDetailPanel = memo(NodeDetailPanelInner)

/* ═══════════════════════════════════════════════════════════════════════════
   EDGE DETAIL PANEL
   ═══════════════════════════════════════════════════════════════════════════ */

function EdgeDetailPanelInner({ edge, onClose }: { edge: NutrientEdge; onClose: () => void }) {
  const sourceNode = NODES.find(n => n.id === (typeof edge.source === 'string' ? edge.source : (edge.source as NutrientNode).id))
  const targetNode = NODES.find(n => n.id === (typeof edge.target === 'string' ? edge.target : (edge.target as NutrientNode).id))
  const edgeC = EDGE_COLORS[edge.type]
  const typeLabel = edge.type === 'synergistic' ? 'Synergistic' : edge.type === 'supportive' ? 'Supportive' : 'Competitive'

  return (
    <motion.div
      initial={{ x: 420, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 420, opacity: 0 }}
      transition={{ type: 'spring', damping: 34, stiffness: 420, mass: 0.75 }}
      style={{
        position: 'absolute', top: 0, right: 0, bottom: 0, width: 400,
        background: PALETTE.surface,
        borderLeft: `1px solid ${PALETTE.border}`,
        overflowY: 'auto', zIndex: 20,
        boxShadow: '-8px 0 32px rgba(0,0,0,0.35)',
      }}
    >
      <div style={{ padding: 24 }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <span style={{ fontSize: 22 }}>{sourceNode?.icon}</span>
              <ArrowRightLeft size={16} color={edgeC.stroke} />
              <span style={{ fontSize: 22 }}>{targetNode?.icon}</span>
            </div>
            <h2 style={{
              fontFamily: '"Inter Tight", Inter, sans-serif', fontSize: '1.1rem',
              fontWeight: 800, color: PALETTE.text, letterSpacing: '-0.02em', margin: 0,
            }}>
              {sourceNode?.label} ↔ {targetNode?.label}
            </h2>
          </div>
          <button onClick={onClose} style={{
            width: 30, height: 30, borderRadius: 8,
            border: `1px solid ${PALETTE.border}`,
            background: PALETTE.card, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', color: PALETTE.textMuted,
          }}><X size={14} /></button>
        </div>

        {/* Type + Strength */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
          <span style={{
            fontSize: 10, fontWeight: 700, color: edgeC.stroke,
            background: `${edgeC.stroke}18`, padding: '5px 12px',
            borderRadius: 6, textTransform: 'uppercase', letterSpacing: '0.05em',
          }}>{typeLabel}</span>
          <span style={{ fontSize: 13, fontWeight: 700, color: PALETTE.text }}>{edge.label}</span>
          <span style={{ fontSize: 10.5, color: PALETTE.textDim, marginLeft: 'auto' }}>
            Strength: {Math.round(edge.strength * 100)}%
          </span>
        </div>

        {/* Biochemical Mechanism */}
        <SectionHeader icon={<Sparkles size={12} />} label="Biochemical Mechanism" color={PALETTE.accent} />
        <p style={{ fontSize: 12.5, color: PALETTE.textMuted, lineHeight: 1.7, marginBottom: 20 }}>{edge.explanation}</p>

        {/* Why This Matters */}
        <SectionHeader icon={<Zap size={12} />} label="Why This Matters" color={RISK_COLORS.MODERATE.primary} />
        <p style={{ fontSize: 12.5, color: PALETTE.textMuted, lineHeight: 1.7, marginBottom: 20 }}>{edge.importance}</p>

        {/* Trace Impact */}
        <div style={{
          padding: '14px 16px', borderRadius: 12,
          background: `${PALETTE.accent}06`, border: `1px solid ${PALETTE.accent}15`,
          marginBottom: 20,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <Eye size={12} color={PALETTE.accent} />
            <span style={{ fontSize: 10, fontWeight: 700, color: PALETTE.accent, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Trace Impact</span>
          </div>
          <p style={{ fontSize: 12.5, color: PALETTE.text, lineHeight: 1.6, margin: 0 }}>{edge.traceImpact}</p>
        </div>

        {/* Dietary Tip */}
        <div style={{
          padding: '14px 16px', borderRadius: 12,
          background: `${RISK_COLORS.LOW.primary}08`, border: `1px solid ${RISK_COLORS.LOW.primary}18`,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <Utensils size={12} color={RISK_COLORS.LOW.primary} />
            <span style={{ fontSize: 10, fontWeight: 700, color: RISK_COLORS.LOW.primary, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Dietary Recommendation</span>
          </div>
          <p style={{ fontSize: 12.5, color: PALETTE.text, lineHeight: 1.6, margin: 0 }}>{edge.dietaryTip}</p>
        </div>
      </div>
    </motion.div>
  )
}

export const EdgeDetailPanel = memo(EdgeDetailPanelInner)

/* ─── Shared Section Header ─── */
function SectionHeader({ icon, label, color }: { icon: React.ReactNode; label: string; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
      <div style={{ color }}>{icon}</div>
      <span style={{ fontSize: 10, fontWeight: 700, color, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</span>
    </div>
  )
}
