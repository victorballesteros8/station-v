from __future__ import annotations

from typing import Any

from backend.app.db import get_connection
from backend.app.osint.usgs.claim_builder import USGSClaim


def _persist_usgs_claim(
    cur: Any,
    evidence_id: str,
    claim: USGSClaim,
) -> str:
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


def persist_usgs_claim(
    evidence_id: str,
    claim: USGSClaim,
) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            claim_id = _persist_usgs_claim(
                cur,
                evidence_id,
                claim,
            )

        conn.commit()

    return claim_id