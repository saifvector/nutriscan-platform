import React, { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react'

interface Props {
  children: ReactNode
  fallbackTitle?: string
  fallbackMessage?: string
  onReset?: () => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  copied: boolean
  showDetails: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    copied: false,
    showDetails: false,
  }

  public static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Clinical ErrorBoundary caught uncaught runtime error:', error, errorInfo)
    this.setState({ errorInfo })
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      copied: false,
      showDetails: false,
    })
    if (this.props.onReset) {
      this.props.onReset()
    }
  }

  private handleCopyDiagnostics = () => {
    const { error, errorInfo } = this.state
    const diagnostics = [
      `Timestamp: ${new Date().toISOString()}`,
      `Error: ${error?.name || 'UnknownError'}: ${error?.message || 'No message'}`,
      `Stack: ${error?.stack || 'No stack trace'}`,
      `Component Stack: ${errorInfo?.componentStack || 'No component stack'}`,
      `User Agent: ${navigator.userAgent}`,
      `URL: ${window.location.href}`,
    ].join('\n\n')

    navigator.clipboard.writeText(diagnostics).then(() => {
      this.setState({ copied: true })
      setTimeout(() => this.setState({ copied: false }), 2500)
    })
  }

  public render() {
    if (this.state.hasError) {
      const { fallbackTitle, fallbackMessage } = this.props
      const { error, errorInfo, copied, showDetails } = this.state

      return (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '65vh',
            padding: '32px 24px',
            backgroundColor: 'transparent',
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: 640,
              backgroundColor: 'var(--c-card, #161B22)',
              border: '1px solid rgba(239, 68, 68, 0.35)',
              borderRadius: 16,
              padding: '32px 28px',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
              color: 'var(--c-secondary, #F8FAFC)',
              fontFamily: 'Inter, system-ui, sans-serif',
            }}
          >
            {/* Header with Icon */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 12,
                  backgroundColor: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--c-danger, #EF4444)',
                  flexShrink: 0,
                }}
              >
                <AlertTriangle size={24} />
              </div>
              <div>
                <span
                  style={{
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    color: 'var(--c-danger, #EF4444)',
                  }}
                >
                  Clinical Resilience Guardrail
                </span>
                <h2
                  style={{
                    fontSize: '1.25rem',
                    fontWeight: 800,
                    margin: '2px 0 0 0',
                    color: 'var(--c-secondary, #F8FAFC)',
                  }}
                >
                  {fallbackTitle || 'Module Temporarily Unavailable'}
                </h2>
              </div>
            </div>

            {/* Description */}
            <p
              style={{
                fontSize: '0.875rem',
                color: 'var(--c-muted, #94A3B8)',
                lineHeight: 1.6,
                marginBottom: 24,
              }}
            >
              {fallbackMessage ||
                'An unexpected runtime condition occurred in this clinical view. Your patient assessment data is safely preserved in the restart-safe persistence layer.'}
            </p>

            {/* Error Message Pill */}
            {error && (
              <div
                style={{
                  backgroundColor: 'rgba(239, 68, 68, 0.08)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: 8,
                  padding: '10px 14px',
                  fontSize: '0.8125rem',
                  color: 'var(--c-danger, #EF4444)',
                  fontFamily: 'monospace',
                  marginBottom: 24,
                  wordBreak: 'break-word',
                }}
              >
                {error.name}: {error.message}
              </div>
            )}

            {/* Actions */}
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 12,
                marginBottom: 20,
              }}
            >
              <button
                type="button"
                onClick={this.handleReset}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 18px',
                  backgroundColor: 'var(--c-primary, #10B981)',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: 10,
                  fontSize: '0.8125rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'opacity 0.2s',
                }}
                onMouseEnter={e => ((e.currentTarget as HTMLElement).style.opacity = '0.9')}
                onMouseLeave={e => ((e.currentTarget as HTMLElement).style.opacity = '1')}
              >
                <RefreshCw size={15} />
                Retry Module
              </button>

              <button
                type="button"
                onClick={() => {
                  window.location.href = '/dashboard'
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '10px 18px',
                  backgroundColor: 'transparent',
                  color: 'var(--c-secondary, #F8FAFC)',
                  border: '1px solid var(--c-border, rgba(148, 163, 184, 0.25))',
                  borderRadius: 10,
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={e =>
                  ((e.currentTarget as HTMLElement).style.backgroundColor = 'rgba(255, 255, 255, 0.05)')
                }
                onMouseLeave={e =>
                  ((e.currentTarget as HTMLElement).style.backgroundColor = 'transparent')
                }
              >
                <Home size={15} />
                Return to Dashboard
              </button>

              <button
                type="button"
                onClick={this.handleCopyDiagnostics}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '10px 14px',
                  backgroundColor: 'transparent',
                  color: 'var(--c-muted, #94A3B8)',
                  border: '1px solid transparent',
                  borderRadius: 10,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  marginLeft: 'auto',
                }}
              >
                {copied ? <Check size={14} color="#10B981" /> : <Copy size={14} />}
                {copied ? 'Diagnostics Copied' : 'Copy Diagnostics'}
              </button>
            </div>

            {/* Collapsible Technical Details */}
            <div style={{ borderTop: '1px solid var(--c-border, rgba(148, 163, 184, 0.15))', paddingTop: 14 }}>
              <button
                type="button"
                onClick={() => this.setState({ showDetails: !showDetails })}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--c-muted, #94A3B8)',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: 0,
                }}
              >
                {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                {showDetails ? 'Hide Technical Diagnostics' : 'Show Technical Diagnostics'}
              </button>

              {showDetails && (
                <div
                  style={{
                    marginTop: 12,
                    padding: 12,
                    backgroundColor: 'rgba(0, 0, 0, 0.3)',
                    borderRadius: 8,
                    fontSize: '0.6875rem',
                    fontFamily: 'monospace',
                    color: '#94A3B8',
                    maxHeight: 180,
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.5,
                  }}
                >
                  {error?.stack || 'No stack trace available.'}
                  {errorInfo?.componentStack && `\n\nComponent Stack:\n${errorInfo.componentStack}`}
                </div>
              )}
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
