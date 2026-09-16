import { useState } from 'react';
import {
  BookOpen, Send, Sparkles, Check, AlertCircle, Droplets,
  Sun, Moon, Pill, Utensils
} from 'lucide-react';
import { outcomesApi } from './outcomesApi';

interface Props {
  assessmentId: string;
  onEntryLogged?: () => void;
}

const SYMPTOM_LIST = [
  'Fatigue',
  'Brain Fog',
  'Hair Loss',
  'Muscle Weakness',
  'Bone Pain',
  'Poor Immunity',
  'Dry Skin',
  'Tingling / Neuropathy',
  'Sleep Fragmentation'
];

export default function RecoveryJournal({ assessmentId, onEntryLogged }: Props) {
  const [logDate, setLogDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [mealsAdhered, setMealsAdhered] = useState<boolean>(true);
  const [supplementsTaken, setSupplementsTaken] = useState<boolean>(true);
  const [waterGlasses, setWaterGlasses] = useState<number>(8);
  const [sunlightMinutes, setSunlightMinutes] = useState<number>(25);
  const [sleepHours, setSleepHours] = useState<number>(7.5);
  const [notes, setNotes] = useState<string>('');

  const [symptoms, setSymptoms] = useState<Record<string, number>>({
    'Fatigue': 3.0,
    'Brain Fog': 2.0,
    'Hair Loss': 3.5,
    'Muscle Weakness': 2.0,
    'Bone Pain': 1.0,
    'Poor Immunity': 2.5,
    'Dry Skin': 2.0,
    'Tingling / Neuropathy': 1.5,
    'Sleep Fragmentation': 2.0
  });

  const [submitting, setSubmitting] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSymptomChange = (symp: string, val: number) => {
    setSymptoms(prev => ({ ...prev, [symp]: val }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      // 1. Log adherence metrics
      await outcomesApi.logAdherence({
        assessment_id: assessmentId,
        log_date: logDate,
        meal_adherence_pct: mealsAdhered ? 100.0 : 40.0,
        supplement_adherence_pct: supplementsTaken ? 100.0 : 30.0,
        lifestyle_adherence_pct: 85.0,
        hydration_liters: Number((waterGlasses * 0.24).toFixed(1)),
        sunlight_minutes: sunlightMinutes,
        sleep_hours: sleepHours,
        exercise_minutes: 30,
        notes,
      });

      // 2. Log symptom journal ratings
      await outcomesApi.logSymptoms({
        assessment_id: assessmentId,
        recorded_date: logDate,
        symptoms,
        notes,
      });

      setSuccessMessage('Recovery session and adherence logged successfully into clinical graph!');
      if (onEntryLogged) onEntryLogged();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit log entry.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl">
        <div className="p-2.5 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
          <BookOpen size={22} />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white tracking-tight">Clinical Recovery Journal</h3>
          <p className="text-xs text-slate-400">Log daily micro-outcomes, symptom progression, and compliance signals</p>
        </div>
      </div>

      {successMessage && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-medium animate-fadeIn">
          <Check size={16} />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-medium animate-fadeIn">
          <AlertCircle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Main Journal Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Column: Habits & Protocols */}
          <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-5">
            <h4 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Sparkles size={16} className="text-teal-400" />
              Daily Protocol Checklist
            </h4>

            {/* Date Picker */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400">Log Date</label>
              <input
                type="date"
                value={logDate}
                onChange={e => setLogDate(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-teal-500"
              />
            </div>

            {/* Checkboxes for Core Protocols */}
            <div className="grid grid-cols-2 gap-3 pt-1">
              <button
                type="button"
                onClick={() => setMealsAdhered(!mealsAdhered)}
                className={`flex items-center gap-2.5 p-3 rounded-xl border text-xs font-medium transition-all ${
                  mealsAdhered
                    ? 'bg-teal-500/15 border-teal-500/40 text-teal-300 shadow-sm'
                    : 'bg-slate-800/40 border-slate-700/50 text-slate-400'
                }`}
              >
                <Utensils size={15} className={mealsAdhered ? 'text-teal-400' : 'text-slate-500'} />
                <span>Meals Followed</span>
              </button>

              <button
                type="button"
                onClick={() => setSupplementsTaken(!supplementsTaken)}
                className={`flex items-center gap-2.5 p-3 rounded-xl border text-xs font-medium transition-all ${
                  supplementsTaken
                    ? 'bg-teal-500/15 border-teal-500/40 text-teal-300 shadow-sm'
                    : 'bg-slate-800/40 border-slate-700/50 text-slate-400'
                }`}
              >
                <Pill size={15} className={supplementsTaken ? 'text-teal-400' : 'text-slate-500'} />
                <span>Supplements Taken</span>
              </button>
            </div>

            {/* Metric Sliders */}
            <div className="space-y-4 pt-2">
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-slate-300">
                    <Droplets size={14} className="text-cyan-400" />
                    Hydration Target
                  </span>
                  <span className="font-semibold text-cyan-300">{waterGlasses} glasses (8 oz)</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="16"
                  step="1"
                  value={waterGlasses}
                  onChange={e => setWaterGlasses(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-slate-300">
                    <Sun size={14} className="text-amber-400" />
                    Direct Sunlight Exposure
                  </span>
                  <span className="font-semibold text-amber-300">{sunlightMinutes} mins</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="90"
                  step="5"
                  value={sunlightMinutes}
                  onChange={e => setSunlightMinutes(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-400"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-slate-300">
                    <Moon size={14} className="text-indigo-400" />
                    Sleep Duration
                  </span>
                  <span className="font-semibold text-indigo-300">{sleepHours} hours</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="12"
                  step="0.5"
                  value={sleepHours}
                  onChange={e => setSleepHours(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-400"
                />
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-1.5 pt-2">
              <label className="text-xs font-medium text-slate-400">Clinical Observations & Subjective Notes</label>
              <textarea
                rows={3}
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder="E.g., Felt noticeably less afternoon fatigue after consistent B12 repletion..."
                className="w-full px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-teal-500 resize-none"
              />
            </div>
          </div>

          {/* Right Column: 9-Symptom Severity Scoring */}
          <div className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-slate-200">9-Symptom Severity Gauge</h4>
              <span className="text-[11px] text-slate-400 font-medium">Scale: 0 (None) to 10 (Severe)</span>
            </div>

            <div className="space-y-3.5 max-h-[420px] overflow-y-auto pr-1">
              {SYMPTOM_LIST.map(symp => {
                const val = symptoms[symp] ?? 0;
                return (
                  <div key={symp} className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/30 space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-200">{symp}</span>
                      <span className={`font-bold px-2 py-0.5 rounded text-[11px] ${
                        val <= 2 ? 'bg-emerald-500/15 text-emerald-300' :
                        val <= 5 ? 'bg-teal-500/15 text-teal-300' :
                        val <= 7 ? 'bg-amber-500/15 text-amber-300' :
                        'bg-rose-500/15 text-rose-300'
                      }`}>
                        {val.toFixed(1)} / 10
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="10"
                      step="0.5"
                      value={val}
                      onChange={e => handleSymptomChange(symp, parseFloat(e.target.value))}
                      className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-teal-400"
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white text-xs font-bold tracking-wide shadow-lg shadow-teal-500/20 disabled:opacity-50 transition-all cursor-pointer"
          >
            {submitting ? (
              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <Send size={15} />
            )}
            <span>RECORD RECOVERY SESSION</span>
          </button>
        </div>
      </form>
    </div>
  );
}
