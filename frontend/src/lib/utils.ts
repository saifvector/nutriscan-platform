import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPercentage(value: number): string {
  return `${Math.round(value * 100)}%`
}

export function getRiskColor(level: string): string {
  const l = level.toUpperCase()
  if (l === 'HIGH' || l === 'SEVERE') return '#DC2626'
  if (l === 'MODERATE') return '#F59E0B'
  return '#16A34A'
}

export function getRiskBadgeClass(level: string): string {
  const l = level.toUpperCase()
  if (l === 'HIGH' || l === 'SEVERE') return 'risk-badge risk-badge-high'
  if (l === 'MODERATE') return 'risk-badge risk-badge-moderate'
  return 'risk-badge risk-badge-low'
}

export function getScoreColor(score: number): string {
  if (score >= 85) return '#16A34A'
  if (score >= 70) return '#0F766E'
  if (score >= 50) return '#F59E0B'
  return '#DC2626'
}

export function getScoreCategory(score: number): string {
  if (score >= 85) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 50) return 'Moderate Risk'
  return 'High Risk'
}
