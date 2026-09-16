import { Sun, Moon, Monitor } from 'lucide-react'
import { useTheme } from '../../lib/theme'

export default function ThemeToggle({ variant = 'default' }: { variant?: 'default' | 'compact' }) {
  const { mode, setMode } = useTheme()

  const modes = [
    { key: 'light' as const, icon: Sun, label: 'Light' },
    { key: 'dark' as const, icon: Moon, label: 'Dark' },
    { key: 'system' as const, icon: Monitor, label: 'System' },
  ]

  if (variant === 'compact') {
    // Cycle through modes on click
    const nextMode = mode === 'light' ? 'dark' : mode === 'dark' ? 'system' : 'light'
    const currentIcon = mode === 'light' ? Sun : mode === 'dark' ? Moon : Monitor
    const Icon = currentIcon
    return (
      <button
        onClick={() => setMode(nextMode)}
        title={`Theme: ${mode} — click to switch`}
        style={{
          width: 32, height: 32, borderRadius: 8, border: 'none',
          background: 'transparent', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--c-muted)', transition: 'color 0.15s, background 0.15s',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = 'var(--c-surface-tint)'
          e.currentTarget.style.color = 'var(--c-primary)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'transparent'
          e.currentTarget.style.color = 'var(--c-muted)'
        }}
      >
        <Icon size={16} />
      </button>
    )
  }

  return (
    <div style={{
      display: 'flex', gap: 2, padding: 3, borderRadius: 10,
      background: 'var(--c-bg-secondary)', border: '1px solid var(--c-border)',
    }}>
      {modes.map(m => (
        <button
          key={m.key}
          onClick={() => setMode(m.key)}
          title={m.label}
          style={{
            display: 'flex', alignItems: 'center', gap: 5,
            padding: '5px 10px', borderRadius: 7, border: 'none',
            background: mode === m.key ? 'var(--c-card)' : 'transparent',
            boxShadow: mode === m.key ? 'var(--c-shadow-sm)' : 'none',
            color: mode === m.key ? 'var(--c-primary)' : 'var(--c-muted)',
            fontSize: '0.6875rem', fontWeight: 600, fontFamily: 'var(--font-body)',
            cursor: 'pointer', transition: 'all 0.15s ease',
          }}
        >
          <m.icon size={13} />
          {m.label}
        </button>
      ))}
    </div>
  )
}
