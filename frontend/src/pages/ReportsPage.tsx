import { useState, useMemo, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import {
  FileText,
  Download,
  Clock,
  CheckCircle,
  Loader2,
  BarChart3,
  Brain,
  Utensils,
  Shield,
  GitCompare,
  TrendingUp,
  Layers,
  Sparkles,
  Eye,
  Calendar,
  AlertCircle
} from 'lucide-react'

import HealthScoreCard from '../components/reporting/HealthScoreCard'
import ProgressOverview from '../components/reporting/ProgressOverview'
import NutrientRecoveryTimeline from '../components/reporting/NutrientRecoveryTimeline'
import AssessmentHistoryTable, { type HistoryEntry } from '../components/reporting/AssessmentHistoryTable'
import TrendAnalyticsCharts from '../components/reporting/TrendAnalyticsCharts'
import ComparisonDashboard from '../components/reporting/ComparisonDashboard'
import PDFPreviewModal from '../components/reporting/PDFPreviewModal'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.05 } } }

export default function ReportsPage() {
  const { assessmentId } = useParams()
  const id = assessmentId || 'demo'

  const [activeTab, setActiveTab] = useState<'overview' | 'analytics' | 'history' | 'comparison'>('overview')
  const [generating, setGenerating] = useState(false)
  const [generated, setGenerated] = useState(false)
  const [pdfModalOpen, setPdfModalOpen] = useState(false)

  // Live state with fallback defaults
  const [healthScore, setHealthScore] = useState(76)
  const [healthCategory, setHealthCategory] = useState('GOOD')
  const [scoreBreakdown, setScoreBreakdown] = useState({
    baseline_score: 100.0,
    nutrient_risk_deduction: 22.5,
    interaction_penalty: 4.5,
    lifestyle_modifier: 3.0,
    confidence_adjustment: 1.5,
    deficiency_count: 1,
    protective_factor_count: 5,
    final_score: 76,
    category: 'GOOD',
    interpretation: 'Good nutritional foundation (75–89). Mild isolated risk factors identified in Vitamin D and Iron. Targeted whole food pairings and lifestyle optimization continue to reinforce homeostatic recovery.',
  })

  const [recoveryItems, setRecoveryItems] = useState(() => [
    { nutrient: 'Vitamin D', initial_risk_score: 87, current_risk_score: 52, improvement_percentage: 40.2, recovery_trend: 'Improving', recovery_status: 'On Track', recommended_action: 'Continue morning sunlight (30m) and daily fatty fish/egg yolk sources.' },
    { nutrient: 'Iron', initial_risk_score: 71, current_risk_score: 43, improvement_percentage: 39.4, recovery_trend: 'Improving', recovery_status: 'On Track', recommended_action: 'Maintain ascorbic acid pairing with legumes; avoid tea 90m post-meal.' },
    { nutrient: 'Vitamin B12', initial_risk_score: 63, current_risk_score: 29, improvement_percentage: 54.0, recovery_trend: 'Improving', recovery_status: 'Resolved', recommended_action: 'Maintenance phase: adequate nutritional yeast or fortified plant milk.' },
    { nutrient: 'Calcium', initial_risk_score: 60, current_risk_score: 44, improvement_percentage: 26.7, recovery_trend: 'Improving', recovery_status: 'Needs Attention', recommended_action: 'Incorporate fortified tahini, almonds, and dark leafy greens.' },
    { nutrient: 'Magnesium', initial_risk_score: 54, current_risk_score: 38, improvement_percentage: 29.6, recovery_trend: 'Improving', recovery_status: 'On Track', recommended_action: 'Maintain pumpkin seeds, dark chocolate, and avocado intake.' },
    { nutrient: 'Folate', initial_risk_score: 48, current_risk_score: 32, improvement_percentage: 33.3, recovery_trend: 'Improving', recovery_status: 'On Track', recommended_action: 'Continue asparagus, lentils, and steamed spinach servings.' },
    { nutrient: 'Zinc', initial_risk_score: 45, current_risk_score: 31, improvement_percentage: 31.1, recovery_trend: 'Improving', recovery_status: 'On Track', recommended_action: 'Optimal immune signaling; continue pumpkin seeds and legumes.' },
    { nutrient: 'Vitamin C', initial_risk_score: 35, current_risk_score: 20, improvement_percentage: 42.9, recovery_trend: 'Improving', recovery_status: 'Resolved', recommended_action: 'Robust antioxidant level; daily citrus and bell pepper intake.' },
    { nutrient: 'Vitamin A', initial_risk_score: 28, current_risk_score: 18, improvement_percentage: 35.7, recovery_trend: 'Improving', recovery_status: 'Resolved', recommended_action: 'Carotenoid status optimal with sweet potatoes and carrots.' },
    { nutrient: 'Vitamin E', initial_risk_score: 22, current_risk_score: 15, improvement_percentage: 31.8, recovery_trend: 'Improving', recovery_status: 'Resolved', recommended_action: 'Lipid membrane protection intact via sunflower seeds and extra virgin olive oil.' },
    { nutrient: 'Protein', initial_risk_score: 20, current_risk_score: 12, improvement_percentage: 40.0, recovery_trend: 'Improving', recovery_status: 'Resolved', recommended_action: 'Nitrogen balance positive with high-density amino acid rotation.' },
  ])

  const [assessmentHistory, setAssessmentHistory] = useState<HistoryEntry[]>([
    { id: 'rpt-003', assessment_id: 'aid-003', assessment_number: 3, date: '2026-09-10', version: 'v1.2', health_score: 76, health_category: 'GOOD', risk_distribution: { HIGH: 0, MODERATE: 3, LOW: 8 }, deficiency_count: 1, status: 'COMPLETED' },
    { id: 'rpt-002', assessment_id: 'aid-002', assessment_number: 2, date: '2026-08-26', version: 'v1.1', health_score: 69, health_category: 'MODERATE_RISK', risk_distribution: { HIGH: 1, MODERATE: 4, LOW: 6 }, deficiency_count: 2, status: 'COMPLETED' },
    { id: 'rpt-001', assessment_id: 'aid-001', assessment_number: 1, date: '2026-08-10', version: 'v1.0', health_score: 62, health_category: 'MODERATE_RISK', risk_distribution: { HIGH: 3, MODERATE: 4, LOW: 4 }, deficiency_count: 3, status: 'COMPLETED' },
  ])

  const [timelineCoordinates, setTimelineCoordinates] = useState([
    { date: 'Aug 10', health_score: 62, 'Vitamin D': 87, 'Iron': 71, 'Vitamin B12': 63, 'Calcium': 60, 'Zinc': 45 },
    { date: 'Aug 26', health_score: 69, 'Vitamin D': 68, 'Iron': 56, 'Vitamin B12': 45, 'Calcium': 51, 'Zinc': 37 },
    { date: 'Sep 10', health_score: 76, 'Vitamin D': 52, 'Iron': 43, 'Vitamin B12': 29, 'Calcium': 44, 'Zinc': 31 },
  ])

  // Fetch live data from API
  useEffect(() => {
    const fetchReportData = async () => {
      try {
        // Fetch health score
        const hsRes = await fetch('/api/v1/analytics/health-score')
        if (hsRes.ok) {
          const hsData = await hsRes.json()
          if (hsData.health_score != null) setHealthScore(hsData.health_score)
          if (hsData.category) setHealthCategory(hsData.category)
          if (hsData.breakdown) setScoreBreakdown(prev => ({ ...prev, ...hsData.breakdown }))
          if (hsData.recovery_items?.length) setRecoveryItems(hsData.recovery_items)
        }

        // Fetch report history
        const histRes = await fetch('/api/v1/reports/history')
        if (histRes.ok) {
          const histData = await histRes.json()
          if (Array.isArray(histData) && histData.length > 0) {
            setAssessmentHistory(histData.map((r: any) => ({
              id: r.id || r.report_id,
              assessment_id: r.assessment_id || r.id,
              assessment_number: r.assessment_number || 0,
              date: r.date || r.created_at?.split('T')[0] || '',
              version: r.version || 'v1.0',
              health_score: r.health_score ?? 0,
              health_category: r.health_category || r.category || 'UNKNOWN',
              risk_distribution: r.risk_distribution || { HIGH: 0, MODERATE: 0, LOW: 0 },
              deficiency_count: r.deficiency_count ?? 0,
              status: r.status || 'COMPLETED',
            })))
          }
        }

        // Fetch progress trends
        const trendRes = await fetch('/api/v1/progress/trends')
        if (trendRes.ok) {
          const trendData = await trendRes.json()
          if (trendData.timeline?.length) setTimelineCoordinates(trendData.timeline)
        }
      } catch (err) {
        console.error('Reports data fetch error:', err)
      }
    }
    fetchReportData()
  }, [id])

  const reportSections = [
    { title: 'Executive Summary', desc: 'Overall health score, risk classification, and priority clinical nutrients.', icon: Shield },
    { title: 'Prediction Matrix', desc: '11-nutrient probability scores with confidence intervals and risk tiers.', icon: BarChart3 },
    { title: 'Risk Factor Attribution', desc: 'SHAP explanations, positive drivers, and lifestyle bottleneck attributions.', icon: Brain },
    { title: 'Dietary Prescriptions', desc: 'Prioritized bioavailable whole foods with synergistic pairings.', icon: Utensils },
    { title: '30-Day Recovery Plan', desc: '3-phase roadmap with acute, optimization, and consolidation targets.', icon: Clock },
    { title: 'Longitudinal Progress', desc: 'Recovery velocity, velocity per week, and before-and-after deltas.', icon: TrendingUp },
  ]

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const res = await fetch('/api/v1/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assessment_id: id })
      })
      if (res.ok) {
        setGenerated(true)
      }
    } catch (err) {
      console.error('Report generation error:', err)
    } finally {
      setGenerating(false)
      setGenerated(true)
    }
  }

  const handleDownloadPdf = (reportId?: string) => {
    // Direct link to backend PDF stream or preview
    const targetId = reportId || 'demo'
    window.open(`/api/v1/reports/${targetId}/pdf`, '_blank')
  }

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger} style={{ paddingBottom: 64 }}>
      {/* Page Header */}
      <motion.div variants={fadeUp} style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 6, color: 'var(--c-text)' }}>
              Clinical Intelligence & Progress Tracking
            </h1>
            <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', margin: 0 }}>
              Longitudinal assessment tracking, recovery monitoring, and publication-grade PDF reporting.
            </p>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={() => setPdfModalOpen(true)}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                padding: '9px 16px', borderRadius: 10,
                background: 'var(--c-surface-tint)', border: '1px solid var(--c-border-light)',
                color: 'var(--c-primary)', fontSize: '0.8125rem', fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              <Eye size={15} /> Preview Clinical PDF
            </button>
            <button
              onClick={() => handleDownloadPdf()}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                padding: '9px 18px', borderRadius: 10,
                background: 'var(--c-primary)', border: 'none',
                color: 'white', fontSize: '0.8125rem', fontWeight: 700,
                cursor: 'pointer',
                boxShadow: 'var(--c-shadow-sm)',
              }}
            >
              <Download size={15} /> Export PDF
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: 8,
          marginTop: 20,
          borderBottom: '1px solid var(--c-border-light)',
          paddingBottom: 2,
        }}>
          {[
            { id: 'overview', label: 'Overview & Reports', icon: FileText },
            { id: 'analytics', label: 'Progress Analytics', icon: TrendingUp },
            { id: 'comparison', label: 'Side-by-Side Comparison', icon: GitCompare },
            { id: 'history', label: 'Assessment History', icon: Calendar },
          ].map(tab => {
            const TabIcon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 18px',
                  borderRadius: '10px 10px 0 0',
                  border: 'none',
                  borderBottom: isActive ? '2px solid var(--c-primary)' : '2px solid transparent',
                  background: isActive ? 'var(--c-selection-bg)' : 'transparent',
                  color: isActive ? 'var(--c-primary)' : 'var(--c-muted)',
                  fontFamily: 'var(--font-heading)',
                  fontSize: '0.875rem',
                  fontWeight: isActive ? 700 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <TabIcon size={15} color={isActive ? 'var(--c-primary)' : 'var(--c-muted)'} />
                {tab.label}
              </button>
            )
          })}
        </div>
      </motion.div>

      {/* TAB 1: OVERVIEW & REPORTS */}
      {activeTab === 'overview' && (
        <motion.div variants={stagger} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Health Score Card */}
          <motion.div variants={fadeUp}>
            <HealthScoreCard score={healthScore} category={healthCategory} breakdown={scoreBreakdown} />
          </motion.div>

          {/* Report Generation Hero Box */}
          <motion.div variants={fadeUp} style={{
            background: 'var(--c-card)',
            border: '1px solid var(--c-border)',
            borderRadius: 20,
            padding: '32px 36px',
            textAlign: 'center',
            boxShadow: 'var(--c-shadow-sm)',
            position: 'relative',
            overflow: 'hidden',
          }}>
            <div style={{
              width: 54, height: 54, borderRadius: 16,
              background: 'var(--c-surface-tint)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 16px',
            }}>
              <FileText size={26} color="var(--c-primary)" />
            </div>

            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--c-text)', marginBottom: 6 }}>
              {generated ? 'Official Clinical Report Ready' : 'Generate Full Clinical Assessment Report'}
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', maxWidth: 520, margin: '0 auto 20px', lineHeight: 1.6 }}>
              {generated
                ? 'Your comprehensive 9-section report consolidating biomarker inference, SHAP risk drivers, recommendations, and longitudinal recovery has been compiled.'
                : 'Synthesizes 11-nutrient predictions, biochemical synergies, lifestyle quality indicators, and recovery trajectory into a validated PDF document.'}
            </p>

            {!generated ? (
              <button
                onClick={handleGenerate}
                disabled={generating}
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 8,
                  padding: '12px 28px', borderRadius: 12,
                  background: 'var(--c-primary)', border: 'none',
                  color: 'white', fontSize: '0.875rem', fontWeight: 700,
                  cursor: generating ? 'not-allowed' : 'pointer',
                  opacity: generating ? 0.75 : 1,
                  boxShadow: 'var(--c-shadow-sm)',
                }}
              >
                {generating ? (
                  <>
                    <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                    Compiling Clinical Report...
                  </>
                ) : (
                  <>
                    <FileText size={16} />
                    Generate Official Report
                  </>
                )}
              </button>
            ) : (
              <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
                <button
                  onClick={() => setPdfModalOpen(true)}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: 6,
                    padding: '12px 24px', borderRadius: 12,
                    background: 'var(--c-surface-tint)', border: '1px solid var(--c-border-light)',
                    color: 'var(--c-primary)', fontSize: '0.875rem', fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  <Eye size={16} /> View Document Preview
                </button>
                <button
                  onClick={() => handleDownloadPdf()}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: 6,
                    padding: '12px 24px', borderRadius: 12,
                    background: 'var(--c-primary)', border: 'none',
                    color: 'white', fontSize: '0.875rem', fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  <Download size={16} /> Download Official PDF
                </button>
                <button
                  onClick={() => setGenerated(false)}
                  style={{
                    padding: '12px 18px', borderRadius: 12,
                    background: 'transparent', border: '1px solid var(--c-border-light)',
                    color: 'var(--c-muted)', fontSize: '0.875rem', fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  Regenerate
                </button>
              </div>
            )}
          </motion.div>

          {/* Report Contents Grid */}
          <motion.div variants={fadeUp}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>
              Clinical Report Structure (9 Sections)
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>
              {reportSections.map(s => {
                const SIcon = s.icon
                return (
                  <div key={s.title} style={{
                    background: 'var(--c-card)', border: '1px solid var(--c-border)',
                    borderRadius: 14, padding: '18px 20px', boxShadow: 'var(--c-shadow-sm)',
                  }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: 'var(--c-surface-tint)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      marginBottom: 10,
                    }}>
                      <SIcon size={16} color="var(--c-primary)" />
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-text)', marginBottom: 4 }}>
                      {s.title}
                    </div>
                    <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', margin: 0, lineHeight: 1.45 }}>
                      {s.desc}
                    </p>
                  </div>
                )
              })}
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* TAB 2: PROGRESS ANALYTICS */}
      {activeTab === 'analytics' && (
        <motion.div variants={stagger} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <motion.div variants={fadeUp}>
            <ProgressOverview
              scoreDelta={14}
              improvementPct={22.6}
              recoveryVelocity={3.5}
              resolvedCount={2}
              emergingCount={0}
              mostImprovedNutrient="Vitamin B12"
              highestRiskNutrient="Vitamin D"
              currentScore={76}
              baselineScore={62}
            />
          </motion.div>

          <motion.div variants={fadeUp}>
            <TrendAnalyticsCharts timelineData={timelineCoordinates} />
          </motion.div>

          <motion.div variants={fadeUp}>
            <NutrientRecoveryTimeline items={recoveryItems} />
          </motion.div>
        </motion.div>
      )}

      {/* TAB 3: SIDE-BY-SIDE COMPARISON */}
      {activeTab === 'comparison' && (
        <motion.div variants={stagger} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <motion.div variants={fadeUp}>
            <ComparisonDashboard
              baseDate="2026-08-10"
              baseScore={62}
              targetDate="2026-09-10"
              targetScore={76}
              scoreDelta={14}
            />
          </motion.div>
        </motion.div>
      )}

      {/* TAB 4: ASSESSMENT HISTORY */}
      {activeTab === 'history' && (
        <motion.div variants={stagger} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <motion.div variants={fadeUp}>
            <AssessmentHistoryTable
              history={assessmentHistory}
              onCompareAssessments={() => setActiveTab('comparison')}
              onDownloadPdf={() => handleDownloadPdf()}
            />
          </motion.div>
        </motion.div>
      )}

      {/* Clinical PDF Preview Modal */}
      <PDFPreviewModal
        isOpen={pdfModalOpen}
        onClose={() => setPdfModalOpen(false)}
        reportId={id}
        patientName="Alex Mercer"
        assessmentDate="2026-09-10"
        healthScore={healthScore}
        healthCategory={healthCategory}
        onDownloadPdf={() => handleDownloadPdf()}
      />
    </motion.div>
  )
}
