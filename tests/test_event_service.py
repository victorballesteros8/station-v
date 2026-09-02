from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

import pytest

from backend.app.schemas.events import EventUpdate
from backend.app.services.event_service import (
    VALID_UPDATE_TYPES,
    update_event,
)


REFERENCE_TIME = datetime(
    2026,
    8,
    28,
    12,
    0,
    tzinfo=timezone.utc,
)


EVENT_ID = UUID("34a5118f-8b83-435e-948e-66bb69f13526")
CURRENT_VERSION_ID = UUID("11111111-1111-1111-1111-111111111111")


class FakeCursor:
    def __init__(self, current_event):
        self.current_event = current_event
        self.executed = []
        self.fetchone_calls = 0

    def execute(self, query, params=None):
        self.executed.append(
            {
                "query": query,
                "params": params,
            }
        )

    def fetchone(self):
        self.fetchone_calls += 1
        return self.current_event

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, current_event):
        self.cursor_instance = FakeCursor(current_event)
        self.commit_calls = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commit_calls += 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def make_current_event(
    *,
    version=1,
    category="border_tension",
    subtype="armed_border_clash",
    title="Enfrentamientos fronterizos",
    summary="Resumen original.",
    analyst_summary="Valoración original.",
    status="active",
    severity="high",
    escalation_score=7.8,
    confidence="high",
):
    return (
        EVENT_ID,
        CURRENT_VERSION_ID,
        version,
        category,
        subtype,
        title,
        summary,
        analyst_summary,
        None,  # location
        "approximate",  # location_precision
        None,  # region
        None,  # place
        REFERENCE_TIME,  # time_start
        None,  # time_end
        "day",  # time_precision
        status,
        severity,
        escalation_score,
        confidence,
        None,  # confidence_score_internal
        None,  # canonical_data
        None,  # human_impact
        None,  # material_impact
    )


def get_queries(connection):
    return [
        entry["query"]
        for entry in connection.cursor_instance.executed
    ]


def test_valid_update_types_are_defined():
    assert VALID_UPDATE_TYPES == {
        "general_update",
        "status_change",
        "severity_change",
        "new_evidence",
        "occurrence",
    }


def test_update_event_creates_new_version_and_timeline_entry():
    connection = FakeConnection(make_current_event(version=1))

    update = EventUpdate(
        severity="critical",
        confidence="high",
        update_type="severity_change",
        description="La valoración de severidad aumenta.",
    )

    with patch(
        "backend.app.services.event_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value = connection

        result = update_event(EVENT_ID, update)

    assert result["event_id"] == EVENT_ID
    assert result["version"] == 2
    assert result["update_type"] == "severity_change"
    assert result["description"] == (
        "La valoración de severidad aumenta."
    )

    queries = get_queries(connection)

    assert any(
        "SELECT" in query
        and "event_versions" in query
        and "FOR UPDATE" in query
        for query in queries
    )

    assert any(
        "INSERT INTO event_versions" in query
        for query in queries
    )

    assert any(
        "UPDATE events" in query
        for query in queries
    )

    assert any(
        "INSERT INTO event_timeline" in query
        for query in queries
    )

    assert connection.commit_calls == 1


def test_update_event_preserves_unchanged_fields():
    connection = FakeConnection(
        make_current_event(
            version=3,
            category="military_activity",
            subtype="military_exercise",
            title="Ejercicio militar",
            summary="Resumen existente.",
            analyst_summary="Análisis existente.",
            status="stable",
            severity="low",
            escalation_score=None,
            confidence="high",
        )
    )

    update = EventUpdate(
        title="Nuevo título",
        update_type="general_update",
        description="Actualización informativa.",
    )

    with patch(
        "backend.app.services.event_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value = connection

        result = update_event(EVENT_ID, update)

    assert result["version"] == 4

    insert = next(
        entry
        for entry in connection.cursor_instance.executed
        if "INSERT INTO event_versions" in entry["query"]
    )

    params = insert["params"]

    assert params[2] == 4
    assert params[3] == "military_activity"
    assert params[4] == "military_exercise"
    assert params[5] == "Nuevo título"
    assert params[6] == "Resumen existente."
    assert params[7] == "Análisis existente."
    assert params[15] == "stable"
    assert params[16] == "low"
    assert params[17] is None
    assert params[18] == "high"


def test_occurrence_creates_timeline_entry():
    connection = FakeConnection(make_current_event(version=2))

    update = EventUpdate(
        update_type="occurrence",
        description="Nueva ocurrencia del mismo episodio.",
    )

    with patch(
        "backend.app.services.event_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value = connection

        result = update_event(EVENT_ID, update)

    assert result["version"] == 3

    timeline = next(
        entry
        for entry in connection.cursor_instance.executed
        if "INSERT INTO event_timeline" in entry["query"]
    )

    assert timeline["params"][0] == EVENT_ID
    assert timeline["params"][2] == "occurrence"
    assert timeline["params"][3] == (
        "Nueva ocurrencia del mismo episodio."
    )


def test_invalid_update_type_is_rejected():
    update = EventUpdate(
        update_type="invalid_type",
    )

    with pytest.raises(ValueError, match="Invalid update_type"):
        update_event(EVENT_ID, update)


def test_unknown_event_is_rejected():
    connection = FakeConnection(None)

    update = EventUpdate(
        update_type="general_update",
        description="Actualización.",
    )

    with patch(
        "backend.app.services.event_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value = connection

        with pytest.raises(
            LookupError,
            match="Event not found",
        ):
            update_event(EVENT_ID, update)


def test_update_event_uses_next_version_number():
    connection = FakeConnection(make_current_event(version=7))

    update = EventUpdate(
        status="decreasing",
        update_type="status_change",
        description="El evento muestra signos de disminución.",
    )

    with patch(
        "backend.app.services.event_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value = connection

        result = update_event(EVENT_ID, update)

    assert result["version"] == 8


def test_update_event_updates_current_version():
    connection = FakeConnection(make_current_event(version=1))

    update = EventUpdate(
        update_type="general_update",
    )

    with patch(
        "backend.app.services.event_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value = connection

        update_event(EVENT_ID, update)

    update_query = next(
        entry
        for entry in connection.cursor_instance.executed
        if "UPDATE events" in entry["query"]
    )

    assert update_query["params"][0] != CURRENT_VERSION_ID
    assert update_query["params"][2] == EVENT_ID
    assert connection.commit_calls == 1
