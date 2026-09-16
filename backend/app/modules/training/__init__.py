"""
Phase 10B Training Module.
Provides training pipelines, model calibration, configuration, and evaluation for clinical nutrient deficiency targets.
"""

from backend.app.modules.training.config import (
    TARGETS,
    TARGET_DISPLAY_NAMES,
    AUDITED_SCALE_POS_WEIGHTS,
    CV_SPLITS,
    RANDOM_STATE,
    MODELS_DIR,
    REPORTS_DIR
)
from backend.app.modules.training.calibration import (
    PlattCalibrator,
    compute_ece,
    evaluate_calibration
)
from backend.app.modules.training.pipeline import ClinicalModelTrainingPipeline

__all__ = [
    "TARGETS",
    "TARGET_DISPLAY_NAMES",
    "AUDITED_SCALE_POS_WEIGHTS",
    "CV_SPLITS",
    "RANDOM_STATE",
    "MODELS_DIR",
    "REPORTS_DIR",
    "PlattCalibrator",
    "compute_ece",
    "evaluate_calibration",
    "ClinicalModelTrainingPipeline"
]
