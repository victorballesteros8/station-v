from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.app.db import get_connection


router = APIRouter(
    prefix="/api/v1/situation",
    tags=["situation"],
)


def _get_latest_snapshots(cur: Any) -> list[dict]:
    cur.execute(
        """
        SELECT DISTINCT ON (rs.country_id)
            rs.country_id,
            c.iso2,
            c.name,
            rs.timestamp,
            rs.country_risk,
            rs.confidence
        FROM risk_snapshots rs
        JOIN countries c
            ON c.id = rs.country_id
        ORDER BY
            rs.country_id,
            rs.timestamp DESC
        """
    )

    return [
        {
            "country_id": int(row[0]),
            "iso2": row[1],
            "name": row[2],
            "timestamp": row[3],
            "country_risk": float(row[4]),
            "confidence": row[5],
        }
        for row in cur.fetchall()
    ]


def _get_risk_24h_ago(
    cur: Any,
    country_id: int,
    current_timestamp,
) -> float | None:
    cur.execute(
        """
        SELECT country_risk
        FROM risk_snapshots
        WHERE country_id = %s
          AND timestamp <= %s - INTERVAL '24 hours'
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (
            country_id,
            current_timestamp,
        ),
    )

    row = cur.fetchone()

    if row is None:
        return None

    return float(row[0])


def _get_relevant_events(cur: Any) -> list[dict]:
    cur.execute(
        """
        SELECT
            e.id,
            ev.title,
            ev.status,
            ev.severity,
            ev.escalation_score,
            ev.time_start,
            ev.confidence
        FROM events e
        JOIN event_versions ev
            ON ev.id = e.current_version_id
        WHERE ev.severity IN ('high', 'critical')
        ORDER BY
            ev.escalation_score DESC NULLS LAST,
            ev.time_start DESC
        LIMIT 10
        """
    )

    events = []

    for row in cur.fetchall():
        event_id = row[0]

        cur.execute(
            """
            SELECT
                c.iso2,
                c.name
            FROM event_countries ec
            JOIN countries c
                ON c.id = ec.country_id
            WHERE ec.event_id = %s
            ORDER BY c.name
            """,
            (event_id,),
        )

        countries = [
            {
                "iso2": country[0],
                "name": country[1],
            }
            for country in cur.fetchall()
        ]

        events.append(
            {
                "id": str(row[0]),
                "title": row[1],
                "status": row[2],
                "countries": countries,
                "severity": row[3],
                "escalation_score": (
                    float(row[4])
                    if row[4] is not None
                    else None
                ),
                "time_start": row[5],
                "confidence": row[6],
            }
        )

    return events


@router.get("")
def get_situation():
    with get_connection() as conn:
        with conn.cursor() as cur:
            snapshots = _get_latest_snapshots(cur)

            countries = []

            for snapshot in snapshots:
                risk_24h_ago = _get_risk_24h_ago(
                    cur,
                    snapshot["country_id"],
                    snapshot["timestamp"],
                )

                if risk_24h_ago is None:
                    trend = None
                else:
                    trend = (
                        snapshot["country_risk"]
                        - risk_24h_ago
                    )

                countries.append(
                    {
                        **snapshot,
                        "trend": trend,
                    }
                )

            top_risk = sorted(
                countries,
                key=lambda item: item["country_risk"],
                reverse=True,
            )[:10]

            deterioration = sorted(
                [
                    country
                    for country in countries
                    if country["trend"] is not None
                    and country["trend"] > 0
                ],
                key=lambda item: item["trend"],
                reverse=True,
            )[:10]

            improvement = sorted(
                [
                    country
                    for country in countries
                    if country["trend"] is not None
                    and country["trend"] < 0
                ],
                key=lambda item: item["trend"],
            )[:10]

            relevant_events = _get_relevant_events(cur)

    return {
        "top_risk": top_risk,
        "deterioration_24h": deterioration,
        "improvement_24h": improvement,
        "relevant_events": relevant_events,
    }