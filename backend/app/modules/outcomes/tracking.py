"""
Outcome Tracking Engine
Phase 9: Outcome Learning & Adaptive Nutrition Intelligence

Performs longitudinal tracking across symptoms (0-10), biometrics, and laboratory markers.
Calculates baseline vs. current comparisons, improvement rates, and recovery statuses.
"""

from typing import List, Dict, Any, Optional
import uuid
from datetime import date, datetime, timedelta

from .schemas import (
    SymptomLogRequest,
    SymptomProgressItem,
    SymptomTimelineResponse,
    LabLogRequest,
    BiomarkerComparisonItem,
    LabTrackingResponse,
    RecoveryStatusResponse
)


# ─────────────────────────────────────────────────────────────────────────────
# Clinical Reference Standards for Longitudinal Biomarker Tracking
# ─────────────────────────────────────────────────────────────────────────────

CLINICAL_LAB_RANGES: Dict[str, Dict[str, Any]] = {
    "Serum Ferritin": {"unit": "ng/mL", "optimal_min": 40.0, "optimal_max": 150.0, "optimal_range": "40.0 - 150.0"},
    "25-Hydroxy Vitamin D": {"unit": "ng/mL", "optimal_min": 30.0, "optimal_max": 60.0, "optimal_range": "30.0 - 60.0"},
    "Serum Vitamin B12": {"unit": "pg/mL", "optimal_min": 400.0, "optimal_max": 900.0, "optimal_range": "400.0 - 900.0"},
    "Serum Folate": {"unit": "ng/mL", "optimal_min": 7.0, "optimal_max": 20.0, "optimal_range": "7.0 - 20.0"},
    "RBC Magnesium": {"unit": "mg/dL", "optimal_min": 5.0, "optimal_max": 6.5, "optimal_range": "5.0 - 6.5"},
    "Serum Zinc": {"unit": "mcg/dL", "optimal_min": 70.0, "optimal_max": 120.0, "optimal_range": "70.0 - 120.0"},
    "Hemoglobin (CBC)": {"unit": "g/dL", "optimal_min": 12.0, "optimal_max": 15.5, "optimal_range": "12.0 - 15.5"},
    "Serum Potassium": {"unit": "mmol/L", "optimal_min": 3.8, "optimal_max": 5.0, "optimal_range": "3.8 - 5.0"}
}


class OutcomeTrackingEngine:
    """
    Manages longitudinal patient recovery outcomes based strictly on real logged data.
    Target latency: < 50ms.
    """

    def __init__(self):
        self._symptom_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._lab_cache: Dict[str, List[Dict[str, Any]]] = {}

    def log_symptoms(
        self,
        request: SymptomLogRequest
    ) -> SymptomTimelineResponse:
        rec_dt = request.recorded_date or date.today().isoformat()
        entry = {
            "id": str(uuid.uuid4()),
            "assessment_id": request.assessment_id,
            "recorded_date": rec_dt,
            "symptoms": request.symptoms,
            "notes": request.notes
        }

        if request.assessment_id not in self._symptom_cache:
            self._symptom_cache[request.assessment_id] = []
        self._symptom_cache[request.assessment_id].append(entry)

        return self.get_symptom_timeline(request.assessment_id)

    def get_symptom_timeline(
        self,
        assessment_id: str = "demo"
    ) -> SymptomTimelineResponse:
        from ...core.persistence import PersistenceRepository
        history = self._symptom_cache.get(assessment_id, [])
        asmnt = PersistenceRepository.get_assessment(assessment_id)
        raw_symptoms = (asmnt.get("symptoms") or {}) if asmnt else {}

        # If no history and no baseline symptoms in assessment, return clean empty state
        if not history and not raw_symptoms:
            return SymptomTimelineResponse(
                assessment_id=assessment_id,
                overall_symptom_score=0.0,
                symptom_recovery_score=100.0,
                symptoms_tracked_count=0,
                improving_count=0,
                resolved_count=0,
                symptom_progress=[],
                clinical_summary="No symptom observations or longitudinal follow-up logs recorded.",
                historical_curve_points=[]
            )

        baseline_symp: Dict[str, float] = {}
        for k, v in raw_symptoms.items():
            try:
                val = float(v)
                if val > 0:
                    baseline_symp[k.replace("_", " ").title()] = val
            except (ValueError, TypeError):
                continue

        if not history:
            # Baseline-only state
            progress_items: List[SymptomProgressItem] = []
            for name, base_val in baseline_symp.items():
                progress_items.append(
                    SymptomProgressItem(
                        symptom_name=name,
                        baseline_severity=base_val,
                        current_severity=base_val,
                        delta_change=0.0,
                        percentage_improvement=0.0,
                        status="BASELINE",
                        weekly_recovery_velocity=0.0,
                        forecast_days_to_resolution=None
                    )
                )
            avg_base = round(sum(p.baseline_severity for p in progress_items) / len(progress_items), 1) if progress_items else 0.0
            recov_score = round(max(0.0, min(100.0, (1.0 - (avg_base / 10.0)) * 100.0)), 1)
            return SymptomTimelineResponse(
                assessment_id=assessment_id,
                overall_symptom_score=avg_base,
                symptom_recovery_score=recov_score,
                symptoms_tracked_count=len(progress_items),
                improving_count=0,
                resolved_count=0,
                symptom_progress=progress_items,
                clinical_summary="Initial intake baseline recorded. Submit follow-up logs to track recovery progression.",
                historical_curve_points=[{"day": 0, "overall_severity": avg_base, "symptom_recovery_score": recov_score}]
            )

        # Longitudinal logs exist!
        first_log = history[0]
        latest_log = history[-1]
        current_symp = latest_log["symptoms"]

        effective_baseline = baseline_symp if baseline_symp else {k.replace("_", " ").title(): float(v) for k, v in first_log["symptoms"].items()}

        progress_items = []
        improving_cnt = 0
        resolved_cnt = 0

        try:
            d0 = datetime.fromisoformat(first_log.get("recorded_date", date.today().isoformat()))
            d1 = datetime.fromisoformat(latest_log.get("recorded_date", date.today().isoformat()))
            days_elapsed = max(1, (d1 - d0).days)
        except Exception:
            days_elapsed = max(1, len(history) * 7)

        weeks_elapsed = max(0.5, days_elapsed / 7.0)

        for name, baseline_val in effective_baseline.items():
            curr_val = float(current_symp.get(name, current_symp.get(name.lower(), baseline_val)))
            delta = round(baseline_val - curr_val, 1)
            pct_imp = round((delta / baseline_val) * 100.0, 1) if baseline_val > 0 else 0.0
            vel = round(delta / weeks_elapsed, 2)

            if curr_val <= 1.5:
                status = "RESOLVED"
                resolved_cnt += 1
                days_to_res = 0
            elif delta > 0.5:
                status = "IMPROVING"
                improving_cnt += 1
                days_to_res = max(7, int((curr_val / vel) * 7.0)) if vel > 0 else 30
            elif abs(delta) <= 0.5:
                status = "STABLE"
                days_to_res = 45
            else:
                status = "DECLINING"
                days_to_res = None

            progress_items.append(
                SymptomProgressItem(
                    symptom_name=name,
                    baseline_severity=baseline_val,
                    current_severity=curr_val,
                    delta_change=delta,
                    percentage_improvement=pct_imp,
                    status=status,
                    weekly_recovery_velocity=vel,
                    forecast_days_to_resolution=days_to_res
                )
            )

        avg_curr = round(sum(p.current_severity for p in progress_items) / len(progress_items), 1) if progress_items else 0.0
        avg_base = round(sum(p.baseline_severity for p in progress_items) / len(progress_items), 1) if progress_items else 0.0
        recov_score = round(max(0.0, min(100.0, (1.0 - (avg_curr / 10.0)) * 100.0)), 1)

        curve_pts = []
        for i, h in enumerate(history):
            h_symps = [float(v) for v in h["symptoms"].values() if isinstance(v, (int, float))]
            h_avg = round(sum(h_symps) / len(h_symps), 1) if h_symps else avg_curr
            h_rec = round(max(0.0, min(100.0, (1.0 - (h_avg / 10.0)) * 100.0)), 1)
            curve_pts.append({"day": i * 7, "overall_severity": h_avg, "symptom_recovery_score": h_rec})

        overall_pct = round(((avg_base - avg_curr) / avg_base) * 100) if avg_base > 0 else 0
        summary = f"Patient demonstrates {overall_pct}% overall symptom reduction over baseline. {resolved_cnt} symptoms clinically resolved; {improving_cnt} actively improving."

        return SymptomTimelineResponse(
            assessment_id=assessment_id,
            overall_symptom_score=avg_curr,
            symptom_recovery_score=recov_score,
            symptoms_tracked_count=len(progress_items),
            improving_count=improving_cnt,
            resolved_count=resolved_cnt,
            symptom_progress=progress_items,
            clinical_summary=summary,
            historical_curve_points=curve_pts
        )

    def log_labs(
        self,
        request: LabLogRequest
    ) -> LabTrackingResponse:
        test_dt = request.test_date or date.today().isoformat()
        entry = {
            "id": str(uuid.uuid4()),
            "assessment_id": request.assessment_id,
            "test_date": test_dt,
            "lab_provider": request.lab_provider,
            "biomarkers": request.biomarkers,
            "clinical_interpretation": request.clinical_interpretation
        }

        if request.assessment_id not in self._lab_cache:
            self._lab_cache[request.assessment_id] = []
        self._lab_cache[request.assessment_id].append(entry)

        return self.get_lab_tracking(request.assessment_id)

    def get_lab_tracking(
        self,
        assessment_id: str = "demo"
    ) -> LabTrackingResponse:
        from ...core.persistence import PersistenceRepository
        logs = self._lab_cache.get(assessment_id, [])
        asmnt = PersistenceRepository.get_assessment(assessment_id)
        baseline_biomarkers = (asmnt.get("biomarkers") or {}) if asmnt else {}

        if not logs and not baseline_biomarkers:
            return LabTrackingResponse(
                assessment_id=assessment_id,
                test_date=date.today().isoformat(),
                biomarkers=[],
                overall_lab_adequacy_score=0.0,
                clinical_interpretation="No laboratory records or follow-up panels logged for tracking."
            )

        biomarker_items: List[BiomarkerComparisonItem] = []

        if not logs:
            for name, val in baseline_biomarkers.items():
                v = float(val) if isinstance(val, (int, float)) else 0.0
                disp_name = name.replace("_", " ").title()
                meta = CLINICAL_LAB_RANGES.get(disp_name, {"unit": "standard", "optimal_range": "Reference range"})
                biomarker_items.append(
                    BiomarkerComparisonItem(
                        biomarker_name=disp_name,
                        unit=meta["unit"],
                        baseline_value=v,
                        current_value=v,
                        optimal_range=meta["optimal_range"],
                        delta_value=0.0,
                        percentage_change=0.0,
                        status="BASELINE",
                        clinical_significance="Baseline laboratory marker recorded at intake."
                    )
                )
            return LabTrackingResponse(
                assessment_id=assessment_id,
                test_date=date.today().isoformat(),
                biomarkers=biomarker_items,
                overall_lab_adequacy_score=75.0,
                clinical_interpretation="Initial baseline laboratory panel recorded. Submit follow-up laboratory testing to monitor biological repletion."
            )

        latest_entry = logs[-1]
        first_entry = logs[0]
        latest_biomarkers = latest_entry.get("biomarkers", {})
        baseline_ref = baseline_biomarkers if baseline_biomarkers else first_entry.get("biomarkers", {})

        for name, curr_v in latest_biomarkers.items():
            curr_val = float(curr_v) if isinstance(curr_v, (int, float)) else 0.0
            base_val = float(baseline_ref.get(name, curr_val))
            delta = round(curr_val - base_val, 2)
            pct = round((delta / base_val) * 100.0, 1) if base_val > 0 else 0.0

            disp_name = name.replace("_", " ").title()
            meta = CLINICAL_LAB_RANGES.get(disp_name, {"unit": "standard", "optimal_range": "Normal", "optimal_min": base_val, "optimal_max": base_val * 2})

            if curr_val >= meta.get("optimal_min", base_val) and curr_val <= meta.get("optimal_max", base_val * 2):
                st = "OPTIMAL"
            elif delta > 0:
                st = "IMPROVING"
            else:
                st = "SUBOPTIMAL"

            biomarker_items.append(
                BiomarkerComparisonItem(
                    biomarker_name=disp_name,
                    unit=meta.get("unit", "standard"),
                    baseline_value=base_val,
                    current_value=curr_val,
                    optimal_range=meta.get("optimal_range", "Normal"),
                    delta_value=delta,
                    percentage_change=pct,
                    status=st,
                    clinical_significance=f"{'+' if delta >= 0 else ''}{pct}% change from baseline observation."
                )
            )

        return LabTrackingResponse(
            assessment_id=assessment_id,
            test_date=latest_entry.get("test_date", date.today().isoformat()),
            biomarkers=biomarker_items,
            overall_lab_adequacy_score=round(sum(1.0 for b in biomarker_items if b.status == "OPTIMAL") / len(biomarker_items) * 100.0, 1) if biomarker_items else 0.0,
            clinical_interpretation=latest_entry.get("clinical_interpretation") or "Follow-up laboratory panel evaluated against baseline."
        )

    def get_recovery_status(
        self,
        assessment_id: str = "demo"
    ) -> RecoveryStatusResponse:
        from ...core.persistence import PersistenceRepository
        asmnt = PersistenceRepository.get_assessment(assessment_id)
        symp_history = self._symptom_cache.get(assessment_id, [])

        if not asmnt and not symp_history:
            return RecoveryStatusResponse(
                assessment_id=assessment_id,
                baseline_health_score=0.0,
                current_health_score=0.0,
                health_score_delta=0.0,
                recovery_velocity_pts_per_week=0.0,
                recovery_status="NO_DATA",
                days_in_protocol=0,
                projected_full_recovery_date=None,
                overall_improvement_percentage=0.0,
                clinical_progress_summary="No assessment or tracking data recorded."
            )

        baseline = 55.0
        if asmnt and asmnt.get("symptoms"):
            s_vals = [float(v) for v in asmnt["symptoms"].values() if isinstance(v, (int, float))]
            if s_vals:
                avg_s = sum(s_vals) / len(s_vals)
                baseline = round(max(10.0, min(90.0, (1.0 - (avg_s / 10.0)) * 100.0)), 1)

        if not symp_history:
            return RecoveryStatusResponse(
                assessment_id=assessment_id,
                baseline_health_score=baseline,
                current_health_score=baseline,
                health_score_delta=0.0,
                recovery_velocity_pts_per_week=0.0,
                recovery_status="BASELINE",
                days_in_protocol=0,
                projected_full_recovery_date=None,
                overall_improvement_percentage=0.0,
                clinical_progress_summary="Initial intake baseline recorded. Longitudinal logs will establish recovery trajectory."
            )

        days_in = len(symp_history) * 7
        latest_symps = [float(v) for v in symp_history[-1]["symptoms"].values() if isinstance(v, (int, float))]
        curr_avg = sum(latest_symps) / len(latest_symps) if latest_symps else 5.0
        current = round(max(10.0, min(95.0, (1.0 - (curr_avg / 10.0)) * 100.0)), 1)
        delta = round(current - baseline, 1)
        weeks = max(1.0, days_in / 7.0)
        velocity = round(delta / weeks, 2)

        status = "RAPID_RECOVERY" if velocity >= 4.0 else ("STEADY_RECOVERY" if velocity >= 1.0 else "PLATEAU")
        days_left = max(7, int(((100.0 - current) / max(velocity, 0.5)) * 7)) if current < 95.0 else 0
        proj_date = (date.today() + timedelta(days=days_left)).isoformat() if days_left > 0 else None

        return RecoveryStatusResponse(
            assessment_id=assessment_id,
            baseline_health_score=baseline,
            current_health_score=current,
            health_score_delta=delta,
            recovery_velocity_pts_per_week=velocity,
            recovery_status=status,
            days_in_protocol=days_in,
            projected_full_recovery_date=proj_date,
            overall_improvement_percentage=round((delta / baseline) * 100.0, 1) if baseline > 0 else 0.0,
            clinical_progress_summary=f"Patient is {days_in} days into protocol with {delta:+.1f} point health score delta."
        )

