from datetime import datetime, timezone
from uuid import uuid4

from backend.app.db import get_connection


EVENTS = [
    {
        "category": "border_tension",
        "subtype": "armed_border_clash",
        "title": "Enfrentamientos fronterizos",
        "summary": "Evento sintético de prueba para STATION V.",
        "analyst_summary": "Evento de desarrollo utilizado para validar el mapa y la API.",
        "lat": 34.6,
        "lon": 73.5,
        "status": "active",
        "severity": "high",
        "escalation_score": 7.8,
        "confidence": "high",
        "countries": ["PAK", "IND"],
    },
    {
        "category": "protests_unrest",
        "subtype": "mass_protest",
        "title": "Manifestaciones masivas",
        "summary": "Evento sintético de protesta para pruebas.",
        "analyst_summary": "Evento de desarrollo utilizado para validar categorías y severidad.",
        "lat": 30.0444,
        "lon": 31.2357,
        "status": "active",
        "severity": "medium",
        "escalation_score": None,
        "confidence": "medium",
        "countries": ["EGY"],
    },
    {
        "category": "military_activity",
        "subtype": "military_exercise",
        "title": "Ejercicio militar",
        "summary": "Evento sintético de actividad militar.",
        "analyst_summary": "Evento de desarrollo utilizado para validar la representación militar.",
        "lat": 36.2048,
        "lon": 138.2529,
        "status": "stable",
        "severity": "low",
        "escalation_score": None,
        "confidence": "high",
        "countries": ["JPN"],
    },
    {
        "category": "critical_infrastructure",
        "subtype": "infrastructure_attack",
        "title": "Ataque contra infraestructura crítica",
        "summary": "Evento sintético de ataque contra infraestructura.",
        "analyst_summary": "Evento de desarrollo utilizado para validar eventos críticos.",
        "lat": 50.4501,
        "lon": 30.5234,
        "status": "active",
        "severity": "critical",
        "escalation_score": 9.1,
        "confidence": "high",
        "countries": ["UKR"],
    },
    {
        "category": "disaster",
        "subtype": "earthquake",
        "title": "Terremoto",
        "summary": "Evento sintético de desastre natural.",
        "analyst_summary": "Evento de desarrollo utilizado para validar eventos de desastre.",
        "lat": 35.6762,
        "lon": 139.6503,
        "status": "decreasing",
        "severity": "high",
        "escalation_score": 6.4,
        "confidence": "high",
        "countries": ["JPN"],
    },
]


def get_country_ids(conn, iso3_codes):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, iso3
            FROM countries
            WHERE iso3 = ANY(%s)
            """,
            (iso3_codes,),
        )

        rows = cur.fetchall()

    countries = {row[1]: row[0] for row in rows}

    missing = set(iso3_codes) - set(countries)

    if missing:
        raise RuntimeError(
            f"Countries not found in database: {sorted(missing)}"
        )

    return countries


def seed_events():
    now = datetime.now(timezone.utc)

    with get_connection() as conn:
        country_cache = {}

        for data in EVENTS:
            event_id = uuid4()
            version_id = uuid4()

            country_ids = get_country_ids(
                conn,
                data["countries"],
            )

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO events (
                        id,
                        created_at,
                        updated_at,
                        first_detected_at,
                        last_evidence_at
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        event_id,
                        now,
                        now,
                        now,
                        now,
                    ),
                )

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
                        analyst_summary,
                        location,
                        location_precision,
                        time_start,
                        time_precision,
                        status,
                        severity,
                        escalation_score,
                        confidence,
                        created_at
                    )
                    VALUES (
                        %s,
                        %s,
                        1,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        ST_SetSRID(
                            ST_MakePoint(%s, %s),
                            4326
                        )::geography,
                        'approximate',
                        %s,
                        'day',
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        version_id,
                        event_id,
                        data["category"],
                        data["subtype"],
                        data["title"],
                        data["summary"],
                        data["analyst_summary"],
                        data["lon"],
                        data["lat"],
                        now,
                        data["status"],
                        data["severity"],
                        data["escalation_score"],
                        data["confidence"],
                        now,
                    ),
                )

                cur.execute(
                    """
                    UPDATE events
                    SET current_version_id = %s
                    WHERE id = %s
                    """,
                    (
                        version_id,
                        event_id,
                    ),
                )

                for country_id in country_ids.values():
                    cur.execute(
                        """
                        INSERT INTO event_countries (
                            event_id,
                            country_id,
                            relationship_type
                        )
                        VALUES (%s, %s, 'directly_affected')
                        """,
                        (
                            event_id,
                            country_id,
                        ),
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
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        event_id,
                        now,
                        "initial_detection",
                        "Detección inicial del acontecimiento.",
                        version_id,
                    ),
                )                

            print(
                f"Created event: {data['title']} "
                f"({event_id})"
            )

    print(f"\nSeed completed: {len(EVENTS)} events created.")


if __name__ == "__main__":
    seed_events()