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
from backend.app.osint.usgs.claim_builder import build_usgs_claim
from backend.app.osint.usgs.client import fetch_usgs_feed
from backend.app.osint.usgs.normalizer import (
    USGSEarthquake,
    normalize_usgs_feed,
)
from backend.app.services.event_resolution import (
    resolve_evidence_event,
)


USGS_SOURCE_NAME = "USGS"

USGS_SOURCE_CONFIG = {
    "name": USGS_SOURCE_NAME,
    "tier": "T1",
    "source_class": "primary",
    "source_type": "structured_dataset",
    "geographic_scope": "global",
    "coverage": {
        "domain": "earthquakes",
    },
    "roles": [
        "detection",
        "observation",
    ],
    "expertise": [
        "seismic_activity",
        "earthquakes",
    ],
    "independence_group": "usgs",
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
        (USGS_SOURCE_NAME,),
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
            **USGS_SOURCE_CONFIG,
            "coverage": _json_value(USGS_SOURCE_CONFIG["coverage"]),
            "roles": _json_value(USGS_SOURCE_CONFIG["roles"]),
            "expertise": _json_value(USGS_SOURCE_CONFIG["expertise"]),
        },
    )

    return str(cur.fetchone()[0])


def _build_structured_data(earthquake: USGSEarthquake) -> Jsonb:
    return Jsonb(
        {
            "provider": "USGS",
            "magnitude": earthquake.magnitude,
            "place": earthquake.place,
            "latitude": earthquake.latitude,
            "longitude": earthquake.longitude,
            "depth": earthquake.depth,
            "alert": earthquake.alert,
            "significance": earthquake.significance,
            "tsunami": earthquake.tsunami,
            "felt": earthquake.felt,
            "mmi": earthquake.mmi,
            "cdi": earthquake.cdi,
            "event_time": (
                earthquake.time.isoformat()
                if earthquake.time is not None
                else None
            ),
            "updated_time": (
                earthquake.updated.isoformat()
                if earthquake.updated is not None
                else None
            ),
        }
    )


def _upsert_evidence(
    cur: Any,
    source_id: str,
    earthquake: USGSEarthquake,
    retrieved_at: datetime,
) -> str:
    return upsert_evidence(
        cur,
        {
            "source_id": source_id,
            "external_id": earthquake.external_id,
            "external_episode_id": None,
            "published_at": earthquake.time,
            "retrieved_at": retrieved_at,
            "title": earthquake.place,
            "url": earthquake.source_url,
            "content_type": "application/geo+json",
            "evidence_type": "measurement",
            "source_role": "detection",
            "independence_group": "usgs",
            "evidence_quality": 100.0,
            "first_seen_at": retrieved_at,
            "last_seen_at": retrieved_at,
            "structured_data": _build_structured_data(earthquake),
        },
    )


def ingest_usgs(payload: dict[str, Any] | None = None) -> int:
    if payload is None:
        payload = fetch_usgs_feed()

    earthquakes = normalize_usgs_feed(payload)
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

                claim = build_usgs_claim(earthquake)
                _persist_claim(cur, evidence_id, claim)

                resolve_evidence_event(
                    cur,
                    evidence_id=evidence_id,
                    source_id=source_id,
                    source_name=USGS_SOURCE_NAME,
                    external_event_id=earthquake.external_id,
                    title=earthquake.place or "Earthquake detected by USGS",
                    summary=claim.statement,
                    subtype="earthquake",
                    time_start=earthquake.time,
                    latitude=earthquake.latitude,
                    longitude=earthquake.longitude,
                    canonical_data={
                        "provider": "USGS",
                        "external_event_id": earthquake.external_id,
                        "magnitude": earthquake.magnitude,
                        "place": earthquake.place,
                        "latitude": earthquake.latitude,
                        "longitude": earthquake.longitude,
                        "depth": earthquake.depth,
                    },
                )

        conn.commit()

    return len(earthquakes)
