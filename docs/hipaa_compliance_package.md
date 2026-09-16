# NutriScan AI — HIPAA & Regulatory Compliance Package

**Document Version:** 1.0 (Production Master)  
**Effective Date:** September 14, 2026  
**Applicable Regulations:** Health Insurance Portability and Accountability Act (HIPAA) of 1996 (45 CFR Parts 160 and 164), Health Information Technology for Economic and Clinical Health (HITECH) Act, FDA 21st Century Cures Act Section 520(o)(1)(E).

---

## 1. HIPAA Readiness Checklist (Security Rule 45 CFR Part 164)

```
+====================================================================================================+
|                              HIPAA SECURITY RULE COMPLIANCE AUDIT                                  |
+====================================================================================================+
| Regulation Citation     | Specification Description                             | Status  | Evidence Location        |
+-------------------------+-------------------------------------------------------+---------+--------------------------+
| 164.308(a)(1)(ii)(A)    | Risk Analysis & Management Protocol                   | PASSED  | docs/risk_register.md    |
| 164.308(a)(1)(ii)(B)    | Sanction Policy for Workforce Non-Compliance          | PASSED  | Section 6.3 of this Doc  |
| 164.308(a)(1)(ii)(D)    | Information System Activity Review (Audit Log Review) | PASSED  | `audit_service.py`       |
| 164.308(a)(3)(i)        | Workforce Security (Role-Based Access Clearance)      | PASSED  | `auth.py`, RBAC Schemas  |
| 164.308(a)(4)(i)        | Information Access Management (Least Privilege)       | PASSED  | Database user permissions|
| 164.308(a)(5)(ii)(C)    | Log-in Monitoring & Brute Force Lockout               | PASSED  | Rate-limiter middleware  |
| 164.308(a)(7)(ii)(A)    | Data Backup Plan (Daily Automated Snapshots)          | PASSED  | `deploy/backup_plan.md`  |
| 164.308(a)(7)(ii)(B)    | Disaster Recovery Plan (Multi-AZ Failover)            | PASSED  | Section 3 of Deploy Pkg  |
| 164.310(a)(1)           | Physical Facility Access Controls (Cloud Provider BAA)| PASSED  | AWS/GCP SOC 2 Type II    |
| 164.310(d)(1)           | Device & Media Controls (Cryptographic Erasure)       | PASSED  | KMS Key Revocation       |
| 164.312(a)(1)           | Unique User Identification (UUID Participant Tracking)| PASSED  | `database/schema.sql`    |
| 164.312(a)(2)(i)        | Emergency Access Procedure ("Break-Glass" Protocol)   | PASSED  | Section 4 of this Doc    |
| 164.312(a)(2)(iii)      | Automatic Logoff (15-Minute Token Inactivity Timeout)  | PASSED  | Frontend Session Hook    |
| 164.312(a)(2)(iv)       | Encryption at Rest (FIPS 140-2 Validated AES-256)     | PASSED  | PostgreSQL EBS / CloudSQL|
| 164.312(b)              | Audit Controls (Tamper-Evident Immutable SHA-256)     | PASSED  | `audit_service.py:118`   |
| 164.312(c)(1)           | Integrity Controls (Digital Signatures / Hash Checks)  | PASSED  | Decision PDF Certificates|
| 164.312(d)              | Person or Entity Authentication (JWT + Bcrypt)        | PASSED  | `core/security.py`       |
| 164.312(e)(1)           | Transmission Security (TLS 1.3 Enforced In-Transit)   | PASSED  | Ingress Manifests        |
+====================================================================================================+
```

---

## 2. Business Associate Agreement (BAA) Requirements Checklist

When deploying NutriScan AI with healthcare covered entities, the following contractual provisions must be verified prior to execution:

- [x] **Permitted Uses & Disclosures:** Explicitly restrict software data processing to Clinical Decision Support, longitudinal trend analysis, and authorized operational monitoring.
- [x] **Prohibition on Data Monetization:** Strict prohibition against selling, licensing, or commercializing patient Protected Health Information (PHI) or training external generative AI models on identifiable patient inputs.
- [x] **Sub-Processor Flow-Down:** All third-party cloud infrastructure vendors (e.g. AWS, GCP, Cloudflare) must execute signed BAAs adhering to identical security standards.
- [x] **Breach Notification SLA:** NutriScan AI contracts to notify the Covered Entity within **72 hours** of discovering any confirmed or reasonably suspected security breach of unsecured PHI.
- [x] **Individual Rights Assistance:** API mechanisms enabling the Covered Entity to fulfill patient requests for access, amendment, or accounting of disclosures (§164.524, §164.526, §164.528).
- [x] **Data Return or Destruction at Termination:** Upon contract termination, all electronic PHI must be cryptographically shredded (NIST SP 800-88 Rev. 1 guidelines) with a signed Certificate of Destruction provided within 30 days.

---

## 3. Security Audit & Infrastructure Hardening Checklist

```
+====================================================================================================+
|                         CONTAINER & INFRASTRUCTURE HARDENING CONTROLS                              |
+====================================================================================================+
| Control Category       | Implementation Standard                                | Verification Status      |
+------------------------+--------------------------------------------------------+--------------------------+
| Container Execution    | Non-root user `nutriscan` (UID 10001) enforced         | VERIFIED in Dockerfile   |
| Linux Capabilities     | Dropped all capabilities: `drop: [ALL]`                | VERIFIED in k8s manifests|
| Privilege Escalation   | `allowPrivilegeEscalation: false`                      | VERIFIED in k8s manifests|
| Filesystem Security    | Read-only root filesystem with ephemeral `/tmp` mount  | VERIFIED in k8s manifests|
| Network Isolation      | Pod-to-pod NetworkPolicy blocking ingress outside mesh  | VERIFIED in k8s manifests|
| Memory Management      | Strict CPU (500m/2000m) and Memory (1Gi/4Gi) limits    | VERIFIED in k8s manifests|
| Database Connection    | TLS 1.3 encrypted socket with asyncpg pooling          | VERIFIED in database.py  |
| Secrets Management     | Zero secrets in Git; injected via KMS Secret Provider  | VERIFIED in secret.yaml  |
+====================================================================================================+
```

---

## 4. Access Control & Role-Based Permissions Review (RBAC)

NutriScan AI enforces strict principle-of-least-privilege access across four distinct operational roles:

| Role Name | Permitted System Actions | Restricted / Prohibited Actions |
| :--- | :--- | :--- |
| **`PATIENT`** | View own intake profile; log daily dietary intakes; view doctor-approved nutrition plans; view educational brochures. | Cannot access raw ML inference parameters, other patient profiles, or audit logs. |
| **`CLINICIAN`** | Ingest patient data; view 10-stream dossier; view differential diagnoses & 95% Wilson CIs; perform `APPROVE`/`MODIFY`/`REJECT`/`ESCALATE`; export SOAP notes; order lab tests. | Cannot modify baseline model weights, delete audit trail logs, or alter hospital system configurations. |
| **`NUTRITIONIST`** | Review dietary gap analysis; customize precision food recommendations; tailor 7-day meal plans and grocery lists. | Cannot prescribe pharmaceutical agents or override medical contraindication blocks. |
| **`ADMIN`** | Monitor system health; view aggregated drift telemetry (PSI); manage user authentication lifecycles and SSO bindings. | Cannot view unmasked clinical encounter PHI without documented Break-Glass authorization. |

### Emergency Break-Glass Protocol:
In life-threatening clinical circumstances, an authorized medical officer may trigger a `BREAK_GLASS` session. This action immediately generates an unmaskable alert to the Data Protection Officer, logs the justification, captures the user's IP and timestamp, and issues an immutable SHA-256 event notification.

---

## 5. Logging, Retention & Sanitization Policy

1. **Log Sanitization & PHI Redaction:**
   - All standard application stdout/stderr logs are filtered via a regex-based PHI sanitization filter.
   - Names, email addresses, phone numbers, and Social Security numbers are replaced with `[REDACTED_PHI]`.
   - Encounter lookups are conducted strictly via UUID (`assessment_id` / `patient_id`).
2. **Cryptographic Immutability:**
   - Every assessment, inference vector, and clinician sign-off is hashed using SHA-256:
     $$\text{Hash} = \text{SHA256}(\text{AssessmentID} \parallel \text{Timestamp} \parallel \text{Vector} \parallel \text{ClinicianID} \parallel \text{Action})$$
   - Hashes are recorded in an append-only PostgreSQL table with strict revocation of `UPDATE` and `DELETE` SQL permissions.
3. **Retention Schedule:**
   - **Clinical Decision Records & Audit Logs:** Retained for a minimum of **7 years** (pediatric records: age of majority + 7 years) in compliance with federal medical record standards.
   - **System Performance & Latency Telemetry:** High-resolution Prometheus metrics retained for 90 days; aggregated statistical summaries retained for 3 years.
   - **Automated Database Purge:** Expired non-clinical staging traces purged using automated cron jobs with cryptographic verification receipts.

---

## 6. Security Incident Response Policy

```
[ Security Event Detected ]
         │ (Automated Alert / Clinician Report / Integrity Anomaly)
         ▼
[ Phase 1: Triage & Classification ]
  ├── Level 1: Low (Isolated non-PHI error, cosmetic defect)
  ├── Level 2: Medium (Suspicious unauthorized login attempt blocked, drift spike)
  └── Level 3: Critical (Suspected or confirmed PHI breach, perimeter intrusion)
         │
         ▼ (If Level 3 Critical)
[ Phase 2: Containment & Isolation (< 1 Hour) ]
  - Automated pod network isolation via Kubernetes NetworkPolicy
  - Revocation of compromised API tokens / JWT credentials
  - Database snapshot capture for digital forensics
         │
         ▼
[ Phase 3: Forensic Investigation (< 24 Hours) ]
  - Review of immutable SHA-256 audit ledger
  - Determination of affected patient record count and specific data fields
  - Root Cause Analysis (RCA) compilation by Chief Information Security Officer
         │
         ▼
[ Phase 4: Regulatory & Institutional Notification (< 72 Hours) ]
  - Written notification to affected Covered Entity Privacy Officers
  - Formal report to HHS Office for Civil Rights (OCR) if required under HITECH Act
  - Notification to impacted participants in accordance with 45 CFR §164.404
         │
         ▼
[ Phase 5: Remediation & Post-Incident Review ]
  - Deployment of vulnerability patch with regression testing
  - External audit re-certification and executive sign-off
```
