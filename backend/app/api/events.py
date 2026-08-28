from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.app.db import get_connection
from backend.app.schemas.events import EventDetail, EventMapItem

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
)


def build_event(row, countries):
    return {
        "id": row[0],
        "category": row[1],
        "subtype": row[2],
        "title": row[3],
        "status": row[4],
        "severity": row[5],
        "escalation_score": row[6],
        "confidence": row[7],
        "location": (
            {
                "lat": row[8],
                "lon": row[9],
            }
            if row[8] is not None and row[9] is not None
            else None
        ),
        "countries": countries,
        "updated_at": row[10],
    }


@router.get("", response_model=list[EventMapItem])
def list_events():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    e.id,
                    ev.category,
                    ev.subtype,
                    ev.title,
                    ev.status,
                    ev.severity,
                    ev.escalation_score,
                    ev.confidence,
                    ST_Y(ev.location::geometry) AS lat,
                    ST_X(ev.location::geometry) AS lon,
                    e.updated_at
                FROM events e
                JOIN event_versions ev
                    ON ev.id = e.current_version_id
                ORDER BY e.updated_at DESC
                """
            )

            rows = cur.fetchall()

            events = []

            for row in rows:
                event_id = row[0]

                cur.execute(
                    """
                    SELECT
			c.id,
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
                        "id": country[0],
                        "iso2": country[1],
                        "name": country[2],
                    }
                    for country in cur.fetchall()
                ]

                events.append(build_event(row, countries))

    return events


@router.get("/{event_id}", response_model=EventDetail)
def get_event(event_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    e.id,
                    ev.category,
                    ev.subtype,
                    ev.title,
                    ev.status,
                    ev.severity,
                    ev.escalation_score,
                    ev.confidence,
                    ST_Y(ev.location::geometry) AS lat,
                    ST_X(ev.location::geometry) AS lon,
                    e.updated_at
                FROM events e
                JOIN event_versions ev
                    ON ev.id = e.current_version_id
                WHERE e.id = %s
                """,
                (event_id,),
            )

            row = cur.fetchone()

            if row is None:
                raise HTTPException(
                    status_code=404,
                    detail="Event not found",
                )

            cur.execute(
                """
                SELECT
                    c.id,
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
                    "id": country[0],
                    "iso2": country[1],
                    "name": country[2],
                }
                for country in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT
                    evi.id,
                    evi.title,
                    evi.url,
                    evi.published_at,
                    evi.evidence_type,
                    evi.source_role,
                    evi.relationship_to_event,
                    evi.evidence_quality,
                    s.id,
                    s.name,
                    s.tier,
                    s.source_class,
                    s.source_type,
                    s.reliability
                FROM evidence evi
                JOIN sources s
                    ON s.id = evi.source_id
                WHERE evi.event_id = %s
                ORDER BY evi.published_at DESC NULLS LAST,
                         evi.created_at DESC
                """,
                (event_id,),
            )

            evidence_rows = cur.fetchall()

            evidence = []

            for evidence_row in evidence_rows:
                evidence_id = evidence_row[0]

                cur.execute(
                    """
                    SELECT
                        claim_type,
                        statement,
                        assertion_status,
                        confidence
                    FROM claims
                    WHERE evidence_id = %s
                    ORDER BY created_at
                    """,
                    (evidence_id,),
                )

                claims = [
                    {
                        "claim_type": claim[0],
                        "statement": claim[1],
                        "assertion_status": claim[2],
                        "confidence": claim[3],
                    }
                    for claim in cur.fetchall()
                ]

                evidence.append(
                    {
                        "id": evidence_row[0],
                        "title": evidence_row[1],
                        "url": evidence_row[2],
                        "published_at": evidence_row[3],
                        "evidence_type": evidence_row[4],
                        "source_role": evidence_row[5],
                        "relationship_to_event": evidence_row[6],
                        "evidence_quality": evidence_row[7],
                        "source": {
                            "id": evidence_row[8],
                            "name": evidence_row[9],
                            "tier": evidence_row[10],
                            "source_class": evidence_row[11],
                            "source_type": evidence_row[12],
                            "reliability": evidence_row[13],
                        },
                        "claims": claims,
                    }
                )

    event = build_event(row, countries)
    event["evidence"] = evidence

    return event