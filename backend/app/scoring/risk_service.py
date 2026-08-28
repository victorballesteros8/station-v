from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from backend.app.db import get_connection

from .risk_engine import (
    RiskImpactInput,
    calculate_country_risk,
    calculate_dimension_score,
    calculate_event_pressure,
    calculate_risk_impact,
    calculate_subindicator_score,
)


@dataclass(frozen=True)
class CountryRiskResult:
    country_id: int
    country_risk: float
    internal_instability: float
    conflict_violence: float
    international_tension: float
    military_activity: float
    pressure_stress: float
    confidence: str


def _normalise_timestamp(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)

    return timestamp.astimezone(timezone.utc)


def _country_exists(
    cur: Any,
    country_id: int,
) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM countries
        WHERE id = %s
        LIMIT 1
        """,
        (country_id,),
    )

    return cur.fetchone() is not None


def _get_previous_subindicator_score(
    cur: Any,
    country_id: int,
    subindicator_id: int,
    reference_time: datetime,
) -> float:
    cur.execute(
        """
        SELECT score
        FROM risk_subindicator_snapshots
        WHERE country_id = %s
          AND subindicator_id = %s
          AND timestamp < %s
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (
            country_id,
            subindicator_id,
            reference_time,
        ),
    )

    row = cur.fetchone()

    if row is None:
        return 0.0

    return float(row[0])


def _get_repetition_count(
    cur: Any,
    event_id: str,
    reference_time: datetime,
) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM event_timeline
        WHERE event_id = %s
          AND update_type IN (
              'initial_detection',
              'occurrence'
          )
          AND timestamp >= %s - INTERVAL '7 days'
          AND timestamp <= %s
        """,
        (
            event_id,
            reference_time,
            reference_time,
        ),
    )

    timeline_count = int(cur.fetchone()[0])

    return max(1, timeline_count)


def _calculate_confidence(
    cur: Any,
    country_id: int,
) -> str:
    cur.execute(
        """
        SELECT ev.confidence
        FROM risk_impacts ri
        JOIN events e
            ON e.id = ri.event_id
        JOIN event_versions ev
            ON ev.id = e.current_version_id
        WHERE ri.country_id = %s
        """,
        (country_id,),
    )

    values = [row[0] for row in cur.fetchall()]

    if not values:
        return "low"

    if all(value == "high" for value in values):
        return "high"

    if any(value == "medium" for value in values):
        return "medium"

    return "low"


def _load_dimensions(cur: Any) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT
            id,
            code,
            weight
        FROM dimensions
        WHERE active = TRUE
        ORDER BY id
        """
    )

    return [
        {
            "id": int(row[0]),
            "code": row[1],
            "weight": float(row[2]),
        }
        for row in cur.fetchall()
    ]


def _load_subindicators(
    cur: Any,
    dimension_id: int,
) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT
            id,
            code,
            weight
        FROM subindicators
        WHERE dimension_id = %s
          AND active = TRUE
        ORDER BY id
        """,
        (dimension_id,),
    )

    return [
        {
            "id": int(row[0]),
            "code": row[1],
            "weight": float(row[2]) if row[2] is not None else 0.0,
        }
        for row in cur.fetchall()
    ]


def _load_risk_impacts(
    cur: Any,
    country_id: int,
    reference_time: datetime,
) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT
            ri.id,
            ri.event_id,
            ri.subindicator_id,
            ri.base_impact,
            ri.relevance,
            ev.time_start
        FROM risk_impacts ri
        JOIN events e
            ON e.id = ri.event_id
        JOIN event_versions ev
            ON ev.id = e.current_version_id
        WHERE ri.country_id = %s
          AND ev.time_start IS NOT NULL
          AND ev.time_start >= %s - INTERVAL '7 days'
          AND ev.time_start <= %s
        ORDER BY ev.time_start DESC
        """,
        (
            country_id,
            reference_time,
            reference_time,
        ),
    )

    return [
        {
            "id": row[0],
            "event_id": row[1],
            "subindicator_id": int(row[2]),
            "base_impact": float(row[3]),
            "relevance": float(row[4]),
            "time_start": row[5],
        }
        for row in cur.fetchall()
    ]


def calculate_country_risk_snapshot(
    country_id: int,
    *,
    reference_time: datetime | None = None,
) -> CountryRiskResult:

    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    else:
        reference_time = _normalise_timestamp(reference_time)

    with get_connection() as conn:
        with conn.cursor() as cur:

            if not _country_exists(cur, country_id):
                raise ValueError(
                    f"Country not found: {country_id}"
                )

            dimensions = _load_dimensions(cur)

            impacts = _load_risk_impacts(
                cur,
                country_id,
                reference_time,
            )

            impacts_by_subindicator: dict[int, list[float]] = {}

            for impact in impacts:

                repetition_count = _get_repetition_count(
                    cur,
                    impact["event_id"],
                    reference_time,
                )

                result = calculate_risk_impact(
                    RiskImpactInput(
                        base_impact=impact["base_impact"],
                        relevance=impact["relevance"],
                        time_start=impact["time_start"],
                        repetition_count=repetition_count,
                    ),
                    reference_time=reference_time,
                )

                cur.execute(
                    """
                    UPDATE risk_impacts
                    SET
                        temporal_weight = %s,
                        repetition_weight = %s,
                        effective_impact = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        result.temporal_weight,
                        result.repetition_weight,
                        result.effective_impact,
                        impact["id"],
                    ),
                )

                impacts_by_subindicator.setdefault(
                    impact["subindicator_id"],
                    [],
                ).append(result.effective_impact)

            dimension_scores: dict[str, float] = {}

            for dimension in dimensions:

                subindicators = _load_subindicators(
                    cur,
                    dimension["id"],
                )

                weighted_scores: list[tuple[float, float]] = []

                for subindicator in subindicators:

                    subindicator_id = subindicator["id"]

                    effective_impacts = impacts_by_subindicator.get(
                        subindicator_id,
                        [],
                    )

                    previous_score = _get_previous_subindicator_score(
                        cur,
                        country_id,
                        subindicator_id,
                        reference_time,
                    )

                    if effective_impacts:
                        event_pressure = calculate_event_pressure(
                            effective_impacts,
                        )

                        subindicator_score = (
                            calculate_subindicator_score(
                                previous_score,
                                event_pressure,
                            )
                        )
                    else:
                        subindicator_score = previous_score

                    cur.execute(
                        """
                        INSERT INTO risk_subindicator_snapshots (
                            country_id,
                            subindicator_id,
                            timestamp,
                            score
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            country_id,
                            subindicator_id,
                            reference_time,
                            subindicator_score,
                        ),
                    )

                    weighted_scores.append(
                        (
                            subindicator_score,
                            subindicator["weight"],
                        )
                    )

                dimension_scores[dimension["code"]] = (
                    calculate_dimension_score(
                        weighted_scores,
                    )
                )

            internal_instability = dimension_scores.get(
                "internal_instability",
                0.0,
            )

            conflict_violence = dimension_scores.get(
                "conflict_violence",
                0.0,
            )

            international_tension = dimension_scores.get(
                "international_tension",
                0.0,
            )

            military_activity = dimension_scores.get(
                "military_activity",
                0.0,
            )

            pressure_stress = dimension_scores.get(
                "pressure_stress",
                0.0,
            )

            country_risk = calculate_country_risk(
                internal_instability=internal_instability,
                conflict_violence=conflict_violence,
                international_tension=international_tension,
                military_activity=military_activity,
                pressure_stress=pressure_stress,
            )

            confidence = _calculate_confidence(
                cur,
                country_id,
            )

            cur.execute(
                """
                INSERT INTO risk_snapshots (
                    country_id,
                    timestamp,
                    internal_instability,
                    conflict_violence,
                    international_tension,
                    military_activity,
                    pressure_stress,
                    country_risk,
                    confidence
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    country_id,
                    reference_time,
                    internal_instability,
                    conflict_violence,
                    international_tension,
                    military_activity,
                    pressure_stress,
                    country_risk,
                    confidence,
                ),
            )

        conn.commit()

    return CountryRiskResult(
        country_id=country_id,
        country_risk=country_risk,
        internal_instability=internal_instability,
        conflict_violence=conflict_violence,
        international_tension=international_tension,
        military_activity=military_activity,
        pressure_stress=pressure_stress,
        confidence=confidence,
    )