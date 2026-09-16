"""
Probability Calibration Engine & Diagnostic Metrics (Platt Scaling & ECE).
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve

class PlattCalibrator:
    """
    Platt Scaling (Logistic Sigmoid Calibration) for classifier probability scores.
    Fits a 1D logistic regression on validation set probabilities to align
    confidence scores with empirical frequency.
    """
    def __init__(self, random_state: int = 42):
        self.calibrator = LogisticRegression(
            solver='lbfgs',
            max_iter=300,
            random_state=random_state
        )
        self.is_fitted = False

    def fit(self, val_probs: np.ndarray, y_val: np.ndarray):
        """Fit sigmoid calibrator on validation probabilities."""
        val_probs_2d = np.clip(val_probs, 1e-7, 1 - 1e-7).reshape(-1, 1)
        self.calibrator.fit(val_probs_2d, y_val)
        self.is_fitted = True
        return self

    def predict_proba(self, probs: np.ndarray) -> np.ndarray:
        """Predict calibrated probabilities."""
        if not self.is_fitted:
            return probs
        probs_2d = np.clip(probs, 1e-7, 1 - 1e-7).reshape(-1, 1)
        calibrated_probs = self.calibrator.predict_proba(probs_2d)[:, 1]
        return np.clip(calibrated_probs, 0.0, 1.0)


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """
    Compute Expected Calibration Error (ECE) across n_bins.
    ECE = sum_{b=1}^B (|acc(B_b) - conf(B_b)| * (|B_b| / N))
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total_samples = len(y_true)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (y_prob >= bin_lower) & (y_prob < bin_upper if i < n_bins - 1 else y_prob <= bin_upper)
        bin_count = in_bin.sum()
        if bin_count > 0:
            accuracy_in_bin = y_true[in_bin].mean()
            avg_confidence_in_bin = y_prob[in_bin].mean()
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * (bin_count / total_samples)

    return float(ece)


def evaluate_calibration(y_true: np.ndarray, raw_probs: np.ndarray, cal_probs: np.ndarray, n_bins: int = 10):
    """
    Compute comprehensive calibration metrics comparing raw vs calibrated probabilities.
    """
    raw_brier = float(brier_score_loss(y_true, raw_probs))
    cal_brier = float(brier_score_loss(y_true, cal_probs))
    raw_ece = compute_ece(y_true, raw_probs, n_bins=n_bins)
    cal_ece = compute_ece(y_true, cal_probs, n_bins=n_bins)

    prob_true_raw, prob_pred_raw = calibration_curve(y_true, raw_probs, n_bins=min(5, n_bins))
    prob_true_cal, prob_pred_cal = calibration_curve(y_true, cal_probs, n_bins=min(5, n_bins))

    return {
        'brier_score_raw': raw_brier,
        'brier_score_calibrated': cal_brier,
        'brier_improvement_pct': ((raw_brier - cal_brier) / raw_brier * 100) if raw_brier > 0 else 0.0,
        'ece_raw': raw_ece,
        'ece_calibrated': cal_ece,
        'ece_reduction_pct': ((raw_ece - cal_ece) / raw_ece * 100) if raw_ece > 0 else 0.0,
        'curve_raw': {'prob_true': prob_true_raw.tolist(), 'prob_pred': prob_pred_raw.tolist()},
        'curve_calibrated': {'prob_true': prob_true_cal.tolist(), 'prob_pred': prob_pred_cal.tolist()}
    }
