from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from backend.app.osint.usgs.event_backfill import backfill_usgs_events


def _mock_connection(cursor):
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor
    return connection


def test_backfill_usgs_events_resolves_pending_evidence(monkeypatch):
    evidence_id = uuid4()
    source_id = uuid4()
    structured_data = {
        "provider": "USGS",
        "place": "8 km W of Cobb, CA",
        "latitude": 38.8343,
        "longitude": -122.8123,
        "depth": 2.01,
        "magnitude": 1.04,
        "event_time": "2026-08-30T17:04:32.090000+00:00",
    }

    cursor = MagicMock()
    cursor.fetchall.return_value = [
        (
            evidence_id,
            source_id,
            "nc75427292",
            "8 km W of Cobb, CA",
            datetime(2026, 8, 30, 17, 4, 32, 90000, tzinfo=timezone.utc),
            structured_data,
        )
    ]

    connection = _mock_connection(cursor)
    monkeypatch.setattr(
        "backend.app.osint.usgs.event_backfill.get_connection",
        MagicMock(return_value=connection),
    )

    resolve = MagicMock(return_value=uuid4())
    monkeypatch.setattr(
        "backend.app.osint.usgs.event_backfill.resolve_evidence_event",
        resolve,
    )

    assert backfill_usgs_events() == 1
    resolve.assert_called_once()
    kwargs = resolve.call_args.kwargs
    assert kwargs["evidence_id"] == str(evidence_id)
    assert kwargs["source_id"] == str(source_id)
    assert kwargs["external_event_id"] == "nc75427292"
    assert kwargs["subtype"] == "earthquake"
    assert kwargs["latitude"] == 38.8343
    assert kwargs["longitude"] == -122.8123
    connection.commit.assert_called_once()


def test_backfill_usgs_events_is_empty_when_no_pending_evidence(monkeypatch):
    cursor = MagicMock()
    cursor.fetchall.return_value = []

    connection = _mock_connection(cursor)
    monkeypatch.setattr(
        "backend.app.osint.usgs.event_backfill.get_connection",
        MagicMock(return_value=connection),
    )

    resolve = MagicMock()
    monkeypatch.setattr(
        "backend.app.osint.usgs.event_backfill.resolve_evidence_event",
        resolve,
    )

    assert backfill_usgs_events() == 0
    resolve.assert_not_called()
    connection.commit.assert_called_once()
