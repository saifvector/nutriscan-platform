import React, { useState } from 'react'
import { motion, type Variants } from 'framer-motion'
import { Utensils, Clock, DollarSign, Globe, ShieldCheck, Flame, ShoppingBag, Bookmark, Sparkles, ChevronRight } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}

interface MealRecipeItem {
  meal_type: string
  recipe_title: string
  description: string
  calories: number
  protein_g: number
  carbs_g: number
  fats_g: number
  target_nutrients_closed: string[]
  nutrient_density_score: number
  bioavailability_score: number
  correction_efficiency_score: number
  preparation_time_minutes: number
  budget_level: string
  dietary_tags: string[]
  cuisine_type: string
  key_ingredients: string[]
  clinical_notes: string
}

interface DailyMealPlan {
  day_name: string
  day_number: number
  breakfast: MealRecipeItem
  lunch: MealRecipeItem
  dinner: MealRecipeItem
  snack: MealRecipeItem
  daily_calories: number
  daily_protein_g: number
  daily_carbs_g: number
  daily_fats_g: number
  daily_average_bioavailability: number
  daily_average_correction_efficiency: number
}

interface WeeklyMealPlan {
  plan_title: string
  dietary_preference: string
  budget_level: string
  cuisine_preference: string
  days: DailyMealPlan[]
  weekly_grocery_staples: string[]
}

interface Props {
  mealData: {
    target_deficiencies: string[]
    dietary_preference: string
    budget_level: string
    cuisine_preference: string
    daily_plan: DailyMealPlan
    weekly_plan?: WeeklyMealPlan | null
    deficiency_recovery_templates: Array<{
      template_id: string
      title: string
      focus_nutrients: string[]
      clinical_rationale: string
      sample_lunch: string
      synergy_multiplier: string
    }>
  }
  onFilterChange: (diet: string, budget: string, cuisine: string) => void
}

export default function SmartMealPlanner({ mealData, onFilterChange }: Props) {
  const [viewMode, setViewMode] = useState<'DAILY' | 'WEEKLY' | 'TEMPLATES'>('DAILY')
  const [selectedDayIdx, setSelectedDayIdx] = useState<number>(0)
  const [selectedDiet, setSelectedDiet] = useState<string>(mealData.dietary_preference || 'OMNIVORE')
  const [selectedBudget, setSelectedBudget] = useState<string>(mealData.budget_level || 'MODERATE')
  const [selectedCuisine, setSelectedCuisine] = useState<string>(mealData.cuisine_preference || 'MEDITERRANEAN')

  const handleDietChange = (d: string) => {
    setSelectedDiet(d)
    onFilterChange(d, selectedBudget, selectedCuisine)
  }

  const handleBudgetChange = (b: string) => {
    setSelectedBudget(b)
    onFilterChange(selectedDiet, b, selectedCuisine)
  }

  const handleCuisineChange = (c: string) => {
    setSelectedCuisine(c)
    onFilterChange(selectedDiet, selectedBudget, c)
  }

  const activeDailyPlan = viewMode === 'WEEKLY' && mealData.weekly_plan
    ? mealData.weekly_plan.days[selectedDayIdx] || mealData.daily_plan
    : mealData.daily_plan

  const mealsList = [
    { label: 'Breakfast', item: activeDailyPlan.breakfast, color: '#e3b341', time: '08:00 AM' },
    { label: 'Lunch', item: activeDailyPlan.lunch, color: '#388bfd', time: '01:00 PM' },
    { label: 'Dinner', item: activeDailyPlan.dinner, color: '#a371f7', time: '07:30 PM' },
    { label: 'Targeted Snack', item: activeDailyPlan.snack, color: '#3fb950', time: '04:30 PM' },
  ]

  return (
    <motion.div initial="hidden" animate="visible" variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Top Filter Bar: Diet, Budget, Cuisine & View Mode */}
      <div className="card" style={{
        padding: '16px 20px',
        background: 'rgba(22, 27, 34, 0.85)',
        border: '1px solid rgba(48, 54, 61, 0.6)',
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: 16
      }}>
        {/* Constraints Selectors */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center' }}>
          {/* Diet Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase' }}>Diet:</span>
            <select
              value={selectedDiet}
              onChange={(e) => handleDietChange(e.target.value)}
              style={{
                background: 'rgba(13, 17, 23, 0.8)',
                color: 'var(--c-secondary)',
                border: '1px solid rgba(48, 54, 61, 0.8)',
                borderRadius: 6,
                padding: '6px 10px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <option value="OMNIVORE">Omnivore</option>
              <option value="VEGAN">Vegan</option>
              <option value="VEGETARIAN">Vegetarian</option>
              <option value="KETO">Ketogenic</option>
              <option value="MEDITERRANEAN">Mediterranean</option>
              <option value="DAIRY_FREE">Dairy-Free</option>
              <option value="GLUTEN_FREE">Gluten-Free</option>
            </select>
          </div>

          {/* Budget Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase' }}>Budget:</span>
            <div style={{ display: 'flex', background: 'rgba(13, 17, 23, 0.8)', padding: 2, borderRadius: 6, border: '1px solid rgba(48, 54, 61, 0.8)' }}>
              {['BUDGET', 'MODERATE', 'PREMIUM'].map(b => (
                <button
                  key={b}
                  onClick={() => handleBudgetChange(b)}
                  style={{
                    padding: '4px 8px',
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    borderRadius: 4,
                    border: 'none',
                    background: selectedBudget === b ? 'var(--c-primary)' : 'transparent',
                    color: selectedBudget === b ? '#ffffff' : 'var(--c-muted)',
                    cursor: 'pointer'
                  }}
                >
                  {b === 'BUDGET' ? '$' : (b === 'MODERATE' ? '$$' : '$$$')}
                </button>
              ))}
            </div>
          </div>

          {/* Cuisine Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-muted)', textTransform: 'uppercase' }}>Cuisine:</span>
            <select
              value={selectedCuisine}
              onChange={(e) => handleCuisineChange(e.target.value)}
              style={{
                background: 'rgba(13, 17, 23, 0.8)',
                color: 'var(--c-secondary)',
                border: '1px solid rgba(48, 54, 61, 0.8)',
                borderRadius: 6,
                padding: '6px 10px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <option value="MEDITERRANEAN">Mediterranean</option>
              <option value="ASIAN">Asian</option>
              <option value="AMERICAN">American</option>
              <option value="GLOBAL_FUSION">Global Fusion</option>
            </select>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div style={{ display: 'flex', background: 'rgba(13, 17, 23, 0.9)', padding: 3, borderRadius: 8, border: '1px solid rgba(48, 54, 61, 0.7)' }}>
          <button
            onClick={() => setViewMode('DAILY')}
            style={{
              padding: '6px 14px',
              fontSize: '0.75rem',
              fontWeight: 600,
              borderRadius: 6,
              border: 'none',
              background: viewMode === 'DAILY' ? 'var(--c-primary)' : 'transparent',
              color: viewMode === 'DAILY' ? '#ffffff' : 'var(--c-muted)',
              cursor: 'pointer'
            }}
          >
            Daily Plan
          </button>
          <button
            onClick={() => setViewMode('WEEKLY')}
            style={{
              padding: '6px 14px',
              fontSize: '0.75rem',
              fontWeight: 600,
              borderRadius: 6,
              border: 'none',
              background: viewMode === 'WEEKLY' ? 'var(--c-primary)' : 'transparent',
              color: viewMode === 'WEEKLY' ? '#ffffff' : 'var(--c-muted)',
              cursor: 'pointer'
            }}
          >
            7-Day Schedule
          </button>
          <button
            onClick={() => setViewMode('TEMPLATES')}
            style={{
              padding: '6px 14px',
              fontSize: '0.75rem',
              fontWeight: 600,
              borderRadius: 6,
              border: 'none',
              background: viewMode === 'TEMPLATES' ? 'var(--c-primary)' : 'transparent',
              color: viewMode === 'TEMPLATES' ? '#ffffff' : 'var(--c-muted)',
              cursor: 'pointer'
            }}
          >
            Deficiency Protocols
          </button>
        </div>
      </div>

      {/* Mode 1 & 2: Daily & Weekly Plans */}
      {viewMode !== 'TEMPLATES' && (
        <>
          {/* If Weekly: Day Navigator Carousel Tabs */}
          {viewMode === 'WEEKLY' && mealData.weekly_plan && (
            <div style={{
              display: 'flex',
              gap: 8,
              overflowX: 'auto',
              paddingBottom: 4
            }}>
              {mealData.weekly_plan.days.map((d, idx) => (
                <button
                  key={d.day_name}
                  onClick={() => setSelectedDayIdx(idx)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: 8,
                    border: selectedDayIdx === idx ? '1px solid var(--c-primary)' : '1px solid rgba(48, 54, 61, 0.6)',
                    background: selectedDayIdx === idx ? 'rgba(56, 139, 253, 0.15)' : 'rgba(22, 27, 34, 0.7)',
                    color: selectedDayIdx === idx ? 'var(--c-secondary)' : 'var(--c-muted)',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 2,
                    minWidth: 90
                  }}
                >
                  <span>Day {d.day_number}</span>
                  <span style={{ fontSize: '0.6875rem', fontWeight: 500, color: 'var(--c-muted)' }}>{d.day_name}</span>
                </button>
              ))}
            </div>
          )}

          {/* Daily Nutrition Macro Bar */}
          <div className="card" style={{
            padding: '14px 20px',
            background: 'rgba(13, 17, 23, 0.75)',
            border: '1px solid rgba(48, 54, 61, 0.6)',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 16
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ fontSize: '0.875rem', fontWeight: 800, color: 'var(--c-secondary)' }}>
                {activeDailyPlan.day_name} Summary:
              </div>
              <div style={{ display: 'flex', gap: 12, fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                <span>Calories: <strong style={{ color: 'var(--c-secondary)' }}>{activeDailyPlan.daily_calories} kcal</strong></span>
                <span>Protein: <strong style={{ color: '#388bfd' }}>{activeDailyPlan.daily_protein_g}g</strong></span>
                <span>Carbs: <strong style={{ color: '#e3b341' }}>{activeDailyPlan.daily_carbs_g}g</strong></span>
                <span>Fats: <strong style={{ color: '#a371f7' }}>{activeDailyPlan.daily_fats_g}g</strong></span>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <span style={{
                fontSize: '0.6875rem',
                fontWeight: 700,
                color: '#3fb950',
                background: 'rgba(63, 185, 80, 0.12)',
                padding: '4px 10px',
                borderRadius: 6,
                border: '1px solid rgba(63, 185, 80, 0.25)'
              }}>
                Bioavailability: {activeDailyPlan.daily_average_bioavailability}%
              </span>
              <span style={{
                fontSize: '0.6875rem',
                fontWeight: 700,
                color: '#388bfd',
                background: 'rgba(56, 139, 253, 0.12)',
                padding: '4px 10px',
                borderRadius: 6,
                border: '1px solid rgba(56, 139, 253, 0.25)'
              }}>
                Gap Correction Efficiency: {activeDailyPlan.daily_average_correction_efficiency}%
              </span>
            </div>
          </div>

          {/* 4 Meal Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: 16 }}>
            {mealsList.map(({ label, item, color, time }) => (
              <div
                key={label}
                className="card card-hover"
                style={{
                  padding: 20,
                  background: 'rgba(22, 27, 34, 0.85)',
                  border: '1px solid rgba(48, 54, 61, 0.6)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12
                }}
              >
                {/* Header with Type & Time */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ width: 4, height: 16, borderRadius: 2, background: color }} />
                    <span style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {label}
                    </span>
                    <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>({time})</span>
                  </div>
                  <span style={{
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    color: '#3fb950',
                    background: 'rgba(63, 185, 80, 0.12)',
                    padding: '2px 7px',
                    borderRadius: 4
                  }}>
                    {item.correction_efficiency_score}% Efficiency
                  </span>
                </div>

                {/* Recipe Title & Description */}
                <div>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--c-secondary)', margin: '0 0 6px 0', lineHeight: 1.3 }}>
                    {item.recipe_title}
                  </h4>
                  <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.4, margin: 0 }}>
                    {item.description}
                  </p>
                </div>

                {/* Target Nutrients Badges */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {item.target_nutrients_closed.map(nut => (
                    <span
                      key={nut}
                      style={{
                        fontSize: '0.625rem',
                        fontWeight: 700,
                        color: 'var(--c-primary)',
                        background: 'rgba(56, 139, 253, 0.1)',
                        border: '1px solid rgba(56, 139, 253, 0.25)',
                        padding: '2px 6px',
                        borderRadius: 4
                      }}
                    >
                      +{nut}
                    </span>
                  ))}
                </div>

                {/* Macros & Preparation */}
                <div style={{
                  padding: '8px 12px',
                  background: 'rgba(13, 17, 23, 0.6)',
                  borderRadius: 6,
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '0.6875rem',
                  color: 'var(--c-muted)'
                }}>
                  <span><Flame size={12} style={{ verticalAlign: -2, marginRight: 2 }} /> {item.calories} kcal</span>
                  <span><strong>{item.protein_g}g</strong> Prot</span>
                  <span><strong>{item.carbs_g}g</strong> Carb</span>
                  <span><strong>{item.fats_g}g</strong> Fat</span>
                  <span><Clock size={12} style={{ verticalAlign: -2, marginRight: 2 }} /> {item.preparation_time_minutes}m</span>
                </div>

                {/* Key Ingredients */}
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', lineHeight: 1.4 }}>
                  <strong>Ingredients:</strong> {item.key_ingredients.join(', ')}
                </div>

                {/* Clinical Notes */}
                <div style={{
                  marginTop: 'auto',
                  padding: '8px 10px',
                  background: 'rgba(56, 139, 253, 0.06)',
                  borderLeft: '3px solid var(--c-primary)',
                  borderRadius: '0 4px 4px 0',
                  fontSize: '0.6875rem',
                  color: 'var(--c-text-secondary)',
                  lineHeight: 1.4
                }}>
                  <strong>Clinical Bioavailability:</strong> {item.clinical_notes}
                </div>
              </div>
            ))}
          </div>

          {/* If Weekly: Consolidated Grocery Staples */}
          {viewMode === 'WEEKLY' && mealData.weekly_plan && (
            <div className="card" style={{ padding: 22, background: 'rgba(22, 27, 34, 0.85)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
                <ShoppingBag size={18} color="var(--c-primary)" />
                <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                  Aggregated Weekly Clinical Grocery Staples (7-Day Rotation)
                </span>
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))',
                gap: 8
              }}>
                {mealData.weekly_plan.weekly_grocery_staples.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '8px 12px',
                      background: 'rgba(13, 17, 23, 0.6)',
                      borderRadius: 6,
                      border: '1px solid rgba(48, 54, 61, 0.5)',
                      fontSize: '0.75rem',
                      color: 'var(--c-secondary)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8
                    }}
                  >
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#3fb950' }} />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Mode 3: Specialized Deficiency Recovery Templates */}
      {viewMode === 'TEMPLATES' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 4 }}>
            Evidence-based clinical culinary protocols engineered to reverse severe single or multi-nutrient deficits:
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 16 }}>
            {mealData.deficiency_recovery_templates.map(tpl => (
              <div
                key={tpl.template_id}
                className="card"
                style={{
                  padding: 22,
                  background: 'rgba(22, 27, 34, 0.85)',
                  border: '1px solid rgba(48, 54, 61, 0.7)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Bookmark size={18} color="var(--c-primary)" />
                  <h4 style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--c-secondary)', margin: 0 }}>
                    {tpl.title}
                  </h4>
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {tpl.focus_nutrients.map(nut => (
                    <span
                      key={nut}
                      style={{
                        fontSize: '0.6875rem',
                        fontWeight: 700,
                        color: '#a371f7',
                        background: 'rgba(163, 113, 247, 0.12)',
                        border: '1px solid rgba(163, 113, 247, 0.3)',
                        padding: '2px 8px',
                        borderRadius: 4
                      }}
                    >
                      {nut} Focus
                    </span>
                  ))}
                </div>

                <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', lineHeight: 1.5, margin: 0 }}>
                  {tpl.clinical_rationale}
                </p>

                <div style={{ padding: '10px 12px', background: 'rgba(13, 17, 23, 0.7)', borderRadius: 6, fontSize: '0.75rem', color: 'var(--c-secondary)' }}>
                  <strong>Sample Core Meal:</strong> {tpl.sample_lunch}
                </div>

                <div style={{
                  marginTop: 'auto',
                  padding: '8px 12px',
                  background: 'rgba(63, 185, 80, 0.1)',
                  borderRadius: 6,
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  color: '#3fb950',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6
                }}>
                  <Sparkles size={14} />
                  {tpl.synergy_multiplier}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
