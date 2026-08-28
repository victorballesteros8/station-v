from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp, log
from typing import Iterable


HALF_LIFE_HOURS = 48.0
EVENT_WINDOW_DAYS = 7
EVENT_WINDOW_HOURS = EVENT_WINDOW_DAYS * 24

SUBINDICATOR_EVENT_WEIGHT = 0.35
SUBINDICATOR_PREVIOUS_WEIGHT = 0.65

PRESSURE_SATURATION_K = 3.0

REPETITION_WEIGHTS = {
    1: 1.00,
    2: 0.60,
    3: 0.35,
    4: 0.20,
    5: 0.10,
}


@dataclass(frozen=True)
class RiskImpactInput:
    base_impact: float
    relevance: float
    time_start: datetime
    repetition_count: int = 1


@dataclass(frozen=True)
class RiskImpactResult:
    temporal_weight: float
    repetition_weight: float
    effective_impact: float


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _ensure_utc(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)

    return timestamp.astimezone(timezone.utc)


def calculate_temporal_weight(
    time_start: datetime,
    *,
    reference_time: datetime | None = None,
) -> float:
    """
    Calculates temporal decay using a 48-hour half-life.

    Events older than the seven-day calculation window return 0.
    """

    event_time = _ensure_utc(time_start)

    if reference_time is None:
        reference = datetime.now(timezone.utc)
    else:
        reference = _ensure_utc(reference_time)

    age_hours = (reference - event_time).total_seconds() / 3600

    if age_hours <= 0:
        return 1.0

    if age_hours > EVENT_WINDOW_HOURS:
        return 0.0

    weight = exp(-log(2) * age_hours / HALF_LIFE_HOURS)

    return _clamp(weight, 0.0, 1.0)


def calculate_repetition_weight(repetition_count: int) -> float:
    """
    Returns the repetition weight defined by V1.1.

    1 occurrence  -> 1.00
    2 occurrences -> 0.60
    3 occurrences -> 0.35
    4 occurrences -> 0.20
    5+ occurrences -> 0.10
    """

    if repetition_count <= 1:
        return 1.00

    if repetition_count == 2:
        return 0.60

    if repetition_count == 3:
        return 0.35

    if repetition_count == 4:
        return 0.20

    return 0.10


def calculate_effective_impact(
    base_impact: float,
    relevance: float,
    temporal_weight: float,
    repetition_weight: float,
) -> float:
    """
    I_effective = I_base × R × W_t × W_r
    """

    base = _clamp(base_impact, 0.0, 100.0)
    rel = _clamp(relevance, 0.0, 1.0)
    temporal = _clamp(temporal_weight, 0.0, 1.0)
    repetition = _clamp(repetition_weight, 0.0, 1.0)

    result = base * rel * temporal * repetition

    return _clamp(result, 0.0, 100.0)


def calculate_risk_impact(
    impact: RiskImpactInput,
    *,
    reference_time: datetime | None = None,
) -> RiskImpactResult:
    temporal_weight = calculate_temporal_weight(
        impact.time_start,
        reference_time=reference_time,
    )

    repetition_weight = calculate_repetition_weight(
        impact.repetition_count,
    )

    effective_impact = calculate_effective_impact(
        impact.base_impact,
        impact.relevance,
        temporal_weight,
        repetition_weight,
    )

    return RiskImpactResult(
        temporal_weight=temporal_weight,
        repetition_weight=repetition_weight,
        effective_impact=effective_impact,
    )


def calculate_event_pressure(
    effective_impacts: Iterable[float],
) -> float:
    """
    Aggregates event impacts using a saturating pressure function.

    Pressure = 100 × (1 - exp(-sum(I_effective) / K))
    """

    total_impact = sum(
        max(0.0, min(float(impact), 100.0))
        for impact in effective_impacts
    )

    if total_impact <= 0:
        return 0.0

    pressure = 100.0 * (
        1.0 - exp(-total_impact / PRESSURE_SATURATION_K)
    )

    return _clamp(pressure, 0.0, 100.0)


def calculate_subindicator_score(
    previous_score: float,
    event_pressure: float,
) -> float:
    """
    Subindicator update:

    0.65 × previous state
    +
    0.35 × current event pressure
    """

    previous = _clamp(previous_score, 0.0, 100.0)
    pressure = _clamp(event_pressure, 0.0, 100.0)

    score = (
        previous * SUBINDICATOR_PREVIOUS_WEIGHT
        + pressure * SUBINDICATOR_EVENT_WEIGHT
    )

    return _clamp(score, 0.0, 100.0)


def calculate_dimension_score(
    subindicator_scores: Iterable[tuple[float, float]],
) -> float:
    """
    Calculates a weighted dimension score.

    Each tuple contains:

        (subindicator_score, subindicator_weight)

    Active subindicator weights are normalized before aggregation.
    """

    items = [
        (
            _clamp(float(score), 0.0, 100.0),
            max(0.0, float(weight)),
        )
        for score, weight in subindicator_scores
    ]

    total_weight = sum(weight for _, weight in items)

    if total_weight <= 0:
        return 0.0

    score = sum(
        subindicator_score * (weight / total_weight)
        for subindicator_score, weight in items
    )

    return _clamp(score, 0.0, 100.0)


def calculate_country_risk(
    *,
    internal_instability: float,
    conflict_violence: float,
    international_tension: float,
    military_activity: float,
    pressure_stress: float,
) -> float:
    """
    Calculates Country Risk using the V1.1 dimension weights.
    """

    scores = {
        "internal_instability": (
            _clamp(internal_instability, 0.0, 100.0),
            0.25,
        ),
        "conflict_violence": (
            _clamp(conflict_violence, 0.0, 100.0),
            0.25,
        ),
        "international_tension": (
            _clamp(international_tension, 0.0, 100.0),
            0.20,
        ),
        "military_activity": (
            _clamp(military_activity, 0.0, 100.0),
            0.15,
        ),
        "pressure_stress": (
            _clamp(pressure_stress, 0.0, 100.0),
            0.15,
        ),
    }

    risk = sum(score * weight for score, weight in scores.values())

    return _clamp(risk, 0.0, 100.0)


def calculate_trend(
    current_country_risk: float,
    previous_country_risk: float,
) -> float:
    """
    Trend = current Country Risk - previous Country Risk.
    """

    return (
        _clamp(current_country_risk, 0.0, 100.0)
        - _clamp(previous_country_risk, 0.0, 100.0)
    )