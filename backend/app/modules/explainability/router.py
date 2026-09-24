"""
FastAPI Explainability & Risk Factor Analysis Router
Phase 4: Explainable AI and Risk Factor Analysis System

Endpoints:
- GET /api/v1/predictions/{id}/explainability: Multi-nutrient local SHAP attributions, contribution percentages, and clinical reasoning
- GET /api/v1/predictions/{id}/risk-factors: Categorized risk factors across 5 clinical categories with severity ratings
- GET /api/v1/predictions/{id}/explainability/{nutrient_code}: Focused single-nutrient deep dive with waterfall data
- GET /api/v1/predictions/{id}/visualizations/waterfall/{nutrient_code}: Standalone SVG chart or Recharts JSON coordinates
- GET /api/v1/explainability/global: Population-level global feature importance across all 11 target nutrients
"""

from typing import Dict, Any, List, Optional
import uuid
from fastapi import APIRouter, HTTPException, status, Path, Query
from fastapi.responses import Response

from .service import ExplainabilityService
from ...schemas.explainability import (
    MultiNutrientExplainabilityResponse,
    CategorizedRiskFactorsResponse,
    GlobalFeatureImportanceResponse,
    NutrientExplainabilityDetail
)
from ...schemas.phase11_explainability import (
    PredictionExplanationResponse,
    EvidenceSummaryResponse,
    NutrientInteractionsResponse,
    WhatIfSimulationRequest,
    WhatIfSimulationResponse,
    RecommendationRationaleResponse
)

router = APIRouter(prefix="", tags=["Explainable AI & Risk Factor Analysis"])


@router.get(
    "/predictions/{prediction_id}/explainability",
    response_model=MultiNutrientExplainabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Multi-Nutrient Explainability & SHAP Attributions",
    description="Returns positive risk drivers, protective factors, contribution percentages, and dual-layer clinical reasoning."
)
async def get_prediction_explainability(
    prediction_id: uuid.UUID = Path(..., description="Unique assessment or prediction ID"),
    top_k: int = Query(6, ge=1, le=15, description="Number of top positive and protective drivers to retrieve")
):
    try:
        report = ExplainabilityService.get_explainability(
            assessment_id=prediction_id,
            top_k=top_k
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explainability evaluation failed: {str(e)}"
        )


@router.get(
    "/predictions/{prediction_id}/risk-factors",
    response_model=CategorizedRiskFactorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get 5-Category Clinical Risk Factor Breakdown",
    description="Partitions all identified risk factors into Dietary, Lifestyle, Symptom, Medical History, and Supplement categories."
)
async def get_prediction_risk_factors(
    prediction_id: uuid.UUID = Path(..., description="Unique assessment or prediction ID")
):
    try:
        risk_breakdown = ExplainabilityService.get_categorized_risk_factors(
            assessment_id=prediction_id
        )
        return risk_breakdown
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk factor categorization failed: {str(e)}"
        )


@router.get(
    "/predictions/{prediction_id}/explainability/{nutrient_code}",
    response_model=NutrientExplainabilityDetail,
    status_code=status.HTTP_200_OK,
    summary="Get Single Nutrient Explainability Drill-Down",
    description="Provides deep-dive feature attribution, waterfall steps, and clinician notes for a single nutrient (e.g. VITAMIN_D, IRON)."
)
async def get_nutrient_explainability(
    prediction_id: uuid.UUID = Path(..., description="Unique assessment or prediction ID"),
    nutrient_code: str = Path(..., description="Standard nutrient code (e.g., VITAMIN_D, IRON, VITAMIN_B12, CALCIUM)")
):
    try:
        report = ExplainabilityService.get_explainability(
            assessment_id=prediction_id,
            target_nutrient_code=nutrient_code
        )
        if not report.nutrients_explained:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nutrient '{nutrient_code}' not found in prediction record."
            )
        return report.nutrients_explained[0]
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nutrient explainability failed: {str(e)}"
        )


@router.get(
    "/predictions/{prediction_id}/visualizations/waterfall/{nutrient_code}",
    summary="Get Standalone SVG Waterfall Chart or JSON Contract",
    description="Generates server-rendered standalone SVG diagram or JSON coordinate data for frontend Recharts / Chart.js integration."
)
async def get_waterfall_visualization(
    prediction_id: uuid.UUID = Path(..., description="Unique assessment or prediction ID"),
    nutrient_code: str = Path(..., description="Nutrient code (e.g. VITAMIN_D)"),
    format: str = Query("svg", pattern="^(svg|json)$", description="Output format: 'svg' or 'json'")
):
    try:
        chart_result = ExplainabilityService.get_waterfall_chart(
            assessment_id=prediction_id,
            nutrient_code=nutrient_code,
            format=format
        )
        if format.lower() == "svg":
            svg_data = chart_result.get("svg_content", "")
            return Response(content=svg_data, media_type="image/svg+xml")
        else:
            return chart_result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Waterfall rendering failed: {str(e)}"
        )


@router.get(
    "/explainability/global",
    response_model=GlobalFeatureImportanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Global Feature Importance Across Population",
    description="Returns population-wide driver importance rankings and relative contribution percentages across all 11 nutrients."
)
async def get_global_feature_importance(
    nutrient_code: Optional[str] = Query(None, description="Optional filter by nutrient code")
):
    try:
        return ExplainabilityService.get_global_importance(target_nutrient_code=nutrient_code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Global importance query failed: {str(e)}"
        )


# ==============================================================================
# PHASE 11: EXPLAINABLE AI, CLINICAL REASONING & EVIDENCE REST ENDPOINTS
# ==============================================================================

@router.get(
    "/explainability/prediction-explanation",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Multi-Target Prediction Explanation (Phase 11)",
    description="Decomposes clinical predictions into positive vs. protective drivers with dual-layer patient & clinician narratives."
)
async def get_clinical_prediction_explanation(
    prediction_id: Optional[uuid.UUID] = Query(None, description="Assessment or prediction UUID (Required)")
):
    if not prediction_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assessment or prediction ID provided. Cannot generate clinical explanation without a valid assessment."
        )
    try:
        id_str = str(prediction_id)
        payload = ExplainabilityService._active_payload_cache.get(id_str)
        if payload is None:
            from ...core.persistence import PersistenceRepository
            payload = PersistenceRepository.get_assessment(id_str)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment record for ID '{prediction_id}' not found. Cannot generate explanation without clinical intake data."
            )

        return ExplainabilityService.explain_clinical_prediction(
            assessment_payload=payload,
            prediction_id=prediction_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical prediction explanation failed: {str(e)}"
        )


@router.get(
    "/explainability/prediction-explanation/{prediction_id}",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Prediction Explanation by ID (Phase 11)",
    description="Parameterized endpoint fetching dual-layer explainability and positive/protective drivers for an assessment."
)
async def get_clinical_prediction_explanation_by_id(
    prediction_id: uuid.UUID = Path(..., description="Unique assessment or prediction session UUID")
):
    return await get_clinical_prediction_explanation(prediction_id=prediction_id)


@router.get(
    "/explainability/evidence",
    status_code=status.HTTP_200_OK,
    summary="Get Dynamic Clinical Evidence & Scientific Knowledge Base (Phase 5 Remediation)",
    description="Returns patient-grounded scientific evidence, citations, narratives, structured findings, and risk drivers."
)
async def get_dynamic_clinical_evidence(
    target_id: Optional[str] = Query(None, description="Specific target ID (e.g. target_iron_deficiency)"),
    assessment_id: Optional[str] = Query(None, description="Active assessment ID to ground dynamically in patient SHAP attributions (Required)")
):
    if not assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assessment ID provided. Cannot generate clinical evidence without a valid assessment."
        )
    try:
        return ExplainabilityService.get_dynamic_evidence_base(
            target_id=target_id,
            assessment_id=assessment_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate clinical evidence: {str(e)}"
        )


@router.get(
    "/explainability/evidence-summary",
    response_model=EvidenceSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Primary Scientific Citations & Evidence Base (Phase 11)",
    description="Retrieves evidence citations linking predictions and recommendations to NIH ODS, USDA FoodData Central, and NHANES."
)
async def get_clinical_evidence_summary(
    nutrient: Optional[str] = Query(None, description="Filter citations by target nutrient or deficiency name")
):
    try:
        return ExplainabilityService.get_evidence_summary(nutrient=nutrient)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence retrieval failed: {str(e)}"
        )


@router.get(
    "/explainability/nutrient-interactions",
    response_model=NutrientInteractionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Nutrient Interaction Reasoning Catalog (Phase 11)",
    description="Returns synergistic absorptions, competitive antagonisms, and biochemical timing recommendations."
)
async def get_nutrient_interaction_reasoning(
    nutrients: Optional[List[str]] = Query(None, description="List of nutrients to filter interactions for")
):
    try:
        return ExplainabilityService.get_nutrient_interactions(nutrients=nutrients)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nutrient interaction query failed: {str(e)}"
        )


@router.post(
    "/explainability/what-if-simulation",
    response_model=WhatIfSimulationResponse,
    status_code=status.HTTP_200_OK,
    summary="Run What-If Clinical Risk Simulation (Phase 11)",
    description="Simulates prospective dietary, supplement, and lifestyle changes, recomputing calibrated deficiency probabilities."
)
async def run_what_if_simulation(
    request: WhatIfSimulationRequest
):
    try:
        return ExplainabilityService.simulate_what_if(request=request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"What-if simulation failed: {str(e)}"
        )


@router.get(
    "/explainability/recommendation-rationale",
    response_model=RecommendationRationaleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Recommendation Rationale & Evidence Traceability (Phase 11)",
    description="Provides traceable clinical evidence, source citations, and expected outcomes for each food and lifestyle recommendation."
)
async def get_recommendation_rationale(
    prediction_id: Optional[uuid.UUID] = Query(None, description="Optional prediction or assessment UUID")
):
    try:
        return ExplainabilityService.get_recommendation_rationales(assessment_id=prediction_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation rationale query failed: {str(e)}"
        )
