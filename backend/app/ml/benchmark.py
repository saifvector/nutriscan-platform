"""
Model Benchmarking, Evaluation & Comparison Framework
Phase 2: Dataset Engineering and Machine Learning Foundation

Evaluates:
- Logistic Regression
- Random Forest
- XGBoost
- CatBoost

Metrics:
- Accuracy, Precision (macro & weighted), Recall (macro & weighted), F1-Score (macro & weighted), ROC-AUC (OvR)
- Confusion Matrices across all 11 target nutrients
- Strict train-test split before feature pipeline fitting to eliminate data leakage.
"""

from typing import Dict, Any, List, Tuple
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
import joblib

from .constants import TARGET_NUTRIENTS
from .dataset_generator import NutritionalDatasetGenerator
from .feature_engineering import ClinicalFeaturePipeline
from .models import (
    LogisticRegressionNutrientModel,
    RandomForestNutrientModel,
    XGBoostNutrientModel,
    CatBoostNutrientModel,
    BaseNutrientModel
)


class ModelBenchmarkRunner:
    """
    Executes reproducible model training, multi-metric evaluation,
    cross-model comparison, and artifact persistence.
    """

    def __init__(self, test_size: float = 0.2, random_state: int = 42):
        self.test_size = test_size
        self.random_state = random_state

    def prepare_data(
        self,
        n_samples: int = 3000
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, ClinicalFeaturePipeline]:
        """
        Generates dataset and performs STRICT featurization ordering:
        Splits into train/test BEFORE fitting the feature engineering pipeline.
        """
        generator = NutritionalDatasetGenerator(seed=self.random_state)
        raw_df = generator.generate_dataframe(n_samples=n_samples)

        # Separate feature columns from target columns
        target_cols = [f"target_{nut}" for nut in TARGET_NUTRIENTS]
        feature_cols = [c for c in raw_df.columns if not c.startswith("target_") and not c.startswith("prob_")]

        df_features = raw_df[feature_cols]
        df_targets = raw_df[target_cols]

        # Train/Test split FIRST
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            df_features, df_targets, test_size=self.test_size, random_state=self.random_state
        )

        # Fit feature pipeline strictly on training data
        pipeline = ClinicalFeaturePipeline(scaler_type="robust")
        pipeline.fit(X_train_raw)

        # Transform train and test independently
        X_train = pipeline.transform(X_train_raw)
        X_test = pipeline.transform(X_test_raw)

        return X_train, X_test, y_train, y_test, pipeline

    def evaluate_model(
        self,
        model: BaseNutrientModel,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.DataFrame,
        y_test: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Trains and rigorously evaluates a model across all 11 target nutrients.
        """
        # Time training
        start_train = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_train

        # Time inference
        start_infer = time.time()
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
        inference_time = time.time() - start_infer

        nutrient_metrics = {}
        all_acc, all_f1_macro, all_f1_weighted = [], [], []
        all_prec_macro, all_rec_macro = [], []
        all_roc_auc = []

        for nut in TARGET_NUTRIENTS:
            y_true = y_test[f"target_{nut}"].values
            y_pred = predictions[nut]
            y_prob = probabilities[nut]

            acc = accuracy_score(y_true, y_pred)
            prec_m = precision_score(y_true, y_pred, average="macro", zero_division=0)
            rec_m = recall_score(y_true, y_pred, average="macro", zero_division=0)
            f1_m = f1_score(y_true, y_pred, average="macro", zero_division=0)
            f1_w = f1_score(y_true, y_pred, average="weighted", zero_division=0)
            cm = confusion_matrix(y_true, y_pred).tolist()

            # Multi-class ROC-AUC (OvR)
            try:
                roc_auc = roc_auc_score(y_true, y_prob, multi_class="ovr", average="macro")
            except Exception:
                roc_auc = 0.50

            nutrient_metrics[nut] = {
                "accuracy": round(float(acc), 4),
                "precision_macro": round(float(prec_m), 4),
                "recall_macro": round(float(rec_m), 4),
                "f1_macro": round(float(f1_m), 4),
                "f1_weighted": round(float(f1_w), 4),
                "roc_auc_ovr": round(float(roc_auc), 4),
                "confusion_matrix": cm
            }

            all_acc.append(acc)
            all_f1_macro.append(f1_m)
            all_f1_weighted.append(f1_w)
            all_prec_macro.append(prec_m)
            all_rec_macro.append(rec_m)
            all_roc_auc.append(roc_auc)

        summary = {
            "model_name": model.model_name,
            "mean_accuracy": round(float(np.mean(all_acc)), 4),
            "mean_f1_macro": round(float(np.mean(all_f1_macro)), 4),
            "mean_f1_weighted": round(float(np.mean(all_f1_weighted)), 4),
            "mean_precision_macro": round(float(np.mean(all_prec_macro)), 4),
            "mean_recall_macro": round(float(np.mean(all_rec_macro)), 4),
            "mean_roc_auc": round(float(np.mean(all_roc_auc)), 4),
            "training_time_sec": round(float(train_time), 3),
            "inference_time_sec": round(float(inference_time), 4),
            "per_sample_latency_ms": round((inference_time / len(X_test)) * 1000, 3),
            "per_nutrient_metrics": nutrient_metrics
        }
        return summary

    def run_benchmark_comparison(
        self,
        n_samples: int = 3000,
        include_catboost: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any], BaseNutrientModel, ClinicalFeaturePipeline]:
        """
        Trains and benchmarks all 4 models side-by-side, compiling comparison table.
        """
        print(f"Generating synthetic dataset ({n_samples} samples)...")
        X_train, X_test, y_train, y_test, pipeline = self.prepare_data(n_samples=n_samples)

        candidates = [
            LogisticRegressionNutrientModel(C=1.0, max_iter=1000),
            RandomForestNutrientModel(n_estimators=100, max_depth=10),
            XGBoostNutrientModel(n_estimators=100, max_depth=4, learning_rate=0.08)
        ]

        if include_catboost:
            try:
                import catboost
                candidates.append(CatBoostNutrientModel(iterations=100, depth=5, learning_rate=0.08))
            except ImportError:
                print("CatBoost not installed; omitting from candidate list.")

        results = []
        detailed_reports = {}
        fitted_models = []

        for model in candidates:
            print(f"Training and evaluating: {model.model_name}...")
            report = self.evaluate_model(model, X_train, X_test, y_train, y_test)
            detailed_reports[model.model_name] = report
            fitted_models.append(model)
            
            results.append({
                "Model": model.model_name,
                "Mean Accuracy": f"{report['mean_accuracy']:.4f}",
                "Macro F1": f"{report['mean_f1_macro']:.4f}",
                "Weighted F1": f"{report['mean_f1_weighted']:.4f}",
                "Mean ROC-AUC": f"{report['mean_roc_auc']:.4f}",
                "Train Time (s)": f"{report['training_time_sec']:.2f}",
                "Latency (ms/sample)": f"{report['per_sample_latency_ms']:.2f}"
            })

        comparison_df = pd.DataFrame(results).sort_values(by="Macro F1", ascending=False)
        
        # Select champion model
        best_model_name = comparison_df.iloc[0]["Model"]
        champion_model = next(m for m in fitted_models if m.model_name == best_model_name)
        print(f"Champion Model selected: {best_model_name}")

        return comparison_df, detailed_reports, champion_model, pipeline
