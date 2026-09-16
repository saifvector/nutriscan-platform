import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

type ThemeMode = 'light' | 'dark' | 'system'
type ResolvedTheme = 'light' | 'dark'

interface ThemeContextValue {
  mode: ThemeMode
  resolved: ResolvedTheme
  setMode: (mode: ThemeMode) => void
}

const ThemeContext = createContext<ThemeContextValue>({
  mode: 'system',
  resolved: 'light',
  setMode: () => {},
})

export function useTheme() {
  return useContext(ThemeContext)
}

function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function resolveTheme(mode: ThemeMode): ResolvedTheme {
  if (mode === 'system') return getSystemTheme()
  return mode
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(() => {
    try {
      const stored = localStorage.getItem('nutriscan-theme')
      if (stored === 'light' || stored === 'dark' || stored === 'system') return stored
    } catch { /* ignore */ }
    return 'dark'
  })

  const [resolved, setResolved] = useState<ResolvedTheme>(() => resolveTheme(mode))

  // Apply theme to <html> element
  useEffect(() => {
    const newResolved = resolveTheme(mode)
    setResolved(newResolved)
    document.documentElement.setAttribute('data-theme', newResolved)
  }, [mode])

  // Listen for system theme changes when mode is 'system'
  useEffect(() => {
    if (mode !== 'system') return
    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => {
      const newResolved = resolveTheme('system')
      setResolved(newResolved)
      document.documentElement.setAttribute('data-theme', newResolved)
    }
    mql.addEventListener('change', handler)
    return () => mql.removeEventListener('change', handler)
  }, [mode])

  const setMode = (newMode: ThemeMode) => {
    setModeState(newMode)
    try { localStorage.setItem('nutriscan-theme', newMode) } catch { /* ignore */ }
  }

  return (
    <ThemeContext.Provider value={{ mode, resolved, setMode }}>
      {children}
    </ThemeContext.Provider>
  )
}
