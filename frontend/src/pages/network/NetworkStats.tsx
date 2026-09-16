/* ═══════════════════════════════════════════════════════════════════════════
   NetworkStats.tsx — Phase 6.1 Floating Intelligence Pills
   Compact floating overlay · Collapsible · Glassmorphism
   ═══════════════════════════════════════════════════════════════════════════ */

import { useState, useMemo, memo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, AlertTriangle, TrendingUp, Zap, Link2, ChevronDown, ChevronUp } from 'lucide-react'
import { PALETTE, RISK_COLORS, getAggregateStats } from './NetworkData'

function NetworkStatsInner() {
  const stats = useMemo(() => getAggregateStats(), [])
  const [expanded, setExpanded] = useState(true)

  const items = [
    { icon: <Activity size={11} />, label: 'Nutrients', value: stats.totalNutrients.toString(), color: PALETTE.accent },
    { icon: <AlertTriangle size={11} />, label: 'High Risk', value: stats.highRiskCount.toString(), color: RISK_COLORS.HIGH.primary, pulse: true },
    { icon: <TrendingUp size={11} />, label: 'Avg Risk', value: `${stats.avgRisk}%`, color: stats.avgRisk > 50 ? RISK_COLORS.HIGH.primary : stats.avgRisk > 35 ? RISK_COLORS.MODERATE.primary : RISK_COLORS.LOW.primary },
    { icon: <Link2 size={11} />, label: 'Links', value: stats.totalInteractions.toString(), color: PALETTE.accent },
    { icon: <Zap size={11} />, label: 'Cascades', value: stats.criticalCascades.toString(), color: RISK_COLORS.MODERATE.primary },
  ]

  return (
    <div style={{
      position: 'absolute', top: 12, left: 12, zIndex: 15,
      display: 'flex', flexDirection: 'column', gap: 4,
    }}>
      {/* Toggle button */}
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
          textTransform: 'uppercase', letterSpacing: '0.06em',
          width: 'fit-content',
        }}
      >
        <Activity size={10} color={PALETTE.accent} />
        Intelligence
        {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
      </button>

      {/* Pills */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            style={{ display: 'flex', flexWrap: 'wrap', gap: 4, maxWidth: 320 }}
          >
            {items.map((item, i) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.03, duration: 0.15 }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 5,
                  padding: '4px 10px', borderRadius: 7,
                  background: PALETTE.frostedBg,
                  backdropFilter: 'blur(16px)',
                  WebkitBackdropFilter: 'blur(16px)',
                  border: `1px solid ${PALETTE.frostedBorder}`,
                }}
              >
                <div style={{ color: item.color, display: 'flex', alignItems: 'center' }}>{item.icon}</div>
                <span style={{ fontSize: 9.5, color: PALETTE.textDim, fontWeight: 500 }}>{item.label}</span>
                <span style={{
                  fontSize: 12, fontWeight: 800, color: item.color,
                  fontFamily: '"Inter Tight", Inter, sans-serif',
                }}>{item.value}</span>
                {item.pulse && (
                  <div style={{
                    width: 5, height: 5, borderRadius: 3, background: item.color,
                    animation: 'stats-pulse 1.5s ease-in-out infinite',
                  }} />
                )}
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @keyframes stats-pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(1.3); }
        }
      `}</style>
    </div>
  )
}

const NetworkStats = memo(NetworkStatsInner)
export default NetworkStats
