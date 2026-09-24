import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import ErrorBoundary from './components/common/ErrorBoundary'

// Lazy-loaded page components for optimal bundle splitting and performance
const LandingPage = lazy(() => import('./pages/LandingPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const AssessmentPage = lazy(() => import('./pages/AssessmentPage'))
const PredictionsPage = lazy(() => import('./pages/PredictionsPage'))
const ExplainabilityPage = lazy(() => import('./pages/ExplainabilityPage'))
const RecommendationsPage = lazy(() => import('./pages/RecommendationsPage'))
const ReportsPage = lazy(() => import('./pages/ReportsPage'))
const PatientRecordsPage = lazy(() => import('./pages/PatientRecordsPage'))
const NutrientNetworkPage = lazy(() => import('./pages/NutrientNetworkPage'))
const NutritionIntelligencePage = lazy(() => import('./pages/NutritionIntelligencePage'))
const OutcomeCenter = lazy(() => import('./pages/outcomes/OutcomeCenter'))
const MonitoringDashboardPage = lazy(() => import('./pages/governance/MonitoringDashboardPage'))
const PersonalizedDashboardPage = lazy(() => import('./pages/personalization/PersonalizedDashboardPage'))
const RecommendationCenterPage = lazy(() => import('./pages/personalization/RecommendationCenterPage'))
const MealPlannerPage = lazy(() => import('./pages/personalization/MealPlannerPage'))
const ForecastDashboardPage = lazy(() => import('./pages/personalization/ForecastDashboardPage'))
const InterventionComparisonPage = lazy(() => import('./pages/personalization/InterventionComparisonPage'))
const ClinicalCopilotPage = lazy(() => import('./pages/copilot/ClinicalCopilotPage'))

function RouteLoadingFallback() {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[60vh] gap-4"
      role="status"
      aria-label="Loading clinical module"
    >
      <div className="relative flex items-center justify-center">
        <div className="w-12 h-12 rounded-full border-4 border-emerald-500/20 border-t-emerald-600 animate-spin" />
        <div className="absolute w-5 h-5 rounded-full bg-emerald-50 dark:bg-emerald-950/40" />
      </div>
      <div className="text-center">
        <p className="text-sm font-semibold text-slate-700 dark:text-slate-200 tracking-wide">
          Loading Clinical Module...
        </p>
        <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
          Initializing high-assurance intelligence workspace
        </p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<RouteLoadingFallback />}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route element={<AppShell />}>
            <Route path="/copilot" element={<ClinicalCopilotPage />} />
            <Route path="/copilot/:assessmentId" element={<ClinicalCopilotPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/dashboard/:assessmentId" element={<DashboardPage />} />
            <Route path="/assessment" element={<AssessmentPage />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/predictions/:assessmentId" element={<PredictionsPage />} />
            <Route path="/explainability" element={<ExplainabilityPage />} />
            <Route path="/explainability/:assessmentId" element={<ExplainabilityPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/recommendations/:assessmentId" element={<RecommendationsPage />} />
            <Route path="/personalization" element={<PersonalizedDashboardPage />} />
            <Route path="/personalization/:assessmentId" element={<PersonalizedDashboardPage />} />
            <Route path="/recommendation-center" element={<RecommendationCenterPage />} />
            <Route path="/recommendation-center/:assessmentId" element={<RecommendationCenterPage />} />
            <Route path="/meal-planner" element={<MealPlannerPage />} />
            <Route path="/meal-planner/:assessmentId" element={<MealPlannerPage />} />
            <Route path="/forecasting" element={<ForecastDashboardPage />} />
            <Route path="/forecasting/:assessmentId" element={<ForecastDashboardPage />} />
            <Route path="/intervention-comparison" element={<InterventionComparisonPage />} />
            <Route path="/intervention-comparison/:assessmentId" element={<InterventionComparisonPage />} />
            <Route path="/intelligence" element={<NutritionIntelligencePage />} />
            <Route path="/intelligence/:assessmentId" element={<NutritionIntelligencePage />} />
            <Route path="/outcomes" element={<OutcomeCenter />} />
            <Route path="/outcomes/:assessmentId" element={<OutcomeCenter />} />
            <Route path="/governance" element={<MonitoringDashboardPage />} />
            <Route path="/governance/:assessmentId" element={<MonitoringDashboardPage />} />
            <Route path="/monitoring" element={<MonitoringDashboardPage />} />
            <Route path="/monitoring/:assessmentId" element={<MonitoringDashboardPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/reports/:assessmentId" element={<ReportsPage />} />
            <Route path="/network" element={<NutrientNetworkPage />} />
            <Route path="/network/:assessmentId" element={<NutrientNetworkPage />} />
            <Route path="/patients" element={<PatientRecordsPage />} />
            <Route path="/patients/:patientId" element={<PatientRecordsPage />} />
            <Route path="/profile" element={<Navigate to="/patients" replace />} />
          </Route>
          {/* Catch-all fallback to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}

