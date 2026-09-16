import { motion } from 'framer-motion'
import { Calendar, Download, Eye, GitCompare, CheckCircle2, FileText } from 'lucide-react'

export interface HistoryEntry {
  id: string
  assessment_id: string
  assessment_number: number
  date: string
  version: string
  health_score: number
  health_category: string
  risk_distribution: { [key: string]: number }
  deficiency_count: number
  status: string
  pdf_file_url?: string
}

interface AssessmentHistoryTableProps {
  history: HistoryEntry[]
  onSelectAssessment?: (assessmentId: string) => void
  onCompareAssessments?: (baseId: string, targetId: string) => void
  onDownloadPdf?: (reportId: string) => void
}

export default function AssessmentHistoryTable({
  history,
  onSelectAssessment,
  onCompareAssessments,
  onDownloadPdf,
}: AssessmentHistoryTableProps) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'var(--c-success)'
    if (score >= 75) return 'var(--c-primary)'
    if (score >= 60) return 'var(--c-warning)'
    if (score >= 40) return '#F97316'
    return 'var(--c-danger)'
  }

  return (
    <div style={{
      background: 'var(--c-card)',
      border: '1px solid var(--c-border)',
      borderRadius: 20,
      padding: '24px 28px',
      boxShadow: 'var(--c-shadow-sm)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 20,
      }}>
        <div>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-text)', margin: 0 }}>
            Longitudinal Assessment History
          </h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', margin: '4px 0 0' }}>
            Permanent chronological archive of all diagnostic screening sessions with version tracking.
          </p>
        </div>

        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-muted)' }}>
          Total Screenings: <b style={{ color: 'var(--c-text)' }}>{history.length}</b>
        </span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--c-border-light)' }}>
              <th style={{ padding: '12px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Session</th>
              <th style={{ padding: '12px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Date</th>
              <th style={{ padding: '12px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Health Score</th>
              <th style={{ padding: '12px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Deficiencies</th>
              <th style={{ padding: '12px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Risk Breakdown</th>
              <th style={{ padding: '12px 16px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry, idx) => {
              const scoreColor = getScoreColor(entry.health_score)
              const highCount = entry.risk_distribution?.HIGH || 0
              const modCount = entry.risk_distribution?.MODERATE || 0
              const lowCount = entry.risk_distribution?.LOW || 0

              return (
                <motion.tr
                  key={entry.id || idx}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2, delay: idx * 0.04 }}
                  style={{
                    borderBottom: '1px solid var(--c-border-light)',
                    transition: 'background 0.15s ease',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--c-surface-alt)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '16px', fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-text)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{
                        width: 24, height: 24, borderRadius: 6, background: 'var(--c-surface-tint)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.6875rem', fontWeight: 800, color: 'var(--c-primary)',
                      }}>
                        #{entry.assessment_number}
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>{entry.version}</span>
                    </div>
                  </td>

                  <td style={{ padding: '16px', fontSize: '0.8125rem', color: 'var(--c-text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Calendar size={14} color="var(--c-muted)" />
                      {entry.date}
                    </div>
                  </td>

                  <td style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{
                        fontFamily: 'var(--font-heading)',
                        fontSize: '1rem',
                        fontWeight: 800,
                        color: scoreColor,
                      }}>
                        {entry.health_score}
                      </span>
                      <span style={{
                        fontSize: '0.6875rem',
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: 10,
                        background: 'var(--c-surface-alt)',
                        color: 'var(--c-text-secondary)',
                      }}>
                        {entry.health_category.replace('_', ' ')}
                      </span>
                    </div>
                  </td>

                  <td style={{ padding: '16px', fontSize: '0.8125rem' }}>
                    <span style={{
                      fontWeight: 600,
                      color: entry.deficiency_count > 0 ? '#F97316' : 'var(--c-success)',
                    }}>
                      {entry.deficiency_count > 0 ? `${entry.deficiency_count} detected` : 'None (optimal)'}
                    </span>
                  </td>

                  <td style={{ padding: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {highCount > 0 && (
                        <span style={{ fontSize: '0.6875rem', fontWeight: 700, padding: '2px 6px', borderRadius: 6, background: 'rgba(239, 68, 68, 0.12)', color: 'var(--c-danger)' }}>
                          {highCount} High
                        </span>
                      )}
                      {modCount > 0 && (
                        <span style={{ fontSize: '0.6875rem', fontWeight: 700, padding: '2px 6px', borderRadius: 6, background: 'rgba(245, 158, 11, 0.12)', color: 'var(--c-warning)' }}>
                          {modCount} Mod
                        </span>
                      )}
                      <span style={{ fontSize: '0.6875rem', fontWeight: 700, padding: '2px 6px', borderRadius: 6, background: 'rgba(34, 197, 94, 0.12)', color: 'var(--c-success)' }}>
                        {lowCount} Low
                      </span>
                    </div>
                  </td>

                  <td style={{ padding: '16px', textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: 6 }}>
                      {idx < history.length - 1 && onCompareAssessments && (
                        <button
                          onClick={() => onCompareAssessments(history[history.length - 1].assessment_id, entry.assessment_id)}
                          title="Compare with baseline"
                          style={{
                            display: 'inline-flex', alignItems: 'center', gap: 4,
                            padding: '6px 10px', borderRadius: 8,
                            background: 'var(--c-surface-tint)', border: '1px solid var(--c-border-light)',
                            fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
                            cursor: 'pointer',
                          }}
                        >
                          <GitCompare size={12} /> Compare
                        </button>
                      )}

                      {onDownloadPdf && (
                        <button
                          onClick={() => onDownloadPdf(entry.id)}
                          title="Download PDF"
                          style={{
                            display: 'inline-flex', alignItems: 'center', gap: 4,
                            padding: '6px 10px', borderRadius: 8,
                            background: 'transparent', border: '1px solid var(--c-border-light)',
                            fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-text-secondary)',
                            cursor: 'pointer',
                          }}
                        >
                          <Download size={12} /> PDF
                        </button>
                      )}
                    </div>
                  </td>
                </motion.tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
