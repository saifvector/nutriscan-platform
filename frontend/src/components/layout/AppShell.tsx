/* ═══════════════════════════════════════════════════════════════════════════
   AppShell.tsx — Premium Glassmorphism Navigation System
   Inspired by Linear, Arc Browser, Apple VisionOS, Stripe, Raycast
   ═══════════════════════════════════════════════════════════════════════════ */

import { Outlet, NavLink, useParams, Link, useLocation } from 'react-router-dom'
import { useState, useRef, useEffect, useLayoutEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import {
  LayoutDashboard, ClipboardList, BarChart3,
  FileText, Leaf, Sparkles, ShieldCheck,
  Calendar, TrendingUp, Compass, Stethoscope, FlaskConical, Network,
  MoreHorizontal, ChevronDown, Check
} from 'lucide-react'
import ThemeToggle from '../ui/ThemeToggle'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/copilot', label: 'Copilot', icon: Stethoscope },
  { to: '/research', label: 'Research', icon: FlaskConical },
  { to: '/network', label: 'Network', icon: Network },
  { to: '/assessment', label: 'Assessment', icon: ClipboardList },
  { to: '/predictions', label: 'Predictions', icon: BarChart3 },
  { to: '/personalization', label: 'Personalization', icon: Compass },
  { to: '/recommendation-center', label: 'Precision Foods', icon: Sparkles },
  { to: '/meal-planner', label: 'Meal Planner', icon: Calendar },
  { to: '/forecasting', label: 'Forecasting', icon: TrendingUp },
  { to: '/monitoring', label: 'Governance', icon: ShieldCheck },
  { to: '/reports', label: 'Reports', icon: FileText },
]

export default function AppShell() {
  const { assessmentId } = useParams()
  const location = useLocation()
  const id = assessmentId || 'demo'
  const navRef = useRef<HTMLDivElement>(null)
  const moreButtonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const [capsuleStyle, setCapsuleStyle] = useState<{ left: number; width: number } | null>(null)
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null)
  const [moreHovered, setMoreHovered] = useState(false)
  const [moreOpen, setMoreOpen] = useState(false)
  const [dropdownPos, setDropdownPos] = useState<{ top: number; right: number } | null>(null)
  const [windowWidth, setWindowWidth] = useState(() => typeof window !== 'undefined' ? window.innerWidth : 1440)

  // Track window resize for responsive tab partitioning
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Calculate visible vs overflow items based on viewport
  const visibleLimit =
    windowWidth >= 1440 ? 8 :
    windowWidth >= 1240 ? 6 :
    windowWidth >= 1024 ? 5 : 4

  const visibleItems = navItems.slice(0, visibleLimit)
  const overflowItems = navItems.slice(visibleLimit)

  const resolveLink = (base: string) => {
    if (base === '/assessment') return base
    return `${base}/${id}`
  }

  const activeIdx = navItems.findIndex(item => location.pathname.startsWith(item.to))
  const isMoreActive = activeIdx >= visibleLimit

  // Measure active item position for sliding glass capsule
  const measureCapsule = useCallback(() => {
    if (!navRef.current) { setCapsuleStyle(null); return }
    const nav = navRef.current
    const activeEl = nav.querySelector<HTMLElement>('[data-nav-item][data-active="true"]')
    if (!activeEl) { setCapsuleStyle(null); return }
    const navRect = nav.getBoundingClientRect()
    const itemRect = activeEl.getBoundingClientRect()
    setCapsuleStyle({
      left: itemRect.left - navRect.left + nav.scrollLeft,
      width: itemRect.width,
    })
  }, [])

  useLayoutEffect(() => {
    measureCapsule()
  }, [measureCapsule, activeIdx, visibleLimit, windowWidth])

  useEffect(() => {
    window.addEventListener('resize', measureCapsule)
    return () => window.removeEventListener('resize', measureCapsule)
  }, [measureCapsule])

  // Close dropdown on outside click or window resize
  useEffect(() => {
    if (!moreOpen) return
    const handleClickOutside = (e: MouseEvent) => {
      if (
        moreButtonRef.current?.contains(e.target as Node) ||
        dropdownRef.current?.contains(e.target as Node)
      ) {
        return
      }
      setMoreOpen(false)
    }
    const handleWindowClose = () => setMoreOpen(false)

    document.addEventListener('mousedown', handleClickOutside)
    window.addEventListener('resize', handleWindowClose)
    window.addEventListener('scroll', handleWindowClose, true)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      window.removeEventListener('resize', handleWindowClose)
      window.removeEventListener('scroll', handleWindowClose, true)
    }
  }, [moreOpen])

  // Close dropdown upon navigation
  useEffect(() => {
    setMoreOpen(false)
  }, [location.pathname])

  const toggleMore = () => {
    if (!moreOpen && moreButtonRef.current) {
      const rect = moreButtonRef.current.getBoundingClientRect()
      setDropdownPos({
        top: rect.bottom + 8,
        right: Math.max(16, window.innerWidth - rect.right),
      })
    }
    setMoreOpen(prev => !prev)
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--c-bg)' }}>
      {/* ─── Premium Floating Navigation ─── */}
      <header style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50, height: 64,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '0 20px',
      }}>
        {/* Glass bar container — floating, 3-section layout, zero overflow */}
        <div style={{
          width: '100%', maxWidth: 1420, height: 48,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          overflow: 'hidden',
          padding: '0 10px 0 16px',
          borderRadius: 16,
          background: 'var(--c-glass-bg, rgba(10, 15, 25, 0.5))',
          backdropFilter: 'blur(28px) saturate(180%)',
          WebkitBackdropFilter: 'blur(28px) saturate(180%)',
          border: '1px solid var(--c-glass-border, rgba(255, 255, 255, 0.08))',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.04)',
        }}>
          {/* SECTION 1: Logo Area (max-width 180px, fixed width, flex-shrink 0) */}
          <div style={{
            maxWidth: 180,
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
          }}>
            <Link to="/" style={{
              display: 'flex', alignItems: 'center', gap: 9, textDecoration: 'none',
              flexShrink: 0,
            }}>
              <div style={{
                width: 26, height: 26, borderRadius: 7,
                background: 'linear-gradient(135deg, var(--c-primary), var(--c-primary-light))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 2px 8px rgba(20, 184, 166, 0.3)',
              }}>
                <Leaf size={13} color="white" strokeWidth={2.5} />
              </div>
              <span style={{
                fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '0.875rem',
                color: 'var(--c-secondary)', letterSpacing: '-0.025em', whiteSpace: 'nowrap',
              }}>
                NutriScan
              </span>
            </Link>
          </div>

          {/* SECTION 2: Center Navigation Menu (flex-grow, flex 1, min-width 0, overflow hidden) */}
          <div style={{
            flex: 1,
            minWidth: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0 12px',
            overflow: 'hidden',
          }}>
            <nav
              ref={navRef}
              onWheel={(e) => {
                if (navRef.current && e.deltaY !== 0) {
                  navRef.current.scrollLeft += e.deltaY * 0.6
                  measureCapsule()
                }
              }}
              style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                padding: 3,
                borderRadius: 12,
                background: 'var(--c-nav-track, rgba(255, 255, 255, 0.04))',
                border: '1px solid var(--c-nav-track-border, rgba(255, 255, 255, 0.04))',
                maxWidth: '100%',
                overflowX: 'auto',
                overflowY: 'hidden',
                whiteSpace: 'nowrap',
              }}
            >
              {/* Sliding glass capsule (active indicator) */}
              {capsuleStyle && (
                <div
                  aria-hidden
                  style={{
                    position: 'absolute', top: 3, height: 'calc(100% - 6px)',
                    left: capsuleStyle.left,
                    width: capsuleStyle.width,
                    borderRadius: 9,
                    background: 'var(--c-capsule-bg, rgba(20, 184, 166, 0.12))',
                    border: '1px solid var(--c-capsule-border, rgba(20, 184, 166, 0.2))',
                    boxShadow: '0 0 16px var(--c-capsule-glow, rgba(20, 184, 166, 0.15)), inset 0 1px 0 rgba(255, 255, 255, 0.06)',
                    transition: 'left 0.35s cubic-bezier(0.4, 0, 0.2, 1), width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    zIndex: 0,
                    pointerEvents: 'none',
                  }}
                />
              )}

              {/* Primary Visible Nav Items */}
              {visibleItems.map((item, i) => {
                const active = activeIdx === i
                const hovered = hoveredIdx === i
                return (
                  <NavLink
                    key={item.to}
                    to={resolveLink(item.to)}
                    data-nav-item
                    data-active={active ? 'true' : undefined}
                    onMouseEnter={() => setHoveredIdx(i)}
                    onMouseLeave={() => setHoveredIdx(null)}
                    style={{
                      position: 'relative', zIndex: 1,
                      display: 'flex', alignItems: 'center', gap: 5,
                      padding: '5px 10px', borderRadius: 9, textDecoration: 'none',
                      fontSize: '0.7rem', fontWeight: 600, letterSpacing: '-0.01em',
                      fontFamily: 'var(--font-body)',
                      color: active
                        ? 'var(--c-primary-light)'
                        : hovered
                          ? 'var(--c-secondary)'
                          : 'var(--c-muted)',
                      transform: hovered && !active ? 'translateY(-0.5px)' : 'none',
                      transition: 'color 0.2s ease, transform 0.2s ease',
                      whiteSpace: 'nowrap',
                      flexShrink: 0,
                    }}
                  >
                    <item.icon
                      size={13}
                      strokeWidth={active ? 2.2 : 1.8}
                      style={{
                        filter: active ? 'drop-shadow(0 0 4px var(--c-primary))' : 'none',
                        transition: 'filter 0.3s ease',
                      }}
                    />
                    {item.label}
                  </NavLink>
                )
              })}

              {/* Overflow "More" Dropdown Trigger */}
              {overflowItems.length > 0 && (
                <button
                  ref={moreButtonRef}
                  type="button"
                  data-nav-item
                  data-active={isMoreActive ? 'true' : undefined}
                  onClick={toggleMore}
                  onMouseEnter={() => setMoreHovered(true)}
                  onMouseLeave={() => setMoreHovered(false)}
                  aria-expanded={moreOpen}
                  aria-haspopup="true"
                  style={{
                    position: 'relative', zIndex: 1,
                    display: 'flex', alignItems: 'center', gap: 5,
                    padding: '5px 10px', borderRadius: 9,
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '0.7rem', fontWeight: 600, letterSpacing: '-0.01em',
                    fontFamily: 'var(--font-body)',
                    color: isMoreActive
                      ? 'var(--c-primary-light)'
                      : moreHovered || moreOpen
                        ? 'var(--c-secondary)'
                        : 'var(--c-muted)',
                    transform: (moreHovered || moreOpen) && !isMoreActive ? 'translateY(-0.5px)' : 'none',
                    transition: 'color 0.2s ease, transform 0.2s ease',
                    whiteSpace: 'nowrap',
                    flexShrink: 0,
                  }}
                >
                  <MoreHorizontal
                    size={13}
                    strokeWidth={isMoreActive ? 2.2 : 1.8}
                    style={{
                      filter: isMoreActive ? 'drop-shadow(0 0 4px var(--c-primary))' : 'none',
                      transition: 'filter 0.3s ease',
                    }}
                  />
                  <span>More</span>
                  <ChevronDown
                    size={11}
                    strokeWidth={2}
                    style={{
                      transform: moreOpen ? 'rotate(180deg)' : 'none',
                      transition: 'transform 0.2s ease',
                      opacity: 0.7,
                    }}
                  />
                </button>
              )}
            </nav>
          </div>

          {/* SECTION 3: Right User & Theme Controls (max-width 120px, fixed width, flex-shrink 0) */}
          <div style={{
            maxWidth: 120,
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            gap: 8,
          }}>
            <ThemeToggle variant="compact" />
            <Link to="/profile" style={{
              width: 28, height: 28, borderRadius: 8,
              background: 'linear-gradient(135deg, var(--c-primary), var(--c-primary-dark))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              textDecoration: 'none', fontSize: '0.625rem', fontWeight: 700, color: 'white',
              fontFamily: 'var(--font-heading)',
              boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.1)',
              flexShrink: 0,
            }}>
              JD
            </Link>
          </div>
        </div>
      </header>

      {/* ─── Portal Dropdown for "More" Navigation Items ─── */}
      {moreOpen && dropdownPos && createPortal(
        <div
          ref={dropdownRef}
          role="menu"
          style={{
            position: 'fixed',
            top: dropdownPos.top,
            right: dropdownPos.right,
            zIndex: 9999,
            minWidth: 200,
            borderRadius: 14,
            background: 'var(--c-dropdown-bg, rgba(10, 15, 25, 0.94))',
            backdropFilter: 'blur(28px) saturate(180%)',
            WebkitBackdropFilter: 'blur(28px) saturate(180%)',
            border: '1px solid var(--c-glass-border, rgba(255, 255, 255, 0.08))',
            boxShadow: '0 16px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.06)',
            padding: 6,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            animation: 'dropdownFadeIn 0.15s ease-out',
          }}
        >
          <div style={{
            padding: '6px 10px 4px',
            fontSize: '0.625rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            color: 'var(--c-muted)',
            userSelect: 'none',
          }}>
            More Modules
          </div>
          {overflowItems.map((item) => {
            const active = location.pathname.startsWith(item.to)
            return (
              <NavLink
                key={item.to}
                to={resolveLink(item.to)}
                role="menuitem"
                onClick={() => setMoreOpen(false)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 10,
                  padding: '7px 10px',
                  borderRadius: 8,
                  textDecoration: 'none',
                  fontSize: '0.75rem',
                  fontWeight: active ? 600 : 500,
                  fontFamily: 'var(--font-body)',
                  color: active ? 'var(--c-primary-light)' : 'var(--c-secondary)',
                  background: active ? 'var(--c-capsule-bg, rgba(20, 184, 166, 0.12))' : 'transparent',
                  border: active ? '1px solid var(--c-capsule-border, rgba(20, 184, 166, 0.2))' : '1px solid transparent',
                  transition: 'background 0.15s ease, color 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  if (!active) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
                }}
                onMouseLeave={(e) => {
                  if (!active) e.currentTarget.style.background = 'transparent'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <item.icon
                    size={14}
                    strokeWidth={active ? 2.2 : 1.8}
                    style={{
                      filter: active ? 'drop-shadow(0 0 4px var(--c-primary))' : 'none',
                      color: active ? 'var(--c-primary-light)' : 'var(--c-muted)',
                    }}
                  />
                  <span>{item.label}</span>
                </div>
                {active && (
                  <Check size={12} strokeWidth={2.5} color="var(--c-primary-light)" />
                )}
              </NavLink>
            )
          })}
        </div>,
        document.body
      )}

      {/* ─── Page Content ─── */}
      <main style={{ paddingTop: 64, minHeight: '100vh' }}>
        {location.pathname.startsWith('/network') || location.pathname.startsWith('/copilot') ? (
          <Outlet />
        ) : (
          <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px 80px' }}>
            <Outlet />
            {/* CDSS Statutory Regulatory Notice */}
            <footer style={{
              marginTop: 80,
              padding: '14px 18px',
              borderRadius: 12,
              background: 'var(--c-glass-bg, rgba(20, 184, 166, 0.04))',
              border: '1px solid var(--c-border, rgba(255, 255, 255, 0.08))',
              display: 'flex',
              gap: 12,
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
            }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', flex: 1, minWidth: 280 }}>
                <ShieldCheck size={16} color="var(--c-primary)" style={{ flexShrink: 0 }} />
                <p style={{
                  fontSize: '0.7rem',
                  lineHeight: 1.4,
                  color: 'var(--c-muted)',
                  margin: 0,
                }}>
                  <strong style={{ color: 'var(--c-secondary)' }}>Clinical Decision Support System (CDSS):</strong> Informational non-device clinical decision support platform compliant with FDA Section 520(o)(1)(E) and EU MDR (2017/745 Class I). Does not replace professional clinical diagnosis or customized prescriptions.
                </p>
              </div>
              <span style={{ fontSize: '0.65rem', color: 'var(--c-muted-light)', whiteSpace: 'nowrap' }}>
                NutriScan Enterprise v2.4.0 • Cryptographic SHA-256 Audit Chaining
              </span>
            </footer>
          </div>
        )}
      </main>

      {/* ─── Glass theme tokens & utility styles ─── */}
      <style>{`
        :root {
          --c-glass-bg: rgba(250, 250, 249, 0.65);
          --c-glass-border: rgba(0, 0, 0, 0.06);
          --c-nav-track: rgba(0, 0, 0, 0.03);
          --c-nav-track-border: rgba(0, 0, 0, 0.04);
          --c-capsule-bg: rgba(15, 118, 110, 0.1);
          --c-capsule-border: rgba(15, 118, 110, 0.18);
          --c-capsule-glow: rgba(15, 118, 110, 0.1);
          --c-dropdown-bg: rgba(255, 255, 255, 0.94);
        }
        [data-theme="dark"] {
          --c-glass-bg: rgba(8, 12, 20, 0.55);
          --c-glass-border: rgba(255, 255, 255, 0.07);
          --c-nav-track: rgba(255, 255, 255, 0.04);
          --c-nav-track-border: rgba(255, 255, 255, 0.03);
          --c-capsule-bg: rgba(20, 184, 166, 0.12);
          --c-capsule-border: rgba(20, 184, 166, 0.2);
          --c-capsule-glow: rgba(20, 184, 166, 0.18);
          --c-dropdown-bg: rgba(10, 15, 25, 0.94);
        }
        nav::-webkit-scrollbar {
          display: none;
        }
        nav {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        @keyframes dropdownFadeIn {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
