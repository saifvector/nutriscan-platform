import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, Trash2, Loader2, X, ShieldAlert } from 'lucide-react'

interface DeleteAllPatientsModalProps {
  isOpen: boolean
  patientCount: number
  isDeleting: boolean
  onConfirm: () => void
  onCancel: () => void
}

export const DeleteAllPatientsModal: React.FC<DeleteAllPatientsModalProps> = ({
  isOpen,
  patientCount,
  isDeleting,
  onConfirm,
  onCancel,
}) => {
  const [confirmText, setConfirmText] = useState('')

  // Reset confirmation input when modal opens or closes
  useEffect(() => {
    if (isOpen) {
      setConfirmText('')
    }
  }, [isOpen])

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

  const isConfirmed = confirmText.trim() === 'DELETE ALL'

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-all-patients-title"
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 99999,
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
              background: 'rgba(5, 10, 18, 0.85)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
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
              maxWidth: 520,
              background: 'var(--c-card, #111a28)',
              borderRadius: 16,
              border: '1px solid rgba(239, 68, 68, 0.45)',
              boxShadow: '0 25px 60px rgba(0, 0, 0, 0.7), 0 0 35px rgba(239, 68, 68, 0.15)',
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
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.35)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ef4444',
                    flexShrink: 0,
                  }}
                >
                  <ShieldAlert size={26} />
                </div>
                <div>
                  <h3
                    id="delete-all-patients-title"
                    style={{
                      fontSize: '1.25rem',
                      fontWeight: 700,
                      color: 'var(--c-secondary, #f8fafc)',
                      margin: 0,
                      lineHeight: 1.3,
                    }}
                  >
                    Delete All Patient Records
                  </h3>
                  <span style={{ fontSize: '0.75rem', color: '#ef4444', fontWeight: 600 }}>
                    Irreversible System-Wide Deletion
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

            {/* Impact Record Counts Badge */}
            <div
              style={{
                background: 'rgba(15, 23, 42, 0.65)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                borderRadius: 10,
                padding: '12px 16px',
                marginBottom: 18,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.875rem', color: '#f87171' }}>
                  Total Patients in Registry: {patientCount}
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted, #94a3b8)', marginTop: 2 }}>
                  All associated assessments, predictions, reports & trajectories will be purged
                </div>
              </div>
              <span
                style={{
                  fontSize: '0.6875rem',
                  padding: '3px 10px',
                  borderRadius: 999,
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: '#f87171',
                  fontWeight: 700,
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                }}
              >
                CASCADING PURGE
              </span>
            </div>

            {/* Primary Warning Description */}
            <div style={{ fontSize: '0.875rem', color: 'var(--c-muted, #cbd5e1)', lineHeight: 1.6, marginBottom: 20 }}>
              <p style={{ margin: 0 }}>
                This will permanently delete ALL patients, assessments, predictions, reports, longitudinal histories, and clinical records. This action cannot be undone.
              </p>
            </div>

            {/* Safety Verification Prompt */}
            <div style={{ marginBottom: 24 }}>
              <label
                htmlFor="confirm-delete-all-input"
                style={{
                  display: 'block',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  color: 'var(--c-secondary, #f8fafc)',
                  marginBottom: 8,
                }}
              >
                Please type <strong style={{ color: '#ef4444', letterSpacing: '0.05em' }}>DELETE ALL</strong> to confirm:
              </label>
              <input
                id="confirm-delete-all-input"
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                disabled={isDeleting}
                placeholder="DELETE ALL"
                autoComplete="off"
                spellCheck={false}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 8,
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: isConfirmed
                    ? '1px solid #10b981'
                    : confirmText.length > 0
                    ? '1px solid #ef4444'
                    : '1px solid var(--c-border-light, #24354a)',
                  outline: 'none',
                  color: '#ffffff',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  letterSpacing: '0.04em',
                  fontFamily: 'monospace',
                  transition: 'border-color 0.15s ease',
                  boxSizing: 'border-box',
                }}
              />
              {confirmText.length > 0 && !isConfirmed && (
                <div style={{ fontSize: '0.6875rem', color: '#f87171', marginTop: 4, fontWeight: 500 }}>
                  Confirmation text must match exactly &ldquo;DELETE ALL&rdquo;
                </div>
              )}
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
                disabled={!isConfirmed || isDeleting}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '9px 20px',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: '#ffffff',
                  background: !isConfirmed
                    ? 'rgba(239, 68, 68, 0.3)'
                    : isDeleting
                    ? '#991b1b'
                    : '#ef4444',
                  border: isConfirmed ? '1px solid rgba(239, 68, 68, 0.8)' : '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: 8,
                  cursor: !isConfirmed || isDeleting ? 'not-allowed' : 'pointer',
                  boxShadow: isConfirmed ? '0 4px 14px rgba(239, 68, 68, 0.35)' : 'none',
                  transition: 'all 0.15s ease',
                  opacity: !isConfirmed ? 0.5 : isDeleting ? 0.8 : 1,
                }}
                onMouseEnter={(e) => {
                  if (isConfirmed && !isDeleting) e.currentTarget.style.background = '#dc2626'
                }}
                onMouseLeave={(e) => {
                  if (isConfirmed && !isDeleting) e.currentTarget.style.background = '#ef4444'
                }}
              >
                {isDeleting ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Permanently Deleting Everything...</span>
                  </>
                ) : (
                  <>
                    <Trash2 size={16} />
                    <span>Permanently Delete Everything</span>
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

export default DeleteAllPatientsModal
