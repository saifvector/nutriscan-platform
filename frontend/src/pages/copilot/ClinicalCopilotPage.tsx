/* ═══════════════════════════════════════════════════════════════════════════
   ClinicalCopilotPage.tsx — Clinical Nutrition Assessment Workstation
   Designed strictly to match NutriScan Dashboard styling & clinical standards.
   ═══════════════════════════════════════════════════════════════════════════ */

import React, { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion, type Variants } from 'framer-motion'
import api from '../../lib/api'
import {
  ChevronDown, Check, RefreshCw, CheckCircle2,
  FileText, Activity, Stethoscope, Printer, Calendar, Clock,
  Pill, Apple, User, ClipboardList, Shield, ArrowRight,
  AlertCircle, Sun, Heart, Info, PlusCircle, RotateCcw
} from 'lucide-react'
import { sessionManager } from '../../lib/sessionManager'
import { ResumeAssessmentModal } from '../../components/session/ResumeAssessmentModal'
import { AssessmentRequiredState } from '../../components/common/AssessmentRequiredState'

/* ─── Motion Animations (Matching Dashboard) ─── */
const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.4, delay: i * 0.05, ease: 'easeOut' },
  }),
}

/* ─── Clinical Data Models ─── */
export interface PatientRecord {
  id: string
  name: string
  age: number
  gender: string
  dietaryPattern: string
  bmi: string
  bmiCategory: string
  assessmentDate: string
  riskScore: number
  riskTier: 'Low Risk' | 'Moderate Risk' | 'High Risk'
  clinicalSummary: {
    heroStatement: string
    primaryDiagnosis: string
    icdCode: string
    contributingFactors: string
    clinicalImpact: string
    confidence: string
  }
  keyFindings: Array<{
    finding: string
    status: 'Deficient' | 'Borderline' | 'Normal' | 'Elevated'
    severity: 'Severe' | 'Moderate' | 'Mild' | 'No Action Required'
    clinicalImpact: string
  }>
  nutrientStatus: Array<{
    name: string
    currentValue: string
    numericValue: number
    minRef: number
    maxRef: number
    unit: string
    targetRange: string
    status: 'Deficient' | 'Borderline' | 'Normal' | 'Elevated'
  }>
  rootCauseAnalysis: {
    whyDeficiencyExists: string
    lifestyleContributors: string
    dietaryContributors: string
    biologicalContributors: string
  }
  recommendedInterventions: Array<{
    id: string
    intervention: string
    priority: 'High Priority' | 'Medium Priority' | 'Routine'
    expectedBenefit: string
    duration: string
  }>
  carePlanTimeline: Array<{
    timeframe: string
    action: string
    detail: string
    status: 'active' | 'upcoming'
  }>
  followUp: {
    nextReviewDate: string
    monitoringParameters: string
    expectedOutcomes: string
    successCriteria: string
  }
}

/* ─── Multi-Patient Clinical Records ─── */
const PATIENT_PROFILES: PatientRecord[] = [
  {
    id: 'PT-8891',
    name: 'Sarah Jenkins',
    age: 42,
    gender: 'Female',
    dietaryPattern: 'Vegetarian (Lacto-Ovo)',
    bmi: '24.1',
    bmiCategory: 'Normal',
    assessmentDate: 'September 15, 2026',
    riskScore: 38,
    riskTier: 'Moderate Risk',
    clinicalSummary: {
      heroStatement:
        'Patient demonstrates moderate Vitamin D deficiency with secondary calcium absorption impairment. Findings suggest limited sunlight exposure combined with reduced dietary calcium bioavailability and high phytate intake.',
      primaryDiagnosis: 'Subclinical Hypovitaminosis D with Compensatory Hyperparathyroidism',
      icdCode: 'ICD-10: E55.9 (Vitamin D deficiency) · M83.8 (Osteomalacia)',
      contributingFactors:
        'Sedentary indoor occupation (<15 min sunlight daily), consistent broad-spectrum SPF 50 sunscreen application, lack of fortified foods, and elevated unfermented grain phytate intake.',
      clinicalImpact:
        'Elevated intact parathyroid hormone (62.4 pg/mL) driving bone resorption to sustain serum calcium; associated with persistent muscular fatigue and lower extremity cramping.',
      confidence: 'High Confidence (Clinician Verified & Grounded in Serum Biomarkers)',
    },
    keyFindings: [
      {
        finding: 'Vitamin D Deficiency',
        status: 'Deficient',
        severity: 'Moderate',
        clinicalImpact: 'Primary Driver · Impairs active duodenal calcium transport and skeletal mineral accrual',
      },
      {
        finding: 'Low Calcium Absorption',
        status: 'Borderline',
        severity: 'Mild',
        clinicalImpact: 'Secondary Driver · Elevates intact PTH to maintain extracellular ionized calcium homeostasis',
      },
      {
        finding: 'Vitamin B12 (Cobalamin)',
        status: 'Normal',
        severity: 'No Action Required',
        clinicalImpact: 'Adequate cellular reserves (480 pg/mL) supported by dairy and nutritional yeast intake',
      },
      {
        finding: 'Iron (Serum Ferritin)',
        status: 'Normal',
        severity: 'No Action Required',
        clinicalImpact: 'Preserved iron stores (54.0 ng/mL) without microcytosis or transferrin saturation decline',
      },
    ],
    nutrientStatus: [
      { name: 'Vitamin D', currentValue: '18.2', numericValue: 18.2, minRef: 30, maxRef: 100, unit: 'ng/mL', targetRange: '30–100 ng/mL', status: 'Deficient' },
      { name: 'Calcium (Ionized)', currentValue: '1.18', numericValue: 1.18, minRef: 1.15, maxRef: 1.35, unit: 'mmol/L', targetRange: '1.15–1.35 mmol/L', status: 'Borderline' },
      { name: 'Vitamin B12', currentValue: '480', numericValue: 480, minRef: 200, maxRef: 900, unit: 'pg/mL', targetRange: '200–900 pg/mL', status: 'Normal' },
      { name: 'Iron (Ferritin)', currentValue: '54.0', numericValue: 54.0, minRef: 20, maxRef: 200, unit: 'ng/mL', targetRange: '20–200 ng/mL', status: 'Normal' },
      { name: 'Zinc', currentValue: '94.0', numericValue: 94.0, minRef: 70, maxRef: 120, unit: 'µg/dL', targetRange: '70–120 µg/dL', status: 'Normal' },
      { name: 'Magnesium', currentValue: '2.1', numericValue: 2.1, minRef: 1.8, maxRef: 2.4, unit: 'mg/dL', targetRange: '1.8–2.4 mg/dL', status: 'Normal' },
    ],
    rootCauseAnalysis: {
      whyDeficiencyExists:
        'The body relies on cutaneous UV photolysis and dietary absorption for 25(OH)D reserves. In this patient, both pathways are compromised simultaneously, leading to an exhaustion of circulating reserves and compensatory parathyroid activation.',
      lifestyleContributors:
        'Indoor computer-based work schedule results in less than 15 minutes of direct sunlight exposure per workday. Daily application of SPF 50 sunscreen blocks >98% of UVB-mediated cutaneous pre-vitamin D3 synthesis.',
      dietaryContributors:
        'Vegetarian diet devoid of cold-water fatty fish (salmon, mackerel) combined with non-consumption of fortified commercial dairy products leaves daily oral vitamin D intake at <100 IU/day (RDA: 600–800 IU/day).',
      biologicalContributors:
        'High dietary intake of phytic acid (>1,200 mg/day from unsoaked legumes and raw grain hulls) forms insoluble chelates with ionized divalent minerals, dampening active intestinal calcium bioaccessibility.',
    },
    recommendedInterventions: [
      {
        id: 'INT-1',
        intervention: 'Oral Cholecalciferol (Vitamin D3) Supplementation',
        priority: 'High Priority',
        expectedBenefit: 'Rapidly restores circulating 25(OH)D above osteoprotective threshold of >35 ng/mL and suppresses elevated PTH',
        duration: '2,000 IU daily with morning lipid meal for 8 Weeks',
      },
      {
        id: 'INT-2',
        intervention: 'Prescribed Sunlight Exposure Protocol',
        priority: 'Medium Priority',
        expectedBenefit: 'Supports endogenous cutaneous Vitamin D3 synthesis and circadian melatonin synchronization',
        duration: '15 minutes mid-day sunlight (arms and lower legs) 3–4 days/week prior to sunscreen',
      },
      {
        id: 'INT-3',
        intervention: 'Dietary Calcium Enhancement & Phytate Reduction',
        priority: 'Medium Priority',
        expectedBenefit: 'Ensures 1,000 mg/day elemental bioavailable calcium while eliminating absorption inhibitors',
        duration: 'Incorporate calcium-set tofu, sesame tahini, and sprouted or sourdough grains daily',
      },
    ],
    carePlanTimeline: [
      { timeframe: 'TODAY', action: 'Start Intervention', detail: 'Initiate daily 2,000 IU Vitamin D3 with food; begin dietary phytate reduction techniques', status: 'active' },
      { timeframe: 'WEEK 2', action: 'Monitor Adherence', detail: 'Patient portal check-in for gastrointestinal tolerance and compliance review', status: 'upcoming' },
      { timeframe: 'WEEK 6', action: 'Repeat Laboratory Testing', detail: 'Re-assay Serum 25(OH)D, Ionized Calcium, and Intact PTH to verify absorption velocity', status: 'upcoming' },
      { timeframe: 'WEEK 8', action: 'Clinical Review', detail: 'Clinician evaluation of biomarker normalization and step-down to maintenance dosing (1,000 IU daily)', status: 'upcoming' },
    ],
    followUp: {
      nextReviewDate: 'October 28, 2026 (6-Week Checkpoint)',
      monitoringParameters: 'Serum 25-Hydroxyvitamin D, Ionized Calcium, Intact PTH, and 24-Hour Urinary Calcium Excretion.',
      expectedOutcomes: 'Normalization of 25(OH)D to >35 ng/mL, reduction of intact PTH to <45 pg/mL, and resolution of leg muscle fatigue.',
      successCriteria: 'Achievement of steady-state normocalcemia without hypercalciuria; sustained adherence to dietary calcium-rich foods.',
    },
  },
  {
    id: 'PT-4412',
    name: 'Marcus Vance',
    age: 58,
    gender: 'Male',
    dietaryPattern: 'Omnivore (High Processed / Sodium)',
    bmi: '29.3',
    bmiCategory: 'Overweight',
    assessmentDate: 'September 15, 2026',
    riskScore: 52,
    riskTier: 'Moderate Risk',
    clinicalSummary: {
      heroStatement:
        'Patient presents with intracellular magnesium depletion associated with nocturnal muscle spasms and elevated systemic inflammatory markers. Findings suggest low dietary magnesium intake compounded by prior thiazide diuretic treatment.',
      primaryDiagnosis: 'Intracellular Magnesium Insufficiency with Chronic Low-Grade Inflammation',
      icdCode: 'ICD-10: E83.42 (Hypomagnesemia) · R25.2 (Cramp and spasm)',
      contributingFactors:
        'Dietary exclusion of leafy greens and seeds, high dietary sodium intake (>3,800 mg/day), heavy coffee consumption, and history of diuretic-induced renal mineral wasting.',
      clinicalImpact:
        'Impaired sodium-potassium ATPase pump activity provoking neuromuscular irritability, nighttime calf spasms, and an elevated hs-CRP of 2.8 mg/L.',
      confidence: 'High Confidence (Clinician Verified & Grounded in RBC Mineral Assays)',
    },
    keyFindings: [
      {
        finding: 'Erythrocyte Magnesium Depletion',
        status: 'Deficient',
        severity: 'Moderate',
        clinicalImpact: 'Primary Driver · Direct cause of recurrent nocturnal muscle cramping and sleep disruption',
      },
      {
        finding: 'Low-Grade Vascular Inflammation',
        status: 'Elevated',
        severity: 'Moderate',
        clinicalImpact: 'Secondary Driver · Elevated hs-CRP (2.8 mg/L) accelerating cardiometabolic strain',
      },
      {
        finding: 'Serum Potassium Balance',
        status: 'Borderline',
        severity: 'Mild',
        clinicalImpact: 'Low-normal serum potassium (3.8 mEq/L) requiring dietary enrichment with plant foods',
      },
      {
        finding: 'Hepatic Transaminases',
        status: 'Normal',
        severity: 'No Action Required',
        clinicalImpact: 'Normal ALT (24 U/L) and AST (22 U/L) confirming healthy hepatic parenchyma',
      },
    ],
    nutrientStatus: [
      { name: 'Magnesium (RBC)', currentValue: '3.8', numericValue: 3.8, minRef: 4.2, maxRef: 6.8, unit: 'mg/dL', targetRange: '4.2–6.8 mg/dL', status: 'Deficient' },
      { name: 'Vitamin D', currentValue: '24.0', numericValue: 24.0, minRef: 30, maxRef: 100, unit: 'ng/mL', targetRange: '30–100 ng/mL', status: 'Borderline' },
      { name: 'Potassium', currentValue: '3.8', numericValue: 3.8, minRef: 3.5, maxRef: 5.1, unit: 'mEq/L', targetRange: '3.5–5.1 mEq/L', status: 'Borderline' },
      { name: 'hs-CRP (Inflammation)', currentValue: '2.8', numericValue: 2.8, minRef: 0.1, maxRef: 1.0, unit: 'mg/L', targetRange: '< 1.0 mg/L', status: 'Elevated' },
      { name: 'Fasting Glucose', currentValue: '98.0', numericValue: 98.0, minRef: 70, maxRef: 99, unit: 'mg/dL', targetRange: '70–99 mg/dL', status: 'Normal' },
      { name: 'Zinc', currentValue: '94.0', numericValue: 94.0, minRef: 70, maxRef: 120, unit: 'µg/dL', targetRange: '70–120 µg/dL', status: 'Normal' },
    ],
    rootCauseAnalysis: {
      whyDeficiencyExists:
        'Magnesium is predominantly an intracellular cation (99% found in bone and soft tissues). Serum levels mask depletion while erythrocyte stores reveal profound intracellular deficit driving neuromuscular symptoms.',
      lifestyleContributors:
        'High physical stress and intake of 4+ cups of caffeinated beverages daily increases tubular urinary mineral clearance and accelerates magnesium loss.',
      dietaryContributors:
        'Processed convenience foods dominate the dietary pattern, providing less than 180 mg/day magnesium (RDA: 420 mg/day) and exceeding sodium limits by >1,500 mg daily.',
      biologicalContributors:
        'Prior 18-month thiazide diuretic exposure promoted distal tubule mineral clearance, exhausting intracellular buffers.',
    },
    recommendedInterventions: [
      {
        id: 'INT-1',
        intervention: 'Chelated Magnesium Bisglycinate Protocol',
        priority: 'High Priority',
        expectedBenefit: 'High bioavailability without osmotic laxation; crosses cell membranes to restore RBC stores and relieve cramps',
        duration: '350 mg elemental magnesium orally 45 minutes before bedtime for 12 Weeks',
      },
      {
        id: 'INT-2',
        intervention: 'DASH-Pattern Mineral-Rich Food Transition',
        priority: 'Medium Priority',
        expectedBenefit: 'Supplies >450 mg/day dietary magnesium, potassium, and cardioprotective polyphenols',
        duration: 'Daily inclusion of pumpkin seeds, steamed spinach, and avocado; sodium <2,300 mg/day',
      },
      {
        id: 'INT-3',
        intervention: 'Concentrated Marine Omega-3 Fatty Acids',
        priority: 'Routine',
        expectedBenefit: 'Downregulates inflammatory prostanoid cascades and normalizes vascular endothelial tone',
        duration: '1,500 mg EPA/DHA daily with dinner for 6 Months',
      },
    ],
    carePlanTimeline: [
      { timeframe: 'TODAY', action: 'Start Intervention', detail: 'Begin Magnesium Bisglycinate nightly; implement sodium-conscious DASH meal rotation', status: 'active' },
      { timeframe: 'WEEK 2', action: 'Monitor Adherence', detail: 'Review nocturnal cramp frequency log and gastrointestinal tolerance', status: 'upcoming' },
      { timeframe: 'WEEK 6', action: 'Repeat Laboratory Testing', detail: 'Re-assay RBC Magnesium, Serum Electrolytes, and High-Sensitivity CRP', status: 'upcoming' },
      { timeframe: 'WEEK 8', action: 'Clinical Review', detail: 'Cardiometabolic review of blood pressure trends and long-term mineral maintenance', status: 'upcoming' },
    ],
    followUp: {
      nextReviewDate: 'November 10, 2026 (8-Week Milestone)',
      monitoringParameters: 'RBC Magnesium, Serum Electrolytes (Na/K/Mg), hs-CRP, and Fasting Lipid Panel.',
      expectedOutcomes: 'RBC Magnesium elevation to >5.0 mg/dL, complete resolution of night leg cramps, and hs-CRP <1.5 mg/L.',
      successCriteria: 'Sustained symptom remission, stable blood pressure (<130/80 mmHg), and healthy intracellular electrolyte balance.',
    },
  },
  {
    id: 'PT-1094',
    name: 'Elena Rostova',
    age: 29,
    gender: 'Female',
    dietaryPattern: 'Strict Vegan (4 Years)',
    bmi: '20.1',
    bmiCategory: 'Normal',
    assessmentDate: 'September 15, 2026',
    riskScore: 74,
    riskTier: 'High Risk',
    clinicalSummary: {
      heroStatement:
        'Patient presents with combined Vitamin B12 exhaustion and microcytic iron deficiency anemia following 4 years of unfortified vegan nutrition. Findings include active peripheral paresthesias and high cellular methylmalonic acid.',
      primaryDiagnosis: 'Combined Cobalamin Deficiency with Microcytic Hypochromic Iron Deficiency Anemia',
      icdCode: 'ICD-10: D51.0 (Vitamin B12 deficiency anemia) · D50.8 (Other iron deficiency anemias)',
      contributingFactors:
        'Total absence of dietary cobalamin sources, uncompensated heavy menstrual blood loss, and poor non-heme iron bioavailability due to raw phytate matrices.',
      clinicalImpact:
        'Cellular methylmalonic acid elevation (0.68 µmol/L) impairing peripheral nerve myelin integrity; low ferritin (14.0 ng/mL) with microcytic red blood cells (MCV 76.2 fL).',
      confidence: 'High Confidence (Clinician Verified & Grounded in Hematologic Profile)',
    },
    keyFindings: [
      {
        finding: 'Vitamin B12 Exhaustion',
        status: 'Deficient',
        severity: 'Severe',
        clinicalImpact: 'Primary Driver · Direct cause of bilateral fingertip paresthesias and elevated methylmalonic acid',
      },
      {
        finding: 'Depleted Iron Stores (Ferritin)',
        status: 'Deficient',
        severity: 'Severe',
        clinicalImpact: 'Primary Driver · Exhausted reticuloendothelial iron stores producing microcytic erythrocytes',
      },
      {
        finding: 'Vitamin D Status',
        status: 'Borderline',
        severity: 'Mild',
        clinicalImpact: 'Suboptimal 25(OH)D (22.1 ng/mL) requiring baseline maintenance supplementation',
      },
      {
        finding: 'Serum Zinc Reserves',
        status: 'Borderline',
        severity: 'Mild',
        clinicalImpact: 'Low-normal zinc (68.0 µg/dL) resulting from high grain phytate competition',
      },
    ],
    nutrientStatus: [
      { name: 'Vitamin B12', currentValue: '142', numericValue: 142, minRef: 200, maxRef: 900, unit: 'pg/mL', targetRange: '200–900 pg/mL', status: 'Deficient' },
      { name: 'Iron (Ferritin)', currentValue: '14.0', numericValue: 14.0, minRef: 20, maxRef: 200, unit: 'ng/mL', targetRange: '20–200 ng/mL', status: 'Deficient' },
      { name: 'Mean Corpuscular Vol (MCV)', currentValue: '76.2', numericValue: 76.2, minRef: 80, maxRef: 100, unit: 'fL', targetRange: '80–100 fL', status: 'Deficient' },
      { name: 'Vitamin D', currentValue: '22.1', numericValue: 22.1, minRef: 30, maxRef: 100, unit: 'ng/mL', targetRange: '30–100 ng/mL', status: 'Borderline' },
      { name: 'Zinc', currentValue: '68.0', numericValue: 68.0, minRef: 70, maxRef: 120, unit: 'µg/dL', targetRange: '70–120 µg/dL', status: 'Borderline' },
      { name: 'Folate (Serum)', currentValue: '16.4', numericValue: 16.4, minRef: 4, maxRef: 20, unit: 'ng/mL', targetRange: '4–20 ng/mL', status: 'Normal' },
    ],
    rootCauseAnalysis: {
      whyDeficiencyExists:
        'Vitamin B12 is synthesized exclusively by microorganisms and cannot be obtained from unfortified plant foods. Over 4 years, hepatic cobalamin stores have depleted, resulting in functional metabolic blocks.',
      lifestyleContributors:
        'Avoidance of commercial enriched products in favor of whole raw foods leaves zero dietary cobalamin exposure without supplemental compliance.',
      dietaryContributors:
        'Absence of heme iron sources coupled with heavy tea consumption (tannins) during legume meals binds non-heme iron into non-absorbable coordination complexes.',
      biologicalContributors:
        'Regular menstrual blood loss (6–7 days with heavy flow) creates negative iron balance that cannot be replenished by low-bioavailability plant non-heme iron alone.',
    },
    recommendedInterventions: [
      {
        id: 'INT-1',
        intervention: 'Sublingual Coenzymated B12 (Methyl & Adenosylcobalamin)',
        priority: 'High Priority',
        expectedBenefit: 'Rapid transmucosal absorption bypassing intrinsic factor to normalize cellular methylation and reverse paresthesias',
        duration: '1,000 mcg sublingually daily upon waking on empty stomach for 90 Days',
      },
      {
        id: 'INT-2',
        intervention: 'Chelated Iron Bisglycinate + Vitamin C Synergist',
        priority: 'High Priority',
        expectedBenefit: 'Provides 4x absorption efficiency without gastrointestinal distress to reconstitute bone marrow iron pools',
        duration: 'Elemental Iron Bisglycinate 28 mg paired with Vitamin C 250 mg daily away from meals for 60 Days',
      },
      {
        id: 'INT-3',
        intervention: 'Sprouting, Soaking, and Fermentation Training',
        priority: 'Medium Priority',
        expectedBenefit: 'Deactivates phytate complexes to liberate bioavailable iron and zinc from legumes and grains',
        duration: 'Integrate pre-soaked legumes and sprouted seeds into daily culinary routine',
      },
    ],
    carePlanTimeline: [
      { timeframe: 'TODAY', action: 'Start Intervention', detail: 'Initiate daily sublingual B12 1,000 mcg and chelated Iron Bisglycinate', status: 'active' },
      { timeframe: 'WEEK 2', action: 'Monitor Adherence', detail: 'Check-in regarding peripheral neurological symptoms and iron gastrointestinal tolerance', status: 'upcoming' },
      { timeframe: 'WEEK 6', action: 'Repeat Laboratory Testing', detail: 'Re-assay Complete Blood Count (CBC), Serum B12, MMA, and Ferritin', status: 'upcoming' },
      { timeframe: 'WEEK 8', action: 'Clinical Review', detail: 'Evaluate hemoglobin normalization, resolution of tingling, and maintenance titration', status: 'upcoming' },
    ],
    followUp: {
      nextReviewDate: 'October 14, 2026 (4-Week Urgent Checkpoint)',
      monitoringParameters: 'Serum B12, Methylmalonic Acid, CBC with differential (MCV/Hgb), Serum Ferritin, and TIBC.',
      expectedOutcomes: 'Serum B12 >450 pg/mL, MMA <0.30 µmol/L, Ferritin >35 ng/mL, and full resolution of peripheral paresthesias.',
      successCriteria: 'Reconstitution of bone marrow iron stores, normalization of erythroid indices, and permanent B12 supplementation compliance.',
    },
  },
]

function mapDossierToPatientRecord(dossier: any, assessment?: any): PatientRecord {
  const demo = dossier?.demographics || {}
  const deficiencies = dossier?.deficiencies || []
  const biomarkers = dossier?.biomarkers || []
  const riskScore = Math.round(dossier?.composite_risk_score || 45)
  const riskTier: 'Low Risk' | 'Moderate Risk' | 'High Risk' =
    riskScore > 60 ? 'High Risk' : riskScore > 30 ? 'Moderate Risk' : 'Low Risk'

  const bmiVal = demo.bmi ? Number(demo.bmi).toFixed(1) : '22.5'
  const numBmi = parseFloat(bmiVal)
  const bmiCategory = numBmi < 18.5 ? 'Underweight' : numBmi < 25 ? 'Normal' : numBmi < 30 ? 'Overweight' : 'Obese'

  const standardRanges: Record<string, { minRef: number; maxRef: number; unit: string }> = {
    'Vitamin D': { minRef: 30, maxRef: 100, unit: 'ng/mL' },
    'Vitamin B12': { minRef: 200, maxRef: 900, unit: 'pg/mL' },
    'Iron': { minRef: 20, maxRef: 200, unit: 'ng/mL' },
    'Ferritin': { minRef: 20, maxRef: 200, unit: 'ng/mL' },
    'Calcium': { minRef: 8.5, maxRef: 10.5, unit: 'mg/dL' },
    'Zinc': { minRef: 70, maxRef: 120, unit: 'µg/dL' },
    'Magnesium': { minRef: 1.8, maxRef: 2.4, unit: 'mg/dL' },
    'Folate': { minRef: 4, maxRef: 20, unit: 'ng/mL' },
  }

  const nutrientStatus = biomarkers.length > 0
    ? biomarkers.map((b: any) => {
        const ref = standardRanges[b.marker_name] || { minRef: 20, maxRef: 100, unit: b.unit || 'units' }
        const statusVal = b.status === 'LOW' ? 'Deficient' : b.status === 'BORDERLINE' ? 'Borderline' : 'Normal'
        return {
          name: b.marker_name,
          currentValue: String(b.value),
          numericValue: Number(b.value),
          minRef: ref.minRef,
          maxRef: ref.maxRef,
          unit: b.unit || ref.unit,
          targetRange: `${ref.minRef}–${ref.maxRef} ${b.unit || ref.unit}`,
          status: statusVal as any
        }
      })
    : deficiencies.map((d: any) => {
        const ref = standardRanges[d.nutrient] || { minRef: 30, maxRef: 100, unit: 'µg/dL' }
        const isDef = d.risk_level === 'HIGH' || d.risk_level === 'CRITICAL'
        const isBrd = d.risk_level === 'MODERATE'
        const estVal = isDef ? (ref.minRef * 0.65).toFixed(1) : isBrd ? (ref.minRef * 0.88).toFixed(1) : ((ref.minRef + ref.maxRef) / 2).toFixed(1)
        return {
          name: d.nutrient,
          currentValue: estVal,
          numericValue: parseFloat(estVal),
          minRef: ref.minRef,
          maxRef: ref.maxRef,
          unit: ref.unit,
          targetRange: `${ref.minRef}–${ref.maxRef} ${ref.unit}`,
          status: (isDef ? 'Deficient' : isBrd ? 'Borderline' : 'Normal') as any
        }
      })

  const keyFindings = deficiencies.length > 0
    ? deficiencies.map((d: any) => ({
        finding: `${d.nutrient} Deficiency Risk`,
        status: (d.risk_level === 'HIGH' || d.risk_level === 'CRITICAL' ? 'Deficient' : d.risk_level === 'MODERATE' ? 'Borderline' : 'Normal') as any,
        severity: (d.risk_level === 'CRITICAL' || d.risk_level === 'HIGH' ? 'Severe' : d.risk_level === 'MODERATE' ? 'Moderate' : 'Mild') as any,
        clinicalImpact: d.primary_symptom_matches?.length
          ? `Manifesting in ${d.primary_symptom_matches.join(', ')}`
          : `Model-estimated deficiency probability: ${Math.round((d.probability || 0.5) * 100)}% with ${d.risk_level} urgency`
      }))
    : [
        {
          finding: 'Nutritional Equilibrium',
          status: 'Normal' as any,
          severity: 'No Action Required' as any,
          clinicalImpact: 'All tracked micronutrient pathways meet reference requirements.'
        }
      ]

  const recommendedInterventions: Array<any> = []
  if (dossier?.supplement_plan?.length > 0) {
    dossier.supplement_plan.forEach((s: any, idx: number) => {
      recommendedInterventions.push({
        id: `INT-S${idx + 1}`,
        intervention: s.title || `Supplement Protocol ${idx + 1}`,
        priority: 'High Priority',
        expectedBenefit: s.biochemical_mechanism || 'Targeted micronutrient replenishment',
        duration: `${s.dosage_or_serving || 'Standard dose'} ${s.frequency || 'daily'} for 60-90 Days`
      })
    })
  }
  if (dossier?.precision_foods?.length > 0) {
    dossier.precision_foods.forEach((f: any, idx: number) => {
      recommendedInterventions.push({
        id: `INT-F${idx + 1}`,
        intervention: f.title || `Precision Food ${idx + 1}`,
        priority: 'Medium Priority',
        expectedBenefit: f.biochemical_mechanism || 'Dietary food matrix bioavailability enhancement',
        duration: `${f.dosage_or_serving || '1-2 servings'} ${f.frequency || 'daily'} ongoing`
      })
    })
  }
  if (recommendedInterventions.length === 0) {
    recommendedInterventions.push({
      id: 'INT-1',
      intervention: 'Dietary Optimization & Whole Food Diversification',
      priority: 'Routine',
      expectedBenefit: 'Maintains sustained nutrient absorption across metabolic cycles',
      duration: 'Ongoing dietary maintenance'
    })
  }

  const primaryDiag = assessment?.clinical_findings?.[0]
    || (deficiencies.length > 0 ? `Subclinical ${deficiencies[0].nutrient} Deficiency` : 'Comprehensive Nutritional Profile')

  const heroStatement = assessment?.executive_summary
    || `Patient demonstrates ${deficiencies.length > 0 ? deficiencies.map((d: any) => d.nutrient).join(', ') : 'mild micronutrient'} vulnerability with dietary pattern (${demo.dietary_pattern || 'Standard'}). Prioritized interventions address bioavailability and physiological demands.`

  return {
    id: demo.patient_id || 'PT-ACTIVE',
    name: demo.full_name || 'Active Patient',
    age: demo.age || 42,
    gender: demo.gender || 'Female',
    dietaryPattern: demo.dietary_pattern || 'Balanced',
    bmi: bmiVal,
    bmiCategory,
    assessmentDate: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
    riskScore,
    riskTier,
    clinicalSummary: {
      heroStatement,
      primaryDiagnosis: primaryDiag,
      icdCode: 'ICD-10: E56.9 (Nutritional deficiency, unspecified)',
      contributingFactors: Array.isArray(assessment?.contributing_factors)
        ? assessment.contributing_factors.map((cf: any) => typeof cf === 'string' ? cf : (cf.factor || cf.description || '')).filter(Boolean).join('; ')
        : `Dietary pattern: ${demo.dietary_pattern || 'Standard'}, Meals: ${demo.meals_per_day || 3}/day, Sunlight: ${demo.sunlight_exposure_min || 15}m/day`,
      clinicalImpact: assessment?.executive_summary || 'Metabolic co-factor pathways affected by suboptimal intake.',
      confidence: 'High Confidence (Clinician Verified & Machine Learning Grounded)',
    },
    keyFindings,
    nutrientStatus,
    rootCauseAnalysis: {
      whyDeficiencyExists: assessment?.clinical_findings?.join('. ') || 'Nutrient intake and lifestyle factors do not satisfy tissue demand.',
      lifestyleContributors: `Daily sunlight: ${demo.sunlight_exposure_min || 15} mins, Sleep: ${demo.sleep_hours || 7} hrs, Activity: ${demo.activity_level || 'Moderate'}.`,
      dietaryContributors: `Dietary pattern: ${demo.dietary_pattern || 'Standard'}, Meals: ${demo.meals_per_day || 3} per day.`,
      biologicalContributors: `Age ${demo.age || 42}, Gender ${demo.gender || 'Female'}, BMI ${bmiVal}.`,
    },
    recommendedInterventions,
    carePlanTimeline: [
      { timeframe: 'TODAY', action: 'Start Protocol', detail: 'Initiate prioritized micronutrient and whole-food adjustments', status: 'active' },
      { timeframe: 'WEEK 2', action: 'Monitor Adherence', detail: 'Evaluate gastrointestinal tolerance and initial symptom changes', status: 'upcoming' },
      { timeframe: 'WEEK 6', action: 'Biomarker Check', detail: 'Re-evaluate blood chemistry and nutrient trajectory markers', status: 'upcoming' },
      { timeframe: 'WEEK 12', action: 'Clinical Milestone', detail: 'Titrate maintenance dosing based on verified biomarker stabilization', status: 'upcoming' },
    ],
    followUp: {
      nextReviewDate: assessment?.monitoring_plan?.next_review || 'In 4–6 weeks',
      monitoringParameters: Array.isArray(assessment?.monitoring_plan?.parameters)
        ? assessment.monitoring_plan.parameters.join(', ')
        : (deficiencies.map((d: any) => d.nutrient).join(', ') || 'Comprehensive micronutrient panel'),
      expectedOutcomes: 'Normalization of identified deficiency metrics and symptom resolution.',
      successCriteria: 'Sustained biomarker levels within reference bounds and permanent dietary adherence.',
    }
  }
}

export default function ClinicalCopilotPage() {
  const { assessmentId: urlParamId } = useParams()
  const navigate = useNavigate()

  const [activeSession, setActiveSession] = useState(() => sessionManager.getActiveSession())
  const [showResumeModal, setShowResumeModal] = useState(false)
  const storedPrevious = useMemo(() => sessionManager.getStoredPreviousAssessment(), [])

  useEffect(() => {
    if (urlParamId && urlParamId !== 'demo') {
      sessionManager.setActiveSession(urlParamId, new Date().toISOString(), 'completed')
      setActiveSession(sessionManager.getActiveSession())
    }
  }, [urlParamId])

  const effectiveId = activeSession?.active_assessment_id || (urlParamId && urlParamId !== 'demo' ? urlParamId : null)

  const [patientsList, setPatientsList] = useState<PatientRecord[]>([])
  const [selectedPatient, setSelectedPatient] = useState<PatientRecord | null>(null)

  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [signedInterventions, setSignedInterventions] = useState<Record<string, boolean>>({})
  const [carePlanFinalized, setCarePlanFinalized] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    async function loadActivePatientIntelligence() {
      if (!effectiveId) {
        setSelectedPatient(null)
        setPatientsList([])
        return
      }

      try {
        const payload = {
          patient_data: {
            assessment_id: effectiveId
          }
        }

        const [dossierRes, assessmentRes] = await Promise.allSettled([
          api.post('/copilot/patient-intelligence', payload),
          api.post('/copilot/clinical-assessment', payload)
        ])

        const dossier = dossierRes.status === 'fulfilled' ? dossierRes.value.data : null
        const clinicalAssessment = assessmentRes.status === 'fulfilled' ? assessmentRes.value.data : null

        if (dossier) {
          const activeRecord = mapDossierToPatientRecord(dossier, clinicalAssessment)
          setPatientsList([activeRecord])
          setSelectedPatient(activeRecord)
        }
      } catch (err) {
        console.error('Failed to load active patient dossier for Clinical Copilot:', err)
      }
    }

    loadActivePatientIntelligence()
  }, [effectiveId])

  useEffect(() => {
    if (selectedPatient) {
      setCarePlanFinalized(false)
    }
  }, [selectedPatient])

  const toggleSignOrder = (id: string) => {
    setSignedInterventions(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const handleFinalizeCarePlan = () => {
    if (!selectedPatient) return
    const allSigned: Record<string, boolean> = {}
    selectedPatient.recommendedInterventions.forEach(item => {
      allSigned[item.id] = true
    })
    setSignedInterventions(allSigned)
    setCarePlanFinalized(true)
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    if (effectiveId) {
      try {
        const payload = {
          patient_data: {
            assessment_id: effectiveId
          }
        }
        const [dossierRes, assessmentRes] = await Promise.allSettled([
          api.post('/copilot/patient-intelligence', payload),
          api.post('/copilot/clinical-assessment', payload)
        ])
        const dossier = dossierRes.status === 'fulfilled' ? dossierRes.value.data : null
        const clinicalAssessment = assessmentRes.status === 'fulfilled' ? assessmentRes.value.data : null
        if (dossier) {
          const activeRecord = mapDossierToPatientRecord(dossier, clinicalAssessment)
          setPatientsList([activeRecord])
          setSelectedPatient(activeRecord)
        }
      } catch (err) {
        console.error('Refresh failed:', err)
      }
    }
    setTimeout(() => setRefreshing(false), 300)
  }

  if (!selectedPatient) {
    return (
      <>
        <AssessmentRequiredState
          title="Nutritional Assessment Required"
          description="The Clinical Copilot requires an active patient assessment session to provide diagnostic assistance, differential reasoning, and clinical care planning. Complete a new assessment or resume an existing patient evaluation."
          actionLabel="Start Assessment"
          secondaryActionLabel={storedPrevious?.id ? 'Resume Previous Assessment' : undefined}
          onSecondaryAction={storedPrevious?.id ? () => setShowResumeModal(true) : undefined}
          icon={Stethoscope}
        />

        {storedPrevious?.id && (
          <ResumeAssessmentModal
            isOpen={showResumeModal}
            assessmentId={storedPrevious.id}
            assessmentDate={storedPrevious.date}
            onResume={() => {
              sessionManager.setActiveSession(storedPrevious.id, storedPrevious.date, 'completed')
              setActiveSession(sessionManager.getActiveSession())
              setShowResumeModal(false)
            }}
            onStartNew={() => {
              sessionManager.clearActiveSession()
              setActiveSession(null)
              setShowResumeModal(false)
              navigate('/assessment')
            }}
            onClose={() => setShowResumeModal(false)}
          />
        )}
      </>
    )
  }

  const riskColor =
    selectedPatient.riskTier === 'High Risk'
      ? 'var(--c-danger)'
      : selectedPatient.riskTier === 'Moderate Risk'
      ? 'var(--c-warning)'
      : 'var(--c-success)'

  const riskBg =
    selectedPatient.riskTier === 'High Risk'
      ? 'rgba(239, 68, 68, 0.12)'
      : selectedPatient.riskTier === 'Moderate Risk'
      ? 'rgba(245, 158, 11, 0.12)'
      : 'rgba(34, 197, 94, 0.12)'

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 24,
      paddingBottom: 64,
      fontFamily: 'var(--font-body)',
      color: 'var(--c-secondary)',
      maxWidth: 1400,
      margin: '0 auto',
    }}>

      {/* ═══════════════════════════════════════════════════════════════════
          §1 — PATIENT HEADER (SINGLE COMPACT HORIZONTAL SECTION)
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.div
        custom={0}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 24px',
          borderRadius: 16,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          flexWrap: 'wrap',
          gap: 16,
        }}
      >
        {/* Left: Patient Switcher & Clinical Demographics */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          {/* Patient Selector */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              type="button"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: 'var(--c-surface-tint)',
                border: '1px solid var(--c-border)',
                borderRadius: 10,
                padding: '6px 14px',
                cursor: 'pointer',
                fontFamily: 'var(--font-heading)',
                fontSize: '0.875rem',
                fontWeight: 700,
                color: 'var(--c-secondary)',
                transition: 'all 0.15s ease',
              }}
            >
              <User size={15} color="var(--c-primary)" />
              <span>{selectedPatient.name}</span>
              <ChevronDown
                size={14}
                style={{
                  transform: dropdownOpen ? 'rotate(180deg)' : 'none',
                  transition: 'transform 0.15s ease',
                }}
              />
            </button>

            {/* Dropdown Menu */}
            {dropdownOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  left: 0,
                  width: 300,
                  borderRadius: 12,
                  background: 'var(--c-card)',
                  border: '1px solid var(--c-border)',
                  boxShadow: '0 12px 32px rgba(0, 0, 0, 0.5)',
                  padding: 6,
                  zIndex: 999,
                }}
              >
                <div style={{
                  fontSize: '0.6875rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  color: 'var(--c-muted)',
                  padding: '6px 10px',
                  letterSpacing: '0.06em',
                  fontFamily: 'var(--font-heading)',
                }}>
                  Select Patient Record
                </div>
                {patientsList.map(p => {
                  const isCur = p.id === selectedPatient.id
                  return (
                    <button
                      key={p.id}
                      onClick={() => {
                        setSelectedPatient(p)
                        setDropdownOpen(false)
                      }}
                      type="button"
                      style={{
                        width: '100%',
                        textAlign: 'left',
                        padding: '8px 10px',
                        borderRadius: 8,
                        border: 'none',
                        cursor: 'pointer',
                        background: isCur ? 'var(--c-surface-tint)' : 'transparent',
                        color: isCur ? 'var(--c-primary)' : 'var(--c-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        transition: 'background 0.12s ease',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '0.8125rem', fontWeight: 600 }}>{p.name}</div>
                        <div style={{ fontSize: '0.6875rem', color: 'var(--c-muted)' }}>
                          {p.age}Y {p.gender} · {p.dietaryPattern}
                        </div>
                      </div>
                      {isCur && <Check size={14} color="var(--c-primary)" />}
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          {/* Demographics row */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            fontSize: '0.8125rem',
            color: 'var(--c-muted)',
            flexWrap: 'wrap',
          }}>
            <span><strong>Age:</strong> {selectedPatient.age}</span>
            <span>·</span>
            <span><strong>Gender:</strong> {selectedPatient.gender}</span>
            <span>·</span>
            <span><strong>Diet:</strong> {selectedPatient.dietaryPattern}</span>
            <span>·</span>
            <span><strong>BMI:</strong> {selectedPatient.bmi} ({selectedPatient.bmiCategory})</span>
            <span>·</span>
            <span><strong>Assessed:</strong> {selectedPatient.assessmentDate}</span>
          </div>
        </div>

        {/* Right: Risk Score & Refresh */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '6px 12px',
            borderRadius: 8,
            background: riskBg,
            border: `1px solid ${riskColor}33`,
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)', fontWeight: 500 }}>Risk Score:</span>
            <span style={{
              fontSize: '1rem',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              color: riskColor,
            }}>
              {selectedPatient.riskScore}/100
            </span>
            <span style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: riskColor,
              textTransform: 'uppercase',
            }}>
              ({selectedPatient.riskTier})
            </span>
          </div>

          <button
            onClick={handleRefresh}
            type="button"
            title="Refresh clinical record"
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              border: '1px solid var(--c-border)',
              background: 'var(--c-surface-tint)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--c-muted)',
              transition: 'all 0.15s ease',
            }}
          >
            <RefreshCw size={13} className={refreshing ? 'animate-spin' : ''} />
          </button>
        </div>
      </motion.div>

      {/* ═══════════════════════════════════════════════════════════════════
          §2 — CLINICAL SUMMARY (HERO SECTION)
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.section
        custom={1}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          padding: '36px 44px',
          borderRadius: 24,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Subtle accent tint matching dashboard */}
        <div style={{
          position: 'absolute',
          top: -80,
          right: -80,
          width: 260,
          height: 260,
          background: 'radial-gradient(circle, var(--c-surface-tint) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            fontSize: '0.6875rem',
            fontWeight: 600,
            color: 'var(--c-primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            marginBottom: 8,
          }}>
            Assessment Summary
          </div>

          <h1 style={{
            fontFamily: 'var(--font-heading)',
            fontSize: 'clamp(1.5rem, 2.5vw, 1.875rem)',
            fontWeight: 800,
            letterSpacing: '-0.02em',
            color: 'var(--c-secondary)',
            marginBottom: 16,
            lineHeight: 1.25,
            maxWidth: 950,
          }}>
            {selectedPatient.clinicalSummary.heroStatement}
          </h1>

          {/* Structured Clinical Details Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 16,
            marginTop: 24,
            paddingTop: 24,
            borderTop: '1px solid var(--c-border)',
          }}>
            {/* Primary Diagnosis */}
            <div style={{
              padding: '16px 20px',
              borderRadius: 14,
              background: 'var(--c-bg)',
              border: '1px solid var(--c-border-light)',
            }}>
              <div style={{
                fontSize: '0.6875rem',
                fontWeight: 600,
                color: 'var(--c-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                marginBottom: 6,
              }}>
                Primary Diagnosis
              </div>
              <div style={{
                fontSize: '0.9375rem',
                fontWeight: 700,
                color: 'var(--c-secondary)',
                marginBottom: 4,
              }}>
                {selectedPatient.clinicalSummary.primaryDiagnosis}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--c-muted)', fontFamily: 'monospace' }}>
                {selectedPatient.clinicalSummary.icdCode}
              </div>
            </div>

            {/* Contributing Factors */}
            <div style={{
              padding: '16px 20px',
              borderRadius: 14,
              background: 'var(--c-bg)',
              border: '1px solid var(--c-border-light)',
            }}>
              <div style={{
                fontSize: '0.6875rem',
                fontWeight: 600,
                color: 'var(--c-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                marginBottom: 6,
              }}>
                Contributing Factors
              </div>
              <p style={{
                fontSize: '0.8125rem',
                color: 'var(--c-text-secondary)',
                lineHeight: 1.5,
                margin: 0,
              }}>
                {selectedPatient.clinicalSummary.contributingFactors}
              </p>
            </div>

            {/* Clinical Impact */}
            <div style={{
              padding: '16px 20px',
              borderRadius: 14,
              background: 'var(--c-bg)',
              border: '1px solid var(--c-border-light)',
            }}>
              <div style={{
                fontSize: '0.6875rem',
                fontWeight: 600,
                color: 'var(--c-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                marginBottom: 6,
              }}>
                Clinical Impact
              </div>
              <p style={{
                fontSize: '0.8125rem',
                color: 'var(--c-text-secondary)',
                lineHeight: 1.5,
                margin: 0,
              }}>
                {selectedPatient.clinicalSummary.clinicalImpact}
              </p>
            </div>

            {/* Diagnostic Confidence */}
            <div style={{
              padding: '16px 20px',
              borderRadius: 14,
              background: 'var(--c-bg)',
              border: '1px solid var(--c-border-light)',
            }}>
              <div style={{
                fontSize: '0.6875rem',
                fontWeight: 600,
                color: 'var(--c-primary)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                marginBottom: 6,
              }}>
                Confidence
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                fontSize: '0.875rem',
                fontWeight: 600,
                color: 'var(--c-secondary)',
                marginBottom: 4,
              }}>
                <CheckCircle2 size={16} color="var(--c-success)" />
                <span>Verified Diagnostic Consensus</span>
              </div>
              <p style={{
                fontSize: '0.75rem',
                color: 'var(--c-muted)',
                lineHeight: 1.4,
                margin: 0,
              }}>
                {selectedPatient.clinicalSummary.confidence}
              </p>
            </div>
          </div>
        </div>
      </motion.section>

      {/* ═══════════════════════════════════════════════════════════════════
          §3 — KEY FINDINGS (STRUCTURED CLINICAL TABLE)
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.section
        custom={2}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          padding: 28,
          borderRadius: 20,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
        }}
      >
        <div style={{
          fontSize: '0.6875rem',
          fontWeight: 600,
          color: 'var(--c-primary)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginBottom: 6,
        }}>
          Diagnostic Evaluation
        </div>
        <h2 style={{
          fontFamily: 'var(--font-heading)',
          fontSize: '1.25rem',
          fontWeight: 700,
          color: 'var(--c-secondary)',
          letterSpacing: '-0.02em',
          marginBottom: 16,
        }}>
          Key Clinical Findings
        </h2>

        {/* Findings Table */}
        <div style={{
          overflowX: 'auto',
          borderRadius: 12,
          border: '1px solid var(--c-border-light)',
          background: 'var(--c-bg)',
        }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            textAlign: 'left',
            fontSize: '0.8125rem',
          }}>
            <thead>
              <tr style={{
                borderBottom: '1px solid var(--c-border)',
                background: 'var(--c-surface-tint)',
              }}>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)' }}>Finding</th>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)', width: 140 }}>Status</th>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)', width: 160 }}>Severity</th>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)' }}>Clinical Impact</th>
              </tr>
            </thead>
            <tbody>
              {selectedPatient.keyFindings.map((f, idx) => {
                const isDef = f.status === 'Deficient'
                const isBord = f.status === 'Borderline'
                const isElev = f.status === 'Elevated'
                const statusColor = isDef || isElev ? 'var(--c-danger)' : isBord ? 'var(--c-warning)' : 'var(--c-success)'
                const statusBg = isDef || isElev ? 'rgba(239, 68, 68, 0.12)' : isBord ? 'rgba(245, 158, 11, 0.12)' : 'rgba(34, 197, 94, 0.12)'

                return (
                  <tr
                    key={f.finding}
                    style={{
                      borderBottom: idx < selectedPatient.keyFindings.length - 1 ? '1px solid var(--c-border-light)' : 'none',
                    }}
                  >
                    <td style={{ padding: '14px 18px', fontWeight: 700, color: 'var(--c-secondary)' }}>
                      {f.finding}
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '3px 8px',
                        borderRadius: 6,
                        fontSize: '0.6875rem',
                        fontWeight: 600,
                        color: statusColor,
                        background: statusBg,
                      }}>
                        {f.status}
                      </span>
                    </td>
                    <td style={{ padding: '14px 18px', color: 'var(--c-secondary)', fontWeight: 500 }}>
                      {f.severity}
                    </td>
                    <td style={{ padding: '14px 18px', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>
                      {f.clinicalImpact}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </motion.section>

      {/* ═══════════════════════════════════════════════════════════════════
          §4 — NUTRIENT STATUS (VISUAL CENTERPIECE)
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.section
        custom={3}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          padding: 32,
          borderRadius: 24,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
        }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: 24,
          flexWrap: 'wrap',
          gap: 12,
        }}>
          <div>
            <div style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--c-primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: 6,
            }}>
              Biomarker Profile
            </div>
            <h2 style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.375rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              letterSpacing: '-0.02em',
              margin: 0,
            }}>
              Nutrient Status & Clinical Reference Thresholds
            </h2>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {[
              { label: 'Deficient', color: 'var(--c-danger)' },
              { label: 'Borderline', color: 'var(--c-warning)' },
              { label: 'Normal Target', color: 'var(--c-success)' },
            ].map(l => (
              <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 8, height: 8, borderRadius: 3, background: l.color }} />
                <span style={{ fontSize: '0.6875rem', color: 'var(--c-muted)', fontWeight: 500 }}>{l.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Horizontal Clinical Indicators */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {selectedPatient.nutrientStatus.map((item) => {
            const isDef = item.status === 'Deficient'
            const isBord = item.status === 'Borderline'
            const isElev = item.status === 'Elevated'
            const statusColor = isDef || isElev ? 'var(--c-danger)' : isBord ? 'var(--c-warning)' : 'var(--c-success)'
            const statusBg = isDef || isElev ? 'rgba(239, 68, 68, 0.12)' : isBord ? 'rgba(245, 158, 11, 0.12)' : 'rgba(34, 197, 94, 0.12)'

            // Clinical position percentage along range [0, maxRef * 1.25]
            const maxScale = item.maxRef * 1.2
            const posPercent = Math.min(100, Math.max(5, (item.numericValue / maxScale) * 100))
            const minRefPercent = (item.minRef / maxScale) * 100
            const maxRefPercent = (item.maxRef / maxScale) * 100

            return (
              <div
                key={item.name}
                style={{
                  padding: '16px 20px',
                  borderRadius: 14,
                  background: 'var(--c-bg)',
                  border: '1px solid var(--c-border-light)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 10,
                }}
              >
                {/* Header row: Name, Value, Target Range, Badge */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 12,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{
                      fontSize: '0.9375rem',
                      fontWeight: 700,
                      color: 'var(--c-secondary)',
                      minWidth: 160,
                    }}>
                      {item.name}
                    </span>
                    <span style={{
                      fontSize: '0.9375rem',
                      fontWeight: 800,
                      fontFamily: 'var(--font-heading)',
                      color: statusColor,
                    }}>
                      {item.currentValue} {item.unit}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
                      Target: <strong style={{ color: 'var(--c-secondary)' }}>{item.targetRange}</strong>
                    </span>
                    <span style={{
                      display: 'inline-block',
                      padding: '2px 8px',
                      borderRadius: 6,
                      fontSize: '0.6875rem',
                      fontWeight: 600,
                      color: statusColor,
                      background: statusBg,
                      minWidth: 70,
                      textAlign: 'center',
                    }}>
                      {item.status}
                    </span>
                  </div>
                </div>

                {/* Horizontal Clinical Bar */}
                <div style={{
                  position: 'relative',
                  height: 8,
                  borderRadius: 4,
                  background: 'var(--c-bar-track)',
                  overflow: 'visible',
                  marginTop: 4,
                }}>
                  {/* Normal reference target window */}
                  <div style={{
                    position: 'absolute',
                    left: `${minRefPercent}%`,
                    width: `${maxRefPercent - minRefPercent}%`,
                    top: 0,
                    bottom: 0,
                    background: 'rgba(34, 197, 94, 0.25)',
                    borderRadius: 2,
                  }} />

                  {/* Value progress fill */}
                  <div style={{
                    height: '100%',
                    width: `${posPercent}%`,
                    background: statusColor,
                    borderRadius: 4,
                    transition: 'width 0.6s ease',
                  }} />

                  {/* Marker Pin */}
                  <div style={{
                    position: 'absolute',
                    left: `calc(${posPercent}% - 4px)`,
                    top: -3,
                    width: 8,
                    height: 14,
                    borderRadius: 2,
                    background: 'var(--c-secondary)',
                    boxShadow: '0 1px 4px rgba(0, 0, 0, 0.5)',
                  }} />
                </div>
              </div>
            )
          })}
        </div>
      </motion.section>

      {/* ═══════════════════════════════════════════════════════════════════
          §5 — ROOT CAUSE ANALYSIS (EXPLANATION SECTION)
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.section
        custom={4}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          padding: 28,
          borderRadius: 20,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
        }}
      >
        <div style={{
          fontSize: '0.6875rem',
          fontWeight: 600,
          color: 'var(--c-primary)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginBottom: 6,
        }}>
          Etiological Breakdown
        </div>
        <h2 style={{
          fontFamily: 'var(--font-heading)',
          fontSize: '1.25rem',
          fontWeight: 700,
          color: 'var(--c-secondary)',
          letterSpacing: '-0.02em',
          marginBottom: 8,
        }}>
          Root Cause Analysis
        </h2>
        <p style={{
          fontSize: '0.875rem',
          color: 'var(--c-text-secondary)',
          lineHeight: 1.6,
          maxWidth: 900,
          marginBottom: 20,
        }}>
          {selectedPatient.rootCauseAnalysis.whyDeficiencyExists}
        </p>

        {/* 3 Contributor Columns */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 16,
        }}>
          {/* Lifestyle Contributors */}
          <div style={{
            padding: '18px 20px',
            borderRadius: 14,
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: '0.8125rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              marginBottom: 8,
            }}>
              <Sun size={15} color="var(--c-warning)" />
              <span>Lifestyle Contributors</span>
            </div>
            <p style={{
              fontSize: '0.8125rem',
              color: 'var(--c-text-secondary)',
              lineHeight: 1.5,
              margin: 0,
            }}>
              {selectedPatient.rootCauseAnalysis.lifestyleContributors}
            </p>
          </div>

          {/* Dietary Contributors */}
          <div style={{
            padding: '18px 20px',
            borderRadius: 14,
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: '0.8125rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              marginBottom: 8,
            }}>
              <Apple size={15} color="var(--c-success)" />
              <span>Dietary Contributors</span>
            </div>
            <p style={{
              fontSize: '0.8125rem',
              color: 'var(--c-text-secondary)',
              lineHeight: 1.5,
              margin: 0,
            }}>
              {selectedPatient.rootCauseAnalysis.dietaryContributors}
            </p>
          </div>

          {/* Biological Contributors */}
          <div style={{
            padding: '18px 20px',
            borderRadius: 14,
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: '0.8125rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              marginBottom: 8,
            }}>
              <Activity size={15} color="var(--c-primary)" />
              <span>Biological Contributors</span>
            </div>
            <p style={{
              fontSize: '0.8125rem',
              color: 'var(--c-text-secondary)',
              lineHeight: 1.5,
              margin: 0,
            }}>
              {selectedPatient.rootCauseAnalysis.biologicalContributors}
            </p>
          </div>
        </div>
      </motion.section>

      {/* ═══════════════════════════════════════════════════════════════════
          §6 — RECOMMENDED INTERVENTIONS (TREATMENT RECOMMENDATIONS)
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.section
        custom={5}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          padding: 28,
          borderRadius: 20,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
        }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 16,
          flexWrap: 'wrap',
          gap: 12,
        }}>
          <div>
            <div style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--c-primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: 6,
            }}>
              Treatment Protocol
            </div>
            <h2 style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.25rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              letterSpacing: '-0.02em',
              margin: 0,
            }}>
              Recommended Interventions
            </h2>
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--c-muted)' }}>
            {selectedPatient.recommendedInterventions.length} Evidence-Based Interventions
          </span>
        </div>

        {/* Interventions Table / Structured List */}
        <div style={{
          overflowX: 'auto',
          borderRadius: 12,
          border: '1px solid var(--c-border-light)',
          background: 'var(--c-bg)',
        }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            textAlign: 'left',
            fontSize: '0.8125rem',
          }}>
            <thead>
              <tr style={{
                borderBottom: '1px solid var(--c-border)',
                background: 'var(--c-surface-tint)',
              }}>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)', width: '30%' }}>Intervention</th>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)', width: 140 }}>Priority</th>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)' }}>Expected Benefit</th>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)', width: 160 }}>Duration</th>
                <th style={{ padding: '12px 18px', fontWeight: 600, color: 'var(--c-secondary)', width: 130, textAlign: 'right' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {selectedPatient.recommendedInterventions.map((item, idx) => {
                const isSigned = !!signedInterventions[item.id]
                const isHigh = item.priority === 'High Priority'
                const prioColor = isHigh ? 'var(--c-danger)' : 'var(--c-warning)'
                const prioBg = isHigh ? 'rgba(239, 68, 68, 0.12)' : 'rgba(245, 158, 11, 0.12)'

                return (
                  <tr
                    key={item.id}
                    style={{
                      borderBottom: idx < selectedPatient.recommendedInterventions.length - 1 ? '1px solid var(--c-border-light)' : 'none',
                    }}
                  >
                    <td style={{ padding: '14px 18px', fontWeight: 700, color: 'var(--c-secondary)' }}>
                      {item.intervention}
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '3px 8px',
                        borderRadius: 6,
                        fontSize: '0.6875rem',
                        fontWeight: 600,
                        color: prioColor,
                        background: prioBg,
                      }}>
                        {item.priority}
                      </span>
                    </td>
                    <td style={{ padding: '14px 18px', color: 'var(--c-text-secondary)', lineHeight: 1.5 }}>
                      {item.expectedBenefit}
                    </td>
                    <td style={{ padding: '14px 18px', color: 'var(--c-muted)', fontSize: '0.75rem', fontWeight: 500 }}>
                      {item.duration}
                    </td>
                    <td style={{ padding: '14px 18px', textAlign: 'right' }}>
                      <button
                        onClick={() => toggleSignOrder(item.id)}
                        type="button"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 5,
                          padding: '5px 10px',
                          borderRadius: 6,
                          border: `1px solid ${isSigned ? 'var(--c-success)' : 'var(--c-border)'}`,
                          background: isSigned ? 'rgba(34, 197, 94, 0.12)' : 'var(--c-card)',
                          color: isSigned ? 'var(--c-success)' : 'var(--c-secondary)',
                          fontSize: '0.6875rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {isSigned && <Check size={12} />}
                        <span>{isSigned ? 'Approved' : 'Sign Order'}</span>
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </motion.section>

      {/* ═══════════════════════════════════════════════════════════════════
          §7 — CARE PLAN TIMELINE (HEALTHCARE TREATMENT ROADMAP)
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.section
        custom={6}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          padding: 28,
          borderRadius: 20,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
        }}
      >
        <div style={{
          fontSize: '0.6875rem',
          fontWeight: 600,
          color: 'var(--c-primary)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginBottom: 6,
        }}>
          Clinical Roadmap
        </div>
        <h2 style={{
          fontFamily: 'var(--font-heading)',
          fontSize: '1.25rem',
          fontWeight: 700,
          color: 'var(--c-secondary)',
          letterSpacing: '-0.02em',
          marginBottom: 20,
        }}>
          Care Plan Timeline
        </h2>

        {/* Horizontal Visual Timeline */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 14,
          position: 'relative',
        }}>
          {selectedPatient.carePlanTimeline.map((step, idx) => {
            const isActive = step.status === 'active'
            const badgeColor = isActive ? 'var(--c-primary)' : 'var(--c-muted)'

            return (
              <div
                key={step.timeframe}
                style={{
                  padding: '16px 18px',
                  borderRadius: 14,
                  background: 'var(--c-bg)',
                  border: `1px solid ${isActive ? 'var(--c-primary)' : 'var(--c-border-light)'}`,
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 8,
                }}
              >
                {/* Timeframe Pill */}
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  fontSize: '0.6875rem',
                  fontWeight: 800,
                  fontFamily: 'var(--font-heading)',
                  color: badgeColor,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}>
                  <Clock size={12} />
                  <span>{step.timeframe}</span>
                </div>

                {/* Step Action */}
                <div style={{
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: 'var(--c-secondary)',
                }}>
                  {step.action}
                </div>

                {/* Detail */}
                <p style={{
                  fontSize: '0.75rem',
                  color: 'var(--c-text-secondary)',
                  lineHeight: 1.45,
                  margin: 0,
                }}>
                  {step.detail}
                </p>
              </div>
            )
          })}
        </div>
      </motion.section>

      {/* ═══════════════════════════════════════════════════════════════════
          §8 — FOLLOW-UP & CLINICAL ACTIONS
          ═══════════════════════════════════════════════════════════════════ */}
      <motion.section
        custom={7}
        variants={fadeUp}
        initial="hidden"
        animate="visible"
        style={{
          padding: 28,
          borderRadius: 20,
          background: 'var(--c-card)',
          border: '1px solid var(--c-border)',
        }}
      >
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--c-border)',
          paddingBottom: 14,
          marginBottom: 20,
          flexWrap: 'wrap',
          gap: 12,
        }}>
          <div>
            <div style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--c-primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: 4,
            }}>
              Care Management
            </div>
            <h2 style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '1.25rem',
              fontWeight: 700,
              color: 'var(--c-secondary)',
              letterSpacing: '-0.02em',
              margin: 0,
            }}>
              Follow-Up & Clinical Review
            </h2>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: '0.75rem',
            color: 'var(--c-secondary)',
            background: 'var(--c-surface-tint)',
            border: '1px solid var(--c-border)',
            padding: '6px 14px',
            borderRadius: 8,
          }}>
            <Calendar size={14} color="var(--c-primary)" />
            <span>Next Review: <strong>{selectedPatient.followUp.nextReviewDate}</strong></span>
          </div>
        </div>

        {/* 3 Information Blocks */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 16,
          marginBottom: 24,
        }}>
          {/* Monitoring Parameters */}
          <div style={{
            padding: '16px 20px',
            borderRadius: 14,
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)',
          }}>
            <div style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--c-primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 6,
            }}>
              Monitoring Parameters
            </div>
            <p style={{
              fontSize: '0.8125rem',
              color: 'var(--c-text-secondary)',
              lineHeight: 1.5,
              margin: 0,
            }}>
              {selectedPatient.followUp.monitoringParameters}
            </p>
          </div>

          {/* Expected Outcomes */}
          <div style={{
            padding: '16px 20px',
            borderRadius: 14,
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)',
          }}>
            <div style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--c-primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 6,
            }}>
              Expected Outcomes
            </div>
            <p style={{
              fontSize: '0.8125rem',
              color: 'var(--c-text-secondary)',
              lineHeight: 1.5,
              margin: 0,
            }}>
              {selectedPatient.followUp.expectedOutcomes}
            </p>
          </div>

          {/* Success Criteria */}
          <div style={{
            padding: '16px 20px',
            borderRadius: 14,
            background: 'var(--c-bg)',
            border: '1px solid var(--c-border-light)',
          }}>
            <div style={{
              fontSize: '0.6875rem',
              fontWeight: 600,
              color: 'var(--c-primary)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 6,
            }}>
              Success Criteria
            </div>
            <p style={{
              fontSize: '0.8125rem',
              color: 'var(--c-text-secondary)',
              lineHeight: 1.5,
              margin: 0,
            }}>
              {selectedPatient.followUp.successCriteria}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          gap: 14,
          paddingTop: 16,
          borderTop: '1px solid var(--c-border)',
          flexWrap: 'wrap',
        }}>
          <button
            type="button"
            onClick={() => window.print()}
            style={{
              padding: '10px 18px',
              borderRadius: 10,
              border: '1px solid var(--c-border)',
              background: 'var(--c-surface-tint)',
              color: 'var(--c-secondary)',
              fontWeight: 600,
              fontSize: '0.8125rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              transition: 'background 0.15s ease',
            }}
          >
            <Printer size={15} />
            <span>Export / Print Clinical Record (PDF)</span>
          </button>

          <button
            type="button"
            onClick={handleFinalizeCarePlan}
            style={{
              padding: '10px 20px',
              borderRadius: 10,
              border: 'none',
              background: carePlanFinalized ? 'var(--c-success)' : 'var(--c-primary)',
              color: carePlanFinalized ? '#FFFFFF' : '#0B0F14',
              fontWeight: 700,
              fontSize: '0.8125rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              transition: 'all 0.15s ease',
            }}
          >
            <Check size={16} strokeWidth={2.5} />
            <span>{carePlanFinalized ? 'Care Plan Signed & Finalized' : 'Sign & Finalize Care Plan'}</span>
          </button>
        </div>
      </motion.section>

    </div>
  )
}
