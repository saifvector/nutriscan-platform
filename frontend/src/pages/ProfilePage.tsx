import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import { User, Mail, Calendar, ClipboardList, Settings, Bell, Shield, LogOut, ExternalLink } from 'lucide-react'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}
const stagger: Variants = { visible: { transition: { staggerChildren: 0.06 } } }

interface AssessmentItem {
  id: string
  date: string
  score: number
  risk: string
  nutrients_flagged: number
  title?: string
}

export default function ProfilePage() {
  const [assessments, setAssessments] = useState<AssessmentItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true)
        const res = await fetch('/api/v1/reports/history')
        if (res.ok) {
          const items = await res.json()
          if (Array.isArray(items) && items.length > 0) {
            setAssessments(items.map((it: any) => ({
              id: it.assessment_id || it.id,
              date: it.generated_at ? it.generated_at.split('T')[0] : 'Recent',
              score: it.overall_health_score ?? 70,
              risk: (it.health_score_category || 'MODERATE').replace('_RISK', ''),
              nutrients_flagged: it.report_payload?.flagged_nutrients ?? 0,
              title: it.report_title || 'Nutritional Screening Assessment',
            })))
            return
          }
        }

        // Fallback to active local assessment if available
        const activeId = localStorage.getItem('nutriscan_assessment_id')
        const rawAssessment = localStorage.getItem('nutriscan_active_assessment')
        if (activeId || rawAssessment) {
          const parsed = rawAssessment ? JSON.parse(rawAssessment) : null
          setAssessments([{
            id: activeId || 'active-assessment',
            date: 'Today',
            score: 74,
            risk: 'MODERATE',
            nutrients_flagged: 2,
            title: parsed?.dietary_pattern ? `${parsed.dietary_pattern} Intake Assessment` : 'Active Patient Assessment'
          }])
        }
      } catch (err) {
        console.error('Failed to load assessment history in profile:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchHistory()
  }, [])

  return (
    <motion.div initial="hidden" animate="visible" variants={stagger} style={{ maxWidth: 800, margin: '0 auto' }}>
      <motion.div variants={fadeUp} style={{ marginBottom: 32 }}>
        <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 6 }}>Profile</h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)' }}>Manage your account and view assessment history.</p>
      </motion.div>

      <motion.div variants={fadeUp} className="card" style={{ padding: 28, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 24 }}>
        <div style={{
          width: 72, height: 72, borderRadius: 20, background: 'var(--c-primary)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '1.5rem', fontWeight: 800, color: 'white', fontFamily: 'var(--font-heading)',
        }}>JD</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 4 }}>Dr. John Doe</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, color: 'var(--c-muted)', fontSize: '0.8125rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Mail size={13} /> john.doe@clinical-nutriscan.ai</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Calendar size={13} /> Joined Sept 2026</span>
          </div>
        </div>
        <button className="btn-ghost" style={{ padding: '8px 16px', fontSize: '0.75rem' }}>Edit Profile</button>
      </motion.div>

      <motion.div variants={fadeUp} className="card" style={{ padding: 24, marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 18 }}>
          <ClipboardList size={16} color="var(--c-primary)" />
          <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>Assessment History</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {assessments.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '32px 16px',
              color: 'var(--c-muted)',
              fontSize: '0.8125rem'
            }}>
              No previous clinical assessments found. Complete a nutritional assessment to view your historical recovery timeline.
              <div style={{ marginTop: 14 }}>
                <Link to="/assessment" className="btn-primary" style={{ padding: '8px 16px', fontSize: '0.75rem', textDecoration: 'none' }}>
                  Take Assessment
                </Link>
              </div>
            </div>
          ) : (
            assessments.map(a => (
              <div key={a.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '14px 16px', borderRadius: 10, background: 'var(--c-surface-alt)', border: '1px solid var(--c-border-light)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 10,
                    background: a.risk === 'HIGH' ? 'var(--c-danger-bg)' : 'var(--c-warning-bg)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: 'var(--font-heading)', fontSize: '0.875rem', fontWeight: 800,
                    color: a.risk === 'HIGH' ? 'var(--c-danger-text)' : 'var(--c-warning-text)',
                  }}>{a.score}</div>
                  <div>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)' }}>{a.title || 'Assessment'} · {a.date}</div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{a.nutrients_flagged} nutrients flagged · {a.risk} risk</div>
                  </div>
                </div>
                <Link to={`/dashboard/${a.id}`} className="btn-ghost" style={{ padding: '6px 14px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 4 }}>
                  View Details <ExternalLink size={12} />
                </Link>
              </div>
            ))
          )}
        </div>
      </motion.div>

      <motion.div variants={fadeUp} className="card" style={{ padding: 24 }}>
        <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', marginBottom: 18 }}>Settings</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {[
            { label: 'Notification Preferences', desc: 'Manage email and push notifications', icon: Bell },
            { label: 'Privacy & Security', desc: 'Data sharing, export, and deletion', icon: Shield },
            { label: 'Application Settings', desc: 'Theme, language, and display preferences', icon: Settings },
            { label: 'Sign Out', desc: 'End your current session', icon: LogOut, danger: true },
          ].map(item => (
            <div key={item.label} style={{
              display: 'flex', alignItems: 'center', gap: 14,
              padding: '14px 12px', borderRadius: 8, cursor: 'pointer', transition: 'background 0.15s',
            }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--c-card-hover)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
            >
              <div style={{
                width: 36, height: 36, borderRadius: 10,
                background: item.danger ? 'var(--c-danger-bg)' : 'var(--c-bar-track)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <item.icon size={16} color={item.danger ? 'var(--c-danger)' : 'var(--c-muted)'} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: item.danger ? 'var(--c-danger)' : 'var(--c-secondary)' }}>{item.label}</div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}
