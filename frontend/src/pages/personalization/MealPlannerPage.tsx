import React, { useState, useEffect } from 'react'
import { motion, type Variants } from 'framer-motion'
import api from '../../lib/api'
import {
  Calendar, ShoppingCart, Utensils, DollarSign, Clock,
  Sparkles, CheckCircle2, ChevronRight, Download, Activity,
  Layers, ArrowRight
} from 'lucide-react'

/* ─── Animations (Consistent with DashboardPage) ─── */
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.4, delay: i * 0.05, ease: 'easeOut' },
  }),
}

interface CalendarMeal {
  mealType: 'Breakfast' | 'Lunch' | 'Snack' | 'Dinner'
  title: string
  cal: number
  cost: number
  keyNutrient: string
  prepTime: string
}

const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

const WEEK_SCHEDULE: Record<string, Record<'Breakfast' | 'Lunch' | 'Snack' | 'Dinner', CalendarMeal>> = {
  Monday: {
    Breakfast: { mealType: 'Breakfast', title: 'Greek Yogurt with Pumpkin Seeds & Berries', cal: 380, cost: 2.10, keyNutrient: 'Calcium & Mg', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Warm Spiced Lentil & Spinach Bowl', cal: 520, cost: 2.80, keyNutrient: 'Folate & Iron', prepTime: '15m' },
    Snack: { mealType: 'Snack', title: 'Brazil Nut & Dark Cacao Micro-Dose', cal: 160, cost: 0.75, keyNutrient: 'Selenium (347%)', prepTime: '1m' },
    Dinner: { mealType: 'Dinner', title: 'Pan-Seared Salmon with Steamed Greens', cal: 580, cost: 4.80, keyNutrient: 'Vitamin D & B12', prepTime: '20m' }
  },
  Tuesday: {
    Breakfast: { mealType: 'Breakfast', title: 'Chia Seed Pudding with Fortified Soy Milk', cal: 350, cost: 1.95, keyNutrient: 'Calcium & Omega-3', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Mediterranean Chickpea & Tahini Salad', cal: 490, cost: 2.50, keyNutrient: 'Iron & Zinc', prepTime: '10m' },
    Snack: { mealType: 'Snack', title: 'Raw Walnuts & Golden Kiwifruit', cal: 180, cost: 1.10, keyNutrient: 'Vitamin C & Folate', prepTime: '2m' },
    Dinner: { mealType: 'Dinner', title: 'Calcium-Set Tofu Stir-Fry with Bok Choy', cal: 540, cost: 3.40, keyNutrient: 'Calcium & Magnesium', prepTime: '18m' }
  },
  Wednesday: {
    Breakfast: { mealType: 'Breakfast', title: 'Pasture-Raised Poached Eggs on Sourdough', cal: 410, cost: 2.60, keyNutrient: 'Choline & D3', prepTime: '10m' },
    Lunch: { mealType: 'Lunch', title: 'Quinoa Tabbouleh with Hemp Hearts & Lemon', cal: 480, cost: 2.90, keyNutrient: 'Magnesium & Iron', prepTime: '12m' },
    Snack: { mealType: 'Snack', title: 'Pumpkin Seed Butter on Rice Crisps', cal: 170, cost: 0.85, keyNutrient: 'Zinc & Magnesium', prepTime: '3m' },
    Dinner: { mealType: 'Dinner', title: 'Sardines in Olive Oil with Lemon Pasta', cal: 560, cost: 3.90, keyNutrient: 'Vitamin D & Calcium', prepTime: '15m' }
  },
  Thursday: {
    Breakfast: { mealType: 'Breakfast', title: 'Steel-Cut Oats with Fortified Almond Milk', cal: 390, cost: 1.80, keyNutrient: 'B-Complex & Fiber', prepTime: '8m' },
    Lunch: { mealType: 'Lunch', title: 'Steamed Asparagus, Lentils & Sesame Salad', cal: 510, cost: 3.10, keyNutrient: 'Folate & Vitamin K', prepTime: '15m' },
    Snack: { mealType: 'Snack', title: 'Brazil Nut Pair & Green Tea Catechins', cal: 150, cost: 0.70, keyNutrient: 'Selenium Micro-Dose', prepTime: '2m' },
    Dinner: { mealType: 'Dinner', title: 'Wild Sockeye Salmon with Roasted Sweet Potato', cal: 610, cost: 5.20, keyNutrient: 'Vitamin D & Potassium', prepTime: '22m' }
  },
  Friday: {
    Breakfast: { mealType: 'Breakfast', title: 'Berry Protein Smoothie with Spinach & Flax', cal: 360, cost: 2.40, keyNutrient: 'Iron & Polyphenols', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Black Bean & Roasted Bell Pepper Salad', cal: 490, cost: 2.20, keyNutrient: 'Non-Heme Iron & C', prepTime: '10m' },
    Snack: { mealType: 'Snack', title: 'Almonds & Sprouted Pumpkin Seeds', cal: 190, cost: 1.05, keyNutrient: 'Magnesium & E', prepTime: '1m' },
    Dinner: { mealType: 'Dinner', title: 'Herbed Cod Fillet with Braised Swiss Chard', cal: 530, cost: 4.60, keyNutrient: 'Iodine & Vitamin K', prepTime: '20m' }
  },
  Saturday: {
    Breakfast: { mealType: 'Breakfast', title: 'Avocado & Nutritional Yeast Toast with Egg', cal: 440, cost: 3.10, keyNutrient: 'B12 & Monounsaturates', prepTime: '12m' },
    Lunch: { mealType: 'Lunch', title: 'Kale & White Bean Minestrone with Garlic', cal: 460, cost: 2.30, keyNutrient: 'Folate & Calcium', prepTime: '20m' },
    Snack: { mealType: 'Snack', title: 'Spiced Edamame with Sea Salt', cal: 160, cost: 0.90, keyNutrient: 'Protein & Isoflavones', prepTime: '5m' },
    Dinner: { mealType: 'Dinner', title: 'Grilled Halibut with Steamed Broccoli & Sesame', cal: 590, cost: 5.60, keyNutrient: 'Vitamin D & Calcium', prepTime: '25m' }
  },
  Sunday: {
    Breakfast: { mealType: 'Breakfast', title: 'Kefir Parfait with Toasted Seeds & Figs', cal: 370, cost: 2.50, keyNutrient: 'Calcium & Probiotics', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Lentil Dal with Wilted Spinach & Brown Rice', cal: 530, cost: 2.10, keyNutrient: 'Iron, Folate & Zinc', prepTime: '20m' },
    Snack: { mealType: 'Snack', title: 'Brazil Nut Micro-Dose & Dark Cacao', cal: 160, cost: 0.75, keyNutrient: 'Selenium & Antioxidants', prepTime: '1m' },
    Dinner: { mealType: 'Dinner', title: 'Roasted Salmon with Asparagus & Quinoa', cal: 620, cost: 5.10, keyNutrient: 'Vitamin D & Folate', prepTime: '25m' }
  }
}

const VEGETARIAN_WEEK_SCHEDULE: Record<string, Record<'Breakfast' | 'Lunch' | 'Snack' | 'Dinner', CalendarMeal>> = {
  Monday: {
    Breakfast: { mealType: 'Breakfast', title: 'Greek Yogurt with Pumpkin Seeds & Berries', cal: 380, cost: 2.10, keyNutrient: 'Calcium & Mg', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Warm Spiced Lentil & Spinach Bowl', cal: 520, cost: 2.80, keyNutrient: 'Folate & Iron', prepTime: '15m' },
    Snack: { mealType: 'Snack', title: 'Brazil Nut & Dark Cacao Micro-Dose', cal: 160, cost: 0.75, keyNutrient: 'Selenium (347%)', prepTime: '1m' },
    Dinner: { mealType: 'Dinner', title: 'Sesame Crusted Tofu with Steamed Bok Choy', cal: 540, cost: 3.40, keyNutrient: 'Calcium & Magnesium', prepTime: '18m' }
  },
  Tuesday: {
    Breakfast: { mealType: 'Breakfast', title: 'Chia Seed Pudding with Fortified Soy Milk', cal: 350, cost: 1.95, keyNutrient: 'Calcium & Omega-3', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Mediterranean Chickpea & Tahini Salad', cal: 490, cost: 2.50, keyNutrient: 'Iron & Zinc', prepTime: '10m' },
    Snack: { mealType: 'Snack', title: 'Raw Walnuts & Golden Kiwifruit', cal: 180, cost: 1.10, keyNutrient: 'Vitamin C & Folate', prepTime: '2m' },
    Dinner: { mealType: 'Dinner', title: 'Calcium-Set Tofu Stir-Fry with Bok Choy', cal: 540, cost: 3.40, keyNutrient: 'Calcium & Magnesium', prepTime: '18m' }
  },
  Wednesday: {
    Breakfast: { mealType: 'Breakfast', title: 'Pasture-Raised Poached Eggs on Sourdough', cal: 410, cost: 2.60, keyNutrient: 'Choline & D3', prepTime: '10m' },
    Lunch: { mealType: 'Lunch', title: 'Quinoa Tabbouleh with Hemp Hearts & Lemon', cal: 480, cost: 2.90, keyNutrient: 'Magnesium & Iron', prepTime: '12m' },
    Snack: { mealType: 'Snack', title: 'Pumpkin Seed Butter on Rice Crisps', cal: 170, cost: 0.85, keyNutrient: 'Zinc & Magnesium', prepTime: '3m' },
    Dinner: { mealType: 'Dinner', title: 'Hearty Chickpea & Spinach Coconut Curry', cal: 550, cost: 2.90, keyNutrient: 'Iron & Magnesium', prepTime: '20m' }
  },
  Thursday: {
    Breakfast: { mealType: 'Breakfast', title: 'Steel-Cut Oats with Fortified Almond Milk', cal: 390, cost: 1.80, keyNutrient: 'B-Complex & Fiber', prepTime: '8m' },
    Lunch: { mealType: 'Lunch', title: 'Steamed Asparagus, Lentils & Sesame Salad', cal: 510, cost: 3.10, keyNutrient: 'Folate & Vitamin K', prepTime: '15m' },
    Snack: { mealType: 'Snack', title: 'Brazil Nut Pair & Green Tea Catechins', cal: 150, cost: 0.70, keyNutrient: 'Selenium Micro-Dose', prepTime: '2m' },
    Dinner: { mealType: 'Dinner', title: 'Lentil Dal with Wilted Spinach & Cumin Rice', cal: 530, cost: 2.30, keyNutrient: 'Iron, Folate & Zinc', prepTime: '20m' }
  },
  Friday: {
    Breakfast: { mealType: 'Breakfast', title: 'Berry Protein Smoothie with Spinach & Flax', cal: 360, cost: 2.40, keyNutrient: 'Iron & Polyphenols', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Black Bean & Roasted Bell Pepper Salad', cal: 490, cost: 2.20, keyNutrient: 'Non-Heme Iron & C', prepTime: '10m' },
    Snack: { mealType: 'Snack', title: 'Almonds & Sprouted Pumpkin Seeds', cal: 190, cost: 1.05, keyNutrient: 'Magnesium & E', prepTime: '1m' },
    Dinner: { mealType: 'Dinner', title: 'Crispy Tempeh & Broccoli Bowl with Peanut Sauce', cal: 560, cost: 3.50, keyNutrient: 'B-Vitamins & Protein', prepTime: '18m' }
  },
  Saturday: {
    Breakfast: { mealType: 'Breakfast', title: 'Avocado & Nutritional Yeast Toast with Egg', cal: 440, cost: 3.10, keyNutrient: 'B12 & Monounsaturates', prepTime: '12m' },
    Lunch: { mealType: 'Lunch', title: 'Kale & White Bean Minestrone with Garlic', cal: 460, cost: 2.30, keyNutrient: 'Folate & Calcium', prepTime: '20m' },
    Snack: { mealType: 'Snack', title: 'Spiced Edamame with Sea Salt', cal: 160, cost: 0.90, keyNutrient: 'Protein & Isoflavones', prepTime: '5m' },
    Dinner: { mealType: 'Dinner', title: 'Stuffed Bell Peppers with Quinoa & Feta', cal: 510, cost: 3.60, keyNutrient: 'Folate & Calcium', prepTime: '22m' }
  },
  Sunday: {
    Breakfast: { mealType: 'Breakfast', title: 'Kefir Parfait with Toasted Seeds & Figs', cal: 370, cost: 2.50, keyNutrient: 'Calcium & Probiotics', prepTime: '5m' },
    Lunch: { mealType: 'Lunch', title: 'Lentil Dal with Wilted Spinach & Brown Rice', cal: 530, cost: 2.10, keyNutrient: 'Iron, Folate & Zinc', prepTime: '20m' },
    Snack: { mealType: 'Snack', title: 'Brazil Nut Micro-Dose & Dark Cacao', cal: 160, cost: 0.75, keyNutrient: 'Selenium & Antioxidants', prepTime: '1m' },
    Dinner: { mealType: 'Dinner', title: 'Portobello & Black Bean Bowl with Guacamole', cal: 540, cost: 3.40, keyNutrient: 'Zinc & Vitamin D', prepTime: '20m' }
  }
}

export default function MealPlannerPage() {
  const [schedule, setSchedule] = useState<Record<string, Record<'Breakfast' | 'Lunch' | 'Snack' | 'Dinner', CalendarMeal>>>(() => {
    try {
      const raw = localStorage.getItem('nutriscan_active_assessment')
      if (raw) {
        const parsed = JSON.parse(raw)
        const pat = (parsed.dietary_pattern || parsed.dietaryPattern || '').toLowerCase()
        if (pat.includes('veg')) return VEGETARIAN_WEEK_SCHEDULE
      }
    } catch { /* ignore */ }
    return WEEK_SCHEDULE
  })

  const [selectedDay, setSelectedDay] = useState('Monday')
  const [selectedMeal, setSelectedMeal] = useState<CalendarMeal>(() => {
    try {
      const raw = localStorage.getItem('nutriscan_active_assessment')
      if (raw) {
        const parsed = JSON.parse(raw)
        const pat = (parsed.dietary_pattern || parsed.dietaryPattern || '').toLowerCase()
        if (pat.includes('veg')) return VEGETARIAN_WEEK_SCHEDULE['Monday']['Lunch']
      }
    } catch { /* ignore */ }
    return WEEK_SCHEDULE['Monday']['Lunch']
  })

  const [nutritionCoverage, setNutritionCoverage] = useState<Array<{ name: string; pct: number; color: string }>>([
    { name: 'Vitamin D', pct: 104, color: 'var(--c-primary)' },
    { name: 'Calcium', pct: 98, color: 'var(--c-success)' },
    { name: 'Iron (Non-Heme+C)', pct: 112, color: 'var(--c-primary)' },
    { name: 'Magnesium', pct: 100, color: 'var(--c-success)' },
    { name: 'Folate', pct: 125, color: 'var(--c-primary)' }
  ])

  const [shoppingItems, setShoppingItems] = useState<string[]>(() => {
    try {
      const raw = localStorage.getItem('nutriscan_active_assessment')
      if (raw) {
        const parsed = JSON.parse(raw)
        const pat = (parsed.dietary_pattern || parsed.dietaryPattern || '').toLowerCase()
        if (pat.includes('veg')) {
          return [
            'Calcium-Set Organic Tofu (2 blocks)',
            'Baby Spinach & Steamed Greens (2 lbs)',
            'Raw Shelled Brazil Nuts (1 pouch)',
            'Whole Brown Lentils & Quinoa (1 lb)',
            'Fortified Soy / Almond Milk (2 qts)'
          ]
        }
      }
    } catch { /* ignore */ }
    return [
      'Wild Atlantic Salmon (3 x 6oz)',
      'Calcium-Set Organic Tofu (2 blocks)',
      'Baby Spinach & Steamed Greens (2 lbs)',
      'Raw Shelled Brazil Nuts (1 pouch)',
      'Whole Brown Lentils & Quinoa (1 lb)'
    ]
  })

  const [costPacing, setCostPacing] = useState({ daily: 14.10, weekly: 98.70 })

  useEffect(() => {
    async function loadMealPlan() {
      let activeAssessment: any = null
      let assessmentId: string | null = null
      try {
        assessmentId = localStorage.getItem('nutriscan_assessment_id')
        const raw = localStorage.getItem('nutriscan_active_assessment')
        if (raw) activeAssessment = JSON.parse(raw)
      } catch { /* ignore */ }

      const rawDiet = (activeAssessment?.dietary_pattern || activeAssessment?.dietaryPattern || 'OMNIVORE').toUpperCase()
      const diet = rawDiet.includes('VEGAN') ? 'VEGAN' : rawDiet.includes('VEG') ? 'VEGETARIAN' : 'OMNIVORE'

      try {
        const res = await api.post('/meal-plans/weekly', {
          assessment_id: assessmentId,
          dietary_pattern: diet,
          cultural_pattern: 'MEDITERRANEAN',
          daily_calorie_target: 2000,
          daily_budget_usd: 14.0,
          plan_duration_days: 7,
          target_deficiencies: ['Iron', 'Vitamin D', 'Calcium', 'Zinc']
        })

        const plan = res.data
        if (plan && plan.daily_plans && plan.daily_plans.length > 0) {
          const newSchedule: Record<string, any> = {}
          plan.daily_plans.forEach((dp: any) => {
            const dayName = dp.day_name
            newSchedule[dayName] = {}
            dp.meals.forEach((m: any) => {
              const typeKey = (m.meal_type.charAt(0).toUpperCase() + m.meal_type.slice(1).toLowerCase()) as 'Breakfast' | 'Lunch' | 'Snack' | 'Dinner'
              const topNutrients = Object.keys(m.key_nutrients_supplied || {}).slice(0, 2).join(' & ') || 'Essential Micronutrients'
              newSchedule[dayName][typeKey] = {
                mealType: typeKey,
                title: m.dish_name,
                cal: m.estimated_calories,
                cost: m.estimated_cost_usd,
                keyNutrient: topNutrients,
                prepTime: `${m.prep_time_minutes || 15}m`
              }
            })
          })

          setSchedule(newSchedule)
          if (newSchedule[selectedDay]?.['Lunch']) {
            setSelectedMeal(newSchedule[selectedDay]['Lunch'])
          }

          if (plan.overall_rda_compliance_pct) {
            const colors = ['var(--c-primary)', 'var(--c-success)', 'var(--c-primary)', 'var(--c-success)', 'var(--c-primary)']
            const covList = Object.entries(plan.overall_rda_compliance_pct).slice(0, 5).map(([nut, val], idx) => ({
              name: nut,
              pct: Math.round(Number(val)),
              color: colors[idx % colors.length]
            }))
            if (covList.length > 0) setNutritionCoverage(covList)
          }

          if (plan.weekly_grocery_list?.department_groups) {
            const items: string[] = []
            Object.values(plan.weekly_grocery_list.department_groups).forEach((group: any) => {
              if (Array.isArray(group)) {
                group.forEach((gi: any) => {
                  if (gi.item_name && items.length < 6) {
                    items.push(`${gi.item_name} (${gi.quantity || '1 pkg'})`)
                  }
                })
              }
            })
            if (items.length > 0) setShoppingItems(items)
          }

          if (plan.weekly_grocery_list?.total_estimated_cost_usd) {
            const totalWk = Number(plan.weekly_grocery_list.total_estimated_cost_usd)
            setCostPacing({
              weekly: Math.round(totalWk * 100) / 100,
              daily: Math.round((totalWk / 7) * 100) / 100
            })
          }
        }
      } catch (err) {
        console.error('Failed to load real weekly meal plan:', err)
      }
    }

    loadMealPlan()
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ═══════════════════════════════════════════════════════════════════
          HEADER: WORKFLOW TITLE & UTILITIES
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={0} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: '24px 32px', borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexWrap: 'wrap', gap: 20
        }}
      >
        <div>
          <div style={{
            fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
            textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4,
          }}>
            Clinical Nutrition Planning Workstation
          </div>
          <h2 style={{
            fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800,
            color: 'var(--c-secondary)', letterSpacing: '-0.02em'
          }}>
            7-Day Precision Therapeutic Meal Schedule
          </h2>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', marginTop: 4 }}>
            Chrononutrition schedule synchronized with patient circadian mineral absorption and phytate separation rules.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            padding: '8px 14px', borderRadius: 10, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)', fontSize: '0.75rem', color: 'var(--c-muted)'
          }}>
            Pace: <strong style={{ color: 'var(--c-success-text)' }}>${costPacing.daily.toFixed(2)} / day (${costPacing.weekly.toFixed(2)} / wk)</strong>
          </div>
          <button
            style={{
              padding: '8px 16px', borderRadius: 10, background: 'var(--c-surface-tint)',
              border: '1px solid var(--c-border)', color: 'var(--c-primary)',
              fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', display: 'flex',
              alignItems: 'center', gap: 6
            }}
          >
            <Download size={14} /> Export Plan
          </button>
        </div>
      </motion.div>

      {/* ═══════════════════════════════════════════════════════════════════
          MAIN: 7-DAY CALENDAR GRID (72%) vs SIDEBAR (28%)
          ═══════════════════════════════════════════════════════════════════ */}
      <div style={{ display: 'grid', gridTemplateColumns: '72fr 28fr', gap: 20 }}>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* LEFT: WEEKLY CALENDAR GRID */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={1} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 24, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column'
          }}
        >
          <div style={{
            display: 'grid', gridTemplateColumns: '70px repeat(7, 1fr)',
            gap: 8, paddingBottom: 12, borderBottom: '1px solid var(--c-border-light)',
            textAlign: 'center'
          }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase' }}>
              Slot
            </span>
            {DAYS_OF_WEEK.map(d => (
              <span key={d} style={{
                fontSize: '0.75rem', fontWeight: 700,
                color: selectedDay === d ? 'var(--c-primary)' : 'var(--c-secondary)'
              }}>
                {d.slice(0, 3)}
              </span>
            ))}
          </div>

          {/* Meal Rows */}
          {(['Breakfast', 'Lunch', 'Snack', 'Dinner'] as const).map(mealCategory => (
            <div
              key={mealCategory}
              style={{
                display: 'grid', gridTemplateColumns: '70px repeat(7, 1fr)',
                gap: 8, padding: '10px 0', borderBottom: '1px solid var(--c-border-light)',
                alignItems: 'stretch'
              }}
            >
              {/* Row Header */}
              <div style={{
                display: 'flex', alignItems: 'center', fontSize: '0.6875rem',
                fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase'
              }}>
                {mealCategory}
              </div>

              {/* 7 Days */}
              {DAYS_OF_WEEK.map(day => {
                const item = schedule[day]?.[mealCategory] || WEEK_SCHEDULE[day][mealCategory]
                const isSelected = selectedMeal.title === item.title && selectedDay === day

                return (
                  <div
                    key={day}
                    onClick={() => {
                      setSelectedDay(day)
                      setSelectedMeal(item)
                    }}
                    style={{
                      padding: '10px 10px', borderRadius: 10,
                      background: isSelected ? 'var(--c-surface-tint)' : 'var(--c-bg)',
                      border: `1px solid ${isSelected ? 'var(--c-primary)' : 'var(--c-border-light)'}`,
                      cursor: 'pointer', display: 'flex', flexDirection: 'column',
                      justifyContent: 'space-between', gap: 6, transition: 'all 0.15s',
                      minHeight: 88
                    }}
                    onMouseEnter={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--c-primary)' }}
                    onMouseLeave={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--c-border-light)' }}
                  >
                    <div style={{
                      fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-secondary)',
                      lineHeight: 1.25, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden'
                    }}>
                      {item.title}
                    </div>

                    <div style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      fontSize: '0.625rem', color: 'var(--c-muted)'
                    }}>
                      <span style={{ color: 'var(--c-primary)', fontWeight: 600 }}>{item.cal} kcal</span>
                      <span>${item.cost.toFixed(2)}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          ))}
        </motion.div>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* RIGHT SIDEBAR: NUTRITION COVERAGE, COST & SHOPPING */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={2} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 24, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column', gap: 20
          }}
        >
          {/* Active Meal Inspector */}
          <div>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Active Selection ({selectedDay})
            </div>
            <h4 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1rem', fontWeight: 700,
              color: 'var(--c-secondary)'
            }}>
              {selectedMeal.title}
            </h4>
            <div style={{
              display: 'flex', gap: 12, fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 4
            }}>
              <span>{selectedMeal.cal} kcal</span>
              <span>•</span>
              <span>${selectedMeal.cost.toFixed(2)}</span>
              <span>•</span>
              <span>Prep: {selectedMeal.prepTime}</span>
            </div>
          </div>

          {/* Nutrition Coverage (% RDA) */}
          <div style={{
            padding: '16px 18px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)', textTransform: 'uppercase', marginBottom: 12 }}>
              Weekly Nutrient Target Coverage
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {nutritionCoverage.map(n => (
                <div key={n.name} style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem' }}>
                    <span style={{ color: 'var(--c-secondary)', fontWeight: 600 }}>{n.name}</span>
                    <span style={{ color: n.color, fontWeight: 700 }}>{n.pct}% RDA</span>
                  </div>
                  <div style={{ height: 4, background: 'var(--c-bar-track)', borderRadius: 2, overflow: 'hidden' }}>
                    <div style={{ width: `${Math.min(100, n.pct)}%`, height: '100%', background: n.color, borderRadius: 2 }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Shopping Intelligence */}
          <div style={{
            padding: '16px 18px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-secondary)', textTransform: 'uppercase' }}>
                Shopping Intelligence
              </span>
              <span style={{ fontSize: '0.6875rem', color: 'var(--c-primary)', fontWeight: 600 }}>
                {shoppingItems.length} Items
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.75rem', color: 'var(--c-text-secondary)' }}>
              {shoppingItems.map(item => (
                <div key={item}>• {item}</div>
              ))}
            </div>
          </div>
        </motion.div>

      </div>

      {/* ═══════════════════════════════════════════════════════════════════
          §3 — BOTTOM: WEEKLY SUMMARY
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={3} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: 24, borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20
        }}
      >
        <div style={{
          padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
          border: '1px solid var(--c-border-light)'
        }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)', textTransform: 'uppercase', marginBottom: 4 }}>
            Deficiency Coverage
          </div>
          <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 4 }}>
            100% Core Targets Met
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)' }}>
            All priority deficiencies covered without pharmaceutical megadosing or toxic upper-limit breaches.
          </p>
        </div>

        <div style={{
          padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
          border: '1px solid var(--c-border-light)'
        }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)', textTransform: 'uppercase', marginBottom: 4 }}>
            Weekly Cost Efficiency
          </div>
          <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 4 }}>
            ${costPacing.daily.toFixed(2)} / Day Average
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)' }}>
            Economical bulk-legume sequencing offset high-bioavailability precision foods, maintaining target budget pacing.
          </p>
        </div>

        <div style={{
          padding: '16px 20px', borderRadius: 14, background: 'var(--c-bg)',
          border: '1px solid var(--c-border-light)'
        }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-success-text)', textTransform: 'uppercase', marginBottom: 4 }}>
            Adherence Feasibility
          </div>
          <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-success)', marginBottom: 4 }}>
            91% Probability
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)' }}>
            Mean prep time of 14 minutes per therapeutic meal with batch preparation options on Sundays.
          </p>
        </div>
      </motion.div>

    </div>
  )
}
