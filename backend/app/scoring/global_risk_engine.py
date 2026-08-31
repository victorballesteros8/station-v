from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Tier1Components:
    """Intermediate components of Tier 1 pressure."""

    intensity: float
    average: float
    breadth: float
    pressure: float


def _validate_score(value: float) -> float:
    if not 0 <= value <= 100:
        raise ValueError("Country Risk must be between 0 and 100")

    return float(value)


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0

    return sum(values) / len(values)


def calculate_tier_1_components(
    country_risks: Sequence[float],
) -> Tier1Components:
    """
    Calculate the Tier 1 components defined by Global Risk V1.

    Intensity:
        I = 0.60 × max(T1) + 0.40 × mean(Top4 T1)

    Average:
        A = mean(T1)

    Breadth:
        B = 100 × N(Country Risk >= 50) / N(Tier 1)

    Tier 1 pressure:
        T1 = 0.50 × I + 0.30 × A + 0.20 × B
    """

    if not country_risks:
        return Tier1Components(
            intensity=0.0,
            average=0.0,
            breadth=0.0,
            pressure=0.0,
        )

    values = sorted(
        (_validate_score(value) for value in country_risks),
        reverse=True,
    )

    maximum = values[0]
    top4_mean = _mean(values[:4])

    intensity = (
        0.60 * maximum
        + 0.40 * top4_mean
    )

    average = _mean(values)

    breadth = (
        100.0
        * sum(1 for value in values if value >= 50)
        / len(values)
    )

    pressure = (
        0.50 * intensity
        + 0.30 * average
        + 0.20 * breadth
    )

    return Tier1Components(
        intensity=intensity,
        average=average,
        breadth=breadth,
        pressure=max(0.0, min(100.0, pressure)),
    )


def calculate_tier_2_pressure(
    country_risks: Sequence[float],
) -> float:
    """
    T2 = mean(Top8 T2)
    """

    values = sorted(
        (_validate_score(value) for value in country_risks),
        reverse=True,
    )

    return _mean(values[:8])


def calculate_tier_3_pressure(
    country_risks: Sequence[float],
) -> float:
    """
    T3 = mean(Top10 T3)
    """

    values = sorted(
        (_validate_score(value) for value in country_risks),
        reverse=True,
    )

    return _mean(values[:10])


def calculate_global_risk(
    tier_1_risks: Sequence[float],
    tier_2_risks: Sequence[float],
    tier_3_risks: Sequence[float],
) -> float:
    """
    Calculate Global Risk V1.

    GR = 0.65 × T1 + 0.25 × T2 + 0.10 × T3
    """

    tier1 = calculate_tier_1_components(tier_1_risks)
    tier2 = calculate_tier_2_pressure(tier_2_risks)
    tier3 = calculate_tier_3_pressure(tier_3_risks)

    global_risk = (
        0.65 * tier1.pressure
        + 0.25 * tier2
        + 0.10 * tier3
    )

    return max(0.0, min(100.0, global_risk))