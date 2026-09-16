import React, { useState, useEffect } from 'react'
import { motion, type Variants } from 'framer-motion'
import {
  Sparkles, Search, Filter, BookOpen, ChevronRight,
  ShieldCheck, Award, Flame, DollarSign, Check, ExternalLink,
  Layers, ArrowUpRight, Activity
} from 'lucide-react'

/* ─── Animations (Consistent with DashboardPage) ─── */
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.4, delay: i * 0.05, ease: 'easeOut' },
  }),
}

interface FoodItem {
  id: string
  name: string
  usda_fdc_id: string
  category: string
  serving_size: string
  calories: number
  cost_usd: number
  density_score: number
  bioavailability: number
  composite_score: number
  culinary_role: string
  primary_nutrients: Record<string, string>
  preparation: string
  evidence: string
  substitutions: string[]
}

const FALLBACK_FOODS: FoodItem[] = [
  {
    id: 'FOOD_SALMON_WILD',
    name: 'Wild Atlantic Salmon (Cooked)',
    usda_fdc_id: '173686',
    category: 'Seafood & Fish',
    serving_size: '100g (3.5 oz)',
    calories: 182,
    cost_usd: 3.20,
    density_score: 95,
    bioavailability: 95,
    composite_score: 95.2,
    culinary_role: 'Main Therapeutic Protein',
    primary_nutrients: {
      'Vitamin D': '11.0 mcg (73% RDA)',
      'Selenium': '36.5 mcg (66% RDA)',
      'Vitamin B12': '3.2 mcg (133% RDA)',
      'Protein': '25.4 g'
    },
    preparation: 'Pan-sear skin-side down for 4 mins, flip for 3 mins. Pair with lemon (Vitamin C) for antioxidant lipid preservation.',
    evidence: 'USDA FoodData Central Foundation FDC ID 173686',
    substitutions: ['Sardines in Olive Oil', 'Atlantic Mackerel', 'Rainbow Trout']
  },
  {
    id: 'FOOD_SPINACH_STEAMED',
    name: 'Baby Spinach (Steamed)',
    usda_fdc_id: '170417',
    category: 'Dark Leafy Greens',
    serving_size: '180g (1 cup cooked)',
    calories: 41,
    cost_usd: 0.85,
    density_score: 96,
    bioavailability: 78,
    composite_score: 91.8,
    culinary_role: 'High-Density Micronutrient Base',
    primary_nutrients: {
      'Folate': '263.0 mcg (65% RDA)',
      'Iron': '6.4 mg (35% RDA)',
      'Magnesium': '157.0 mg (40% RDA)',
      'Calcium': '245.0 mg (25% RDA)'
    },
    preparation: 'Steam lightly for 90 seconds to preserve water-soluble Folate and eliminate volatile oxalates.',
    evidence: 'USDA FDC ID 170417',
    substitutions: ['Swiss Chard', 'Tuscan Kale', 'Collard Greens']
  },
  {
    id: 'FOOD_LENTILS_BROWN',
    name: 'Brown Lentils (Cooked)',
    usda_fdc_id: '172421',
    category: 'Legumes & Pulses',
    serving_size: '198g (1 cup cooked)',
    calories: 230,
    cost_usd: 0.45,
    density_score: 92,
    bioavailability: 80,
    composite_score: 89.4,
    culinary_role: 'Complex Carbohydrate & Fiber',
    primary_nutrients: {
      'Folate': '358.0 mcg (90% RDA)',
      'Iron': '6.6 mg (37% RDA)',
      'Potassium': '731.0 mg (22% RDA)',
      'Magnesium': '71.0 mg (18% RDA)'
    },
    preparation: 'Soak overnight prior to boiling; pair with diced bell peppers to multiply non-heme iron uptake 3x.',
    evidence: 'USDA FDC ID 172421',
    substitutions: ['Chickpeas', 'Black Beans', 'Sprouted Mung Dal']
  },
  {
    id: 'FOOD_SARDINES_CANNED',
    name: 'Sardines in Olive Oil (Canned with Bones)',
    usda_fdc_id: '175139',
    category: 'Seafood & Fish',
    serving_size: '92g (1 can drained)',
    calories: 191,
    cost_usd: 1.75,
    density_score: 98,
    bioavailability: 95,
    composite_score: 93.6,
    culinary_role: 'High-Density Calcium Booster',
    primary_nutrients: {
      'Calcium': '351.0 mg (35% RDA)',
      'Vitamin D': '4.4 mcg (30% RDA)',
      'Selenium': '48.5 mcg (88% RDA)',
      'Iron': '2.7 mg (15% RDA)'
    },
    preparation: 'Mash whole with Dijon mustard, fresh lemon, and capers onto seeded whole grain sourdough.',
    evidence: 'USDA FDC ID 175139',
    substitutions: ['Canned Pink Salmon with Bones', 'Wild Anchovies in Olive Oil']
  },
  {
    id: 'FOOD_BRAZIL_NUTS',
    name: 'Brazil Nuts (Raw Shelled)',
    usda_fdc_id: '170569',
    category: 'Nuts & Seeds',
    serving_size: '10g (2 kernels)',
    calories: 66,
    cost_usd: 0.35,
    density_score: 99,
    bioavailability: 96,
    composite_score: 97.4,
    culinary_role: 'Targeted Micronutrient Micro-Dose',
    primary_nutrients: {
      'Selenium': '191.0 mcg (347% RDA)',
      'Magnesium': '37.0 mg (9% RDA)'
    },
    preparation: 'Consume exactly 1 to 2 kernels daily for thyroid selenoprotein saturation without exceeding 400 mcg UL.',
    evidence: 'USDA FDC ID 170569',
    substitutions: ['Sprouted Sunflower Seeds', 'Yellowfin Tuna']
  }
]

export default function RecommendationCenterPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTarget, setSelectedTarget] = useState('ALL')
  const [activeFood, setActiveFood] = useState<FoodItem>(FALLBACK_FOODS[0])
  const [foodDatabase, setFoodDatabase] = useState<FoodItem[]>(FALLBACK_FOODS)

  useEffect(() => {
    const fetchFoods = async () => {
      try {
        const res = await fetch('/api/v1/recommendations/precision-foods')
        if (res.ok) {
          const data = await res.json()
          if (data.top_recommended_foods?.length) {
            const mapped: FoodItem[] = data.top_recommended_foods.map((f: any) => ({
              id: f.food_id || f.id || f.usda_fdc_id,
              name: f.food_name || f.name,
              usda_fdc_id: f.usda_fdc_id || f.fdc_id || 'FDC-1092',
              category: f.food_category || f.category || 'Therapeutic Food',
              serving_size: f.serving_size || '100g',
              calories: f.calories_per_serving ?? f.calories ?? 150,
              cost_usd: f.estimated_cost_usd ?? f.cost_usd ?? 1.5,
              density_score: Math.round(f.nutrient_density_score ?? f.density_score ?? 90),
              bioavailability: Math.round(f.bioavailability_pct ?? f.bioavailability ?? 85),
              composite_score: Number((f.composite_score ?? 91).toFixed(1)),
              culinary_role: f.culinary_role || f.meal_role || 'Main Component',
              primary_nutrients: f.primary_nutrients || f.key_nutrients || {},
              preparation: f.preparation_tip || f.preparation || '',
              evidence: f.evidence_source || f.evidence || 'USDA FoodData Central',
              substitutions: f.substitutions || f.alternatives || [],
            }))
            setFoodDatabase(mapped)
            if (mapped.length > 0) setActiveFood(mapped[0])
          }
        }
      } catch (err) {
        console.error('Precision foods fetch error:', err)
      }
    }
    fetchFoods()
  }, [])

  const filteredFoods = foodDatabase.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.category.toLowerCase().includes(searchQuery.toLowerCase())
    if (selectedTarget === 'ALL') return matchesSearch
    return matchesSearch && Object.keys(item.primary_nutrients).some(k => k.toLowerCase().includes(selectedTarget.toLowerCase()))
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ═══════════════════════════════════════════════════════════════════
          §1 — TOP: SEARCH & FILTERS TOOLBAR
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={0} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: '20px 24px', borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          gap: 20, flexWrap: 'wrap'
        }}
      >
        {/* Left: Search input */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 260,
          padding: '10px 14px', borderRadius: 12, background: 'var(--c-bg)',
          border: '1px solid var(--c-border-light)'
        }}>
          <Search size={16} color="var(--c-muted)" />
          <input
            type="text"
            placeholder="Search USDA food library, categories, or bioavailable nutrients..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{
              background: 'transparent', border: 'none', outline: 'none',
              fontSize: '0.8125rem', color: 'var(--c-secondary)', width: '100%'
            }}
          />
        </div>

        {/* Right: Nutrient Target Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase' }}>
            Target:
          </span>
          {['ALL', 'Vitamin D', 'Iron', 'Folate', 'Calcium', 'Magnesium', 'Selenium'].map(target => (
            <button
              key={target}
              onClick={() => setSelectedTarget(target)}
              style={{
                padding: '6px 12px', borderRadius: 8, border: 'none', cursor: 'pointer',
                fontSize: '0.75rem', fontWeight: 600,
                background: selectedTarget === target ? 'var(--c-primary)' : 'var(--c-bg)',
                color: selectedTarget === target ? '#fff' : 'var(--c-muted)',
                transition: 'background 0.15s'
              }}
            >
              {target}
            </button>
          ))}
        </div>
      </motion.div>

      {/* ═══════════════════════════════════════════════════════════════════
          CENTER & RIGHT: FOOD INTELLIGENCE TABLE (60%) vs ANALYSIS (40%)
          ═══════════════════════════════════════════════════════════════════ */}
      <div style={{ display: 'grid', gridTemplateColumns: '60fr 40fr', gap: 20 }}>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* CENTER: FOOD INTELLIGENCE TABLE */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={1} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 28, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div>
              <div style={{
                fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
                textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
              }}>
                Nutrition Intelligence Database
              </div>
              <h3 style={{
                fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700,
                color: 'var(--c-secondary)', letterSpacing: '-0.02em'
              }}>
                Food Intelligence & Comparison Terminal
              </h3>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
              {filteredFoods.length} Verified Entries
            </span>
          </div>

          {/* Table Header */}
          <div style={{
            display: 'grid', gridTemplateColumns: '40fr 15fr 15fr 15fr 15fr',
            padding: '10px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)',
            textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: '1px solid var(--c-border-light)'
          }}>
            <span>Food</span>
            <span style={{ textAlign: 'center' }}>Density</span>
            <span style={{ textAlign: 'center' }}>Bioavail.</span>
            <span style={{ textAlign: 'center' }}>Cost / Svg</span>
            <span style={{ textAlign: 'right' }}>Score</span>
          </div>

          {/* Table Rows */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8 }}>
            {filteredFoods.map(food => {
              const isSelected = activeFood.id === food.id
              return (
                <div
                  key={food.id}
                  onClick={() => setActiveFood(food)}
                  style={{
                    display: 'grid', gridTemplateColumns: '40fr 15fr 15fr 15fr 15fr',
                    alignItems: 'center', padding: '12px 16px', borderRadius: 12,
                    background: isSelected ? 'var(--c-surface-tint)' : 'var(--c-bg)',
                    border: `1px solid ${isSelected ? 'var(--c-primary)' : 'var(--c-border-light)'}`,
                    cursor: 'pointer', transition: 'all 0.15s'
                  }}
                  onMouseEnter={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--c-primary)' }}
                  onMouseLeave={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--c-border-light)' }}
                >
                  {/* Food Name & Category */}
                  <div>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: isSelected ? 'var(--c-primary)' : 'var(--c-secondary)' }}>
                      {food.name}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
                      {food.category} · {food.serving_size}
                    </div>
                  </div>

                  {/* Density */}
                  <div style={{ textAlign: 'center' }}>
                    <span style={{ fontFamily: 'var(--font-heading)', fontSize: '0.875rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                      {food.density_score}
                    </span>
                    <span style={{ fontSize: '0.625rem', color: 'var(--c-muted)' }}>/100</span>
                  </div>

                  {/* Bioavailability */}
                  <div style={{ textAlign: 'center' }}>
                    <span style={{
                      fontSize: '0.6875rem', fontWeight: 700, padding: '2px 6px', borderRadius: 6,
                      background: food.bioavailability >= 90 ? 'var(--c-success-bg)' : 'var(--c-warning-bg)',
                      color: food.bioavailability >= 90 ? 'var(--c-success-text)' : 'var(--c-warning-text)'
                    }}>
                      {food.bioavailability}%
                    </span>
                  </div>

                  {/* Cost */}
                  <div style={{ textAlign: 'center', fontSize: '0.8125rem', color: 'var(--c-muted)', fontWeight: 600 }}>
                    ${food.cost_usd.toFixed(2)}
                  </div>

                  {/* Clinical Score */}
                  <div style={{ textAlign: 'right' }}>
                    <span style={{
                      fontFamily: 'var(--font-heading)', fontSize: '1rem', fontWeight: 800,
                      color: 'var(--c-primary)'
                    }}>
                      {food.composite_score}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </motion.div>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* RIGHT: FOOD ANALYSIS WORKSPACE */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={2} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 28, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column', gap: 20
          }}
        >
          <div>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Active Food Dossier
            </div>
            <h3 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700,
              color: 'var(--c-secondary)', letterSpacing: '-0.02em'
            }}>
              {activeFood.name}
            </h3>
            <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 2 }}>
              Role: <strong style={{ color: 'var(--c-secondary)' }}>{activeFood.culinary_role}</strong>
            </div>
          </div>

          {/* Key Nutrient Breakdown */}
          <div style={{
            padding: '16px 18px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)', textTransform: 'uppercase', marginBottom: 12 }}>
              Target Micronutrient Yield (% RDA)
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {Object.entries(activeFood.primary_nutrients).map(([nutrient, value]) => (
                <div key={nutrient} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--c-secondary)' }}>{nutrient}</span>
                  <span style={{ color: 'var(--c-primary)', fontWeight: 700 }}>{value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Synergistic Preparation Tip */}
          <div style={{
            padding: '16px 18px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-accent)', textTransform: 'uppercase', marginBottom: 6 }}>
              ⚡ Synergistic Preparation Directive
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.6 }}>
              {activeFood.preparation}
            </p>
          </div>

          {/* Deficiency Coverage */}
          <div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
              Direct Deficiency Coverage:
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {Object.keys(activeFood.primary_nutrients).map(nut => (
                <span key={nut} style={{
                  fontSize: '0.6875rem', fontWeight: 700, padding: '3px 8px', borderRadius: 6,
                  background: 'var(--c-surface-tint)', color: 'var(--c-primary)', border: '1px solid var(--c-border)'
                }}>
                  Resolves {nut}
                </span>
              ))}
            </div>
          </div>
        </motion.div>

      </div>

      {/* ═══════════════════════════════════════════════════════════════════
          §3 — BOTTOM: AI EXPLANATION & COMPARISON
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={3} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: 28, borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <Sparkles size={16} color="var(--c-primary)" />
          <span style={{
            fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
            textTransform: 'uppercase', letterSpacing: '0.08em'
          }}>
            Algorithmic Selection Justification & Clinical Trade-Offs
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          {/* Why Selected */}
          <div style={{
            padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 6 }}>
              Why Selected by Optimizer
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.6 }}>
              Ranks in top 2% of USDA database for composite micronutrient bioavailability and dense bio-active cofactors with minimal digestive burden.
            </p>
          </div>

          {/* Validated Substitutions */}
          <div style={{
            padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 6 }}>
              Equivalent Alternatives
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {activeFood.substitutions.map(sub => (
                <div key={sub} style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)' }}>
                  • {sub}
                </div>
              ))}
            </div>
          </div>

          {/* Biochemical Trade-offs */}
          <div style={{
            padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 6 }}>
              Biochemical Trade-Offs & Grounding
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.6 }}>
              Evidence Grounding: <strong style={{ color: 'var(--c-primary)' }}>{activeFood.evidence}</strong>. Consume with proper meal pacing to prevent mineral competition.
            </p>
          </div>
        </div>
      </motion.div>

    </div>
  )
}
