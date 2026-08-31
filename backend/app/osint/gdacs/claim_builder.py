from __future__ import annotations

from dataclasses import dataclass

from backend.app.osint.gdacs.normalizer import GDACSEarthquake


@dataclass(frozen=True)
class GDACSClaim:
    claim_type: str
    statement: str
    assertion_status: str
    confidence: str


def build_gdacs_claim(
    earthquake: GDACSEarthquake,
) -> GDACSClaim:
    magnitude = (
        f"{earthquake.magnitude:.1f}"
        if earthquake.magnitude is not None
        else "unknown"
    )

    location = (
        earthquake.country
        if earthquake.country
        else "unknown location"
    )

    alert_level = (
        earthquake.alert_level
        if earthquake.alert_level
        else "unknown"
    )

    statement = (
        f"GDACS reports an earthquake alert: "
        f"magnitude {magnitude}, "
        f"{location}, "
        f"alert level {alert_level}."
    )

    return GDACSClaim(
        claim_type="earthquake_alert",
        statement=statement,
        assertion_status="reported",
        confidence="high",
    )