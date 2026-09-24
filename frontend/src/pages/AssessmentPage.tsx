import { useState, useCallback, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence, type Variants } from 'framer-motion'
import {
  ChevronRight,
  ChevronLeft,
  Send,
  User,
  Utensils,
  Activity,
  Heart,
  Stethoscope,
  Pill,
  Search,
  CheckCircle2,
  History,
  AlertCircle
} from 'lucide-react'
import { DIET_PATTERNS, ACTIVITY_LEVELS, SYMPTOM_LIST } from '../lib/constants'
import api from '../lib/api'
import { sessionManager } from '../lib/sessionManager'

const slideVariants: Variants = {
  enter: { opacity: 0, x: 30 },
  center: { opacity: 1, x: 0, transition: { duration: 0.3, ease: 'easeOut' } },
  exit: { opacity: 0, x: -30, transition: { duration: 0.2 } },
}

const STEPS = [
  { label: 'Patient Info', icon: User },
  { label: 'Dietary Habits', icon: Utensils },
  { label: 'Lifestyle', icon: Activity },
  { label: 'Symptoms', icon: Heart },
  { label: 'Medical History', icon: Stethoscope },
  { label: 'Supplements', icon: Pill },
]

function StepIndicator({ current, total }: { current: number; total: number }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 40 }}>
      {STEPS.map((step, i) => (
        <div key={step.label} style={{ display: 'flex', alignItems: 'center', gap: 4, flex: 1 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '8px 14px', borderRadius: 8,
            background: i === current ? 'var(--c-primary)' : i < current ? 'var(--c-surface-tint)' : 'var(--c-card)',
            border: `1px solid ${i === current ? 'var(--c-primary)' : i < current ? 'var(--c-primary)' : 'var(--c-border)'}`,
            transition: 'all 0.2s',
          }}>
            <step.icon size={14} color={i === current ? 'white' : i < current ? 'var(--c-primary)' : 'var(--c-muted)'} />
            <span style={{
              fontSize: '0.75rem', fontWeight: 600,
              color: i === current ? 'white' : i < current ? 'var(--c-primary)' : 'var(--c-muted)',
            }}>
              {step.label}
            </span>
          </div>
          {i < total - 1 && (
            <div style={{ flex: 1, height: 1, background: i < current ? 'var(--c-primary)' : 'var(--c-border)', minWidth: 8 }} />
          )}
        </div>
      ))}
    </div>
  )
}

function FormField({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)', marginBottom: 6 }}>
        {label}
      </label>
      {children}
      {hint && <p style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 4 }}>{hint}</p>}
    </div>
  )
}

function Input({ value, onChange, type = 'text', placeholder, min, max, step }: {
  value: string | number; onChange: (v: string) => void; type?: string; placeholder?: string; min?: number; max?: number; step?: number
}) {
  return (
    <input
      type={type} value={value} placeholder={placeholder} min={min} max={max} step={step}
      onChange={e => onChange(e.target.value)}
      style={{
        width: '100%', padding: '10px 14px', borderRadius: 8,
        border: '1px solid var(--c-input-border)', fontSize: '0.875rem',
        fontFamily: 'var(--font-body)', color: 'var(--c-secondary)',
        background: 'var(--c-input-bg)', outline: 'none', transition: 'border-color 0.15s',
      }}
      onFocus={e => e.target.style.borderColor = 'var(--c-input-focus)'}
      onBlur={e => e.target.style.borderColor = 'var(--c-input-border)'}
    />
  )
}

function Select({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) {
  return (
    <select
      value={value} onChange={e => onChange(e.target.value)}
      style={{
        width: '100%', padding: '10px 14px', borderRadius: 8,
        border: '1px solid var(--c-input-border)', fontSize: '0.875rem',
        fontFamily: 'var(--font-body)', color: 'var(--c-secondary)',
        background: 'var(--c-input-bg)', outline: 'none', cursor: 'pointer',
      }}
    >
      <option value="">Select...</option>
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  )
}

function Slider({ value, onChange, min, max, label }: { value: number; onChange: (v: number) => void; min: number; max: number; label: string }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>{label}</span>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-primary)' }}>{value}</span>
      </div>
      <input
        type="range" min={min} max={max} value={value}
        onChange={e => onChange(parseInt(e.target.value))}
        style={{ width: '100%', accentColor: 'var(--c-primary)' }}
      />
    </div>
  )
}

interface FormData {
  patient_name: string
  patient_id: string
  age: number
  gender: string
  height_cm: number
  weight_kg: number
  dietary_pattern: string
  meals_per_day: number
  water_intake_liters: number
  daily_fruit_vegetable_servings: number
  junk_food_frequency: string
  activity_level: string
  sleep_hours_per_night: number
  smoking_status: string
  alcohol_consumption: string
  sunlight_exposure_min_per_day: number
  stress_level: number
  symptoms: Record<string, number>
  medical_history: { condition_name: string; is_active: boolean; impacts_absorption: boolean }[]
  supplement_usage: { supplement_name: string; dosage: string; frequency: string }[]
}

export default function AssessmentPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [step, setStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const [patientSuggestions, setPatientSuggestions] = useState<any[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [matchedPatientRecord, setMatchedPatientRecord] = useState<any | null>(null)
  const [autoPopulated, setAutoPopulated] = useState(false)
  const searchTimeoutRef = useRef<any>(null)

  const [form, setForm] = useState<FormData>({
    patient_name: '',
    patient_id: '',
    age: 30,
    gender: 'MALE',
    height_cm: 170,
    weight_kg: 70,
    dietary_pattern: 'OMNIVORE',
    meals_per_day: 3,
    water_intake_liters: 2.0,
    daily_fruit_vegetable_servings: 3,
    junk_food_frequency: 'RARELY',
    activity_level: 'MODERATELY_ACTIVE',
    sleep_hours_per_night: 7,
    smoking_status: 'NEVER',
    alcohol_consumption: 'NONE',
    sunlight_exposure_min_per_day: 30,
    stress_level: 5,
    symptoms: {},
    medical_history: [],
    supplement_usage: [],
  })

  const update = useCallback(<K extends keyof FormData>(key: K, val: FormData[K]) => {
    setForm(prev => ({ ...prev, [key]: val }))
  }, [])

  const applyPatientBaseline = useCallback((p: any) => {
    update('patient_id', p.id || '')
    update('patient_name', p.name || '')
    if (p.age) update('age', p.age)
    if (p.gender) update('gender', p.gender)
    if (p.height_cm) update('height_cm', p.height_cm)
    if (p.weight_kg) update('weight_kg', p.weight_kg)
    if (p.dietary_pattern) update('dietary_pattern', p.dietary_pattern)

    const payload = p.latest_payload || {}
    const diet = payload.dietary_habits || {}
    if (diet.meals_per_day) update('meals_per_day', diet.meals_per_day)
    if (diet.water_intake_liters) update('water_intake_liters', diet.water_intake_liters)
    if (diet.daily_fruit_vegetable_servings) update('daily_fruit_vegetable_servings', diet.daily_fruit_vegetable_servings)
    if (diet.junk_food_frequency) update('junk_food_frequency', diet.junk_food_frequency)

    const life = payload.lifestyle_factors || p.lifestyle_factors || {}
    if (life.activity_level) update('activity_level', life.activity_level)
    if (life.sleep_hours_per_night) update('sleep_hours_per_night', life.sleep_hours_per_night)
    if (life.smoking_status) update('smoking_status', life.smoking_status)
    if (life.alcohol_consumption) update('alcohol_consumption', life.alcohol_consumption)
    if (life.sunlight_exposure_min_per_day) update('sunlight_exposure_min_per_day', life.sunlight_exposure_min_per_day)
    if (life.stress_level) update('stress_level', life.stress_level)

    if (Array.isArray(p.medical_history) && p.medical_history.length > 0) {
      update('medical_history', p.medical_history)
    }

    setMatchedPatientRecord(p)
    setAutoPopulated(true)
    setShowSuggestions(false)
  }, [update])

  // Pre-fill from URL query parameters if coming from PatientRecordsPage
  useEffect(() => {
    const urlPid = searchParams.get('patient_id')
    const urlPname = searchParams.get('patient_name')
    if (urlPid) {
      update('patient_id', urlPid)
      if (urlPname) update('patient_name', urlPname)
      api.get(`/patients/${urlPid}`).then(res => {
        if (res.data) {
          applyPatientBaseline(res.data)
        }
      }).catch(err => console.error('Failed to pre-fill patient:', err))
    }
  }, [searchParams, update, applyPatientBaseline])

  // Live search for existing patients as clinician types
  const handlePatientNameChange = (val: string) => {
    update('patient_name', val)
    setMatchedPatientRecord(null)
    setAutoPopulated(false)

    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current)
    if (!val || val.trim().length < 2) {
      setPatientSuggestions([])
      setShowSuggestions(false)
      return
    }

    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const res = await api.get('/patients', { params: { search: val.trim(), limit: 5 } })
        if (Array.isArray(res.data) && res.data.length > 0) {
          setPatientSuggestions(res.data)
          setShowSuggestions(true)
        } else {
          setPatientSuggestions([])
          setShowSuggestions(false)
        }
      } catch (err) {
        console.error('Patient search error:', err)
      }
    }, 250)
  }

  const next = () => setStep(s => Math.min(s + 1, 5))
  const prev = () => setStep(s => Math.max(s - 1, 0))

  const handleSubmit = async () => {
    setSubmitting(true)
    setSubmitError(null)
    try {
      const payload = {
        patient_name: form.patient_name.trim() || undefined,
        patient_id: form.patient_id.trim() || undefined,
        age: Number(form.age),
        gender: form.gender,
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        dietary_habits: {
          dietary_pattern: form.dietary_pattern,
          meals_per_day: Number(form.meals_per_day),
          water_intake_liters: Number(form.water_intake_liters),
          daily_fruit_vegetable_servings: Number(form.daily_fruit_vegetable_servings),
          junk_food_frequency: form.junk_food_frequency,
          dietary_restrictions: [],
        },
        lifestyle_factors: {
          activity_level: form.activity_level,
          sleep_hours_per_night: Number(form.sleep_hours_per_night),
          smoking_status: form.smoking_status,
          alcohol_consumption: form.alcohol_consumption,
          sunlight_exposure_min_per_day: Number(form.sunlight_exposure_min_per_day),
          stress_level: Number(form.stress_level),
        },
        symptoms: form.symptoms,
        medical_history: form.medical_history,
        supplement_usage: form.supplement_usage,
      }
      const res = await api.post('/predict', payload)
      const assessmentId = String(res.data.assessment_id || 'latest')
      sessionManager.setActiveSession(
        assessmentId,
        new Date().toISOString(),
        'completed',
        form.patient_name.trim() || undefined
      )
      navigate(`/dashboard/${assessmentId}`)
    } catch (err: any) {
      console.error('Assessment submission error:', err)
      const rawDetail = err?.response?.data?.detail
      let errorMsg = 'Assessment submission failed. Please verify connection and try again.'
      if (typeof rawDetail === 'string') {
        errorMsg = rawDetail
      } else if (Array.isArray(rawDetail)) {
        errorMsg = rawDetail.map((d: any) => d.msg || JSON.stringify(d)).join(', ')
      } else if (rawDetail && typeof rawDetail === 'object') {
        errorMsg = JSON.stringify(rawDetail)
      } else if (err?.message) {
        errorMsg = err.message
      }
      setSubmitError(errorMsg)
    } finally {
      setSubmitting(false)
    }
  }

  const toggleSymptom = (key: string, severity: number) => {
    setForm(prev => {
      const s = { ...prev.symptoms }
      if (s[key]) { delete s[key] } else { s[key] = severity }
      return { ...prev, symptoms: s }
    })
  }

  const updateSymptomSeverity = (key: string, severity: number) => {
    setForm(prev => ({ ...prev, symptoms: { ...prev.symptoms, [key]: severity } }))
  }

  const steps = [
    <div key="personal">
      <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.375rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.02em' }}>
        Patient Intake & Demographics
      </h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 24 }}>
        Enter patient identification and physiological baseline parameters for clinical screening.
      </p>

      {/* Patient Name with Live Search */}
      <div style={{ position: 'relative', marginBottom: 20 }}>
        <FormField label="Patient Name" hint="Search existing patient by name or enter new patient name">
          <div style={{ position: 'relative' }}>
            <Input
              value={form.patient_name}
              onChange={handlePatientNameChange}
              placeholder="e.g., Eleanor Vance"
            />
            <div style={{ position: 'absolute', right: 12, top: 11, color: 'var(--c-muted)', pointerEvents: 'none' }}>
              <Search size={16} />
            </div>
          </div>
        </FormField>

        {/* Live Search Suggestions Dropdown */}
        {showSuggestions && patientSuggestions.length > 0 && (
          <div
            style={{
              position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
              background: 'var(--c-card)', border: '1px solid var(--c-primary)',
              borderRadius: 10, marginTop: -12, padding: 6,
              boxShadow: '0 12px 30px rgba(0,0,0,0.5)'
            }}
          >
            <div style={{ padding: '6px 10px', fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Existing Clinical Records
            </div>
            {patientSuggestions.map(p => (
              <div
                key={p.id}
                onClick={async () => {
                  try {
                    const full = await api.get(`/patients/${p.id}`)
                    applyPatientBaseline(full.data || p)
                  } catch {
                    applyPatientBaseline(p)
                  }
                }}
                style={{
                  padding: '10px 12px', borderRadius: 8, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  transition: 'background 0.15s'
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--c-card-hover)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--c-secondary)' }}>
                    {p.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                    Age: {p.age ?? '—'} · Gender: {p.gender ?? '—'} · {p.assessment_count} past screening{p.assessment_count === 1 ? '' : 's'}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--c-primary)', fontWeight: 600 }}>
                  Select Record <ChevronRight size={14} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Matched Patient Record Alert Card */}
      {matchedPatientRecord && (
        <div style={{
          padding: 16, borderRadius: 10, marginBottom: 20,
          background: 'rgba(13, 148, 136, 0.12)', border: '1px solid rgba(13, 148, 136, 0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <CheckCircle2 size={20} color="var(--c-primary)" />
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                Linked to Patient: {matchedPatientRecord.name}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                {autoPopulated ? 'Demographics and baseline habits pre-filled.' : 'Existing record loaded.'}
                {matchedPatientRecord.latest_assessment_id && ' Prior screening available.'}
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {matchedPatientRecord.latest_assessment_id && (
              <button
                type="button"
                onClick={() => navigate(`/dashboard/${matchedPatientRecord.latest_assessment_id}`)}
                className="btn-ghost"
                style={{ padding: '6px 12px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6 }}
              >
                <History size={13} /> Resume Latest
              </button>
            )}
            <button
              type="button"
              onClick={() => {
                setMatchedPatientRecord(null)
                update('patient_id', '')
                setAutoPopulated(false)
              }}
              className="btn-ghost"
              style={{ padding: '6px 10px', fontSize: '0.75rem' }}
            >
              Unlink
            </button>
          </div>
        </div>
      )}

      {/* Demographics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <FormField label="Age (years)"><Input type="number" value={form.age} onChange={v => update('age', parseInt(v) || 0)} min={1} max={125} /></FormField>
        <FormField label="Gender"><Select value={form.gender} onChange={v => update('gender', v)} options={[{ value: 'MALE', label: 'Male' }, { value: 'FEMALE', label: 'Female' }, { value: 'OTHER', label: 'Other' }]} /></FormField>
        <FormField label="Height (cm)"><Input type="number" value={form.height_cm} onChange={v => update('height_cm', parseFloat(v) || 0)} min={40} max={260} /></FormField>
        <FormField label="Weight (kg)"><Input type="number" value={form.weight_kg} onChange={v => update('weight_kg', parseFloat(v) || 0)} min={20} max={350} /></FormField>
      </div>

      <div className="card" style={{ padding: 16, marginTop: 16, background: 'var(--c-surface-tint)', border: '1px solid var(--c-border)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', marginBottom: 4 }}>Calculated BMI</div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--c-primary)', fontFamily: 'var(--font-heading)' }}>
          {form.height_cm > 0 ? (form.weight_kg / ((form.height_cm / 100) ** 2)).toFixed(1) : '—'}
        </div>
      </div>
    </div>,

    <div key="dietary">
      <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.375rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.02em' }}>Dietary Habits</h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 28 }}>Dietary patterns directly determine baseline nutritional availability.</p>
      <FormField label="Dietary Pattern"><Select value={form.dietary_pattern} onChange={v => update('dietary_pattern', v)} options={[...DIET_PATTERNS]} /></FormField>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <FormField label="Meals per Day"><Input type="number" value={form.meals_per_day} onChange={v => update('meals_per_day', parseInt(v) || 1)} min={1} max={8} /></FormField>
        <FormField label="Water Intake (liters/day)"><Input type="number" value={form.water_intake_liters} onChange={v => update('water_intake_liters', parseFloat(v) || 0)} min={0} max={10} step={0.5} /></FormField>
      </div>
      <FormField label="Daily Fruit & Vegetable Servings"><Slider value={form.daily_fruit_vegetable_servings} onChange={v => update('daily_fruit_vegetable_servings', v)} min={0} max={10} label="Servings" /></FormField>
      <FormField label="Junk Food Frequency"><Select value={form.junk_food_frequency} onChange={v => update('junk_food_frequency', v)} options={[{ value: 'NEVER', label: 'Never' }, { value: 'RARELY', label: 'Rarely' }, { value: 'WEEKLY', label: 'Weekly' }, { value: 'DAILY', label: 'Daily' }]} /></FormField>
    </div>,

    <div key="lifestyle">
      <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.375rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.02em' }}>Lifestyle Factors</h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 28 }}>Physical activity, sleep, and environmental factors impact nutrient metabolism.</p>
      <FormField label="Activity Level"><Select value={form.activity_level} onChange={v => update('activity_level', v)} options={[...ACTIVITY_LEVELS]} /></FormField>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <FormField label="Sleep (hours/night)"><Input type="number" value={form.sleep_hours_per_night} onChange={v => update('sleep_hours_per_night', parseFloat(v) || 0)} min={0} max={24} step={0.5} /></FormField>
        <FormField label="Sunlight Exposure (min/day)"><Input type="number" value={form.sunlight_exposure_min_per_day} onChange={v => update('sunlight_exposure_min_per_day', parseInt(v) || 0)} min={0} max={480} /></FormField>
      </div>
      <FormField label="Stress Level"><Slider value={form.stress_level} onChange={v => update('stress_level', v)} min={1} max={10} label="1 = Low, 10 = Severe" /></FormField>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <FormField label="Smoking Status"><Select value={form.smoking_status} onChange={v => update('smoking_status', v)} options={[{ value: 'NEVER', label: 'Never' }, { value: 'FORMER', label: 'Former' }, { value: 'CURRENT', label: 'Current' }]} /></FormField>
        <FormField label="Alcohol Consumption"><Select value={form.alcohol_consumption} onChange={v => update('alcohol_consumption', v)} options={[{ value: 'NONE', label: 'None' }, { value: 'OCCASIONAL', label: 'Occasional' }, { value: 'MODERATE', label: 'Moderate' }, { value: 'HEAVY', label: 'Heavy' }]} /></FormField>
      </div>
    </div>,

    <div key="symptoms">
      <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.375rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.02em' }}>Symptoms</h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 28 }}>Select symptoms currently experienced and rate their severity.</p>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        {SYMPTOM_LIST.map(s => {
          const isActive = s.key in form.symptoms
          return (
            <div key={s.key} style={{
              padding: '12px 14px', borderRadius: 10,
              border: `1px solid ${isActive ? 'var(--c-primary)' : 'var(--c-border)'}`,
              background: isActive ? 'var(--c-surface-tint)' : 'var(--c-card)',
              cursor: 'pointer', transition: 'all 0.15s',
            }}>
              <div onClick={() => toggleSymptom(s.key, 5)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--c-secondary)' }}>{s.label}</span>
                <div style={{
                  width: 18, height: 18, borderRadius: 4,
                  border: `2px solid ${isActive ? 'var(--c-primary)' : 'var(--c-border)'}`,
                  background: isActive ? 'var(--c-primary)' : 'var(--c-badge-check-bg)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  {isActive && <svg width="10" height="8" viewBox="0 0 10 8"><path d="M1 4l2.5 2.5L9 1" stroke="white" strokeWidth="2" fill="none" /></svg>}
                </div>
              </div>
              {isActive && <div style={{ marginTop: 8 }}><Slider value={form.symptoms[s.key]} onChange={v => updateSymptomSeverity(s.key, v)} min={1} max={10} label="Severity" /></div>}
            </div>
          )
        })}
      </div>
    </div>,

    <div key="medical">
      <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.375rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.02em' }}>Medical History</h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 28 }}>Conditions that may affect nutrient absorption or metabolism.</p>
      {form.medical_history.map((item, i) => (
        <div key={i} className="card" style={{ padding: 16, marginBottom: 12 }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div style={{ flex: 1 }}><Input value={item.condition_name} placeholder="Condition name (e.g., Celiac Disease)" onChange={v => { const mh = [...form.medical_history]; mh[i] = { ...mh[i], condition_name: v }; update('medical_history', mh) }} /></div>
            <button onClick={() => update('medical_history', form.medical_history.filter((_, j) => j !== i))} style={{ padding: '8px 12px', background: 'var(--c-danger-bg)', color: 'var(--c-danger-text)', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600 }}>Remove</button>
          </div>
          <div style={{ display: 'flex', gap: 16, marginTop: 10 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--c-muted)', cursor: 'pointer' }}>
              <input type="checkbox" checked={item.is_active} onChange={e => { const mh = [...form.medical_history]; mh[i] = { ...mh[i], is_active: e.target.checked }; update('medical_history', mh) }} style={{ accentColor: 'var(--c-primary)' }} /> Active
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--c-muted)', cursor: 'pointer' }}>
              <input type="checkbox" checked={item.impacts_absorption} onChange={e => { const mh = [...form.medical_history]; mh[i] = { ...mh[i], impacts_absorption: e.target.checked }; update('medical_history', mh) }} style={{ accentColor: 'var(--c-primary)' }} /> Impacts Absorption
            </label>
          </div>
        </div>
      ))}
      <button onClick={() => update('medical_history', [...form.medical_history, { condition_name: '', is_active: true, impacts_absorption: false }])} className="btn-ghost" style={{ padding: '10px 20px', fontSize: '0.8125rem' }}>+ Add Condition</button>
    </div>,

    <div key="supplements">
      <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.375rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.02em' }}>Supplement Usage</h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 28 }}>Current vitamins, minerals, or dietary supplements.</p>
      {form.supplement_usage.map((item, i) => (
        <div key={i} className="card" style={{ padding: 16, marginBottom: 12 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: 10, alignItems: 'center' }}>
            <Input value={item.supplement_name} placeholder="e.g., Vitamin D3" onChange={v => { const su = [...form.supplement_usage]; su[i] = { ...su[i], supplement_name: v }; update('supplement_usage', su) }} />
            <Input value={item.dosage} placeholder="e.g., 2000IU" onChange={v => { const su = [...form.supplement_usage]; su[i] = { ...su[i], dosage: v }; update('supplement_usage', su) }} />
            <Select value={item.frequency} onChange={v => { const su = [...form.supplement_usage]; su[i] = { ...su[i], frequency: v }; update('supplement_usage', su) }} options={[{ value: 'DAILY', label: 'Daily' }, { value: 'WEEKLY', label: 'Weekly' }, { value: 'AS_NEEDED', label: 'As Needed' }]} />
            <button onClick={() => update('supplement_usage', form.supplement_usage.filter((_, j) => j !== i))} style={{ padding: '8px 12px', background: 'var(--c-danger-bg)', color: 'var(--c-danger-text)', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600 }}>✕</button>
          </div>
        </div>
      ))}
      <button onClick={() => update('supplement_usage', [...form.supplement_usage, { supplement_name: '', dosage: '', frequency: 'DAILY' }])} className="btn-ghost" style={{ padding: '10px 20px', fontSize: '0.8125rem' }}>+ Add Supplement</button>
    </div>,
  ]

  return (
    <div style={{ maxWidth: 720, margin: '0 auto' }}>
      <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 8 }}>
        Clinical Health Assessment
      </h1>
      <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', marginBottom: 32 }}>
        Complete the screening intake to evaluate multi-nutrient deficiency risks and generate personalized interventions.
      </p>

      {submitError && (
        <div style={{
          padding: '14px 18px', borderRadius: 10, background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)', color: '#EF4444',
          fontSize: '0.875rem', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10
        }}>
          <AlertCircle size={18} />
          <span>{submitError}</span>
        </div>
      )}

      <StepIndicator current={step} total={6} />

      <div className="card" style={{ padding: 32, marginBottom: 24 }}>
        <AnimatePresence mode="wait">
          <motion.div key={step} variants={slideVariants} initial="enter" animate="center" exit="exit">
            {steps[step]}
          </motion.div>
        </AnimatePresence>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <button
          onClick={prev}
          disabled={step === 0}
          className="btn-ghost"
          style={{ padding: '10px 24px', fontSize: '0.8125rem', opacity: step === 0 ? 0.4 : 1 }}
        >
          <ChevronLeft size={14} /> Previous
        </button>
        {step < 5 ? (
          <button onClick={next} className="btn-primary" style={{ padding: '10px 24px', fontSize: '0.8125rem' }}>
            Next <ChevronRight size={14} />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="btn-primary"
            style={{ padding: '10px 28px', fontSize: '0.8125rem', opacity: submitting ? 0.7 : 1 }}
          >
            {submitting ? 'Analyzing...' : 'Submit Assessment'} <Send size={14} />
          </button>
        )}
      </div>
    </div>
  )
}
