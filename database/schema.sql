-- ============================================================================
-- Project: Integrated AI-Based Nutrient Deficiency Screening and Personalized Nutrition Platform
-- Phase: Phase 1 - Project Foundation and Database Architecture
-- Target Database: PostgreSQL 15+
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

CREATE TYPE user_role AS ENUM ('USER', 'NUTRITIONIST', 'CLINICIAN', 'ADMIN');
CREATE TYPE biological_gender AS ENUM ('MALE', 'FEMALE', 'OTHER');
CREATE TYPE activity_level AS ENUM (
    'SEDENTARY',            -- Little to no exercise
    'LIGHTLY_ACTIVE',       -- Light exercise 1-3 days/week
    'MODERATELY_ACTIVE',    -- Moderate exercise 3-5 days/week
    'VERY_ACTIVE',          -- Hard exercise 6-7 days/week
    'EXTRA_ACTIVE'          -- Physical labor or athletic training
);
CREATE TYPE diet_pattern AS ENUM (
    'OMNIVORE',
    'VEGETARIAN',
    'VEGAN',
    'PESCATARIAN',
    'KETO',
    'PALEO',
    'MEDITERRANEAN',
    'OTHER'
);
CREATE TYPE deficiency_risk_level AS ENUM ('LOW', 'MODERATE', 'HIGH', 'CRITICAL');
CREATE TYPE report_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

-- ============================================================================
-- 1. USERS TABLE
-- Authentication, access control, and identity lifecycle
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'USER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- 2. USER PROFILES TABLE
-- Demographic, physiological baseline, and persistent health profile
-- ============================================================================
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender biological_gender NOT NULL,
    height_cm NUMERIC(5, 2) NOT NULL CHECK (height_cm > 40 AND height_cm < 260),
    weight_kg NUMERIC(5, 2) NOT NULL CHECK (weight_kg > 20 AND weight_kg < 350),
    bmi NUMERIC(4, 1) GENERATED ALWAYS AS (
        ROUND(weight_kg / ((height_cm / 100.0) * (height_cm / 100.0)), 1)
    ) STORED,
    blood_group VARCHAR(5),
    pregnancy_status BOOLEAN DEFAULT FALSE,
    lactating_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_dob ON user_profiles(date_of_birth);

-- ============================================================================
-- 3. HEALTH ASSESSMENTS TABLE
-- Immutable point-in-time screening evaluation records
-- Contains raw user questionnaire answers (diet, lifestyle, symptoms, supplements)
-- ============================================================================
CREATE TABLE health_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assessment_version VARCHAR(20) NOT NULL DEFAULT 'v1.0',
    
    -- Point-in-time physiological snapshots (allows tracking changes over time)
    age_at_assessment INT NOT NULL CHECK (age_at_assessment >= 1 AND age_at_assessment <= 125),
    height_cm NUMERIC(5, 2) NOT NULL,
    weight_kg NUMERIC(5, 2) NOT NULL,
    bmi NUMERIC(4, 1) NOT NULL,
    
    -- Dietary Habits
    dietary_pattern diet_pattern NOT NULL,
    meals_per_day INT NOT NULL CHECK (meals_per_day BETWEEN 1 AND 8),
    water_intake_liters NUMERIC(3, 1) NOT NULL CHECK (water_intake_liters >= 0.0),
    daily_fruit_vegetable_servings INT NOT NULL DEFAULT 0,
    junk_food_frequency VARCHAR(50), -- e.g., 'RARELY', '1_2_PER_WEEK', 'DAILY'
    dietary_restrictions JSONB NOT NULL DEFAULT '[]'::jsonb, -- e.g. ["dairy-free", "gluten-free"]
    
    -- Lifestyle Factors
    activity_level activity_level NOT NULL,
    sleep_hours_per_night NUMERIC(3, 1) NOT NULL CHECK (sleep_hours_per_night BETWEEN 0 AND 24),
    smoking_status VARCHAR(50) NOT NULL, -- 'NEVER', 'FORMER', 'CURRENT'
    alcohol_consumption VARCHAR(50) NOT NULL, -- 'NONE', 'OCCASIONAL', 'MODERATE', 'HEAVY'
    sunlight_exposure_min_per_day INT NOT NULL DEFAULT 15,
    stress_level INT NOT NULL CHECK (stress_level BETWEEN 1 AND 10),
    
    -- Symptoms (Clinical Indicators of Deficiencies)
    -- Structured JSONB with severity ratings (e.g. {"fatigue": 8, "brittle_nails": 5, "hair_loss": 6, "muscle_cramps": 3})
    symptoms JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Medical History & Conditions
    -- Structured JSONB: Chronic diseases, GI tract absorption disorders (e.g. Celiac, Crohn's, Gastritis)
    medical_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    -- Supplement Usage
    -- Structured JSONB: Current vitamins/minerals taken, dosages, frequency
    supplement_usage JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- ML Feature Vector Ready Snapshot
    feature_vector JSONB, -- Normalized numerical feature map directly fed into ML model
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_assessments_user_id ON health_assessments(user_id);
CREATE INDEX idx_health_assessments_created_at ON health_assessments(created_at DESC);
CREATE INDEX idx_health_assessments_symptoms_gin ON health_assessments USING GIN (symptoms);
CREATE INDEX idx_health_assessments_medical_history_gin ON health_assessments USING GIN (medical_history);

-- ============================================================================
-- 4. NUTRIENT PREDICTIONS TABLE
-- Outputs of the AI/ML deficiency inference engine for an assessment
-- ============================================================================
CREATE TABLE nutrient_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES health_assessments(id) ON DELETE CASCADE,
    nutrient_code VARCHAR(50) NOT NULL, -- Canonical: 'PROTEIN', 'VITAMIN_A', 'VITAMIN_B12', 'FOLATE_B9', 'VITAMIN_C', 'VITAMIN_D', 'VITAMIN_E', 'IRON', 'CALCIUM', 'ZINC', 'MAGNESIUM', 'VITAMIN_B1', 'VITAMIN_B2', 'VITAMIN_B3', 'VITAMIN_B6', 'POTASSIUM', 'SELENIUM', 'IODINE'
    nutrient_name VARCHAR(100) NOT NULL, -- e.g., 'Vitamin D3 (Cholecalciferol)', 'Thiamine (Vitamin B1)', 'Potassium'
    probability_score NUMERIC(5, 4) NOT NULL CHECK (probability_score BETWEEN 0.0000 AND 1.0000),
    confidence_score NUMERIC(5, 4) NOT NULL DEFAULT 0.8500 CHECK (confidence_score BETWEEN 0.0000 AND 1.0000),
    confidence_level VARCHAR(30) NOT NULL DEFAULT 'High Confidence', -- 'High Confidence', 'Medium Confidence', 'Low Confidence'
    predicted_risk_level deficiency_risk_level NOT NULL,
    priority_rank INT,
    confidence_interval_low NUMERIC(5, 4),
    confidence_interval_high NUMERIC(5, 4),
    model_name VARCHAR(100) NOT NULL, -- e.g., 'xgboost_deficiency_classifier'
    model_version VARCHAR(50) NOT NULL, -- e.g., 'v2.1.0'
    inference_latency_ms INT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nutrient_predictions_assessment_id ON nutrient_predictions(assessment_id);
CREATE INDEX idx_nutrient_predictions_nutrient_code ON nutrient_predictions(nutrient_code);
CREATE INDEX idx_nutrient_predictions_risk_level ON nutrient_predictions(predicted_risk_level);

-- ============================================================================
-- 5. RISK FACTORS TABLE
-- Explainability & Attribution: Links specific user features to predicted deficiencies
-- (SHAP / LIME values, physiological causal attributions)
-- ============================================================================
CREATE TABLE risk_factors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES nutrient_predictions(id) ON DELETE CASCADE,
    factor_category VARCHAR(100) NOT NULL, -- 'SYMPTOM', 'DIET', 'LIFESTYLE', 'MEDICAL_HISTORY'
    factor_name VARCHAR(150) NOT NULL, -- e.g., 'Low Sunlight Exposure', 'Vegan Diet without B12', 'Severe Fatigue'
    factor_description TEXT NOT NULL,
    impact_score NUMERIC(5, 4) NOT NULL, -- Positive = increases deficiency risk, Negative = protective
    impact_magnitude VARCHAR(20) NOT NULL, -- 'HIGH', 'MEDIUM', 'LOW'
    evidence_reference TEXT, -- Clinical citation or rule reference
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_factors_prediction_id ON risk_factors(prediction_id);
CREATE INDEX idx_risk_factors_category ON risk_factors(factor_category);

-- ============================================================================
-- 6. FOOD RECOMMENDATIONS TABLE
-- Evidence-backed, personalized dietary intervention suggestions
-- ============================================================================
CREATE TABLE food_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES nutrient_predictions(id) ON DELETE CASCADE,
    nutrient_name VARCHAR(100), -- e.g. 'Iron', 'Vitamin D'
    food_name VARCHAR(150) NOT NULL, -- e.g., 'Wild Atlantic Salmon', 'Spinach', 'Lentils'
    food_group VARCHAR(100) NOT NULL, -- 'LEAFY_GREENS', 'SEAFOOD', 'LEGUMES', 'DAIRY_ALTERNATIVES'
    priority_rank INT DEFAULT 1, -- 1 = Priority 1 (Staple), 2 = Priority 2 (Supportive), 3 = Priority 3 (Rotation)
    recommendation_score NUMERIC(5, 2), -- 0.00 to 100.00 composite score
    serving_size VARCHAR(100) NOT NULL, -- e.g., '100g cooked', '1 cup'
    nutrient_density_mg NUMERIC(8, 2) NOT NULL, -- Estimated targeted nutrient concentration per serving
    unit VARCHAR(20) NOT NULL DEFAULT 'mg', -- 'mg', 'mcg', 'IU'
    dietary_compatibility VARCHAR(100) NOT NULL, -- 'VEGAN', 'VEGETARIAN', 'ALL'
    rationale TEXT, -- Clinical explanation why this food was chosen
    preparation_tips TEXT, -- e.g., 'Pair with Vitamin C rich foods for enhanced non-heme iron absorption'
    contraindications TEXT, -- e.g., 'Caution with kidney stones due to oxalates'
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_food_recommendations_prediction_id ON food_recommendations(prediction_id);
CREATE INDEX idx_food_recommendations_food_group ON food_recommendations(food_group);

-- ============================================================================
-- 7. GENERATED REPORTS TABLE
-- Clinical-grade compiled summaries, PDF exports, and dashboard views
-- ============================================================================
CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES health_assessments(id) ON DELETE CASCADE,
    report_title VARCHAR(255) NOT NULL,
    status report_status NOT NULL DEFAULT 'PENDING',
    summary_text TEXT,
    overall_health_score INT CHECK (overall_health_score BETWEEN 0 AND 100),
    report_payload JSONB NOT NULL DEFAULT '{}'::jsonb, -- Complete static JSON snapshot of assessment + predictions + risk factors + food
    pdf_file_url VARCHAR(500),
    generated_by VARCHAR(100) DEFAULT 'AI_PIPELINE_ENGINE',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_generated_reports_user_id ON generated_reports(user_id);
CREATE INDEX idx_generated_reports_assessment_id ON generated_reports(assessment_id);
CREATE INDEX idx_generated_reports_status ON generated_reports(status);

-- ============================================================================
-- 8. ASSESSMENT HISTORY TABLE
-- Historical snapshots and longitudinal tracking of screening assessments
-- ============================================================================
CREATE TABLE assessment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES health_assessments(id) ON DELETE CASCADE,
    assessment_number INT NOT NULL DEFAULT 1,
    version_tag VARCHAR(50) NOT NULL DEFAULT 'v1.0',
    health_score INT NOT NULL CHECK (health_score BETWEEN 0 AND 100),
    health_category VARCHAR(50) NOT NULL,
    risk_distribution JSONB NOT NULL DEFAULT '{}'::jsonb,
    deficiencies_identified JSONB NOT NULL DEFAULT '[]'::jsonb,
    snapshot_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    clinical_notes TEXT,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessment_history_user_id ON assessment_history(user_id);
CREATE INDEX idx_assessment_history_assessment_id ON assessment_history(assessment_id);
CREATE INDEX idx_assessment_history_recorded_at ON assessment_history(recorded_at DESC);

-- ============================================================================
-- 9. HEALTH SCORES TABLE
-- Granular score breakdown, confidence weighting, and clinical interpretations
-- ============================================================================
CREATE TABLE health_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES health_assessments(id) ON DELETE CASCADE,
    score INT NOT NULL CHECK (score BETWEEN 0 AND 100),
    category VARCHAR(50) NOT NULL, -- EXCELLENT, GOOD, MODERATE_RISK, HIGH_RISK, CRITICAL
    baseline_score NUMERIC(5, 2) NOT NULL DEFAULT 100.0,
    nutrient_risk_deduction NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    interaction_penalty NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    lifestyle_modifier NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    confidence_adjustment NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    deficiency_count INT NOT NULL DEFAULT 0,
    protective_factor_count INT NOT NULL DEFAULT 0,
    interpretation TEXT NOT NULL,
    breakdown_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_scores_user_id ON health_scores(user_id);
CREATE INDEX idx_health_scores_assessment_id ON health_scores(assessment_id);
CREATE INDEX idx_health_scores_category ON health_scores(category);

-- ============================================================================
-- 10. PROGRESS METRICS TABLE
-- Longitudinal progress analytics, velocity, resolved risks, and nutrient trends
-- ============================================================================
CREATE TABLE progress_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_assessment_id UUID NOT NULL REFERENCES health_assessments(id) ON DELETE CASCADE,
    baseline_assessment_id UUID REFERENCES health_assessments(id) ON DELETE SET NULL,
    previous_assessment_id UUID REFERENCES health_assessments(id) ON DELETE SET NULL,
    health_score_delta INT NOT NULL DEFAULT 0,
    recovery_velocity NUMERIC(5, 2) NOT NULL DEFAULT 0.0, -- Points improvement per week
    deficiencies_resolved INT NOT NULL DEFAULT 0,
    emerging_risks INT NOT NULL DEFAULT 0,
    most_improved_nutrient VARCHAR(100),
    highest_risk_nutrient VARCHAR(100),
    fastest_recovery_nutrient VARCHAR(100),
    nutrient_progress JSONB NOT NULL DEFAULT '{}'::jsonb, -- Per-nutrient tracking
    lifestyle_progress JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_progress_metrics_user_id ON progress_metrics(user_id);
CREATE INDEX idx_progress_metrics_current_assessment_id ON progress_metrics(current_assessment_id);

-- ============================================================================
-- AUTOMATED TRIGGERS FOR TIMESTAMP SYNCHRONIZATION
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_user_profiles_updated_at
BEFORE UPDATE ON user_profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
