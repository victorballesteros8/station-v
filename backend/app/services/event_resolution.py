from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from backend.app.schemas.events import EventUpdate
from backend.app.services.event_service import _update_event_with_cursor


# V1 deliberately resolves deterministic source identities first. Heuristic
# cross-source matching is kept out of this service until source-specific
# thresholds have been validated against real data.


def _find_existing_event(
    cur: Any,
    *,
    source_id: str,
    external_event_id: str,
    evidence_id: str,
) -> UUID | None:
    cur.execute(
        """
        SELECT event_id
        FROM evidence
        WHERE source_id = %s
          AND external_id = %s
          AND event_id IS NOT NULL
          AND id <> %s
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (source_id, external_event_id, evidence_id),
    )
    row = cur.fetchone()
    return UUID(str(row[0])) if row is not None else None


def _severity_rank(value: str) -> int:
    return {
        "info": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }[value]


def _create_event(
    cur: Any,
    *,
    source_name: str,
    title: str,
    summary: str,
    category: str,
    subtype: str,
    severity: str,
    confidence: str,
    time_start: datetime | None,
    latitude: float | None,
    longitude: float | None,
    canonical_data: dict[str, Any],
    country_iso3: str | None = None,
) -> UUID:
    event_id = uuid4()
    version_id = uuid4()
    detected_at = time_start or datetime.now(timezone.utc)

    cur.execute(
        """
        INSERT INTO events (
            id,
            current_version_id,
            first_detected_at,
            last_evidence_at
        )
        VALUES (%s, NULL, %s, %s)
        """,
        (event_id, detected_at, detected_at),
    )

    import json

    location_precision = (
        "point"
        if latitude is not None and longitude is not None
        else "unknown"
    )
    time_precision = "exact" if time_start is not None else "unknown"

    cur.execute(
        """
        INSERT INTO event_versions (
            id,
            event_id,
            version,
            category,
            subtype,
            title,
            summary,
            location,
            location_precision,
            place,
            time_start,
            time_precision,
            status,
            severity,
            confidence,
            canonical_data,
            created_at
        )
        VALUES (
            %s, %s, 1, %s, %s, %s, %s,
            CASE
                WHEN %s IS NOT NULL AND %s IS NOT NULL
                THEN ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ELSE NULL
            END,
            %s,
            %s,
            %s,
            %s,
            'active',
            %s,
            %s,
            %s::jsonb,
            now()
        )
        """,
        (
            version_id,
            event_id,
            category,
            subtype,
            title,
            summary,
            latitude,
            longitude,
            longitude,
            latitude,
            location_precision,
            canonical_data.get("place") or canonical_data.get("event_name"),
            time_start,
            time_precision,
            severity,
            confidence,
            json.dumps(canonical_data),
        ),
    )

    cur.execute(
        """
        UPDATE events
        SET current_version_id = %s, updated_at = now()
        WHERE id = %s
        """,
        (version_id, event_id),
    )

    if country_iso3:
        cur.execute(
            """
            INSERT INTO event_countries (
                event_id,
                country_id,
                relationship_type
            )
            SELECT %s, id, 'directly_affected'
            FROM countries
            WHERE iso3 = upper(%s)
            ON CONFLICT DO NOTHING
            """,
            (event_id, country_iso3),
        )

    cur.execute(
        """
        INSERT INTO event_timeline (
            event_id,
            timestamp,
            update_type,
            description,
            event_version_id
        )
        VALUES (%s, now(), 'new_evidence', %s, %s)
        """,
        (
            event_id,
            f"EVENT creado a partir de Evidence de {source_name}.",
            version_id,
        ),
    )

    return event_id


def resolve_evidence_event(
    cur: Any,
    *,
    evidence_id: str,
    source_id: str,
    source_name: str,
    external_event_id: str,
    title: str,
    summary: str,
    category: str,
    subtype: str,
    severity: str,
    confidence: str,
    time_start: datetime | None,
    latitude: float | None,
    longitude: float | None,
    canonical_data: dict[str, Any],
    country_iso3: str | None = None,
) -> UUID:
    """Resolve one structured Evidence against a STATION V EVENT.

    V1 uses deterministic source identity only. Repeated observations from
    the same source event are attached to the existing EVENT. If a repeated
    source observation resolves to a higher severity, the existing EVENT is
    versioned through Event Service rather than duplicated.
    """
    existing_event_id = _find_existing_event(
        cur,
        source_id=source_id,
        external_event_id=external_event_id,
        evidence_id=evidence_id,
    )

    event_id = existing_event_id

    if event_id is None:
        event_id = _create_event(
            cur,
            source_name=source_name,
            title=title,
            summary=summary,
            category=category,
            subtype=subtype,
            severity=severity,
            confidence=confidence,
            time_start=time_start,
            latitude=latitude,
            longitude=longitude,
            canonical_data=canonical_data,
            country_iso3=country_iso3,
        )
    else:
        cur.execute(
            """
            SELECT ev.severity
            FROM events e
            JOIN event_versions ev
                ON ev.id = e.current_version_id
            WHERE e.id = %s
            FOR UPDATE
            """,
            (event_id,),
        )
        row = cur.fetchone()
        current_severity = str(row[0]) if row is not None else "info"

        if _severity_rank(severity) > _severity_rank(current_severity):
            _update_event_with_cursor(
                cur,
                event_id=event_id,
                update=EventUpdate(
                    severity=severity,
                    update_type="severity_change",
                    description=(
                        f"Severidad actualizada de {current_severity} a {severity} "
                        f"por nueva evidencia de {source_name}."
                    ),
                ),
            )

    cur.execute(
        """
        UPDATE evidence
        SET
            event_id = %s,
            updated_at = now()
        WHERE id = %s
        """,
        (event_id, evidence_id),
    )

    cur.execute(
        """
        UPDATE events
        SET
            last_evidence_at = now(),
            updated_at = now()
        WHERE id = %s
        """,
        (event_id,),
    )

    return event_id
