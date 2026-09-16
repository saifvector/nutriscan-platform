import { useState, useEffect } from 'react';
import {
  Zap, AlertTriangle, ArrowUpRight, Award,
  Sparkles, Layers
} from 'lucide-react';
import type { EffectivenessResponse } from './types';
import { outcomesApi } from './outcomesApi';

interface Props {
  assessmentId: string;
}

export default function EffectivenessCenter({ assessmentId }: Props) {
  const [data, setData] = useState<EffectivenessResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    outcomesApi.getEffectiveness(assessmentId)
      .then(res => {
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error('Failed to load effectiveness report', err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [assessmentId]);

  if (loading && !data) {
    return (
      <div className="p-8 text-center text-slate-400">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full mb-3" />
        <p className="text-sm font-medium">Evaluating Intervention Effectiveness...</p>
      </div>
    );
  }

  if (!data) return null;

  const accelerators = data.recovery_accelerators ?? [];
  const bottlenecks = data.recovery_bottlenecks ?? [];

  return (
    <div className="space-y-6">
      {/* Header with Effectiveness KPI */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
            <Zap size={22} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Intervention Effectiveness Center</h3>
            <p className="text-xs text-slate-400">Causal attribution of foods, supplements & habits to clinical progress</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-300">
          <Award size={18} />
          <span className="text-xs font-semibold">Protocol Effectiveness:</span>
          <span className="text-base font-extrabold text-white">{data.overall_effectiveness_score}%</span>
        </div>
      </div>

      {/* Accelerators vs Bottlenecks Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Accelerators */}
        <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
              <Sparkles size={18} />
              <h4>Top Clinical Accelerators ({accelerators.length})</h4>
            </div>
            <span className="text-[11px] text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
              High Impact
            </span>
          </div>

          <div className="space-y-3">
            {accelerators.map((acc, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/40 hover:border-emerald-700/60 transition-all space-y-2"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h5 className="text-xs font-bold text-white flex items-center gap-1.5">
                      {acc.name}
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-mono">
                        {acc.intervention_type}
                      </span>
                    </h5>
                    <p className="text-[11px] text-emerald-400 font-medium mt-0.5">
                      Target: {acc.target_deficiency}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 text-emerald-300 font-bold text-xs bg-emerald-500/20 px-2 py-0.5 rounded-lg">
                    <ArrowUpRight size={13} />
                    +{acc.recovery_contribution_score}%
                  </div>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-300 pt-1">
                  <span>Adherence: <strong className="text-white">{acc.adherence_rate}%</strong></span>
                  <span className="text-emerald-300">Response: <strong>{acc.response_rate}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottlenecks & Friction Points */}
        <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
              <AlertTriangle size={18} />
              <h4>Protocol Friction & Bottlenecks ({bottlenecks.length})</h4>
            </div>
            <span className="text-[11px] text-amber-400 font-semibold bg-amber-500/10 px-2.5 py-0.5 rounded-full border border-amber-500/20">
              Optimization Needed
            </span>
          </div>

          <div className="space-y-3">
            {bottlenecks.map((bot, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/40 hover:border-amber-700/60 transition-all space-y-2"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h5 className="text-xs font-bold text-white flex items-center gap-1.5">
                      {bot.name}
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-mono">
                        {bot.intervention_type}
                      </span>
                    </h5>
                    <p className="text-[11px] text-amber-400 font-medium mt-0.5">
                      Target: {bot.target_deficiency}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 text-amber-300 font-bold text-xs bg-amber-500/20 px-2 py-0.5 rounded-lg">
                    <span>{bot.recovery_contribution_score}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-300 pt-1">
                  <span>Adherence: <strong className="text-white">{bot.adherence_rate}%</strong></span>
                  <span className="text-amber-300">Response: <strong>{bot.response_rate}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Intervention Response Summary & Insights */}
      <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-3">
        <h4 className="text-xs font-bold text-slate-200 flex items-center gap-2">
          <Layers size={15} className="text-teal-400" />
          Clinical Intervention Response Summary
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/40 p-3 rounded-xl border border-slate-700/40">
          {data.intervention_response_summary}
        </p>
      </div>
    </div>
  );
}
