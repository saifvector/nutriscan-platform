import { motion, type Variants } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  Shield, Activity, ArrowRight, CheckCircle2, Brain, Utensils,
  BarChart3, FileText, Scan, Zap, TrendingUp,
  Heart, ChevronRight, Sparkles, Target, Leaf
} from 'lucide-react'
import ThemeToggle from '../components/ui/ThemeToggle'

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
}

const stagger: Variants = {
  visible: { transition: { staggerChildren: 0.08 } },
}

/* ───────────── Navbar ───────────── */
function Navbar() {
  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
      backdropFilter: 'blur(12px)', backgroundColor: 'var(--c-navbar-bg)',
      borderBottom: '1px solid var(--c-border)',
    }}>
      <div className="container-wide" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'var(--c-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Leaf size={18} color="white" />
          </div>
          <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1.1rem', color: 'var(--c-secondary)', letterSpacing: '-0.02em' }}>
            NutriScan AI
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <a href="#features" style={{ color: 'var(--c-muted)', fontSize: '0.875rem', fontWeight: 500, textDecoration: 'none' }}>Features</a>
          <a href="#how-it-works" style={{ color: 'var(--c-muted)', fontSize: '0.875rem', fontWeight: 500, textDecoration: 'none' }}>How It Works</a>
          <a href="#architecture" style={{ color: 'var(--c-muted)', fontSize: '0.875rem', fontWeight: 500, textDecoration: 'none' }}>Architecture</a>
          <ThemeToggle />
          <Link to="/assessment" className="btn-primary" style={{ padding: '8px 20px', fontSize: '0.8125rem' }}>
            Start Assessment
          </Link>
        </div>
      </div>
    </nav>
  )
}

/* ───────────── Hero ───────────── */
function Hero() {
  return (
    <section style={{ paddingTop: 140, paddingBottom: 100, overflow: 'hidden' }}>
      <div className="container-wide" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
        <motion.div initial="hidden" animate="visible" variants={stagger}>
          <motion.p variants={fadeUp} style={{
            fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-primary)',
            textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 16
          }}>
            AI-Powered Nutritional Screening
          </motion.p>
          <motion.h1 variants={fadeUp} style={{
            fontFamily: 'var(--font-heading)', fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
            fontWeight: 800, lineHeight: 1.08, color: 'var(--c-secondary)',
            letterSpacing: '-0.03em', marginBottom: 24,
          }}>
            Understand Nutritional{' '}
            <span style={{ color: 'var(--c-primary)' }}>Deficiencies</span>{' '}
            Before They Become Health Problems
          </motion.h1>
          <motion.p variants={fadeUp} style={{
            fontSize: '1.125rem', lineHeight: 1.7, color: 'var(--c-text-secondary)',
            maxWidth: 480, marginBottom: 40,
          }}>
            AI-powered screening that predicts deficiencies across 11 essential nutrients,
            explains risk factors with SHAP analysis, and provides personalized food recommendations.
          </motion.p>
          <motion.div variants={fadeUp} style={{ display: 'flex', gap: 12 }}>
            <Link to="/assessment" className="btn-primary" style={{ padding: '14px 32px' }}>
              Start Assessment <ArrowRight size={16} />
            </Link>
            <a href="#features" className="btn-ghost" style={{ padding: '14px 32px' }}>
              Explore Platform
            </a>
          </motion.div>
        </motion.div>

        {/* Dashboard Mockup */}
        <motion.div
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: 'easeOut' }}
          style={{ perspective: 1200 }}
        >
          <div style={{
            transform: 'rotateY(-6deg) rotateX(2deg)',
            transformStyle: 'preserve-3d',
          }}>
            <div style={{
              background: 'var(--c-card)', borderRadius: 16, border: '1px solid var(--c-border)',
              boxShadow: 'var(--c-shadow-lg)', padding: 28, position: 'relative',
            }}>
              {/* Health Score */}
              <div style={{ display: 'flex', gap: 20, marginBottom: 20 }}>
                <div style={{
                  width: 120, height: 120, borderRadius: 16, background: 'var(--c-success-bg)',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                  border: '1px solid var(--c-border)',
                }}>
                  <span style={{ fontSize: 36, fontWeight: 800, color: 'var(--c-primary)', fontFamily: 'var(--font-heading)', letterSpacing: '-0.03em' }}>78</span>
                  <span style={{ fontSize: 11, color: 'var(--c-muted)', fontWeight: 600 }}>Health Score</span>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, color: 'var(--c-muted)', fontWeight: 500, marginBottom: 8 }}>Risk Distribution</div>
                  <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
                    {[
                      { label: 'Low', count: 5, bg: 'var(--c-success-bg)', color: 'var(--c-success-text)' },
                      { label: 'Moderate', count: 4, bg: 'var(--c-warning-bg)', color: 'var(--c-warning-text)' },
                      { label: 'High', count: 2, bg: 'var(--c-danger-bg)', color: 'var(--c-danger-text)' },
                    ].map(r => (
                      <div key={r.label} style={{
                        padding: '4px 10px', borderRadius: 6, background: r.bg,
                        fontSize: 11, fontWeight: 600, color: r.color,
                      }}>
                        {r.count} {r.label}
                      </div>
                    ))}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    {[
                      { name: 'Vitamin D', pct: 82, color: 'var(--c-danger)' },
                      { name: 'Iron', pct: 71, color: 'var(--c-danger)' },
                      { name: 'Vitamin B12', pct: 58, color: 'var(--c-warning)' },
                    ].map(n => (
                      <div key={n.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 10, color: 'var(--c-muted)', width: 64, flexShrink: 0 }}>{n.name}</span>
                        <div style={{ flex: 1, height: 6, background: 'var(--c-bar-track)', borderRadius: 3 }}>
                          <div style={{ width: `${n.pct}%`, height: '100%', background: n.color, borderRadius: 3 }} />
                        </div>
                        <span style={{ fontSize: 10, fontWeight: 600, color: n.color, width: 28 }}>{n.pct}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recommendation cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {[
                  { food: 'Wild Salmon', nutrient: 'Vitamin D', icon: '🐟' },
                  { food: 'Spinach & Lentils', nutrient: 'Iron + Folate', icon: '🥬' },
                ].map(f => (
                  <div key={f.food} style={{
                    padding: '10px 12px', borderRadius: 10, border: '1px solid var(--c-border-light)',
                    background: 'var(--c-surface-alt)', display: 'flex', alignItems: 'center', gap: 10,
                  }}>
                    <span style={{ fontSize: 20 }}>{f.icon}</span>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--c-secondary)' }}>{f.food}</div>
                      <div style={{ fontSize: 10, color: 'var(--c-muted)' }}>for {f.nutrient}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

/* ───────────── Problem Statement ───────────── */
function ProblemStatement() {
  const stats = [
    { number: '2B+', label: 'People affected by micronutrient deficiencies globally' },
    { number: '80%', label: 'Of deficiencies go undiagnosed until symptoms appear' },
    { number: '11', label: 'Essential nutrients our platform screens simultaneously' },
    { number: '<35ms', label: 'AI inference latency for real-time clinical screening' },
  ]
  return (
    <section className="section" style={{ background: 'var(--c-card)' }}>
      <div className="container-wide">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ textAlign: 'center', marginBottom: 64 }}>
          <motion.h2 variants={fadeUp} style={{ fontSize: 'clamp(1.75rem, 3vw, 2.5rem)', marginBottom: 16, letterSpacing: '-0.03em' }}>
            The Silent Epidemic of Nutrient Deficiencies
          </motion.h2>
          <motion.p variants={fadeUp} style={{ fontSize: '1.0625rem', color: 'var(--c-text-secondary)', maxWidth: 600, margin: '0 auto' }}>
            Hidden deficiencies lead to chronic fatigue, weakened immunity, and long-term health complications.
            Early detection changes outcomes.
          </motion.p>
        </motion.div>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20 }}>
          {stats.map(s => (
            <motion.div key={s.number} variants={fadeUp} className="card" style={{ padding: 32, textAlign: 'center', background: 'var(--c-bg)' }}>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '2.5rem', fontWeight: 800, color: 'var(--c-primary)', letterSpacing: '-0.04em', marginBottom: 8 }}>
                {s.number}
              </div>
              <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', lineHeight: 1.5 }}>{s.label}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

/* ───────────── How It Works ───────────── */
function HowItWorks() {
  const steps = [
    { num: '01', title: 'Assessment', desc: 'Complete a comprehensive health questionnaire covering diet, lifestyle, symptoms, and medical history.', icon: Scan },
    { num: '02', title: 'AI Prediction', desc: 'Our XGBoost ensemble model simultaneously screens 11 essential nutrients with calibrated probability scoring.', icon: Brain },
    { num: '03', title: 'Risk Analysis', desc: 'SHAP explainability engine identifies the exact factors driving your deficiency risk and protective counterbalances.', icon: Target },
    { num: '04', title: 'Recovery Plan', desc: 'Receive personalized food recommendations, synergistic pairings, and a structured 30-day recovery roadmap.', icon: Utensils },
  ]
  return (
    <section id="how-it-works" className="section">
      <div className="container-wide">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ textAlign: 'center', marginBottom: 64 }}>
          <motion.h2 variants={fadeUp} style={{ fontSize: 'clamp(1.75rem, 3vw, 2.5rem)', marginBottom: 16, letterSpacing: '-0.03em' }}>
            How It Works
          </motion.h2>
          <motion.p variants={fadeUp} style={{ fontSize: '1.0625rem', color: 'var(--c-text-secondary)', maxWidth: 520, margin: '0 auto' }}>
            From screening to recovery in four evidence-based steps.
          </motion.p>
        </motion.div>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24, position: 'relative' }}>
          <div style={{
            position: 'absolute', top: 48, left: 'calc(12.5% + 24px)', right: 'calc(12.5% + 24px)',
            height: 1, background: 'var(--c-border)', zIndex: 0,
          }} />
          {steps.map((s) => (
            <motion.div key={s.num} variants={fadeUp} style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
              <div style={{
                width: 56, height: 56, borderRadius: 16, background: 'var(--c-card)',
                border: '2px solid var(--c-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 20px',
              }}>
                <s.icon size={24} color="var(--c-primary)" />
              </div>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '0.75rem', fontWeight: 700, color: 'var(--c-primary)', marginBottom: 8, letterSpacing: '0.06em' }}>
                STEP {s.num}
              </div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: 10 }}>{s.title}</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', lineHeight: 1.6 }}>{s.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

/* ───────────── Bento Grid ───────────── */
function BentoGrid() {
  const features = [
    { title: 'Multi-Nutrient Prediction', desc: 'Simultaneously screen 11 essential nutrients with calibrated XGBoost probability scores.', icon: BarChart3, span: 'col-span-1' },
    { title: 'Explainable AI', desc: 'SHAP-powered feature attribution reveals exactly what drives your risk profile.', icon: Brain, span: 'col-span-1' },
    { title: 'Risk Factor Analysis', desc: 'Categorized risk drivers across dietary, lifestyle, symptom, medical, and supplement dimensions.', icon: Shield, span: 'col-span-1' },
    { title: 'Nutrient Interactions', desc: 'Biochemical synergies and competitive absorptions mapped for clinical decision support.', icon: Zap, span: 'col-span-2' },
    { title: 'Personalized Recommendations', desc: 'Dietary-filtered whole food recommendations with bioavailability scoring and preparation tips.', icon: Utensils, span: 'col-span-1' },
    { title: 'Recovery Roadmaps', desc: 'Progressive 7, 14, and 30-day recovery plans from acute replenishment to systemic resilience.', icon: TrendingUp, span: 'col-span-1' },
    { title: 'Health Reports', desc: 'Clinical-grade PDF reports with executive summaries, prediction matrices, and physician guidance.', icon: FileText, span: 'col-span-1' },
    { title: 'Clinical Insights', desc: 'Dual-audience narratives for patients and healthcare professionals with ICD-10 code references.', icon: Sparkles, span: 'col-span-1' },
  ]
  return (
    <section id="features" className="section" style={{ background: 'var(--c-card)' }}>
      <div className="container-wide">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ textAlign: 'center', marginBottom: 64 }}>
          <motion.h2 variants={fadeUp} style={{ fontSize: 'clamp(1.75rem, 3vw, 2.5rem)', marginBottom: 16, letterSpacing: '-0.03em' }}>
            Built for Clinical Precision
          </motion.h2>
          <motion.p variants={fadeUp} style={{ fontSize: '1.0625rem', color: 'var(--c-text-secondary)', maxWidth: 560, margin: '0 auto' }}>
            Every module designed for evidence-based nutritional intelligence at production scale.
          </motion.p>
        </motion.div>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          {features.map(f => (
            <motion.div key={f.title} variants={fadeUp} className="card card-hover"
              style={{
                padding: 28, gridColumn: f.span === 'col-span-2' ? 'span 2' : 'span 1',
                cursor: 'default', background: 'var(--c-bg)',
              }}
            >
              <div style={{
                width: 40, height: 40, borderRadius: 10, background: 'var(--c-surface-tint)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16,
              }}>
                <f.icon size={20} color="var(--c-primary)" />
              </div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.01em' }}>{f.title}</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--c-muted)', lineHeight: 1.6 }}>{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

/* ───────────── Architecture ───────────── */
function Architecture() {
  const pipeline = [
    { label: 'Health Assessment', sub: '10-field clinical questionnaire' },
    { label: 'Feature Engineering', sub: 'BMI, nutrient interactions, risk scoring' },
    { label: 'Prediction Engine', sub: '11 calibrated XGBoost classifiers' },
    { label: 'Explainable AI', sub: 'SHAP attribution & clinical reasoning' },
    { label: 'Risk Analysis', sub: 'Nutrient interaction compounding' },
    { label: 'Recommendation Engine', sub: 'Personalized foods & lifestyle' },
    { label: 'Recovery Planning', sub: '7/14/30-day progressive roadmap' },
    { label: 'Report Generation', sub: 'Dashboard, PDF, & clinical insights' },
  ]
  return (
    <section id="architecture" className="section">
      <div className="container-narrow">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ textAlign: 'center', marginBottom: 64 }}>
          <motion.h2 variants={fadeUp} style={{ fontSize: 'clamp(1.75rem, 3vw, 2.5rem)', marginBottom: 16, letterSpacing: '-0.03em' }}>
            End-to-End Intelligence Pipeline
          </motion.h2>
          <motion.p variants={fadeUp} style={{ fontSize: '1.0625rem', color: 'var(--c-text-secondary)', maxWidth: 520, margin: '0 auto' }}>
            Eight integrated modules from intake to clinical reporting.
          </motion.p>
        </motion.div>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
          {pipeline.map((step, i) => (
            <motion.div key={step.label} variants={fadeUp}>
              <div style={{
                padding: '16px 32px', background: 'var(--c-card)', border: '1px solid var(--c-border)',
                borderRadius: 12, textAlign: 'center', minWidth: 320,
                boxShadow: 'var(--c-shadow-sm)',
              }}>
                <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--c-secondary)', letterSpacing: '-0.01em' }}>{step.label}</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', marginTop: 4 }}>{step.sub}</div>
              </div>
              {i < pipeline.length - 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '6px 0' }}>
                  <div style={{ width: 1, height: 24, background: 'var(--c-border)' }} />
                </div>
              )}
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

/* ───────────── Benefits ───────────── */
function Benefits() {
  const items = [
    { title: 'Early Risk Detection', desc: 'Identify subclinical deficiencies before they cause symptoms.', icon: Shield },
    { title: 'Personalized Guidance', desc: 'Dietary-filtered recommendations tailored to your biology.', icon: Utensils },
    { title: 'Explainable Results', desc: 'Understand exactly what factors contribute to your risk.', icon: Brain },
    { title: 'Better Decisions', desc: 'Evidence-based insights for patients and practitioners.', icon: Heart },
    { title: 'Progress Tracking', desc: 'Monitor recovery across structured 30-day roadmaps.', icon: Activity },
  ]
  return (
    <section className="section" style={{ background: 'var(--c-card)' }}>
      <div className="container-wide">
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ textAlign: 'center', marginBottom: 64 }}>
          <motion.h2 variants={fadeUp} style={{ fontSize: 'clamp(1.75rem, 3vw, 2.5rem)', marginBottom: 16, letterSpacing: '-0.03em' }}>
            Why NutriScan AI
          </motion.h2>
        </motion.div>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-60px' }} variants={stagger} style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 20 }}>
          {items.map(b => (
            <motion.div key={b.title} variants={fadeUp} className="card" style={{ padding: 28, textAlign: 'center', background: 'var(--c-bg)' }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12, background: 'var(--c-surface-tint)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 16px',
              }}>
                <b.icon size={22} color="var(--c-primary)" />
              </div>
              <h3 style={{ fontSize: '0.9375rem', fontWeight: 700, marginBottom: 8 }}>{b.title}</h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', lineHeight: 1.5 }}>{b.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

/* ───────────── CTA ───────────── */
function CTA() {
  return (
    <section className="section" style={{ background: 'var(--c-surface-warm)' }}>
      <div className="container-narrow" style={{ textAlign: 'center' }}>
        <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={stagger}>
          <motion.h2 variants={fadeUp} style={{
            fontFamily: 'var(--font-heading)', fontSize: 'clamp(2rem, 3.5vw, 2.75rem)',
            fontWeight: 800, letterSpacing: '-0.03em', marginBottom: 20,
          }}>
            Take Control of Your Nutritional Health
          </motion.h2>
          <motion.p variants={fadeUp} style={{ fontSize: '1.0625rem', color: 'var(--c-text-secondary)', maxWidth: 480, margin: '0 auto 36px' }}>
            Complete your free assessment in under 5 minutes and receive AI-powered insights
            personalized to your biology.
          </motion.p>
          <motion.div variants={fadeUp}>
            <Link to="/assessment" className="btn-primary" style={{ padding: '16px 40px', fontSize: '1rem' }}>
              Start Free Assessment <ChevronRight size={18} />
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

/* ───────────── Footer ───────────── */
function Footer() {
  const cols = [
    { title: 'Product', links: ['Assessment', 'Dashboard', 'Reports', 'API'] },
    { title: 'Resources', links: ['Documentation', 'Architecture', 'Clinical Evidence', 'Blog'] },
    { title: 'Company', links: ['About', 'Careers', 'Contact', 'Press'] },
    { title: 'Legal', links: ['Privacy', 'Terms', 'HIPAA', 'Security'] },
  ]
  return (
    <footer style={{ borderTop: '1px solid var(--c-border)', paddingTop: 56, paddingBottom: 40, background: 'var(--c-bg)' }}>
      <div className="container-wide">
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr repeat(4, 1fr)', gap: 40, marginBottom: 48 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <div style={{
                width: 28, height: 28, borderRadius: 7, background: 'var(--c-primary)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Leaf size={15} color="white" />
              </div>
              <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '1rem', color: 'var(--c-secondary)' }}>
                NutriScan AI
              </span>
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--c-muted)', lineHeight: 1.6, maxWidth: 240 }}>
              AI-powered nutritional intelligence for preventive healthcare.
            </p>
          </div>
          {cols.map(col => (
            <div key={col.title}>
              <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--c-secondary)', marginBottom: 16 }}>{col.title}</div>
              {col.links.map(link => (
                <a key={link} href="#" style={{ display: 'block', fontSize: '0.8125rem', color: 'var(--c-muted)', textDecoration: 'none', marginBottom: 10 }}>{link}</a>
              ))}
            </div>
          ))}
        </div>
        {/* CDSS Statutory Regulatory Notice */}
        <div style={{
          marginTop: 24,
          marginBottom: 32,
          padding: '14px 18px',
          borderRadius: 10,
          background: 'var(--c-glass-bg, rgba(20, 184, 166, 0.04))',
          border: '1px solid var(--c-border, rgba(255, 255, 255, 0.08))',
          display: 'flex',
          gap: 12,
          alignItems: 'flex-start'
        }}>
          <Shield size={16} color="var(--c-primary)" style={{ flexShrink: 0, marginTop: 2 }} />
          <p style={{
            fontSize: '0.725rem',
            lineHeight: 1.5,
            color: 'var(--c-muted)',
            margin: 0
          }}>
            <strong style={{ color: 'var(--c-secondary)' }}>Clinical Decision Support System (CDSS) Notice:</strong> NutriScan is an informational clinical decision support platform compliant with FDA Section 520(o)(1)(E) and European Medical Device Regulation (EU MDR 2017/745 Class I non-device software). NutriScan recommendations, predictive biomarker trajectories, and meal plans do not constitute formal medical diagnosis, pharmacological prescription, or a physician-patient relationship. Always consult a licensed healthcare practitioner prior to commencing high-potency nutritional interventions or altering prescribed regimens.
          </p>
        </div>

        <div style={{ borderTop: '1px solid var(--c-border)', paddingTop: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-muted-light)' }}>© 2026 NutriScan AI. All rights reserved.</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--c-muted-light)' }}>Built with clinical precision & regulatory integrity.</p>
        </div>
      </div>
    </footer>
  )
}

/* ───────────── Landing Page ───────────── */
export default function LandingPage() {
  return (
    <div style={{ background: 'var(--c-bg)' }}>
      <Navbar />
      <Hero />
      <ProblemStatement />
      <HowItWorks />
      <BentoGrid />
      <Architecture />
      <Benefits />
      <CTA />
      <Footer />
    </div>
  )
}
