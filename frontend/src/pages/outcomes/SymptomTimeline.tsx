import { useState, useEffect } from 'react';
import {
  TrendingDown, CheckCircle, Activity,
  Calendar, Award, FlaskConical, Sparkles
} from 'lucide-react';
import type { SymptomTimelineResponse, LabTrackingResponse, SymptomProgressItem } from './types';
import { outcomesApi } from './outcomesApi';

interface Props {
  assessmentId: string;
}

export default function SymptomTimeline({ assessmentId }: Props) {
  const [timeline, setTimeline] = useState<SymptomTimelineResponse | null>(null);
  const [labs, setLabs] = useState<LabTrackingResponse | null>(null);
  const [activeSubTab, setActiveSubTab] = useState<'symptoms' | 'labs'>('symptoms');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    Promise.all([
      outcomesApi.getSymptoms(assessmentId),
      outcomesApi.getLabs(assessmentId),
    ])
      .then(([sympRes, labRes]) => {
        if (mounted) {
          setTimeline(sympRes);
          setLabs(labRes);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error('Failed to load timeline or labs', err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [assessmentId]);

  if (loading && !timeline) {
    return (
      <div className="p-8 text-center text-slate-400">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full mb-3" />
        <p className="text-sm font-medium">Synthesizing Recovery Trajectory...</p>
      </div>
    );
  }

  if (!timeline) return null;

  const symptoms = timeline.symptom_progress ?? [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'RESOLVED':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">RESOLVED</span>;
      case 'IMPROVING':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/15 text-teal-300 border border-teal-500/30">IMPROVING</span>;
      case 'PLATEAU':
      case 'STABLE':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">PLATEAU</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/15 text-rose-300 border border-rose-500/30">DECLINING</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Sub-tab Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
            <Activity size={22} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Longitudinal Outcome Trajectory</h3>
            <p className="text-xs text-slate-400">Baseline vs. Current clinical progression across 9 symptoms and 8 biomarkers</p>
          </div>
        </div>

        <div className="flex rounded-xl p-1 bg-slate-800/80 border border-slate-700/60">
          <button
            onClick={() => setActiveSubTab('symptoms')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeSubTab === 'symptoms'
                ? 'bg-teal-500 text-white shadow-md shadow-teal-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <TrendingDown size={14} />
            <span>Symptom Progression</span>
          </button>
          <button
            onClick={() => setActiveSubTab('labs')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeSubTab === 'labs'
                ? 'bg-teal-500 text-white shadow-md shadow-teal-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FlaskConical size={14} />
            <span>Laboratory Biomarkers</span>
          </button>
        </div>
      </div>

      {activeSubTab === 'symptoms' ? (
        <div className="space-y-6">
          {/* Recovery Velocity Summary Banner */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 flex items-center gap-3">
              <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
                <TrendingDown size={20} />
              </div>
              <div>
                <p className="text-[11px] text-slate-400 font-medium">Symptom Recovery Score</p>
                <p className="text-sm font-bold text-white">{timeline.symptom_recovery_score}%</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                <CheckCircle size={20} />
              </div>
              <div>
                <p className="text-[11px] text-slate-400 font-medium">Symptoms Resolved</p>
                <p className="text-sm font-bold text-emerald-400">
                  {timeline.resolved_count} of {timeline.symptoms_tracked_count} items
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                <Calendar size={20} />
              </div>
              <div>
                <p className="text-[11px] text-slate-400 font-medium">Resolution Trajectory</p>
                <p className="text-sm font-bold text-purple-300">~28 Days to Full Saturation</p>
              </div>
            </div>
          </div>

          {/* 9-Symptom Progression Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {symptoms.map((s: SymptomProgressItem) => {
              const baselinePct = (s.baseline_severity / 10) * 100;
              const currentPct = (s.current_severity / 10) * 100;
              const status = s.status ?? 'IMPROVING';

              return (
                <div
                  key={s.symptom_name}
                  className="p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-lg space-y-3 relative overflow-hidden"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-white">{s.symptom_name}</h4>
                      <p className="text-[11px] text-slate-400">
                        Velocity: -{(s.weekly_recovery_velocity ?? 0.65).toFixed(2)} pts/wk
                      </p>
                    </div>
                    {getStatusBadge(status)}
                  </div>

                  {/* Dual Bar Comparison */}
                  <div className="space-y-1.5 pt-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-400">Baseline: {s.baseline_severity.toFixed(1)}</span>
                      <span className="text-teal-300 font-semibold">Current: {s.current_severity.toFixed(1)}</span>
                    </div>

                    <div className="relative w-full h-3 rounded-full bg-slate-800 overflow-hidden">
                      {/* Baseline Ghost Bar */}
                      <div
                        className="absolute h-full bg-slate-700/60 rounded-full"
                        style={{ width: `${baselinePct}%` }}
                      />
                      {/* Current Solid Bar */}
                      <div
                        className="absolute h-full bg-gradient-to-r from-teal-500 to-emerald-400 rounded-full transition-all duration-700"
                        style={{ width: `${currentPct}%` }}
                      />
                    </div>
                  </div>

                  {/* Resolution Estimate / Stats Footer */}
                  <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800/60">
                    <span className="font-semibold text-emerald-400">
                      ↓ {(s.percentage_improvement ?? 50).toFixed(1)}% improvement
                    </span>
                    <span className="text-slate-400">
                      {!s.forecast_days_to_resolution || s.forecast_days_to_resolution === 0
                        ? 'Completely cleared'
                        : `~${s.forecast_days_to_resolution} days left`}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* Laboratory Biomarkers View */
        <div className="space-y-6">
          {labs && (
            <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-teal-400 text-sm font-semibold">
                  <Award size={18} />
                  <span>Clinical Lab Adequacy Score: {labs.overall_lab_adequacy_score}%</span>
                </div>
                <span className="text-xs text-slate-400">Panel Date: {labs.test_date}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/40 p-3 rounded-xl border border-slate-700/40">
                <span className="font-semibold text-teal-300">Interpretation: </span>
                {labs.clinical_interpretation}
              </p>

              {/* Biomarkers Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-3 font-semibold">Biomarker</th>
                      <th className="pb-3 font-semibold">Baseline</th>
                      <th className="pb-3 font-semibold">Current</th>
                      <th className="pb-3 font-semibold">Optimal Range</th>
                      <th className="pb-3 font-semibold">Delta</th>
                      <th className="pb-3 font-semibold">Status</th>
                      <th className="pb-3 font-semibold">Clinical Significance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {labs.biomarkers.map((b, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/20">
                        <td className="py-3 font-bold text-white flex items-center gap-1.5">
                          <Sparkles size={12} className="text-teal-400" />
                          {b.biomarker_name}
                        </td>
                        <td className="py-3 text-slate-400">{b.baseline_value} {b.unit}</td>
                        <td className="py-3 font-bold text-teal-300">{b.current_value} {b.unit}</td>
                        <td className="py-3 text-slate-400">{b.optimal_range} {b.unit}</td>
                        <td className="py-3 font-semibold text-emerald-400">
                          {b.delta_value > 0 ? `+${b.delta_value}` : b.delta_value} ({b.percentage_change > 0 ? `+${b.percentage_change}%` : `${b.percentage_change}%`})
                        </td>
                        <td className="py-3">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            b.status === 'OPTIMAL' || b.status === 'NORMAL'
                              ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20'
                              : 'bg-teal-500/15 text-teal-300 border border-teal-500/20'
                          }`}>
                            {b.status}
                          </span>
                        </td>
                        <td className="py-3 text-slate-300 max-w-xs">{b.clinical_significance}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
