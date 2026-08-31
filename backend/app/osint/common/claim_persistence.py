from __future__ import annotations

from typing import Any

from backend.app.db import get_connection


def _persist_claim(
    cur: Any,
    evidence_id: str,
    claim: Any,
) -> str:
    """Persist a source-built claim using the shared claims contract."""
    cur.execute(
        """
        INSERT INTO claims (
            evidence_id,
            claim_type,
            statement,
            assertion_status,
            confidence
        )
        VALUES (
            %(evidence_id)s,
            %(claim_type)s,
            %(statement)s,
            %(assertion_status)s,
            %(confidence)s
        )
        ON CONFLICT (evidence_id, claim_type)
        DO UPDATE SET
            statement = EXCLUDED.statement,
            assertion_status = EXCLUDED.assertion_status,
            confidence = EXCLUDED.confidence,
            updated_at = now()
        RETURNING id
        """,
        {
            "evidence_id": evidence_id,
            "claim_type": claim.claim_type,
            "statement": claim.statement,
            "assertion_status": claim.assertion_status,
            "confidence": claim.confidence,
        },
    )

    return str(cur.fetchone()[0])


def persist_claim(
    evidence_id: str,
    claim: Any,
) -> str:
    """Persist a claim in its own transaction."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            claim_id = _persist_claim(
                cur,
                evidence_id,
                claim,
            )

        conn.commit()

    return claim_id
