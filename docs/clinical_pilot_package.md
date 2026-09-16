# NutriScan AI — Clinical Pilot Package (IRB-Ready)

**Protocol Number:** NUTRI-AI-2026-01  
**Version:** 1.0 (Final)  
**Date:** September 14, 2026  
**Study Title:** Prospective Clinical Evaluation of NutriScan AI Clinical Copilot for Nutrient Deficiency Screening and Precision Nutrition in Outpatient Healthcare  
**Investigational Product:** NutriScan AI Clinical Decision Support System (v1.0)  
**Sponsor:** NutriScan Health Technologies, Inc.  
**Principal Investigator:** Chief Medical Information Officer (CMIO), MD, FACP  

---

## 1. Executive Summary & Study Protocol

### 1.1 Clinical Background & Rationale
Micronutrient deficiencies (notably Iron, Vitamin D, Vitamin B12, Folate, and Magnesium) affect over 2 billion individuals globally and contribute to chronic fatigue, metabolic dysfunction, impaired immunity, and hematological abnormalities. In traditional outpatient medicine, dietary recalls are time-consuming (averaging 15–20 minutes), clinical signs are non-specific, and empirical supplement prescriptions frequently fail to account for drug-nutrient antagonisms, absorption kinetics, or NIH Tolerable Upper Intake Levels (UL).

NutriScan AI is an algorithmic Clinical Decision Support System (CDSS) built upon 45 calibrated machine learning models trained on 82 CDC NHANES multi-cycle laboratory tables, USDA Foundation Foods, and NIH Dietary Supplement Ingredient Databases. Under Section 520(o)(1)(E) of the 21st Century Cures Act, NutriScan AI assists licensed clinicians by providing 10-stream clinical dossiers, differential diagnostic reasoning with 95% Wilson confidence intervals, and 1-click EMR SOAP notes, maintaining the clinician as the ultimate decision-maker.

### 1.2 Study Objectives
- **Primary Objective:** To evaluate the diagnostic concordance between NutriScan AI Copilot differential etiology rankings and board-certified attending clinician final diagnoses.
- **Secondary Objectives:**
  1. Measure reduction in clinician documentation and assessment time per encounter.
  2. Quantify 30-day patient adherence to precision nutrition interventions.
  3. Verify zero unintercepted clinical safety contraindications or NIH Upper Limit violations.
  4. Assess clinician usability using the System Usability Scale (SUS).

### 1.3 Study Design
A prospective, multi-center, observational and guided-intervention cohort study ($N = 300$) conducted across three outpatient clinics:
1. Academic Medical Center Outpatient Internal Medicine Clinic ($N = 120$)
2. Community Primary Care & Family Medicine Center ($N = 100$)
3. Specialized Clinical Nutrition & Bariatric Recovery Clinic ($N = 80$)

---

## 2. Patient Eligibility Criteria

### 2.1 Inclusion Criteria
To be eligible for enrollment, participants must meet all of the following criteria:
1. Male or female aged $\ge 18$ years and $\le 75$ years at the time of intake.
2. Presenting with one or more of the following clinical indicators:
   - Unexplained chronic fatigue, weakness, or lethargy ($> 4$ weeks).
   - Documented or suspected restrictive diet (e.g., strict vegan, restrictive vegetarian, ketogenic, or high-ultra-processed food diet).
   - Clinical signs compatible with micronutrient deficit (e.g., brittle nails, hair thinning, restless legs, macrocytosis, microcytosis, muscle cramping, paresthesias).
   - History of gastrointestinal malabsorption (e.g., status post bariatric surgery $> 6$ months, celiac disease, inflammatory bowel disease in remission).
3. Access to an internet-connected smartphone, tablet, or personal computer to access dietary log and consent forms.
4. Ability to provide written informed consent in English or Spanish.

### 2.2 Exclusion Criteria
Participants presenting with any of the following conditions will be excluded:
1. Age $< 18$ years (pediatric patients are excluded from automated dosing).
2. End-Stage Renal Disease (ESRD) requiring active hemodialysis or peritoneal dialysis (GFR $< 15\text{ mL/min/1.73m}^2$).
3. Active acute hematological malignancy or ongoing chemotherapy/radiation therapy.
4. Acute critical illness requiring immediate hospital admission or ICU transfer.
5. Inability or refusal to sign the Institutional Review Board (IRB) Informed Consent document.

---

## 3. Clinical Study Workflow

```
[ Patient Intake ]
       │ (Symptom Survey, 24h Dietary Recall, Medication/Allergy List)
       ▼
[ NutriScan AI Engine ]
       │ - Ingests 10 clinical data streams into master dossier
       │ - Computes posterior probabilities across 9 deficiency targets
       │ - Evaluates TreeSHAP feature attributions
       │ - Formulates competing differential diagnoses with 95% Wilson CIs
       │ - Enforces NIH UL caps & contraindication checks (Fail-Closed)
       ▼
[ Clinician Copilot Workstation ]
       │ (Attending Clinician Reviews Findings)
       ├─► Action: APPROVE (Adopts proposed SOAP note & plan)
       ├─► Action: MODIFY  (Adjusts dosage, diet, or confirmatory tests)
       ├─► Action: REJECT  (Dismisses finding with clinical justification)
       └─► Action: ESCALATE(Refers to Hematology / Gastroenterology)
       │
       ▼
[ Immutable SHA-256 Audit Record ] ──► [ 1-Click EMR SOAP Note Export (Epic/Cerner) ]
       │
       ▼
[ Diagnostic Blood Draw ] (Baseline: Serum Ferritin, 25-OH-D, RBC Folate, Chem-14)
       │
       ▼
[ 30-Day Follow-Up Encounter ]
       │ - Re-assessment of symptom resolution (VAS scale)
       │ - Adherence tracking to precision nutrition plan
       │ - Confirmatory follow-up lab re-testing
```

---

## 4. Primary Endpoints, Success Metrics & Stopping Rules

### 4.1 Primary Endpoint
- **Diagnostic Concordance Rate:** Percentage of encounters where the primary or secondary clinical deficiency identified by the attending physician matches the top-2 ranked differential etiologies generated by NutriScan AI.
  - **Success Target:** $\ge 90.0\%$ overall concordance across the 300-patient cohort.

### 4.2 Secondary Endpoints
1. **Clinical Efficiency:** Average time spent by clinicians synthesizing nutritional recommendations and completing documentation.
   - **Baseline:** 14.5 minutes.
   - **Success Target:** $\le 6.0$ minutes ($\ge 58.6\%$ time savings).
2. **Safety Integrity:** Number of adverse events attributable to unintercepted toxic nutrient overdoses or drug-nutrient contraindications.
   - **Success Target:** Exactly 0 events.
3. **Patient Adherence:** Proportion of participants reporting $\ge 80\%$ compliance with recommended dietary/supplement adjustments at 30 days.
   - **Success Target:** $\ge 75.0\%$ of active cohort.
4. **Clinician System Usability:** Usability score evaluated via standard 10-item System Usability Scale (SUS).
   - **Success Target:** Mean SUS score $\ge 80 / 100$ ("Excellent").

### 4.3 Study Stopping & Failure Criteria
The pilot study will be paused or terminated immediately if any of the following occur:
1. **Critical Safety Breach:** A single occurrence of an adverse event resulting from an unintercepted NIH UL exceedance or contraindication bypass.
2. **Excessive Clinical Divergence:** Clinician disagreement rate exceeding $25.0\%$ across any single target category over 30 consecutive patients.
3. **Severe Platform Unavailability:** System availability dropping below $99.0\%$ or p95 API latency exceeding $500\text{ ms}$ for more than 48 continuous hours.
4. **Participant Attrition:** Unexplained participant withdrawal rate $> 20.0\%$ prior to the 30-day follow-up.

---

## 5. Participant Informed Consent Template

```text
INSTITUTIONAL REVIEW BOARD (IRB) INFORMED CONSENT FORM
Title of Study: Clinical Evaluation of NutriScan AI for Nutrient Deficiency Screening
Principal Investigator: [Physician Name, MD], Department of Medicine
Participant ID: PT-2026-______     Date of Birth: ____/____/________

1. PURPOSE OF THIS RESEARCH STUDY
You are invited to participate in a clinical research study evaluating NutriScan AI, an intelligent clinical software application designed to help doctors and registered dietitians identify potential dietary vitamin and mineral deficiencies and formulate personalized nutrition guidance.

2. WHAT WILL HAPPEN IN THIS STUDY?
If you agree to participate:
- You will complete a 10-minute digital health intake covering your current symptoms, daily food intake, and medications.
- NutriScan AI will analyze your information and provide automated suggestions to your doctor.
- YOUR DOCTOR WILL INDEPENDENTLY REVIEW AND APPROVE ALL RECOMMENDATIONS. The AI will never make changes to your medical care without your doctor's direct sign-off.
- You will receive personalized meal and supplement advice approved by your doctor.
- You will return in 30 days for a brief follow-up visit and routine blood test.

3. RISKS AND DISCOMFORTS
There are no physical risks associated with using the software. Routine blood draws may cause brief discomfort, slight bruising, or rare dizziness. All personal health data is protected under strict HIPAA encryption standards.

4. VOLUNTARY PARTICIPATION & WITHDRAWAL
Participation is completely voluntary. You may withdraw at any time without penalty or loss of benefits to which you are otherwise entitled. Your standard medical care will not be affected.

5. CONFIDENTIALITY
Your information will be assigned a unique cryptographic code (Participant ID). Personal identifiers (name, address, Social Security number) will be securely separated. All computerized records are encrypted with AES-256 and stored on secure, HIPAA-compliant servers.

PARTICIPANT SIGNATURE & CONSENT:
I have read this form, had my questions answered, and voluntarily agree to participate.

________________________________________         ____/____/________
Participant Printed Name                         Date

________________________________________         ____/____/________
Participant Signature                            Time

INVESTIGATOR SIGNATURE:
________________________________________         ____/____/________
Investigator / Designee Signature                Date
```

---

## 6. Clinician Onboarding & Training Checklist

```
+====================================================================================================+
|                          CLINICIAN ONBOARDING & PILOT TRAINING CHECKLIST                           |
+====================================================================================================+
| Module                 | Topic / Task                                             | Completed (Y/N)|
+------------------------+----------------------------------------------------------+----------------+
| 1. Regulatory Context  | Overview of FDA Non-Device CDS Section 520(o)(1)(E)      | [ ]            |
| 1. Regulatory Context  | Clinician-in-the-loop legal responsibility & role        | [ ]            |
| 2. Copilot Workstation | Accessing `/copilot` via hospital SSO / JWT login        | [ ]            |
| 2. Copilot Workstation | Navigating the 10-Stream Patient Intelligence Dossier    | [ ]            |
| 2. Copilot Workstation | Interpreting 9-Target Posterior Probabilities & 95% CIs  | [ ]            |
| 3. Explainability      | Reading TreeSHAP feature waterfall contributions         | [ ]            |
| 3. Explainability      | Evaluating evidence grades & PubMed/ODS literature links | [ ]            |
| 4. Differential Engine | Reviewing competing etiologies and distinguishing features| [ ]            |
| 4. Differential Engine | Ordering recommended confirmatory diagnostic blood panels| [ ]            |
| 5. Review & Sign-Off   | Performing APPROVE, MODIFY, REJECT, and ESCALATE actions | [ ]            |
| 5. Review & Sign-Off   | Entering mandatory clinical justification for overrides  | [ ]            |
| 5. Review & Sign-Off   | Verifying SHA-256 cryptographic audit receipt            | [ ]            |
| 6. EMR Integration     | 1-Click Clipboard copy of SOAP notes into Epic / Cerner  | [ ]            |
| 6. EMR Integration     | Using dot-phrase / smart-phrase text macros              | [ ]            |
| 7. Safety & Incident   | Identifying fail-closed NIH UL warnings and drug blocks  | [ ]            |
| 7. Safety & Incident   | Adverse event reporting procedure to Study Coordinator   | [ ]            |
+====================================================================================================+
Clinician Name: __________________________ License #: ________________ NPI: ________________
Trainer Signature: _______________________ Date: ____/____/________
```
