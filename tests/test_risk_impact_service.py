from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from backend.app.services.risk_impact_service import (
    EARTHQUAKE_SUBINDICATOR_ID,
    assign_event_risk_impacts,
)


class FakeCursor:
    def __init__(self) -> None:
        self.queries: list[tuple[str, tuple]] = []
        self._fetchone_values: list[tuple | None] = []
        self._fetchall_values: list[list[tuple]] = []

    def execute(self, query: str, params=()) -> None:
        self.queries.append((query, params))

    def fetchone(self):
        if not self._fetchone_values:
            raise AssertionError("Unexpected fetchone()")
        return self._fetchone_values.pop(0)

    def fetchall(self):
        if not self._fetchall_values:
            raise AssertionError("Unexpected fetchall()")
        return self._fetchall_values.pop(0)


def test_earthquake_creates_risk_impact() -> None:
    event_id = str(uuid4())
    cur = FakeCursor()
    cur._fetchone_values = [
        ("disaster", "earthquake", "high"),
        None,
    ]
    cur._fetchall_values = [[(123,)]]

    result = assign_event_risk_impacts(cur, event_id)

    assert result == 1
    insert = [query for query, _ in cur.queries if "INSERT INTO risk_impacts" in query]
    assert len(insert) == 1
    params = cur.queries[-1][1]
    assert params == (event_id, 123, EARTHQUAKE_SUBINDICATOR_ID, 8.0, 1.0)


def test_earthquake_updates_existing_risk_impact() -> None:
    event_id = str(uuid4())
    impact_id = str(uuid4())
    cur = FakeCursor()
    cur._fetchone_values = [
        ("disaster", "earthquake", "critical"),
        (impact_id,),
    ]
    cur._fetchall_values = [[(456,)]]

    result = assign_event_risk_impacts(cur, event_id)

    assert result == 1
    update_queries = [
        (query, params)
        for query, params in cur.queries
        if "UPDATE risk_impacts" in query
    ]
    assert len(update_queries) == 1
    assert update_queries[0][1] == (15.0, 1.0, impact_id)


def test_non_earthquake_event_is_not_assigned() -> None:
    cur = FakeCursor()
    cur._fetchone_values = [("conflict_violence", "armed_clash", "high")]

    assert assign_event_risk_impacts(cur, str(uuid4())) == 0
    assert not any("risk_impacts" in query for query, _ in cur.queries)


def test_event_without_direct_country_is_not_assigned() -> None:
    cur = FakeCursor()
    cur._fetchone_values = [("disaster", "earthquake", "medium")]
    cur._fetchall_values = [[]]

    assert assign_event_risk_impacts(cur, str(uuid4())) == 0
    assert not any("INSERT INTO risk_impacts" in query for query, _ in cur.queries)
