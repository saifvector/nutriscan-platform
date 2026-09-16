-- ============================================================================
-- Sample Seed Data for Nutrient Deficiency Platform
-- ============================================================================

-- Insert sample admin & user
INSERT INTO users (id, email, password_hash, role, is_active, is_verified)
VALUES 
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'dr.smith@nutritionai.com', '$2b$12$e8Yx9H1k6kKxW9r8y4kH.OjU4Yp7gYm7Y8Xp9gq4k7k6k7k6k7k6k', 'CLINICIAN', TRUE, TRUE),
    ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'john.doe@example.com', '$2b$12$e8Yx9H1k6kKxW9r8y4kH.OjU4Yp7gYm7Y8Xp9gq4k7k6k7k6k7k6k', 'USER', TRUE, TRUE);

-- Insert profile for john.doe
INSERT INTO user_profiles (id, user_id, first_name, last_name, date_of_birth, gender, height_cm, weight_kg, blood_group)
VALUES 
    ('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380c33', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22', 'John', 'Doe', '1995-06-15', 'MALE', 178.0, 74.5, 'O+');

-- Insert sample health assessment
INSERT INTO health_assessments (
    id, user_id, assessment_version, age_at_assessment, height_cm, weight_kg, bmi,
    dietary_pattern, meals_per_day, water_intake_liters, daily_fruit_vegetable_servings, junk_food_frequency, dietary_restrictions,
    activity_level, sleep_hours_per_night, smoking_status, alcohol_consumption, sunlight_exposure_min_per_day, stress_level,
    symptoms, medical_history, supplement_usage
) VALUES (
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
    'v1.0',
    31,
    178.0,
    74.5,
    23.5,
    'VEGAN',
    3,
    2.5,
    4,
    'RARELY',
    '["dairy-free", "egg-free", "meat-free"]'::jsonb,
    'MODERATELY_ACTIVE',
    6.5,
    'NEVER',
    'OCCASIONAL',
    10,
    7,
    '{"chronic_fatigue": 8, "brittle_nails": 6, "cold_hands_feet": 7, "brain_fog": 5}'::jsonb,
    '["Mild Acid Reflux"]'::jsonb,
    '[]'::jsonb
);

-- Insert ML predictions for the assessment
INSERT INTO nutrient_predictions (
    id, assessment_id, nutrient_code, nutrient_name, probability_score, predicted_risk_level, confidence_interval_low, confidence_interval_high, model_name, model_version, inference_latency_ms
) VALUES 
(
    'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e55',
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
    'VITAMIN_B12',
    'Vitamin B12 (Cobalamin)',
    0.8850,
    'HIGH',
    0.8210,
    0.9320,
    'ensemble_gradient_boost_v1',
    'v1.2.0',
    42
),
(
    'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f66',
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
    'VITAMIN_D',
    'Vitamin D3 (Cholecalciferol)',
    0.7920,
    'HIGH',
    0.7300,
    0.8450,
    'ensemble_gradient_boost_v1',
    'v1.2.0',
    38
),
(
    'a6eebc99-9c0b-4ef8-bb6d-6bb9bd380a77',
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
    'IRON',
    'Iron (Ferritin marker)',
    0.6400,
    'MODERATE',
    0.5700,
    0.7100,
    'ensemble_gradient_boost_v1',
    'v1.2.0',
    40
),
(
    'b7eebc99-9c0b-4ef8-bb6d-6bb9bd380b88',
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
    'POTASSIUM',
    'Potassium (Serum K marker)',
    0.5800,
    'MODERATE',
    0.5100,
    0.6500,
    'ensemble_gradient_boost_v1',
    'v1.2.0',
    35
),
(
    'c8eebc99-9c0b-4ef8-bb6d-6bb9bd380c99',
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
    'IODINE',
    'Iodine (Urinary excretion marker)',
    0.7100,
    'HIGH',
    0.6300,
    0.7900,
    'ensemble_gradient_boost_v1',
    'v1.2.0',
    37
);

-- Insert Risk Factors (SHAP feature attribution)
INSERT INTO risk_factors (id, prediction_id, factor_category, factor_name, factor_description, impact_score, impact_magnitude, evidence_reference)
VALUES
(
    gen_random_uuid(),
    'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e55',
    'DIET',
    'Strict Vegan Diet without Supplementation',
    'Dietary B12 is almost exclusively found in animal products or fortified foods. No B12 supplement logged.',
    0.4850,
    'HIGH',
    'NIH Dietary Supplement Fact Sheet: Vitamin B12'
),
(
    gen_random_uuid(),
    'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e55',
    'SYMPTOM',
    'Severe Chronic Fatigue & Brain Fog',
    'High reported fatigue (8/10) and cognitive brain fog correlate strongly with megaloblastic anemia precursors.',
    0.3200,
    'HIGH',
    'WHO Nutritional Anemias Technical Report'
),
(
    gen_random_uuid(),
    'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f66',
    'LIFESTYLE',
    'Sub-Optimal Sunlight Exposure',
    'Reported 10 minutes/day sunlight exposure is insufficient for cutaneous synthesis of cholecalciferol.',
    0.5120,
    'HIGH',
    'Endocrine Society Clinical Practice Guidelines on Vitamin D'
);

-- Insert Food Recommendations
INSERT INTO food_recommendations (id, prediction_id, food_name, food_group, serving_size, nutrient_density_mg, unit, dietary_compatibility, preparation_tips)
VALUES
(
    gen_random_uuid(),
    'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e55',
    'Fortified Nutritional Yeast',
    'FORTIFIED_FOODS',
    '2 tablespoons (16g)',
    0.024,
    'mg',
    'VEGAN',
    'Sprinkle over salads, roasted vegetables, or popcorn for a cheesy flavor and ~1000% daily B12 value.'
),
(
    gen_random_uuid(),
    'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e55',
    'Fortified Plant Milk (Soy / Almond)',
    'DAIRY_ALTERNATIVES',
    '1 cup (240ml)',
    0.003,
    'mg',
    'VEGAN',
    'Check nutrition label to ensure cyanocobalamin fortification.'
),
(
    gen_random_uuid(),
    'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f66',
    'UV-Exposed Cremini or Maitake Mushrooms',
    'VEGETABLES',
    '100g',
    0.028,
    'mg',
    'VEGAN',
    'Sauté lightly with olive oil. Ergocalciferol (D2) absorption is fat-soluble.'
),
(
    gen_random_uuid(),
    'b7eebc99-9c0b-4ef8-bb6d-6bb9bd380b88',
    'Baked Russet Potato with Skin',
    'VEGETABLES',
    '1 medium potato (173g)',
    926.0,
    'mg',
    'VEGAN',
    'Consume with skin intact where potassium and prebiotic fiber are concentrated.'
),
(
    gen_random_uuid(),
    'c8eebc99-9c0b-4ef8-bb6d-6bb9bd380c99',
    'Organic Dried Wakame or Nori Seaweed',
    'VEGETABLES',
    '2 sheets nori (5g)',
    0.116,
    'mg',
    'VEGAN',
    'Natural marine iodine source essential for T3/T4 thyroid hormone synthesis.'
);

-- Insert Generated Report
INSERT INTO generated_reports (
    id, user_id, assessment_id, report_title, status, summary_text, overall_health_score, pdf_file_url
) VALUES (
    gen_random_uuid(),
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
    'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
    'Comprehensive Nutritional Screening Report #1042',
    'COMPLETED',
    'Screening indicates elevated probability for Vitamin B12 and Vitamin D3 deficiencies, primarily driven by strict vegan dietary habits without fortified supplement support and limited sunlight exposure.',
    72,
    '/reports/pdf/rep_1042_john_doe.pdf'
);
