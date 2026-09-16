# NutriScan AI — Production Deployment & Operations Package

**Document Version:** 1.0 (Production Release)  
**Target Environment:** Cloud-Native Managed Kubernetes (AWS EKS v1.28+ / GCP GKE v1.28+)  
**Database:** Managed PostgreSQL 15+ (AWS RDS Multi-AZ / Cloud SQL) with `asyncpg` connection pooling  
**Ingress & Security:** TLS 1.3 terminating Ingress with Cert-Manager and Let's Encrypt / DigiCert  

---

## 1. Kubernetes Production Deployment Runbook

### 1.1 Pre-Flight Prerequisites
- Kubernetes CLI (`kubectl` v1.28+) configured with target cluster credentials.
- Helm v3.12+ installed.
- Cloud KMS / HashiCorp Vault Secrets Operator running.
- Target Namespace: `nutriscan-production`.

### 1.2 Step-by-Step Deployment Commands

```bash
# 1. Create and verify the isolated production namespace
kubectl create namespace nutriscan-production --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace nutriscan-production pod-security.kubernetes.io/enforce=restricted

# 2. Deploy database secret via Cloud KMS / Vault integration
kubectl apply -f deploy/kubernetes/secret.yaml -n nutriscan-production

# 3. Apply ConfigMap containing non-sensitive application environment variables
kubectl apply -f deploy/kubernetes/configmap.yaml -n nutriscan-production

# 4. Deploy NutriScan AI production pods via Helm chart
helm upgrade --install nutriscan ./deploy/helm/nutriscan \
  --namespace nutriscan-production \
  --set image.repository="123456789012.dkr.ecr.us-east-1.amazonaws.com/nutriscan-ai" \
  --set image.tag="v1.0.0" \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --set resources.limits.cpu="2000m" \
  --set resources.limits.memory="4Gi" \
  --set resources.requests.cpu="500m" \
  --set resources.requests.memory="1Gi"

# 5. Apply TLS Ingress routing
kubectl apply -f deploy/kubernetes/ingress.yaml -n nutriscan-production

# 6. Verify rollout status and pod health
kubectl rollout status deployment/nutriscan-backend -n nutriscan-production
kubectl get pods -n nutriscan-production -l app.kubernetes.io/name=nutriscan
```

### 1.3 Post-Deployment Smoke Verification
```bash
# Verify database connection pool and application liveness
curl -fsS https://api.nutriscan.health/health | jq .

# Expected Output:
# {
#   "status": "HEALTHY",
#   "database": {
#     "status": "HEALTHY",
#     "connected": true,
#     "pool_size": 20,
#     "checked_out": 0
#   }
# }
```

---

## 2. Backup & Continuous Data Protection Strategy

```
[ Active PostgreSQL Primary ]
         │ (Streaming Replication to Standby AZ)
         ├─────────────────────────────────────────┐
         ▼                                         ▼
[ Synchronous Standby (AZ 2) ]        [ Continuous WAL Archiving ]
  (Zero Data Loss RPO)                              │ (Encrypted S3/GCS Bucket)
                                                    ▼
                                      [ Point-in-Time Recovery (PITR) ]
                                      - Recover to any second in past 30 days
                                      - Cross-Region Replication to Secondary
```

1. **Continuous WAL Archiving (Point-in-Time Recovery):**
   - Continuous Write-Ahead Log (WAL) archiving pushes transaction logs every 60 seconds to a secondary encrypted object storage bucket.
   - **RPO (Recovery Point Objective):** $< 5\text{ minutes}$.
2. **Automated Daily Snapshots:**
   - Full automated snapshot generated daily at 02:00 UTC.
   - Snapshots encrypted with dedicated AWS KMS / Cloud KMS keys (AES-256).
3. **Retention Schedule:**
   - Daily snapshots retained for 30 days.
   - Weekly snapshots retained for 12 weeks.
   - Monthly snapshots retained for 7 years (medical compliance).
4. **Automated Restoration Verification:**
   - Automated weekly cron job restores the latest snapshot into an isolated sandbox database, executes data integrity validation queries, and issues a signed report.

---

## 3. Disaster Recovery (DR) Plan

```
+====================================================================================================+
|                              DISASTER RECOVERY ARCHITECTURAL TIERS                                 |
+====================================================================================================+
| Parameter              | Primary Region (`us-east-1`)            | Secondary DR Region (`us-west-2`)|
+------------------------+-----------------------------------------+----------------------------------+
| Compute Topology       | Active EKS Cluster (2–10 Pods)          | Warm Standby Cluster (2 Pods)    |
| Database Engine        | Multi-AZ Amazon RDS PostgreSQL 15       | Read Replica (Async Replication) |
| Storage Replication    | Multi-AZ EBS Volumes                    | Cross-Region S3 Bucket Mirroring |
| Ingress Routing        | Route 53 Weighted DNS (100% Primary)    | Route 53 Health Checked (0% DR)  |
| Target RTO             | < 30 Minutes                            | Automated DNS Cutover in < 5 Min |
| Target RPO             | < 15 Minutes                            | Max WAL Lag: < 30 Seconds        |
+====================================================================================================+
```

### 3.1 Disaster Recovery Failover Protocol
1. **Trigger Condition:** Unrecoverable outage in primary cloud region lasting $> 15\text{ minutes}$ with cloud provider SLA breach confirmation.
2. **Execution Steps:**
   ```bash
   # 1. Promote secondary RDS read replica to standalone primary writer
   aws rds promote-read-replica --db-instance-identifier nutriscan-db-dr --region us-west-2

   # 2. Scale up compute nodes in secondary DR cluster
   kubectl scale deployment/nutriscan-backend --replicas=6 -n nutriscan-production --context=us-west-2

   # 3. Update Route 53 DNS routing policy to point api.nutriscan.health to DR Ingress IP
   aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch file://deploy/dr_dns_failover.json
   ```
3. **Failback Procedure:** Re-establish asynchronous replication from secondary back to restored primary region before scheduling an off-peak maintenance window cutover.

---

## 4. Production Monitoring Configuration

NutriScan AI deploys a zero-overhead pure ASGI Prometheus middleware collecting high-resolution metrics exposed at `/metrics`.

### 4.1 Core Metric Definitions
- `nutriscan_requests_total`: Counter tracking total requests partitioned by method, path, and HTTP status code.
- `nutriscan_request_duration_seconds`: Histogram measuring execution latency percentiles ($p_{50}, p_{90}, p_{95}, p_{99}$) across endpoints.
- `nutriscan_inference_duration_seconds`: Histogram measuring pure ML model prediction duration.
- `nutriscan_db_connections_active`: Gauge tracking active checked-out connections from the `asyncpg` pool.
- `nutriscan_safety_violations_total`: Counter tracking intercepted NIH UL and contraindication events.
- `nutriscan_population_drift_psi`: Gauge recording real-time Population Stability Index values per nutrient target.

---

## 5. Alerting Configuration & PagerDuty Runbooks

### 5.1 Prometheus Alert Rules (`prometheus-alerts.yml`)

```yaml
groups:
  - name: nutriscan_clinical_alerts
    rules:
      - alert: ClinicalLatencySLABreach
        expr: histogram_quantile(0.95, sum(rate(nutriscan_request_duration_seconds_bucket[5m])) by (le)) > 0.200
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "NutriScan API p95 latency exceeded 200ms clinical SLA target."
          runbook_url: "https://ops.nutriscan.health/runbooks/high-latency"

      - alert: HighErrorRateSpike
        expr: sum(rate(nutriscan_requests_total{status=~"5.."}[5m])) / sum(rate(nutriscan_requests_total[5m])) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API 5xx error rate exceeds 1% of total traffic."
          runbook_url: "https://ops.nutriscan.health/runbooks/error-spike"

      - alert: DatabasePoolExhaustion
        expr: nutriscan_db_connections_active > 18
        for: 2m
        labels:
          severity: high
        annotations:
          summary: "PostgreSQL asyncpg connection pool exceeds 90% capacity (18/20)."
          runbook_url: "https://ops.nutriscan.health/runbooks/db-pool"

      - alert: CriticalModelDriftDetected
        expr: nutriscan_population_drift_psi >= 0.20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Population Stability Index (PSI) >= 0.20 indicates significant distribution shift."
          runbook_url: "https://ops.nutriscan.health/runbooks/model-drift"
```

---

## 6. Zero-Downtime Rollback Procedures

```bash
# 1. Identify previous healthy Helm release revision
helm history nutriscan -n nutriscan-production

# 2. Execute instantaneous rollback to prior stable revision
helm rollback nutriscan 3 -n nutriscan-production

# 3. Verify pod termination and restoration of stable deployment
kubectl rollout status deployment/nutriscan-backend -n nutriscan-production

# 4. Verify API response status
curl -I https://api.nutriscan.health/health
```

### Database Schema Rollback Policy:
- All database migrations must strictly maintain **N-1 backward compatibility**.
- Column drops and breaking table transformations are prohibited in single-step releases.
- If a migration failure occurs, the application code rolls back without requiring an emergency database downgrade.
