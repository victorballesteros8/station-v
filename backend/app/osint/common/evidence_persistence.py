from __future__ import annotations

from typing import Any


def upsert_evidence(
    cur: Any,
    values: dict[str, Any],
) -> str:
    """Upsert Evidence using the shared database contract.

    Source adapters own normalization and semantic field selection; this
    function owns only the persistence semantics and SQL.
    """
    cur.execute(
        """
        INSERT INTO evidence (
            source_id,
            external_id,
            external_episode_id,
            published_at,
            retrieved_at,
            title,
            url,
            content_type,
            evidence_type,
            source_role,
            independence_group,
            evidence_quality,
            first_seen_at,
            last_seen_at,
            structured_data
        )
        VALUES (
            %(source_id)s,
            %(external_id)s,
            %(external_episode_id)s,
            %(published_at)s,
            %(retrieved_at)s,
            %(title)s,
            %(url)s,
            %(content_type)s,
            %(evidence_type)s,
            %(source_role)s,
            %(independence_group)s,
            %(evidence_quality)s,
            %(first_seen_at)s,
            %(last_seen_at)s,
            %(structured_data)s
        )
        ON CONFLICT (
            source_id,
            external_id,
            (COALESCE(external_episode_id, ''))
        )
        DO UPDATE SET
            published_at = EXCLUDED.published_at,
            retrieved_at = EXCLUDED.retrieved_at,
            title = EXCLUDED.title,
            url = EXCLUDED.url,
            content_type = EXCLUDED.content_type,
            evidence_type = EXCLUDED.evidence_type,
            source_role = EXCLUDED.source_role,
            independence_group = EXCLUDED.independence_group,
            evidence_quality = EXCLUDED.evidence_quality,
            last_seen_at = EXCLUDED.last_seen_at,
            structured_data = EXCLUDED.structured_data,
            updated_at = now()
        RETURNING id
        """,
        values,
    )

    return str(cur.fetchone()[0])
