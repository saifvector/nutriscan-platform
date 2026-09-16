# NutriScan AI — Phase 11 Clinical Safety & Regulatory Audit
**Audit Protocol:** Software as a Medical Device (SaMD) / Clinical Decision Support (CDS) Boundaries  
**Date:** September 13, 2026  
**Auditor:** Clinical AI Auditor & Healthcare Compliance Lead  
**Compliance Status:** **100% REGULATORY BOUNDARIES MAINTAINED**

---

## 1. Statutory Boundaries & Non-Diagnostic Affirmation

NutriScan AI is engineered strictly as an **educational and preliminary clinical nutritional risk screening tool**. It does NOT operate as a primary diagnostic device or physician replacement.

### Prohibited Claims Audit across Codebase & Reports:
- **Diagnostic Claims:** **0**. No endpoints return "Diagnosis", "Diagnostic Certainty", or clinical pathology confirmations. All outputs are framed as "Risk Tier" (`HIGH`, `MODERATE`, `LOW`) and "Nutritional Deficiency Probability".
- **Therapeutic Treatment Claims:** **0**. Recommendations focus strictly on dietary whole foods, culinary preparation tips, and standard dietary supplement safety ranges.
- **Physician Replacement Claims:** **0**. All user-facing documents and reports mandate confirmatory laboratory testing and physician consultation.

---

## 2. Disclaimers & Warning Notices Verification

The following standardized disclaimer was verified present across the clinical PDF reporting module (`pdf_generator.py`), UI preview modals (`PDFPreviewModal.tsx`), and supplement guidance centers (`SupplementGuidanceCenter.tsx`):

> **Clinical Notice & Regulatory Disclaimer:**  
> *"This AI-generated screening report provides nutritional risk assessment based on demographic, dietary, symptom, and lifestyle factors. It is not a standalone diagnostic evaluation. Confirmatory venous serum laboratory testing (e.g., 25-OH Vitamin D, Ferritin, Serum B12, RBC Folate) and consultation with a qualified medical professional or registered dietitian is recommended before initiating high-dose therapeutic supplementation."*

---

## 3. Supplement Safety Boundaries & Toxicity Safeguards

- **Tolerable Upper Intake Levels (UL):** Integrated into the recommendation engine to prevent excessive micronutrient exposure:
  - Vitamin D: Safe upper limit capped at 4,000 IU/day.
  - Iron: Supplemental guidance cautions against non-anemic iron loading to prevent hemochromatosis risk.
  - Selenium: Strict 1–2 Brazil nut daily limit warnings enforced to prevent selenosis (UL: 400 mcg/day).
- **Synergy & Antagonism Guidance:** Engine explicitly advises on inhibitory interactions (e.g., Calcium inhibiting non-heme Iron absorption; phytates in unsoaked legumes).

---

## 4. Uncertainty & Confidence Communication

- Every target prediction returns both an empirical probability and a transparent **Confidence Score** $[0.50, 0.99]$.
- When input questionnaires are sparse (e.g., $< 25\%$ complete), the confidence tier automatically downgrades to `LOW_CONFIDENCE`, and the user is alerted to provide additional clinical inputs for optimal certainty.

**Clinical Safety Gate: PASS**
