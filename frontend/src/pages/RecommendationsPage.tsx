import { useState, useMemo, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import { Utensils, Leaf, Dumbbell, Moon, Sun, Droplets, Heart, FileText, ChevronRight, Zap } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.05 } } }

function getFoodEmoji(name: string, group?: string): string {
  const n = (name + ' ' + (group || '')).toLowerCase()
  if (n.includes('mushroom')) return '🍄'
  if (n.includes('lentil') || n.includes('bean') || n.includes('chickpea')) return '🫘'
  if (n.includes('yeast')) return '🧀'
  if (n.includes('spinach') || n.includes('kale') || n.includes('green') || n.includes('chard')) return '🥬'
  if (n.includes('tofu') || n.includes('soy') || n.includes('tempeh')) return '🧊'
  if (n.includes('pumpkin') || n.includes('seed')) return '🎃'
  if (n.includes('nut') || n.includes('almond') || n.includes('walnut')) return '🌰'
  if (n.includes('pepper')) return '🫑'
  if (n.includes('potato')) return '🍠'
  if (n.includes('yogurt') || n.includes('milk')) return '🥛'
  if (n.includes('egg')) return '🥚'
  if (n.includes('citrus') || n.includes('orange') || n.includes('lemon')) return '🍋'
  if (n.includes('avocado')) return '🥑'
  if (n.includes('berry') || n.includes('blueberr')) return '🫐'
  return '🥗'
}

const FALLBACK_DATA = {
  foods: {
    priority1: [
      { name: 'UV-Exposed Shiitake & Portobello Mushrooms', nutrient: 'Vitamin D', serving: '100g (3.5 oz)', density: 'Very High', tip: 'Sauté with cold-pressed olive oil. Exposure to ultraviolet sunlight boosts natural plant-derived Vitamin D2.', emoji: '🍄' },
      { name: 'Cooked Green Lentils & Spinach', nutrient: 'Iron + Folate', serving: '1 cup cooked (180g)', density: 'Exceptional', tip: 'Pair with lemon juice or bell pepper (Vitamin C) to enhance non-heme iron absorption by up to 6x.', emoji: '🫘' },
      { name: 'Fortified Nutritional Yeast', nutrient: 'Vitamin B12 + B-Complex', serving: '2 tablespoons (15g)', density: 'High', tip: 'Sprinkle on pasta, roasted vegetables, or soups. Rich in B1, B2, B3, B6, and active Vitamin B12.', emoji: '🧀' },
      { name: 'Organic Sprouted Tofu', nutrient: 'Calcium + Protein + Zinc', serving: '150g (firm)', density: 'High', tip: 'Calcium-set tofu provides bioavailable calcium and complete essential amino acids for tissue repair.', emoji: '🧊' },
    ],
    priority2: [
      { name: 'Steamed Baby Spinach', nutrient: 'Folate + Potassium + Magnesium', serving: '1 cup cooked (180g)', density: 'High', tip: 'Steaming reduces soluble oxalates while concentrating folate and magnesium availability.', emoji: '🥬' },
      { name: 'Greek Yogurt or Fortified Soy Yogurt', nutrient: 'Calcium + B12 + Protein', serving: '200g', density: 'High', tip: 'Rich in probiotic cultures and calcium. Add berries for Vitamin C and antioxidant synergy.', emoji: '🥛' },
      { name: 'Raw Pumpkin & Chia Seeds', nutrient: 'Zinc + Magnesium', serving: '30g (1 oz)', density: 'High', tip: 'Toast lightly. Excellent zinc-dense plant source with anti-inflammatory omega-3 alpha-linolenic acid.', emoji: '🎃' },
      { name: 'Brazil Nuts (Selenium Micro-Dose)', nutrient: 'Selenium', serving: '1-2 nuts daily (5g)', density: 'Exceptional', tip: 'A single nut fulfills >100% RDA for selenoprotein enzymes and thyroid peroxidase support.', emoji: '🌰' },
      { name: 'Whole Cooked Chickpeas', nutrient: 'Folate + Iron + Zinc', serving: '1 cup cooked', density: 'Very High', tip: 'Soak overnight before cooking to reduce phytate binding. Add cumin and turmeric for digestive ease.', emoji: '🫘' },
    ],
    priority3: [
      { name: 'Orange & Red Bell Peppers', nutrient: 'Vitamin C', serving: '1 medium pepper', density: 'Very High', tip: 'Consume raw or lightly charred. Contains 3x the Vitamin C concentration of whole oranges.', emoji: '🫑' },
      { name: 'Raw Almonds & Walnuts', nutrient: 'Vitamin E + Magnesium', serving: '30g (23 nuts)', density: 'High', tip: 'Raw or dry-roasted. Soak for 4 hours to improve enzyme inhibition and digestive ease.', emoji: '🥜' },
      { name: 'Roasted Japanese Sweet Potato', nutrient: 'Vitamin A + Potassium', serving: '1 medium baked', density: 'Exceptional', tip: 'Bake with skin intact. Add healthy lipid drizzle (olive or avocado oil) for carotenoid micelle absorption.', emoji: '🍠' },
    ],
  },
  synergies: [
    { pair: ['Iron', 'Vitamin C'], mechanism: 'Ascorbic acid converts ferric (Fe3+) iron to bioavailable ferrous (Fe2+) form, multiplying absorption up to 6x.', foods: 'Spinach + Fresh Lemon Juice, Lentils + Red Bell Pepper', icon: '⚡' },
    { pair: ['Calcium', 'Vitamin D'], mechanism: 'Vitamin D enhances active enterocyte calbindin synthesis for transcellular calcium transport.', foods: 'Fortified Plant Milk + Sunlight, Steamed Tofu + UV-Treated Mushrooms', icon: '🦴' },
    { pair: ['Iodine', 'Selenium'], mechanism: 'Selenium-dependent iodothyronine deiodinases convert T4 to metabolically active T3 hormone.', foods: 'Brazil Nuts + Sea Vegetables (Nori / Dulse)', icon: '🦋' },
    { pair: ['Potassium', 'Magnesium'], mechanism: 'Magnesium regulates the myocardial Na+/K+ ATPase pump, sustaining cellular electrical gradient.', foods: 'Avocado + Steamed Greens, Baked Sweet Potato + Pumpkin Seeds', icon: '❤️' },
    { pair: ['Zinc', 'Plant Protein'], mechanism: 'Sprouting and fermenting legume protein degrades phytate complexation, elevating free ionic zinc.', foods: 'Sprouted Chickpeas + Pumpkin Seed Tahini, Tempeh + Sesame Dressing', icon: '💪' },
  ],
  lifestyle: [
    { category: 'Sunlight & Photobiology', icon: Sun, actions: ['Get 15-30 min of direct midday sunlight (10am-2pm) for cutaneous pre-vitamin D3 synthesis', 'Expose arms and legs without sunscreen for optimal photochemical conversion', 'Consider broad-spectrum clinical UV-B lamp during winter months'] },
    { category: 'Hydration & Electrolytes', icon: Droplets, actions: ['Maintain 2.5-3.0 liters of structured cellular water intake daily', 'Consume fluids between meals rather than during eating to preserve gastric acid enzymatic potency', 'Add a squeeze of fresh lemon and pinch of sea salt for intracellular electrolyte delivery'] },
    { category: 'Circadian Sleep Architecture', icon: Moon, actions: ['Prioritize 7-8 hours of uninterrupted restorative slow-wave sleep', 'Consume magnesium-dense foods or herbal chamomile 1 hour before bed to support GABAergic relaxation', 'Avoid caffeine after 2pm to prevent adenosine receptor disruption and calcium clearance'] },
    { category: 'Physical Activity & Bone Loading', icon: Dumbbell, actions: ['Engage in 30 minutes of progressive resistance or brisk walking 5 days weekly', 'Axial weight-bearing movement stimulates osteoblast mechanoreceptors and mineral uptake', 'Consume plant-based protein with electrolytes within 60 minutes post-training'] },
    { category: 'Stress Regulation & Neuroendocrine', icon: Heart, actions: ['Practice 10-15 minutes of autonomic down-regulation (box breathing, diaphragmatic pacing)', 'Chronic sympathetic cortisol elevations accelerate renal excretion of magnesium and zinc', 'Incorporate adaptogenic teas (ashwagandha or holy basil) under clinical guidance'] },
  ],
  recovery: [
    { phase: 1, label: 'Week 1', title: 'Acute Cellular Replenishment', milestones: ['Initiate targeted daily dietary protocol for identified high-priority micronutrients', 'Incorporate at least 2 Priority-1 therapeutic foods into every main meal', 'Implement strict Vitamin C pairing with every non-heme iron food source'] },
    { phase: 2, label: 'Weeks 2-3', title: 'Metabolic Consolidation & Mineral Rebalancing', milestones: ['Introduce Priority-2 supportive staple foods into weekly meal rotations', 'Consistently hit sunlight, hydration, and sleep hygiene lifestyle protocols', 'Assess early functional recovery markers (mental clarity, muscle endurance, digestion)'] },
    { phase: 3, label: 'Week 4+', title: 'Systemic Resilience & Long-Term Homeostasis', milestones: ['Maintain diversified dietary rotation across all three priority tiers', 'Conduct follow-up assessment to quantify clinical score trajectory and status improvement', 'Transition from acute therapeutic repletion to sustainable long-term maintenance habits'] },
  ],
}

function useRecommendationData(assessmentId?: string) {
  const [data, setData] = useState<typeof FALLBACK_DATA>(FALLBACK_DATA)

  useEffect(() => {
    const fetchRecs = async () => {
      try {
        const storedId = localStorage.getItem('nutriscan_assessment_id')
        const id = (assessmentId && assessmentId !== 'demo') ? assessmentId : (storedId || '')
        const url = id ? `/api/v1/recommendations/${id}` : '/api/v1/recommendations'
        const res = await fetch(url)
        if (res.ok) {
          const apiData = await res.json()
          
          let p1: any[] = []
          let p2: any[] = []
          let p3: any[] = []

          if (Array.isArray(apiData.food_recommendations) && apiData.food_recommendations.length > 0) {
            apiData.food_recommendations.forEach((f: any) => {
              const mapped = {
                name: f.food_name,
                nutrient: f.target_nutrient,
                serving: f.serving_size,
                density: `${f.nutrient_density} ${f.unit || ''}`.trim(),
                tip: f.preparation_tips || f.rationale || 'Targeted functional nutrient source.',
                emoji: getFoodEmoji(f.food_name, f.food_group),
              }
              if (f.priority_tier === 'PRIORITY_1') p1.push(mapped)
              else if (f.priority_tier === 'PRIORITY_2') p2.push(mapped)
              else p3.push(mapped)
            })
            // If tiers were unassigned, distribute evenly
            if (p1.length === 0 && p2.length === 0) {
              const allMapped = apiData.food_recommendations.map((f: any) => ({
                name: f.food_name,
                nutrient: f.target_nutrient,
                serving: f.serving_size,
                density: `${f.nutrient_density} ${f.unit || ''}`.trim(),
                tip: f.preparation_tips || f.rationale || 'Targeted functional nutrient source.',
                emoji: getFoodEmoji(f.food_name, f.food_group),
              }))
              p1 = allMapped.slice(0, 3)
              p2 = allMapped.slice(3, 7)
              p3 = allMapped.slice(7)
            }
          }

          const synergies = Array.isArray(apiData.synergistic_pairings) && apiData.synergistic_pairings.length > 0
            ? apiData.synergistic_pairings.map((s: any) => ({
                pair: [s.primary_nutrient, s.synergistic_nutrient],
                mechanism: s.biochemical_mechanism,
                foods: s.meal_concept || `${s.primary_food} + ${s.enhancer_food}`,
                icon: '⚡'
              }))
            : data.synergies

          const recovery = Array.isArray(apiData.recovery_milestones) && apiData.recovery_milestones.length > 0
            ? apiData.recovery_milestones.map((m: any, idx: number) => ({
                phase: idx + 1,
                label: m.day_range,
                title: m.phase_title,
                milestones: m.daily_action_checklist && m.daily_action_checklist.length > 0
                  ? m.daily_action_checklist
                  : [m.clinical_focus, m.primary_dietary_strategy].filter(Boolean)
              }))
            : data.recovery

          setData({
            foods: {
              priority1: p1.length > 0 ? p1 : FALLBACK_DATA.foods.priority1,
              priority2: p2.length > 0 ? p2 : FALLBACK_DATA.foods.priority2,
              priority3: p3.length > 0 ? p3 : FALLBACK_DATA.foods.priority3,
            },
            synergies,
            lifestyle: FALLBACK_DATA.lifestyle,
            recovery,
          })
        }
      } catch (err) {
        console.error('Recommendations fetch error:', err)
      }
    }
    fetchRecs()
  }, [assessmentId])

  return data
}

function FoodCard({ food }: { food: any }) {
  return (
    <div className="card card-hover" style={{ padding: 20, cursor: 'default' }}>
      <div style={{ display: 'flex', gap: 14 }}>
        <span style={{ fontSize: 28 }}>{food.emoji}</span>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 2 }}>{food.name}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--c-primary)', fontWeight: 600 }}>for {food.nutrient}</div>
            </div>
            <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-accent)', background: 'var(--c-warning-bg)', padding: '2px 8px', borderRadius: 4 }}>{food.density}</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 8 }}><strong>Serving:</strong> {food.serving}</div>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.5, marginTop: 6 }}>{food.tip}</p>
        </div>
      </div>
    </div>
  )
}

export default function RecommendationsPage() {
  const { assessmentId } = useParams()
  const data = useRecommendationData(assessmentId)
  const [activeTab, setActiveTab] = useState<'foods' | 'lifestyle' | 'recovery'>('foods')

  const tabs = [
    { key: 'foods' as const, label: 'Food Recommendations', icon: Utensils },
    { key: 'lifestyle' as const, label: 'Lifestyle Interventions', icon: Leaf },
    { key: 'recovery' as const, label: 'Recovery Roadmap', icon: Zap },
  ]

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger}>
      <motion.div variants={fadeUp} style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 6 }}>Personalized Recommendations</h1>
            <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)' }}>Evidence-based dietary guidance, lifestyle interventions, and structured recovery plans.</p>
          </div>
          <Link
            to={`/intelligence/${assessmentId || 'demo'}`}
            className="card card-hover"
            style={{
              padding: '10px 16px',
              background: 'linear-gradient(135deg, rgba(56, 139, 253, 0.15) 0%, rgba(22, 27, 34, 0.8) 100%)',
              border: '1px solid rgba(56, 139, 253, 0.4)',
              color: 'var(--c-secondary)',
              textDecoration: 'none',
              fontSize: '0.8125rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              borderRadius: 8
            }}
          >
            <Zap size={15} color="var(--c-primary)" />
            <span>Launch Nutrition Intelligence Center &rarr;</span>
          </Link>
        </div>
      </motion.div>

      <motion.div variants={fadeUp} style={{ display: 'flex', gap: 4, marginBottom: 24, background: 'var(--c-bg-secondary)', padding: 4, borderRadius: 10, border: '1px solid var(--c-border)', width: 'fit-content' }}>
        {tabs.map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)} style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 8, border: 'none',
            background: activeTab === tab.key ? 'var(--c-primary)' : 'transparent',
            color: activeTab === tab.key ? 'white' : 'var(--c-muted)',
            fontSize: '0.8125rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'var(--font-body)', transition: 'all 0.15s',
          }}>
            <tab.icon size={14} /> {tab.label}
          </button>
        ))}
      </motion.div>

      {activeTab === 'foods' && (
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          {[
            { label: 'Priority 1 — Critical', desc: 'Address immediately for highest-risk nutrients', foods: data.foods.priority1, color: 'var(--c-danger)' },
            { label: 'Priority 2 — Important', desc: 'Add to weekly meal rotation', foods: data.foods.priority2, color: 'var(--c-warning)' },
            { label: 'Priority 3 — Maintenance', desc: 'Include regularly for overall balance', foods: data.foods.priority3, color: 'var(--c-success)' },
          ].map(section => (
            <motion.div key={section.label} variants={fadeUp} style={{ marginBottom: 28 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <div style={{ width: 4, height: 20, borderRadius: 2, background: section.color }} />
                <div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{section.label}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>{section.desc}</div>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
                {section.foods.map(f => <FoodCard key={f.name} food={f} />)}
              </div>
            </motion.div>
          ))}
          <motion.div variants={fadeUp} style={{ marginBottom: 28 }}>
            <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 14 }}>Nutrient Synergy Pairings</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              {data.synergies.map(s => (
                <div key={s.pair.join('-')} className="card" style={{ padding: 20 }}>
                  <div style={{ fontSize: 20, marginBottom: 10 }}>{s.icon}</div>
                  <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-primary)', marginBottom: 6 }}>{s.pair.join(' + ')}</div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.5, marginBottom: 8 }}>{s.mechanism}</p>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-text-secondary)', fontWeight: 500 }}><strong>Try:</strong> {s.foods}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}

      {activeTab === 'lifestyle' && (
        <motion.div initial="hidden" animate="visible" variants={stagger} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {data.lifestyle.map(cat => (
            <motion.div key={cat.category} variants={fadeUp} className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--c-surface-tint)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <cat.icon size={18} color="var(--c-primary)" />
                </div>
                <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>{cat.category}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {cat.actions.map((action, i) => (
                  <div key={i} style={{ display: 'flex', gap: 10 }}>
                    <div style={{ width: 5, height: 5, borderRadius: 3, background: 'var(--c-primary)', marginTop: 6, flexShrink: 0 }} />
                    <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>{action}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {activeTab === 'recovery' && (
        <motion.div initial="hidden" animate="visible" variants={stagger} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {data.recovery.map((phase, i) => (
            <motion.div key={phase.phase} variants={fadeUp} className="card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 20 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 14, flexShrink: 0,
                  background: i === 0 ? 'var(--c-primary)' : i === 1 ? 'var(--c-accent)' : 'var(--c-border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.125rem', fontWeight: 800, color: 'white', fontFamily: 'var(--font-heading)',
                }}>{phase.phase}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>{phase.label}</div>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 12, letterSpacing: '-0.01em' }}>{phase.title}</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {phase.milestones.map((m, j) => (
                      <div key={j} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                        <div style={{ width: 18, height: 18, borderRadius: 4, flexShrink: 0, marginTop: 1, border: '2px solid var(--c-border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }} />
                        <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>{m}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      <motion.div variants={fadeUp} style={{ marginTop: 24 }}>
        <Link to={`/reports/${assessmentId}`} className="btn-primary" style={{ padding: '10px 24px', fontSize: '0.8125rem' }}>
          <FileText size={14} /> Generate Report <ChevronRight size={14} />
        </Link>
      </motion.div>
    </motion.div>
  )
}
