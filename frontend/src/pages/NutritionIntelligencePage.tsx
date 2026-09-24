import React, { useState, useEffect, useMemo } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import {
  Sparkles,
  Layers,
  Utensils,
  RefreshCw,
  Pill,
  TrendingUp,
  Target,
  FileText,
  Share2,
  AlertCircle,
  BrainCircuit,
  Activity
} from 'lucide-react'

import NutrientGapDashboard from './intelligence/NutrientGapDashboard'
import SmartMealPlanner from './intelligence/SmartMealPlanner'
import FoodSwapExplorer from './intelligence/FoodSwapExplorer'
import SupplementGuidanceCenter from './intelligence/SupplementGuidanceCenter'
import RecoverySimulator from './intelligence/RecoverySimulator'
import ActionPlanCenter from './intelligence/ActionPlanCenter'
import AssessmentRequiredState from '../components/common/AssessmentRequiredState'
import { ResumeAssessmentModal } from '../components/session/ResumeAssessmentModal'
import { sessionManager } from '../lib/sessionManager'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.06 } } }

export default function NutritionIntelligencePage() {
  const { assessmentId } = useParams()
  const navigate = useNavigate()
  const [activeSession, setActiveSession] = useState(() => sessionManager.getActiveSession())
  const [showResumeModal, setShowResumeModal] = useState(false)
  const storedPrevious = useMemo(() => sessionManager.getStoredPreviousAssessment(), [])

  const effectiveId = activeSession?.active_assessment_id || (assessmentId && assessmentId !== 'demo' ? assessmentId : null)
  const id = effectiveId

  const [activeTab, setActiveTab] = useState<'gaps' | 'meals' | 'swaps' | 'supplements' | 'projections' | 'action-plan'>('gaps')
  const [loading, setLoading] = useState<boolean>(true)
  const [planData, setPlanData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Current constraints
  const [diet, setDiet] = useState<string>('OMNIVORE')
  const [budget, setBudget] = useState<string>('MODERATE')
  const [cuisine, setCuisine] = useState<string>('MEDITERRANEAN')

  const fetchIntelligencePlan = async (currentDiet = diet, currentBudget = budget, currentCuisine = cuisine) => {
    if (!id) return
    try {
      setLoading(true)
      setError(null)
      const res = await fetch('/api/v1/intelligence/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assessment_id: id,
          dietary_preference: currentDiet,
          budget_level: currentBudget,
          cuisine_preference: currentCuisine,
          gender: 'FEMALE'
        })
      })

      if (!res.ok) {
        throw new Error(`Failed to generate intelligence plan: ${res.statusText}`)
      }

      const data = await res.json()
      setPlanData(data)
    } catch (err: any) {
      console.error('Error fetching nutrition intelligence plan:', err)
      setError(err.message || 'Error loading clinical intelligence plan.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (id) {
      fetchIntelligencePlan(diet, budget, cuisine)
    }
  }, [id])

  if (!effectiveId) {
    return (
      <>
        <AssessmentRequiredState
          title="Clinical Decision Support Assessment Required"
          description="Autonomous clinical intelligence plans, USDA nutrient gap analysis, and precision meal planning require an active nutritional assessment. Complete an assessment to generate your personalized clinical protocol."
          actionLabel="Start Assessment"
          onAction={() => navigate('/assessment')}
          secondaryActionLabel={storedPrevious ? "Resume Previous Assessment" : undefined}
          onSecondaryAction={storedPrevious ? () => setShowResumeModal(true) : undefined}
          icon={BrainCircuit}
        />

        {storedPrevious && (
          <ResumeAssessmentModal
            isOpen={showResumeModal}
            assessmentId={storedPrevious.id}
            assessmentDate={storedPrevious.date}
            onResume={() => {
              sessionManager.setActiveSession(storedPrevious.id, storedPrevious.date, 'completed')
              setActiveSession(sessionManager.getActiveSession())
              setShowResumeModal(false)
            }}
            onStartNew={() => {
              sessionManager.clearActiveSession()
              setActiveSession(null)
              setShowResumeModal(false)
              navigate('/assessment')
            }}
            onClose={() => setShowResumeModal(false)}
          />
        )}
      </>
    )
  }

  const handleFilterChange = (newDiet: string, newBudget: string, newCuisine: string) => {
    setDiet(newDiet)
    setBudget(newBudget)
    setCuisine(newCuisine)
    fetchIntelligencePlan(newDiet, newBudget, newCuisine)
  }

  const tabs = [
    { key: 'gaps' as const, label: 'Nutrient Gap Dashboard', icon: Layers },
    { key: 'meals' as const, label: 'Smart Meal Planner', icon: Utensils },
    { key: 'swaps' as const, label: 'Food Swap Explorer', icon: RefreshCw },
    { key: 'supplements' as const, label: 'Supplement Guidance', icon: Pill },
    { key: 'projections' as const, label: 'Recovery Simulator', icon: TrendingUp },
    { key: 'action-plan' as const, label: 'Action Plan Center', icon: Target },
  ]

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger} style={{ paddingBottom: 48 }}>
      {/* Page Header */}
      <motion.div variants={fadeUp} style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{
                fontSize: '0.6875rem',
                fontWeight: 700,
                color: 'var(--c-primary)',
                background: 'rgba(56, 139, 253, 0.12)',
                padding: '2px 8px',
                borderRadius: 4,
                textTransform: 'uppercase',
                letterSpacing: '0.06em'
              }}>
                Phase 8 Clinical Decision Layer
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                Case ID: <strong>{id}</strong>
              </span>
            </div>
            <h1 style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.85rem',
              fontWeight: 900,
              letterSpacing: '-0.03em',
              margin: '0 0 6px 0',
              color: 'var(--c-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: 10
            }}>
              <BrainCircuit size={28} color="var(--c-primary)" />
              Nutrition Intelligence & Decision Engine
            </h1>
            <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', margin: 0 }}>
              Autonomous clinical decision support synthesizing multi-nutrient risks, knowledge graph causal centrality, USDA composition, and NIH RDA/UL guidelines.
            </p>
          </div>

          {/* Quick Deep Link to Network Graph */}
          <div style={{ display: 'flex', gap: 10 }}>
            <Link
              to={`/network/${id}`}
              className="card card-hover"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 14px',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--c-primary)',
                textDecoration: 'none'
              }}
            >
              <Share2 size={14} /> View Causal Graph
            </Link>
            <Link
              to={`/outcomes/${id}`}
              className="card card-hover"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 14px',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--c-primary-light, #14b8a6)',
                borderColor: 'rgba(20, 184, 166, 0.3)',
                background: 'rgba(20, 184, 166, 0.08)',
                textDecoration: 'none'
              }}
            >
              <Activity size={14} /> Outcome Learning (Phase 9)
            </Link>
            <Link
              to={`/reports/${id}`}
              className="card card-hover"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 14px',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--c-secondary)',
                textDecoration: 'none'
              }}
            >
              <FileText size={14} /> Clinical Report
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Tabs Navigation */}
      <motion.div
        variants={fadeUp}
        style={{
          display: 'flex',
          gap: 6,
          marginBottom: 24,
          background: 'var(--c-bg-secondary)',
          padding: 4,
          borderRadius: 10,
          border: '1px solid var(--c-border)',
          overflowX: 'auto',
          width: 'fit-content',
          maxWidth: '100%'
        }}
      >
        {tabs.map(tab => {
          const isActive = activeTab === tab.key
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 7,
                padding: '9px 16px',
                borderRadius: 8,
                border: 'none',
                background: isActive ? 'var(--c-primary)' : 'transparent',
                color: isActive ? '#ffffff' : 'var(--c-muted)',
                fontSize: '0.8125rem',
                fontWeight: 600,
                cursor: 'pointer',
                fontFamily: 'var(--font-body)',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease'
              }}
            >
              <tab.icon size={15} />
              {tab.label}
            </button>
          )
        })}
      </motion.div>

      {/* Loading State */}
      {loading && (
        <div style={{
          padding: '60px 0',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 12
        }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            border: '3px solid rgba(56, 139, 253, 0.2)',
            borderTopColor: 'var(--c-primary)',
            animation: 'spin 0.8s linear infinite'
          }} />
          <span style={{ fontSize: '0.875rem', color: 'var(--c-muted)' }}>
            Synthesizing clinical decision matrix & recovery projections...
          </span>
        </div>
      )}

      {/* Error Banner */}
      {error && !loading && (
        <div className="card" style={{
          padding: 20,
          background: 'rgba(248, 81, 73, 0.1)',
          border: '1px solid rgba(248, 81, 73, 0.4)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          color: '#f85149'
        }}>
          <AlertCircle size={20} />
          <div style={{ fontSize: '0.875rem' }}>{error}</div>
        </div>
      )}

      {/* Active Tab View */}
      {!loading && planData && (
        <>
          {activeTab === 'gaps' && (
            <NutrientGapDashboard gapsData={planData.nutrient_gaps} />
          )}

          {activeTab === 'meals' && (
            <SmartMealPlanner
              mealData={planData.meal_intelligence}
              onFilterChange={handleFilterChange}
            />
          )}

          {activeTab === 'swaps' && (
            <FoodSwapExplorer substitutions={planData.food_substitutions.substitutions} />
          )}

          {activeTab === 'supplements' && (
            <SupplementGuidanceCenter supplementData={planData.supplement_guidance} />
          )}

          {activeTab === 'projections' && (
            <RecoverySimulator projectionData={planData.recovery_projections} />
          )}

          {activeTab === 'action-plan' && (
            <ActionPlanCenter actionPlanData={planData.clinical_action_plan} />
          )}
        </>
      )}
    </motion.div>
  )
}
