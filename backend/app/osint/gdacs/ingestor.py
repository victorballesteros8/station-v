from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from psycopg.types.json import Jsonb

from backend.app.db import get_connection
from backend.app.osint.common.claim_persistence import (
    _persist_claim,
)
from backend.app.osint.common.evidence_persistence import (
    upsert_evidence,
)
from backend.app.osint.gdacs.claim_builder import build_gdacs_claim
from backend.app.osint.gdacs.client import fetch_gdacs_events
from backend.app.osint.gdacs.normalizer import (
    GDACSEarthquake,
    normalize_gdacs_feed,
)
from backend.app.services.event_resolution import (
    resolve_evidence_event,
)


GDACS_SOURCE_NAME = "GDACS"

GDACS_SOURCE_CONFIG = {
    "name": GDACS_SOURCE_NAME,
    "tier": "T1",
    "source_class": "institutional",
    "source_type": "structured_dataset",
    "geographic_scope": "global",
    "coverage": {
        "domain": "natural_disasters",
        "specialization": "earthquakes",
    },
    "roles": [
        "detection",
        "observation",
        "context",
    ],
    "expertise": [
        "natural_disasters",
        "earthquakes",
        "disaster_alerts",
    ],
    "independence_group": "gdacs",
    "access_method": "api",
    "status": "active",
}


def _json_value(value: Any) -> Any:
    import json

    return json.dumps(value)


def _get_or_create_source(cur: Any) -> str:
    cur.execute(
        """
        SELECT id
        FROM sources
        WHERE name = %s
        LIMIT 1
        """,
        (GDACS_SOURCE_NAME,),
    )

    row = cur.fetchone()

    if row is not None:
        return str(row[0])

    cur.execute(
        """
        INSERT INTO sources (
            name,
            tier,
            source_class,
            source_type,
            geographic_scope,
            coverage,
            roles,
            expertise,
            independence_group,
            access_method,
            status
        )
        VALUES (
            %(name)s,
            %(tier)s,
            %(source_class)s,
            %(source_type)s,
            %(geographic_scope)s,
            %(coverage)s,
            %(roles)s,
            %(expertise)s,
            %(independence_group)s,
            %(access_method)s,
            %(status)s
        )
        RETURNING id
        """,
        {
            **GDACS_SOURCE_CONFIG,
            "coverage": _json_value(GDACS_SOURCE_CONFIG["coverage"]),
            "roles": _json_value(GDACS_SOURCE_CONFIG["roles"]),
            "expertise": _json_value(GDACS_SOURCE_CONFIG["expertise"]),
        },
    )

    return str(cur.fetchone()[0])


def _build_structured_data(earthquake: GDACSEarthquake) -> Jsonb:
    return Jsonb(
        {
            "provider": "GDACS",
            "event_id": earthquake.event_id,
            "episode_id": earthquake.episode_id,
            "event_type": earthquake.event_type,
            "alert_level": earthquake.alert_level,
            "alert_score": earthquake.alert_score,
            "event_name": earthquake.event_name,
            "country": earthquake.country,
            "country_iso3": earthquake.country_iso3,
            "latitude": earthquake.latitude,
            "longitude": earthquake.longitude,
            "magnitude": earthquake.magnitude,
            "depth": earthquake.depth,
            "event_time": (
                earthquake.event_time.isoformat()
                if earthquake.event_time is not None
                else None
            ),
            "update_time": (
                earthquake.update_time.isoformat()
                if earthquake.update_time is not None
                else None
            ),
            "source": earthquake.source,
            "geometry_url": earthquake.geometry_url,
            "report_url": earthquake.report_url,
            "details_url": earthquake.details_url,
        }
    )


def _upsert_evidence(
    cur: Any,
    source_id: str,
    earthquake: GDACSEarthquake,
    retrieved_at: datetime,
) -> str:
    title = (
        earthquake.event_name
        or (
            f"Earthquake in {earthquake.country}"
            if earthquake.country
            else "GDACS earthquake alert"
        )
    )

    return upsert_evidence(
        cur,
        {
            "source_id": source_id,
            "external_id": earthquake.event_id,
            "external_episode_id": earthquake.episode_id,
            "published_at": earthquake.event_time,
            "retrieved_at": retrieved_at,
            "title": title,
            "url": earthquake.report_url or earthquake.details_url,
            "content_type": "application/geo+json",
            "evidence_type": "alert",
            "source_role": "detection",
            "independence_group": "gdacs",
            "evidence_quality": 90.0,
            "first_seen_at": retrieved_at,
            "last_seen_at": retrieved_at,
            "structured_data": _build_structured_data(earthquake),
        },
    )


def ingest_gdacs(
    payload: dict[str, Any] | None = None,
    *,
    from_date=None,
    to_date=None,
    event_type: str = "EQ",
) -> int:
    if payload is None:
        if from_date is None or to_date is None:
            raise ValueError(
                "from_date and to_date are required when payload is not provided"
            )

        payload = fetch_gdacs_events(
            from_date=from_date,
            to_date=to_date,
            event_type=event_type,
        )

    earthquakes = normalize_gdacs_feed(payload)
    retrieved_at = datetime.now(timezone.utc)

    with get_connection() as conn:
        with conn.cursor() as cur:
            source_id = _get_or_create_source(cur)

            for earthquake in earthquakes:
                evidence_id = _upsert_evidence(
                    cur,
                    source_id,
                    earthquake,
                    retrieved_at,
                )

                claim = build_gdacs_claim(earthquake)
                _persist_claim(cur, evidence_id, claim)

                resolve_evidence_event(
                    cur,
                    evidence_id=evidence_id,
                    source_id=source_id,
                    source_name=GDACS_SOURCE_NAME,
                    external_event_id=earthquake.event_id,
                    title=(
                        earthquake.event_name
                        or (
                            f"Earthquake in {earthquake.country}"
                            if earthquake.country
                            else "GDACS earthquake alert"
                        )
                    ),
                    summary=claim.statement,
                    subtype="earthquake",
                    time_start=earthquake.event_time,
                    latitude=earthquake.latitude,
                    longitude=earthquake.longitude,
                    country_iso3=earthquake.country_iso3,
                    canonical_data={
                        "provider": "GDACS",
                        "external_event_id": earthquake.event_id,
                        "external_episode_id": earthquake.episode_id,
                        "event_type": earthquake.event_type,
                        "alert_level": earthquake.alert_level,
                        "alert_score": earthquake.alert_score,
                        "event_name": earthquake.event_name,
                        "country": earthquake.country,
                        "country_iso3": earthquake.country_iso3,
                        "latitude": earthquake.latitude,
                        "longitude": earthquake.longitude,
                        "magnitude": earthquake.magnitude,
                        "depth": earthquake.depth,
                    },
                )

        conn.commit()

    return len(earthquakes)
