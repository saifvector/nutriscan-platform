import { motion, AnimatePresence } from 'framer-motion'
import { X, Download, Printer, Shield, CheckCircle, FileText, Calendar, User, ExternalLink, Leaf } from 'lucide-react'

interface PDFPreviewModalProps {
  isOpen: boolean
  onClose: () => void
  reportId?: string
  patientName?: string
  assessmentDate?: string
  healthScore?: number
  healthCategory?: string
  onDownloadPdf?: () => void
}

export default function PDFPreviewModal({
  isOpen,
  onClose,
  reportId = 'rpt-2026-alpha',
  patientName = 'Alex Mercer',
  assessmentDate = '2026-09-10',
  healthScore = 76,
  healthCategory = 'GOOD',
  onDownloadPdf,
}: PDFPreviewModalProps) {
  if (!isOpen) return null

  const handlePrint = () => {
    window.print()
  }

  return (
    <AnimatePresence>
      <div style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
        background: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(8px)',
      }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ duration: 0.25 }}
          style={{
            width: '100%',
            maxWidth: 860,
            maxHeight: '90vh',
            background: 'var(--c-card)',
            border: '1px solid var(--c-border)',
            borderRadius: 20,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: 'var(--c-shadow-lg)',
          }}
        >
          {/* Modal Header */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '18px 24px',
            borderBottom: '1px solid var(--c-border-light)',
            background: 'var(--c-surface-alt)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 8, background: 'var(--c-primary)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <FileText size={16} color="white" />
              </div>
              <div>
                <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '0.9375rem', fontWeight: 700, margin: 0, color: 'var(--c-text)' }}>
                  Clinical Assessment Report Preview
                </h3>
                <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
                  ID: {reportId} · Official Medical Summary
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <button
                onClick={handlePrint}
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                  padding: '8px 14px', borderRadius: 10,
                  border: '1px solid var(--c-border-light)', background: 'transparent',
                  color: 'var(--c-text-secondary)', fontSize: '0.75rem', fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <Printer size={13} /> Print
              </button>
              <button
                onClick={onDownloadPdf}
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                  padding: '8px 16px', borderRadius: 10,
                  border: 'none', background: 'var(--c-primary)',
                  color: 'white', fontSize: '0.75rem', fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                <Download size={13} /> Download PDF
              </button>
              <button
                onClick={onClose}
                style={{
                  width: 32, height: 32, borderRadius: 8,
                  border: 'none', background: 'var(--c-surface-tint)',
                  color: 'var(--c-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  cursor: 'pointer',
                }}
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Modal Document Body (Scrollable Clinical Page) */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '32px 36px',
            background: 'var(--c-bg)',
            display: 'flex',
            flexDirection: 'column',
            gap: 24,
          }}>
            {/* Document Cover Header */}
            <div style={{
              background: 'var(--c-card)',
              border: '1px solid var(--c-border)',
              borderRadius: 16,
              padding: '24px 28px',
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: 16,
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <div style={{ width: 22, height: 22, borderRadius: 6, background: 'var(--c-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Leaf size={12} color="white" />
                  </div>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 800, color: 'var(--c-primary)', letterSpacing: '0.04em' }}>
                    NUTRISCAN CLINICAL INTELLIGENCE PLATFORM
                  </span>
                </div>
                <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.375rem', fontWeight: 800, margin: '0 0 6px', color: 'var(--c-text)' }}>
                  Nutritional Deficiency Screening & Recovery Report
                </h1>
                <div style={{ display: 'flex', gap: 16, fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                  <span><b>Patient:</b> {patientName}</span>
                  <span><b>Date:</b> {assessmentDate}</span>
                  <span><b>Protocol:</b> Multi-Nutrient Screening v1.2</span>
                </div>
              </div>

              <div style={{
                textAlign: 'center',
                padding: '12px 20px',
                borderRadius: 12,
                background: 'var(--c-surface-alt)',
                border: '1px solid var(--c-border-light)',
              }}>
                <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase' }}>Overall Health Score</div>
                <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, color: 'var(--c-primary)', lineHeight: 1.1 }}>
                  {healthScore}
                </div>
                <span style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-success)' }}>
                  {healthCategory} (75–89)
                </span>
              </div>
            </div>

            {/* Section 1: Executive Summary */}
            <div style={{ background: 'var(--c-card)', border: '1px solid var(--c-border)', borderRadius: 14, padding: '20px 24px' }}>
              <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-text)', marginBottom: 8 }}>
                1. Executive Summary & Clinical Highlights
              </h4>
              <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.6, margin: '0 0 12px' }}>
                Multi-nutrient predictive modeling indicates good overall nutritional resilience with targeted depletions in
                Vitamin D (52%) and Iron (43%). Previous acute deficiencies in Vitamin B12 and Zinc have successfully reached
                homeostatic recovery following dietary protocol adherence.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {[
                  'Primary Residual Risk: Moderate Vitamin D insufficiency requiring continued 30m daylight exposure.',
                  'Significant Improvement: Non-heme iron absorption normalized under ascorbic acid pairings.',
                  'Biochemical Balance: Calcium-Magnesium ratio restored to recommended 2:1 physiological equilibrium.'
                ].map((item, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.75rem', color: 'var(--c-text)' }}>
                    <CheckCircle size={14} color="var(--c-success)" style={{ flexShrink: 0 }} />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Section 2: Deficiency Prediction Matrix */}
            <div style={{ background: 'var(--c-card)', border: '1px solid var(--c-border)', borderRadius: 14, padding: '20px 24px' }}>
              <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-text)', marginBottom: 12 }}>
                2. 11-Nutrient Deficiency Analysis Matrix
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
                {[
                  { n: 'Vitamin D', s: 52, l: 'MODERATE' },
                  { n: 'Iron', s: 43, l: 'MODERATE' },
                  { n: 'Calcium', s: 44, l: 'MODERATE' },
                  { n: 'Magnesium', s: 38, l: 'LOW' },
                  { n: 'Folate', s: 32, l: 'LOW' },
                  { n: 'Zinc', s: 31, l: 'LOW' },
                  { n: 'Vitamin B12', s: 29, l: 'LOW' },
                  { n: 'Vitamin C', s: 20, l: 'LOW' },
                  { n: 'Vitamin A', s: 18, l: 'LOW' },
                  { n: 'Vitamin E', s: 15, l: 'LOW' },
                  { n: 'Protein', s: 12, l: 'LOW' },
                ].map(row => (
                  <div key={row.n} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '8px 12px', borderRadius: 8, background: 'var(--c-surface-alt)',
                    fontSize: '0.75rem',
                  }}>
                    <span style={{ fontWeight: 600, color: 'var(--c-text)' }}>{row.n}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontWeight: 800, color: row.s > 50 ? '#F97316' : 'var(--c-success)' }}>{row.s}%</span>
                      <span style={{ fontSize: '0.625rem', color: 'var(--c-muted)' }}>({row.l})</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Section 3: Recovery Roadmap & Progress Tracking */}
            <div style={{ background: 'var(--c-card)', border: '1px solid var(--c-border)', borderRadius: 14, padding: '20px 24px' }}>
              <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-text)', marginBottom: 8 }}>
                3. Longitudinal Progress & 30-Day Recovery Roadmap
              </h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 12 }}>
                Sequential screening demonstrates +14 points total improvement at a recovery velocity of 3.5 points/week.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                <div style={{ padding: '12px', borderRadius: 10, background: 'var(--c-surface-alt)' }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)' }}>Phase 1 (Days 1–7)</div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-text)', margin: '4px 0' }}>Arrest Depletion</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Daily wild salmon, fortified eggs, and 2.5L hydration.</div>
                </div>
                <div style={{ padding: '12px', borderRadius: 10, background: 'var(--c-surface-alt)' }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)' }}>Phase 2 (Days 8–14)</div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-text)', margin: '4px 0' }}>Synergistic Uptake</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>Pair spinach with citrus; space calcium from iron.</div>
                </div>
                <div style={{ padding: '12px', borderRadius: 10, background: 'var(--c-surface-alt)' }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)' }}>Phase 3 (Days 15–30)</div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-text)', margin: '4px 0' }}>Cellular Homeostasis</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>20+ diverse whole foods and active recovery habits.</div>
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <div style={{
              padding: '12px 16px',
              borderRadius: 10,
              background: 'var(--c-surface-alt)',
              fontSize: '0.6875rem',
              color: 'var(--c-muted)',
              lineHeight: 1.5,
            }}>
              <b>Clinical Disclaimer:</b> This report is generated by an AI screening model based on questionnaire and biomarker indicators.
              Confirmatory laboratory blood testing (25-OH Vitamin D, Ferritin, Serum B12) and physician consultation is advised prior to therapeutic supplementation.
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
