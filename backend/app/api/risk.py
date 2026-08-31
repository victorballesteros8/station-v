from fastapi import APIRouter, HTTPException

from backend.app.scoring.risk_service import (
    CountryRiskResult,
    calculate_country_risk_snapshot,
    GlobalRiskResult,
    calculate_global_risk_snapshot,
)

router = APIRouter(
    prefix="/api/risk",
    tags=["risk"],
)


def _result_to_dict(result: CountryRiskResult) -> dict:
    return {
        "country_id": result.country_id,
        "country_risk": result.country_risk,
        "dimensions": {
            "internal_instability": result.internal_instability,
            "conflict_violence": result.conflict_violence,
            "international_tension": result.international_tension,
            "military_activity": result.military_activity,
            "pressure_stress": result.pressure_stress,
        },
        "confidence": result.confidence,
    }

def _global_result_to_dict(result: GlobalRiskResult) -> dict:
    return {
        "global_risk": result.global_risk,
        "tier1_pressure": result.tier1_pressure,
        "tier1_intensity": result.tier1_intensity,
        "tier1_average": result.tier1_average,
        "tier1_breadth": result.tier1_breadth,
        "tier2_pressure": result.tier2_pressure,
        "tier3_pressure": result.tier3_pressure,
        "coverage_global": result.coverage_global,
        "coverage_systemic": result.coverage_systemic,
        "coverage_status": result.coverage_status,
    }

@router.get("/global")
def get_global_risk():
    try:
        result = calculate_global_risk_snapshot()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating global risk: {exc}",
        ) from exc

    return _global_result_to_dict(result)

@router.post("/recalculate/{country_id}")
def recalculate_country_risk(country_id: int):
    try:
        result = calculate_country_risk_snapshot(
            country_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating country risk: {exc}",
        ) from exc

    return _result_to_dict(result)
