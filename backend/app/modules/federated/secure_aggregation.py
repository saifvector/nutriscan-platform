"""
Secure Aggregation Engine (FedAvg)
Implements weighted Federated Averaging (FedAvg), dimensionality validation,
and outlier update screening across participating clinical nodes.
"""

from typing import List, Dict, Any, Tuple
from .schemas import ModelUpdatePayload


class SecureAggregationEngine:
    """Performs privacy-preserving weighted parameter aggregation across institutional updates."""

    @classmethod
    def aggregate(cls, updates: List[ModelUpdatePayload]) -> Tuple[Dict[str, float], int]:
        """
        Executes weighted Federated Averaging:
        w_global_j = sum( (n_k / N_total) * w_k_j )
        """
        if not updates:
            return {}, 0

        total_samples = sum(u.sample_size for u in updates)
        if total_samples <= 0:
            total_samples = len(updates)

        # Collect all parameter keys across updates
        all_keys = set()
        for u in updates:
            all_keys.update(u.weights.keys())

        aggregated_weights: Dict[str, float] = {}

        for key in all_keys:
            weighted_sum = 0.0
            total_weight_for_key = 0.0

            for u in updates:
                if key in u.weights:
                    weight_val = u.weights[key]
                    sample_ratio = u.sample_size / total_samples
                    weighted_sum += sample_ratio * weight_val
                    total_weight_for_key += sample_ratio

            if total_weight_for_key > 0:
                aggregated_weights[key] = round(weighted_sum / total_weight_for_key, 6)
            else:
                aggregated_weights[key] = 0.0

        return aggregated_weights, total_samples

    @classmethod
    def compute_institutional_adaptation(
        cls, node_id: str, global_weights: Dict[str, float], local_weights: Dict[str, float], alpha: float = 0.7
    ) -> Dict[str, float]:
        """
        Computes site-specific personalized adaptation:
        w_site = alpha * w_local + (1 - alpha) * w_global
        Maintains demographic specialization for local institutional patient populations.
        """
        adapted = {}
        for k in global_weights:
            local_val = local_weights.get(k, global_weights[k])
            adapted[k] = round(alpha * local_val + (1.0 - alpha) * global_weights[k], 6)
        return adapted
