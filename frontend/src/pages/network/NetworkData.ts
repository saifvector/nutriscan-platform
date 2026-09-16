/* ═══════════════════════════════════════════════════════════════════════════
   NetworkData.ts — Phase 7B Clinical Intelligence Data Layer
   ═══════════════════════════════════════════════════════════════════════════ */

/* ─── Type Definitions ─── */

export type RiskLevel = 'HIGH' | 'MODERATE' | 'LOW'
export type EdgeType = 'synergistic' | 'supportive' | 'competitive'
export type ViewMode = 'overview' | 'clinical' | 'food' | 'recovery'

export interface Contributor {
  name: string
  impact: number
  direction: 'risk' | 'protective'
}

export interface NutrientNode extends d3.SimulationNodeDatum {
  id: string
  label: string
  icon: string
  probability: number
  risk: RiskLevel
  confidence: number
  description: string
  symptoms: string[]
  foods: string[]
  bodySystem: string
  influences: string[]
  topContributors: Contributor[]
}

export interface NutrientEdge extends d3.SimulationLinkDatum<NutrientNode> {
  id: string
  source: string
  target: string
  type: EdgeType
  label: string
  strength: number
  explanation: string
  importance: string
  dietaryTip: string
  traceImpact: string
}

export interface ConnectedGraph {
  nodes: Set<string>
  edges: Set<string>
  paths: { nodeId: string; edgeId: string; depth: number }[]
}

/* ─── Risk-Based Sizing Formula ─── */

const BASE_RADIUS = 22
const SCALE_FACTOR = 28

/** Returns the visual radius for a node based on its risk probability */
export function getNodeRadius(probability: number): number {
  return BASE_RADIUS + probability * SCALE_FACTOR
}

/** Pulse speed: higher risk = faster pulse (in seconds per cycle) */
export function getPulseSpeed(probability: number): number {
  return 3.0 - probability * 1.8 // HIGH → 1.4s, LOW → 2.7s
}

/* ─── Risk Color System (Gradient Stops) ─── */

export const RISK_COLORS = {
  HIGH: { primary: '#FF4D4D', secondary: '#FF6B6B', glow: 'rgba(255, 77, 77, 0.4)', bg: 'rgba(255, 77, 77, 0.08)' },
  MODERATE: { primary: '#FFB020', secondary: '#FFCF5C', glow: 'rgba(255, 176, 32, 0.35)', bg: 'rgba(255, 176, 32, 0.08)' },
  LOW: { primary: '#00D68F', secondary: '#38E4AE', glow: 'rgba(0, 214, 143, 0.3)', bg: 'rgba(0, 214, 143, 0.08)' },
} as const

export const EDGE_COLORS = {
  synergistic: { stroke: '#3FB950', glow: 'rgba(63, 185, 80, 0.3)', label: '#3FB950' },
  supportive: { stroke: '#D29922', glow: 'rgba(210, 153, 34, 0.3)', label: '#D29922' },
  competitive: { stroke: '#F85149', glow: 'rgba(248, 81, 73, 0.3)', label: '#F85149' },
} as const

/* ─── Premium Dark Palette ─── */

export const PALETTE = {
  bg: '#06090F',
  surface: '#0D1117',
  card: '#161B22',
  cardHover: '#1C2333',
  border: 'rgba(48, 54, 61, 0.6)',
  borderLight: 'rgba(48, 54, 61, 0.35)',
  text: '#E6EDF3',
  textMuted: '#8B949E',
  textDim: '#484F58',
  accent: '#58A6FF',
  accentGlow: 'rgba(88, 166, 255, 0.15)',
  gridDot: 'rgba(48, 54, 61, 0.5)',
  frostedBg: 'rgba(13, 17, 23, 0.75)',
  frostedBorder: 'rgba(48, 54, 61, 0.4)',
} as const

/* ═══════════════════════════════════════════════════════════════════════════
   NODE DATA — 18 Clinically Relevant Nutrients
   ═══════════════════════════════════════════════════════════════════════════ */

export const NODES: NutrientNode[] = [
  {
    id: 'vitamin_d', label: 'Vitamin D', icon: '☀️', probability: 0.87, risk: 'HIGH', confidence: 0.92, bodySystem: 'Bones & Immunity',
    description: 'The "sunshine vitamin" — a fat-soluble hormone precursor essential for calcium absorption, bone mineralization, and immune modulation.',
    influences: ['Calcium Absorption', 'Bone Mineralization', 'Immune Modulation', 'Mood Regulation'],
    symptoms: ['Bone pain & muscle weakness', 'Chronic fatigue', 'Depression & mood changes', 'Impaired wound healing', 'Frequent infections'],
    foods: ['Wild Salmon (100g)', 'Egg Yolks (2 large)', 'Fortified Milk (1 cup)', 'UV-exposed Mushrooms', 'Cod Liver Oil (1 tsp)'],
    topContributors: [{ name: 'Low Sunlight Exposure', impact: 18.7, direction: 'risk' }, { name: 'Dairy-Free Diet', impact: 12.3, direction: 'risk' }, { name: 'Indoor Lifestyle', impact: 9.1, direction: 'risk' }, { name: 'D3 Supplement', impact: 7.2, direction: 'protective' }],
  },
  {
    id: 'calcium', label: 'Calcium', icon: '🦴', probability: 0.48, risk: 'MODERATE', confidence: 0.79, bodySystem: 'Skeletal System',
    description: 'The most abundant mineral in the body. 99% resides in bones and teeth. Requires Vitamin D for intestinal absorption.',
    influences: ['Bone Density', 'Muscle Contraction', 'Nerve Transmission', 'Heart Rhythm'],
    symptoms: ['Muscle cramps & spasms', 'Numbness in extremities', 'Brittle nails', 'Osteopenia risk', 'Dental problems'],
    foods: ['Greek Yogurt (200g)', 'Sardines with bones', 'Kale (1 cup cooked)', 'Fortified Plant Milk', 'Tofu calcium-set'],
    topContributors: [{ name: 'Vegan Diet', impact: 15.1, direction: 'risk' }, { name: 'Low Vitamin D', impact: 11.4, direction: 'risk' }, { name: 'Calcium supplement', impact: 8.3, direction: 'protective' }],
  },
  {
    id: 'magnesium', label: 'Magnesium', icon: '💤', probability: 0.38, risk: 'LOW', confidence: 0.86, bodySystem: 'Nervous System',
    description: 'Cofactor in 300+ enzymatic reactions. Critical for ATP energy production, nerve transmission, muscle contraction, and DNA synthesis.',
    influences: ['Vitamin D Activation', 'Sleep Quality', 'Stress Response', 'Energy Production'],
    symptoms: ['Sleep disturbances', 'Anxiety & restlessness', 'Muscle cramps', 'Heart palpitations', 'Migraine headaches'],
    foods: ['Pumpkin Seeds (30g)', 'Dark Chocolate 85%+', 'Spinach (1 cup)', 'Almonds (30g)', 'Avocado (1 medium)'],
    topContributors: [{ name: 'High Stress', impact: 9.8, direction: 'risk' }, { name: 'Processed Diet', impact: 7.2, direction: 'risk' }, { name: 'Regular Exercise', impact: 5.1, direction: 'protective' }],
  },
  {
    id: 'iron', label: 'Iron', icon: '🩸', probability: 0.74, risk: 'HIGH', confidence: 0.88, bodySystem: 'Blood & Oxygen',
    description: 'Essential for hemoglobin synthesis and oxygen transport. Exists as heme iron (animal, 15-35% absorption) and non-heme iron (plant, 2-20%).',
    influences: ['Oxygen Transport', 'Energy Metabolism', 'Cognitive Function', 'Immune Defense'],
    symptoms: ['Chronic fatigue & weakness', 'Pale skin & conjunctiva', 'Shortness of breath', 'Cold hands & feet', 'Restless leg syndrome'],
    foods: ['Beef Liver (85g)', 'Lentils (1 cup)', 'Spinach + Lemon juice', 'Fortified Cereals', 'Pumpkin Seeds (30g)'],
    topContributors: [{ name: 'Vegan Diet', impact: 23.4, direction: 'risk' }, { name: 'Chronic Fatigue', impact: 14.2, direction: 'risk' }, { name: 'Iron Supplement', impact: 11.8, direction: 'protective' }],
  },
  {
    id: 'vitamin_c', label: 'Vitamin C', icon: '🍊', probability: 0.31, risk: 'LOW', confidence: 0.90, bodySystem: 'Immune & Skin',
    description: 'Powerful water-soluble antioxidant. Essential for collagen synthesis, immune defense, and iron absorption enhancement.',
    influences: ['Iron Absorption', 'Collagen Synthesis', 'Antioxidant Defense', 'Immune Response'],
    symptoms: ['Easy bruising', 'Slow wound healing', 'Dry & rough skin', 'Frequent colds', 'Joint pain'],
    foods: ['Orange Bell Pepper (1)', 'Kiwi Fruit (2)', 'Strawberries (1 cup)', 'Broccoli (1 cup)', 'Citrus Fruits'],
    topContributors: [{ name: 'Low Fruit Intake', impact: 7.6, direction: 'risk' }, { name: 'Smoking', impact: 4.2, direction: 'risk' }, { name: 'Regular Citrus', impact: 6.8, direction: 'protective' }],
  },
  {
    id: 'vitamin_b12', label: 'Vitamin B12', icon: '🧠', probability: 0.62, risk: 'MODERATE', confidence: 0.85, bodySystem: 'Brain & Nerves',
    description: 'Critical for myelin sheath maintenance, DNA synthesis, and red blood cell formation. Found almost exclusively in animal products.',
    influences: ['Myelin Maintenance', 'DNA Synthesis', 'Red Blood Cells', 'Homocysteine Metabolism'],
    symptoms: ['Cognitive fog & confusion', 'Tingling in hands/feet', 'Balance problems', 'Megaloblastic anemia', 'Mood disturbances'],
    foods: ['Beef Liver (85g)', 'Nutritional Yeast fortified', 'Clams (85g)', 'Fortified Cereals', 'Eggs (2 large)'],
    topContributors: [{ name: 'Vegan Diet', impact: 19.5, direction: 'risk' }, { name: 'Low Stomach Acid', impact: 6.3, direction: 'risk' }, { name: 'B12 Supplement', impact: 9.7, direction: 'protective' }],
  },
  {
    id: 'folate', label: 'Folate', icon: '🧬', probability: 0.55, risk: 'MODERATE', confidence: 0.81, bodySystem: 'Cell Division',
    description: 'Vitamin B9 — essential for DNA synthesis, cell division, and amino acid metabolism. Works with B12 in the methionine cycle.',
    influences: ['DNA Synthesis', 'Cell Division', 'Neural Tube Formation', 'Amino Acid Metabolism'],
    symptoms: ['Fatigue & weakness', 'Mouth sores', 'Gray hair changes', 'Swollen tongue', 'Growth problems'],
    foods: ['Lentils (1 cup)', 'Spinach (1 cup)', 'Asparagus (6 spears)', 'Black-eyed Peas', 'Broccoli (1 cup)'],
    topContributors: [{ name: 'Low Leafy Greens', impact: 11.2, direction: 'risk' }, { name: 'Alcohol Use', impact: 5.8, direction: 'risk' }, { name: 'Prenatal Supplement', impact: 8.4, direction: 'protective' }],
  },
  {
    id: 'zinc', label: 'Zinc', icon: '🛡️', probability: 0.42, risk: 'MODERATE', confidence: 0.83, bodySystem: 'Immune Defense',
    description: 'Trace mineral essential for 100+ enzyme functions, immune response, wound healing, and DNA synthesis.',
    influences: ['Immune Function', 'Wound Healing', 'Taste & Smell', 'Vitamin A Transport'],
    symptoms: ['Impaired immunity', 'Loss of taste/smell', 'Slow wound healing', 'Hair loss', 'Skin lesions'],
    foods: ['Oysters (6 medium)', 'Beef (100g)', 'Pumpkin Seeds (30g)', 'Chickpeas (1 cup)', 'Cashews (30g)'],
    topContributors: [{ name: 'Plant-Based Diet', impact: 10.6, direction: 'risk' }, { name: 'High Phytates', impact: 7.1, direction: 'risk' }, { name: 'Zinc Lozenges', impact: 4.5, direction: 'protective' }],
  },
  {
    id: 'protein', label: 'Protein', icon: '💪', probability: 0.18, risk: 'LOW', confidence: 0.91, bodySystem: 'Muscle & Structure',
    description: 'Macronutrient composed of amino acids. Essential for muscle synthesis, enzyme production, and immune antibody formation.',
    influences: ['Muscle Synthesis', 'Enzyme Production', 'Zinc Bioavailability', 'Satiety'],
    symptoms: ['Muscle wasting', 'Edema/swelling', 'Brittle hair & nails', 'Slow recovery', 'Weakened immunity'],
    foods: ['Chicken Breast (150g)', 'Greek Yogurt (200g)', 'Lentils (1 cup)', 'Eggs (3 large)', 'Tofu firm (150g)'],
    topContributors: [{ name: 'Adequate Legumes', impact: 6.2, direction: 'protective' }, { name: 'Regular Exercise', impact: 8.9, direction: 'protective' }],
  },
  {
    id: 'vitamin_a', label: 'Vitamin A', icon: '👁️', probability: 0.25, risk: 'LOW', confidence: 0.87, bodySystem: 'Vision & Skin',
    description: 'Fat-soluble vitamin in two forms: preformed retinol (animal) and provitamin carotenoids (plants). Essential for vision and immunity.',
    influences: ['Night Vision', 'Skin Integrity', 'Immune Function', 'Gene Expression'],
    symptoms: ['Night blindness', 'Dry eyes', 'Rough/dry skin', 'Frequent infections', 'Poor wound healing'],
    foods: ['Sweet Potato (1 medium)', 'Beef Liver (85g)', 'Carrots (1 cup)', 'Spinach (1 cup)', 'Cantaloupe (1 cup)'],
    topContributors: [{ name: 'Low Zinc (transport)', impact: 5.3, direction: 'risk' }, { name: 'Regular Carrots', impact: 7.8, direction: 'protective' }],
  },
  {
    id: 'vitamin_e', label: 'Vitamin E', icon: '✨', probability: 0.14, risk: 'LOW', confidence: 0.89, bodySystem: 'Antioxidant Shield',
    description: 'Fat-soluble antioxidant that protects cell membranes from oxidative damage. Regenerated by Vitamin C.',
    influences: ['Cell Membrane Protection', 'Antioxidant Defense', 'Skin Health', 'Immune Support'],
    symptoms: ['Muscle weakness', 'Vision problems', 'Impaired immunity', 'Numbness & tingling', 'Difficulty walking'],
    foods: ['Almonds (30g)', 'Sunflower Seeds (30g)', 'Avocado (1 medium)', 'Olive Oil (1 tbsp)', 'Hazelnuts (30g)'],
    topContributors: [{ name: 'Low Fat Diet', impact: 4.1, direction: 'risk' }, { name: 'Nut Consumption', impact: 6.5, direction: 'protective' }],
  },
  {
    id: 'vitamin_b1', label: 'Vitamin B1', icon: '🍞', probability: 0.32, risk: 'LOW', confidence: 0.88, bodySystem: 'Nerves & Energy',
    description: 'Thiamine — obligate coenzyme for pyruvate dehydrogenase and glucose oxidation into ATP. Essential for peripheral nerves and cardiac contractility.',
    influences: ['Glucose Metabolism', 'Nerve Conduction', 'Cardiac Function', 'Cognitive Energy'],
    symptoms: ['Severe fatigue', 'Irritability & mood changes', 'Loss of appetite', 'Burning feet neuropathy', 'Muscle weakness'],
    foods: ['Sunflower Seeds (35g)', 'Green Lentils (1 cup)', 'Brown Rice (1 cup)', 'Nutritional Yeast', 'Pork Tenderloin'],
    topContributors: [{ name: 'Refined Carb Diet', impact: 8.4, direction: 'risk' }, { name: 'Alcohol Use', impact: 6.2, direction: 'risk' }, { name: 'Sunflower Seeds', impact: 7.1, direction: 'protective' }],
  },
  {
    id: 'vitamin_b2', label: 'Vitamin B2', icon: '🍄', probability: 0.28, risk: 'LOW', confidence: 0.86, bodySystem: 'Cellular Energy & Eyes',
    description: 'Riboflavin — electron carrier coenzyme (FAD/FMN) for the mitochondrial respiratory chain and glutathione recycling.',
    influences: ['Mitochondrial Respiration', 'Glutathione Recycling', 'B6 Activation', 'Corneal Health'],
    symptoms: ['Angular cheilosis (cracked lips)', 'Mouth ulcers & glossitis', 'Eye irritation & photophobia', 'Seborrheic dermatitis'],
    foods: ['Nutritional Yeast (2 tbsp)', 'Pasture Eggs (2 large)', 'Raw Almonds (35g)', 'Cremini Mushrooms (1 cup)', 'Greek Yogurt'],
    topContributors: [{ name: 'Dairy-Free Diet', impact: 9.8, direction: 'risk' }, { name: 'Nutritional Yeast', impact: 11.2, direction: 'protective' }],
  },
  {
    id: 'vitamin_b3', label: 'Vitamin B3', icon: '🍗', probability: 0.22, risk: 'LOW', confidence: 0.90, bodySystem: 'DNA Repair & Metabolism',
    description: 'Niacin — substrate for NAD+/NADP+ cellular coenzymes catalyzing >400 biochemical reactions and PARP nuclear DNA repair.',
    influences: ['NAD+ Energy Production', 'DNA Repair (PARPs)', 'Cholesterol Balance', 'Skin Barrier'],
    symptoms: ['Photosensitive dermatitis', 'Digestive disturbances & diarrhea', 'Cognitive fatigue & confusion', 'Swollen tongue'],
    foods: ['Chicken Breast (100g)', 'Yellowfin Tuna (100g)', 'Dry-Roasted Peanuts', 'Brown Lentils', 'Mushrooms'],
    topContributors: [{ name: 'Low Protein Intake', impact: 7.1, direction: 'risk' }, { name: 'Poultry / Fish', impact: 9.4, direction: 'protective' }],
  },
  {
    id: 'vitamin_b6', label: 'Vitamin B6', icon: '🍌', probability: 0.45, risk: 'MODERATE', confidence: 0.84, bodySystem: 'Neurotransmitters & Blood',
    description: 'Pyridoxine (PLP) — coenzyme for >140 enzymes in amino acid metabolism, neurotransmitter synthesis (GABA, serotonin, dopamine), and hemoglobin formation.',
    influences: ['Neurotransmitter Synthesis', 'Hemoglobin Formation', 'Homocysteine Clearance', 'Immune Defense'],
    symptoms: ['Mood changes & irritability', 'Microcytic anemia', 'Tingling neuropathy in fingers/toes', 'Cracked lip corners'],
    foods: ['Cooked Chickpeas (1 cup)', 'Fresh Bananas (1 large)', 'Wild Sockeye Salmon', 'Baked Potato with skin', 'Pistachios'],
    topContributors: [{ name: 'Oral Contraceptives', impact: 8.9, direction: 'risk' }, { name: 'High Chronic Stress', impact: 7.3, direction: 'risk' }, { name: 'Chickpea Hummus', impact: 6.8, direction: 'protective' }],
  },
  {
    id: 'potassium', label: 'Potassium', icon: '🥔', probability: 0.58, risk: 'MODERATE', confidence: 0.87, bodySystem: 'Heart & Muscles',
    description: 'The primary intracellular electrolyte cation. Regulates resting membrane potential, muscle contraction, and counteracts sodium-driven hypertension.',
    influences: ['Cardiac Rhythm', 'Muscle Contraction', 'Blood Pressure Control', 'Fluid Equilibrium'],
    symptoms: ['Muscle cramps & spasms', 'Cardiac palpitations / flutter', 'Constipation & abdominal distension', 'Generalized weakness'],
    foods: ['Baked Russet Potato with skin', 'Hass Avocado (1 medium)', 'Cooked Swiss Chard', 'White Cannellini Beans', 'Coconut Water'],
    topContributors: [{ name: 'Low Fruit & Greens', impact: 14.2, direction: 'risk' }, { name: 'High Sodium Diet', impact: 9.5, direction: 'risk' }, { name: 'Daily Avocado', impact: 8.1, direction: 'protective' }],
  },
  {
    id: 'selenium', label: 'Selenium', icon: '🌰', probability: 0.25, risk: 'LOW', confidence: 0.91, bodySystem: 'Thyroid & Cellular Defense',
    description: 'Essential catalytic constituent of 25 selenoproteins, notably glutathione peroxidases (antioxidant defense) and deiodinases (converting T4 to active T3 thyroid hormone).',
    influences: ['Thyroid Hormone Conversion', 'Glutathione Defense', 'Sperm Motility', 'Antiviral Immunity'],
    symptoms: ['Impaired thyroid conversion', 'Diffuse hair thinning & brittle nails', 'Weakened viral defenses', 'Cardiomyopathy risk'],
    foods: ['Brazil Nuts (1-2 nuts/day)', 'Yellowfin Tuna', 'Whole Eggs', 'Shiitake Mushrooms', 'Sunflower Seeds'],
    topContributors: [{ name: 'Low-Soil Region', impact: 6.8, direction: 'risk' }, { name: 'Brazil Nut Intake', impact: 14.5, direction: 'protective' }],
  },
  {
    id: 'iodine', label: 'Iodine', icon: '🌊', probability: 0.65, risk: 'HIGH', confidence: 0.86, bodySystem: 'Thyroid & Basal Metabolism',
    description: 'Obligate structural substrate for thyroid hormones (T4 and T3) that control basal metabolic rate, body temperature, and neurocognitive development.',
    influences: ['Thyroid Hormone Synthesis', 'Basal Metabolic Rate', 'Thermoregulation', 'Cognitive Focus'],
    symptoms: ['Visible thyroid goiter', 'Unprovoked weight gain', 'Cold intolerance & chilliness', 'Dry coarse skin', 'Mental sluggishness'],
    foods: ['Wakame & Nori Seaweed', 'Iodized Sea Salt (1/4 tsp)', 'Wild Atlantic Cod', 'Organic Greek Yogurt', 'Pasture Eggs'],
    topContributors: [{ name: 'Un-iodized Salt Exclusively', impact: 18.2, direction: 'risk' }, { name: 'Dairy & Seafood-Free Diet', impact: 14.1, direction: 'risk' }, { name: 'Seaweed Consumption', impact: 11.8, direction: 'protective' }],
  },
]

/* ═══════════════════════════════════════════════════════════════════════════
   EDGE DATA — 15 Biochemical Interactions
   ═══════════════════════════════════════════════════════════════════════════ */

export const EDGES: NutrientEdge[] = [
  {
    id: 'e1', source: 'vitamin_d', target: 'calcium', type: 'synergistic', label: 'Absorption Enabler', strength: 0.95,
    explanation: 'Vitamin D is the primary hormonal regulator of intestinal calcium absorption. Active 1,25(OH)₂D binds to VDR receptors upregulating calbindin proteins. Without adequate Vitamin D, only 10-15% of dietary calcium is absorbed versus 30-40% with sufficient levels.',
    importance: 'The most critical nutrient synergy for bone health. Vitamin D deficiency effectively creates a secondary calcium deficiency even when dietary calcium is adequate.',
    dietaryTip: 'Pair calcium-rich foods (yogurt, milk) with Vitamin D sources (egg yolks, salmon). Take supplements together.',
    traceImpact: 'Vitamin D deficiency reduces calcium absorption by 60-75%, accelerating bone density loss and increasing long-term osteoporosis risk.',
  },
  {
    id: 'e2', source: 'vitamin_d', target: 'magnesium', type: 'supportive', label: 'Activation Pathway', strength: 0.75,
    explanation: 'Magnesium is required for Vitamin D metabolism: hepatic CYP2R1 and renal CYP27B1 enzymes are both magnesium-dependent. Magnesium deficiency can render Vitamin D supplementation ineffective.',
    importance: 'Explains why some patients show no Vitamin D improvement despite supplementation — they lack the magnesium cofactor.',
    dietaryTip: 'Ensure magnesium adequacy (400mg/day) before starting Vitamin D supplements. Add pumpkin seeds or dark chocolate daily.',
    traceImpact: 'Magnesium deficiency blocks Vitamin D activation, creating a hidden cascade: Mg↓ → VitD activation↓ → Ca absorption↓ → bone risk↑',
  },
  {
    id: 'e3', source: 'iron', target: 'vitamin_c', type: 'synergistic', label: 'Absorption Booster', strength: 0.90,
    explanation: 'Vitamin C enhances non-heme iron absorption by 2-6x: reducing Fe³⁺ to Fe²⁺ and chelating iron to prevent phytate binding.',
    importance: 'The most actionable synergy for plant-based eaters. Vitamin C pairing can effectively triple iron absorption from plant sources.',
    dietaryTip: 'Squeeze lemon on spinach, add bell peppers to lentil soup. Consume Vitamin C with iron-rich meals, not hours later.',
    traceImpact: 'Without Vitamin C pairing, plant-based iron absorption drops to 2-5%, significantly increasing anemia risk on vegan diets.',
  },
  {
    id: 'e4', source: 'iron', target: 'zinc', type: 'competitive', label: 'Absorption Competition', strength: 0.65,
    explanation: 'Iron and Zinc compete for DMT1 transporter. High-dose iron supplements (>25mg) can reduce zinc absorption by 50%.',
    importance: 'Clinically significant for supplement users. Competition does NOT apply to whole foods where the food matrix buffers the interaction.',
    dietaryTip: 'Take iron and zinc supplements at different times (iron AM, zinc PM). Whole food sources are safe together.',
    traceImpact: 'High-dose iron supplementation without zinc monitoring can create an iatrogenic zinc deficiency, impairing immune function.',
  },
  {
    id: 'e5', source: 'vitamin_b12', target: 'folate', type: 'synergistic', label: 'Methionine Cycle', strength: 0.85,
    explanation: 'B12 and Folate are co-dependent in methionine synthase. Without B12, folate becomes "trapped" in methyl form (methyl trap hypothesis).',
    importance: 'B12 deficiency creates a functional folate deficiency. High-dose folate can mask B12 deficiency while neurological damage continues.',
    dietaryTip: 'Always address B12 and Folate together. For vegans: fortified nutritional yeast (B12) + lentils and spinach (folate).',
    traceImpact: 'B12 deficiency traps folate, disrupting DNA synthesis and cell division — elevating homocysteine and cardiovascular risk.',
  },
  {
    id: 'e6', source: 'calcium', target: 'magnesium', type: 'competitive', label: 'Absorption Balance', strength: 0.60,
    explanation: 'Calcium and Magnesium share TRPM6/7 absorption channels. Excess calcium (>2500mg/day) inhibits magnesium absorption. Ideal ratio is 2:1.',
    importance: 'Over-supplementation of calcium without magnesium attention paradoxically increases cardiovascular risk. Ratio matters more than absolute intake.',
    dietaryTip: 'Maintain 2:1 Ca:Mg ratio. If taking 1000mg calcium, ensure 400-500mg magnesium. Separate supplements by 2 hours.',
    traceImpact: 'Calcium excess displaces magnesium, disrupting nerve/muscle function and potentially increasing arrhythmia risk.',
  },
  {
    id: 'e7', source: 'protein', target: 'zinc', type: 'supportive', label: 'Bioavailability Enhancer', strength: 0.70,
    explanation: 'Animal protein releases amino acids (histidine, cysteine) that chelate zinc, preventing phytate binding. Protein also stimulates gastric acid for zinc solubility.',
    importance: 'Explains higher zinc status in omnivores vs. vegans despite similar intake quantities.',
    dietaryTip: 'Pair zinc sources with protein: pumpkin seeds + yogurt, chickpeas + tofu stir-fry. Soak and sprout grains to reduce phytates.',
    traceImpact: 'Low protein intake reduces zinc bioavailability by 30-50%, compounding immune and wound healing deficits.',
  },
  {
    id: 'e8', source: 'vitamin_a', target: 'zinc', type: 'supportive', label: 'Transport & Activation', strength: 0.72,
    explanation: 'Zinc synthesizes retinol-binding protein (RBP) that transports Vitamin A from liver to tissues. Zinc also activates retinol → retinal conversion for vision.',
    importance: 'Creates a hidden cascade: Zinc↓ → Vitamin A transport↓ → night blindness + immune suppression even with adequate Vitamin A intake.',
    dietaryTip: 'Combine Vitamin A + Zinc: sweet potato + pumpkin seeds, carrots + chickpea hummus, or liver (contains both).',
    traceImpact: 'Zinc deficiency impairs Vitamin A mobilization, creating functional deficiency in vision and immune pathways despite adequate stores.',
  },
  {
    id: 'e9', source: 'vitamin_b6', target: 'vitamin_b12', type: 'synergistic', label: 'Homocysteine Clearance', strength: 0.88,
    explanation: 'Vitamin B6 (as PLP) and Vitamin B12 act concurrently in transsulfuration and remethylation to detoxify cellular homocysteine into cystathionine and methionine.',
    importance: 'Co-deficiency induces rapid hyperhomocysteinemia, accelerating endothelial oxidative damage and microvascular stroke risk.',
    dietaryTip: 'Combine chickpeas or wild salmon (B6) with fortified nutritional yeast (B12).',
    traceImpact: 'Dual B6-B12 deficiency blocks homocysteine clearance, doubling cardiovascular inflammatory risk.',
  },
  {
    id: 'e10', source: 'vitamin_b6', target: 'folate', type: 'synergistic', label: 'One-Carbon Shuttle', strength: 0.82,
    explanation: 'Vitamin B6 is the obligate coenzyme for serine hydroxymethyltransferase (SHMT), which transfers single-carbon units to THF for purine and thymidylate synthesis.',
    importance: 'Without B6, folate is trapped and cellular DNA synthesis stalls, compounding megaloblastic anemia.',
    dietaryTip: 'Enjoy a spinach salad (folate) with chickpeas and sliced avocado (B6).',
    traceImpact: 'B6 deficiency cripples folate-dependent cellular division and nucleotide repair.',
  },
  {
    id: 'e11', source: 'iodine', target: 'selenium', type: 'synergistic', label: 'Thyroid Activation', strength: 0.94,
    explanation: 'Iodine synthesizes the T4 thyroid hormone, but selenium-dependent iodothyronine deiodinase enzymes (DIO1, DIO2) are required to convert T4 into active T3.',
    importance: 'Taking iodine without adequate selenium can exacerbate autoimmune thyroiditis, as selenium neutralizes peroxide radicals formed during thyroid synthesis.',
    dietaryTip: 'Pair nori or wakame seaweed (iodine) with a Brazil nut or tuna steak (selenium).',
    traceImpact: 'Selenium deficiency halts iodine-driven thyroid hormone activation, precipitating severe metabolic hypothyroidism.',
  },
  {
    id: 'e12', source: 'potassium', target: 'magnesium', type: 'synergistic', label: 'Electrolyte Homeostasis', strength: 0.90,
    explanation: 'Magnesium activates the Na+/K+-ATPase pump that moves potassium into cells, and directly inhibits renal ROMK channels from leaking potassium into urine.',
    importance: 'Hypomagnesemia causes refractory hypokalemia that will NOT correct with potassium supplements alone until magnesium is repleted.',
    dietaryTip: 'Pair baked potato or avocado (potassium) with pumpkin seeds and dark leafy chard (magnesium).',
    traceImpact: 'Low magnesium causes persistent renal potassium wasting, triggering cardiac arrhythmias and refractory muscle cramps.',
  },
  {
    id: 'e13', source: 'vitamin_b1', target: 'magnesium', type: 'supportive', label: 'Thiamine Activation', strength: 0.80,
    explanation: 'Thiamine pyrophosphokinase, the enzyme converting thiamine into its active coenzyme form (TPP), is strictly magnesium-dependent.',
    importance: 'Thiamine supplementation is therapeutically inactive in magnesium-depleted individuals.',
    dietaryTip: 'Pair sunflower seeds or brown rice (B1) with raw almonds or dark chocolate (magnesium).',
    traceImpact: 'Magnesium deficit locks thiamine in its inactive unphosphorylated form, compounding metabolic fatigue and lactic acidosis.',
  },
  {
    id: 'e14', source: 'vitamin_b2', target: 'vitamin_b6', type: 'supportive', label: 'PLP Synthesis Pathway', strength: 0.78,
    explanation: 'Pyridoxine 5-phosphate oxidase (PNPO), which converts dietary pyridoxine to active pyridoxal 5-phosphate (PLP), requires flavin mononucleotide (FMN, Vitamin B2).',
    importance: 'Riboflavin deficiency directly impairs B6 activation, mimicking primary B6 deficiency.',
    dietaryTip: 'Pair pasture eggs or mushrooms (B2) with chickpeas or bananas (B6).',
    traceImpact: 'B2 deficiency arrests B6 coenzyme synthesis, triggering secondary microcytic anemia and peripheral neuropathy.',
  },
  {
    id: 'e15', source: 'vitamin_b3', target: 'protein', type: 'supportive', label: 'Tryptophan Conversion', strength: 0.74,
    explanation: 'The essential amino acid tryptophan in dietary protein is converted in the liver into niacin equivalents (60 mg tryptophan yields 1 mg niacin).',
    importance: 'Adequate dietary protein provides a metabolic buffer protecting against Pellagra when niacin intake is marginal.',
    dietaryTip: 'Consume balanced complete proteins (eggs, poultry, lentils) to fuel the de novo NAD synthesis pathway.',
    traceImpact: 'Low protein intake eliminates the tryptophan buffer, elevating clinical risk of Pellagra in low-niacin diets.',
  },
]

/* ═══════════════════════════════════════════════════════════════════════════
   HELPER FUNCTIONS
   ═══════════════════════════════════════════════════════════════════════════ */

/** Find all connected nodes (1st and 2nd degree) and edges from a given node */
export function getConnectedGraph(nodeId: string): ConnectedGraph {
  const directEdges = EDGES.filter(e => e.source === nodeId || e.target === nodeId)
  const nodes = new Set<string>([nodeId])
  const edges = new Set<string>()
  const paths: { nodeId: string; edgeId: string; depth: number }[] = []

  directEdges.forEach(e => {
    const otherId = e.source === nodeId ? e.target : e.source
    nodes.add(otherId as string)
    edges.add(e.id)
    paths.push({ nodeId: otherId as string, edgeId: e.id, depth: 1 })
  })

  // Second-degree (indirect)
  const firstDegreeNodes = [...nodes].filter(n => n !== nodeId)
  firstDegreeNodes.forEach(fdn => {
    EDGES.forEach(e => {
      const src = e.source as string
      const tgt = e.target as string
      if ((src === fdn || tgt === fdn) && !edges.has(e.id)) {
        const otherId = src === fdn ? tgt : src
        if (!nodes.has(otherId)) {
          nodes.add(otherId)
          edges.add(e.id)
          paths.push({ nodeId: otherId, edgeId: e.id, depth: 2 })
        }
      }
    })
  })

  return { nodes, edges, paths }
}

/** Get edges connected to a specific node */
export function getNodeEdges(nodeId: string): NutrientEdge[] {
  return EDGES.filter(e => e.source === nodeId || e.target === nodeId)
}

/** Get the other node in an edge */
export function getEdgePartner(edge: NutrientEdge, nodeId: string): NutrientNode | undefined {
  const partnerId = edge.source === nodeId ? edge.target : edge.source
  return NODES.find(n => n.id === partnerId)
}

/** Get aggregate stats for the stats bar */
export function getAggregateStats() {
  const highRisk = NODES.filter(n => n.risk === 'HIGH')
  const avgRisk = NODES.reduce((sum, n) => sum + n.probability, 0) / NODES.length
  const cascades = EDGES.filter(e => {
    const src = NODES.find(n => n.id === e.source)
    const tgt = NODES.find(n => n.id === e.target)
    return src && tgt && (src.risk === 'HIGH' || tgt.risk === 'HIGH') && e.type === 'synergistic'
  })

  return {
    totalNutrients: NODES.length,
    highRiskCount: highRisk.length,
    avgRisk: Math.round(avgRisk * 100),
    totalInteractions: EDGES.length,
    criticalCascades: cascades.length,
  }
}

/** Sort nodes by risk priority for layout (high risk first → center) */
export function getNodesByRiskPriority(): NutrientNode[] {
  const order: Record<RiskLevel, number> = { HIGH: 0, MODERATE: 1, LOW: 2 }
  return [...NODES].sort((a, b) => order[a.risk] - order[b.risk] || b.probability - a.probability)
}

/** Multi-field search result with match context */
export interface SearchResult {
  node: NutrientNode
  matchType: 'name' | 'symptom' | 'food' | 'system'
  matchText: string
}

/** Search nodes across name, symptoms, foods, body system */
export function searchNodes(query: string): NutrientNode[] {
  const q = query.toLowerCase().trim()
  if (!q) return []
  return NODES.filter(n =>
    n.label.toLowerCase().includes(q) ||
    n.bodySystem.toLowerCase().includes(q) ||
    n.id.toLowerCase().includes(q) ||
    n.symptoms.some(s => s.toLowerCase().includes(q)) ||
    n.foods.some(f => f.toLowerCase().includes(q)) ||
    n.influences.some(inf => inf.toLowerCase().includes(q))
  )
}

/** Rich search with match context for grouped display */
export function searchNodesRich(query: string): SearchResult[] {
  const q = query.toLowerCase().trim()
  if (!q) return []
  const results: SearchResult[] = []
  const seen = new Set<string>()

  // Priority 1: Name matches
  NODES.forEach(n => {
    if (n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q)) {
      if (!seen.has(n.id)) { seen.add(n.id); results.push({ node: n, matchType: 'name', matchText: n.label }) }
    }
  })

  // Priority 2: Body system matches
  NODES.forEach(n => {
    if (n.bodySystem.toLowerCase().includes(q)) {
      if (!seen.has(n.id)) { seen.add(n.id); results.push({ node: n, matchType: 'system', matchText: n.bodySystem }) }
    }
  })

  // Priority 3: Symptom matches
  NODES.forEach(n => {
    const match = n.symptoms.find(s => s.toLowerCase().includes(q))
    if (match) {
      if (!seen.has(n.id)) { seen.add(n.id); results.push({ node: n, matchType: 'symptom', matchText: match }) }
    }
  })

  // Priority 4: Food matches
  NODES.forEach(n => {
    const match = n.foods.find(f => f.toLowerCase().includes(q))
    if (match) {
      if (!seen.has(n.id)) { seen.add(n.id); results.push({ node: n, matchType: 'food', matchText: match }) }
    }
  })

  return results
}

/** Build deficiency cascade chains from a starting node */
export interface CascadeStep {
  nodeId: string
  label: string
  icon: string
  edgeLabel: string
  impact: string
  depth: number
}

export function getCascadeChains(nodeId: string): CascadeStep[][] {
  const chains: CascadeStep[][] = []
  const startNode = NODES.find(n => n.id === nodeId)
  if (!startNode) return chains

  // Find all direct edges from this node
  const directEdges = EDGES.filter(e => e.source === nodeId || e.target === nodeId)

  directEdges.forEach(edge => {
    const partnerId = (edge.source === nodeId ? edge.target : edge.source) as string
    const partner = NODES.find(n => n.id === partnerId)
    if (!partner) return

    const chain: CascadeStep[] = [
      { nodeId: partner.id, label: partner.label, icon: partner.icon, edgeLabel: edge.label, impact: edge.traceImpact, depth: 1 },
    ]

    // Extend chain one more level
    const secondEdges = EDGES.filter(e =>
      (e.source === partnerId || e.target === partnerId) && e.id !== edge.id
    )
    secondEdges.slice(0, 1).forEach(e2 => {
      const thirdId = (e2.source === partnerId ? e2.target : e2.source) as string
      const thirdNode = NODES.find(n => n.id === thirdId)
      if (thirdNode && thirdNode.id !== nodeId) {
        chain.push({ nodeId: thirdNode.id, label: thirdNode.label, icon: thirdNode.icon, edgeLabel: e2.label, impact: e2.traceImpact, depth: 2 })
      }
    })

    chains.push(chain)
  })

  return chains.sort((a, b) => b.length - a.length).slice(0, 4) // top 4 chains
}

// D3 type import for SimulationNodeDatum / SimulationLinkDatum
import type * as d3 from 'd3'
