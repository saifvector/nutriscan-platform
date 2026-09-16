-- ============================================================================
-- Phase 12: Clinical Governance, Safety & Production Monitoring
-- ============================================================================

-- 1. Clinical Audit Records: Immutable transaction log of every screening execution
CREATE TABLE IF NOT EXISTS clinical_audit_records (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL,
    assessment_id UUID,
    user_id UUID,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model_suite_version VARCHAR(50) NOT NULL,
    feature_completeness_pct NUMERIC(5, 2) NOT NULL,
    total_features_evaluated INT NOT NULL,
    observed_features_count INT NOT NULL,
    overall_risk_tier VARCHAR(20) NOT NULL,
    overall_risk_score NUMERIC(5, 2) NOT NULL,
    safety_score NUMERIC(5, 2) NOT NULL,
    safety_tier VARCHAR(20) NOT NULL,
    predictions_json JSONB NOT NULL,
    top_predictors_json JSONB NOT NULL,
    recommendation_ids UUID[],
    evidence_ids VARCHAR[],
    safety_flags_json JSONB,
    inference_latency_ms NUMERIC(7, 2) NOT NULL,
    client_ip VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_prediction_id ON clinical_audit_records(prediction_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON clinical_audit_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_risk_tier ON clinical_audit_records(overall_risk_tier);
CREATE INDEX IF NOT EXISTS idx_audit_safety_tier ON clinical_audit_records(safety_tier);

-- 2. Clinical Safety Events: High-risk violations, upper limit exceedances, and contraindications
CREATE TABLE IF NOT EXISTS clinical_safety_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_id UUID REFERENCES clinical_audit_records(audit_id) ON DELETE SET NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    rule_id VARCHAR(100) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    nutrient VARCHAR(100),
    violating_value NUMERIC(10, 2),
    threshold_value NUMERIC(10, 2),
    clinical_rationale TEXT NOT NULL,
    action_taken VARCHAR(50) NOT NULL CHECK (action_taken IN ('FLAGGED', 'QUARANTINED', 'BLOCKED', 'OVERRIDDEN')),
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_safety_severity ON clinical_safety_events(severity);
CREATE INDEX IF NOT EXISTS idx_safety_timestamp ON clinical_safety_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_safety_rule_id ON clinical_safety_events(rule_id);

-- 3. Model Drift Snapshots: Periodic drift measurements (PSI and KS two-sample tests)
CREATE TABLE IF NOT EXISTS model_drift_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    target_or_feature VARCHAR(100) NOT NULL,
    drift_category VARCHAR(50) NOT NULL CHECK (drift_category IN ('FEATURE', 'POPULATION', 'PREDICTION', 'NUTRIENT_INTAKE')),
    metric_type VARCHAR(20) NOT NULL CHECK (metric_type IN ('PSI', 'KS_2SAMPLE', 'WASSERSTEIN')),
    metric_value NUMERIC(8, 5) NOT NULL,
    p_value NUMERIC(8, 5),
    drift_status VARCHAR(20) NOT NULL CHECK (drift_status IN ('STABLE', 'MODERATE_SHIFT', 'SIGNIFICANT_DRIFT')),
    alert_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    sample_size INT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_drift_target ON model_drift_snapshots(target_or_feature);
CREATE INDEX IF NOT EXISTS idx_drift_status ON model_drift_snapshots(drift_status);
CREATE INDEX IF NOT EXISTS idx_drift_timestamp ON model_drift_snapshots(timestamp);

-- 4. Demographic Validation Benchmarks: Stratified holdout performance tracking
CREATE TABLE IF NOT EXISTS validation_benchmarks (
    benchmark_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target VARCHAR(100) NOT NULL,
    subgroup_category VARCHAR(50) NOT NULL, -- AGE, SEX, RACE_ETHNICITY, INCOME_PIR
    subgroup_value VARCHAR(100) NOT NULL,
    sample_size INT NOT NULL,
    prevalence_pct NUMERIC(5, 2) NOT NULL,
    auroc NUMERIC(5, 4) NOT NULL,
    auprc NUMERIC(5, 4) NOT NULL,
    sensitivity NUMERIC(5, 4) NOT NULL,
    specificity NUMERIC(5, 4) NOT NULL,
    ppv NUMERIC(5, 4) NOT NULL,
    npv NUMERIC(5, 4) NOT NULL,
    f1_score NUMERIC(5, 4) NOT NULL,
    calibrated_ece NUMERIC(6, 4) NOT NULL,
    brier_score NUMERIC(6, 4) NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_validation_target ON validation_benchmarks(target);
CREATE INDEX IF NOT EXISTS idx_validation_subgroup ON validation_benchmarks(subgroup_category, subgroup_value);

-- 5. Monitoring Alerts: System notifications, drift warnings, and safety breach alerts
CREATE TABLE IF NOT EXISTS monitoring_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('DRIFT_ALERT', 'CALIBRATION_DEGRADATION', 'SAFETY_VIOLATION', 'PREDICTION_FAILURE', 'DATA_QUALITY', 'FAIRNESS_DISPARITY')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    metadata_json JSONB,
    is_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON monitoring_alerts(is_acknowledged);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON monitoring_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON monitoring_alerts(timestamp);
