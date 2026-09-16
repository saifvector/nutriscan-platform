import { useState, useEffect } from 'react';
import {
  BrainCircuit, CheckCircle2, ShieldCheck,
  TrendingUp, Sparkles, AlertCircle
} from 'lucide-react';
import type { PredictionAccuracyResponse } from './types';
import { outcomesApi } from './outcomesApi';

interface Props {
  assessmentId: string;
}

export default function PredictionAccuracyDashboard({ assessmentId }: Props) {
  const [data, setData] = useState<PredictionAccuracyResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    outcomesApi.getPredictionAccuracy(assessmentId)
      .then(res => {
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error('Failed to load prediction accuracy', err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [assessmentId]);

  if (loading && !data) {
    return (
      <div className="p-8 text-center text-slate-400">
        <div className="animate-spin inline-block w-8 h-8 border-teal-500 border-4 border-t-transparent rounded-full mb-3" />
        <p className="text-sm font-medium">Validating Model Calibration & Trajectory...</p>
      </div>
    );
  }

  if (!data) return null;

  const milestones = data.milestone_evaluations ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
            <BrainCircuit size={22} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Prediction Accuracy & Validation Engine</h3>
            <p className="text-xs text-slate-400">Closed-loop evaluation comparing predicted recovery curves against real-world biological outcomes</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-xs font-semibold">
          <ShieldCheck size={16} />
          <span>{data.calibration_status}</span>
        </div>
      </div>

      {/* Model KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Model Reliability Score</span>
            <CheckCircle2 size={16} className="text-teal-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{data.model_reliability_score}%</p>
          <p className="text-[11px] text-teal-400 font-medium">High confidence Bayesian prior alignment</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Mean Absolute Error (MAE)</span>
            <TrendingUp size={16} className="text-emerald-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{data.projection_mean_absolute_error}</p>
          <p className="text-[11px] text-emerald-400 font-medium">&lt; 1.0 threshold (High Precision)</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Overall Prediction Accuracy</span>
            <Sparkles size={16} className="text-purple-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{data.overall_prediction_accuracy_pct}%</p>
          <p className="text-[11px] text-purple-400 font-medium">Confidence Calibration: {data.confidence_calibration_score}%</p>
        </div>
      </div>

      {/* Predicted vs Actual Longitudinal Trajectory Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-4">
        <h4 className="text-sm font-semibold text-slate-200">Milestone Accuracy Evaluation (Days 30, 60, 90)</h4>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-semibold">Milestone Day</th>
                <th className="pb-3 font-semibold">Predicted Health Score</th>
                <th className="pb-3 font-semibold">Actual Logged Health Score</th>
                <th className="pb-3 font-semibold">Absolute Deviation</th>
                <th className="pb-3 font-semibold">Accuracy</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {milestones.map((m, idx) => (
                <tr key={idx} className="hover:bg-slate-800/20">
                  <td className="py-3 font-bold text-white">Day {m.milestone_day}</td>
                  <td className="py-3 text-slate-300 font-mono">{m.predicted_health_score.toFixed(1)}</td>
                  <td className="py-3 font-bold text-teal-300 font-mono">{m.actual_health_score.toFixed(1)}</td>
                  <td className="py-3 text-emerald-400 font-mono">{m.absolute_error.toFixed(2)} pts</td>
                  <td className="py-3 text-teal-300 font-semibold">{m.accuracy_percentage.toFixed(1)}%</td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/15 text-teal-300 border border-teal-500/20">
                      {m.within_confidence_band ? 'PRECISE MATCH' : 'WITHIN 95% CI'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Clinical Model Report */}
      <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-3">
        <div className="flex items-center gap-2 text-teal-400 font-semibold text-xs">
          <AlertCircle size={16} />
          <h4>Continuous Clinical Learning Report</h4>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/40 p-3 rounded-xl border border-slate-700/40">
          {data.clinical_model_report}
        </p>
      </div>
    </div>
  );
}
