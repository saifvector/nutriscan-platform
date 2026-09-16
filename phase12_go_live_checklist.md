# PHASE 12 TO PHASE 13 GO-LIVE & DEPLOYMENT CHECKLIST
**NutriScan AI — Stage-Gated Production Verification Protocol**
**Date:** September 14, 2026  
**Auditor Roles:** Principal Release Engineer & Clinical Governance Board  
**Status:** AUDITED PROTOCOL  

---

## 1. STAGE-GATED VERIFICATION GATES

### STAGE 1: MACHINE LEARNING & CLINICAL VALIDATION
- [x] **Gate 1.1:** 9 champion models trained, calibrated, and serializable in `models/` directory.
- [x] **Gate 1.2:** Platt probability calibrators loaded and operational for all targets.
- [x] **Gate 1.3:** Demographic holdout validation stratified across Age, Sex, Race, and Income PIR.
- [ ] **Gate 1.4:** Re-optimize Calcium decision threshold to achieve Recall $\ge 0.60$ on minority class. *(Phase 13 Prerequisite)*
- [ ] **Gate 1.5:** Re-tune Potassium decision threshold to bring Precision $\ge 0.20$. *(Phase 13 Prerequisite)*
- [x] **Gate 1.6:** Scikit-learn feature name mismatch warnings eliminated during inference.

---

### STAGE 2: CLINICAL SAFETY & GUARDRAILS
- [x] **Gate 2.1:** NIH Tolerable Upper Limit (UL) guardrails enforced across 10 core micronutrients.
- [x] **Gate 2.2:** Critical pathological contraindications (Hemochromatosis, CKD, Wilson's, Pregnancy) enforced with fail-closed blocking.
- [x] **Gate 2.3:** Pharmacological checks for Warfarin + Vitamin K and Folate + B12 masking active.
- [ ] **Gate 2.4:** Implement age-banded Upper Limits for pediatric patients (ages 1–3, 4–8, 9–13, 14–18). *(Phase 13 Prerequisite)*
- [ ] **Gate 2.5:** Add ACE inhibitor / ARB + Potassium conflict check. *(Phase 13 Prerequisite)*
- [ ] **Gate 2.6:** Add Levothyroxine (Synthroid) + Iron/Calcium chelation spacing rule. *(Phase 13 Prerequisite)*

---

### STAGE 3: PERSISTENCE & DATABASE INTEGRATION
- [x] **Gate 3.1:** PostgreSQL DDL migration scripts (`database/migrations/`) fully articulated.
- [x] **Gate 3.2:** SQLAlchemy ORM models (`backend/app/models/`) defined with foreign keys and indexes.
- [ ] **Gate 3.3:** Instantiate asynchronous database engine (`create_async_engine`) in `backend/app/core/database.py`. *(Phase 13 Prerequisite)*
- [ ] **Gate 3.4:** Inject `db: AsyncSession` dependency into all API routers. *(Phase 13 Prerequisite)*
- [ ] **Gate 3.5:** Migrate in-memory state in `ClinicalAuditService` and `ModelDriftEngine` to PostgreSQL tables. *(Phase 13 Prerequisite)*
- [ ] **Gate 3.6:** Implement live DB lookup for `GET /api/v1/predictions/{prediction_id}`. *(Phase 13 Prerequisite)*

---

### STAGE 4: AUTHENTICATION, AUTHORIZATION & SECURITY
- [ ] **Gate 4.1:** Implement JWT authentication middleware and token validation. *(Phase 13 Prerequisite)*
- [ ] **Gate 4.2:** Implement Role-Based Access Control (RBAC): `PATIENT`, `CLINICIAN`, `CLINICAL_AUDITOR`. *(Phase 13 Prerequisite)*
- [ ] **Gate 4.3:** Restrict CORS origins to whitelisted domains; eliminate wildcard with credentials. *(Phase 13 Prerequisite)*
- [ ] **Gate 4.4:** Move JWT secrets and DB credentials to environment variables with mandatory startup validation. *(Phase 13 Prerequisite)*
- [ ] **Gate 4.5:** Implement PHI redaction filter in application logging formatter. *(Phase 13 Prerequisite)*
- [ ] **Gate 4.6:** Configure API rate-limiting middleware (`slowapi` or Redis-backed bucket). *(Phase 13 Prerequisite)*

---

### STAGE 5: EXPLAINABILITY & AUDIT INTEGRITY
- [x] **Gate 5.1:** Pre-warmed TreeExplainer SHAP attribution latency verified $< 50\text{ ms}$.
- [x] **Gate 5.2:** Evidence engine linking recommendations to NIH ODS and USDA citations with evidence grades.
- [ ] **Gate 5.3:** Remove synthetic vegan fallback profile on cache miss; return HTTP 404. *(Phase 13 Prerequisite)*
- [x] **Gate 5.4:** Cryptographic SHA-256 hash generation for every clinical decision record.
- [x] **Gate 5.5:** ReportLab PDF clinical decision certificate generation operational.
- [x] **Gate 5.6:** CSV audit log streaming verified.

---

### STAGE 6: MLOPS, DRIFT & PRODUCTION TELEMETRY
- [x] **Gate 6.1:** 10-bin Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) drift calculation active.
- [x] **Gate 6.2:** Baseline NHANES probability distributions initialized during startup lifespan.
- [x] **Gate 6.3:** Real-time throughput (req/min) and $p_{50}, p_{95}, p_{99}$ latency metrics aggregated.
- [x] **Gate 6.4:** Automated governance alert lifecycle (`ACTIVE` $\rightarrow$ `ACKNOWLEDGED` $\rightarrow$ `RESOLVED`).
- [x] **Gate 6.5:** Algorithmic fairness monitoring auditing EEOC 80% Four-Fifths rule and parity ratios.

---

### STAGE 7: FRONTEND & USER EXPERIENCE
- [x] **Gate 7.1:** Production build verification: `npm run build` succeeds in $< 2\text{ seconds}$ with zero errors.
- [x] **Gate 7.2:** Governance & Monitoring console (`/monitoring`, `/governance`) fully accessible via navigation.
- [x] **Gate 7.3:** Interactive Population Drift Shift Simulator (+15%, +35%) operational.
- [x] **Gate 7.4:** Interactive Clinical Safety Sandbox operational.
- [ ] **Gate 7.5:** Implement `React.lazy()` dynamic code splitting to optimize 1.45 MB bundle. *(Phase 13 Prerequisite)*

---

### STAGE 8: REGULATORY, HIPAA & LEGAL SIGN-OFF
- [x] **Gate 8.1:** Full regression suite passing: 175 / 175 tests green (100% pass rate).
- [ ] **Gate 8.2:** HIPAA §164.312(a)(1) Access Control sign-off upon completion of Auth module. *(Phase 13 Prerequisite)*
- [ ] **Gate 8.3:** HIPAA §164.312(b) Immutable Audit Logging sign-off upon DB table persistence. *(Phase 13 Prerequisite)*
- [x] **Gate 8.4:** FDA Clinical Decision Support (CDS) statutory disclaimers embedded in reports and UI.

---

## 2. PHASE TRANSITION PROTOCOL

```
                                  PHASE 12
                   [ Clinical Governance & Validation ]
                                     │
                        (Verified 175/175 Tests)
                                     ▼
                      [ PHASE 12 CERTIFICATION GATE ]
                                     │
                                 (APPROVED)
                                     ▼
                                  PHASE 13
            [ Enterprise Hardening, DB Integration & Deployment ]
```

### Sign-Off
- **Phase 12 Completion Status:** **100% VERIFIED**
- **Transition Authorization:** **APPROVED TO PROCEED TO PHASE 13**
