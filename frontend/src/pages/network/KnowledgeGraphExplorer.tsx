/* ═══════════════════════════════════════════════════════════════════════════
   KnowledgeGraphExplorer.tsx — Phase 7B Clinical Knowledge Graph Explorer
   Desktop-grade intelligence workspace integrating search, node expansion,
   relationship filters, influence badges, path viewer, and system impacts.
   ═══════════════════════════════════════════════════════════════════════════ */

import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Filter, Network, GitCommit, Trophy, Activity,
  Zap, ShieldAlert, ChevronRight, BookOpen, Layers,
  ExternalLink, Sparkles, X, Check
} from 'lucide-react'
import { PALETTE } from './NetworkData'
import ClinicalPathViewer from './ClinicalPathViewer'
import InfluenceRankingsPanel from './InfluenceRankingsPanel'
import SystemImpactPanel from './SystemImpactPanel'

export interface GraphEntity {
  id: string
  name: string
  entity_type: string
  category?: string
  description: string
  metadata: Record<string, any>
}

export interface GraphRelationship {
  id: string
  source_id: string
  source_name: string
  source_type: string
  target_id: string
  target_name: string
  target_type: string
  relationship_type: string
  weight: number
  mechanism: string
  citation?: string
}

export interface SubgraphData {
  center_nutrient_id: string
  center_nutrient_name: string
  nodes: GraphEntity[]
  edges: GraphRelationship[]
  summary_counts: {
    nutrients: number
    symptoms: number
    foods: number
    lifestyle_factors: number
    medical_conditions: number
    lab_tests: number
    biological_systems: number
  }
  categorized_explorer: Record<string, GraphEntity[]>
}

const CATEGORY_TABS = [
  { id: 'ALL', label: 'All Entities' },
  { id: 'NUTRIENT', label: 'Nutrients' },
  { id: 'SYMPTOM', label: 'Symptoms' },
  { id: 'FOOD', label: 'Foods' },
  { id: 'LIFESTYLE_FACTOR', label: 'Lifestyle' },
  { id: 'MEDICAL_CONDITION', label: 'Conditions' },
  { id: 'LAB_TEST', label: 'Lab Tests' },
  { id: 'BIOLOGICAL_SYSTEM', label: 'Body Systems' },
]

const RELATIONSHIP_FILTERS = [
  'CAUSES', 'CONTRIBUTES_TO', 'REQUIRES', 'SUPPORTS', 'IMPACTS', 'CONFIRMS', 'INHIBITS', 'ENHANCES'
]

export default function KnowledgeGraphExplorer() {
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<'explorer' | 'path' | 'rankings' | 'systems'>('explorer')
  const [selectedEntityId, setSelectedEntityId] = useState<string>('NUTRIENT_VITAMIN_D')
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL')
  const [activeRelFilters, setActiveRelFilters] = useState<string[]>(RELATIONSHIP_FILTERS)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [entities, setEntities] = useState<GraphEntity[]>([])
  const [subgraph, setSubgraph] = useState<SubgraphData | null>(null)
  const [loadingSubgraph, setLoadingSubgraph] = useState<boolean>(false)
  const [centralityMap, setCentralityMap] = useState<Record<string, { influence: number; dependency: number }>>({})

  // Load entities catalog
  useEffect(() => {
    fetch('/api/v1/knowledge-graph/entities')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setEntities(data)
      })
      .catch(err => console.error('Failed to load entities:', err))

    // Load centrality for badge displays
    fetch('/api/v1/knowledge-graph/centrality')
      .then(res => res.json())
      .then(data => {
        if (data && data.all_nutrients_centrality) {
          const map: Record<string, { influence: number; dependency: number }> = {}
          data.all_nutrients_centrality.forEach((item: any) => {
            map[item.nutrient_id] = {
              influence: item.influence_score,
              dependency: item.dependency_score
            }
          })
          setCentralityMap(map)
        }
      })
      .catch(err => console.error('Failed to load centrality for badges:', err))
  }, [])

  // Load subgraph when selected entity changes
  useEffect(() => {
    if (!selectedEntityId) return
    setLoadingSubgraph(true)
    fetch(`/api/v1/knowledge-graph/nutrients/${selectedEntityId}/network`)
      .then(res => {
        if (!res.ok) throw new Error('Not found')
        return res.json()
      })
      .then(data => {
        setSubgraph(data)
        setLoadingSubgraph(false)
      })
      .catch(() => {
        setSubgraph(null)
        setLoadingSubgraph(false)
      })
  }, [selectedEntityId])

  const filteredEntities = useMemo(() => {
    return entities.filter(e => {
      const matchesCat = selectedCategory === 'ALL' || e.entity_type === selectedCategory
      const matchesSearch = !searchQuery ||
        e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.id.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesCat && matchesSearch
    })
  }, [entities, selectedCategory, searchQuery])

  const toggleRelFilter = (rel: string) => {
    setActiveRelFilters(prev =>
      prev.includes(rel) ? prev.filter(r => r !== rel) : [...prev, rel]
    )
  }

  const selectedEntity = entities.find(e => e.id === selectedEntityId)
  const centrality = centralityMap[selectedEntityId]

  return (
    <div style={{
      width: '100%', height: '100%',
      display: 'flex', flexDirection: 'column',
      background: PALETTE.bg, color: PALETTE.text,
      fontFamily: 'Inter, system-ui, sans-serif',
      overflow: 'hidden'
    }}>
      {/* Top Workspace Navigation Bar */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 20px', background: PALETTE.surface,
        borderBottom: `1px solid ${PALETTE.border}`,
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 7,
            background: 'rgba(88, 166, 255, 0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: PALETTE.accent
          }}>
            <Network size={16} />
          </div>
          <div>
            <span style={{ fontSize: 13, fontWeight: 700, color: PALETTE.text, letterSpacing: '-0.01em' }}>
              Clinical Knowledge Graph & Causal Intelligence
            </span>
            <span style={{ fontSize: 11, color: PALETTE.textDim, marginLeft: 8, padding: '1px 6px', borderRadius: 4, background: PALETTE.card, border: `1px solid ${PALETTE.borderLight}` }}>
              Phase 7B
            </span>
          </div>
        </div>

        {/* View Mode Switcher */}
        <div style={{
          display: 'flex', background: PALETTE.card,
          padding: 2, borderRadius: 8, border: `1px solid ${PALETTE.borderLight}`
        }}>
          <button
            onClick={() => setActiveWorkspaceTab('explorer')}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '5px 12px', fontSize: 11.5, fontWeight: 600, borderRadius: 6,
              background: activeWorkspaceTab === 'explorer' ? PALETTE.surface : 'transparent',
              color: activeWorkspaceTab === 'explorer' ? PALETTE.accent : PALETTE.textMuted,
              border: 'none', cursor: 'pointer', transition: 'all 0.15s ease'
            }}
          >
            <Layers size={13} />
            <span>Graph Explorer</span>
          </button>
          <button
            onClick={() => setActiveWorkspaceTab('path')}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '5px 12px', fontSize: 11.5, fontWeight: 600, borderRadius: 6,
              background: activeWorkspaceTab === 'path' ? PALETTE.surface : 'transparent',
              color: activeWorkspaceTab === 'path' ? PALETTE.accent : PALETTE.textMuted,
              border: 'none', cursor: 'pointer', transition: 'all 0.15s ease'
            }}
          >
            <GitCommit size={13} />
            <span>Clinical Path Viewer</span>
          </button>
          <button
            onClick={() => setActiveWorkspaceTab('rankings')}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '5px 12px', fontSize: 11.5, fontWeight: 600, borderRadius: 6,
              background: activeWorkspaceTab === 'rankings' ? PALETTE.surface : 'transparent',
              color: activeWorkspaceTab === 'rankings' ? PALETTE.accent : PALETTE.textMuted,
              border: 'none', cursor: 'pointer', transition: 'all 0.15s ease'
            }}
          >
            <Trophy size={13} />
            <span>Influence Rankings</span>
          </button>
          <button
            onClick={() => setActiveWorkspaceTab('systems')}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '5px 12px', fontSize: 11.5, fontWeight: 600, borderRadius: 6,
              background: activeWorkspaceTab === 'systems' ? PALETTE.surface : 'transparent',
              color: activeWorkspaceTab === 'systems' ? PALETTE.accent : PALETTE.textMuted,
              border: 'none', cursor: 'pointer', transition: 'all 0.15s ease'
            }}
          >
            <Activity size={13} />
            <span>System Impacts</span>
          </button>
        </div>
      </div>

      {/* Main Workspace Area */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px 20px' }}>
        {activeWorkspaceTab === 'path' && <ClinicalPathViewer />}
        {activeWorkspaceTab === 'rankings' && (
          <InfluenceRankingsPanel onSelectNutrient={(id) => {
            setSelectedEntityId(id)
            setActiveWorkspaceTab('explorer')
          }} />
        )}
        {activeWorkspaceTab === 'systems' && <SystemImpactPanel />}

        {activeWorkspaceTab === 'explorer' && (
          <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 16, height: '100%' }}>
            {/* Left Column: Entity Directory & Search */}
            <div style={{
              display: 'flex', flexDirection: 'column', gap: 12,
              background: PALETTE.card, borderRadius: 12,
              border: `1px solid ${PALETTE.border}`, padding: 14,
              overflow: 'hidden'
            }}>
              {/* Search Bar */}
              <div style={{
                position: 'relative', display: 'flex', alignItems: 'center'
              }}>
                <Search size={14} color={PALETTE.textDim} style={{ position: 'absolute', left: 10 }} />
                <input
                  type="text"
                  placeholder="Search entities, symptoms, foods..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%', padding: '7px 10px 7px 30px',
                    background: PALETTE.surface, border: `1px solid ${PALETTE.borderLight}`,
                    borderRadius: 7, color: PALETTE.text, fontSize: 12,
                    outline: 'none'
                  }}
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    style={{
                      position: 'absolute', right: 8, background: 'none',
                      border: 'none', color: PALETTE.textDim, cursor: 'pointer'
                    }}
                  >
                    <X size={12} />
                  </button>
                )}
              </div>

              {/* Category Pills */}
              <div style={{
                display: 'flex', flexWrap: 'wrap', gap: 4, maxHeight: 80, overflowY: 'auto'
              }}>
                {CATEGORY_TABS.map(tab => {
                  const isSelected = selectedCategory === tab.id
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setSelectedCategory(tab.id)}
                      style={{
                        padding: '3px 8px', borderRadius: 5, fontSize: 10.5, fontWeight: 600,
                        background: isSelected ? PALETTE.accentGlow : 'rgba(255, 255, 255, 0.02)',
                        color: isSelected ? PALETTE.accent : PALETTE.textMuted,
                        border: `1px solid ${isSelected ? PALETTE.accent : PALETTE.borderLight}`,
                        cursor: 'pointer', transition: 'all 0.15s ease'
                      }}
                    >
                      {tab.label}
                    </button>
                  )
                })}
              </div>

              {/* Filtered Entity List */}
              <div style={{
                flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 4,
                paddingRight: 2
              }}>
                {filteredEntities.map(e => {
                  const isSelected = e.id === selectedEntityId
                  return (
                    <div
                      key={e.id}
                      onClick={() => setSelectedEntityId(e.id)}
                      style={{
                        padding: '8px 10px', borderRadius: 7,
                        background: isSelected ? 'rgba(88, 166, 255, 0.1)' : 'rgba(255, 255, 255, 0.015)',
                        border: `1px solid ${isSelected ? PALETTE.accent : 'transparent'}`,
                        cursor: 'pointer', transition: 'all 0.12s ease'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{
                          fontSize: 12, fontWeight: isSelected ? 700 : 500,
                          color: isSelected ? PALETTE.accent : PALETTE.text
                        }}>
                          {e.name}
                        </span>
                        <span style={{
                          fontSize: 9.5, fontWeight: 700, padding: '1px 5px', borderRadius: 3,
                          background: 'rgba(255, 255, 255, 0.04)', color: PALETTE.textDim
                        }}>
                          {e.entity_type}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Right Column: Node Details & Causal Neighborhood */}
            <div style={{
              display: 'flex', flexDirection: 'column', gap: 14,
              overflowY: 'auto'
            }}>
              {/* Active Entity Banner */}
              {selectedEntity && (
                <div style={{
                  background: PALETTE.card, borderRadius: 12,
                  border: `1px solid ${PALETTE.border}`, padding: '16px 20px',
                  display: 'flex', flexDirection: 'column', gap: 10
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 10 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: PALETTE.text }}>
                          {selectedEntity.name}
                        </h2>
                        <span style={{
                          fontSize: 10.5, fontWeight: 700, padding: '2px 8px', borderRadius: 4,
                          background: 'rgba(88, 166, 255, 0.12)', color: PALETTE.accent,
                          border: '1px solid rgba(88, 166, 255, 0.25)'
                        }}>
                          {selectedEntity.entity_type}
                        </span>
                        {selectedEntity.category && (
                          <span style={{ fontSize: 11, color: PALETTE.textMuted }}>
                            ({selectedEntity.category})
                          </span>
                        )}
                      </div>
                      <p style={{ margin: '6px 0 0', fontSize: 12.5, color: '#C9D1D9', lineHeight: 1.5 }}>
                        {selectedEntity.description}
                      </p>
                    </div>

                    {/* Centrality Badges (if nutrient) */}
                    {centrality && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{
                          display: 'flex', alignItems: 'center', gap: 5,
                          fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 6,
                          background: 'rgba(56, 189, 248, 0.12)', color: '#38BDF8',
                          border: '1px solid rgba(56, 189, 248, 0.3)'
                        }} title="Causal Downstream Influence Score">
                          <Zap size={13} />
                          <span>Influence: {centrality.influence}</span>
                        </div>

                        <div style={{
                          display: 'flex', alignItems: 'center', gap: 5,
                          fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 6,
                          background: 'rgba(255, 176, 32, 0.12)', color: '#FFCF5C',
                          border: '1px solid rgba(255, 176, 32, 0.3)'
                        }} title="Upstream Cofactor Dependency Score">
                          <ShieldAlert size={13} />
                          <span>Dependency: {centrality.dependency}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Relationship Filter Toggles */}
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap',
                    paddingTop: 8, borderTop: `1px solid ${PALETTE.borderLight}`
                  }}>
                    <span style={{ fontSize: 11, color: PALETTE.textDim, fontWeight: 600, textTransform: 'uppercase' }}>
                      Filter Edges:
                    </span>
                    {RELATIONSHIP_FILTERS.map(rel => {
                      const isActive = activeRelFilters.includes(rel)
                      return (
                        <button
                          key={rel}
                          onClick={() => toggleRelFilter(rel)}
                          style={{
                            padding: '2px 8px', borderRadius: 4, fontSize: 10, fontWeight: 700,
                            background: isActive ? 'rgba(255, 255, 255, 0.08)' : 'transparent',
                            color: isActive ? PALETTE.text : PALETTE.textDim,
                            border: `1px solid ${isActive ? PALETTE.border : PALETTE.borderLight}`,
                            cursor: 'pointer', transition: 'all 0.15s ease'
                          }}
                        >
                          {rel}
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Subgraph Connections Breakdown */}
              {loadingSubgraph ? (
                <div style={{ padding: 24, textAlign: 'center', color: PALETTE.textMuted, fontSize: 13 }}>
                  Resolving connected causal graph neighborhood...
                </div>
              ) : subgraph ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {/* Summary Metric Pills */}
                  <div style={{
                    display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 8
                  }}>
                    {Object.entries(subgraph.summary_counts).map(([key, count]) => (
                      <div
                        key={key}
                        style={{
                          background: PALETTE.card, padding: '8px 10px', borderRadius: 8,
                          border: `1px solid ${PALETTE.borderLight}`, textAlign: 'center'
                        }}
                      >
                        <span style={{ display: 'block', fontSize: 14, fontWeight: 800, color: count > 0 ? PALETTE.accent : PALETTE.textDim }}>
                          {count}
                        </span>
                        <span style={{ fontSize: 9.5, color: PALETTE.textMuted, textTransform: 'uppercase', fontWeight: 600 }}>
                          {key.replace('_', ' ')}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Connected Edges List */}
                  <div style={{
                    display: 'flex', flexDirection: 'column', gap: 8,
                    background: PALETTE.card, borderRadius: 12,
                    border: `1px solid ${PALETTE.border}`, padding: 16
                  }}>
                    <h4 style={{ margin: 0, fontSize: 13, fontWeight: 700, color: PALETTE.text, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Direct Causal Connections ({subgraph.edges.filter(e => activeRelFilters.includes(e.relationship_type)).length})
                    </h4>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {subgraph.edges
                        .filter(e => activeRelFilters.includes(e.relationship_type))
                        .map(edge => {
                          const isOrigin = edge.source_id === selectedEntityId
                          const otherNodeName = isOrigin ? edge.target_name : edge.source_name
                          const otherNodeType = isOrigin ? edge.target_type : edge.source_type
                          const otherNodeId = isOrigin ? edge.target_id : edge.source_id

                          return (
                            <div
                              key={edge.id}
                              style={{
                                display: 'flex', flexDirection: 'column', gap: 6,
                                background: 'rgba(255, 255, 255, 0.02)',
                                border: `1px solid ${PALETTE.borderLight}`,
                                borderRadius: 8, padding: 12
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                  <span style={{
                                    fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                                    background: 'rgba(88, 166, 255, 0.1)', color: PALETTE.accent,
                                    border: '1px solid rgba(88, 166, 255, 0.2)'
                                  }}>
                                    {edge.relationship_type}
                                  </span>
                                  <span style={{ fontSize: 13, fontWeight: 700, color: PALETTE.text }}>
                                    {otherNodeName}
                                  </span>
                                  <span style={{ fontSize: 10, color: PALETTE.textDim, fontWeight: 600 }}>
                                    [{otherNodeType}]
                                  </span>
                                </div>

                                <button
                                  onClick={() => setSelectedEntityId(otherNodeId)}
                                  style={{
                                    display: 'flex', alignItems: 'center', gap: 4,
                                    fontSize: 11, fontWeight: 600, color: PALETTE.accent,
                                    background: 'none', border: 'none', cursor: 'pointer'
                                  }}
                                >
                                  <span>Focus Node</span>
                                  <ChevronRight size={13} />
                                </button>
                              </div>

                              <p style={{ margin: 0, fontSize: 12, color: '#C9D1D9', lineHeight: 1.4 }}>
                                {edge.mechanism}
                              </p>

                              {edge.citation && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10.5, color: PALETTE.textDim, fontStyle: 'italic' }}>
                                  <BookOpen size={11} />
                                  <span>{edge.citation}</span>
                                </div>
                              )}
                            </div>
                          )
                        })}
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{
                  padding: 24, textAlign: 'center', color: PALETTE.textMuted,
                  background: PALETTE.card, borderRadius: 12, border: `1px solid ${PALETTE.border}`
                }}>
                  Select an entity on the left to inspect its complete causal network.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
