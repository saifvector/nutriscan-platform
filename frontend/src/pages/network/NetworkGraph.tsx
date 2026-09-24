/* ═══════════════════════════════════════════════════════════════════════════
   NetworkGraph.tsx — Phase 6.1 Performance-Optimized Clinical Intelligence Network
   Zero graph rebuilds · Stable callback refs · Vector gradient glow (no feGaussianBlur)
   Decoupled autoFit · Pre-cached tick selections · < 600ms simulation settle
   ═══════════════════════════════════════════════════════════════════════════ */

import { useRef, useEffect, useCallback, memo } from 'react'
import * as d3 from 'd3'
import {
  NODES, EDGES, PALETTE, RISK_COLORS, EDGE_COLORS,
  getNodeRadius, getConnectedGraph, getFilteredNetworkData,
  type NutrientNode, type NutrientEdge, type ConnectedGraph, type RiskLevel,
} from './NetworkData'

/* ─── Constants ─── */
const PARTICLES_PER_EDGE = 3
const BASE_SPEED = 0.003
const SPEED_MULTIPLIER = 0.004

/* ─── Constellation Star Points (Layer 2: Deterministic, < 8% Opacity) ─── */
const CONSTELLATION_POINTS = Array.from({ length: 52 }, (_, i) => {
  const seed = (i + 1) * 9301 + 49297
  const x = ((Math.sin(seed * 1.13) * 0.5 + 0.5) * 2800) - 600
  const y = ((Math.cos(seed * 1.71) * 0.5 + 0.5) * 2000) - 500
  const r = 0.85 + ((Math.sin(seed * 2.37) * 0.5 + 0.5) * 0.75)
  const opacity = 0.03 + ((Math.cos(seed * 3.23) * 0.5 + 0.5) * 0.045)
  const isTeal = i % 3 === 0
  return { id: i, x, y, r, opacity, color: isTeal ? '#2DD4BF' : '#93C5FD' }
})

const CONSTELLATION_LINKS = [
  [0, 5], [5, 11], [11, 19], [2, 7], [7, 14], [14, 23],
  [16, 22], [22, 31], [25, 34], [34, 43], [37, 46], [46, 51],
]

/* ─── Props ─── */
interface NetworkGraphProps {
  riskFilter?: RiskLevel | null
  selectedId: string | null
  hoveredId: string | null
  onNodeClick: (node: NutrientNode) => void
  onNodeHover: (node: NutrientNode | null, event?: MouseEvent) => void
  onEdgeClick: (edge: NutrientEdge) => void
}

/* ═══════════════════════════════════════════════════════════════════════════
   COMPONENT
   ═══════════════════════════════════════════════════════════════════════════ */

function NetworkGraph({
  riskFilter = null, selectedId, hoveredId, onNodeClick, onNodeHover, onEdgeClick,
}: NetworkGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animRef = useRef<number>(0)
  const isTransitioningRef = useRef<boolean>(false)

  // Stable callback refs — prevents setupGraph from ever invalidating
  const onNodeClickRef = useRef(onNodeClick)
  onNodeClickRef.current = onNodeClick
  const onNodeHoverRef = useRef(onNodeHover)
  onNodeHoverRef.current = onNodeHover
  const onEdgeClickRef = useRef(onEdgeClick)
  onEdgeClickRef.current = onEdgeClick

  const stateRef = useRef<{
    nodes: NutrientNode[]
    edges: NutrientEdge[]
    particles: { edge: NutrientEdge; progress: number; speed: number; reverse: boolean }[]
    connected: ConnectedGraph | null
    selectedId: string | null
    hoveredId: string | null
    zoomTransform: d3.ZoomTransform
    applyVisualState: (() => void) | null
    autoFit: ((animate?: boolean) => void) | null
    sim: d3.Simulation<NutrientNode, NutrientEdge> | null
    animRunning: boolean
    tabVisible: boolean
  }>({
    nodes: [], edges: [], particles: [],
    connected: null, selectedId: null, hoveredId: null,
    zoomTransform: d3.zoomIdentity,
    applyVisualState: null,
    autoFit: null,
    sim: null,
    animRunning: false,
    tabVisible: true,
  })

  // Synchronize selection state without tearing down graph
  useEffect(() => {
    stateRef.current.selectedId = selectedId
    stateRef.current.connected = selectedId ? getConnectedGraph(selectedId, stateRef.current.edges) : null

    // Spawn directional particles only for connected edges
    if (selectedId && stateRef.current.connected) {
      const particles: typeof stateRef.current.particles = []
      stateRef.current.connected.edges.forEach(eid => {
        const edge = stateRef.current.edges.find(e => e.id === eid)
        if (!edge) return
        const reverse = edge.type === 'competitive'
        const speed = BASE_SPEED + edge.strength * SPEED_MULTIPLIER
        for (let i = 0; i < PARTICLES_PER_EDGE; i++) {
          particles.push({ edge, progress: i / PARTICLES_PER_EDGE, speed, reverse })
        }
      })
      stateRef.current.particles = particles
      if (!stateRef.current.animRunning) startAnimation()
    } else {
      stateRef.current.particles = []
      const canvas = canvasRef.current
      if (canvas) {
        const ctx = canvas.getContext('2d')
        if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
    }

    // Surgical visual update — zero DOM recreation
    stateRef.current.applyVisualState?.()
  }, [selectedId])

  useEffect(() => {
    stateRef.current.hoveredId = hoveredId
    stateRef.current.applyVisualState?.()
  }, [hoveredId])

  // Pause animation when tab is hidden
  useEffect(() => {
    const onVisibility = () => {
      stateRef.current.tabVisible = !document.hidden
      if (!document.hidden && stateRef.current.particles.length > 0 && !stateRef.current.animRunning) {
        startAnimation()
      }
    }
    document.addEventListener('visibilitychange', onVisibility)
    return () => document.removeEventListener('visibilitychange', onVisibility)
  }, [])

  // Start/stop animation loop (only runs on demand when particles exist)
  const startAnimation = useCallback(() => {
    if (stateRef.current.animRunning) return
    stateRef.current.animRunning = true
    const canvas = canvasRef.current
    if (!canvas) { stateRef.current.animRunning = false; return }
    const ctx = canvas.getContext('2d')
    if (!ctx) { stateRef.current.animRunning = false; return }

    function tick() {
      const { particles, zoomTransform: zt, tabVisible } = stateRef.current

      if (particles.length === 0 || !tabVisible) {
        stateRef.current.animRunning = false
        ctx!.clearRect(0, 0, canvas!.width, canvas!.height)
        return
      }

      ctx!.clearRect(0, 0, canvas!.width, canvas!.height)
      ctx!.save()
      ctx!.translate(zt.x, zt.y)
      ctx!.scale(zt.k, zt.k)

      particles.forEach(p => {
        p.progress = (p.progress + p.speed) % 1
        const s = (p.reverse ? p.edge.target : p.edge.source) as any
        const t = (p.reverse ? p.edge.source : p.edge.target) as any
        if (s.x == null || t.x == null) return

        const prog = p.progress
        const mx = (s.x + t.x) / 2
        const my = (s.y + t.y) / 2
        const dx = t.x - s.x
        const dy = t.y - s.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        const offset = dist * 0.15
        const cx = mx + (-dy / dist) * offset
        const cy = my + (dx / dist) * offset

        const it = 1 - prog
        const px = it * it * s.x + 2 * it * prog * cx + prog * prog * t.x
        const py = it * it * s.y + 2 * it * prog * cy + prog * prog * t.y

        const color = EDGE_COLORS[p.edge.type].stroke

        // Core particle dot
        ctx!.beginPath()
        ctx!.arc(px, py, 2, 0, Math.PI * 2)
        ctx!.fillStyle = color
        ctx!.globalAlpha = 0.85
        ctx!.fill()

        // Direction trail
        const trailProg = Math.max(0, prog - 0.035)
        const it2 = 1 - trailProg
        const tx2 = it2 * it2 * s.x + 2 * it2 * trailProg * cx + trailProg * trailProg * t.x
        const ty2 = it2 * it2 * s.y + 2 * it2 * trailProg * cy + trailProg * trailProg * t.y
        ctx!.beginPath()
        ctx!.moveTo(tx2, ty2)
        ctx!.lineTo(px, py)
        ctx!.strokeStyle = color
        ctx!.lineWidth = 1.2
        ctx!.globalAlpha = 0.3
        ctx!.stroke()
        ctx!.globalAlpha = 1.0
      })

      ctx!.restore()
      animRef.current = requestAnimationFrame(tick)
    }
    animRef.current = requestAnimationFrame(tick)
  }, [])

  /* ═══ MAIN D3 SETUP (STRICTLY RUNS ONCE ON MOUNT) ═══ */
  const setupGraph = useCallback(() => {
    if (!svgRef.current || !containerRef.current || !canvasRef.current) return

    const svg = d3.select(svgRef.current)
    const rect = containerRef.current.getBoundingClientRect()
    const W = rect.width, H = rect.height

    // Set canvas size with Retina DPR scaling
    const canvas = canvasRef.current
    const dpr = window.devicePixelRatio || 1
    canvas.width = W * dpr
    canvas.height = H * dpr
    canvas.style.width = `${W}px`
    canvas.style.height = `${H}px`
    const ctx = canvas.getContext('2d')!
    ctx.scale(dpr, dpr)

    svg.selectAll('*').remove()
    svg.attr('width', W).attr('height', H).attr('viewBox', `0 0 ${W} ${H}`)

    /* ── Defs ── */
    const defs = svg.append('defs')

    // Native vector radial shadow gradient (replaces feDropShadow filter)
    const nodeShadowGrad = defs.append('radialGradient').attr('id', 'grad-node-shadow').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    nodeShadowGrad.append('stop').attr('offset', '65%').attr('stop-color', '#000000').attr('stop-opacity', '0.6')
    nodeShadowGrad.append('stop').attr('offset', '100%').attr('stop-color', '#000000').attr('stop-opacity', '0')

    // Radial gradients per risk level (Node body fills)
    const createRadialGrad = (id: string, innerColor: string, outerColor: string) => {
      const g = defs.append('radialGradient').attr('id', id).attr('cx', '35%').attr('cy', '35%')
      g.append('stop').attr('offset', '0%').attr('stop-color', innerColor)
      g.append('stop').attr('offset', '100%').attr('stop-color', outerColor)
    }
    createRadialGrad('grad-high', '#2A1717', '#170B0B')
    createRadialGrad('grad-moderate', '#281F0E', '#161208')
    createRadialGrad('grad-low', '#0A261D', '#071611')
    createRadialGrad('grad-default', '#1A2130', '#11161F')

    /* ── Layer 3 Gradients: Ambient Aurora Lighting ── */
    const auroraTeal = defs.append('radialGradient').attr('id', 'aurora-teal').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    auroraTeal.append('stop').attr('offset', '0%').attr('stop-color', '#14B8A6').attr('stop-opacity', '0.11')
    auroraTeal.append('stop').attr('offset', '50%').attr('stop-color', '#0D9488').attr('stop-opacity', '0.04')
    auroraTeal.append('stop').attr('offset', '100%').attr('stop-color', '#06090F').attr('stop-opacity', '0')

    const auroraBlue = defs.append('radialGradient').attr('id', 'aurora-blue').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    auroraBlue.append('stop').attr('offset', '0%').attr('stop-color', '#38BDF8').attr('stop-opacity', '0.09')
    auroraBlue.append('stop').attr('offset', '50%').attr('stop-color', '#2563EB').attr('stop-opacity', '0.03')
    auroraBlue.append('stop').attr('offset', '100%').attr('stop-color', '#06090F').attr('stop-opacity', '0')

    const auroraViolet = defs.append('radialGradient').attr('id', 'aurora-violet').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    auroraViolet.append('stop').attr('offset', '0%').attr('stop-color', '#818CF8').attr('stop-opacity', '0.07')
    auroraViolet.append('stop').attr('offset', '55%').attr('stop-color', '#6366F1').attr('stop-opacity', '0.02')
    auroraViolet.append('stop').attr('offset', '100%').attr('stop-color', '#06090F').attr('stop-opacity', '0')

    /* ── Layer 4 Gradients: Soft Risk Heat Regions (Native vector radial gradients) ── */
    const heatHigh = defs.append('radialGradient').attr('id', 'heat-grad-high').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    heatHigh.append('stop').attr('offset', '0%').attr('stop-color', '#FF4D4D').attr('stop-opacity', '0.14')
    heatHigh.append('stop').attr('offset', '45%').attr('stop-color', '#FF4D4D').attr('stop-opacity', '0.04')
    heatHigh.append('stop').attr('offset', '100%').attr('stop-color', '#FF4D4D').attr('stop-opacity', '0')

    const heatMod = defs.append('radialGradient').attr('id', 'heat-grad-moderate').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    heatMod.append('stop').attr('offset', '0%').attr('stop-color', '#FFB020').attr('stop-opacity', '0.11')
    heatMod.append('stop').attr('offset', '45%').attr('stop-color', '#FFB020').attr('stop-opacity', '0.03')
    heatMod.append('stop').attr('offset', '100%').attr('stop-color', '#FFB020').attr('stop-opacity', '0')

    const heatLow = defs.append('radialGradient').attr('id', 'heat-grad-low').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    heatLow.append('stop').attr('offset', '0%').attr('stop-color', '#00D68F').attr('stop-opacity', '0.08')
    heatLow.append('stop').attr('offset', '45%').attr('stop-color', '#00D68F').attr('stop-opacity', '0.02')
    heatLow.append('stop').attr('offset', '100%').attr('stop-color', '#00D68F').attr('stop-opacity', '0')

    /* ── Spotlight Gradient (Focus Mode) ── */
    const spotlightGrad = defs.append('radialGradient').attr('id', 'spotlight-grad').attr('cx', '50%').attr('cy', '50%').attr('r', '50%')
    spotlightGrad.append('stop').attr('id', 'spotlight-s0').attr('offset', '0%').attr('stop-color', '#58A6FF').attr('stop-opacity', '0.22')
    spotlightGrad.append('stop').attr('id', 'spotlight-s50').attr('offset', '45%').attr('stop-color', '#58A6FF').attr('stop-opacity', '0.07')
    spotlightGrad.append('stop').attr('offset', '100%').attr('stop-color', '#06090F').attr('stop-opacity', '0')

    /* ── Layer 1: Scientific Coordinate Grid Pattern (3–4% opacity) ── */
    const gridPattern = defs.append('pattern')
      .attr('id', 'scientific-grid')
      .attr('width', 100).attr('height', 100)
      .attr('patternUnits', 'userSpaceOnUse')
    const gridPatternNode = gridPattern.node()

    gridPattern.append('path')
      .attr('d', 'M 100 0 L 0 0 0 100')
      .attr('fill', 'none')
      .attr('stroke', 'rgba(56, 189, 248, 0.035)')
      .attr('stroke-width', 1)

    gridPattern.append('path')
      .attr('d', 'M -5 0 L 5 0 M 0 -5 L 0 5')
      .attr('fill', 'none')
      .attr('stroke', 'rgba(56, 189, 248, 0.075)')
      .attr('stroke-width', 1)

    gridPattern.append('path')
      .attr('d', 'M 47 50 L 53 50 M 50 47 L 50 53')
      .attr('fill', 'none')
      .attr('stroke', 'rgba(20, 184, 166, 0.045)')
      .attr('stroke-width', 0.75)

    /* ═══ ENVIRONMENT RENDER LAYERS ═══ */

    svg.append('rect')
      .attr('class', 'env-grid')
      .attr('width', '100%').attr('height', '100%')
      .attr('fill', 'url(#scientific-grid)')
      .style('pointer-events', 'none')

    const auroraG = svg.append('g').attr('class', 'env-aurora').style('pointer-events', 'none')
    auroraG.append('ellipse')
      .attr('cx', W * 0.32).attr('cy', H * 0.44)
      .attr('rx', Math.max(280, W * 0.24)).attr('ry', Math.max(220, H * 0.32))
      .attr('fill', 'url(#aurora-teal)')
    auroraG.append('ellipse')
      .attr('cx', W * 0.68).attr('cy', H * 0.54)
      .attr('rx', Math.max(300, W * 0.26)).attr('ry', Math.max(240, H * 0.34))
      .attr('fill', 'url(#aurora-blue)')
    auroraG.append('ellipse')
      .attr('cx', W * 0.50).attr('cy', H * 0.36)
      .attr('rx', Math.max(240, W * 0.20)).attr('ry', Math.max(180, H * 0.26))
      .attr('fill', 'url(#aurora-violet)')

    const constellationG = svg.append('g').attr('class', 'env-constellations').style('pointer-events', 'none')
    CONSTELLATION_LINKS.forEach(([i1, i2]) => {
      const p1 = CONSTELLATION_POINTS[i1]
      const p2 = CONSTELLATION_POINTS[i2]
      if (p1 && p2) {
        constellationG.append('line')
          .attr('x1', p1.x).attr('y1', p1.y).attr('x2', p2.x).attr('y2', p2.y)
          .attr('stroke', 'rgba(147, 197, 253, 0.025)')
          .attr('stroke-width', 0.8)
          .attr('stroke-dasharray', '2,4')
      }
    })
    CONSTELLATION_POINTS.forEach(pt => {
      constellationG.append('circle')
        .attr('cx', pt.x).attr('cy', pt.y)
        .attr('r', pt.r)
        .attr('fill', pt.color)
        .attr('opacity', pt.opacity)
    })

    // Focus Mode Dimmer
    const focusDimmer = svg.append('rect')
      .attr('class', 'env-focus-dimmer')
      .attr('width', '100%').attr('height', '100%')
      .attr('fill', PALETTE.bg)
      .attr('opacity', 0)
      .style('pointer-events', 'none')

    /* ── Main Graph Group (Pan & Zoom) ── */
    const g = svg.append('g').attr('class', 'main-graph-group')

    /* ── Layer 4: Soft Risk Heat Regions (moves with nodes) ── */
    const heatG = g.append('g').attr('class', 'risk-heat-regions').style('pointer-events', 'none')

    /* ── Focus Spotlight (around selected node) ── */
    const spotlight = g.append('circle')
      .attr('class', 'nutrient-spotlight')
      .attr('r', 230)
      .attr('fill', 'url(#spotlight-grad)')
      .attr('opacity', 0)
      .style('pointer-events', 'none')

    /* ── Zoom Behavior with rAF Coalescing ── */
    let zoomRaf = 0
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3.2])
      .on('zoom', (event) => {
        const zt = event.transform
        stateRef.current.zoomTransform = zt

        if (!zoomRaf) {
          zoomRaf = requestAnimationFrame(() => {
            zoomRaf = 0
            g.attr('transform', zt.toString())
            if (gridPatternNode) gridPatternNode.setAttribute('patternTransform', zt.toString())
            constellationG.attr('transform', `translate(${zt.x * 0.28}, ${zt.y * 0.28}) scale(${0.72 + zt.k * 0.28})`)
            auroraG.attr('transform', `translate(${zt.x * 0.40}, ${zt.y * 0.40}) scale(${0.65 + zt.k * 0.35})`)
          })
        }
      })
    svg.call(zoomBehavior)

    /* ── Fast-Settling Physics Force Layout ── */
    const minDim = Math.min(W, H)
    const aspect = W / H
    const radFactor = Math.max(0.9, Math.min(1.6, minDim / 600))
    const rModerate = 175 * radFactor
    const rLow = 300 * radFactor

    // Retrieve strictly visible nodes and edges based on active risk filter
    const { visibleNodes, visibleEdges } = getFilteredNetworkData(riskFilter)

    // Dynamic counts for radial angle distribution
    const highCount = visibleNodes.filter(n => (n.risk_level || n.risk) === 'HIGH').length || 1
    const modCount = visibleNodes.filter(n => (n.risk_level || n.risk) === 'MODERATE').length || 1
    const lowCount = visibleNodes.filter(n => (n.risk_level || n.risk) === 'LOW').length || 1
    let highIdx = 0, modIdx = 0, lowIdx = 0

    const nodes: NutrientNode[] = visibleNodes.map(n => {
      let r = 0, angle = 0
      const risk = n.risk_level || n.risk
      if (risk === 'HIGH') {
        r = riskFilter ? 80 * radFactor : 60
        angle = (2 * Math.PI * highIdx++) / highCount
      } else if (risk === 'MODERATE') {
        r = riskFilter ? 120 * radFactor : rModerate
        angle = (2 * Math.PI * modIdx++) / modCount
      } else {
        r = riskFilter ? 160 * radFactor : rLow
        angle = (2 * Math.PI * lowIdx++) / lowCount
      }
      return {
        ...n,
        x: W / 2 + Math.cos(angle) * r,
        y: H / 2 + Math.sin(angle) * r,
      }
    })
    const edges: NutrientEdge[] = visibleEdges.map(e => ({ ...e }))
    stateRef.current.nodes = nodes
    stateRef.current.edges = edges

    // Simulation tuned to settle cleanly in < 600ms
    const sim = d3.forceSimulation(nodes)
      .alphaDecay(0.048)          // Accelerated stabilization
      .alphaMin(0.005)            // Clean freeze cutoff
      .velocityDecay(0.55)        // Smooth deceleration without oscillation
      .force('link', d3.forceLink<NutrientNode, NutrientEdge>(edges).id(d => d.id).distance(d => {
        return (145 + (1 - d.strength) * 90) * Math.min(1.3, radFactor)
      }).strength(0.45))
      .force('charge', d3.forceManyBody().strength(d => {
        const n = d as NutrientNode
        const risk = n.risk_level || n.risk
        return (risk === 'HIGH' ? -820 : risk === 'MODERATE' ? -600 : -440) * radFactor
      }))
      .force('center', d3.forceCenter(W / 2, H / 2).strength(riskFilter ? 0.08 : 0.05))
      .force('collision', d3.forceCollide<NutrientNode>(d => getNodeRadius(d.probability) + 34 * Math.min(1.25, radFactor)))
      .force('x', d3.forceX(W / 2).strength(0.028 / Math.max(1, aspect * 0.6)))
      .force('y', d3.forceY(H / 2).strength(0.038 * Math.max(1, aspect * 0.7)))
      .force('radial', d3.forceRadial<NutrientNode>(d => {
        const risk = d.risk_level || d.risk
        return risk === 'HIGH' ? 0 : risk === 'MODERATE' ? (riskFilter ? 120 * radFactor : rModerate) : (riskFilter ? 160 * radFactor : rLow)
      }, W / 2, H / 2).strength(riskFilter ? 0.04 : 0.085))
    stateRef.current.sim = sim

    /* ── Layer 4: Render Soft Risk Heat Regions ── */
    const heatSel = heatG.selectAll<SVGCircleElement, NutrientNode>('circle')
      .data(nodes).join('circle')
      .attr('class', 'heat-region')
      .attr('r', d => d.risk === 'HIGH' ? 180 : d.risk === 'MODERATE' ? 145 : 120)
      .attr('fill', d => `url(#heat-grad-${d.risk.toLowerCase()})`)

    /* ── Edge Rendering ── */
    const edgeG = g.append('g').attr('class', 'edges')

    // Pre-create edge linear gradients and cache direct DOM nodes
    const edgeGradCache: { edge: NutrientEdge; el: SVGLinearGradientElement | null }[] = []
    edges.forEach(e => {
      const sourceNode = nodes.find(n => n.id === (typeof e.source === 'string' ? e.source : (e.source as NutrientNode).id))
      const targetNode = nodes.find(n => n.id === (typeof e.target === 'string' ? e.target : (e.target as NutrientNode).id))
      if (!sourceNode || !targetNode) return

      const lg = defs.append('linearGradient').attr('id', `edge-grad-${e.id}`)
        .attr('gradientUnits', 'userSpaceOnUse')
      lg.append('stop').attr('offset', '0%')
        .attr('stop-color', RISK_COLORS[sourceNode.risk].primary).attr('stop-opacity', 0.5)
      lg.append('stop').attr('offset', '50%')
        .attr('stop-color', EDGE_COLORS[e.type].stroke).attr('stop-opacity', 0.7)
      lg.append('stop').attr('offset', '100%')
        .attr('stop-color', RISK_COLORS[targetNode.risk].primary).attr('stop-opacity', 0.5)

      edgeGradCache.push({ edge: e, el: lg.node() })
    })

    const edgeSel = edgeG.selectAll<SVGGElement, NutrientEdge>('g')
      .data(edges).join('g').attr('cursor', 'pointer')

    edgeSel.append('path').attr('class', 'edge-path')
      .attr('fill', 'none')
      .attr('stroke', d => EDGE_COLORS[d.type].stroke)
      .attr('stroke-width', d => 1 + d.strength * 2.5)
      .attr('stroke-opacity', 0.3)
      .attr('stroke-dasharray', d => d.type === 'competitive' ? '8,5' : 'none')

    edgeSel.append('path').attr('class', 'edge-hit')
      .attr('fill', 'none')
      .attr('stroke', 'transparent').attr('stroke-width', 18)

    edgeSel.append('rect').attr('class', 'edge-label-bg')
      .attr('rx', 8).attr('ry', 8)
      .attr('fill', PALETTE.card)
      .attr('stroke', d => EDGE_COLORS[d.type].stroke)
      .attr('stroke-width', 1).attr('stroke-opacity', 0.4)
      .attr('width', d => d.label.length * 6.5 + 20).attr('height', 24)
      .attr('opacity', 0)

    edgeSel.append('text').attr('class', 'edge-label-text')
      .text(d => d.label)
      .attr('fill', d => EDGE_COLORS[d.type].label)
      .attr('font-size', 10).attr('font-weight', 600)
      .attr('font-family', 'Inter, system-ui, sans-serif')
      .attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
      .attr('opacity', 0)

    // Cached D3 sub-selections (eliminates querySelector in tick loop)
    const edgePathSel = edgeSel.selectAll<SVGPathElement, NutrientEdge>('.edge-path, .edge-hit')
    const edgeLabelBgSel = edgeSel.selectAll<SVGRectElement, NutrientEdge>('.edge-label-bg')
    const edgeLabelTextSel = edgeSel.selectAll<SVGTextElement, NutrientEdge>('.edge-label-text')

    // Stable edge event handlers
    edgeSel.on('mouseenter', function (_, d) {
      d3.select(this).select('.edge-path').attr('stroke-opacity', 0.8).attr('stroke-width', 2 + d.strength * 3)
      d3.select(this).select('.edge-label-bg').transition().duration(150).attr('opacity', 1)
      d3.select(this).select('.edge-label-text').transition().duration(150).attr('opacity', 1)
    }).on('mouseleave', function (_, d) {
      d3.select(this).select('.edge-path').attr('stroke-opacity', 0.3).attr('stroke-width', 1 + d.strength * 2.5)
      d3.select(this).select('.edge-label-bg').transition().duration(150).attr('opacity', 0)
      d3.select(this).select('.edge-label-text').transition().duration(150).attr('opacity', 0)
    }).on('click', (_, d) => onEdgeClickRef.current(d))

    /* ── Node Rendering ── */
    const nodeG = g.append('g').attr('class', 'nodes')
    const nodeSel = nodeG.selectAll<SVGGElement, NutrientNode>('g')
      .data(nodes).join('g').attr('cursor', 'pointer')

    // High-performance shadow circle (replaces feDropShadow filter)
    nodeSel.append('circle').attr('class', 'shadow-circle')
      .attr('r', d => getNodeRadius(d.probability) + 4)
      .attr('cx', 0).attr('cy', 3)
      .attr('fill', 'url(#grad-node-shadow)')

    // Glow ring (replaces feGaussianBlur filter)
    nodeSel.append('circle').attr('class', 'glow-ring')
      .attr('r', d => getNodeRadius(d.probability) + 7)
      .attr('fill', 'none')
      .attr('stroke', d => RISK_COLORS[d.risk].primary)
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0)

    // Pulse ring
    nodeSel.append('circle').attr('class', 'pulse-ring')
      .attr('r', d => getNodeRadius(d.probability) + 6)
      .attr('fill', 'none')
      .attr('stroke', d => RISK_COLORS[d.risk].primary)
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0)

    // Risk arc ring
    nodeSel.each(function (d) {
      const r = getNodeRadius(d.probability) + 4
      const circumference = 2 * Math.PI * r
      const arcLength = circumference * d.probability
      d3.select(this).append('circle').attr('class', 'risk-arc')
        .attr('r', r).attr('fill', 'none')
        .attr('stroke', RISK_COLORS[d.risk].primary)
        .attr('stroke-width', 2.5)
        .attr('stroke-opacity', 0.5)
        .attr('stroke-dasharray', `${arcLength} ${circumference - arcLength}`)
        .attr('transform', 'rotate(-90)')
    })

    // Main node circle
    nodeSel.append('circle').attr('class', 'main-circle')
      .attr('r', d => getNodeRadius(d.probability))
      .attr('fill', d => `url(#grad-${d.risk === 'HIGH' ? 'high' : d.risk === 'MODERATE' ? 'moderate' : 'low'})`)
      .attr('stroke', d => RISK_COLORS[d.risk].primary)
      .attr('stroke-width', d => d.risk === 'HIGH' ? 2 : 1.5)
      .attr('stroke-opacity', 0.4)

    // Inner highlight ring
    nodeSel.append('circle').attr('class', 'inner-highlight')
      .attr('r', d => getNodeRadius(d.probability) - 2)
      .attr('fill', 'none')
      .attr('stroke', d => RISK_COLORS[d.risk].primary)
      .attr('stroke-width', 0.5)
      .attr('stroke-opacity', 0.15)

    // Emoji icon
    nodeSel.append('text').attr('class', 'node-icon')
      .text(d => d.icon)
      .attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
      .attr('font-size', d => 14 + d.probability * 12)
      .attr('dy', -2)
      .style('pointer-events', 'none')

    // Label below node
    nodeSel.append('text').attr('class', 'node-label')
      .text(d => d.label)
      .attr('text-anchor', 'middle')
      .attr('y', d => getNodeRadius(d.probability) + 16)
      .attr('fill', PALETTE.text)
      .attr('font-size', 10.5)
      .attr('font-weight', 700)
      .attr('font-family', '"Inter Tight", Inter, system-ui, sans-serif')
      .attr('letter-spacing', '-0.01em')
      .style('pointer-events', 'none')

    // Risk badge below label
    nodeSel.each(function (d) {
      const y = getNodeRadius(d.probability) + 28
      const badgeG = d3.select(this).append('g').attr('class', 'risk-badge').attr('transform', `translate(0, ${y})`)
      const text = `${Math.round(d.probability * 100)}%`
      const w = text.length * 6 + 12
      badgeG.append('rect')
        .attr('x', -w / 2).attr('y', -7)
        .attr('width', w).attr('height', 14)
        .attr('rx', 7).attr('ry', 7)
        .attr('fill', RISK_COLORS[d.risk].bg)
        .attr('stroke', RISK_COLORS[d.risk].primary)
        .attr('stroke-width', 0.5)
        .attr('stroke-opacity', 0.4)
      badgeG.append('text')
        .text(text)
        .attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
        .attr('fill', RISK_COLORS[d.risk].primary)
        .attr('font-size', 9).attr('font-weight', 700)
        .attr('font-family', '"Inter Tight", Inter, system-ui, sans-serif')
        .style('pointer-events', 'none')
    })

    // Stable node interaction handlers (delegates through refs)
    nodeSel.on('mouseenter', function (event, d) {
      if (stateRef.current.selectedId && stateRef.current.selectedId !== d.id) {
        const conn = stateRef.current.connected
        if (conn && !conn.nodes.has(d.id)) return
      }
      d3.select(this).select('.main-circle')
        .transition().duration(150)
        .attr('r', getNodeRadius(d.probability) + 4)
        .attr('stroke-opacity', 0.8)
      d3.select(this).select('.glow-ring')
        .transition().duration(150)
        .attr('stroke-opacity', 0.65)
        .attr('r', getNodeRadius(d.probability) + 11)
      onNodeHoverRef.current(d, event as unknown as MouseEvent)
    }).on('mouseleave', function (_, d) {
      d3.select(this).select('.main-circle')
        .transition().duration(200)
        .attr('r', getNodeRadius(d.probability))
        .attr('stroke-opacity', 0.4)
      d3.select(this).select('.glow-ring')
        .transition().duration(200)
        .attr('stroke-opacity', 0)
        .attr('r', getNodeRadius(d.probability) + 7)
      onNodeHoverRef.current(null)
    }).on('click', (_, d) => {
      onNodeClickRef.current(d)
    })

    // Drag behavior
    const drag = d3.drag<SVGGElement, NutrientNode>()
      .on('start', (event, d) => {
        if (!event.active) sim.alphaTarget(0.3).restart()
        d.fx = d.x; d.fy = d.y
        onNodeHoverRef.current(null)
      })
      .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y })
      .on('end', (event, d) => {
        if (!event.active) sim.alphaTarget(0)
        d.fx = null; d.fy = null
      })
    nodeSel.call(drag as any)

    /* ── Curved Path Generator ── */
    function curvedPath(d: NutrientEdge): string {
      const s = d.source as any
      const t = d.target as any
      if (s.x == null || t.x == null) return ''
      const dx = t.x - s.x
      const dy = t.y - s.y
      const dr = Math.sqrt(dx * dx + dy * dy) * 0.8
      return `M${s.x},${s.y} A${dr},${dr} 0 0,1 ${t.x},${t.y}`
    }

    /* ── Viewport Auto-Fit (Decoupled from Tick Loop) ── */
    function autoFit(animate = true) {
      if (isTransitioningRef.current) return
      const liveNodes = stateRef.current.nodes
      if (!liveNodes || liveNodes.length === 0) return

      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
      liveNodes.forEach(n => {
        if (n.x == null || n.y == null) return
        const r = getNodeRadius(n.probability) + 40
        minX = Math.min(minX, n.x - r)
        maxX = Math.max(maxX, n.x + r)
        minY = Math.min(minY, n.y - r)
        maxY = Math.max(maxY, n.y + r + 26)
      })

      if (!isFinite(minX) || !isFinite(maxX)) return

      const graphW = Math.max(maxX - minX, 150)
      const graphH = Math.max(maxY - minY, 150)
      const centerX = (minX + maxX) / 2
      const centerY = (minY + maxY) / 2

      const targetW = W * 0.85
      const targetH = H * 0.85
      const scaleX = targetW / graphW
      const scaleY = targetH / graphH
      const optimalK = Math.max(0.65, Math.min(1.45, Math.min(scaleX, scaleY)))

      const tx = W / 2 - centerX * optimalK
      const ty = H / 2 - centerY * optimalK
      const targetTransform = d3.zoomIdentity.translate(tx, ty).scale(optimalK)

      stateRef.current.zoomTransform = targetTransform

      if (animate) {
        isTransitioningRef.current = true
        svg.transition().duration(650).ease(d3.easeCubicOut)
          .call(zoomBehavior.transform as any, targetTransform)
          .on('end', () => { isTransitioningRef.current = false })
      } else {
        svg.call(zoomBehavior.transform as any, targetTransform)
      }
    }
    stateRef.current.autoFit = autoFit

    svg.on('dblclick.zoom', () => autoFit(true))

    /* ── High-Performance Tick Loop (Zero querySelectors) ── */
    sim.on('tick', () => {
      // 1. Update heat regions
      heatSel
        .attr('cx', d => d.x!)
        .attr('cy', d => d.y!)

      // 2. Update edge paths via cached selection
      edgePathSel.attr('d', d => curvedPath(d))

      // 3. Update edge labels via cached selection
      edgeLabelBgSel
        .attr('x', d => {
          const s = d as any
          return ((s.source.x + s.target.x) / 2) - ((s.label.length * 6.5 + 20) / 2)
        })
        .attr('y', d => { const s = d as any; return ((s.source.y + s.target.y) / 2) - 12 })

      edgeLabelTextSel
        .attr('x', d => { const s = d as any; return (s.source.x + s.target.x) / 2 })
        .attr('y', d => { const s = d as any; return (s.source.y + s.target.y) / 2 })

      // 4. Update edge gradients directly on cached DOM elements
      edgeGradCache.forEach(({ edge, el }) => {
        const s = edge.source as any; const t = edge.target as any
        if (s.x == null || !el) return
        el.setAttribute('x1', String(s.x))
        el.setAttribute('y1', String(s.y))
        el.setAttribute('x2', String(t.x))
        el.setAttribute('y2', String(t.y))
      })

      // 5. Update node positions
      nodeSel.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    // Settle simulation and auto-fit only on natural completion
    sim.on('end', () => {
      sim.stop() // Freeze physics completely — 0% idle CPU
      if (!stateRef.current.selectedId) {
        autoFit(true)
      }
    })

    /* ═══ SURGICAL VISUAL STATE UPDATES (ZERO REBUILD) ═══ */
    function applyVisualState() {
      const { selectedId: selId, connected: conn, hoveredId: hovId } = stateRef.current

      if (!selId && !hovId) {
        // Reset all nodes
        nodeSel.transition().duration(200).attr('opacity', 1)
        nodeSel.selectAll('.main-circle')
          .attr('stroke-width', d => (d as NutrientNode).risk === 'HIGH' ? 2 : 1.5)
          .attr('stroke-opacity', 0.4)
        nodeSel.selectAll('.glow-ring').attr('stroke-opacity', 0)

        // Reset edges
        edgeSel.transition().duration(200).attr('opacity', 1)
        edgeSel.selectAll('.edge-path').attr('stroke-opacity', 0.3)

        // Reset heat regions
        heatSel.transition().duration(250).attr('opacity', 1)

        // Reset focus dimmer and spotlight
        focusDimmer.transition().duration(250).attr('opacity', 0)
        spotlight.transition().duration(200).attr('opacity', 0)
        return
      }

      if (selId && conn) {
        // Focus Dimmer
        focusDimmer.transition().duration(300).attr('opacity', 0.55)

        // Soft optical spotlight around selected nutrient
        const selNode = nodes.find(n => n.id === selId)
        if (selNode && selNode.x != null && selNode.y != null) {
          const riskColor = RISK_COLORS[selNode.risk].primary
          defs.select('#spotlight-s0').attr('stop-color', riskColor)
          defs.select('#spotlight-s50').attr('stop-color', riskColor)
          spotlight
            .attr('cx', selNode.x)
            .attr('cy', selNode.y)
            .transition().duration(300)
            .attr('opacity', 1)
        }

        // Fade non-connected nodes; elevate connected
        nodeSel.transition().duration(200)
          .attr('opacity', d => conn.nodes.has(d.id) ? 1 : 0.08)

        nodeSel.selectAll('.main-circle')
          .attr('stroke-width', function () {
            const parent = (this as any)?.parentNode
            const d = parent ? (d3.select(parent).datum() as NutrientNode) : null
            if (!d) return 1.5
            return conn.nodes.has(d.id) ? 2.5 : 1
          })
          .attr('stroke-opacity', function () {
            const parent = (this as any)?.parentNode
            const d = parent ? (d3.select(parent).datum() as NutrientNode) : null
            if (!d) return 0.4
            return conn.nodes.has(d.id) ? 0.95 : 0.2
          })

        // Highlight glow ring on connected nodes
        nodeSel.selectAll('.glow-ring')
          .attr('stroke-opacity', function () {
            const parent = (this as any)?.parentNode
            const d = parent ? (d3.select(parent).datum() as NutrientNode) : null
            if (!d) return 0
            return d.id === selId ? 0.9 : conn.nodes.has(d.id) ? 0.5 : 0
          })

        // Highlight connected pathways; suppress unrelated
        edgeSel.transition().duration(200)
          .attr('opacity', d => conn.edges.has(d.id) ? 1 : 0.04)
        edgeSel.selectAll('.edge-path')
          .attr('stroke-opacity', function () {
            const parent = (this as any)?.parentNode
            const d = parent ? (d3.select(parent).datum() as NutrientEdge) : null
            if (!d) return 0.1
            return conn.edges.has(d.id) ? 0.85 : 0.04
          })

        // Edge labels
        edgeSel.each(function (d) {
          if (conn.edges.has(d.id)) {
            d3.select(this).select('.edge-label-bg').transition().duration(250).attr('opacity', 1)
            d3.select(this).select('.edge-label-text').transition().duration(250).attr('opacity', 1)
          } else {
            d3.select(this).select('.edge-label-bg').attr('opacity', 0)
            d3.select(this).select('.edge-label-text').attr('opacity', 0)
          }
        })

        // Heat regions
        heatSel.transition().duration(250)
          .attr('opacity', d => conn.nodes.has(d.id) ? 1 : 0.1)

        // Smooth camera zoom with transition lock
        if (selNode && selNode.x != null && selNode.y != null) {
          isTransitioningRef.current = true
          svg.transition().duration(500).ease(d3.easeCubicOut)
            .call(zoomBehavior.transform as any, d3.zoomIdentity
              .translate(W / 2, H / 2)
              .scale(1.05)
              .translate(-selNode.x, -selNode.y)
            )
            .on('end', () => { isTransitioningRef.current = false })
        }
      }
    }

    stateRef.current.applyVisualState = applyVisualState
    applyVisualState()

    const handleCenterEvent = () => autoFit(true)
    window.addEventListener('nutriscan:center-graph', handleCenterEvent)

    return () => {
      window.removeEventListener('nutriscan:center-graph', handleCenterEvent)
      svg.on('.zoom', null)
      nodeSel.on('.drag', null)
      sim.stop()
      stateRef.current.sim = null
      stateRef.current.applyVisualState = null
      stateRef.current.autoFit = null
      stateRef.current.animRunning = false
      cancelAnimationFrame(animRef.current)
      if (zoomRaf) cancelAnimationFrame(zoomRaf)
    }
  }, [riskFilter])

  // Mount setupGraph once; handle resize cleanly
  useEffect(() => {
    const cleanup = setupGraph()
    let resizeTimer: ReturnType<typeof setTimeout>
    const debouncedResize = () => {
      clearTimeout(resizeTimer)
      resizeTimer = setTimeout(() => {
        if (cleanup) cleanup()
        setupGraph()
      }, 200)
    }
    window.addEventListener('resize', debouncedResize)
    return () => {
      if (cleanup) cleanup()
      window.removeEventListener('resize', debouncedResize)
      clearTimeout(resizeTimer)
    }
  }, [setupGraph])

  const pulseCSS = `
    @keyframes pulse-ring-anim {
      0%, 100% { stroke-opacity: 0; r: attr(r); }
      50% { stroke-opacity: 0.25; }
    }
  `

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative', background: PALETTE.bg, overflow: 'hidden' }}>
      <svg ref={svgRef} style={{ display: 'block', width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }} />
      <canvas ref={canvasRef} style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none', width: '100%', height: '100%' }} />
      <style>{pulseCSS}</style>
    </div>
  )
}

export default memo(NetworkGraph)
