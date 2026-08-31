from __future__ import annotations

from typing import Any

from backend.app.db import get_connection
from backend.app.osint.common.claim_persistence import (
    _persist_claim,
)
from backend.app.osint.usgs.claim_builder import USGSClaim


def _persist_usgs_claim(
    cur: Any,
    evidence_id: str,
    claim: USGSClaim,
) -> str:
    """Compatibility wrapper around the shared claim persistence layer."""
    return _persist_claim(
        cur,
        evidence_id,
        claim,
    )


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
