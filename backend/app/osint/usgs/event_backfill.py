from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.app.db import get_connection
from backend.app.osint.earthquake_severity import resolve_usgs_earthquake_severity
from backend.app.services.event_resolution import resolve_evidence_event

USGS_SOURCE_NAME = "USGS"


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


def backfill_usgs_events() -> int:
    """Resolve pending USGS Evidence into deterministic STATION V EVENTs.

    Only Evidence without an event_id is processed. Event identity is left
    entirely to the shared V1 event-resolution service, which uses the
    deterministic USGS source identity (external_id) and performs no
    heuristic cross-source matching.
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
                    e.structured_data
                FROM evidence e
                JOIN sources s
                    ON s.id = e.source_id
                WHERE s.name = %s
                  AND e.event_id IS NULL
                ORDER BY e.retrieved_at, e.id
                """,
                (USGS_SOURCE_NAME,),
            )

            rows = cur.fetchall()
            resolved = 0

            for row in rows:
                (
                    evidence_id,
                    source_id,
                    external_event_id,
                    title,
                    published_at,
                    structured_data,
                ) = row

                if not isinstance(structured_data, dict):
                    raise ValueError(
                        f"USGS evidence {evidence_id} has invalid structured_data"
                    )

                event_time = _parse_datetime(
                    structured_data.get("event_time")
                ) or published_at

                place = structured_data.get("place")
                if not isinstance(place, str) or not place:
                    place = title or external_event_id

                severity = resolve_usgs_earthquake_severity(
                    structured_data
                )

                resolve_evidence_event(
                    cur,
                    evidence_id=str(evidence_id),
                    source_id=str(source_id),
                    source_name=USGS_SOURCE_NAME,
                    external_event_id=str(external_event_id),
                    title=place,
                    summary=f"USGS earthquake: {place}",
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
                    canonical_data=structured_data,
                )

                resolved += 1

        conn.commit()

    return resolved


if __name__ == "__main__":
    print(f"USGS EVENTS RESOLVED: {backfill_usgs_events()}")
