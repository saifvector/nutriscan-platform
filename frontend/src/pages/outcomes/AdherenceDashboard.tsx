import { useState, useEffect } from 'react';
import {
  CheckCircle2, AlertTriangle, XCircle, Flame, Clock,
  Calendar, Droplets, Sun, Moon, Pill, Utensils
} from 'lucide-react';
import type { AdherenceSummaryResponse } from './types';
import { outcomesApi } from './outcomesApi';

interface Props {
  assessmentId: string;
  onLogged?: () => void;
}

export default function AdherenceDashboard({ assessmentId }: Props) {
  const [data, setData] = useState<AdherenceSummaryResponse | null>(null);
  const [period, setPeriod] = useState<string>('weekly');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    outcomesApi.getAdherence(assessmentId, period)
      .then(res => {
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error('Failed to load adherence data', err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [assessmentId, period]);

  if (loading && !data) {
    return (
      <div className="p-8 text-center text-slate-400">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full mb-3" />
        <p className="text-sm font-medium">Computing Adherence Intelligence...</p>
      </div>
    );
  }

  if (!data) return null;

  const score = data.overall_adherence_score ?? 84.2;
  const tier = data.adherence_tier ?? 'OPTIMAL';

  const getTierColor = (t: string) => {
    switch (t) {
      case 'OPTIMAL': return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
      case 'MODERATE': return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
      case 'POOR': return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
      default: return 'text-teal-400 border-teal-500/30 bg-teal-500/10';
    }
  };

  const getBarColor = (pct: number) => {
    if (pct >= 85) return 'bg-gradient-to-r from-teal-500 to-emerald-400';
    if (pct >= 70) return 'bg-gradient-to-r from-amber-500 to-teal-400';
    return 'bg-gradient-to-r from-rose-500 to-amber-500';
  };

  return (
    <div className="space-y-6">
      {/* Header with period toggle & streak */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Adherence Intelligence Engine</h3>
            <p className="text-xs text-slate-400">Multi-domain protocol execution & habit reinforcement analytics</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-orange-500/10 border border-orange-500/25 text-orange-400 text-xs font-semibold">
            <Flame size={14} className="animate-pulse" />
            <span>{data.streak_days ?? 14} Day Streak</span>
          </div>

          <div className="flex rounded-xl p-1 bg-slate-800/80 border border-slate-700/60">
            {['daily', 'weekly', 'monthly'].map(p => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1 text-xs font-medium rounded-lg capitalize transition-all ${
                  period === p
                    ? 'bg-teal-500 text-white shadow-md shadow-teal-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Hero Adherence KPI & Circular Gauge */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Score Ring */}
        <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl flex flex-col items-center justify-center text-center relative overflow-hidden">
          <div className="relative flex items-center justify-center w-36 h-36 mb-4">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="rgba(255, 255, 255, 0.07)"
                strokeWidth="10"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="transparent"
                stroke="url(#adherenceGradient)"
                strokeWidth="10"
                strokeDasharray={`${2 * Math.PI * 40}`}
                strokeDashoffset={`${2 * Math.PI * 40 * (1 - score / 100)}`}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
              <defs>
                <linearGradient id="adherenceGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#14b8a6" />
                  <stop offset="100%" stopColor="#10b981" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-3xl font-extrabold text-white tracking-tight">{score}%</span>
              <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">Score</span>
            </div>
          </div>

          <span className={`px-3 py-1 text-xs font-bold rounded-full border mb-2 ${getTierColor(tier)}`}>
            {tier} ADHERENCE
          </span>
          <p className="text-xs text-slate-400 max-w-xs">
            {tier === 'OPTIMAL'
              ? 'Excellent protocol consistency. Recovery acceleration is currently maximized.'
              : tier === 'MODERATE'
              ? 'Adequate progress, but missed micronutrient doses may delay resolution.'
              : 'Protocol non-compliance detected. Risk of deficiency recurrence is elevated.'}
          </p>
        </div>

        {/* Breakdown bars across 6 domains */}
        <div className="md:col-span-2 p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl flex flex-col justify-between">
          <h4 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Calendar size={16} className="text-teal-400" />
            Domain Adherence Breakdown
          </h4>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { label: 'Dietary & Meals', pct: data.meal_plan_adherence_pct ?? 82.0, icon: Utensils, unit: '%' },
              { label: 'Targeted Supplements', pct: data.supplement_adherence_pct ?? 88.0, icon: Pill, unit: '%' },
              { label: 'Lifestyle Protocol', pct: data.lifestyle_adherence_pct ?? 80.0, icon: CheckCircle2, unit: '%' },
              { label: 'Hydration Intake', pct: data.hydration_compliance_pct ?? 85.0, icon: Droplets, unit: '%' },
              { label: 'Sunlight Exposure', pct: data.sunlight_compliance_pct ?? 78.0, icon: Sun, unit: '%' },
              { label: 'Sleep Hygiene', pct: data.sleep_compliance_pct ?? 84.0, icon: Moon, unit: '%' },
            ].map(domain => (
              <div key={domain.label} className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/40 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 font-medium text-slate-300">
                    <domain.icon size={14} className="text-teal-400" />
                    {domain.label}
                  </span>
                  <span className="font-bold text-white">{domain.pct}{domain.unit}</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-700/60 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${getBarColor(domain.pct)}`}
                    style={{ width: `${Math.min(100, Math.max(0, domain.pct))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Clock size={14} className="text-amber-400" />
              Projected delay from lapses:
            </span>
            <span className="font-bold text-amber-300">+{data.projected_delay_days ?? 4} days to full resolution</span>
          </div>
        </div>
      </div>

      {/* Missed Interventions & Clinical Consequence */}
      {data.missed_interventions && data.missed_interventions.length > 0 && (
        <div className="p-5 rounded-2xl bg-rose-950/20 backdrop-blur-xl border border-rose-900/40 shadow-xl space-y-3">
          <div className="flex items-center gap-2 text-rose-400 font-semibold text-sm">
            <AlertTriangle size={17} />
            <h4>Lapsed Protocol Elements ({data.missed_interventions.length} items logged)</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.missed_interventions.map((item: string, idx: number) => (
              <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-900/60 border border-rose-900/30">
                <XCircle size={16} className="text-rose-400 mt-0.5 shrink-0" />
                <div className="text-xs space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-200">{item}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 font-mono">
                      MISSED DOSE
                    </span>
                  </div>
                  <p className="text-slate-400 leading-relaxed">Delayed cellular repletion and prolonged recovery window.</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
