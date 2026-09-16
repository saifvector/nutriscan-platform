import React from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sparkles, PlusCircle, RotateCcw, type LucideIcon } from 'lucide-react'

export interface AssessmentRequiredStateProps {
  title?: string
  description: string
  actionLabel?: string
  onAction?: () => void
  secondaryActionLabel?: string
  onSecondaryAction?: () => void
  icon?: LucideIcon
  badge?: string
}

export const AssessmentRequiredState: React.FC<AssessmentRequiredStateProps> = ({
  title = 'Nutritional Assessment Required',
  description,
  actionLabel = 'Start Assessment',
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  icon: Icon = Sparkles,
  badge = 'CLINICAL INTAKE REQUIRED',
}) => {
  const navigate = useNavigate()

  const handlePrimaryClick = () => {
    if (onAction) {
      onAction()
    } else {
      navigate('/assessment')
    }
  }

  return (
    <div className="nutriscan-empty-state-wrapper">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="nutriscan-glass-card"
      >
        {/* Soft background glow aura */}
        <div className="nutriscan-glow-aura" />

        {/* Clinical protocol pill badge */}
        {badge && (
          <div className="nutriscan-badge">
            <span className="nutriscan-badge-dot" />
            {badge}
          </div>
        )}

        {/* Large icon container */}
        <div className="nutriscan-icon-container">
          <Icon size={44} strokeWidth={2.2} />
        </div>

        {/* Large heading */}
        <h2 className="nutriscan-empty-heading">
          {title}
        </h2>

        {/* Supporting description */}
        <p className="nutriscan-empty-desc">
          {description}
        </p>

        {/* Action button row */}
        <div className="nutriscan-btn-row">
          <button
            type="button"
            onClick={handlePrimaryClick}
            className="nutriscan-cta-primary"
          >
            <PlusCircle size={20} />
            <span>{actionLabel}</span>
          </button>

          {secondaryActionLabel && onSecondaryAction && (
            <button
              type="button"
              onClick={onSecondaryAction}
              className="nutriscan-cta-secondary"
            >
              <RotateCcw size={18} />
              <span>{secondaryActionLabel}</span>
            </button>
          )}
        </div>
      </motion.div>

      {/* Scoped CSS ensuring exact responsive typography and 80px footer separation */}
      <style>{`
        .nutriscan-empty-state-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          width: 100%;
          max-width: 900px;
          min-height: 500px;
          margin: 40px auto 80px auto;
          padding: 0 16px;
          box-sizing: border-box;
        }

        .nutriscan-glass-card {
          width: 100%;
          min-height: 500px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: var(--c-card, rgba(23, 31, 46, 0.78));
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border: 1px solid rgba(45, 212, 191, 0.2);
          border-radius: 28px;
          box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45), 0 0 40px rgba(20, 184, 166, 0.08);
          padding: 64px 44px;
          text-align: center;
          position: relative;
          overflow: hidden;
          box-sizing: border-box;
        }

        .nutriscan-glow-aura {
          position: absolute;
          top: -120px;
          left: 50%;
          transform: translateX(-50%);
          width: 480px;
          height: 320px;
          background: radial-gradient(circle, rgba(20, 184, 166, 0.16) 0%, rgba(15, 118, 110, 0.04) 60%, transparent 80%);
          pointer-events: none;
          z-index: 0;
        }

        .nutriscan-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 6px 16px;
          border-radius: 9999px;
          background: rgba(20, 184, 166, 0.1);
          border: 1px solid rgba(20, 184, 166, 0.25);
          color: var(--c-primary, #14B8A6);
          font-size: 0.75rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          margin-bottom: 24px;
          z-index: 1;
        }

        .nutriscan-badge-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--c-primary, #14B8A6);
          box-shadow: 0 0 8px var(--c-primary, #14B8A6);
        }

        .nutriscan-icon-container {
          width: 96px;
          height: 96px;
          border-radius: 28px;
          background: linear-gradient(135deg, rgba(20, 184, 166, 0.2) 0%, rgba(15, 118, 110, 0.06) 100%);
          border: 1px solid rgba(45, 212, 191, 0.35);
          box-shadow: 0 12px 30px rgba(20, 184, 166, 0.25), inset 0 1px 2px rgba(255, 255, 255, 0.15);
          color: var(--c-primary, #14B8A6);
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 28px auto;
          position: relative;
          z-index: 1;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .nutriscan-icon-container:hover {
          transform: translateY(-2px) scale(1.02);
          box-shadow: 0 16px 36px rgba(20, 184, 166, 0.35);
        }

        .nutriscan-empty-heading {
          font-family: var(--font-heading, 'Inter Tight', system-ui, sans-serif);
          font-weight: 800;
          letter-spacing: -0.03em;
          line-height: 1.15;
          color: var(--c-text, #F8FAFC);
          margin: 0 0 16px 0;
          z-index: 1;
          position: relative;
          /* Desktop default: 48px */
          font-size: 48px;
        }

        .nutriscan-empty-desc {
          color: var(--c-text-secondary, #94A3B8);
          line-height: 1.65;
          max-width: 640px;
          margin: 0 auto 36px auto;
          z-index: 1;
          position: relative;
          /* Desktop default: 18px */
          font-size: 18px;
        }

        .nutriscan-btn-row {
          display: flex;
          gap: 16px;
          justify-content: center;
          flex-wrap: wrap;
          z-index: 1;
          position: relative;
        }

        .nutriscan-cta-primary {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%);
          color: #ffffff;
          padding: 16px 36px;
          border-radius: 14px;
          font-weight: 700;
          font-size: 1.05rem;
          border: none;
          cursor: pointer;
          box-shadow: 0 8px 24px rgba(20, 184, 166, 0.35);
          transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .nutriscan-cta-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 12px 32px rgba(20, 184, 166, 0.45);
        }

        .nutriscan-cta-primary:active {
          transform: translateY(0);
        }

        .nutriscan-cta-secondary {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          background: rgba(255, 255, 255, 0.04);
          color: var(--c-text, #F8FAFC);
          border: 1px solid var(--c-border, #293548);
          padding: 16px 32px;
          border-radius: 14px;
          font-weight: 600;
          font-size: 1.05rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .nutriscan-cta-secondary:hover {
          background: rgba(255, 255, 255, 0.08);
          border-color: rgba(45, 212, 191, 0.3);
          transform: translateY(-2px);
        }

        /* ─── Tablet typography (max-width: 1023px) ─── */
        @media (max-width: 1023px) {
          .nutriscan-glass-card {
            padding: 56px 32px;
          }
          .nutriscan-empty-heading {
            font-size: 36px;
          }
          .nutriscan-empty-desc {
            font-size: 18px;
          }
        }

        /* ─── Mobile typography (max-width: 639px) ─── */
        @media (max-width: 639px) {
          .nutriscan-empty-state-wrapper {
            margin: 24px auto 80px auto;
            padding: 0 12px;
          }
          .nutriscan-glass-card {
            padding: 44px 20px;
            min-height: 440px;
            border-radius: 20px;
          }
          .nutriscan-icon-container {
            width: 80px;
            height: 80px;
            border-radius: 22px;
            margin-bottom: 22px;
          }
          .nutriscan-empty-heading {
            font-size: 28px;
          }
          .nutriscan-empty-desc {
            font-size: 16px;
            margin-bottom: 28px;
          }
          .nutriscan-btn-row {
            flex-direction: column;
            width: 100%;
          }
          .nutriscan-cta-primary,
          .nutriscan-cta-secondary {
            width: 100%;
            justify-content: center;
            padding: 14px 24px;
          }
        }

        /* ─── Ultra-wide displays (min-width: 1920px) ─── */
        @media (min-width: 1920px) {
          .nutriscan-empty-state-wrapper {
            max-width: 960px;
            margin: 60px auto 100px auto;
          }
          .nutriscan-glass-card {
            padding: 72px 56px;
          }
        }
      `}</style>
    </div>
  )
}

export default AssessmentRequiredState
