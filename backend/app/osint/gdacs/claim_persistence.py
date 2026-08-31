from __future__ import annotations

from typing import Any

from backend.app.db import get_connection
from backend.app.osint.common.claim_persistence import (
    _persist_claim,
)
from backend.app.osint.gdacs.claim_builder import GDACSClaim


def _persist_gdacs_claim(
    cur: Any,
    evidence_id: str,
    claim: GDACSClaim,
) -> str:
    """Compatibility wrapper around the shared claim persistence layer."""
    return _persist_claim(
        cur,
        evidence_id,
        claim,
    )


def persist_gdacs_claim(
    evidence_id: str,
    claim: GDACSClaim,
) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            claim_id = _persist_gdacs_claim(
                cur,
                evidence_id,
                claim,
            )

        conn.commit()

    return claim_id
