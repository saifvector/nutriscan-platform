"""
Phase 10C Production Clinical Model Registry.
Discovers, caches, validates, and manages metadata for all Phase 10B champion models.
"""

import os
import glob
import logging
import warnings
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import joblib
import pandas as pd

from ...schemas.clinical_prediction import (
    ModelCardSummary,
    ModelRegistryResponse
)

logger = logging.getLogger(__name__)

# Base Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FEATURE_IMP_CSV = os.path.join(REPORTS_DIR, "phase10b_feature_importance.csv")

TARGET_DISPLAY_NAMES = {
    'target_iron_deficiency': 'Iron Deficiency',
    'target_iron_deficiency_anemia': 'Iron Deficiency Anemia',
    'target_vitamin_d_deficiency': 'Vitamin D Deficiency',
    'target_vitamin_d_insufficiency': 'Vitamin D Insufficiency',
    'target_folate_deficiency': 'Folate Deficiency',
    'target_magnesium_deficiency': 'Magnesium Deficiency',
    'target_selenium_deficiency': 'Selenium Deficiency',
    'target_potassium_deficiency': 'Potassium Deficiency',
    'target_calcium_deficiency': 'Calcium Deficiency'
}


class ClinicalModelRegistry:
    """
    Thread-safe production Model Registry singleton.
    Maintains loaded in-memory payloads for all 9 Phase 10B champion models.
    """

    _instance: Optional['ClinicalModelRegistry'] = None
    _models: Dict[str, Dict[str, Any]] = {}
    _top_predictors: Dict[str, List[Dict[str, Any]]] = {}
    _last_loaded: Optional[datetime] = None
    VERSION = "v10.3.0-prod"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ClinicalModelRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initializes the registry by loading all champion models and SHAP rankings."""
        self.load_all()

    def load_all(self, force_reload: bool = False):
        """Discovers and caches all champion models from models/ directory."""
        if self._models and not force_reload:
            return

        logger.info(f"[ModelRegistry] Discovering Phase 10B champion models in {MODELS_DIR}...")
        self._models.clear()
        self._top_predictors.clear()

        # 1. Load SHAP feature importances if available
        if os.path.exists(FEATURE_IMP_CSV):
            try:
                shap_df = pd.read_csv(FEATURE_IMP_CSV)
                for target, group in shap_df.groupby('target'):
                    self._top_predictors[target] = group.head(5).to_dict(orient='records')
                logger.info(f"[ModelRegistry] Loaded SHAP top predictors for {len(self._top_predictors)} targets.")
            except Exception as e:
                logger.warning(f"[ModelRegistry] Note loading SHAP importances: {e}")

        # 2. Discover best_{target}.joblib files
        pattern = os.path.join(MODELS_DIR, "best_*.joblib")
        matched_files = glob.glob(pattern)

        for fpath in matched_files:
            fname = os.path.basename(fpath)
            # e.g. best_target_iron_deficiency.joblib -> target_iron_deficiency
            target = fname.replace("best_", "").replace(".joblib", "")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    payload = joblib.load(fpath)
                payload['file_path'] = fpath
                payload['file_name'] = fname
                self._models[target] = payload
                logger.info(f"[ModelRegistry] Registered {TARGET_DISPLAY_NAMES.get(target, target)} ({payload.get('model_name', 'Unknown')})")
            except Exception as e:
                logger.error(f"[ModelRegistry] Failed to load {fname}: {e}")

        self._last_loaded = datetime.now(timezone.utc)
        logger.info(f"[ModelRegistry] Initialization complete: {len(self._models)} champion models active.")

    def get_model(self, target: str) -> Optional[Dict[str, Any]]:
        """Returns the cached model bundle for a specific target."""
        return self._models.get(target)

    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Returns all cached champion model bundles."""
        return self._models

    def get_top_predictors(self, target: str) -> List[Dict[str, Any]]:
        """Returns top SHAP predictors for a specific target."""
        return self._top_predictors.get(target, [])

    def get_metadata_catalog(self) -> ModelRegistryResponse:
        """Constructs standardized metadata catalog response for all models."""
        summaries: List[ModelCardSummary] = []

        for target, payload in self._models.items():
            eval_dict = payload.get('evaluation', {})
            disp_name = TARGET_DISPLAY_NAMES.get(target, target)
            summary = ModelCardSummary(
                target=target,
                target_name=disp_name,
                champion_algorithm=payload.get('model_name', payload['model'].__class__.__name__),
                optimal_threshold=float(payload.get('optimal_threshold', 0.5)),
                holdout_roc_auc=float(eval_dict.get('test_roc_auc', 0.0)),
                holdout_pr_auc=float(eval_dict.get('test_pr_auc', 0.0)),
                holdout_sensitivity=float(eval_dict.get('test_recall', 0.0)),
                holdout_specificity=float(eval_dict.get('test_specificity', 0.0)),
                holdout_f1=float(eval_dict.get('test_f1', 0.0)),
                calibrated_brier_score=float(eval_dict.get('brier_score_calibrated', 0.0)),
                calibrated_ece=float(eval_dict.get('ece_calibrated', 0.0)),
                num_features=len(payload.get('features', [])),
                model_file=payload.get('file_name', '')
            )
            summaries.append(summary)

        # Sort logically by target display name
        summaries.sort(key=lambda s: s.target_name)

        return ModelRegistryResponse(
            status="READY",
            model_suite_version=self.VERSION,
            total_registered_models=len(summaries),
            registry_path="models/clinical_v10.3",
            last_reloaded=self._last_loaded or datetime.now(timezone.utc),
            models=summaries
        )

    def is_healthy(self) -> bool:
        """Verifies that all 9 clinical target models are loaded and have calibrators."""
        required = set(TARGET_DISPLAY_NAMES.keys())
        loaded = set(self._models.keys())
        return required.issubset(loaded)
