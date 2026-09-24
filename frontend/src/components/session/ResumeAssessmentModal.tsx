import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Calendar,
  Clock,
  RotateCcw,
  PlusCircle,
  X,
  Copy,
  Check,
} from 'lucide-react'

export interface ResumeAssessmentModalProps {
  isOpen: boolean
  assessmentId: string
  date?: string
  assessmentDate?: string
  onResume: () => void
  onStartNew: () => void
  onClose?: () => void
}

export const ResumeAssessmentModal: React.FC<ResumeAssessmentModalProps> = ({
  isOpen,
  assessmentId,
  date,
  assessmentDate,
  onResume,
  onStartNew,
  onClose,
}) => {
  const [copied, setCopied] = useState(false)
  const modalRef = useRef<HTMLDivElement>(null)
  const primaryBtnRef = useRef<HTMLButtonElement>(null)

  const effectiveDate = assessmentDate || date || ''

  // Format date and time cleanly
  let displayDate = 'Sep 17, 2026'
  let displayTime = '11:34 AM'
  try {
    const d = new Date(effectiveDate)
    if (!isNaN(d.getTime())) {
      displayDate = d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
      displayTime = d.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      })
    } else if (effectiveDate) {
      displayDate = effectiveDate
      displayTime = ''
    }
  } catch {
    displayDate = effectiveDate || 'Sep 17, 2026'
    displayTime = ''
  }

  const handleCopyId = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!assessmentId) return
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(assessmentId)
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = assessmentId
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      }
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback handling
    }
  }

  // Accessibility: focus trap and Escape key listener
  useEffect(() => {
    if (!isOpen) return

    const previousActiveElement = document.activeElement as HTMLElement | null
    primaryBtnRef.current?.focus()

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        if (onClose) {
          onClose()
        } else {
          onStartNew()
        }
        return
      }

      if (e.key === 'Tab' && modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(
          'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
        if (focusableElements.length === 0) return

        const firstElement = focusableElements[0]
        const lastElement = focusableElements[focusableElements.length - 1]

        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      previousActiveElement?.focus()
    }
  }, [isOpen, onClose, onStartNew])

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md"
        role="dialog"
        aria-modal="true"
        aria-labelledby="resume-modal-title"
        aria-describedby="resume-modal-desc"
      >
        <motion.div
          ref={modalRef}
          initial={{ opacity: 0, scale: 0.96, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 16 }}
          transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full text-slate-100 overflow-hidden"
          style={{
            width: '640px',
            maxWidth: '90vw',
            height: 'auto',
            padding: '28px',
            borderRadius: '24px',
            background: 'rgba(12, 18, 35, 0.95)',
            border: '1px solid rgba(45, 212, 191, 0.2)',
            boxShadow: '0 24px 60px rgba(0, 0, 0, 0.45), 0 0 40px rgba(20, 184, 166, 0.08)',
          }}
        >
          {/* Teal Glow Aura Treatment */}
          <div
            className="pointer-events-none absolute -top-28 left-1/2 -translate-x-1/2 w-[420px] h-[260px] rounded-full blur-3xl opacity-60"
            style={{
              background: 'radial-gradient(circle, rgba(20, 184, 166, 0.2) 0%, rgba(15, 118, 110, 0.05) 60%, transparent 80%)',
            }}
            aria-hidden="true"
          />

          {/* Close Button Top Right */}
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/[0.08] transition-all focus:outline-none focus:ring-2 focus:ring-teal-500/50 cursor-pointer z-10"
              aria-label="Close dialog"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          {/* Header Section */}
          <div className="relative z-10 flex flex-col items-center text-center">
            {/* Saved Assessment Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase text-teal-400 bg-teal-500/10 border border-teal-500/25">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 shadow-[0_0_8px_rgba(20,184,166,0.8)]" />
              SAVED ASSESSMENT
            </div>

            {/* Title: 32px, 800 weight, 12px below badge */}
            <h2
              id="resume-modal-title"
              className="text-white tracking-tight"
              style={{
                fontSize: '32px',
                fontWeight: 800,
                lineHeight: 1.15,
                marginTop: '12px',
                marginBottom: '12px',
              }}
            >
              Previous Assessment Found
            </h2>

            {/* Description: Max 2 lines, centered */}
            <p
              id="resume-modal-desc"
              className="text-slate-300 text-sm sm:text-[15px] leading-relaxed max-w-md mx-auto"
              style={{ marginBottom: '24px' }}
            >
              Existing assessment detected in your account history.
            </p>
          </div>

          {/* Two Information Cards */}
          <div className="relative z-10 grid grid-cols-1 sm:grid-cols-2 gap-3" style={{ marginBottom: '22px' }}>
            {/* Card 1: Assessment ID */}
            <div
              className="flex flex-col justify-between"
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '14px',
                padding: '16px',
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Assessment ID
                </span>
                <button
                  type="button"
                  onClick={handleCopyId}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-teal-300 hover:bg-white/[0.08] transition-colors cursor-pointer"
                  aria-label={copied ? 'Assessment ID copied' : 'Copy assessment ID'}
                  title={copied ? 'Copied!' : 'Copy full ID'}
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-teal-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>

              <div
                className="font-mono text-xs sm:text-sm font-semibold text-teal-400 leading-snug select-all"
                style={{
                  wordBreak: 'break-all',
                  overflowWrap: 'anywhere',
                }}
              >
                {assessmentId || 'a256fb17-528c-4ed7-ad6c-15f63331992d'}
              </div>

              {copied && (
                <div className="text-[11px] font-medium text-teal-400 mt-1.5">
                  Copied to clipboard
                </div>
              )}
            </div>

            {/* Card 2: Last Updated */}
            <div
              className="flex flex-col justify-between"
              style={{
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '14px',
                padding: '16px',
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Last Updated
                </span>
                <Calendar className="w-4 h-4 text-teal-400" />
              </div>

              <div>
                <div className="text-sm sm:text-base font-bold text-slate-100">
                  {displayDate}
                </div>
                {displayTime && (
                  <div className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{displayTime}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Text */}
          <p
            className="relative z-10 text-center text-slate-300 text-sm leading-relaxed"
            style={{ marginBottom: '20px' }}
          >
            Resume the saved assessment or start a new screening.
          </p>

          {/* Action Buttons: 52px height, 14px radius, 12px gap, equal widths */}
          <div className="relative z-10 flex flex-col sm:flex-row items-center gap-3">
            <button
              ref={primaryBtnRef}
              type="button"
              onClick={onResume}
              className="w-full sm:w-1/2 flex items-center justify-center gap-2.5 font-bold text-white transition-all cursor-pointer active:scale-[0.99] hover:-translate-y-0.5"
              style={{
                height: '52px',
                borderRadius: '14px',
                background: 'linear-gradient(135deg, #0F766E 0%, #14B8A6 100%)',
                boxShadow: '0 8px 24px rgba(20, 184, 166, 0.35)',
                border: 'none',
                fontSize: '1rem',
              }}
            >
              <RotateCcw className="w-4 h-4" />
              <span>Resume Assessment</span>
            </button>

            <button
              type="button"
              onClick={onStartNew}
              className="w-full sm:w-1/2 flex items-center justify-center gap-2.5 font-semibold text-slate-100 transition-all cursor-pointer active:scale-[0.99] hover:bg-white/[0.08]"
              style={{
                height: '52px',
                borderRadius: '14px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                fontSize: '1rem',
              }}
            >
              <PlusCircle className="w-4 h-4" />
              <span>Start New Assessment</span>
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
