from fastapi import APIRouter, HTTPException

from backend.app.db import get_connection


router = APIRouter(
    prefix="/api/v1/countries",
    tags=["country"],
)


@router.get("/{country_id}")
def get_country(country_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:

            # Identidad del país
            cur.execute(
                """
                SELECT
                    id,
                    iso2,
                    iso3,
                    name,
                    status
                FROM countries
                WHERE id = %s
                """,
                (country_id,),
            )

            country_row = cur.fetchone()

            if country_row is None:
                raise HTTPException(
                    status_code=404,
                    detail="País no encontrado",
                )

            # Último snapshot de riesgo
            cur.execute(
                """
                SELECT
                    timestamp,
                    internal_instability,
                    conflict_violence,
                    international_tension,
                    military_activity,
                    pressure_stress,
                    country_risk,
                    confidence
                FROM risk_snapshots
                WHERE country_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (country_id,),
            )

            risk_row = cur.fetchone()

            # Últimos subindicadores
            cur.execute(
                """
                SELECT DISTINCT ON (rs.subindicator_id)
                    rs.subindicator_id,
                    si.code,
                    si.name,
                    rs.score,
                    rs.timestamp
                FROM risk_subindicator_snapshots rs
                JOIN subindicators si
                    ON si.id = rs.subindicator_id
                WHERE rs.country_id = %s
                ORDER BY
                    rs.subindicator_id,
                    rs.timestamp DESC
                """,
                (country_id,),
            )

            subindicator_rows = cur.fetchall()

            # Eventos asociados al país
            cur.execute(
                """
                SELECT
                    e.id,
                    ev.title,
                    ev.category,
                    ev.severity,
                    ev.escalation_score,
                    ev.time_start,
                    ev.confidence
                FROM event_countries ec
                JOIN events e
                    ON e.id = ec.event_id
                JOIN event_versions ev
                    ON ev.id = e.current_version_id
                WHERE ec.country_id = %s
                ORDER BY
                    ev.time_start DESC NULLS LAST,
                    e.updated_at DESC
                LIMIT 10
                """,
                (country_id,),
            )

            event_rows = cur.fetchall()

    return {
        "country": {
            "id": int(country_row[0]),
            "iso2": country_row[1],
            "iso3": country_row[2],
            "name": country_row[3],
            "status": country_row[4],
        },
        "risk": (
            {
                "timestamp": risk_row[0],
                "internal_instability": float(risk_row[1]),
                "conflict_violence": float(risk_row[2]),
                "international_tension": float(
                    risk_row[3]
                ),
                "military_activity": float(
                    risk_row[4]
                ),
                "pressure_stress": float(
                    risk_row[5]
                ),
                "country_risk": float(risk_row[6]),
                "confidence": risk_row[7],
            }
            if risk_row is not None
            else None
        ),
        "subindicators": [
            {
                "id": int(row[0]),
                "code": row[1],
                "name": row[2],
                "score": float(row[3]),
                "timestamp": row[4],
            }
            for row in subindicator_rows
        ],
        "events": [
            {
                "id": str(row[0]),
                "title": row[1],
                "category": row[2],
                "severity": row[3],
                "escalation_score": (
                    float(row[4])
                    if row[4] is not None
                    else None
                ),
                "time_start": row[5],
                "confidence": row[6],
            }
            for row in event_rows
        ],
    }