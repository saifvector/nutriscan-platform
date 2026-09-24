/**
 * riskFilter.test.ts
 * Comprehensive test suite verifying Network Intelligence Risk Filter system:
 * - High filter isolation
 * - Moderate filter isolation
 * - Low filter isolation
 * - All filter graph restoration
 * - Connected edge pruning
 * - Dynamic statistics calculation
 * - Console diagnostics emission
 */

import {
  NODES,
  EDGES,
  getFilteredNetworkData,
  getAggregateStats,
  updateNodesWithPredictions,
  type RiskLevel,
} from '../NetworkData.ts'

function assert(condition: boolean, message: string) {
  if (!condition) {
    console.error(`❌ ASSERTION FAILED: ${message}`)
    throw new Error(message)
  }
}

console.log('🧪 Starting Network Intelligence Risk Filter Audit Tests...\n')

// Apply test predictions fixture to ensure HIGH, MODERATE, and LOW nodes are present for filter verification
updateNodesWithPredictions([
  { target_name: 'Iron Deficiency', calibrated_probability: 0.74, risk_tier: 'HIGH' },
  { target_name: 'Vitamin D Insufficiency', calibrated_probability: 0.87, risk_tier: 'HIGH' },
  { target_name: 'Calcium Deficiency', calibrated_probability: 0.45, risk_tier: 'MODERATE' },
  { target_name: 'Magnesium Deficiency', calibrated_probability: 0.35, risk_tier: 'MODERATE' },
  { target_name: 'Folate Deficiency', calibrated_probability: 0.05, risk_tier: 'LOW' },
  { target_name: 'Zinc Deficiency', calibrated_probability: 0.02, risk_tier: 'LOW' },
])

// Test 1: Intercept console diagnostics to verify Requirement 8
const diagnosticsCaptured: string[] = []
const originalLog = console.log
console.log = (...args: any[]) => {
  diagnosticsCaptured.push(args.join(' '))
  originalLog(...args)
}

// ─── TEST 1: HIGH FILTER ───
console.log('\n--- Testing HIGH Risk Filter ---')
diagnosticsCaptured.length = 0
const highData = getFilteredNetworkData('HIGH')

assert(highData.visibleNodes.length > 0, 'HIGH filter must return visible nodes')
assert(
  highData.visibleNodes.every(n => n.risk === 'HIGH' && n.risk_level === 'HIGH'),
  'Every visible node in HIGH filter must have risk === "HIGH" and risk_level === "HIGH"'
)
assert(
  highData.hiddenNodes.every(n => n.risk !== 'HIGH'),
  'Hidden nodes in HIGH filter must not contain any HIGH risk nodes'
)
assert(
  highData.visibleNodes.length + highData.hiddenNodes.length === NODES.length,
  'Visible + hidden nodes in HIGH filter must equal total NODES'
)

// Verify edge pruning: all visible edges must only connect visible HIGH nodes
const highNodeIds = new Set(highData.visibleNodes.map(n => n.id))
highData.visibleEdges.forEach(edge => {
  const src = typeof edge.source === 'object' ? (edge.source as any).id : edge.source
  const tgt = typeof edge.target === 'object' ? (edge.target as any).id : edge.target
  assert(
    highNodeIds.has(src) && highNodeIds.has(tgt),
    `Visible edge ${edge.id} connects to non-HIGH node (${src} -> ${tgt})`
  )
})

// Verify hidden edges: every edge connected to a hidden node must be in hiddenEdges
highData.hiddenEdges.forEach(edge => {
  const src = typeof edge.source === 'object' ? (edge.source as any).id : edge.source
  const tgt = typeof edge.target === 'object' ? (edge.target as any).id : edge.target
  assert(
    !highNodeIds.has(src) || !highNodeIds.has(tgt),
    `Hidden edge ${edge.id} incorrectly classified: both nodes are visible`
  )
})
assert(
  highData.visibleEdges.length + highData.hiddenEdges.length === EDGES.length,
  'Visible + hidden edges in HIGH filter must equal total EDGES'
)

// Verify dynamic statistics for HIGH filter
const highStats = getAggregateStats(highData.visibleNodes, highData.visibleEdges)
assert(highStats.totalNutrients === highData.visibleNodes.length, 'totalNutrients must equal visibleNodes.length')
assert(highStats.highRiskCount === highData.visibleNodes.length, 'highRiskCount must equal visibleNodes.length')
assert(highStats.totalInteractions === highData.visibleEdges.length, 'totalInteractions must equal visibleEdges.length')
assert(highStats.avgRisk >= 70, 'Average risk for HIGH filter nodes should be high (>= 70%)')

// Verify console diagnostics format for HIGH
assert(diagnosticsCaptured.some(d => d.includes('Selected Filter: HIGH')), 'Diagnostics must contain "Selected Filter: HIGH"')
assert(diagnosticsCaptured.some(d => d.includes(`Visible Nodes: ${highData.visibleNodes.length}`)), 'Diagnostics must report Visible Nodes')
assert(diagnosticsCaptured.some(d => d.includes(`Visible Edges: ${highData.visibleEdges.length}`)), 'Diagnostics must report Visible Edges')
assert(diagnosticsCaptured.some(d => d.includes(`Hidden Nodes: ${highData.hiddenNodes.length}`)), 'Diagnostics must report Hidden Nodes')
assert(diagnosticsCaptured.some(d => d.includes(`Hidden Edges: ${highData.hiddenEdges.length}`)), 'Diagnostics must report Hidden Edges')
console.log('✅ HIGH filter passed: only HIGH nodes rendered, unrelated edges pruned, stats recalculated.')


// ─── TEST 2: MODERATE FILTER ───
console.log('\n--- Testing MODERATE Risk Filter ---')
diagnosticsCaptured.length = 0
const modData = getFilteredNetworkData('MODERATE')

assert(modData.visibleNodes.length > 0, 'MODERATE filter must return visible nodes')
assert(
  modData.visibleNodes.every(n => n.risk === 'MODERATE' && n.risk_level === 'MODERATE'),
  'Every visible node in MODERATE filter must have risk === "MODERATE" and risk_level === "MODERATE"'
)
assert(
  modData.hiddenNodes.every(n => n.risk !== 'MODERATE'),
  'Hidden nodes in MODERATE filter must not contain any MODERATE risk nodes'
)
assert(
  modData.visibleNodes.length + modData.hiddenNodes.length === NODES.length,
  'Visible + hidden nodes in MODERATE filter must equal total NODES'
)

const modNodeIds = new Set(modData.visibleNodes.map(n => n.id))
modData.visibleEdges.forEach(edge => {
  const src = typeof edge.source === 'object' ? (edge.source as any).id : edge.source
  const tgt = typeof edge.target === 'object' ? (edge.target as any).id : edge.target
  assert(
    modNodeIds.has(src) && modNodeIds.has(tgt),
    `Visible edge ${edge.id} connects to non-MODERATE node (${src} -> ${tgt})`
  )
})

const modStats = getAggregateStats(modData.visibleNodes, modData.visibleEdges)
assert(modStats.totalNutrients === modData.visibleNodes.length, 'totalNutrients must equal visibleNodes.length')
assert(modStats.highRiskCount === 0, 'highRiskCount must be 0 for MODERATE filter')
assert(modStats.totalInteractions === modData.visibleEdges.length, 'totalInteractions must equal visibleEdges.length')
console.log('✅ MODERATE filter passed: only MODERATE nodes rendered, unrelated edges pruned, stats recalculated.')


// ─── TEST 3: LOW FILTER ───
console.log('\n--- Testing LOW Risk Filter ---')
diagnosticsCaptured.length = 0
const lowData = getFilteredNetworkData('LOW')

assert(lowData.visibleNodes.length > 0, 'LOW filter must return visible nodes')
assert(
  lowData.visibleNodes.every(n => n.risk === 'LOW' && n.risk_level === 'LOW'),
  'Every visible node in LOW filter must have risk === "LOW" and risk_level === "LOW"'
)
assert(
  lowData.hiddenNodes.every(n => n.risk !== 'LOW'),
  'Hidden nodes in LOW filter must not contain any LOW risk nodes'
)
assert(
  lowData.visibleNodes.length + lowData.hiddenNodes.length === NODES.length,
  'Visible + hidden nodes in LOW filter must equal total NODES'
)

const lowNodeIds = new Set(lowData.visibleNodes.map(n => n.id))
lowData.visibleEdges.forEach(edge => {
  const src = typeof edge.source === 'object' ? (edge.source as any).id : edge.source
  const tgt = typeof edge.target === 'object' ? (edge.target as any).id : edge.target
  assert(
    lowNodeIds.has(src) && lowNodeIds.has(tgt),
    `Visible edge ${edge.id} connects to non-LOW node (${src} -> ${tgt})`
  )
})

const lowStats = getAggregateStats(lowData.visibleNodes, lowData.visibleEdges)
assert(lowStats.totalNutrients === lowData.visibleNodes.length, 'totalNutrients must equal visibleNodes.length')
assert(lowStats.highRiskCount === 0, 'highRiskCount must be 0 for LOW filter')
assert(lowStats.totalInteractions === lowData.visibleEdges.length, 'totalInteractions must equal visibleEdges.length')
console.log('✅ LOW filter passed: only LOW nodes rendered, unrelated edges pruned, stats recalculated.')


// ─── TEST 4: ALL FILTER (COMPLETE GRAPH RESTORATION) ───
console.log('\n--- Testing ALL Risk Filter (Restoration) ---')
diagnosticsCaptured.length = 0
const allData = getFilteredNetworkData(null)

assert(allData.visibleNodes.length === NODES.length, 'ALL filter must restore all nodes')
assert(allData.visibleEdges.length === EDGES.length, 'ALL filter must restore all edges')
assert(allData.hiddenNodes.length === 0, 'ALL filter must have 0 hidden nodes')
assert(allData.hiddenEdges.length === 0, 'ALL filter must have 0 hidden edges')

const allStats = getAggregateStats(allData.visibleNodes, allData.visibleEdges)
assert(allStats.totalNutrients === NODES.length, 'ALL filter totalNutrients must match NODES count')
assert(allStats.totalInteractions === EDGES.length, 'ALL filter totalInteractions must match EDGES count')
assert(allStats.highRiskCount === NODES.filter(n => n.risk === 'HIGH').length, 'ALL filter highRiskCount must match full dataset')
assert(allStats.criticalCascades > 0, 'ALL filter cascades must match full dataset')

assert(diagnosticsCaptured.some(d => d.includes('Selected Filter: All')), 'Diagnostics must contain "Selected Filter: All"')
console.log('✅ ALL filter passed: complete graph and original metrics fully restored.')

// Restore console.log
console.log = originalLog
console.log('\n🎉 ALL 4 FILTER MODES AND RECALCULATIONS PASSED PERFECTLY!\n')
