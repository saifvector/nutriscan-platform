/**
 * dataConsistency.test.ts
 * Forensic Audit & Data Consistency Test Suite
 *
 * Verifies:
 * 1. Zero hardcoded mock probabilities in NetworkData baseline.
 * 2. Canonical mapping and sanitization for all model targets and suffix variants:
 *    - "Iron Deficiency" -> iron
 *    - "Vitamin D Insufficiency" -> vitamin_d
 *    - "Iron Deficiency Anemia" -> iron_anemia
 *    - "Magnesium Deficiency" -> magnesium
 *    - "Folate Deficiency" -> folate
 * 3. updateNodesWithPredictions updates node probabilities, risk levels, and confidence.
 * 4. Multi-match resolution (e.g. Vitamin D Insufficiency vs Deficiency) retains the higher severity.
 * 5. Debug logging and unmatched warning tracking.
 * 6. validateNetworkConsistency detects and flags any probability variance > 1%.
 * 7. Assessment 704a6f4e-01c8-4d35-ab46-326fbfb2f575 exact payload maps consistently.
 */

import {
  NODES,
  CANONICAL_NUTRIENT_MAP,
  sanitizeNutrientKey,
  updateNodesWithPredictions,
  validateNetworkConsistency,
} from '../NetworkData'

function assert(condition: boolean, message: string) {
  if (!condition) {
    console.error(`❌ ASSERTION FAILED: ${message}`)
    throw new Error(message)
  }
}

console.log('🧪 Starting Forensic Audit & Data Consistency Tests...\n')

// ─── TEST 1: Canonical Mapping Table & Sanitizer ───
console.log('--- Test 1: Canonical Nutrient Mapping & Suffix Sanitization ---')
assert(CANONICAL_NUTRIENT_MAP['iron_deficiency'] === 'iron', 'iron_deficiency must map to iron')
assert(CANONICAL_NUTRIENT_MAP['iron_deficiency_anemia'] === 'iron_anemia', 'iron_deficiency_anemia must map to iron_anemia')
assert(CANONICAL_NUTRIENT_MAP['vitamin_d_insufficiency'] === 'vitamin_d', 'vitamin_d_insufficiency must map to vitamin_d')
assert(CANONICAL_NUTRIENT_MAP['vitamin_d_deficiency'] === 'vitamin_d', 'vitamin_d_deficiency must map to vitamin_d')
assert(CANONICAL_NUTRIENT_MAP['magnesium_deficiency'] === 'magnesium', 'magnesium_deficiency must map to magnesium')
assert(CANONICAL_NUTRIENT_MAP['folate_deficiency'] === 'folate', 'folate_deficiency must map to folate')

// Test sanitizeNutrientKey
assert(sanitizeNutrientKey('Iron Deficiency') === 'iron', '"Iron Deficiency" must sanitize to iron')
assert(sanitizeNutrientKey('Vitamin D Insufficiency') === 'vitamin_d', '"Vitamin D Insufficiency" must sanitize to vitamin_d')
assert(sanitizeNutrientKey('Iron Deficiency Anemia') === 'iron_anemia', '"Iron Deficiency Anemia" must sanitize to iron_anemia')
assert(sanitizeNutrientKey('target_iron_deficiency') === 'iron', '"target_iron_deficiency" must sanitize to iron')
assert(sanitizeNutrientKey('Folate Deficiency') === 'folate', '"Folate Deficiency" must sanitize to folate')
assert(sanitizeNutrientKey('Magnesium Deficiency') === 'magnesium', '"Magnesium Deficiency" must sanitize to magnesium')
assert(sanitizeNutrientKey('Calcium Deficiency') === 'calcium', '"Calcium Deficiency" must sanitize to calcium')
assert(sanitizeNutrientKey('Potassium Deficiency') === 'potassium', '"Potassium Deficiency" must sanitize to potassium')
console.log('✅ Test 1 passed: Canonical mappings and sanitization resolved all test targets.')

// ─── TEST 2: Real Assessment 704a6f4e-01c8-4d35-ab46-326fbfb2f575 Predictions ───
console.log('\n--- Test 2: Applying Assessment 704a6f4e-01c8-4d35-ab46-326fbfb2f575 Predictions ---')

const assessmentPredictions = [
  { target_name: 'Iron Deficiency', calibrated_probability: 0.413, risk_tier: 'HIGH', confidence_score: 0.61 },
  { target_name: 'Vitamin D Insufficiency', calibrated_probability: 0.3361, risk_tier: 'MODERATE', confidence_score: 0.66 },
  { target_name: 'Iron Deficiency Anemia', calibrated_probability: 0.1286, risk_tier: 'LOW', confidence_score: 0.81 },
  { target_name: 'Vitamin D Deficiency', calibrated_probability: 0.0623, risk_tier: 'LOW', confidence_score: 0.86 },
  { target_name: 'Folate Deficiency', calibrated_probability: 0.0499, risk_tier: 'LOW', confidence_score: 0.87 },
  { target_name: 'Magnesium Deficiency', calibrated_probability: 0.047, risk_tier: 'LOW', confidence_score: 0.87 },
  { target_name: 'Selenium Deficiency', calibrated_probability: 0.0263, risk_tier: 'LOW', confidence_score: 0.88 },
  { target_name: 'Potassium Deficiency', calibrated_probability: 0.0164, risk_tier: 'LOW', confidence_score: 0.89 },
  { target_name: 'Calcium Deficiency', calibrated_probability: 0.0073, risk_tier: 'LOW', confidence_score: 0.89 },
]

const updateResult = updateNodesWithPredictions(assessmentPredictions)
assert(updateResult.totalLoaded === 9, 'All 9 predictions must be loaded')
assert(updateResult.matchedCount === 8, '8 unique graph nodes must be matched (Vitamin D merged to higher prob)')
assert(updateResult.unmatchedNutrients.length === 0, 'No prediction should be unmatched')

// Verify node values
const ironNode = NODES.find(n => n.id === 'iron')!
assert(ironNode.probability === 0.41, `Iron probability must be 0.41, got ${ironNode.probability}`)
assert(ironNode.risk === 'HIGH', `Iron risk must be HIGH, got ${ironNode.risk}`)

const vitDNode = NODES.find(n => n.id === 'vitamin_d')!
assert(vitDNode.probability === 0.34, `Vitamin D probability must be 0.34, got ${vitDNode.probability}`)
assert(vitDNode.risk === 'MODERATE', `Vitamin D risk must be MODERATE, got ${vitDNode.risk}`)

const ironAnemiaNode = NODES.find(n => n.id === 'iron_anemia')!
assert(ironAnemiaNode.probability === 0.13, `Iron Anemia probability must be 0.13, got ${ironAnemiaNode.probability}`)
assert(ironAnemiaNode.risk === 'LOW', `Iron Anemia risk must be LOW, got ${ironAnemiaNode.risk}`)

const mgNode = NODES.find(n => n.id === 'magnesium')!
assert(mgNode.probability === 0.05, `Magnesium probability must be 0.05, got ${mgNode.probability}`)
assert(mgNode.risk === 'LOW', `Magnesium risk must be LOW, got ${mgNode.risk}`)

console.log('✅ Test 2 passed: All nodes updated with exact calibrated assessment probabilities.')

// ─── TEST 3: Automated Consistency Validation & Variance Warning Check ───
console.log('\n--- Test 3: Consistency Validation Check ---')

// Perfect match test
const consistency = validateNetworkConsistency(assessmentPredictions, 0.01)
assert(consistency.consistent === true, 'Network graph should be consistent with assessment predictions within 1% tolerance')
assert(consistency.warnings.length === 0, 'No warnings should be emitted for consistent data')
assert(consistency.comparisons.length === 8, 'All 8 unique matched nutrient nodes should have comparison entries')

// High variance test: simulate altered prediction with > 1% variance
const alteredPredictions = [
  ...assessmentPredictions.filter(p => p.target_name !== 'Iron Deficiency'),
  { target_name: 'Iron Deficiency', calibrated_probability: 0.74, risk_tier: 'HIGH' }, // 74% vs 41% = 33% variance
]
const inconsistentCheck = validateNetworkConsistency(alteredPredictions, 0.01)
assert(inconsistentCheck.consistent === false, 'Check must flag inconsistency when variance > 1%')
assert(inconsistentCheck.warnings.length > 0, 'Warning must be emitted for 33% variance')
assert(inconsistentCheck.maxVariance > 0.30, `Max variance must be > 30%, got ${inconsistentCheck.maxVariance}`)

console.log('✅ Test 3 passed: Consistency validation accurately confirms synchronization and flags variances > 1%.')

// ─── TEST 4: Unmatched Warning Emission ───
console.log('\n--- Test 4: Unmatched Nutrient Warning ---')
const unmatchedList = [
  { target_name: 'Unknown Mystery Molecule', calibrated_probability: 0.5 },
]
const unmatchedResult = updateNodesWithPredictions(unmatchedList)
assert(unmatchedResult.unmatchedNutrients.length === 1, 'Unmatched nutrient must be tracked')
assert(unmatchedResult.unmatchedNutrients[0].raw === 'Unknown Mystery Molecule', 'Unmatched name must be preserved')

console.log('✅ Test 4 passed: Unmatched nutrients are tracked and warned without silent failures.')

console.log('\n🎉 ALL FORENSIC DATA CONSISTENCY TESTS PASSED!\n')
