from fastapi import APIRouter, Query

from backend.app.db import get_connection


router = APIRouter(
    prefix="/api/v1/search",
    tags=["search"],
)


COUNTRY_SEARCH_ALIASES = {
    "españa": "ES",
    "espana": "ES",
    "spain": "ES",

    "francia": "FR",
    "france": "FR",

    "alemania": "DE",
    "germany": "DE",

    "reino unido": "GB",
    "united kingdom": "GB",
    "uk": "GB",
    "gran bretaña": "GB",
    "gran bretana": "GB",

    "estados unidos": "US",
    "united states": "US",
    "usa": "US",
    "us": "US",

    "ucrania": "UA",
    "ukraine": "UA",

    "india": "IN",

    "pakistán": "PK",
    "pakistan": "PK",

    "egipto": "EG",
    "egypt": "EG",

    "japón": "JP",
    "japon": "JP",
    "japan": "JP",

    "china": "CN",

    "rusia": "RU",
    "russia": "RU",

    "irán": "IR",
    "iran": "IR",

    "israel": "IL",

    "turquía": "TR",
    "turquia": "TR",
    "turkey": "TR",
}


@router.get("")
def search(
    q: str = Query(..., min_length=1, max_length=100),
):
    query = q.strip()
    normalized_query = query.casefold()
    search_term = f"%{query}%"

    country_alias = COUNTRY_SEARCH_ALIASES.get(
        normalized_query
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            if country_alias:
                cur.execute(
                    """
                    SELECT
                        c.id,
                        c.iso2,
                        c.name
                    FROM countries c
                    WHERE c.iso2 = %s
                    LIMIT 10
                    """,
                    (country_alias,),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        c.id,
                        c.iso2,
                        c.name
                    FROM countries c
                    WHERE c.name ILIKE %s
                       OR c.iso2 ILIKE %s
                    ORDER BY
                        CASE
                            WHEN c.iso2 ILIKE %s
                            THEN 0
                            ELSE 1
                        END,
                        c.name
                    LIMIT 10
                    """,
                    (
                        search_term,
                        search_term,
                        query,
                    ),
                )

            countries = [
                {
                    "id": int(row[0]),
                    "iso2": row[1],
                    "name": row[2],
                }
                for row in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT
                    e.id,
                    ev.title,
                    ev.category,
                    ev.severity,
                    ev.escalation_score
                FROM events e
                JOIN event_versions ev
                    ON ev.id = e.current_version_id
                WHERE ev.title ILIKE %s
                   OR ev.summary ILIKE %s
                   OR ev.category ILIKE %s
                ORDER BY
                    ev.time_start DESC NULLS LAST,
                    ev.created_at DESC
                LIMIT 10
                """,
                (
                    search_term,
                    search_term,
                    search_term,
                ),
            )

            events = [
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
                }
                for row in cur.fetchall()
            ]

    return {
        "query": query,
        "countries": countries,
        "events": events,
    }