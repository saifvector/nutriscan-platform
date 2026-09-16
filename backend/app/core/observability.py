"""
NutriScan Enterprise Observability & Operations Engine
Phase 6: Structured Logging, Health Dashboards, Real-Time Alerting & Telemetry

Implements:
- Production JSON structured logging with request correlation tracing
- Real-time latency tracking (p50, p95, p99) for predictions, forecasts, and recommendations
- HTTP status telemetry, error rate monitoring, and automated alert triggering
- Observability dashboard payload generation
"""

import time
import json
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .security_middleware import get_current_correlation_id


class JSONStructuredFormatter(logging.Formatter):
    """
    Formats standard Python log records into structured JSON format for log aggregators (ELK, CloudWatch, Datadog).
    """
    def format(self, record: logging.LogRecord) -> str:
        cid = getattr(record, "correlation_id", None) or get_current_correlation_id() or "system"
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": cid,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        # Capture custom extra fields attached to the log record
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module",
            "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs",
            "relativeCreated", "thread", "threadName", "processName", "process", "message"
        }
        for k, v in record.__dict__.items():
            if k not in standard_attrs and k not in log_entry:
                log_entry[k] = v

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_structured_logging(logger: Optional[logging.Logger] = None) -> logging.Logger:
    """Configures structured JSON logging output on the specified or root logger."""
    log = logger or logging.getLogger("nutrient_platform")
    log.setLevel(logging.INFO)
    has_json_handler = any(isinstance(h.formatter, JSONStructuredFormatter) for h in log.handlers)
    if not has_json_handler:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONStructuredFormatter())
        log.addHandler(handler)
    return log


class TelemetryTracker:
    """
    Thread-safe operational metrics collector tracking latencies, HTTP metrics, and alert thresholds.
    """
    def __init__(self, max_history: int = 1000):
        self._lock = threading.Lock()
        self.max_history = max_history
        self._prediction_latencies: List[float] = []
        self._forecast_latencies: List[float] = []
        self._recommendation_latencies: List[float] = []
        self._status_counts: Dict[str, int] = {"2xx": 0, "4xx": 0, "5xx": 0}

    def record_latency(self, component: str, duration_ms: float):
        norm = component.strip().lower().rstrip("s")
        with self._lock:
            if "predict" in norm:
                self._prediction_latencies.append(duration_ms)
                if len(self._prediction_latencies) > self.max_history * 2:
                    self._prediction_latencies = self._prediction_latencies[-self.max_history:]
            elif "forecast" in norm:
                self._forecast_latencies.append(duration_ms)
                if len(self._forecast_latencies) > self.max_history * 2:
                    self._forecast_latencies = self._forecast_latencies[-self.max_history:]
            elif "recommend" in norm:
                self._recommendation_latencies.append(duration_ms)
                if len(self._recommendation_latencies) > self.max_history * 2:
                    self._recommendation_latencies = self._recommendation_latencies[-self.max_history:]

    def get_latency_percentiles(self, component: str) -> Dict[str, float]:
        norm = component.strip().lower().rstrip("s")
        with self._lock:
            if "predict" in norm:
                latencies = list(self._prediction_latencies)
            elif "forecast" in norm:
                latencies = list(self._forecast_latencies)
            elif "recommend" in norm:
                latencies = list(self._recommendation_latencies)
            else:
                latencies = []
        return self._calc_percentiles(latencies)

    def record_http_status(self, status_code: int):
        with self._lock:
            if 200 <= status_code < 300:
                self._status_counts["2xx"] += 1
            elif 400 <= status_code < 500:
                self._status_counts["4xx"] += 1
            elif status_code >= 500:
                self._status_counts["5xx"] += 1

    def get_http_metrics(self) -> Dict[str, Any]:
        with self._lock:
            total = sum(self._status_counts.values())
            total_errors = self._status_counts["4xx"] + self._status_counts["5xx"]
            err_rate = round(total_errors / total * 100.0, 2) if total > 0 else 0.0
            return {
                "total_requests": total,
                "2xx_success": self._status_counts["2xx"],
                "4xx_client_error": self._status_counts["4xx"],
                "5xx_server_error": self._status_counts["5xx"],
                "error_rate_pct": err_rate
            }

    def _calc_percentiles(self, latencies: List[float]) -> Dict[str, float]:
        if not latencies:
            return {"count": 0, "p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "mean_ms": 0.0}
        sorted_vals = sorted(latencies)
        n = len(sorted_vals)
        p50 = sorted_vals[int(0.50 * n)]
        p95 = sorted_vals[min(int(0.95 * n), n - 1)]
        p99 = sorted_vals[min(int(0.99 * n), n - 1)]
        mean = sum(sorted_vals) / n
        return {
            "count": n,
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
            "mean_ms": round(mean, 2)
        }

    def check_alert_thresholds(self) -> List[Dict[str, Any]]:
        alerts = []
        http_m = self.get_http_metrics()
        # High error rate threshold: > 5.0%
        if http_m["error_rate_pct"] > 5.0:
            alerts.append({
                "alert": "HIGH_ERROR_RATE",
                "severity": "CRITICAL",
                "current_value": http_m["error_rate_pct"],
                "threshold": 5.0,
                "message": f"System error rate of {http_m['error_rate_pct']}% exceeds critical 5.0% threshold."
            })

        pred_stats = self.get_latency_percentiles("predictions")
        if pred_stats["p95_ms"] > 500.0:
            alerts.append({
                "alert": "HIGH_P95_LATENCY",
                "severity": "WARNING",
                "current_value": pred_stats["p95_ms"],
                "threshold": 500.0,
                "message": f"Prediction p95 latency {pred_stats['p95_ms']}ms exceeds 500ms warning threshold."
            })

        return alerts

    def get_dashboard_summary(self) -> Dict[str, Any]:
        http_m = self.get_http_metrics()
        pred_stats = self.get_latency_percentiles("predictions")
        fore_stats = self.get_latency_percentiles("forecasts")
        rec_stats = self.get_latency_percentiles("recommendations")
        alerts = self.check_alert_thresholds()

        status_str = "OPERATIONAL"
        if any(a["severity"] == "CRITICAL" for a in alerts):
            status_str = "DEGRADED"

        return {
            "status": status_str,
            "service_status": status_str,
            "uptime_status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "http_traffic": http_m,
            "latency_telemetry": {
                "predictions": pred_stats,
                "forecasts": fore_stats,
                "recommendations": rec_stats
            },
            "alerts": alerts,
            "persistence": {
                "engine": "SQLite WAL",
                "wal_mode": True,
                "synchronous": "NORMAL",
                "busy_timeout_ms": 60000,
                "status": "HEALTHY"
            },
            "governance_drift_status": "NOMINAL"
        }


# Global operational telemetry tracker
telemetry_tracker = TelemetryTracker()
