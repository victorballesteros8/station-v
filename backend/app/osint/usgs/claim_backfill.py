from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.app.db import get_connection
from backend.app.osint.usgs.claim_builder import build_usgs_claim
from backend.app.osint.usgs.claim_persistence import (
    _persist_usgs_claim,
)
from backend.app.osint.usgs.normalizer import USGSEarthquake


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        return None

    return datetime.fromisoformat(value)


def _to_int_or_none(value: Any) -> int | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return int(value)

    return None


def _to_float_or_none(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    return None


def _earthquake_from_evidence(
    row: tuple[Any, ...],
) -> USGSEarthquake:
    (
        external_id,
        source_url,
        structured_data,
    ) = row

    if not isinstance(structured_data, dict):
        raise ValueError(
            "USGS evidence has no valid structured_data"
        )

    return USGSEarthquake(
        external_id=str(external_id),
        source_url=source_url,
        time=_parse_datetime(
            structured_data.get("event_time")
        ),
        updated=_parse_datetime(
            structured_data.get("updated_time")
        ),
        magnitude=_to_float_or_none(
            structured_data.get("magnitude")
        ),
        place=(
            structured_data.get("place")
            if isinstance(
                structured_data.get("place"),
                str,
            )
            else None
        ),
        latitude=_to_float_or_none(
            structured_data.get("latitude")
        ),
        longitude=_to_float_or_none(
            structured_data.get("longitude")
        ),
        depth=_to_float_or_none(
            structured_data.get("depth")
        ),
        alert=(
            structured_data.get("alert")
            if isinstance(
                structured_data.get("alert"),
                str,
            )
            else None
        ),
        significance=_to_int_or_none(
            structured_data.get("significance")
        ),
        tsunami=_to_int_or_none(
            structured_data.get("tsunami")
        ),
        felt=_to_int_or_none(
            structured_data.get("felt")
        ),
        mmi=_to_float_or_none(
            structured_data.get("mmi")
        ),
        cdi=_to_float_or_none(
            structured_data.get("cdi")
        ),
    )


def backfill_usgs_claims() -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    e.id,
                    e.external_id,
                    e.url,
                    e.structured_data
                FROM evidence e
                JOIN sources s
                    ON s.id = e.source_id
                LEFT JOIN claims cl
                    ON cl.evidence_id = e.id
                    AND cl.claim_type = 'earthquake'
                WHERE s.name = %s
                  AND cl.id IS NULL
                ORDER BY e.retrieved_at
                """,
                ("USGS",),
            )

            rows = cur.fetchall()

            created = 0

            for row in rows:
                (
                    evidence_id,
                    external_id,
                    source_url,
                    structured_data,
                ) = row

                earthquake = _earthquake_from_evidence(
                    (
                        external_id,
                        source_url,
                        structured_data,
                    )
                )

                claim = build_usgs_claim(
                    earthquake
                )

                _persist_usgs_claim(
                    cur,
                    str(evidence_id),
                    claim,
                )

                created += 1

        conn.commit()

    return created