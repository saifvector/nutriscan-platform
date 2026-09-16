import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts'
import { Activity, TrendingUp, Layers } from 'lucide-react'

interface TrendAnalyticsChartsProps {
  timelineData: Array<{
    date: string
    health_score: number
    'Vitamin D'?: number
    'Iron'?: number
    'Vitamin B12'?: number
    'Calcium'?: number
    'Magnesium'?: number
    'Zinc'?: number
  }>
}

export default function TrendAnalyticsCharts({ timelineData }: TrendAnalyticsChartsProps) {
  const [chartMode, setChartMode] = useState<'SCORE' | 'NUTRIENTS'>('SCORE')

  const fallbackTimeline = [
    { date: 'Aug 10', health_score: 62, 'Vitamin D': 87, 'Iron': 71, 'Vitamin B12': 63, 'Calcium': 60, 'Zinc': 45 },
    { date: 'Aug 26', health_score: 69, 'Vitamin D': 68, 'Iron': 56, 'Vitamin B12': 45, 'Calcium': 51, 'Zinc': 37 },
    { date: 'Sep 10', health_score: 76, 'Vitamin D': 52, 'Iron': 43, 'Vitamin B12': 29, 'Calcium': 44, 'Zinc': 31 },
  ]

  const data = timelineData && timelineData.length > 0 ? timelineData : fallbackTimeline

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          borderRadius: 12,
          padding: '10px 14px',
          boxShadow: 'var(--c-shadow-md)',
          fontSize: '0.75rem',
        }}>
          <div style={{ fontWeight: 700, color: 'var(--c-text)', marginBottom: 6 }}>{label}</div>
          {payload.map((entry: any) => (
            <div key={entry.name} style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '2px 0' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: entry.color }} />
              <span style={{ color: 'var(--c-muted)' }}>{entry.name}:</span>
              <span style={{ fontWeight: 700, color: 'var(--c-text)' }}>{entry.value}{chartMode === 'SCORE' ? ' pts' : '%'}</span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div style={{
      background: 'var(--c-card)',
      border: '1px solid var(--c-border)',
      borderRadius: 20,
      padding: '24px 28px',
      boxShadow: 'var(--c-shadow-sm)',
    }}>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        marginBottom: 20,
      }}>
        <div>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.125rem', fontWeight: 700, color: 'var(--c-text)', margin: 0 }}>
            Longitudinal Trend Analytics
          </h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', margin: '4px 0 0' }}>
            High-resolution trajectory of health score optimization and per-nutrient risk curve reduction.
          </p>
        </div>

        {/* Mode Switcher */}
        <div style={{
          display: 'inline-flex',
          padding: 3,
          borderRadius: 10,
          background: 'var(--c-surface-alt)',
          border: '1px solid var(--c-border-light)',
        }}>
          <button
            onClick={() => setChartMode('SCORE')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 14px',
              borderRadius: 8,
              border: 'none',
              background: chartMode === 'SCORE' ? 'var(--c-card)' : 'transparent',
              color: chartMode === 'SCORE' ? 'var(--c-text)' : 'var(--c-muted)',
              fontSize: '0.75rem',
              fontWeight: 700,
              boxShadow: chartMode === 'SCORE' ? 'var(--c-shadow-xs)' : 'none',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <TrendingUp size={13} color={chartMode === 'SCORE' ? 'var(--c-primary)' : 'var(--c-muted)'} />
            Overall Health Score
          </button>
          <button
            onClick={() => setChartMode('NUTRIENTS')}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 14px',
              borderRadius: 8,
              border: 'none',
              background: chartMode === 'NUTRIENTS' ? 'var(--c-card)' : 'transparent',
              color: chartMode === 'NUTRIENTS' ? 'var(--c-text)' : 'var(--c-muted)',
              fontSize: '0.75rem',
              fontWeight: 700,
              boxShadow: chartMode === 'NUTRIENTS' ? 'var(--c-shadow-xs)' : 'none',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <Layers size={13} color={chartMode === 'NUTRIENTS' ? 'var(--c-primary)' : 'var(--c-muted)'} />
            Nutrient Risk Trajectories
          </button>
        </div>
      </div>

      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartMode === 'SCORE' ? (
            <AreaChart data={data} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--c-primary)" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="var(--c-primary)" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--c-border-light)" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: 'var(--c-muted)', fontSize: 12 }} stroke="var(--c-border-light)" />
              <YAxis domain={[40, 100]} tick={{ fill: 'var(--c-muted)', fontSize: 12 }} stroke="var(--c-border-light)" />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="health_score"
                name="Health Score"
                stroke="var(--c-primary)"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#scoreGradient)"
              />
            </AreaChart>
          ) : (
            <LineChart data={data} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--c-border-light)" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: 'var(--c-muted)', fontSize: 12 }} stroke="var(--c-border-light)" />
              <YAxis domain={[0, 100]} tick={{ fill: 'var(--c-muted)', fontSize: 12 }} stroke="var(--c-border-light)" unit="%" />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: 12 }} />
              <Line type="monotone" dataKey="Vitamin D" stroke="#F59E0B" strokeWidth={2.5} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="Iron" stroke="#EF4444" strokeWidth={2.5} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="Vitamin B12" stroke="#10B981" strokeWidth={2.5} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="Calcium" stroke="#3B82F6" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3 }} />
              <Line type="monotone" dataKey="Zinc" stroke="#8B5CF6" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3 }} />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
