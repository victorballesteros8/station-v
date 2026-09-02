from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.app.db import get_connection
from backend.app.osint.earthquake_severity import (
    resolve_gdacs_earthquake_severity,
)
from backend.app.services.event_resolution import resolve_evidence_event
from backend.app.services.risk_impact_service import assign_event_risk_impacts


GDACS_SOURCE_NAME = "GDACS"


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        return None

    return datetime.fromisoformat(value)


def _to_float_or_none(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    return None


def backfill_gdacs_events() -> int:
    """Resolve GDACS Evidence and ensure their RiskImpacts are assigned.

    The operation is deliberately rerunnable: Evidence already linked to an
    EVENT is not resolved again, but its EVENT is still passed through the
    RiskImpact assignment step. This is necessary because Event Resolution
    and RiskImpact assignment are separate, idempotent stages.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    e.id,
                    e.source_id,
                    e.external_id,
                    e.title,
                    e.published_at,
                    e.structured_data,
                    e.event_id
                FROM evidence e
                JOIN sources s
                    ON s.id = e.source_id
                WHERE s.name = %s
                ORDER BY e.retrieved_at, e.id
                """,
                (GDACS_SOURCE_NAME,),
            )

            rows = cur.fetchall()
            resolved = 0
            impacts_assigned = 0

            for row in rows:
                (
                    evidence_id,
                    source_id,
                    external_event_id,
                    title,
                    published_at,
                    structured_data,
                    existing_event_id,
                ) = row

                if not isinstance(structured_data, dict):
                    raise ValueError(
                        f"GDACS evidence {evidence_id} has invalid structured_data"
                    )

                if existing_event_id is not None:
                    event_id = str(existing_event_id)
                else:
                    event_time = _parse_datetime(
                        structured_data.get("event_time")
                    ) or published_at

                    event_name = structured_data.get("event_name")
                    country = structured_data.get("country")
                    if not isinstance(event_name, str) or not event_name:
                        event_name = title or (
                            f"Earthquake in {country}"
                            if isinstance(country, str) and country
                            else external_event_id
                        )

                    magnitude = structured_data.get("magnitude")
                    alert_level = structured_data.get("alert_level")
                    severity = resolve_gdacs_earthquake_severity(
                        {
                            "magnitude": magnitude,
                            "alert_level": alert_level,
                        }
                    )

                    event_id = str(
                        resolve_evidence_event(
                            cur,
                            evidence_id=str(evidence_id),
                            source_id=str(source_id),
                            source_name=GDACS_SOURCE_NAME,
                            external_event_id=str(external_event_id),
                            title=event_name,
                            summary=(
                                f"GDACS earthquake: {event_name}"
                            ),
                            category="disaster",
                            subtype="earthquake",
                            severity=severity,
                            confidence="high",
                            time_start=event_time,
                            latitude=_to_float_or_none(
                                structured_data.get("latitude")
                            ),
                            longitude=_to_float_or_none(
                                structured_data.get("longitude")
                            ),
                            country_iso3=(
                                str(structured_data["country_iso3"])
                                if structured_data.get("country_iso3")
                                else None
                            ),
                            canonical_data=structured_data,
                        )
                    )
                    resolved += 1

                impacts_assigned += assign_event_risk_impacts(
                    cur,
                    event_id,
                )

        conn.commit()

    print(f"GDACS RISK IMPACTS ASSIGNED: {impacts_assigned}")
    return resolved


if __name__ == "__main__":
    print(f"GDACS EVENTS RESOLVED: {backfill_gdacs_events()}")
