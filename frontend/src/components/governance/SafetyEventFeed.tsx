import React, { useState, useEffect } from 'react'
import { ShieldAlert, ShieldCheck, AlertOctagon, CheckCircle, Ban, Play } from 'lucide-react'

interface SafetyRule {
  rule_id: string
  rule_type: string
  target: string
  threshold?: string
  condition?: string
  severity: string
  action: string
  description?: string
  rationale?: string
}

interface SafetyViolation {
  severity: string
  rule_id: string
  rule_name: string
  nutrient?: string
  violating_value?: number
  threshold_value?: number
  clinical_rationale: string
  action_taken: string
}

interface EvaluationResult {
  safety_score: number
  safety_tier: string
  is_safe_for_dispatch: boolean
  violations_count: number
  violations: SafetyViolation[]
  mitigation_instructions: string
}

export default function SafetyEventFeed() {
  const [rules, setRules] = useState<SafetyRule[]>([])
  const [testCondition, setTestCondition] = useState('HEMOCHROMATOSIS')
  const [testNutrient, setTestNutrient] = useState('Iron')
  const [testDose, setTestDose] = useState(65)
  const [evalResult, setEvalResult] = useState<EvaluationResult | null>(null)
  const [evaluating, setEvaluating] = useState(false)

  useEffect(() => {
    fetchRules()
  }, [])

  const fetchRules = async () => {
    try {
      const res = await fetch('/api/v1/safety/rules')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setRules(data)
    } catch (err) {
      console.error(err)
    }
  }

  const runTestEvaluation = async () => {
    try {
      setEvaluating(true)
      const payload = {
        assessment: {
          age: 45,
          gender: 'Male',
          conditions: testCondition === 'NONE' ? [] : [testCondition],
          medications: testCondition === 'WARFARIN' ? ['Warfarin'] : []
        },
        recommendations: [
          { target_nutrient: testNutrient, dose_mg: testDose }
        ]
      }
      const res = await fetch('/api/v1/safety/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setEvalResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setEvaluating(false)
    }
  }

  return (
    <div style={{
      background: 'var(--c-surface, #ffffff)',
      borderRadius: '16px',
      border: '1px solid var(--c-border, #e2e8f0)',
      padding: '24px',
      boxShadow: '0 4px 20px -2px rgba(0,0,0,0.05)'
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <div style={{
          width: '36px', height: '36px', borderRadius: '10px',
          background: 'linear-gradient(135deg, #ef4444, #b91c1c)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff'
        }}>
          <ShieldAlert size={20} />
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: 'var(--c-text, #0f172a)' }}>
            Clinical Safety Guardrails & Intervention Blocker
          </h3>
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--c-text-muted, #64748b)' }}>
            Enforces NIH Office of Dietary Supplements Upper Limits & Pathological Contraindications
          </p>
        </div>
      </div>

      {/* Interactive Safety Simulator */}
      <div style={{
        padding: '16px', borderRadius: '12px',
        background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)',
        marginBottom: '24px'
      }}>
        <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--c-text, #0f172a)', marginBottom: '12px' }}>
          Interactive Clinical Safety Sandbox
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '4px' }}>
              Patient Condition:
            </label>
            <select
              value={testCondition}
              onChange={e => setTestCondition(e.target.value)}
              style={{
                width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1',
                fontSize: '13px', background: '#fff'
              }}
            >
              <option value="NONE">None (Healthy Adult)</option>
              <option value="HEMOCHROMATOSIS">Hemochromatosis (Iron Overload)</option>
              <option value="CHRONIC_KIDNEY_DISEASE">Chronic Kidney Disease (CKD)</option>
              <option value="WILSONS_DISEASE">Wilson's Disease (Copper)</option>
              <option value="PREGNANCY">Pregnancy (Teratogenic Risk)</option>
              <option value="WARFARIN">On Warfarin / Coumadin</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '4px' }}>
              Proposed Nutrient:
            </label>
            <select
              value={testNutrient}
              onChange={e => setTestNutrient(e.target.value)}
              style={{
                width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1',
                fontSize: '13px', background: '#fff'
              }}
            >
              <option value="Iron">Iron</option>
              <option value="Potassium">Potassium</option>
              <option value="Copper">Copper</option>
              <option value="Vitamin A">Vitamin A (Retinol)</option>
              <option value="Vitamin D">Vitamin D</option>
              <option value="Vitamin K">Vitamin K</option>
              <option value="Calcium">Calcium</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '4px' }}>
              Dose Amount (mg or mcg):
            </label>
            <input
              type="number"
              value={testDose}
              onChange={e => setTestDose(Number(e.target.value))}
              style={{
                width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1',
                fontSize: '13px', background: '#fff'
              }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              onClick={runTestEvaluation}
              disabled={evaluating}
              style={{
                width: '100%', padding: '9px 16px', borderRadius: '6px',
                background: '#0d9488', color: '#fff', border: 'none',
                fontWeight: 700, fontSize: '13px', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px'
              }}
            >
              <Play size={14} /> Evaluate Safety
            </button>
          </div>
        </div>

        {/* Evaluation Output */}
        {evalResult && (
          <div style={{
            padding: '14px', borderRadius: '8px',
            background: evalResult.is_safe_for_dispatch ? '#ecfdf5' : '#fef2f2',
            border: `1px solid ${evalResult.is_safe_for_dispatch ? '#a7f3d0' : '#fecaca'}`,
            marginTop: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {evalResult.is_safe_for_dispatch ? (
                  <ShieldCheck color="#059669" size={18} />
                ) : (
                  <Ban color="#dc2626" size={18} />
                )}
                <span style={{ fontWeight: 800, color: evalResult.is_safe_for_dispatch ? '#059669' : '#dc2626', fontSize: '14px' }}>
                  {evalResult.is_safe_for_dispatch ? 'CLEARED FOR DISPATCH' : 'DISPATCH BLOCKED / QUARANTINED'}
                </span>
              </div>
              <div style={{ fontWeight: 700, fontSize: '13px', color: '#334155' }}>
                Safety Score: <b>{evalResult.safety_score} / 100</b> ({evalResult.safety_tier})
              </div>
            </div>

            <p style={{ margin: '4px 0 8px 0', fontSize: '12px', color: '#475569' }}>
              {evalResult.mitigation_instructions}
            </p>

            {evalResult.violations.map((v, idx) => (
              <div key={idx} style={{
                padding: '8px 12px', borderRadius: '6px', background: '#fff',
                border: '1px solid #fed7aa', marginTop: '6px', fontSize: '12px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: '#9a3412' }}>
                  <span>{v.rule_name}</span>
                  <span>Action: {v.action_taken}</span>
                </div>
                <div style={{ color: '#64748b', marginTop: '2px' }}>{v.clinical_rationale}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Rules Catalog Section */}
      <div>
        <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--c-text, #0f172a)', marginBottom: '10px' }}>
          Active Guardrails Catalog ({rules.length} Certified Rules)
        </div>
        <div style={{ maxHeight: '280px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {rules.map((rule, idx) => (
            <div key={idx} style={{
              padding: '12px 14px', borderRadius: '8px',
              background: 'var(--c-bg, #f8fafc)', border: '1px solid var(--c-border, #e2e8f0)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px'
            }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '13px', color: 'var(--c-text, #0f172a)' }}>
                  {rule.rule_id} &bull; <span style={{ color: '#0d9488' }}>{rule.target}</span>
                </div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                  {rule.description || rule.rationale || `Threshold: ${rule.threshold || rule.condition}`}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexShrink: 0 }}>
                <span style={{
                  fontSize: '11px', fontWeight: 700, padding: '2px 8px', borderRadius: '4px',
                  background: rule.severity === 'CRITICAL' ? '#fef2f2' : '#fef3c7',
                  color: rule.severity === 'CRITICAL' ? '#dc2626' : '#b45309'
                }}>
                  {rule.severity}
                </span>
                <span style={{
                  fontSize: '11px', fontWeight: 700, padding: '2px 8px', borderRadius: '4px',
                  background: rule.action === 'BLOCKED' ? '#dc2626' : '#475569',
                  color: '#fff'
                }}>
                  {rule.action}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
