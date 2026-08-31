from __future__ import annotations

from dataclasses import dataclass

from backend.app.osint.usgs.normalizer import USGSEarthquake


@dataclass(frozen=True)
class USGSClaim:
    claim_type: str
    statement: str
    assertion_status: str
    confidence: str


def build_usgs_claim(
    earthquake: USGSEarthquake,
) -> USGSClaim:
    magnitude = (
        f"{earthquake.magnitude:.1f}"
        if earthquake.magnitude is not None
        else "unknown"
    )

    if earthquake.place:
        location = earthquake.place
    else:
        location = "unknown location"

    statement = (
        f"Earthquake detected by USGS: "
        f"magnitude {magnitude}, {location}."
    )

    return USGSClaim(
        claim_type="earthquake",
        statement=statement,
        assertion_status="confirmed",
        confidence="high",
    )