import { useState, useEffect, useCallback } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import {
  Users,
  User,
  Search,
  Calendar,
  ClipboardList,
  TrendingUp,
  Activity,
  AlertTriangle,
  ArrowRight,
  ChevronRight,
  ArrowLeft,
  ExternalLink,
  PlusCircle,
  RefreshCw,
  Trash2,
  Loader2,
  Heart,
  Pill,
  Utensils,
  CheckCircle2,
  FileText
} from 'lucide-react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts'
import api from '../lib/api'
import { sessionManager } from '../lib/sessionManager'
import { patientApi, type PatientSummary, type PatientTimelineData } from '../api/patientApi'
import { PatientCard } from '../components/patients/PatientCard'
import { DeletePatientModal } from '../components/patients/DeletePatientModal'
import { DeleteAllPatientsModal } from '../components/patients/DeleteAllPatientsModal'

const fadeIn: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: 'easeOut' } },
}

const staggerContainer: Variants = {
  visible: { transition: { staggerChildren: 0.05 } },
}

export default function PatientRecordsPage() {
  const { patientId } = useParams<{ patientId?: string }>()
  const navigate = useNavigate()

  const [patients, setPatients] = useState<PatientSummary[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(patientId || null)
  const [timelineData, setTimelineData] = useState<PatientTimelineData | null>(null)
  const [timelineLoading, setTimelineLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Deletion modal and feedback states
  const [patientToDelete, setPatientToDelete] = useState<PatientSummary | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteAllModal, setShowDeleteAllModal] = useState(false)
  const [isDeletingAll, setIsDeletingAll] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  // Auto-dismiss toast notification
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4000)
      return () => clearTimeout(timer)
    }
  }, [toast])

  // Fetch patient roster with optional search query
  const loadPatients = useCallback(async (query = '') => {
    try {
      setLoading(true)
      setError(null)
      const data = await patientApi.getPatients(query)
      setPatients(data)
    } catch (err: any) {
      console.error('Failed to load patient records:', err)
      setError('Unable to load patient records from clinical database.')
    } finally {
      setLoading(false)
    }
  }, [])

  // Fetch longitudinal timeline when patient is selected
  const loadTimeline = useCallback(async (id: string) => {
    try {
      setTimelineLoading(true)
      const data = await patientApi.getPatientTimeline(id)
      setTimelineData(data)
    } catch (err: any) {
      console.error('Failed to load patient clinical timeline:', err)
    } finally {
      setTimelineLoading(false)
    }
  }, [])

  const handleDeleteRequest = (p: PatientSummary) => {
    setPatientToDelete(p)
  }

  const handleConfirmDelete = async () => {
    if (!patientToDelete) return
    setIsDeleting(true)
    try {
      const res = await patientApi.deletePatient(patientToDelete.id)
      if (res.success) {
        // 1. Immediately remove patient from UI state
        setPatients((prev) => prev.filter((p) => p.id !== patientToDelete.id))

        // 2. If the deleted patient was currently open in timeline view, close it
        if (selectedPatientId === patientToDelete.id) {
          setSelectedPatientId(null)
          setTimelineData(null)
          navigate('/patients')
        }

        // 3. Clear active session if it points to an assessment from this patient
        const activeSession = sessionManager.getActiveSession()
        if (
          activeSession?.active_assessment_id &&
          patientToDelete.latest_assessment_id === activeSession.active_assessment_id
        ) {
          sessionManager.clearActiveSession()
        }

        // 4. Show success toast
        setToast({ type: 'success', message: 'Patient deleted successfully' })
        setPatientToDelete(null)
      } else {
        setToast({ type: 'error', message: 'Failed to delete patient' })
      }
    } catch (err: any) {
      console.error('Failed to delete patient:', err)
      setToast({ type: 'error', message: 'Failed to delete patient' })
    } finally {
      setIsDeleting(false)
    }
  }

  // Handle global destructive deletion of all patient records
  const handleConfirmDeleteAll = async () => {
    try {
      setIsDeletingAll(true)
      const res = await patientApi.deleteAllPatients()
      if (res.success) {
        // 1. Reset active session and stored assessments
        sessionManager.clearAllStoredAssessments()

        // 2. Clear selected patient and timeline state
        setSelectedPatientId(null)
        setTimelineData(null)

        // 3. Clear patient roster
        setPatients([])

        // 4. Close confirmation modal
        setShowDeleteAllModal(false)

        // 5. Navigate to patient registry root (empty state)
        navigate('/patients', { replace: true })

        // 6. Show success toast notification
        setToast({
          type: 'success',
          message: 'All patient records deleted successfully'
        })
      } else {
        setToast({
          type: 'error',
          message: res.message || 'Failed to delete all patient records'
        })
      }
    } catch (err: any) {
      console.error('Failed to delete all patient records:', err)
      setToast({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to delete all patient records'
      })
    } finally {
      setIsDeletingAll(false)
    }
  }

  // Initial load
  useEffect(() => {
    loadPatients(searchQuery)
  }, [loadPatients, searchQuery])

  // Sync selected patient from route parameter
  useEffect(() => {
    if (patientId) {
      setSelectedPatientId(patientId)
      loadTimeline(patientId)
    } else {
      setSelectedPatientId(null)
      setTimelineData(null)
    }
  }, [patientId, loadTimeline])

  const handleSelectPatient = (pId: string) => {
    setSelectedPatientId(pId)
    navigate(`/patients/${pId}`)
  }

  const handleBackToRoster = () => {
    setSelectedPatientId(null)
    setTimelineData(null)
    navigate('/patients')
  }

  const getRiskColor = (level?: string | null) => {
    const l = (level || '').toUpperCase()
    if (l.includes('HIGH') || l.includes('CRITICAL')) return { bg: 'rgba(239, 68, 68, 0.14)', text: '#EF4444', border: 'rgba(239, 68, 68, 0.3)' }
    if (l.includes('MODERATE')) return { bg: 'rgba(245, 158, 11, 0.14)', text: '#F59E0B', border: 'rgba(245, 158, 11, 0.3)' }
    return { bg: 'rgba(16, 185, 129, 0.14)', text: '#10B981', border: 'rgba(16, 185, 129, 0.3)' }
  }

  const getTrajectoryColor = (traj?: string) => {
    if (traj === 'IMPROVING' || traj === 'OPTIMAL') return '#10B981'
    if (traj === 'STABLE') return '#0D9488'
    return '#EF4444'
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 60 }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: 'rgba(13, 148, 136, 0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--c-primary)'
            }}>
              <Users size={18} />
            </div>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
              Patient Records & Clinical History
            </h1>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)' }}>
            Longitudinal patient registry, screening trajectories, deficiency recurrence, and treatment histories.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Link
            to="/assessment"
            className="btn-primary"
            style={{
              padding: '10px 18px', fontSize: '0.8125rem', fontWeight: 600,
              display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none'
            }}
          >
            <PlusCircle size={16} /> New Assessment
          </Link>
          <button
            onClick={() => {
              if (selectedPatientId) loadTimeline(selectedPatientId)
              loadPatients(searchQuery)
            }}
            className="btn-ghost"
            style={{ padding: '10px 14px', fontSize: '0.8125rem' }}
            title="Refresh database records"
          >
            <RefreshCw size={15} />
          </button>
          <button
            onClick={() => setShowDeleteAllModal(true)}
            disabled={isDeletingAll || loading || patients.length === 0}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 16px',
              fontSize: '0.8125rem',
              fontWeight: 600,
              color: '#ffffff',
              background: isDeletingAll ? '#991b1b' : '#ef4444',
              border: '1px solid rgba(239, 68, 68, 0.6)',
              borderRadius: 8,
              cursor: (isDeletingAll || loading || patients.length === 0) ? 'not-allowed' : 'pointer',
              opacity: (isDeletingAll || loading || patients.length === 0) ? 0.6 : 1,
              boxShadow: '0 2px 8px rgba(239, 68, 68, 0.25)',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              if (!isDeletingAll && !loading && patients.length > 0) e.currentTarget.style.background = '#dc2626'
            }}
            onMouseLeave={(e) => {
              if (!isDeletingAll && !loading && patients.length > 0) e.currentTarget.style.background = '#ef4444'
            }}
            title="Delete all patients and clinical history"
          >
            {isDeletingAll ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                <span>Deleting...</span>
              </>
            ) : (
              <>
                <Trash2 size={15} />
                <span>Delete All</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          padding: '14px 18px', borderRadius: 10,
          background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#EF4444', fontSize: '0.875rem', marginBottom: 20
        }}>
          {error}
        </div>
      )}

      {/* VIEW 1: SINGLE PATIENT LONGITUDINAL TIMELINE */}
      {selectedPatientId && (
        <motion.div initial="hidden" animate="visible" variants={fadeIn}>
          <button
            onClick={handleBackToRoster}
            className="btn-ghost"
            style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: '0.8125rem', padding: '6px 12px' }}
          >
            <ArrowLeft size={14} /> Back to Patient Registry
          </button>

          {timelineLoading && !timelineData ? (
            <div className="card" style={{ padding: 48, textAlign: 'center', color: 'var(--c-muted)' }}>
              Loading clinical timeline from persistent records...
            </div>
          ) : timelineData ? (
            <div>
              {/* Patient Profile Header Card */}
              <div className="card" style={{ padding: 24, marginBottom: 24, border: '1px solid var(--c-border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
                    <div style={{
                      width: 56, height: 56, borderRadius: 16,
                      background: 'linear-gradient(135deg, var(--c-primary), #0f766e)',
                      color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '1.375rem', fontWeight: 800, fontFamily: 'var(--font-heading)'
                    }}>
                      {timelineData.patient.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <h2 style={{ fontSize: '1.375rem', fontWeight: 800, color: 'var(--c-secondary)', fontFamily: 'var(--font-heading)' }}>
                          {timelineData.patient.name}
                        </h2>
                        <span style={{
                          fontSize: '0.6875rem', fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                          background: 'var(--c-surface-tint)', color: 'var(--c-primary)', border: '1px solid var(--c-border)'
                        }}>
                          ID: {timelineData.patient.id.slice(0, 8).toUpperCase()}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: 16, marginTop: 6, color: 'var(--c-muted)', fontSize: '0.8125rem', flexWrap: 'wrap' }}>
                        <span>Age: <strong style={{ color: 'var(--c-secondary)' }}>{timelineData.patient.age ?? '—'} yrs</strong></span>
                        <span>Gender: <strong style={{ color: 'var(--c-secondary)' }}>{timelineData.patient.gender ?? '—'}</strong></span>
                        <span>Height: <strong style={{ color: 'var(--c-secondary)' }}>{timelineData.patient.height_cm ? `${timelineData.patient.height_cm} cm` : '—'}</strong></span>
                        <span>Weight: <strong style={{ color: 'var(--c-secondary)' }}>{timelineData.patient.weight_kg ? `${timelineData.patient.weight_kg} kg` : '—'}</strong></span>
                        <span>BMI: <strong style={{ color: 'var(--c-primary)' }}>{timelineData.patient.bmi ?? '—'}</strong></span>
                        <span>Diet: <strong style={{ color: 'var(--c-secondary)' }}>{timelineData.patient.dietary_pattern ?? '—'}</strong></span>
                      </div>
                    </div>
                  </div>

                  <Link
                    to={`/assessment?patient_id=${timelineData.patient.id}&patient_name=${encodeURIComponent(timelineData.patient.name)}`}
                    className="btn-primary"
                    style={{
                      padding: '10px 18px', fontSize: '0.8125rem', fontWeight: 600,
                      display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none'
                    }}
                  >
                    <PlusCircle size={15} /> Start Re-Assessment
                  </Link>
                </div>
              </div>

              {/* Longitudinal Metrics Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 24 }}>
                <div className="card" style={{ padding: 20 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <ClipboardList size={14} color="var(--c-primary)" /> Total Clinical Screenings
                  </div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--c-secondary)' }}>
                    {timelineData.summary.total_screenings}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 4 }}>
                    Registered in database
                  </div>
                </div>

                <div className="card" style={{ padding: 20 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <AlertTriangle size={14} color="#F59E0B" /> Current Risk Score
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                    <span style={{ fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--c-secondary)' }}>
                      {timelineData.summary.latest_risk_score ?? '—'}
                    </span>
                    <span style={{
                      fontSize: '0.6875rem', fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                      ...getRiskColor(timelineData.summary.latest_risk_level)
                    }}>
                      {timelineData.summary.latest_risk_level}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 4 }}>
                    Latest multi-nutrient risk tier
                  </div>
                </div>

                <div className="card" style={{ padding: 20 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Heart size={14} color="#EF4444" /> Active Deficiencies
                  </div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--c-secondary)' }}>
                    {timelineData.summary.active_deficiencies_count}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 4 }}>
                    Nutrients currently flagged
                  </div>
                </div>

                <div className="card" style={{ padding: 20 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <TrendingUp size={14} color={getTrajectoryColor(timelineData.summary.trajectory)} /> Clinical Trajectory
                  </div>
                  <div style={{
                    fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)',
                    color: getTrajectoryColor(timelineData.summary.trajectory)
                  }}>
                    {timelineData.summary.trajectory}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginTop: 4 }}>
                    Longitudinal health progression
                  </div>
                </div>
              </div>

              {/* Longitudinal Risk Progression Chart */}
              {timelineData.trends.dates.length > 1 && (
                <div className="card" style={{ padding: 24, marginBottom: 28 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                    <div>
                      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--c-secondary)', fontFamily: 'var(--font-heading)' }}>
                        Longitudinal Deficiency Risk Progression
                      </h3>
                      <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                        Overall deficiency risk score tracked over consecutive clinical screening dates.
                      </p>
                    </div>
                  </div>
                  <div style={{ width: '100%', height: 220 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={timelineData.trends.dates.map((d, i) => ({
                          date: d,
                          score: timelineData.trends.risk_scores[i]
                        }))}
                        margin={{ top: 10, right: 20, left: -20, bottom: 0 }}
                      >
                        <defs>
                          <linearGradient id="patientRiskGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--c-primary)" stopOpacity={0.4} />
                            <stop offset="95%" stopColor="var(--c-primary)" stopOpacity={0.0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                        <XAxis dataKey="date" stroke="var(--c-muted)" fontSize={11} tickLine={false} />
                        <YAxis stroke="var(--c-muted)" fontSize={11} domain={[0, 100]} tickLine={false} />
                        <Tooltip
                          contentStyle={{
                            background: 'var(--c-card)',
                            border: '1px solid var(--c-border)',
                            borderRadius: 8,
                            fontSize: '0.75rem'
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="score"
                          name="Risk Score"
                          stroke="var(--c-primary)"
                          strokeWidth={2.5}
                          fillOpacity={1}
                          fill="url(#patientRiskGrad)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Chronological Assessment Timeline */}
              <div>
                <h3 style={{ fontSize: '1.125rem', fontWeight: 800, color: 'var(--c-secondary)', marginBottom: 16, fontFamily: 'var(--font-heading)' }}>
                  Chronological Assessment Timeline ({timelineData.timeline.length})
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  {timelineData.timeline.map((entry, idx) => {
                    const rStyle = getRiskColor(entry.risk_level)
                    return (
                      <div
                        key={entry.assessment_id}
                        className="card"
                        style={{
                          padding: 22, border: '1px solid var(--c-border)',
                          position: 'relative'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <div style={{
                              width: 36, height: 36, borderRadius: 10,
                              background: rStyle.bg, border: `1px solid ${rStyle.border}`,
                              color: rStyle.text, display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: '0.875rem'
                            }}>
                              {idx + 1}
                            </div>
                            <div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                                  Screening Session · {entry.formatted_date}
                                </span>
                                <span style={{
                                  fontSize: '0.6875rem', fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                                  background: rStyle.bg, color: rStyle.text, border: `1px solid ${rStyle.border}`
                                }}>
                                  {entry.risk_level} RISK ({entry.risk_score})
                                </span>
                              </div>
                              <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                                ID: {entry.assessment_id}
                              </span>
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: 10 }}>
                            <Link
                              to={`/dashboard/${entry.assessment_id}`}
                              className="btn-ghost"
                              onClick={() => {
                                sessionManager.setActiveSession(entry.assessment_id, entry.date, 'completed', timelineData.patient.name)
                              }}
                              style={{ padding: '6px 14px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6, textDecoration: 'none' }}
                            >
                              <Activity size={13} /> View Dashboard
                            </Link>
                            <Link
                              to={`/reports/${entry.assessment_id}`}
                              className="btn-ghost"
                              onClick={() => {
                                sessionManager.setActiveSession(entry.assessment_id, entry.date, 'completed', timelineData.patient.name)
                              }}
                              style={{ padding: '6px 14px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6, textDecoration: 'none' }}
                            >
                              <FileText size={13} /> Clinical Report
                            </Link>
                          </div>
                        </div>

                        {/* Deficiencies Breakdown */}
                        <div style={{ marginBottom: 16 }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-muted)', marginBottom: 8 }}>
                            Identified Deficiencies & Probabilities:
                          </div>
                          {entry.flagged_deficiencies.length === 0 ? (
                            <div style={{ fontSize: '0.8125rem', color: '#10B981', display: 'flex', alignItems: 'center', gap: 6 }}>
                              <CheckCircle2 size={15} /> All 11 target nutrients within optimal physiological range.
                            </div>
                          ) : (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 8 }}>
                              {entry.flagged_deficiencies.map(d => {
                                const dColor = getRiskColor(d.risk_level)
                                return (
                                  <div
                                    key={d.nutrient}
                                    style={{
                                      padding: '8px 12px', borderRadius: 8,
                                      background: 'var(--c-surface-alt)', border: '1px solid var(--c-border-light)',
                                      display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                                    }}
                                  >
                                    <div>
                                      <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>
                                        {d.nutrient}
                                      </div>
                                      <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
                                        {Math.round(d.probability * 100)}% probability
                                      </div>
                                    </div>
                                    <span style={{
                                      fontSize: '0.625rem', fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                                      background: dColor.bg, color: dColor.text
                                    }}>
                                      {d.risk_level}
                                    </span>
                                  </div>
                                )
                              })}
                            </div>
                          )}
                        </div>

                        {/* Prescribed Treatments / Interventions */}
                        {entry.treatments.length > 0 && (
                          <div style={{ borderTop: '1px solid var(--c-border-light)', paddingTop: 12 }}>
                            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-muted)', marginBottom: 8 }}>
                              Prescribed Interventions & Targeted Diet:
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                              {entry.treatments.map((t, tIdx) => (
                                <div
                                  key={tIdx}
                                  style={{
                                    fontSize: '0.75rem', padding: '4px 10px', borderRadius: 6,
                                    background: t.type === 'SUPPLEMENT' ? 'rgba(13, 148, 136, 0.12)' : 'var(--c-surface-tint)',
                                    border: '1px solid var(--c-border-light)',
                                    color: 'var(--c-secondary)', display: 'flex', alignItems: 'center', gap: 6
                                  }}
                                >
                                  {t.type === 'SUPPLEMENT' ? <Pill size={12} color="var(--c-primary)" /> : <Utensils size={12} color="var(--c-primary)" />}
                                  <strong>{t.title}</strong>
                                  <span style={{ color: 'var(--c-muted)' }}>({t.reason})</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--c-muted)' }}>
              No clinical history found for patient ID {selectedPatientId}.
            </div>
          )}
        </motion.div>
      )}

      {/* VIEW 2: PATIENT REGISTRY ROSTER */}
      {!selectedPatientId && (
        <motion.div initial="hidden" animate="visible" variants={staggerContainer}>
          {/* Search bar */}
          <div className="card" style={{ padding: 16, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 12 }}>
            <Search size={18} color="var(--c-muted)" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search patient registry by name or record ID..."
              style={{
                flex: 1, background: 'transparent', border: 'none',
                outline: 'none', fontSize: '0.875rem', color: 'var(--c-secondary)',
                fontFamily: 'var(--font-body)'
              }}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="btn-ghost"
                style={{ padding: '4px 8px', fontSize: '0.75rem' }}
              >
                Clear
              </button>
            )}
          </div>

          {loading ? (
            <div className="card" style={{ padding: 48, textAlign: 'center', color: 'var(--c-muted)' }}>
              Querying patient records from persistence database...
            </div>
          ) : patients.length === 0 ? (
            <div className="card" style={{ padding: 48, textAlign: 'center' }}>
              <Users size={36} color="var(--c-muted)" style={{ margin: '0 auto 12px' }} />
              <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 6 }}>
                {searchQuery ? 'No Patient Records Found' : 'No Patient Records'}
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', maxWidth: 440, margin: '0 auto 20px' }}>
                {searchQuery
                  ? `No patient matches "${searchQuery}". Try a different search term.`
                  : 'Create a new assessment to begin building your patient registry.'}
              </p>
              <Link
                to="/assessment"
                className="btn-primary"
                style={{
                  padding: '8px 20px',
                  fontSize: '0.8125rem',
                  textDecoration: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <PlusCircle size={15} />
                <span>New Assessment</span>
              </Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {patients.map((p) => (
                <PatientCard
                  key={p.id}
                  patient={p}
                  onSelect={handleSelectPatient}
                  onDeleteRequest={handleDeleteRequest}
                  isDeleting={isDeleting && patientToDelete?.id === p.id}
                  variants={fadeIn}
                />
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* Permanent Single Patient Deletion Confirmation Modal */}
      <DeletePatientModal
        isOpen={!!patientToDelete}
        patientName={patientToDelete?.name || ''}
        patientId={patientToDelete?.id || ''}
        assessmentCount={patientToDelete?.assessment_count}
        isDeleting={isDeleting}
        onConfirm={handleConfirmDelete}
        onCancel={() => !isDeleting && setPatientToDelete(null)}
      />

      {/* Enterprise Global Delete All Confirmation Modal */}
      <DeleteAllPatientsModal
        isOpen={showDeleteAllModal}
        patientCount={patients.length}
        isDeleting={isDeletingAll}
        onConfirm={handleConfirmDeleteAll}
        onCancel={() => !isDeletingAll && setShowDeleteAllModal(false)}
      />

      {/* Toast Notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'fixed',
              bottom: 28,
              right: 28,
              zIndex: 99999,
              padding: '12px 20px',
              borderRadius: 10,
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
              background: toast.type === 'success' ? '#064e3b' : '#7f1d1d',
              border: `1px solid ${toast.type === 'success' ? '#10b981' : '#ef4444'}`,
              color: '#f8fafc',
              fontSize: '0.875rem',
              fontWeight: 600,
            }}
          >
            {toast.type === 'success' ? (
              <CheckCircle2 size={18} color="#34d399" />
            ) : (
              <AlertTriangle size={18} color="#f87171" />
            )}
            <span>{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
