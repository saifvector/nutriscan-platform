import { useState, useEffect } from 'react';
import {
  Sliders, Sparkles, ArrowRight, RefreshCw,
  CheckCircle2, ShieldCheck, AlertCircle
} from 'lucide-react';
import type { AdaptivePlanResponse } from './types';
import { outcomesApi } from './outcomesApi';

interface Props {
  assessmentId: string;
}

export default function AdaptiveRecommendationCenter({ assessmentId }: Props) {
  const [activePlan, setActivePlan] = useState<AdaptivePlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<string>('FISH_AVOIDANCE');

  const loadPlans = async () => {
    setLoading(true);
    try {
      const res = await outcomesApi.getAdaptivePlans(assessmentId);
      setActivePlan(res);
    } catch (err) {
      console.error('Failed to load adaptive plans', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlans();
  }, [assessmentId]);

  const handleGenerateAdaptation = async (scenario?: string) => {
    setGenerating(true);
    try {
      const newPlan = await outcomesApi.generateAdaptation(assessmentId, scenario || selectedScenario);
      setActivePlan(newPlan);
    } catch (err) {
      console.error('Failed to generate adaptation', err);
    } finally {
      setGenerating(false);
    }
  };

  if (loading && !activePlan) {
    return (
      <div className="p-8 text-center text-slate-400">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full mb-3" />
        <p className="text-sm font-medium">Formulating Adaptive Clinical Protocol...</p>
      </div>
    );
  }

  const adaptations = activePlan?.active_adaptations ?? [];

  return (
    <div className="space-y-6">
      {/* Header with Generator Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
            <Sliders size={22} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Adaptive Recommendation Engine</h3>
            <p className="text-xs text-slate-400">Closed-loop dynamic adjustments based on real-time clinical biomarkers and adherence rates</p>
          </div>
        </div>

        {/* Dynamic Scenario Trigger Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedScenario}
            onChange={e => setSelectedScenario(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
          >
            <option value="FISH_AVOIDANCE">Scenario A: Fish / Seafood Avoidance</option>
            <option value="SUNLIGHT_FAILURE">Scenario B: Sunlight Failure / Low D3</option>
            <option value="SUPPLEMENT_RESISTANCE">Scenario C: Supplement Fatigue / Resistance</option>
          </select>

          <button
            onClick={() => handleGenerateAdaptation()}
            disabled={generating}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white text-xs font-bold shadow-lg shadow-teal-500/20 disabled:opacity-50 transition-all cursor-pointer"
          >
            {generating ? (
              <RefreshCw size={14} className="animate-spin" />
            ) : (
              <Sparkles size={14} />
            )}
            <span>Synthesize Adaptation</span>
          </button>
        </div>
      </div>

      {activePlan && (
        <div className="space-y-6">
          {/* Adaptations List */}
          {adaptations.map((adapt, idx) => (
            <div key={idx} className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="text-base font-bold text-white tracking-tight">
                      {adapt.scenario_category.replace(/_/g, ' ')}
                    </h4>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-teal-500/15 text-teal-300 border border-teal-500/30">
                      ACTIVE ADAPTATION
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Adaptation ID: <span className="font-mono text-slate-300">{adapt.adaptation_id.substring(0, 16)}...</span>
                  </p>
                </div>

                <div className="flex items-center gap-2 text-xs text-purple-300 bg-purple-500/10 border border-purple-500/20 px-3 py-1.5 rounded-xl font-medium">
                  <ShieldCheck size={14} />
                  <span>Acceleration: {adapt.expected_recovery_acceleration}</span>
                </div>
              </div>

              {/* Trigger Reason */}
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40 space-y-1.5">
                <div className="flex items-center gap-2 text-teal-400 text-xs font-bold">
                  <AlertCircle size={15} />
                  <span>Clinical Trigger Reason</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {adapt.trigger_reason}
                </p>
              </div>

              {/* Original vs Adapted Guidance Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-800/20 border border-slate-700/30 space-y-2">
                  <span className="text-xs font-bold text-slate-400">Original Prescribed Protocol</span>
                  <p className="text-xs text-slate-300 line-through decoration-slate-600 leading-relaxed">
                    {adapt.original_guidance}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-teal-950/20 border border-teal-800/40 space-y-2">
                  <span className="text-xs font-bold text-teal-300 flex items-center gap-1.5">
                    <ArrowRight size={14} />
                    Adapted Dynamic Protocol
                  </span>
                  <p className="text-xs text-white font-medium leading-relaxed">
                    {adapt.adapted_guidance}
                  </p>
                </div>
              </div>

              {/* Alternative Interventions & Clinical Logic */}
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <span className="text-xs font-bold text-slate-300">Alternative Interventions Deployed</span>
                <div className="flex flex-wrap gap-2">
                  {adapt.alternative_interventions.map((item, aIdx) => (
                    <span
                      key={aIdx}
                      className="px-3 py-1 rounded-lg bg-teal-950/40 border border-teal-800/40 text-xs text-teal-300 font-medium"
                    >
                      ✓ {item}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-slate-400 italic pt-2">
                  Clinical Logic: {adapt.adaptation_logic}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
