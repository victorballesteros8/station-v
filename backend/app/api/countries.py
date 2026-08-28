from fastapi import APIRouter

from backend.app.db import get_connection


router = APIRouter(prefix="/api/countries", tags=["countries"])


@router.get("")
def list_countries():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, iso2, iso3, name, status
                FROM countries
                ORDER BY name
                """
            )

            rows = cur.fetchall()

    return {
        "items": [
            {
                "id": row[0],
                "iso2": row[1],
                "iso3": row[2],
                "name": row[3],
                "status": row[4],
            }
            for row in rows
        ],
        "total": len(rows),
    }