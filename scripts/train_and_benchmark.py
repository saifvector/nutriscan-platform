"""
Training, Benchmarking, and Artifact Export CLI Script
Phase 2: Dataset Engineering and Machine Learning Foundation

Runs full benchmark across:
- Logistic Regression
- Random Forest
- XGBoost
- CatBoost (if installed)

Outputs comprehensive metric tables and exports champion model to ml_artifacts/.
"""

import os
import sys
import json
import joblib

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.ml import (
    ModelBenchmarkRunner,
    NutritionalInferenceEngine,
    TARGET_NUTRIENTS
)


def main():
    print("=" * 80)
    print("AI NUTRIENT DEFICIENCY SCREENING - PHASE 2 MACHINE LEARNING BENCHMARK")
    print("=" * 80)

    runner = ModelBenchmarkRunner(test_size=0.2, random_state=42)
    
    # Run comparison on 1,500 synthetic patient records across all 18 nutrients
    comparison_df, detailed_reports, champion_model, pipeline = runner.run_benchmark_comparison(
        n_samples=1500,
        include_catboost=False
    )

    print("\n" + "=" * 80)
    print("MODEL BENCHMARK COMPARISON SUMMARY (18 TARGET NUTRIENTS)")
    print("=" * 80)
    print(comparison_df.to_string(index=False))

    # Save artifacts to ml_artifacts/
    artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "ml_artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    model_path = os.path.join(artifacts_dir, "champion_model.joblib")
    pipeline_path = os.path.join(artifacts_dir, "feature_pipeline.joblib")
    report_path = os.path.join(artifacts_dir, "benchmark_report.json")

    print(f"\nPersisting champion model to: {model_path}")
    joblib.dump(champion_model, model_path)

    print(f"Persisting fitted feature pipeline to: {pipeline_path}")
    joblib.dump(pipeline, pipeline_path)

    # Save metrics report JSON
    with open(report_path, "w") as f:
        json.dump(detailed_reports, f, indent=2)
    print(f"Persisting detailed metrics report to: {report_path}")

    # Step 4: Verification Run using NutritionalInferenceEngine
    print("\n" + "=" * 80)
    print("VERIFICATION: SIMULATED PATIENT SCREENING INFERENCE")
    print("=" * 80)

    sample_patient = {
        "age": 29,
        "gender": "FEMALE",
        "height_cm": 165.0,
        "weight_kg": 54.0,
        "dietary_pattern": "VEGAN",
        "meals_per_day": 2,
        "water_intake_liters": 1.8,
        "daily_fruit_vegetable_servings": 3,
        "food_restrictions": ["dairy_free", "meat_free"],
        "activity_level": "MODERATELY_ACTIVE",
        "sleep_hours_per_night": 6.0,
        "sunlight_exposure_min_per_day": 10,
        "stress_level": 7,
        "smoking_status": "NEVER",
        "alcohol_consumption": "NONE",
        "has_digestive_disorder": False,
        "has_chronic_disease": False,
        "has_prior_deficiency": True,
        "takes_multivitamin": False,
        "takes_vitamin_d": False,
        "takes_iron": False,
        "takes_b12": False,
        "takes_calcium": False,
        "takes_magnesium": False,
        "takes_zinc": False,
        "supplement_duration_months": 0,
        "symptoms": {
            "fatigue": 8,
            "pale_skin": 7,
            "hair_loss": 6,
            "brittle_nails": 6,
            "brain_fog": 5,
            "bone_pain": 3
        }
    }

    engine = NutritionalInferenceEngine(
        model=champion_model,
        pipeline=pipeline,
        model_version="v2.1.0"
    )

    screening_result = engine.screen_patient(sample_patient, compute_explainability=True)
    summary = screening_result["overall_summary"]

    print(f"Overall Nutritional Risk Score: {summary['overall_risk_score']} / 100")
    print(f"Severity Classification:        {summary['overall_severity']}")
    print(f"Active Deficiencies Flagged:    {summary['high_risk_count']} High Risk, {summary['moderate_risk_count']} Moderate Risk")
    print(f"Compounding Interaction Multiplier: {summary['compounding_interaction_multiplier']}x")

    print("\nPriority Nutrient Triage:")
    for nut_eval in screening_result["nutrient_evaluations"][:5]:
        print(f"  #{nut_eval['priority_rank']} {nut_eval['nutrient']}: {nut_eval['risk_level']} (Score: {nut_eval['score']}, Prob: {nut_eval['probability']})")
        if nut_eval["risk_factors"]:
            top_factor = nut_eval["risk_factors"][0]
            print(f"     -> Top Driver: {top_factor['factor_name']} (Impact: {top_factor['impact_score']}, {top_factor['impact_magnitude']})")

    if screening_result["nutrient_interactions"]:
        print("\nActive Biochemical Nutrient Interactions:")
        for inter in screening_result["nutrient_interactions"]:
            print(f"  * {inter['interaction_type']}: {inter['summary']}")
            print(f"    Clinical Guidance: {inter['actionable_guidance']}")

    print("\nBenchmark & Verification run completed successfully!")


if __name__ == "__main__":
    main()
