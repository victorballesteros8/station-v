from datetime import datetime, timezone
from uuid import uuid4

from backend.app.db import get_connection


DEV_SOURCE_NAMES = {
    "Reuters — STATION V DEV",
    "Associated Press — STATION V DEV",
    "STATION V Synthetic OSINT — DEV",
}


SOURCES = [
    {
        "name": "Reuters — STATION V DEV",
        "tier": "T1",
        "source_class": "news_agency",
        "source_type": "wire_service",
        "geographic_scope": "global",
        "reliability": 95,
        "detection_capability": 90,
        "corroboration_capability": 95,
        "independence_group": "reuters",
        "access_method": "web",
        "status": "active",
    },
    {
        "name": "Associated Press — STATION V DEV",
        "tier": "T1",
        "source_class": "news_agency",
        "source_type": "wire_service",
        "geographic_scope": "global",
        "reliability": 94,
        "detection_capability": 88,
        "corroboration_capability": 94,
        "independence_group": "ap",
        "access_method": "web",
        "status": "active",
    },
    {
        "name": "STATION V Synthetic OSINT — DEV",
        "tier": "T2",
        "source_class": "osint",
        "source_type": "synthetic",
        "geographic_scope": "global",
        "reliability": 70,
        "detection_capability": 75,
        "corroboration_capability": 60,
        "independence_group": "station-v-dev",
        "access_method": "internal",
        "status": "active",
    },
]


EVIDENCE = [
    {
        "event_title": "Enfrentamientos fronterizos",
        "source_name": "Reuters — STATION V DEV",
        "title": "Border clashes reported between Indian and Pakistani forces",
        "author": "STATION V DEV",
        "language": "en",
        "content_type": "news_report",
        "evidence_type": "reported_event",
        "source_role": "detection",
        "relationship_to_event": "direct",
        "evidence_quality": 92,
        "claim_type": "event_occurrence",
        "statement": (
            "Reuters reports that armed clashes occurred along the "
            "India-Pakistan border."
        ),
        "assertion_status": "reported",
        "confidence": "high",
    },
    {
        "event_title": "Manifestaciones masivas",
        "source_name": "Associated Press — STATION V DEV",
        "title": "Large demonstrations reported in Cairo",
        "author": "STATION V DEV",
        "language": "en",
        "content_type": "news_report",
        "evidence_type": "reported_event",
        "source_role": "detection",
        "relationship_to_event": "direct",
        "evidence_quality": 88,
        "claim_type": "event_occurrence",
        "statement": (
            "Large demonstrations were reported in Cairo in the "
            "synthetic development scenario."
        ),
        "assertion_status": "reported",
        "confidence": "medium",
    },
    {
        "event_title": "Ejercicio militar",
        "source_name": "STATION V Synthetic OSINT — DEV",
        "title": "Military exercise detected near Japan",
        "author": "STATION V DEV",
        "language": "en",
        "content_type": "osint_note",
        "evidence_type": "osint_observation",
        "source_role": "detection",
        "relationship_to_event": "direct",
        "evidence_quality": 70,
        "claim_type": "military_activity",
        "statement": (
            "A military exercise is represented in the synthetic "
            "development dataset."
        ),
        "assertion_status": "inferred",
        "confidence": "medium",
    },
    {
        "event_title": "Ataque contra infraestructura crítica",
        "source_name": "Reuters — STATION V DEV",
        "title": "Critical infrastructure attack reported in Ukraine",
        "author": "STATION V DEV",
        "language": "en",
        "content_type": "news_report",
        "evidence_type": "reported_event",
        "source_role": "detection",
        "relationship_to_event": "direct",
        "evidence_quality": 94,
        "claim_type": "event_occurrence",
        "statement": (
            "Reuters reports an attack affecting critical infrastructure "
            "in Ukraine."
        ),
        "assertion_status": "reported",
        "confidence": "high",
    },
    {
        "event_title": "Terremoto",
        "source_name": "Associated Press — STATION V DEV",
        "title": "Earthquake reported near Tokyo",
        "author": "STATION V DEV",
        "language": "en",
        "content_type": "news_report",
        "evidence_type": "reported_event",
        "source_role": "detection",
        "relationship_to_event": "direct",
        "evidence_quality": 91,
        "claim_type": "event_occurrence",
        "statement": (
            "An earthquake is reported near Tokyo in the synthetic "
            "development scenario."
        ),
        "assertion_status": "reported",
        "confidence": "high",
    },
]


def clear_dev_data(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM sources
            WHERE name = ANY(%s)
            """,
            (list(DEV_SOURCE_NAMES),),
        )

    print("Cleared previous STATION V development OSINT data.")


def seed_sources(conn):
    source_ids = {}

    with conn.cursor() as cur:
        for source in SOURCES:
            source_id = uuid4()

            cur.execute(
                """
                INSERT INTO sources (
                    id,
                    name,
                    tier,
                    source_class,
                    source_type,
                    geographic_scope,
                    reliability,
                    detection_capability,
                    corroboration_capability,
                    independence_group,
                    access_method,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    source_id,
                    source["name"],
                    source["tier"],
                    source["source_class"],
                    source["source_type"],
                    source["geographic_scope"],
                    source["reliability"],
                    source["detection_capability"],
                    source["corroboration_capability"],
                    source["independence_group"],
                    source["access_method"],
                    source["status"],
                ),
            )

            source_ids[source["name"]] = source_id

    return source_ids


def get_event_id(conn, title):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.id
            FROM events e
            JOIN event_versions ev
                ON ev.id = e.current_version_id
            WHERE ev.title = %s
            """,
            (title,),
        )

        row = cur.fetchone()

    if row is None:
        raise RuntimeError(f"Event not found: {title}")

    return row[0]


def seed_evidence(conn, source_ids):
    now = datetime.now(timezone.utc)

    for item in EVIDENCE:
        event_id = get_event_id(conn, item["event_title"])
        source_id = source_ids[item["source_name"]]
        evidence_id = uuid4()
        claim_id = uuid4()

        source = next(
            source
            for source in SOURCES
            if source["name"] == item["source_name"]
        )

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO evidence (
                    id,
                    source_id,
                    event_id,
                    published_at,
                    retrieved_at,
                    title,
                    author,
                    language,
                    content_type,
                    evidence_type,
                    source_role,
                    relationship_to_event,
                    independence_group,
                    evidence_quality,
                    first_seen_at,
                    last_seen_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    evidence_id,
                    source_id,
                    event_id,
                    now,
                    now,
                    item["title"],
                    item["author"],
                    item["language"],
                    item["content_type"],
                    item["evidence_type"],
                    item["source_role"],
                    item["relationship_to_event"],
                    source["independence_group"],
                    item["evidence_quality"],
                    now,
                    now,
                ),
            )

            cur.execute(
                """
                INSERT INTO claims (
                    id,
                    evidence_id,
                    claim_type,
                    statement,
                    assertion_status,
                    confidence
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    claim_id,
                    evidence_id,
                    item["claim_type"],
                    item["statement"],
                    item["assertion_status"],
                    item["confidence"],
                ),
            )

        print(
            f"Created evidence for: {item['event_title']}"
        )


def main():
    with get_connection() as conn:
        clear_dev_data(conn)
        source_ids = seed_sources(conn)
        seed_evidence(conn, source_ids)

    print(
        f"\nOSINT seed completed: "
        f"{len(SOURCES)} sources, "
        f"{len(EVIDENCE)} evidence records, "
        f"{len(EVIDENCE)} claims."
    )


if __name__ == "__main__":
    main()