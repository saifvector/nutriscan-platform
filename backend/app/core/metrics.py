"""
Prometheus Observability & Telemetry Metrics Engine
Lightweight, pure-Python Prometheus metric collector and exposition engine.
Formats metrics according to Prometheus text exposition format (version 0.0.4).
Zero external dependencies required.
"""

import time
import threading
from typing import Dict, Tuple


class MetricsCollector:
    """Thread-safe Prometheus metric registry and collector."""

    def __init__(self):
        self._lock = threading.Lock()
        
        # Counters: (name, label_tuple) -> count
        self._http_requests_total: Dict[Tuple[str, str, int], int] = {}
        self._predictions_total: Dict[str, int] = {}
        self._copilot_ops_total: Dict[Tuple[str, str], int] = {}
        self._reviews_total: Dict[str, int] = {}
        
        # Histograms: (name, endpoint) -> [sum, count, bucket_counts]
        # Standard Prometheus buckets for web services (in seconds)
        self.latency_buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._http_duration_sum: Dict[Tuple[str, str], float] = {}
        self._http_duration_count: Dict[Tuple[str, str], int] = {}
        self._http_duration_buckets: Dict[Tuple[str, str, float], int] = {}

    def record_request(self, method: str, endpoint: str, status_code: int, duration_seconds: float):
        """Records HTTP request count and latency distribution."""
        with self._lock:
            # Increment request counter
            key = (method.upper(), endpoint, status_code)
            self._http_requests_total[key] = self._http_requests_total.get(key, 0) + 1
            
            # Record latency
            ep_key = (method.upper(), endpoint)
            self._http_duration_sum[ep_key] = self._http_duration_sum.get(ep_key, 0.0) + duration_seconds
            self._http_duration_count[ep_key] = self._http_duration_count.get(ep_key, 0) + 1
            
            for b in self.latency_buckets:
                b_key = (method.upper(), endpoint, b)
                if duration_seconds <= b:
                    self._http_duration_buckets[b_key] = self._http_duration_buckets.get(b_key, 0) + 1

    def record_prediction(self, status: str = "success"):
        with self._lock:
            self._predictions_total[status] = self._predictions_total.get(status, 0) + 1

    def record_copilot_op(self, op_type: str, status: str = "success"):
        with self._lock:
            key = (op_type, status)
            self._copilot_ops_total[key] = self._copilot_ops_total.get(key, 0) + 1

    def record_review(self, decision: str):
        with self._lock:
            self._reviews_total[decision] = self._reviews_total.get(decision, 0) + 1

    def export_prometheus_text(self) -> str:
        """Serializes current in-memory metrics to Prometheus format."""
        lines = []
        
        # 1. HTTP Requests Total
        lines.append("# HELP nutriscan_http_requests_total Total number of HTTP requests processed")
        lines.append("# TYPE nutriscan_http_requests_total counter")
        with self._lock:
            for (method, endpoint, status), count in sorted(self._http_requests_total.items()):
                lines.append(f'nutriscan_http_requests_total{{method="{method}",endpoint="{endpoint}",status="{status}"}} {count}')
                
            # 2. HTTP Request Duration
            lines.append("# HELP nutriscan_http_request_duration_seconds HTTP request duration in seconds")
            lines.append("# TYPE nutriscan_http_request_duration_seconds histogram")
            for (method, endpoint), count in sorted(self._http_duration_count.items()):
                total_sum = self._http_duration_sum.get((method, endpoint), 0.0)
                cum_count = 0
                for b in self.latency_buckets:
                    b_count = self._http_duration_buckets.get((method, endpoint, b), 0)
                    lines.append(f'nutriscan_http_request_duration_seconds_bucket{{method="{method}",endpoint="{endpoint}",le="{b}"}} {b_count}')
                lines.append(f'nutriscan_http_request_duration_seconds_bucket{{method="{method}",endpoint="{endpoint}",le="+Inf"}} {count}')
                lines.append(f'nutriscan_http_request_duration_seconds_sum{{method="{method}",endpoint="{endpoint}"}} {total_sum:.6f}')
                lines.append(f'nutriscan_http_request_duration_seconds_count{{method="{method}",endpoint="{endpoint}"}} {count}')

            # 3. Prediction Requests
            lines.append("# HELP nutriscan_prediction_requests_total Total AI multi-nutrient screening requests")
            lines.append("# TYPE nutriscan_prediction_requests_total counter")
            for status, count in sorted(self._predictions_total.items()):
                lines.append(f'nutriscan_prediction_requests_total{{status="{status}"}} {count}')

            # 4. Clinical Copilot Operations
            lines.append("# HELP nutriscan_copilot_operations_total Total Clinical Copilot generation calls")
            lines.append("# TYPE nutriscan_copilot_operations_total counter")
            for (op_type, status), count in sorted(self._copilot_ops_total.items()):
                lines.append(f'nutriscan_copilot_operations_total{{operation="{op_type}",status="{status}"}} {count}')

            # 5. Clinician Reviews
            lines.append("# HELP nutriscan_clinical_reviews_total Total clinician review sign-offs logged")
            lines.append("# TYPE nutriscan_clinical_reviews_total counter")
            for decision, count in sorted(self._reviews_total.items()):
                lines.append(f'nutriscan_clinical_reviews_total{{decision="{decision}"}} {count}')

        lines.append("")  # trailing newline required by Prometheus spec
        return "\n".join(lines)


# Singleton instance
metrics = MetricsCollector()
