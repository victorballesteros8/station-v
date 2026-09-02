from __future__ import annotations

from typing import Any
from uuid import UUID


# V1.2 calibration points selected inside the severity ranges defined by
# the mathematical methodology.
BASE_IMPACT_BY_SEVERITY: dict[str, float] = {
    "info": 0.0,
    "low": 2.0,
    "medium": 4.0,
    "high": 8.0,
    "critical": 15.0,
}

EARTHQUAKE_SUBINDICATOR_ID = 40


def _get_event_context(cur: Any, event_id: str) -> tuple[str, str, str]:
    cur.execute(
        """
        SELECT ev.category, ev.subtype, ev.severity
        FROM events e
        JOIN event_versions ev
          ON ev.id = e.current_version_id
        WHERE e.id = %s
        """,
        (event_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"Event not found: {event_id}")

    return str(row[0]), str(row[1]), str(row[2])


def _get_direct_country_ids(cur: Any, event_id: str) -> list[int]:
    cur.execute(
        """
        SELECT country_id
        FROM event_countries
        WHERE event_id = %s
          AND relationship_type = 'directly_affected'
        ORDER BY country_id
        """,
        (event_id,),
    )
    return [int(row[0]) for row in cur.fetchall()]


def _upsert_risk_impact(
    cur: Any,
    *,
    event_id: str,
    country_id: int,
    subindicator_id: int,
    base_impact: float,
    relevance: float,
) -> None:
    cur.execute(
        """
        SELECT id
        FROM risk_impacts
        WHERE event_id = %s
          AND country_id = %s
          AND subindicator_id = %s
        ORDER BY created_at ASC, id ASC
        LIMIT 1
        """,
        (event_id, country_id, subindicator_id),
    )
    row = cur.fetchone()

    if row is None:
        cur.execute(
            """
            INSERT INTO risk_impacts (
                event_id,
                country_id,
                subindicator_id,
                base_impact,
                relevance
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                event_id,
                country_id,
                subindicator_id,
                base_impact,
                relevance,
            ),
        )
        return

    cur.execute(
        """
        UPDATE risk_impacts
        SET
            base_impact = %s,
            relevance = %s,
            updated_at = now()
        WHERE id = %s
        """,
        (base_impact, relevance, row[0]),
    )


def assign_event_risk_impacts(cur: Any, event_id: str) -> int:
    """Assign deterministic V1.2 RiskImpact records from a resolved EVENT.

    The first implementation intentionally covers only the explicit V1.2
    earthquake rule:
        disaster / earthquake -> subindicator 40, relevance 1.00

    No secondary impact is inferred from the existence of an earthquake.
    The function is idempotent for the EVENT/country/subindicator tuple.
    """
    category, subtype, severity = _get_event_context(cur, event_id)

    if category != "disaster" or subtype != "earthquake":
        return 0

    try:
        base_impact = BASE_IMPACT_BY_SEVERITY[severity]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported event severity for risk impact: {severity}"
        ) from exc

    country_ids = _get_direct_country_ids(cur, event_id)
    if not country_ids:
        return 0

    for country_id in country_ids:
        _upsert_risk_impact(
            cur,
            event_id=event_id,
            country_id=country_id,
            subindicator_id=EARTHQUAKE_SUBINDICATOR_ID,
            base_impact=base_impact,
            relevance=1.0,
        )

    return len(country_ids)
