# PHASE 12 CLINICAL & OPERATIONAL RISK REGISTER
**NutriScan AI — Risk Governance & Mitigation Strategy**
**Date:** September 14, 2026  
**Auditor Roles:** Healthcare Safety Auditor & Chief Risk Officer  
**Status:** ACTIVE REGISTER  

---

## 1. RISK ASSESSMENT METHODOLOGY

Risks are quantified using standard clinical and enterprise scoring:
$$\text{Risk Score} = \text{Likelihood (1–5)} \times \text{Impact (1–5)}$$

| Score Range | Priority Tier | Action Required |
| :--- | :--- | :--- |
| **16 – 25** | **CRITICAL** | Production blocker; mandatory resolution before general availability |
| **10 – 15** | **HIGH** | Remediation required in current or next immediate phase (Phase 13) |
| **5 – 9** | **MEDIUM** | Monitored; scheduled for mitigation during stabilization sprint |
| **1 – 4** | **LOW** | Accepted operational risk; documented and observed |

---

## 2. GRANULAR RISK REGISTRY

| Risk ID | Category | Description | Likelihood | Impact | Score | Current Mitigation | Planned Phase 13 Resolution | Owner |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | **Clinical ML** | **Calcium 0.0% Recall:** Model failed to detect all 7 true positive cases in test split (`TP: 0, FN: 7`). | 4 | 5 | **20 (Critical)** | Documented in Model Card and model evaluation report. | Re-optimize decision threshold using $F_2$ utility curve prioritizing recall; train SMOTE rebalanced model. | Lead Data Scientist |
| **RSK-02** | **Security** | **Unauthenticated Endpoints:** All `/api/v1/*` routes lack token or session verification. | 5 | 4 | **20 (Critical)** | Local development environment assumption. | Implement JWT Bearer middleware and `@require_role` RBAC decorators across all routers. | Security Lead |
| **RSK-03** | **Architecture** | **Persistence Disconnect:** In-memory caches clear upon server restart; data is lost. | 5 | 4 | **20 (Critical)** | State retained during active process lifetime for tests. | Instantiate SQLAlchemy async connection pool and migrate services to PostgreSQL. | Backend Lead |
| **RSK-04** | **Clinical Safety**| **Static Pediatric UL:** Adult Upper Limits applied to young children (e.g. Iron 45mg/day). | 3 | 5 | **15 (High)** | Disclaimer that system is calibrated for adults. | Add age-stratified reference table (NIH ODS bands: 1–3y, 4–8y, 9–13y, 14–18y, 19+y). | Clinical Auditor |
| **RSK-05** | **Clinical Safety**| **Synthetic Explainability Profile:** Cache miss triggers fake 34-year-old vegan rationale. | 3 | 5 | **15 (High)** | Warning logged to console. | Remove fallback; query database or return explicit HTTP 404 Not Found error. | ML Engineer |
| **RSK-06** | **Security** | **Wildcard CORS with Credentials:** `allow_origins=["*"]` + `allow_credentials=True`. | 4 | 3 | **12 (High)** | Local CORS testing config. | Remove wildcard; whitelist origin domains from environment configuration. | Security Lead |
| **RSK-07** | **Clinical ML** | **Potassium High False Positive Rate:** Precision is only 3.2% (390 FP vs 13 TP). | 4 | 3 | **12 (High)** | Model indicates moderate confidence score. | Adjust decision threshold from 0.274 to high-specificity operating point (>0.55). | Lead Data Scientist |
| **RSK-08** | **Clinical Safety**| **Missing ACEI/ARB Interaction:** No check for potassium-sparing antihypertensives. | 2 | 5 | **10 (High)** | General chronic disease contraindication warning. | Add pharmacological rule for ACE inhibitors and ARBs to trigger `SafetySeverity.CRITICAL`. | Clinical Pharmacist |
| **RSK-09** | **Operations** | **Unbounded In-Memory Accumulation:** `_history_cache` and `_audit_store` lack TTL limits. | 4 | 2 | **8 (Medium)** | Deque maxlen limits in audit service (`_max_buffer_size = 500`). | Back queues with Redis capped lists and PostgreSQL persistent storage. | Backend Lead |
| **RSK-10** | **Performance** | **Sequential Model Execution:** Single-threaded loop evaluates 9 models sequentially (~165 ms). | 3 | 2 | **6 (Medium)** | Caching pre-warmed models in lifespan. | Parallelize inference using `ThreadPoolExecutor` or vectorized numpy evaluation (<35 ms). | Backend Lead |

---

## 3. RESIDUAL RISK ACCEPTANCE & GATING CRITERIA

### Mandatory Phase 13 Entry Gate
The following critical risks must be addressed during Phase 13 sprint execution before platform launch:
1. **RSK-02 & RSK-06 (Security):** Complete implementation of JWT authentication, role-based authorization, and CORS whitelisting.
2. **RSK-03 (Persistence):** Full migration of audit trails, adherence history, and model drift snapshots into PostgreSQL.
3. **RSK-01 (Clinical ML):** Decision threshold re-tuning for Calcium and Potassium.
4. **RSK-04 & RSK-05 (Clinical Safety):** Pediatric UL stratification and removal of synthetic explainability fallback.
