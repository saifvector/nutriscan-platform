import React, { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, Trash2, Loader2, X } from 'lucide-react'

interface DeletePatientModalProps {
  isOpen: boolean
  patientName: string
  patientId: string
  assessmentCount?: number
  isDeleting: boolean
  onConfirm: () => void
  onCancel: () => void
}

export const DeletePatientModal: React.FC<DeletePatientModalProps> = ({
  isOpen,
  patientName,
  patientId,
  assessmentCount = 0,
  isDeleting,
  onConfirm,
  onCancel,
}) => {
  // Close on Escape key press if not actively deleting
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isDeleting && isOpen) {
        onCancel()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, isDeleting, onCancel])

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-patient-title"
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 16,
          }}
        >
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => !isDeleting && onCancel()}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(5, 10, 18, 0.8)',
              backdropFilter: 'blur(8px)',
              WebkitBackdropFilter: 'blur(8px)',
            }}
          />

          {/* Modal Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 16 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            onClick={(e) => e.stopPropagation()}
            style={{
              position: 'relative',
              width: '100%',
              maxWidth: 480,
              background: 'var(--c-card, #111a28)',
              borderRadius: 16,
              border: '1px solid rgba(239, 68, 68, 0.35)',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(239, 68, 68, 0.1)',
              padding: 28,
              zIndex: 1,
              color: 'var(--c-text, #f1f5f9)',
            }}
          >
            {/* Header with Danger Icon */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 12,
                    background: 'rgba(239, 68, 68, 0.12)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ef4444',
                    flexShrink: 0,
                  }}
                >
                  <AlertTriangle size={22} />
                </div>
                <div>
                  <h3
                    id="delete-patient-title"
                    style={{
                      fontSize: '1.25rem',
                      fontWeight: 700,
                      color: 'var(--c-secondary, #f8fafc)',
                      margin: 0,
                      lineHeight: 1.3,
                    }}
                  >
                    Delete Patient Record
                  </h3>
                  <span style={{ fontSize: '0.75rem', color: '#ef4444', fontWeight: 600 }}>
                    Irreversible Clinical Action
                  </span>
                </div>
              </div>

              {!isDeleting && (
                <button
                  type="button"
                  onClick={onCancel}
                  aria-label="Close dialog"
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--c-muted, #94a3b8)',
                    cursor: 'pointer',
                    padding: 4,
                    borderRadius: 6,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--c-secondary, #f8fafc)')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--c-muted, #94a3b8)')}
                >
                  <X size={18} />
                </button>
              )}
            </div>

            {/* Target Patient Chip */}
            <div
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--c-border-light, #24354a)',
                borderRadius: 10,
                padding: '10px 14px',
                marginBottom: 18,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.9375rem', color: 'var(--c-secondary, #f8fafc)' }}>
                  {patientName}
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted, #94a3b8)', marginTop: 2 }}>
                  ID: <span style={{ fontFamily: 'monospace', color: 'var(--c-primary, #14b8a6)' }}>{patientId}</span>
                </div>
              </div>
              {assessmentCount > 0 && (
                <span
                  style={{
                    fontSize: '0.6875rem',
                    padding: '2px 8px',
                    borderRadius: 999,
                    background: 'rgba(239, 68, 68, 0.15)',
                    color: '#f87171',
                    fontWeight: 600,
                  }}
                >
                  {assessmentCount} assessment{assessmentCount === 1 ? '' : 's'} linked
                </span>
              )}
            </div>

            {/* Warning Message */}
            <div style={{ fontSize: '0.875rem', color: 'var(--c-muted, #cbd5e1)', lineHeight: 1.6, marginBottom: 24 }}>
              <p style={{ margin: '0 0 12px 0' }}>
                Are you sure you want to permanently delete this patient and all associated assessments, predictions, reports, explainability records, and clinical history?
              </p>
              <p style={{ margin: 0, fontWeight: 600, color: '#f87171' }}>
                This action cannot be undone.
              </p>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12 }}>
              <button
                type="button"
                onClick={onCancel}
                disabled={isDeleting}
                className="btn-ghost"
                style={{
                  padding: '9px 18px',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  cursor: isDeleting ? 'not-allowed' : 'pointer',
                  opacity: isDeleting ? 0.6 : 1,
                  borderRadius: 8,
                }}
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={onConfirm}
                disabled={isDeleting}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '9px 20px',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: '#ffffff',
                  background: isDeleting ? '#991b1b' : '#ef4444',
                  border: '1px solid rgba(239, 68, 68, 0.6)',
                  borderRadius: 8,
                  cursor: isDeleting ? 'not-allowed' : 'pointer',
                  boxShadow: '0 4px 14px rgba(239, 68, 68, 0.35)',
                  transition: 'all 0.15s ease',
                  opacity: isDeleting ? 0.8 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!isDeleting) e.currentTarget.style.background = '#dc2626'
                }}
                onMouseLeave={(e) => {
                  if (!isDeleting) e.currentTarget.style.background = '#ef4444'
                }}
              >
                {isDeleting ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Deleting Permanently...</span>
                  </>
                ) : (
                  <>
                    <Trash2 size={16} />
                    <span>Delete Permanently</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}

export default DeletePatientModal
