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

from .global_risk_engine import (
    calculate_global_risk,
    calculate_tier_1_components,
    calculate_tier_2_pressure,
    calculate_tier_3_pressure,
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

@dataclass(frozen=True)
class GlobalRiskResult:
    global_risk: float
    tier1_pressure: float
    tier1_intensity: float
    tier1_average: float
    tier1_breadth: float
    tier2_pressure: float
    tier3_pressure: float
    tier1_countries: int
    tier2_countries: int
    tier3_countries: int
    coverage_global: float
    coverage_systemic: float
    coverage_status: str

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
    country_id: int,
    subindicator_id: int,
    reference_time: datetime,
) -> int:
    """
    Returns the repetition position of an event for a specific
    country/subindicator context.

    Repetition is based on distinct correlated events, not on
    event_timeline updates.

    Qualifying relations:
        - same_series
        - escalates
        - same_series
        - part_of

    Non-qualifying relations such as related, preceded_by and
    followed_by do not activate repetition reduction.

    Relations are traversed as an undirected graph for repetition
    purposes, while preserving their semantic direction elsewhere.
    """

    cur.execute(
        """
        WITH RECURSIVE correlated_events AS (
            SELECT
                %s::uuid AS event_id,
                ARRAY[%s::uuid] AS visited

            UNION ALL

            SELECT
                CASE
                    WHEN er.event_id = ce.event_id
                        THEN er.related_event_id
                    ELSE er.event_id
                END AS event_id,
                ce.visited || CASE
                    WHEN er.event_id = ce.event_id
                        THEN er.related_event_id
                    ELSE er.event_id
                END
            FROM correlated_events ce
            JOIN event_relations er
                ON (
                    er.event_id = ce.event_id
                    OR er.related_event_id = ce.event_id
                )
            WHERE er.relation_type IN (
                'same_series',
                'escalates',
                'same_series',
                'part_of'
            )
            AND NOT (
                CASE
                    WHEN er.event_id = ce.event_id
                        THEN er.related_event_id
                    ELSE er.event_id
                END = ANY(ce.visited)
            )
        ),
        candidate_events AS (
            SELECT DISTINCT
                ce.event_id,
                ev.time_start
            FROM correlated_events ce
            JOIN events e
                ON e.id = ce.event_id
            JOIN event_versions ev
                ON ev.id = e.current_version_id
            JOIN risk_impacts ri
                ON ri.event_id = e.id
            WHERE ri.country_id = %s
              AND ri.subindicator_id = %s
              AND ev.time_start IS NOT NULL
              AND ev.time_start >= %s - INTERVAL '7 days'
              AND ev.time_start <= %s
        )
        SELECT
            event_id,
            time_start
        FROM candidate_events
        ORDER BY time_start ASC, event_id ASC
        """,
        (
            event_id,
            event_id,
            country_id,
            subindicator_id,
            reference_time,
            reference_time,
        ),
    )

    related_events = cur.fetchall()

    if not related_events:
        return 1

    for position, row in enumerate(related_events, start=1):
        if str(row[0]) == str(event_id):
            return position

    return 1


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
          AND e.duplicate_of IS NULL
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
                    country_id,
                    impact["subindicator_id"],
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

def _get_global_risk_coverage_status(
    coverage_global: float,
    coverage_systemic: float,
) -> str:
    if (
        coverage_global >= 60.0
        and coverage_systemic >= 80.0
    ):
        return "operational"

    if (
        coverage_global >= 25.0
        and coverage_systemic >= 50.0
    ):
        return "provisional"

    return "insufficient"

def calculate_global_risk_snapshot(
    *,
    reference_time: datetime | None = None,
) -> GlobalRiskResult:
    """
    Calculate Global Risk from the latest valid Country Risk snapshot
    available for each country.

    Countries without a valid snapshot are excluded from the calculation.
    Missing data is never interpreted as Country Risk = 0.
    """

    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    else:
        reference_time = _normalise_timestamp(reference_time)

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    ct.tier,
                    rs.country_risk
                FROM country_tiers ct
                LEFT JOIN LATERAL (
                    SELECT country_risk
                    FROM risk_snapshots
                    WHERE country_id = ct.country_id
                    AND timestamp <= %s
                    AND country_risk IS NOT NULL
                    ORDER BY timestamp DESC
                    LIMIT 1
                ) rs ON TRUE
                ORDER BY ct.tier, rs.country_risk DESC NULLS LAST
                """,
                (reference_time,),
            )

            rows = cur.fetchall()

    tier1_risks: list[float] = []
    tier2_risks: list[float] = []
    tier3_risks: list[float] = []

    for tier, country_risk in rows:
        if country_risk is None:
            continue

        value = float(country_risk)

        if tier == 1:
            tier1_risks.append(value)
        elif tier == 2:
            tier2_risks.append(value)
        elif tier == 3:
            tier3_risks.append(value)

    tier1_total = sum(1 for tier, _ in rows if tier == 1)
    tier2_total = sum(1 for tier, _ in rows if tier == 2)
    tier3_total = sum(1 for tier, _ in rows if tier == 3)

    total_countries = (
        tier1_total
        + tier2_total
        + tier3_total
    )

    covered_countries = (
        len(tier1_risks)
        + len(tier2_risks)
        + len(tier3_risks)
    )

    systemic_total = tier1_total + tier2_total
    systemic_covered = (
        len(tier1_risks)
        + len(tier2_risks)
    )

    coverage_global = (
        100.0 * covered_countries / total_countries
        if total_countries
        else 0.0
    )

    coverage_systemic = (
        100.0 * systemic_covered / systemic_total
        if systemic_total
        else 0.0
    )

    coverage_status = _get_global_risk_coverage_status(
        coverage_global,
        coverage_systemic,
    )

    tier1 = calculate_tier_1_components(tier1_risks)
    tier2 = calculate_tier_2_pressure(tier2_risks)
    tier3 = calculate_tier_3_pressure(tier3_risks)

    global_risk = calculate_global_risk(
        tier_1_risks=tier1_risks,
        tier_2_risks=tier2_risks,
        tier_3_risks=tier3_risks,
    )

    return GlobalRiskResult(
        global_risk=global_risk,
        tier1_pressure=tier1.pressure,
        tier1_intensity=tier1.intensity,
        tier1_average=tier1.average,
        tier1_breadth=tier1.breadth,
        tier2_pressure=tier2,
        tier3_pressure=tier3,
        tier1_countries=len(tier1_risks),
        tier2_countries=len(tier2_risks),
        tier3_countries=len(tier3_risks),
        coverage_global=coverage_global,
        coverage_systemic=coverage_systemic,
        coverage_status=coverage_status,
    )
