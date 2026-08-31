from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


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


def _create_event(
    cur: Any,
    *,
    source_name: str,
    title: str,
    summary: str,
    subtype: str,
    time_start: datetime | None,
    latitude: float | None,
    longitude: float | None,
    canonical_data: dict[str, Any],
    country_iso3: str | None = None,
) -> UUID:
    event_id = uuid4()
    version_id = uuid4()

    cur.execute(
        """
        INSERT INTO events (
            id,
            current_version_id,
            first_detected_at,
            last_evidence_at
        )
        VALUES (%s, %s, %s, %s)
        """,
        (event_id, version_id, time_start, time_start),
    )

    import json

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
            %s, %s, 1, 'disaster', %s, %s, %s,
            CASE
                WHEN %s IS NOT NULL AND %s IS NOT NULL
                THEN ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ELSE NULL
            END,
            CASE
                WHEN %s IS NOT NULL AND %s IS NOT NULL
                THEN 'point'
                ELSE 'unknown'
            END,
            %s,
            %s,
            'exact',
            'active',
            'info',
            'high',
            %s::jsonb,
            now()
        )
        """,
        (
            version_id,
            event_id,
            subtype,
            title,
            summary,
            latitude,
            longitude,
            longitude,
            latitude,
            latitude,
            longitude,
            canonical_data.get("place"),
            time_start,
            json.dumps(canonical_data),
        ),
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
    subtype: str,
    time_start: datetime | None,
    latitude: float | None,
    longitude: float | None,
    canonical_data: dict[str, Any],
    country_iso3: str | None = None,
) -> UUID:
    """Resolve one structured Evidence against a STATION V EVENT.

    V1 uses deterministic source identity only. Repeated observations from
    the same source event are attached to the existing EVENT. Ambiguous
    cross-source matches are intentionally not guessed here.
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
            subtype=subtype,
            time_start=time_start,
            latitude=latitude,
            longitude=longitude,
            canonical_data=canonical_data,
            country_iso3=country_iso3,
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
