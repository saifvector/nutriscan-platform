-- Phase 13: Real-World Clinical Intelligence, Personalization & Continuous Learning
-- Database Migration Schema

-- 1. Personalized Nutrition Strategies
CREATE TABLE IF NOT EXISTS personalized_nutrition_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID,
    user_id UUID,
    dietary_pattern VARCHAR(50) NOT NULL DEFAULT 'OMNIVORE',
    cultural_pattern VARCHAR(50) NOT NULL DEFAULT 'MEDITERRANEAN',
    budget_tier VARCHAR(20) NOT NULL DEFAULT 'MODERATE',
    daily_budget_usd NUMERIC(6, 2) DEFAULT 12.50,
    target_deficiencies JSONB NOT NULL DEFAULT '[]'::jsonb,
    biomarker_priorities JSONB NOT NULL DEFAULT '[]'::jsonb,
    strategy_summary TEXT NOT NULL,
    macro_split JSONB NOT NULL DEFAULT '{"protein_pct": 25, "carb_pct": 45, "fat_pct": 30}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_p13_strategies_assessment ON personalized_nutrition_strategies(assessment_id);
CREATE INDEX IF NOT EXISTS idx_p13_strategies_user ON personalized_nutrition_strategies(user_id);

-- 2. Precision Food Recommendations
CREATE TABLE IF NOT EXISTS precision_food_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES personalized_nutrition_strategies(id) ON DELETE CASCADE,
    food_name VARCHAR(150) NOT NULL,
    usda_fdc_id VARCHAR(50),
    category VARCHAR(50) NOT NULL,
    serving_size VARCHAR(50) NOT NULL,
    primary_nutrients JSONB NOT NULL DEFAULT '[]'::jsonb,
    nutrient_density_score NUMERIC(5, 2) NOT NULL,
    cost_efficiency_score NUMERIC(5, 2) NOT NULL,
    bioavailability_score NUMERIC(5, 2) NOT NULL,
    clinical_relevance_score NUMERIC(5, 2) NOT NULL,
    adherence_likelihood_score NUMERIC(5, 2) NOT NULL,
    composite_precision_score NUMERIC(5, 2) NOT NULL,
    culinary_role VARCHAR(50) NOT NULL,
    preparation_tips TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_p13_foods_strategy ON precision_food_recommendations(strategy_id);
CREATE INDEX IF NOT EXISTS idx_p13_foods_score ON precision_food_recommendations(composite_precision_score DESC);

-- 3. Intelligent Meal Plans
CREATE TABLE IF NOT EXISTS intelligent_meal_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES personalized_nutrition_strategies(id) ON DELETE CASCADE,
    user_id UUID,
    plan_type VARCHAR(20) NOT NULL DEFAULT 'WEEKLY', -- DAILY, WEEKLY
    total_estimated_cost_usd NUMERIC(8, 2) NOT NULL,
    daily_average_calories NUMERIC(6, 1) NOT NULL,
    nutrient_adequacy_score NUMERIC(5, 2) NOT NULL,
    schedule JSONB NOT NULL DEFAULT '[]'::jsonb, -- Array of daily meal items
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_p13_meals_strategy ON intelligent_meal_plans(strategy_id);

-- 4. Smart Grocery Lists
CREATE TABLE IF NOT EXISTS smart_grocery_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_plan_id UUID REFERENCES intelligent_meal_plans(id) ON DELETE CASCADE,
    user_id UUID,
    items JSONB NOT NULL DEFAULT '[]'::jsonb, -- Categorized items by aisle
    total_estimated_cost_usd NUMERIC(8, 2) NOT NULL,
    item_count INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_p13_grocery_meal_plan ON smart_grocery_lists(meal_plan_id);

-- 5. Longitudinal Learning Profiles & Response Patterns
CREATE TABLE IF NOT EXISTS longitudinal_learning_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE,
    successful_interventions JSONB NOT NULL DEFAULT '[]'::jsonb,
    failed_interventions JSONB NOT NULL DEFAULT '[]'::jsonb,
    tolerance_penalties JSONB NOT NULL DEFAULT '{}'::jsonb,
    efficacy_multipliers JSONB NOT NULL DEFAULT '{}'::jsonb,
    overall_responsiveness_score NUMERIC(5, 2) DEFAULT 80.0,
    last_adapted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Clinical Outcome Forecasts
CREATE TABLE IF NOT EXISTS clinical_outcome_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL,
    user_id UUID,
    nutrient VARCHAR(50) NOT NULL,
    horizon_days INT NOT NULL, -- 30, 60, 90
    baseline_level NUMERIC(8, 2) NOT NULL,
    predicted_level NUMERIC(8, 2) NOT NULL,
    lower_bound_95 NUMERIC(8, 2) NOT NULL,
    upper_bound_95 NUMERIC(8, 2) NOT NULL,
    normalization_probability NUMERIC(5, 4) NOT NULL,
    recovery_velocity_tier VARCHAR(20) NOT NULL,
    forecast_model VARCHAR(50) NOT NULL DEFAULT 'PHARMACOKINETIC_BAYESIAN',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_p13_forecast_assessment ON clinical_outcome_forecasts(assessment_id);

-- 7. Recommendation Feedback Events
CREATE TABLE IF NOT EXISTS recommendation_feedback_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    recommendation_id VARCHAR(100) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- FOOD, MEAL, SUPPLEMENT, LIFESTYLE
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    taste_score INT CHECK (taste_score >= 1 AND taste_score <= 5),
    preparation_ease_score INT CHECK (preparation_ease_score >= 1 AND preparation_ease_score <= 5),
    reported_side_effects JSONB DEFAULT '[]'::jsonb,
    adhered BOOLEAN NOT NULL DEFAULT TRUE,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_p13_feedback_user ON recommendation_feedback_events(user_id);
