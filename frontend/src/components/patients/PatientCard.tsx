import React from 'react'
import { motion, type Variants } from 'framer-motion'
import { ChevronRight, Trash2, Loader2 } from 'lucide-react'
import type { PatientSummary } from '../../api/patientApi'

interface PatientCardProps {
  patient: PatientSummary
  onSelect: (patientId: string) => void
  onDeleteRequest: (patient: PatientSummary) => void
  isDeleting?: boolean
  variants?: Variants
}

const getRiskColor = (risk: string | null) => {
  switch (risk?.toUpperCase()) {
    case 'HIGH':
      return { bg: 'rgba(239, 68, 68, 0.15)', text: '#ef4444', border: 'rgba(239, 68, 68, 0.3)' }
    case 'MODERATE':
      return { bg: 'rgba(245, 158, 11, 0.15)', text: '#f59e0b', border: 'rgba(245, 158, 11, 0.3)' }
    case 'LOW':
      return { bg: 'rgba(16, 185, 129, 0.15)', text: '#10b981', border: 'rgba(16, 185, 129, 0.3)' }
    default:
      return { bg: 'rgba(148, 163, 184, 0.1)', text: '#94a3b8', border: 'rgba(148, 163, 184, 0.2)' }
  }
}

export const PatientCard: React.FC<PatientCardProps> = ({
  patient: p,
  onSelect,
  onDeleteRequest,
  isDeleting = false,
  variants,
}) => {
  const rStyle = getRiskColor(p.latest_risk_level)

  return (
    <motion.div
      variants={variants}
      className="card"
      onClick={() => onSelect(p.id)}
      style={{
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: 'pointer',
        transition: 'all 0.15s ease-in-out',
        border: '1px solid var(--c-border-light)',
        position: 'relative',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--c-primary)'
        e.currentTarget.style.background = 'var(--c-card-hover)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--c-border-light)'
        e.currentTarget.style.background = 'var(--c-card)'
      }}
    >
      {/* Patient Avatar & Demographics */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'linear-gradient(135deg, var(--c-primary), #0f766e)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: '1.125rem',
            fontFamily: 'var(--font-heading)',
            flexShrink: 0,
            boxShadow: '0 4px 12px rgba(20, 184, 166, 0.25)',
          }}
        >
          {p.name.charAt(0).toUpperCase()}
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 2 }}>
            <span style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
              {p.name}
            </span>
            <span
              style={{
                fontSize: '0.625rem',
                padding: '2px 6px',
                borderRadius: 4,
                background: 'var(--c-surface-tint)',
                color: 'var(--c-primary)',
                fontWeight: 600,
                letterSpacing: '0.04em',
              }}
            >
              {p.id.slice(0, 8).toUpperCase()}
            </span>
          </div>
          <div style={{ display: 'flex', gap: 12, color: 'var(--c-muted)', fontSize: '0.75rem' }}>
            <span>Age: {p.age ?? '—'}</span>
            <span>Gender: {p.gender ?? '—'}</span>
            <span>Diet: {p.dietary_pattern ?? '—'}</span>
            {p.bmi && <span>BMI: {p.bmi}</span>}
          </div>
        </div>
      </div>

      {/* Screenings, Risk Score & Action Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8 }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
              {p.assessment_count} screening{p.assessment_count === 1 ? '' : 's'}
            </span>
            {p.latest_risk_level && (
              <span
                style={{
                  fontSize: '0.625rem',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: 4,
                  background: rStyle.bg,
                  color: rStyle.text,
                  border: `1px solid ${rStyle.border}`,
                }}
              >
                {p.latest_risk_level} ({p.latest_risk_score ?? '—'})
              </span>
            )}
          </div>
          <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 2 }}>
            {p.latest_assessment_date ? `Last: ${p.latest_assessment_date.split('T')[0]}` : 'No date'}
          </div>
        </div>

        {/* Action Button Group */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Red Trash Delete Button */}
          <button
            type="button"
            title="Delete Patient"
            aria-label={`Delete patient record for ${p.name}`}
            disabled={isDeleting}
            onClick={(e) => {
              e.stopPropagation()
              onDeleteRequest(p)
            }}
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              color: '#ef4444',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: isDeleting ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease',
              padding: 0,
            }}
            onMouseEnter={(e) => {
              if (!isDeleting) {
                e.currentTarget.style.background = 'rgba(239, 68, 68, 0.22)'
                e.currentTarget.style.borderColor = '#ef4444'
                e.currentTarget.style.boxShadow = '0 0 12px rgba(239, 68, 68, 0.35)'
                e.currentTarget.style.transform = 'scale(1.05)'
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'
              e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.25)'
              e.currentTarget.style.boxShadow = 'none'
              e.currentTarget.style.transform = 'scale(1)'
            }}
          >
            {isDeleting ? (
              <Loader2 size={15} className="animate-spin" color="#ef4444" />
            ) : (
              <Trash2 size={15} />
            )}
          </button>

          {/* Navigation Arrow Button */}
          <div
            title="View Patient Timeline"
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'var(--c-surface-tint)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--c-primary)',
              transition: 'all 0.15s ease',
            }}
          >
            <ChevronRight size={16} />
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default PatientCard
