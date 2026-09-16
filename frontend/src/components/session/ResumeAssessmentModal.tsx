import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Calendar, RotateCcw, PlusCircle, X } from 'lucide-react'

interface ResumeAssessmentModalProps {
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
  if (!isOpen) return null

  const effectiveDate = assessmentDate || date || ''
  // Format date nicely if valid ISO
  let displayDate = effectiveDate
  try {
    const d = new Date(effectiveDate)
    if (!isNaN(d.getTime())) {
      displayDate = d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    }
  } catch {
    displayDate = effectiveDate
  }

  return (
    <AnimatePresence>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 16 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="relative w-full max-w-lg p-6 overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl text-slate-100"
          style={{ background: 'var(--c-card, #0f172a)', borderColor: 'var(--c-border, #1e293b)' }}
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h3 id="modal-title" className="text-lg font-bold text-slate-100">
                  Previous Assessment Found
                </h3>
                <p className="text-xs text-slate-400">
                  An existing clinical assessment record is available in session history.
                </p>
              </div>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Details Card */}
          <div className="my-6 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-400">Assessment ID</span>
              <span className="font-mono text-teal-400 bg-teal-950/40 px-2 py-0.5 rounded border border-teal-800/50">
                {assessmentId}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-400 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" /> Date Recorded
              </span>
              <span className="text-slate-300 font-medium">{displayDate}</span>
            </div>
          </div>

          <p className="text-sm text-slate-300 mb-6">
            Would you like to resume your previous assessment or clear active session and start a new clinical screening?
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <button
              onClick={onResume}
              className="w-full sm:w-1/2 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm bg-teal-600 hover:bg-teal-500 text-white transition-colors shadow-lg shadow-teal-900/30 active:scale-98"
            >
              <RotateCcw className="w-4 h-4" />
              Resume Assessment
            </button>
            <button
              onClick={onStartNew}
              className="w-full sm:w-1/2 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors active:scale-98"
            >
              <PlusCircle className="w-4 h-4" />
              Start New Assessment
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
