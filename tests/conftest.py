import uuid

import pytest

from backend.app.db import get_connection


@pytest.fixture
def test_event_id():
    event_id = uuid.uuid4()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (
                    id,
                    first_detected_at
                )
                VALUES (
                    %s,
                    NOW()
                )
                """,
                (event_id,),
            )

            cur.execute(
                """
                INSERT INTO event_versions (
                    event_id,
                    version,
                    category,
                    subtype,
                    title,
                    summary,
                    analyst_summary,
                    status,
                    severity,
                    escalation_score,
                    confidence
                )
                VALUES (
                    %s,
                    1,
                    'border_tension',
                    'armed_border_clash',
                    'Evento de prueba',
                    'Resumen del evento de prueba.',
                    'Análisis del evento de prueba.',
                    'active',
                    'high',
                    7.0,
                    'high'
                )
                RETURNING id
                """,
                (event_id,),
            )

            version_id = cur.fetchone()[0]

            cur.execute(
                """
                UPDATE events
                SET current_version_id = %s
                WHERE id = %s
                """,
                (version_id, event_id),
            )

    yield event_id

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM events
                WHERE id = %s
                """,
                (event_id,),
            )