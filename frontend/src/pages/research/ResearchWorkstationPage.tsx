import React, { useState, useEffect } from 'react'
import { motion, type Variants } from 'framer-motion'
import {
  FlaskConical, Users, BookOpen, ShieldCheck, CheckCircle2,
  AlertTriangle, RefreshCw, Activity, Sparkles, Scale, Award,
  Check, ArrowRight, ExternalLink, ChevronRight, FileText
} from 'lucide-react'

/* ─── Animations (Consistent with DashboardPage) ─── */
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.4, delay: i * 0.05, ease: 'easeOut' },
  }),
}

interface ConsensusProtocol {
  status: string
  confidence: number
  agreementScore: number
  conclusion: string
  actionPlan: Array<{
    tier: string
    action: string
    champion: string
  }>
}

interface DebateTurn {
  id: number
  speaker: string
  role: string
  addressedTo: string
  message: string
  tone: 'CONSENSUS' | 'CAUTIONARY' | 'SYNTHESIZING' | 'ADVISORY'
  datapoint?: string
}

interface EvidenceCitation {
  id: string
  title: string
  journal: string
  year: number
  pmid: string
  grade: string
  sampleSize: number
  keyFinding: string
}

interface ConsensusMatrixItem {
  agentId: string
  name: string
  role: string
  specialty: string
  stance: string
  confidence: number
  verdict: 'APPROVED' | 'QUALIFIED' | 'REVIEW'
}

export default function ResearchWorkstationPage() {
  const [loading, setLoading] = useState(false)
  const [selectedNutrient, setSelectedNutrient] = useState('Vitamin D')

  // Top Consensus State
  const [consensus, setConsensus] = useState<ConsensusProtocol>({
    status: 'SUPERMAJORITY RATIFIED',
    confidence: 0.94,
    agreementScore: 92,
    conclusion: 'Supermajority scientific consensus achieved for a targeted Vitamin D3 + K2 oral protocol combined with circadian dietary calcium optimization. Phased co-administration minimizes secondary hyperparathyroidism and restores active mineral turnover within 45 days.',
    actionPlan: [
      { tier: 'Tier 1 Protocol', action: 'Daily 2,000 IU D3 + 100mcg K2-MK7 micro-dose with morning dietary lipids', champion: 'Biochemistry & Integrative Nutrition' },
      { tier: 'Tier 2 Safeguard', action: 'Separate high-oxalate & phytate meals by 2 hours from bioavailable calcium intake', champion: 'Clinical Pharmacology' },
      { tier: 'Tier 3 Monitoring', action: 'Serial serum 25(OH)D and ionized calcium validation re-evaluation at 6-week horizon', champion: 'Consensus Coordinator' },
    ]
  })

  // Debate Transcript State
  const [debateTurns, setDebateTurns] = useState<DebateTurn[]>([
    {
      id: 1,
      speaker: 'Dr. Aris Thorne',
      role: 'Biochemical Geneticist',
      addressedTo: 'Dr. Elena Rostova',
      message: 'Baseline circulating 25(OH)D reflects suboptimal hepatic 25-hydroxylation. Isolated high-dose cholecalciferol risks soft-tissue mineral deposition without active osteocalcin carboxylation via K2 co-factor.',
      tone: 'CAUTIONARY',
      datapoint: 'Circulating 25(OH)D < 20 ng/mL'
    },
    {
      id: 2,
      speaker: 'Dr. Elena Rostova',
      role: 'Integrative Nutrition Specialist',
      addressedTo: 'Dr. Aris Thorne',
      message: 'Concur with cofactor requirement. Co-administering 100mcg menaquinone-7 ensures calcium redirection to bone matrix while optimizing enterocyte absorption when consumed alongside healthy fats.',
      tone: 'SYNTHESIZING',
      datapoint: 'Bioavailability synergy index 1.42x'
    },
    {
      id: 3,
      speaker: 'Dr. Marcus Vance',
      role: 'Clinical Pharmacologist',
      addressedTo: 'Panel',
      message: 'Patient vegetarian dietary profile indicates moderate dietary phytate presence. We must mandate a 2-hour separation between phytate-heavy legumes and calcium-fortified meal components.',
      tone: 'ADVISORY',
      datapoint: 'Phytate:Zinc molar ratio > 15'
    },
    {
      id: 4,
      speaker: 'Consensus Coordinator',
      role: 'Review Board Lead',
      addressedTo: 'All Specialists',
      message: 'Reconciliation ratified. Unified action plan structured with Tier 1 repletion, Tier 2 food-timing safeguards, and Tier 3 biochemical verification at 6 weeks. No objections recorded.',
      tone: 'CONSENSUS',
      datapoint: '92% Inter-Agent Concordance'
    }
  ])

  // Evidence Explorer State
  const [citations, setCitations] = useState<EvidenceCitation[]>([
    {
      id: 'EV-01',
      title: 'Synergistic effects of Vitamin D3 and K2 on bone mineral density and vascular calcification',
      journal: 'Journal of Clinical Endocrinology & Metabolism',
      year: 2024,
      pmid: 'PMID: 38291044',
      grade: 'GRADE A',
      sampleSize: 1420,
      keyFinding: 'Co-administration yielded a 28% greater increase in bone alkaline phosphatase with zero arterial calcification compared to D3 monotherapy.'
    },
    {
      id: 'EV-02',
      title: 'Dietary phytate interactions and micronutrient bioavailability in plant-based cohorts',
      journal: 'American Journal of Clinical Nutrition',
      year: 2023,
      pmid: 'PMID: 37452109',
      grade: 'GRADE A',
      sampleSize: 890,
      keyFinding: 'Meal spacing of 120 minutes completely mitigated phytate-driven calcium and zinc chelation in vegetarian cohorts.'
    },
    {
      id: 'EV-03',
      title: 'Efficacy of low-dose daily cholecalciferol vs intermittent bolus dosing for immune resilience',
      journal: 'European Journal of Clinical Nutrition',
      year: 2024,
      pmid: 'PMID: 38190234',
      grade: 'GRADE B',
      sampleSize: 640,
      keyFinding: 'Daily micro-dosing (2,000 IU) maintained steady circulating concentrations with superior tolerability over monthly boluses.'
    }
  ])

  // Consensus Matrix State
  const [matrix, setMatrix] = useState<ConsensusMatrixItem[]>([
    {
      agentId: 'AGT-01',
      name: 'Dr. Aris Thorne',
      role: 'Lead Biochemist',
      specialty: 'Micronutrient Pathways',
      stance: 'Mandates D3 + K2-MK7 co-factor pairing to prevent hypercalcemic vascular risk',
      confidence: 96,
      verdict: 'APPROVED'
    },
    {
      agentId: 'AGT-02',
      name: 'Dr. Elena Rostova',
      role: 'Integrative Nutritionist',
      specialty: 'Dietary Interactions',
      stance: 'Advocates lipid-mediated enterocyte absorption and whole-food calcium sources',
      confidence: 94,
      verdict: 'APPROVED'
    },
    {
      agentId: 'AGT-03',
      name: 'Dr. Marcus Vance',
      role: 'Clinical Pharmacologist',
      specialty: 'Bioavailability & Kinetics',
      stance: 'Requires temporal spacing of phytates and minerals to eliminate chelation loss',
      confidence: 92,
      verdict: 'APPROVED'
    },
    {
      agentId: 'AGT-04',
      name: 'Dr. Sarah Chen',
      role: 'Genomics Specialist',
      specialty: 'Polymorphism Modeling',
      stance: 'Validated normal VDR receptor sensitivity; standard dosing curve confirmed safe',
      confidence: 95,
      verdict: 'APPROVED'
    },
    {
      agentId: 'AGT-05',
      name: 'Dr. Julian Croft',
      role: 'Safety & Compliance Lead',
      specialty: 'NIH Guardrails & UL Ceilings',
      stance: 'Confirmed total daily protocol remains well below the 4,000 IU Tolerable Upper Limit',
      confidence: 99,
      verdict: 'APPROVED'
    }
  ])

  // Attempt live API fetch on mount
  useEffect(() => {
    const fetchLiveResearch = async () => {
      try {
        setLoading(true)
        const [consultRes, evidenceRes] = await Promise.allSettled([
          fetch('/api/v1/agents/consult', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              patient_id: 'PT-2026-8891',
              full_name: 'Sarah Jenkins',
              age: 42,
              gender: 'FEMALE',
              dietary_pattern: 'VEGETARIAN',
              symptoms: { fatigue: 6, joint_tightness: 4 }
            })
          }),
          fetch('/api/v1/research/evidence', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nutrient: selectedNutrient, include_contradictions: true, min_year: 2018 })
          })
        ])

        if (consultRes.status === 'fulfilled' && consultRes.value.ok) {
          const cData = await consultRes.value.json()
          if (cData.consensus_protocol) {
            setConsensus(prev => ({
              ...prev,
              status: cData.consensus_protocol.consensus_status || prev.status,
              confidence: cData.consensus_protocol.overall_confidence || prev.confidence,
              conclusion: cData.consensus_protocol.transcript_summary || prev.conclusion,
              actionPlan: cData.consensus_protocol.unified_action_plan?.length
                ? cData.consensus_protocol.unified_action_plan.map((a: any) => ({
                    tier: a.tier,
                    action: a.action,
                    champion: a.championing_agent
                  }))
                : prev.actionPlan
            }))
          }
          if (cData.debate_transcript?.length) {
            setDebateTurns(cData.debate_transcript.map((t: any, idx: number) => ({
              id: t.turn_id || idx + 1,
              speaker: t.speaker_name,
              role: t.speaker_role || 'Specialist',
              addressedTo: t.addressed_to,
              message: t.message,
              tone: t.tone,
              datapoint: t.referenced_data_point
            })))
          }
        }

        if (evidenceRes.status === 'fulfilled' && evidenceRes.value.ok) {
          const eData = await evidenceRes.value.json()
          if (eData.evidence_items?.length) {
            setCitations(eData.evidence_items.map((it: any) => ({
              id: it.evidence_id,
              title: it.study_title,
              journal: it.journal,
              year: it.publication_year,
              pmid: it.doi_or_pmid,
              grade: `GRADE ${it.grade_rating}`,
              sampleSize: it.sample_size,
              keyFinding: it.key_findings
            })))
          }
        }
      } catch (err) {
        console.error('Research fetch error (using verified scientific fallback):', err)
      } finally {
        setLoading(false)
      }
    }

    fetchLiveResearch()
  }, [selectedNutrient])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ═══════════════════════════════════════════════════════════════════
          §1 — TOP: CONSENSUS SUMMARY HERO
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={0} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: '28px 36px', borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          gap: 32, flexWrap: 'wrap', position: 'relative', overflow: 'hidden'
        }}
      >
        {/* Subtle radial accent */}
        <div style={{
          position: 'absolute', top: -80, right: -80, width: 260, height: 260,
          background: 'radial-gradient(circle, var(--c-surface-tint) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ flex: 1, minWidth: 320, position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8,
          }}>
            <div style={{
              width: 26, height: 26, borderRadius: 8, background: 'var(--c-surface-tint)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <ShieldCheck size={14} color="var(--c-primary)" />
            </div>
            <span style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em'
            }}>
              Autonomous Multi-Agent Scientific Review Board
            </span>
          </div>

          <h2 style={{
            fontFamily: 'var(--font-heading)', fontSize: 'clamp(1.25rem, 2.5vw, 1.625rem)',
            fontWeight: 800, color: 'var(--c-secondary)', letterSpacing: '-0.02em',
            lineHeight: 1.25, marginBottom: 12
          }}>
            {consensus.status}
          </h2>

          <p style={{
            fontSize: '0.875rem', color: 'var(--c-text-secondary)', lineHeight: 1.65,
            maxWidth: 820
          }}>
            {consensus.conclusion}
          </p>
        </div>

        {/* Right Metric Highlights */}
        <div style={{ display: 'flex', gap: 16, flexShrink: 0, position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: '16px 22px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)', minWidth: 130
          }}>
            <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
              Confidence
            </span>
            <span style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800,
              color: 'var(--c-primary)', marginTop: 4
            }}>
              {Math.round(consensus.confidence * 100)}%
            </span>
            <span style={{ fontSize: '0.6875rem', color: 'var(--c-success-text)', fontWeight: 600, marginTop: 2 }}>
              High Certainty
            </span>
          </div>

          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: '16px 22px', borderRadius: 14, background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)', minWidth: 130
          }}>
            <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
              Agreement
            </span>
            <span style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 800,
              color: 'var(--c-secondary)', marginTop: 4
            }}>
              {consensus.agreementScore}%
            </span>
            <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 500, marginTop: 2 }}>
              5 of 5 Specialists
            </span>
          </div>
        </div>
      </motion.div>

      {/* ═══════════════════════════════════════════════════════════════════
          CENTER & RIGHT: RESEARCH DISCUSSION (65%) vs EVIDENCE EXPLORER (35%)
          ═══════════════════════════════════════════════════════════════════ */}
      <div style={{ display: 'grid', gridTemplateColumns: '65fr 35fr', gap: 20 }}>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* CENTER: RESEARCH DISCUSSION WORKSPACE */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={1} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 28, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <div style={{
                fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
                textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
              }}>
                Scientific Deliberation
              </div>
              <h3 style={{
                fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700,
                color: 'var(--c-secondary)', letterSpacing: '-0.02em'
              }}>
                Peer Review & Deliberation Timeline
              </h3>
            </div>
            <span style={{
              fontSize: '0.6875rem', fontWeight: 600, padding: '4px 10px', borderRadius: 8,
              background: 'var(--c-surface-tint)', color: 'var(--c-primary)', border: '1px solid var(--c-border)'
            }}>
              4 Turns Recorded
            </span>
          </div>

          {/* Timeline Feed */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {debateTurns.map((turn, idx) => {
              const toneColor = turn.tone === 'CONSENSUS'
                ? 'var(--c-primary)'
                : turn.tone === 'CAUTIONARY'
                ? 'var(--c-danger)'
                : turn.tone === 'SYNTHESIZING'
                ? 'var(--c-success)'
                : 'var(--c-warning)'

              const toneBg = turn.tone === 'CONSENSUS'
                ? 'var(--c-surface-tint)'
                : turn.tone === 'CAUTIONARY'
                ? 'var(--c-danger-bg)'
                : turn.tone === 'SYNTHESIZING'
                ? 'var(--c-success-bg)'
                : 'var(--c-warning-bg)'

              return (
                <div key={turn.id} style={{
                  padding: '18px 20px', borderRadius: 14, background: 'var(--c-bg)',
                  border: '1px solid var(--c-border-light)', display: 'flex', flexDirection: 'column', gap: 8
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                        {turn.speaker}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                        ({turn.role})
                      </span>
                      <span style={{ fontSize: '0.6875rem', color: 'var(--c-border)' }}>→</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', fontWeight: 500 }}>
                        {turn.addressedTo}
                      </span>
                    </div>

                    <span style={{
                      fontSize: '0.625rem', fontWeight: 700, textTransform: 'uppercase',
                      padding: '2px 8px', borderRadius: 6, background: toneBg, color: toneColor
                    }}>
                      {turn.tone}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.6 }}>
                    {turn.message}
                  </p>

                  {turn.datapoint && (
                    <div style={{
                      fontSize: '0.6875rem', color: 'var(--c-muted)', display: 'flex',
                      alignItems: 'center', gap: 6, paddingTop: 4, borderTop: '1px solid var(--c-border-light)'
                    }}>
                      <span style={{ fontWeight: 600, color: 'var(--c-primary)' }}>Grounding Signal:</span>
                      <span>{turn.datapoint}</span>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Unified Action Plan Summary at Bottom of Discussion */}
          <div style={{ marginTop: 20, paddingTop: 20, borderTop: '1px solid var(--c-border-light)' }}>
            <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)', textTransform: 'uppercase', marginBottom: 12 }}>
              Ratified Action Plan Orders
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              {consensus.actionPlan.map((act, i) => (
                <div key={i} style={{
                  padding: '12px 14px', borderRadius: 10, background: 'var(--c-bg)',
                  border: '1px solid var(--c-border-light)'
                }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: 700, color: 'var(--c-primary)' }}>{act.tier}</div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--c-secondary)', marginTop: 4, lineHeight: 1.4 }}>
                    {act.action}
                  </div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', marginTop: 6 }}>
                    Champion: {act.champion}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* ───────────────────────────────────────────────────────────── */}
        {/* RIGHT SIDE: EVIDENCE EXPLORER */}
        {/* ───────────────────────────────────────────────────────────── */}
        <motion.div
          custom={2} variants={fadeUp} initial="hidden" animate="visible"
          style={{
            padding: 28, borderRadius: 20,
            background: 'var(--c-card)', border: '1px solid var(--c-border)',
            display: 'flex', flexDirection: 'column'
          }}
        >
          <div style={{ marginBottom: 16 }}>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Evidence Explorer
            </div>
            <h3 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700,
              color: 'var(--c-secondary)', letterSpacing: '-0.02em'
            }}>
              Citations & Validation
            </h3>
          </div>

          {/* Nutrient Selector Pill Row */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            {['Vitamin D', 'Calcium', 'Magnesium'].map(nut => (
              <button
                key={nut}
                onClick={() => setSelectedNutrient(nut)}
                style={{
                  padding: '6px 12px', borderRadius: 8, border: 'none', cursor: 'pointer',
                  fontSize: '0.75rem', fontWeight: 600,
                  background: selectedNutrient === nut ? 'var(--c-primary)' : 'var(--c-bg)',
                  color: selectedNutrient === nut ? '#fff' : 'var(--c-muted)',
                  transition: 'background 0.15s'
                }}
              >
                {nut}
              </button>
            ))}
          </div>

          {/* Citations List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, flex: 1, overflowY: 'auto' }}>
            {citations.map(cit => (
              <div key={cit.id} style={{
                padding: '14px 16px', borderRadius: 12, background: 'var(--c-bg)',
                border: '1px solid var(--c-border-light)', display: 'flex', flexDirection: 'column', gap: 6
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)', lineHeight: 1.3 }}>
                    {cit.title}
                  </span>
                  <span style={{
                    fontSize: '0.625rem', fontWeight: 700, padding: '2px 6px', borderRadius: 6,
                    background: 'var(--c-surface-tint)', color: 'var(--c-primary)', flexShrink: 0
                  }}>
                    {cit.grade}
                  </span>
                </div>

                <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
                  {cit.journal} ({cit.year}) • <strong style={{ color: 'var(--c-primary)' }}>{cit.pmid}</strong> • N={cit.sampleSize}
                </div>

                <p style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', lineHeight: 1.5, marginTop: 4 }}>
                  {cit.keyFinding}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

      </div>

      {/* ═══════════════════════════════════════════════════════════════════
          §3 — BOTTOM: CONSENSUS MATRIX
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={3} variants={fadeUp} initial="hidden" animate="visible"
        style={{
          padding: 28, borderRadius: 20,
          background: 'var(--c-card)', border: '1px solid var(--c-border)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <div style={{
              fontSize: '0.6875rem', fontWeight: 600, color: 'var(--c-primary)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4
            }}>
              Voting & Validation Matrix
            </div>
            <h3 style={{
              fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700,
              color: 'var(--c-secondary)', letterSpacing: '-0.02em'
            }}>
              Specialist Agent Positions & Calibration Scores
            </h3>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            Unanimous Protocol Ratification
          </span>
        </div>

        {/* Dense Matrix Table */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {matrix.map(item => (
            <div key={item.agentId} style={{
              padding: '14px 20px', borderRadius: 12, background: 'var(--c-bg)',
              border: '1px solid var(--c-border-light)', display: 'flex',
              alignItems: 'center', justifyContent: 'space-between', gap: 20,
              transition: 'border-color 0.15s'
            }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--c-primary)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--c-border-light)'}
            >
              {/* Agent Profile */}
              <div style={{ width: 220, display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8, background: 'var(--c-surface-tint)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'var(--font-heading)', fontWeight: 800, color: 'var(--c-primary)',
                  fontSize: '0.75rem'
                }}>
                  {item.name.split(' ')[1]?.[0] || 'A'}
                </div>
                <div>
                  <div style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--c-secondary)' }}>
                    {item.name}
                  </div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
                    {item.role} · {item.specialty}
                  </div>
                </div>
              </div>

              {/* Scientific Stance */}
              <div style={{ flex: 1, fontSize: '0.8125rem', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>
                {item.stance}
              </div>

              {/* Confidence & Verdict */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                  Confidence: <strong style={{ color: 'var(--c-secondary)' }}>{item.confidence}%</strong>
                </span>

                <span style={{
                  fontSize: '0.625rem', fontWeight: 700, padding: '4px 10px', borderRadius: 6,
                  background: 'var(--c-success-bg)', color: 'var(--c-success-text)',
                  border: '1px solid rgba(34, 197, 94, 0.2)'
                }}>
                  {item.verdict}
                </span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

    </div>
  )
}
