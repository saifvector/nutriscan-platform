import React, { useState } from 'react'
import { ExternalLink, ShieldCheck, BookOpen, AlertCircle, Search, Filter, Database, AlertOctagon } from 'lucide-react'

export interface EvidenceItem {
  nutrient: string
  evidence_title: string
  evidence_source: string
  evidence_strength: 'GRADE_A' | 'GRADE_B' | 'GRADE_C'
  reference_url: string
  pmid_or_fdc_id?: string
  study_type: string
  key_findings: string
  recommended_daily_intake: string
  tolerable_upper_limit?: string
}

interface ClinicalEvidencePanelProps {
  evidenceItems: EvidenceItem[]
  selectedTarget?: string
}

export const ClinicalEvidencePanel: React.FC<ClinicalEvidencePanelProps> = ({
  evidenceItems = [],
  selectedTarget
}) => {
  const [nutrientFilter, setNutrientFilter] = useState<string>('ALL')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [selectedGrade, setSelectedGrade] = useState<string>('ALL')

  // Extract unique nutrients safely
  const nutrients = ['ALL', ...Array.from(new Set(evidenceItems.map(item => item?.nutrient).filter(Boolean)))]

  // Filtered evidence
  const filteredItems = evidenceItems.filter(item => {
    if (!item) return false
    const matchesNutrient = nutrientFilter === 'ALL' || item.nutrient === nutrientFilter
    const matchesGrade = selectedGrade === 'ALL' || item.evidence_strength === selectedGrade
    const q = searchQuery.toLowerCase()
    const matchesSearch =
      searchQuery === '' ||
      (item.evidence_title && item.evidence_title.toLowerCase().includes(q)) ||
      (item.key_findings && item.key_findings.toLowerCase().includes(q)) ||
      (item.nutrient && item.nutrient.toLowerCase().includes(q)) ||
      (item.study_type && item.study_type.toLowerCase().includes(q))
    return matchesNutrient && matchesGrade && matchesSearch
  })

  const getGradeBadge = (grade: string) => {
    switch (grade) {
      case 'GRADE_A':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-3.5 h-3.5" /> Grade A (Gold Standard)
          </span>
        )
      case 'GRADE_B':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
            <BookOpen className="w-3.5 h-3.5" /> Grade B (Cohort Consensus)
          </span>
        )
      case 'GRADE_C':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            <AlertCircle className="w-3.5 h-3.5" /> Grade C (Mechanistic)
          </span>
        )
    }
  }

  return (
    <div className="bg-white/90 dark:bg-slate-900/90 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-teal-600 dark:text-teal-400" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              Clinical Evidence & Literature Engine
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Ground-truth references linked directly to NIH Office of Dietary Supplements, USDA FoodData Central, and WHO / Endocrine Society guidelines.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {['ALL', 'GRADE_A', 'GRADE_B', 'GRADE_C'].map(grade => (
            <button
              key={grade}
              onClick={() => setSelectedGrade(grade)}
              className={`px-2.5 py-1 text-xs font-medium rounded-lg transition-all ${
                selectedGrade === grade
                  ? 'bg-teal-600 text-white shadow-sm font-semibold'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              {grade === 'ALL' ? 'All Grades' : grade.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3 mb-6">
        <div className="relative md:col-span-8">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search evidence by nutrient, finding, or guideline..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-xs md:text-sm rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500"
          />
        </div>
        <div className="relative md:col-span-4">
          <Filter className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <select
            value={nutrientFilter}
            onChange={e => setNutrientFilter(e.target.value)}
            className="w-full pl-9 pr-8 py-2 text-xs md:text-sm rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 appearance-none cursor-pointer font-medium"
          >
            {nutrients.map(n => (
              <option key={n} value={n}>
                {n === 'ALL' ? 'All Nutrients' : n}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Evidence Cards */}
      {filteredItems.length === 0 ? (
        <div className="py-12 text-center text-slate-500 dark:text-slate-400 text-sm">
          No clinical evidence items match the specified filters.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredItems.map((item, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-200/90 dark:border-slate-800/90 bg-slate-50/50 dark:bg-slate-800/30 hover:border-teal-500/40 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="px-2 py-0.5 rounded text-[11px] font-bold tracking-wider uppercase bg-teal-500/10 text-teal-700 dark:text-teal-300 border border-teal-500/20">
                    {item.nutrient}
                  </span>
                  {getGradeBadge(item.evidence_strength)}
                  <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                    {item.study_type}
                  </span>
                </div>
                {item.reference_url && (
                  <a
                    href={item.reference_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 transition-colors self-start sm:self-auto"
                  >
                    Scientific Citation <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-1.5">
                {item.evidence_title}
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
                {item.key_findings}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 p-2.5 rounded-lg bg-white/80 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800/60 text-xs mb-3">
                <div>
                  <span className="text-slate-400 text-[11px] block">Recommended Intake:</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200">{item.recommended_daily_intake}</span>
                </div>
                {item.tolerable_upper_limit && (
                  <div>
                    <span className="text-amber-600 dark:text-amber-400 text-[11px] font-bold flex items-center gap-1">
                      <AlertOctagon className="w-3 h-3" /> Upper Limit (UL):
                    </span>
                    <span className="font-medium text-slate-700 dark:text-slate-300">{item.tolerable_upper_limit}</span>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center justify-between gap-2 pt-2.5 border-t border-slate-200/60 dark:border-slate-700/60 text-[11px] text-slate-500 dark:text-slate-400">
                <span>Source Authority: <strong className="text-slate-700 dark:text-slate-200">{item.evidence_source}</strong></span>
                {item.pmid_or_fdc_id && (
                  <span className="font-mono bg-slate-200/60 dark:bg-slate-700/60 px-1.5 py-0.5 rounded">
                    {item.pmid_or_fdc_id}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
