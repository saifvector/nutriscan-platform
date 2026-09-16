import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import {
  Activity,
  Layers,
  Sliders,
  ArrowRightLeft,
  Database,
  Utensils,
  ChevronRight,
  UserCheck,
  Stethoscope,
  RefreshCw,
  AlertTriangle
} from 'lucide-react'
import api from '../lib/api'
import { FeatureContributionWaterfall } from '../components/explainability/FeatureContributionWaterfall'
import { ClinicalEvidencePanel, type EvidenceItem } from '../components/explainability/ClinicalEvidencePanel'
import { NutrientInteractionExplorer, type NutrientInteractionItem } from '../components/explainability/NutrientInteractionExplorer'
import { WhatIfSimulatorPanel } from '../components/explainability/WhatIfSimulatorPanel'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.05 } } }

const TARGET_OPTIONS = [
  { id: 'target_iron_deficiency', label: 'Iron Deficiency' },
  { id: 'target_iron_deficiency_anemia', label: 'Iron Deficiency Anemia' },
  { id: 'target_vitamin_d_deficiency', label: 'Vitamin D Deficiency' },
  { id: 'target_vitamin_d_insufficiency', label: 'Vitamin D Insufficiency' },
  { id: 'target_folate_deficiency', label: 'Folate Deficiency' },
  { id: 'target_magnesium_deficiency', label: 'Magnesium Deficiency' },
  { id: 'target_potassium_deficiency', label: 'Potassium Deficiency' },
  { id: 'target_calcium_deficiency', label: 'Calcium Deficiency' },
  { id: 'target_selenium_deficiency', label: 'Selenium Deficiency' }
]

type ActiveTab = 'WATERFALL' | 'SIMULATION' | 'INTERACTIONS' | 'EVIDENCE'
type ViewMode = 'PATIENT' | 'CLINICIAN'

export default function ExplainabilityPage() {
  const { assessmentId } = useParams<{ assessmentId?: string }>()

  const [selectedTarget, setSelectedTarget] = useState<string>('target_iron_deficiency')
  const [activeTab, setActiveTab] = useState<ActiveTab>('WATERFALL')
  const [viewMode, setViewMode] = useState<ViewMode>('CLINICIAN')

  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // API State
  const [explanationData, setExplanationData] = useState<any>(null)
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([])
  const [interactions, setInteractions] = useState<NutrientInteractionItem[]>([])

  // Load explanation data when selectedTarget changes
  useEffect(() => {
    let isMounted = true
    const fetchExplanation = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const [expRes, evRes, intRes] = await Promise.all([
          api.get(`/explainability/prediction-explanation?target=${selectedTarget}`),
          api.get('/explainability/evidence-summary'),
          api.get('/explainability/nutrient-interactions')
        ])

        if (isMounted) {
          setExplanationData(expRes.data)
          setEvidenceItems(evRes.data.evidence_items || [])
          setInteractions(intRes.data.interactions || [])
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err?.response?.data?.detail || 'Failed to load explainability data from server.')
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    fetchExplanation()
    return () => {
      isMounted = false
    }
  }, [selectedTarget])

  const targetExplanation = explanationData?.target_explanations?.[selectedTarget] || null

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger} className="max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <motion.div variants={fadeUp} className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-600 dark:text-teal-400 mb-1">
            <Activity className="w-4 h-4" /> Phase 11 Explainable Clinical Intelligence
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Clinical Reasoning & Evidence Engine
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
            SHAP feature attribution decomposed into risk and protective drivers, verified against NIH ODS, USDA FoodData Central, and NHANES cohorts.
          </p>
        </div>

        {/* View Mode & Target Selector */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Target Dropdown */}
          <select
            value={selectedTarget}
            onChange={e => setSelectedTarget(e.target.value)}
            className="px-3.5 py-2 text-xs md:text-sm font-semibold rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 cursor-pointer"
          >
            {TARGET_OPTIONS.map(opt => (
              <option key={opt.id} value={opt.id}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Perspective Switcher */}
          <div className="inline-flex rounded-xl p-1 bg-slate-100 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80">
            <button
              onClick={() => setViewMode('PATIENT')}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                viewMode === 'PATIENT'
                  ? 'bg-white dark:bg-slate-700 text-teal-600 dark:text-teal-300 shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" /> Patient View
            </button>
            <button
              onClick={() => setViewMode('CLINICIAN')}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                viewMode === 'CLINICIAN'
                  ? 'bg-white dark:bg-slate-700 text-teal-600 dark:text-teal-300 shadow-xs'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Stethoscope className="w-3.5 h-3.5" /> Clinician View
            </button>
          </div>
        </div>
      </motion.div>

      {/* Navigation Tabs */}
      <motion.div variants={fadeUp} className="flex border-b border-slate-200 dark:border-slate-800 overflow-x-auto">
        <button
          onClick={() => setActiveTab('WATERFALL')}
          className={`pb-3 px-4 text-xs md:text-sm font-semibold inline-flex items-center gap-2 border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'WATERFALL'
              ? 'border-teal-600 text-teal-600 dark:border-teal-400 dark:text-teal-400'
              : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" /> Feature Attribution
        </button>

        <button
          onClick={() => setActiveTab('SIMULATION')}
          className={`pb-3 px-4 text-xs md:text-sm font-semibold inline-flex items-center gap-2 border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'SIMULATION'
              ? 'border-teal-600 text-teal-600 dark:border-teal-400 dark:text-teal-400'
              : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <Sliders className="w-4 h-4" /> What-If Simulator
        </button>

        <button
          onClick={() => setActiveTab('INTERACTIONS')}
          className={`pb-3 px-4 text-xs md:text-sm font-semibold inline-flex items-center gap-2 border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'INTERACTIONS'
              ? 'border-teal-600 text-teal-600 dark:border-teal-400 dark:text-teal-400'
              : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <ArrowRightLeft className="w-4 h-4" /> Nutrient Interactions
        </button>

        <button
          onClick={() => setActiveTab('EVIDENCE')}
          className={`pb-3 px-4 text-xs md:text-sm font-semibold inline-flex items-center gap-2 border-b-2 transition-all whitespace-nowrap ${
            activeTab === 'EVIDENCE'
              ? 'border-teal-600 text-teal-600 dark:border-teal-400 dark:text-teal-400'
              : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
          }`}
        >
          <Database className="w-4 h-4" /> Clinical Evidence & Literature
        </button>
      </motion.div>

      {/* Loading & Error States */}
      {isLoading && (
        <div className="py-20 flex flex-col items-center justify-center text-slate-400">
          <RefreshCw className="w-8 h-8 animate-spin text-teal-600 mb-3" />
          <p className="text-sm font-medium">Decomposing SHAP attributions and clinical evidence...</p>
        </div>
      )}

      {error && !isLoading && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Tab 1: Feature Attribution & Waterfall */}
      {!isLoading && !error && activeTab === 'WATERFALL' && targetExplanation && (
        <motion.div variants={fadeUp} className="space-y-6">
          <FeatureContributionWaterfall
            targetName={targetExplanation.target_display_name}
            riskTier={targetExplanation.risk_tier}
            calibratedProbability={targetExplanation.calibrated_probability}
            positiveDrivers={targetExplanation.positive_contributors}
            protectiveDrivers={targetExplanation.protective_factors}
          />

          {/* Clinical Narratives Card */}
          <div className="bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 p-6 shadow-sm">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-4">
              {viewMode === 'PATIENT' ? 'Patient Summary & Guidance' : 'Clinician Diagnostic & Mechanistic Analysis'}
            </h3>

            {viewMode === 'PATIENT' ? (
              <div className="p-4 rounded-xl bg-teal-50/40 dark:bg-teal-950/20 border border-teal-500/20 space-y-3">
                <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed font-medium">
                  {targetExplanation.narratives.patient_summary}
                </p>
                <div className="pt-2 border-t border-teal-500/20 text-xs text-teal-800 dark:text-teal-300">
                  <strong>Recommended Next Steps:</strong> Focus on incorporating protective foods highlighted in green, and review potential medication/supplement spacing with your care team.
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-50/70 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700/60 space-y-3">
                <p className="text-xs md:text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-mono">
                  {targetExplanation.narratives.clinician_analysis}
                </p>
                <div className="pt-2 border-t border-slate-200 dark:border-slate-700 text-xs text-slate-500 dark:text-slate-400 flex items-center justify-between">
                  <span>Confidence: <strong>{Math.round(targetExplanation.narratives.confidence_score * 100)}%</strong></span>
                  <span>Model: <strong>Phase 10C Calibrated Gradient Boosted Ensemble</strong></span>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Tab 2: What-If Simulation */}
      {!isLoading && activeTab === 'SIMULATION' && (
        <motion.div variants={fadeUp}>
          <WhatIfSimulatorPanel initialTarget={selectedTarget} />
        </motion.div>
      )}

      {/* Tab 3: Nutrient Interactions */}
      {!isLoading && activeTab === 'INTERACTIONS' && (
        <motion.div variants={fadeUp}>
          <NutrientInteractionExplorer interactions={interactions} />
        </motion.div>
      )}

      {/* Tab 4: Clinical Evidence & Literature */}
      {!isLoading && activeTab === 'EVIDENCE' && (
        <motion.div variants={fadeUp}>
          <ClinicalEvidencePanel evidenceItems={evidenceItems} selectedTarget={selectedTarget} />
        </motion.div>
      )}

      {/* Bottom CTA to Recommendations */}
      <motion.div variants={fadeUp} className="pt-4 flex items-center justify-between">
        <Link
          to="/dashboard"
          className="text-xs font-semibold text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
        >
          ← Return to Clinical Dashboard
        </Link>

        {assessmentId && (
          <Link
            to={`/recommendations/${assessmentId}`}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs md:text-sm font-semibold text-white bg-teal-600 hover:bg-teal-700 transition-all shadow-sm"
          >
            <Utensils className="w-4 h-4" /> View Traceable Recommendations <ChevronRight className="w-4 h-4" />
          </Link>
        )}
      </motion.div>
    </motion.div>
  )
}
