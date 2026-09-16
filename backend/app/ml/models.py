"""
Multi-Nutrient Machine Learning Models
Phase 2: Dataset Engineering and Machine Learning Foundation

Implements:
1. Logistic Regression (Multinomial / OvR baseline)
2. Random Forest Classifier
3. XGBoost Classifier
4. CatBoost Classifier
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from .constants import TARGET_NUTRIENTS


class BaseNutrientModel:
    """Abstract interface for multi-nutrient risk prediction."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.models_: Dict[str, Any] = {}
        self.is_fitted: bool = False

    def fit(self, X: pd.DataFrame, Y: pd.DataFrame):
        raise NotImplementedError

    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        raise NotImplementedError

    def predict_proba(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        raise NotImplementedError


class LogisticRegressionNutrientModel(BaseNutrientModel):
    """
    Multinomial Logistic Regression Baseline.
    Fast, interpretable, establishes linear baseline across all 11 nutrients.
    """

    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42):
        super().__init__("Logistic Regression")
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state

    def fit(self, X: pd.DataFrame, Y: pd.DataFrame):
        for nut in TARGET_NUTRIENTS:
            y_nut = Y[f"target_{nut}"]
            clf = LogisticRegression(
                C=self.C,
                max_iter=self.max_iter,
                class_weight="balanced",
                random_state=self.random_state
            )
            clf.fit(X, y_nut)
            self.models_[nut] = clf
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        preds = {}
        for nut in TARGET_NUTRIENTS:
            preds[nut] = self.models_[nut].predict(X)
        return preds

    def predict_proba(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        probs = {}
        for nut in TARGET_NUTRIENTS:
            probs[nut] = self.models_[nut].predict_proba(X)
        return probs


class RandomForestNutrientModel(BaseNutrientModel):
    """
    Random Forest Ensemble.
    Captures non-linear feature thresholding, robust to noise and outliers.
    """

    def __init__(self, n_estimators: int = 150, max_depth: int = 12, random_state: int = 42):
        super().__init__("Random Forest")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

    def fit(self, X: pd.DataFrame, Y: pd.DataFrame):
        for nut in TARGET_NUTRIENTS:
            y_nut = Y[f"target_{nut}"]
            clf = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1
            )
            clf.fit(X, y_nut)
            self.models_[nut] = clf
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        preds = {}
        for nut in TARGET_NUTRIENTS:
            preds[nut] = self.models_[nut].predict(X)
        return preds

    def predict_proba(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        probs = {}
        for nut in TARGET_NUTRIENTS:
            probs[nut] = self.models_[nut].predict_proba(X)
        return probs


class XGBoostNutrientModel(BaseNutrientModel):
    """
    XGBoost Classifier.
    Gradient-boosted decision trees optimized for speed, performance, and SHAP compatibility.
    """

    def __init__(self, n_estimators: int = 150, max_depth: int = 5, learning_rate: float = 0.08, random_state: int = 42):
        super().__init__("XGBoost")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state

    def fit(self, X: pd.DataFrame, Y: pd.DataFrame):
        try:
            import xgboost as xgb
        except ImportError:
            raise ImportError("xgboost is not installed. Install via pip install xgboost.")

        for nut in TARGET_NUTRIENTS:
            y_nut = Y[f"target_{nut}"]
            clf = xgb.XGBClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                objective="multi:softmax",
                num_class=3,
                eval_metric="mlogloss",
                random_state=self.random_state,
                n_jobs=-1
            )
            clf.fit(X, y_nut)
            self.models_[nut] = clf
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        preds = {}
        for nut in TARGET_NUTRIENTS:
            p = self.models_[nut].predict(X)
            if len(p.shape) > 1 and p.shape[1] > 1:
                preds[nut] = np.argmax(p, axis=1).astype(int)
            else:
                preds[nut] = np.squeeze(p).astype(int)
        return preds

    def predict_proba(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        probs = {}
        for nut in TARGET_NUTRIENTS:
            probs[nut] = self.models_[nut].predict_proba(X)
        return probs


class CatBoostNutrientModel(BaseNutrientModel):
    """
    CatBoost Classifier.
    State-of-the-art gradient boosting with native categorical handling and reduced overfitting.
    """

    def __init__(self, iterations: int = 150, depth: int = 6, learning_rate: float = 0.08, random_state: int = 42):
        super().__init__("CatBoost")
        self.iterations = iterations
        self.depth = depth
        self.learning_rate = learning_rate
        self.random_state = random_state

    def fit(self, X: pd.DataFrame, Y: pd.DataFrame):
        try:
            from catboost import CatBoostClassifier
        except ImportError:
            raise ImportError("catboost is not installed. Install via pip install catboost.")

        for nut in TARGET_NUTRIENTS:
            y_nut = Y[f"target_{nut}"]
            clf = CatBoostClassifier(
                iterations=self.iterations,
                depth=self.depth,
                learning_rate=self.learning_rate,
                loss_function="MultiClass",
                verbose=False,
                random_seed=self.random_state,
                thread_count=-1
            )
            clf.fit(X, y_nut)
            self.models_[nut] = clf
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        preds = {}
        for nut in TARGET_NUTRIENTS:
            p = self.models_[nut].predict(X)
            if len(p.shape) > 1 and p.shape[1] > 1:
                preds[nut] = np.argmax(p, axis=1).astype(int)
            else:
                preds[nut] = np.squeeze(p).astype(int)
        return preds

    def predict_proba(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        probs = {}
        for nut in TARGET_NUTRIENTS:
            probs[nut] = self.models_[nut].predict_proba(X)
        return probs


def get_nutrient_model(model_type: str, **kwargs) -> BaseNutrientModel:
    """Factory helper to instantiate nutrient models."""
    normalized = model_type.lower().replace(" ", "").replace("_", "")
    if normalized in ["lr", "logistic", "logisticregression"]:
        return LogisticRegressionNutrientModel(**kwargs)
    elif normalized in ["rf", "randomforest", "randomforestclassifier"]:
        return RandomForestNutrientModel(**kwargs)
    elif normalized in ["xgb", "xgboost", "xgboostclassifier"]:
        return XGBoostNutrientModel(**kwargs)
    elif normalized in ["cat", "catboost", "catboostclassifier"]:
        return CatBoostNutrientModel(**kwargs)
    else:
        raise ValueError(f"Unknown model type: '{model_type}'. Choose from 'lr', 'rf', 'xgb', 'catboost'.")
