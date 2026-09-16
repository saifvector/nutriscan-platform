import React from 'react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ReferenceLine } from 'recharts'
import { TrendingUp, TrendingDown, Info } from 'lucide-react'

export interface FeatureDriver {
  feature: string
  label: string
  category: string
  value?: any
  impact: number
  contribution_pct: number
  direction: 'POSITIVE' | 'PROTECTIVE'
}

interface FeatureContributionWaterfallProps {
  targetName: string
  riskTier: string
  calibratedProbability: number
  positiveDrivers: FeatureDriver[]
  protectiveDrivers: FeatureDriver[]
}

export const FeatureContributionWaterfall: React.FC<FeatureContributionWaterfallProps> = ({
  targetName,
  riskTier,
  calibratedProbability,
  positiveDrivers,
  protectiveDrivers
}) => {
  // Combine into unified chart data
  const chartData = [
    ...positiveDrivers.map(d => ({
      name: d.label,
      impact: Math.round(d.impact * 1000) / 1000,
      pct: d.contribution_pct,
      category: d.category,
      direction: 'Risk Contributor'
    })),
    ...protectiveDrivers.map(d => ({
      name: d.label,
      impact: Math.round(d.impact * 1000) / 1000,
      pct: d.contribution_pct,
      category: d.category,
      direction: 'Protective Counterbalance'
    }))
  ]

  const tierBadgeColor =
    riskTier === 'HIGH'
      ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20'
      : riskTier === 'MODERATE'
      ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'
      : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'

  return (
    <div className="bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              Feature Attributions: {targetName}
            </h3>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${tierBadgeColor}`}>
              {riskTier} Risk ({Math.round(calibratedProbability * 100)}%)
            </span>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Local SHAP value decomposition: Positive features increase risk; negative features provide biological protection.
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-rose-500 inline-block" />
            <span className="text-slate-600 dark:text-slate-300">Risk Elevation (+)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-emerald-500 inline-block" />
            <span className="text-slate-600 dark:text-slate-300">Protective Mitigation (-)</span>
          </div>
        </div>
      </div>

      {/* Waterfall Bar Chart */}
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 140, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} horizontal={false} />
            <XAxis
              type="number"
              domain={['dataMin - 0.05', 'dataMax + 0.05']}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickFormatter={(v) => `${v > 0 ? '+' : ''}${v}`}
            />
            <YAxis
              dataKey="name"
              type="category"
              tick={{ fontSize: 12, fill: '#64748b' }}
              width={130}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload
                  const isPos = data.impact >= 0
                  return (
                    <div className="bg-slate-900 text-white p-3 rounded-xl shadow-xl text-xs border border-slate-700 max-w-xs">
                      <div className="font-semibold text-sm mb-1">{data.name}</div>
                      <div className="text-slate-400 mb-2">Category: {data.category}</div>
                      <div className="flex items-center gap-2">
                        {isPos ? <TrendingUp className="w-4 h-4 text-rose-400" /> : <TrendingDown className="w-4 h-4 text-emerald-400" />}
                        <span className={isPos ? 'text-rose-300 font-semibold' : 'text-emerald-300 font-semibold'}>
                          {data.direction}: {isPos ? `+${data.impact}` : data.impact}
                        </span>
                      </div>
                      <div className="text-slate-400 mt-1">Variance Contribution: {data.pct}%</div>
                    </div>
                  )
                }
                return null
              }}
            />
            <ReferenceLine x={0} stroke="#64748b" strokeWidth={1.5} />
            <Bar dataKey="impact" radius={[4, 4, 4, 4]}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.impact >= 0 ? '#f43f5e' : '#10b981'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Driver Breakdown Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <div className="bg-rose-500/5 rounded-xl border border-rose-500/20 p-4">
          <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-semibold text-sm mb-2">
            <TrendingUp className="w-4 h-4" />
            Top Primary Risk Drivers
          </div>
          <div className="space-y-2">
            {positiveDrivers.slice(0, 3).map((d, i) => (
              <div key={i} className="flex justify-between items-center text-xs">
                <span className="text-slate-700 dark:text-slate-300 font-medium">{d.label}</span>
                <span className="text-rose-600 dark:text-rose-400 font-bold">+{d.contribution_pct}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-emerald-500/5 rounded-xl border border-emerald-500/20 p-4">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-semibold text-sm mb-2">
            <TrendingDown className="w-4 h-4" />
            Active Protective Mitigators
          </div>
          <div className="space-y-2">
            {protectiveDrivers.slice(0, 3).map((d, i) => (
              <div key={i} className="flex justify-between items-center text-xs">
                <span className="text-slate-700 dark:text-slate-300 font-medium">{d.label}</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-bold">-{d.contribution_pct}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
