from unittest.mock import MagicMock
from unittest.mock import patch

from backend.app.osint.common.claim_persistence import (
    _persist_claim,
    persist_claim,
)
from backend.app.osint.common.evidence_persistence import (
    upsert_evidence,
)


class _Claim:
    claim_type = "earthquake"
    statement = "Earthquake detected."
    assertion_status = "confirmed"
    confidence = "high"


def test_persist_claim_uses_shared_upsert_contract():
    cursor = MagicMock()
    cursor.fetchone.return_value = ("claim-id",)

    result = _persist_claim(
        cursor,
        "evidence-id",
        _Claim(),
    )

    assert result == "claim-id"
    cursor.execute.assert_called_once()
    params = cursor.execute.call_args.args[1]
    assert params == {
        "evidence_id": "evidence-id",
        "claim_type": "earthquake",
        "statement": "Earthquake detected.",
        "assertion_status": "confirmed",
        "confidence": "high",
    }


def test_persist_claim_manages_its_own_transaction():
    with patch(
        "backend.app.osint.common.claim_persistence.get_connection"
    ) as mock_connection:
        connection = mock_connection.return_value.__enter__.return_value
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = ("claim-id",)

        result = persist_claim(
            "evidence-id",
            _Claim(),
        )

    assert result == "claim-id"
    connection.commit.assert_called_once()


def test_upsert_evidence_uses_shared_persistence_contract():
    cursor = MagicMock()
    cursor.fetchone.return_value = ("evidence-id",)

    values = {
        "source_id": "source-id",
        "external_id": "event-id",
        "published_at": None,
        "retrieved_at": None,
        "title": "Example event",
        "url": "https://example.com/event",
        "content_type": "application/json",
        "evidence_type": "measurement",
        "source_role": "detection",
        "independence_group": "example",
        "evidence_quality": 100.0,
        "first_seen_at": None,
        "last_seen_at": None,
        "structured_data": None,
    }

    result = upsert_evidence(cursor, values)

    assert result == "evidence-id"
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == values
