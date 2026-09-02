from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

from backend.app.services.event_resolution import resolve_evidence_event


EVENT_ID = UUID("34a5118f-8b83-435e-948e-66bb69f13526")
REFERENCE_TIME = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)


class FakeCursor:
    def __init__(self, *, existing_event_id=None, current_severity=None):
        self.existing_event_id = existing_event_id
        self.current_severity = current_severity
        self.executed = []
        self.fetchone_calls = 0

    def execute(self, query, params=None):
        self.executed.append({"query": query, "params": params})

    def fetchone(self):
        self.fetchone_calls += 1
        if self.fetchone_calls == 1:
            if self.existing_event_id is None:
                return None
            return (self.existing_event_id,)
        if self.current_severity is None:
            return None
        return (self.current_severity,)


def _resolve(cur, *, severity):
    return resolve_evidence_event(
        cur,
        evidence_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        source_id="usgs",
        source_name="USGS",
        external_event_id="us7000test",
        title="Terremoto de prueba",
        summary="Resumen de prueba.",
        category="disaster",
        subtype="earthquake",
        severity=severity,
        confidence="high",
        time_start=REFERENCE_TIME,
        latitude=40.0,
        longitude=-3.0,
        canonical_data={"magnitude": 6.5},
        country_iso3="ESP",
    )


def test_new_event_uses_incoming_severity():
    cur = FakeCursor()

    result = _resolve(cur, severity="medium")

    assert result is not None
    insert = next(
        entry
        for entry in cur.executed
        if "INSERT INTO event_versions" in entry["query"]
    )
    assert insert["params"][14] == "medium"


def test_existing_event_same_severity_does_not_create_version():
    cur = FakeCursor(
        existing_event_id=EVENT_ID,
        current_severity="medium",
    )

    with patch(
        "backend.app.services.event_resolution._update_event_with_cursor"
    ) as update_event:
        result = _resolve(cur, severity="medium")

    assert result == EVENT_ID
    update_event.assert_not_called()
    assert not any(
        "INSERT INTO event_versions" in entry["query"]
        for entry in cur.executed
    )


def test_existing_event_higher_severity_creates_version():
    cur = FakeCursor(
        existing_event_id=EVENT_ID,
        current_severity="medium",
    )

    with patch(
        "backend.app.services.event_resolution._update_event_with_cursor"
    ) as update_event:
        result = _resolve(cur, severity="high")

    assert result == EVENT_ID
    update_event.assert_called_once()
    update = update_event.call_args.kwargs["update"]
    assert update.severity == "high"
    assert update.update_type == "severity_change"


def test_existing_event_lower_incoming_severity_does_not_downgrade():
    cur = FakeCursor(
        existing_event_id=EVENT_ID,
        current_severity="high",
    )

    with patch(
        "backend.app.services.event_resolution._update_event_with_cursor"
    ) as update_event:
        result = _resolve(cur, severity="medium")

    assert result == EVENT_ID
    update_event.assert_not_called()
