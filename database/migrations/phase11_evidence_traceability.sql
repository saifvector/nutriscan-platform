-- Phase 11: Clinical Recommendation Evidence & Traceability Migration
-- Adds scientific citation references, evidence strength levels, and expected physiological outcomes

ALTER TABLE food_recommendations 
ADD COLUMN IF NOT EXISTS evidence_source VARCHAR(100) DEFAULT 'USDA FoodData Central / NIH ODS',
ADD COLUMN IF NOT EXISTS evidence_strength VARCHAR(20) DEFAULT 'Grade A',
ADD COLUMN IF NOT EXISTS evidence_reference_url TEXT DEFAULT 'https://ods.od.nih.gov/',
ADD COLUMN IF NOT EXISTS triggering_risk_score NUMERIC(5, 2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS expected_outcome TEXT DEFAULT NULL;

-- Index for evidence queries
CREATE INDEX IF NOT EXISTS idx_food_rec_evidence_strength ON food_recommendations(evidence_strength);
CREATE INDEX IF NOT EXISTS idx_food_rec_nutrient ON food_recommendations(nutrient_name);
