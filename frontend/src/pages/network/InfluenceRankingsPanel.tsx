/* ═══════════════════════════════════════════════════════════════════════════
   InfluenceRankingsPanel.tsx — Phase 7B Graph Analytics & Nutrient Rankings
   Linear/Arc-style leaderboard of most influential nutrients in the network
   ═══════════════════════════════════════════════════════════════════════════ */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Trophy, Zap, ShieldAlert, GitBranch, ArrowUpRight, TrendingUp } from 'lucide-react'
import { PALETTE } from './NetworkData'

export interface NutrientCentralityItem {
  nutrient_id: string
  nutrient_name: string
  degree_centrality: number
  in_degree: number
  out_degree: number
  total_degree: number
  betweenness_centrality: number
  influence_score: number
  dependency_score: number
  rank: number
}

export interface CentralityAnalysisResponse {
  total_nodes: number
  total_edges: number
  density: number
  top_influential_nutrients: NutrientCentralityItem[]
  all_nutrients_centrality: NutrientCentralityItem[]
}

interface Props {
  onSelectNutrient?: (nutrientId: string) => void
}

export default function InfluenceRankingsPanel({ onSelectNutrient }: Props) {
  const [data, setData] = useState<CentralityAnalysisResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [filterMode, setFilterMode] = useState<'top5' | 'all'>('top5')

  useEffect(() => {
    fetch('/api/v1/knowledge-graph/centrality')
      .then(res => res.json())
      .then(json => {
        setData(json)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load centrality rankings:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div style={{
        padding: 20, textAlign: 'center', color: PALETTE.textMuted,
        background: PALETTE.card, borderRadius: 14, border: `1px solid ${PALETTE.border}`
      }}>
        Calculating graph centrality and influence metrics...
      </div>
    )
  }

  if (!data) return null

  const displayList = filterMode === 'top5' ? data.top_influential_nutrients : data.all_nutrients_centrality
  const maxInfluence = Math.max(...data.all_nutrients_centrality.map(n => n.influence_score)) || 1.0

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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'rgba(255, 176, 32, 0.12)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#FFCF5C'
          }}>
            <Trophy size={18} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, letterSpacing: '-0.02em', color: PALETTE.text }}>
              Nutrient Influence & Centrality Rankings
            </h3>
            <span style={{ fontSize: 12, color: PALETTE.textMuted }}>
              Quantifying systemic physiological influence and upstream cofactor vulnerability
            </span>
          </div>
        </div>

        {/* Filter Toggle */}
        <div style={{
          display: 'flex', background: PALETTE.surface,
          padding: 2, borderRadius: 8, border: `1px solid ${PALETTE.borderLight}`
        }}>
          <button
            onClick={() => setFilterMode('top5')}
            style={{
              padding: '4px 12px', fontSize: 11, fontWeight: 600, borderRadius: 6,
              background: filterMode === 'top5' ? PALETTE.card : 'transparent',
              color: filterMode === 'top5' ? PALETTE.accent : PALETTE.textMuted,
              border: 'none', cursor: 'pointer', transition: 'all 0.15s ease'
            }}
          >
            Top 5 Masters
          </button>
          <button
            onClick={() => setFilterMode('all')}
            style={{
              padding: '4px 12px', fontSize: 11, fontWeight: 600, borderRadius: 6,
              background: filterMode === 'all' ? PALETTE.card : 'transparent',
              color: filterMode === 'all' ? PALETTE.accent : PALETTE.textMuted,
              border: 'none', cursor: 'pointer', transition: 'all 0.15s ease'
            }}
          >
            All 18 Nutrients
          </button>
        </div>
      </div>

      {/* Network Health Stats Strip */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10,
        background: 'rgba(0, 0, 0, 0.25)', padding: '10px 14px', borderRadius: 8,
        border: `1px solid ${PALETTE.borderLight}`
      }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: 10.5, color: PALETTE.textMuted, fontWeight: 600, textTransform: 'uppercase' }}>
            Graph Entities
          </span>
          <span style={{ fontSize: 15, fontWeight: 700, color: PALETTE.text }}>
            {data.total_nodes} Nodes
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: 10.5, color: PALETTE.textMuted, fontWeight: 600, textTransform: 'uppercase' }}>
            Biochemical Edges
          </span>
          <span style={{ fontSize: 15, fontWeight: 700, color: PALETTE.accent }}>
            {data.total_edges} Directed Links
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: 10.5, color: PALETTE.textMuted, fontWeight: 600, textTransform: 'uppercase' }}>
            Network Density
          </span>
          <span style={{ fontSize: 15, fontWeight: 700, color: '#3FB950' }}>
            {(data.density * 100).toFixed(1)}% Cohesion
          </span>
        </div>
      </div>

      {/* Leaderboard Rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 380, overflowY: 'auto', paddingRight: 4 }}>
        {displayList.map((item, idx) => {
          const ratio = Math.min(100, Math.round((item.influence_score / maxInfluence) * 100))
          const isTop3 = item.rank <= 3

          return (
            <motion.div
              key={item.nutrient_id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04 }}
              onClick={() => onSelectNutrient && onSelectNutrient(item.nutrient_id)}
              style={{
                display: 'grid', gridTemplateColumns: '40px 1.5fr 2fr auto',
                alignItems: 'center', gap: 12,
                background: isTop3 ? 'rgba(88, 166, 255, 0.04)' : 'rgba(255, 255, 255, 0.015)',
                border: `1px solid ${isTop3 ? 'rgba(88, 166, 255, 0.2)' : PALETTE.borderLight}`,
                borderRadius: 8, padding: '10px 14px',
                cursor: onSelectNutrient ? 'pointer' : 'default',
                transition: 'all 0.15s ease'
              }}
            >
              {/* Rank Pill */}
              <div style={{
                width: 26, height: 26, borderRadius: 6,
                background: isTop3 ? 'rgba(255, 176, 32, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                color: isTop3 ? '#FFCF5C' : PALETTE.textMuted,
                fontSize: 12, fontWeight: 800,
                display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                #{item.rank}
              </div>

              {/* Name & Centrality */}
              <div>
                <div style={{ fontSize: 13.5, fontWeight: 700, color: PALETTE.text }}>
                  {item.nutrient_name}
                </div>
                <div style={{ fontSize: 11, color: PALETTE.textMuted }}>
                  Betweenness: <span style={{ color: PALETTE.accent }}>{item.betweenness_centrality.toFixed(3)}</span> · {item.total_degree} links
                </div>
              </div>

              {/* Influence Meter */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
                  <span style={{ color: PALETTE.textMuted, fontWeight: 500 }}>Systemic Reach</span>
                  <strong style={{ color: PALETTE.accent }}>{item.influence_score} pts</strong>
                </div>
                <div style={{
                  height: 6, width: '100%', background: 'rgba(255, 255, 255, 0.06)',
                  borderRadius: 3, overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%', width: `${ratio}%`,
                    background: 'linear-gradient(90deg, #58A6FF, #38BDF8)',
                    borderRadius: 3
                  }} />
                </div>
              </div>

              {/* Badges */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 4,
                  fontSize: 10.5, fontWeight: 700, padding: '3px 8px', borderRadius: 5,
                  background: 'rgba(56, 189, 248, 0.12)', color: '#38BDF8',
                  border: '1px solid rgba(56, 189, 248, 0.25)'
                }} title="Causal Downstream Influence Score">
                  <Zap size={11} />
                  <span>Inf: {item.influence_score}</span>
                </div>

                <div style={{
                  display: 'flex', alignItems: 'center', gap: 4,
                  fontSize: 10.5, fontWeight: 700, padding: '3px 8px', borderRadius: 5,
                  background: 'rgba(255, 176, 32, 0.12)', color: '#FFCF5C',
                  border: '1px solid rgba(255, 176, 32, 0.25)'
                }} title="Upstream Cofactor Dependency Score">
                  <ShieldAlert size={11} />
                  <span>Dep: {item.dependency_score}</span>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
