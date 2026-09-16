# NutriScan AI — Commercial Operations Package

**Document Version:** 1.0 (Production Master)  
**Target Market:** Enterprise Healthcare Systems, Outpatient Clinic Networks, Accountable Care Organizations (ACOs), Digital Health Providers  
**Operational Framework:** ITIL v4 Service Management & SOC 2 Type II Security Standard  

---

## 1. Enterprise Customer Onboarding Workflow

```
[ Phase 1: Contract & Security Clearance ] (Day 1–7)
  ├── Counter-execution of Master Services Agreement (MSA) & Business Associate Agreement (BAA)
  ├── Completion of Enterprise Security Questionnaire (HECVAT / CAIQ)
  └── Assignment of Dedicated Technical Account Manager (TAM) & Lead Clinical Liaison
         │
         ▼
[ Phase 2: Tenant Provisioning & Identity Federation ] (Day 8–14)
  ├── Provisioning of isolated multi-tenant organization partition in NutriScan Cloud
  ├── SAML 2.0 / OpenID Connect (OIDC) Single Sign-On integration (Okta, Azure AD, Ping)
  └── RBAC role assignments (`CLINICIAN`, `NUTRITIONIST`, `ADMIN`) mapped to clinic AD groups
         │
         ▼
[ Phase 3: Clinical Workflow Configuration ] (Day 15–21)
  ├── Distribution of Epic Hyperspace SmartTool dot-phrases & Cerner Millennium templates
  ├── Customization of clinic-specific confirmatory blood draw laboratory order sets
  └── Hands-on clinician onboarding workshops with interactive Copilot training
         │
         ▼
[ Phase 4: Soft-Launch & Supervised Intake ] (Day 22–30)
  ├── First 50 patient encounters supervised by NutriScan Clinical Implementation Specialist
  ├── Verification of SHA-256 audit log stream and EMR clipboard export fidelity
  └── Formal Transition to General Enterprise Production Availability
```

---

## 2. Enterprise Sales Handoff Checklist

```
+====================================================================================================+
|                              ENTERPRISE SALES HANDOFF CHECKLIST                                    |
+====================================================================================================+
| Verification Item                                    | Assigned Owner         | Completion Verified |
+------------------------------------------------------+------------------------+---------------------+
| 1. Executed MSA, Order Form & Pricing Schedule       | Enterprise Account Exec| [ ]                 |
| 2. Countersigned HIPAA BAA on file                   | Corporate Legal Counsel| [ ]                 |
| 3. Designated Customer Clinical Lead (MD/DO) named   | Account Exec           | [ ]                 |
| 4. Designated Customer IT/Security Lead named        | Account Exec           | [ ]                 |
| 5. Expected Monthly Assessment Volume baseline set   | TAM / Solutions Arch   | [ ]                 |
| 6. EMR Vendor & Version identified (Epic/Cerner/Other)| Solutions Architect   | [ ]                 |
| 7. Staging Tenant ID generated in admin portal       | Cloud Operations Lead  | [ ]                 |
| 8. Customer Success Manager (CSM) kickoff scheduled  | Customer Success Lead  | [ ]                 |
+====================================================================================================+
```

---

## 3. Tiered Support Workflow

```
[ Incident / Support Ticket Submitted ]
         │ (Email, Clinical Portal Ticket, or Emergency Telephone Hotline)
         ▼
[ Tier 1: Frontline Operations Helpdesk ]
  - 24/7/365 coverage for password resets, login issues, general portal navigation
  - Initial triage against known knowledge base articles within 15 minutes
         │
         ▼ (If Unresolved or Technical/Clinical in Nature)
[ Tier 2: Clinical Application & Systems Engineering ]
  - In-depth investigation of data intake discrepancies, EMR export formatting errors
  - Assessment of clinical rule outputs and interaction queries with clinical team
         │
         ▼ (If Infrastructure, Outage, or Core Algorithmic Defect)
[ Tier 3: Core MLOps & Platform Engineering ]
  - Direct engagement of on-call MLOps and Backend Platform Architects
  - Code patches, hotfix deployment, database query optimization, infrastructure scaling
```

---

## 4. Operational Escalation Matrix

```
+====================================================================================================+
|                                     INCIDENT ESCALATION MATRIX                                     |
+====================================================================================================+
| Severity Level | Definition / Criteria             | Initial Response | Target Resolution | Escalation Contact       |
+----------------+-----------------------------------+------------------+-------------------+--------------------------+
| **P1: CRITICAL**| Full platform outage; API down;   | **< 15 Minutes** | **< 4 Hours**     | CTO, VP Engineering,     |
|                | suspected security/PHI breach.    |                  |                   | On-Call MLOps Lead       |
+----------------+-----------------------------------+------------------+-------------------+--------------------------+
| **P2: HIGH**   | Severe degradation; p95 latency   | **< 1 Hour**     | **< 8 Hours**     | Principal Backend Eng,   |
|                | > 500ms; single clinic blocked.   |                  |                   | Clinical Product Manager |
+----------------+-----------------------------------+------------------+-------------------+--------------------------+
| **P3: MEDIUM** | Non-blocking defect; single model | **< 4 Hours**    | **< 24 Hours**    | Senior Software Engineer,|
|                | warning; export formatting issue. |                  |                   | Support Desk Lead        |
+----------------+-----------------------------------+------------------+-------------------+--------------------------+
| **P4: LOW**    | Minor cosmetic issue; feature     | **< 24 Hours**   | Scheduled Release | Assigned Product Backlog |
|                | enhancement request; docs update. |                  |                   |                          |
+====================================================================================================+
```

---

## 5. Service Level Agreement (SLA) Definitions

1. **Uptime Commitment:**
   - NutriScan AI guarantees **99.9% Monthly Application Availability**, excluding planned maintenance windows.
   - Monthly Uptime Percentage is computed as:
     $$\text{Uptime \%} = \frac{\text{Total Minutes in Month} - \text{Unscheduled Outage Minutes}}{\text{Total Minutes in Month}} \times 100$$
2. **Latency Commitments:**
   - $p_{95}$ API execution latency guaranteed $< 200\text{ ms}$ under contracted peak request volumes.
3. **Scheduled Maintenance Windows:**
   - Maintenance scheduled strictly during off-peak hours (Sundays 01:00–04:00 UTC) with a minimum of **5 business days advance notice**.
4. **Service Credits for Downtime:**
   - Availability $99.0\% - 99.89\% \rightarrow 10\%$ Monthly Fee Credit.
   - Availability $95.0\% - 98.99\% \rightarrow 25\%$ Monthly Fee Credit.
   - Availability $< 95.0\% \rightarrow 50\%$ Monthly Fee Credit.

---

## 6. Standard Production Support Runbooks

### Runbook 6.1: Handling Model Drift Alert (`PSI >= 0.20`)
1. **Notification:** PagerDuty triggers `CriticalModelDriftDetected` alert.
2. **Inspection:** MLOps engineer navigates to `/monitoring` dashboard; identifies the specific nutrient target triggering distribution divergence.
3. **Forensic Analysis:** Query database to inspect recent demographic and dietary patterns in incoming requests.
4. **Action:**
   - If benign demographic shift (e.g. specialized vegan clinic onboarding), adjust baseline reference weighting in `drift_engine.py`.
   - If aberrant input distributions or sensor errors, flag for retrained model checkpoint deployment.

### Runbook 6.2: Handling PostgreSQL Pool Starvation
1. **Notification:** Prometheus triggers `DatabasePoolExhaustion` ($> 18/20$ connections checked out).
2. **Inspection:** Execute `check_db_health()` and inspect active queries:
   ```sql
   SELECT pid, age(clock_timestamp(), query_start), usename, query 
   FROM pg_stat_activity 
   WHERE state != 'idle' AND query NOT ILIKE '%pg_stat_activity%'
   ORDER BY query_start ASC LIMIT 5;
   ```
3. **Action:** Terminate long-running blocking analytics queries; scale `max_overflow` in `database.py` if legitimate traffic burst.
