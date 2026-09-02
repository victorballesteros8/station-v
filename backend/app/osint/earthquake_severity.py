"""V1.2 source-specific severity rules for earthquake events.

The resolver is intentionally pure: it converts objective source fields into
an STATION V event severity without modifying confidence, evidence quality,
or Country Risk.
"""

from __future__ import annotations

from typing import Any

SEVERITY_ORDER = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def _max_severity(*severities: str) -> str:
    return max(severities, key=lambda value: SEVERITY_ORDER[value])


def severity_from_magnitude(magnitude: float | None) -> str:
    """Return the V1.2 minimum severity supported by earthquake magnitude."""
    if magnitude is None:
        return "info"
    if magnitude < 5.0:
        return "info"
    if magnitude < 6.0:
        return "low"
    if magnitude < 7.0:
        return "medium"
    if magnitude < 8.0:
        return "high"
    return "critical"


def _elevate_by_mmi(severity: str, mmi: float | None) -> str:
    if mmi is None:
        return severity
    if mmi >= 8.0:
        return _max_severity(severity, _step_up(severity, 2))
    if mmi >= 7.0:
        return _max_severity(severity, _step_up(severity, 1))
    return severity


def _step_up(severity: str, levels: int) -> str:
    index = min(SEVERITY_ORDER[severity] + levels, SEVERITY_ORDER["critical"])
    return next(name for name, value in SEVERITY_ORDER.items() if value == index)


def resolve_usgs_earthquake_severity(data: dict[str, Any]) -> str:
    """Resolve USGS earthquake severity under the V1.2 documented matrix.

    Magnitude establishes the minimum. USGS PAGER alert and MMI may elevate
    severity; tsunami=1 adds one severity level. ``felt`` and ``significance``
    are deliberately contextual and do not elevate severity in V1.2.
    """
    severity = severity_from_magnitude(_as_float(data.get("magnitude")))

    alert = str(data.get("alert") or "").strip().lower()
    alert_minimum = {
        "green": "info",
        "yellow": "low",
        "orange": "medium",
        "red": "high",
    }.get(alert)
    if alert_minimum:
        severity = _max_severity(severity, alert_minimum)

    severity = _elevate_by_mmi(severity, _as_float(data.get("mmi")))

    if data.get("tsunami") in (1, True, "1", "true", "True"):
        severity = _step_up(severity, 1)

    return severity


def resolve_gdacs_earthquake_severity(data: dict[str, Any]) -> str:
    """Resolve GDACS earthquake severity under the V1.2 documented matrix."""
    severity = severity_from_magnitude(_as_float(data.get("magnitude")))

    alert = str(data.get("alert_level") or "").strip().lower()
    alert_minimum = {
        "green": "info",
        "orange": "medium",
        "red": "high",
    }.get(alert)
    if alert_minimum:
        severity = _max_severity(severity, alert_minimum)

    return severity


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
