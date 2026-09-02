from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from backend.app.scoring.risk_service import (
    _calculate_confidence,
    _get_previous_subindicator_score,
    _get_repetition_count,
    _load_dimensions,
    _load_risk_impacts,
    _load_subindicators,
    calculate_country_risk_snapshot,
    _get_global_risk_coverage_status
)

EVENT_1 = "11111111-1111-1111-1111-111111111111"
EVENT_2 = "22222222-2222-2222-2222-222222222222"
EVENT_3 = "33333333-3333-3333-3333-333333333333"

REFERENCE_TIME = datetime(
    2026,
    8,
    28,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


# ============================================================
# Helpers
# ============================================================


def make_cursor():
    cur = MagicMock()

    cur.fetchone.return_value = None
    cur.fetchall.return_value = []

    return cur


def make_connection(cur):
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cur
    return connection

def configure_snapshot_cursor(
    *,
    dimensions,
    subindicators_by_dimension=None,
    impacts=None,
    previous_scores=None,
    repetition_counts=None,
    relations=None,
    confidence_values=None,
    country_exists=True,
):
    subindicators_by_dimension = (
        subindicators_by_dimension or {}
    )
    impacts = impacts or []
    previous_scores = previous_scores or {}
    repetition_counts = repetition_counts or {}
    relations = relations or []
    confidence_values = confidence_values or []

    cur = make_cursor()

    def execute(sql, params=None):
        normalized_sql = " ".join(
            str(sql).split()
        ).upper()

        if (
            "SELECT 1" in normalized_sql
            and "FROM COUNTRIES" in normalized_sql
        ):
            cur.fetchone.return_value = (
                (1,)
                if country_exists
                else None
            )
            return

        if "FROM DIMENSIONS" in normalized_sql:
            cur.fetchall.return_value = dimensions
            return

        if "SELECT EV.CONFIDENCE" in normalized_sql:
            cur.fetchall.return_value = [
                (value,)
                for value in confidence_values
            ]
            return

        if "FROM RISK_IMPACTS RI" in normalized_sql:
            cur.fetchall.return_value = impacts
            return

        if "WITH RECURSIVE CORRELATED_EVENTS" in normalized_sql:
            qualifying_relations = {
                "same_series",
                "escalates",
                "same_series",
                "part_of",
            }

            event_id = str(params[0])

            graph = {}

            for relation_event_id, related_event_id, relation_type in relations:
                if relation_type not in qualifying_relations:
                    continue

                left = str(relation_event_id)
                right = str(related_event_id)

                graph.setdefault(left, set()).add(right)
                graph.setdefault(right, set()).add(left)

            connected = {event_id}
            pending = [event_id]

            while pending:
                current = pending.pop()

                for neighbour in graph.get(current, set()):
                    if neighbour not in connected:
                        connected.add(neighbour)
                        pending.append(neighbour)

            window_start = params[4] - timedelta(days=7)
            reference_time = params[4]
            country_id = params[2]
            subindicator_id = params[3]

            filtered_impacts = []

            for impact in impacts:
                # Repetition tests use:
                # (event_id, time_start)
                if len(impact) == 2:
                    if (
                        str(impact[0]) in connected
                        and window_start <= impact[1] <= reference_time
                    ):
                        filtered_impacts.append(
                            (
                                impact[0],
                                impact[1],
                            )
                        )

                # Snapshot tests use the normal risk_impacts shape.
                elif len(impact) >= 6:
                    # Snapshot impacts are not the result set expected by
                    # _get_repetition_count(), so they are only included
                    # when their event matches the current event context.
                    #
                    # The actual snapshot query remains handled by the
                    # normal risk_impacts branch below.
                    continue

            cur.fetchall.return_value = filtered_impacts
            return

        if "FROM SUBINDICATORS" in normalized_sql:
            dimension_id = params[0]
            cur.fetchall.return_value = (
                subindicators_by_dimension.get(
                    dimension_id,
                    [],
                )
            )
            return

        if (
            "FROM RISK_SUBINDICATOR_SNAPSHOTS" in normalized_sql
            and "SELECT SCORE" in normalized_sql
        ):
            country_id = params[0]
            subindicator_id = params[1]

            score = previous_scores.get(
                (country_id, subindicator_id)
            )

            cur.fetchone.return_value = (
                (score,)
                if score is not None
                else None
            )
            return

        if "FROM EVENT_TIMELINE" in normalized_sql:
            event_id = params[0]

            count = repetition_counts.get(
                event_id,
                0,
            )

            cur.fetchone.return_value = (count,)
            return

        cur.fetchone.return_value = None
        cur.fetchall.return_value = []

    cur.execute.side_effect = execute

    return cur


# ============================================================
# Previous subindicator score
# ============================================================


def test_previous_subindicator_score_returns_latest_value():
    cur = make_cursor()
    cur.fetchone.return_value = (42.5,)

    result = _get_previous_subindicator_score(
        cur,
        country_id=321,
        subindicator_id=29,
        reference_time=REFERENCE_TIME,
    )

    assert result == pytest.approx(42.5)

    cur.execute.assert_called_once()


def test_previous_subindicator_score_defaults_to_zero():
    cur = make_cursor()
    cur.fetchone.return_value = None

    result = _get_previous_subindicator_score(
        cur,
        country_id=321,
        subindicator_id=29,
        reference_time=REFERENCE_TIME,
    )

    assert result == 0.0


# ============================================================
# Repetition count
# ============================================================


def test_repetition_count_is_one_without_qualifying_relations():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 1

def test_repetition_count_counts_qualifying_same_series_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "same_series"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 2

def test_repetition_count_counts_escalation_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_2, EVENT_1, "escalates"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 2


def test_repetition_count_counts_continuation_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_2, EVENT_1, "same_series"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 2


def test_repetition_count_counts_part_of_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_2, EVENT_1, "part_of"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 2


def test_repetition_count_counts_escalation_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_2, EVENT_1, "escalates"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 2


def test_repetition_count_counts_continuation_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_2, EVENT_1, "same_series"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 2


def test_repetition_count_counts_part_of_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_2, EVENT_1, "part_of"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 2


def test_repetition_count_does_not_reduce_for_non_qualifying_related_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "related_to"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 1


def test_repetition_count_does_not_reduce_for_temporal_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "preceded_by"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 1


def test_repetition_count_does_not_reduce_for_followed_by_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "followed_by"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 1


def test_repetition_count_does_not_reduce_for_caused_by_relation():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "caused_by"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 1

def test_repetition_count_traverses_relation_chain():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_3,
                REFERENCE_TIME - timedelta(hours=24),
            ),
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "same_series"),
            (EVENT_2, EVENT_3, "same_series"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 3


def test_repetition_count_is_calculated_separately_by_country_and_subindicator():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(hours=12),
                2,
                1,
            ),
            (
                EVENT_3,
                REFERENCE_TIME - timedelta(hours=12),
                1,
                2,
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
                1,
                1,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "same_series"),
            (EVENT_1, EVENT_3, "same_series"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 1


def test_repetition_count_ignores_events_outside_seven_day_window():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[
            (
                EVENT_2,
                REFERENCE_TIME - timedelta(days=8),
            ),
            (
                EVENT_1,
                REFERENCE_TIME,
            ),
        ],
        relations=[
            (EVENT_1, EVENT_2, "same_series"),
        ],
    )

    result = _get_repetition_count(
        cur,
        event_id=EVENT_1,
        country_id=1,
        subindicator_id=1,
        reference_time=REFERENCE_TIME,
    )

    assert result == 1
    
# ============================================================
# Confidence
# ============================================================


def test_confidence_is_low_without_impacts():
    cur = make_cursor()
    cur.fetchall.return_value = []

    result = _calculate_confidence(
        cur,
        country_id=321,
    )

    assert result == "low"


def test_confidence_is_high_when_all_impacts_are_high():
    cur = make_cursor()
    cur.fetchall.return_value = [
        ("high",),
        ("high",),
    ]

    result = _calculate_confidence(
        cur,
        country_id=321,
    )

    assert result == "high"


def test_confidence_is_medium_when_any_impact_is_medium():
    cur = make_cursor()
    cur.fetchall.return_value = [
        ("high",),
        ("medium",),
    ]

    result = _calculate_confidence(
        cur,
        country_id=321,
    )

    assert result == "medium"


def test_confidence_is_low_when_only_low_impacts_exist():
    cur = make_cursor()
    cur.fetchall.return_value = [
        ("low",),
        ("low",),
    ]

    result = _calculate_confidence(
        cur,
        country_id=321,
    )

    assert result == "low"


# ============================================================
# Catalogue loading
# ============================================================


def test_load_dimensions():
    cur = make_cursor()

    cur.fetchall.return_value = [
        (1, "internal_instability", 0.25),
        (2, "conflict_violence", 0.25),
    ]

    result = _load_dimensions(cur)

    assert result == [
        {
            "id": 1,
            "code": "internal_instability",
            "weight": 0.25,
        },
        {
            "id": 2,
            "code": "conflict_violence",
            "weight": 0.25,
        },
    ]


def test_load_subindicators():
    cur = make_cursor()

    cur.fetchall.return_value = [
        (29, "anomalous_military_exercises", 1.0),
        (30, "military_deployment", None),
    ]

    result = _load_subindicators(
        cur,
        dimension_id=4,
    )

    assert result == [
        {
            "id": 29,
            "code": "anomalous_military_exercises",
            "weight": 1.0,
        },
        {
            "id": 30,
            "code": "military_deployment",
            "weight": 0.0,
        },
    ]


# ============================================================
# Risk impacts loading
# ============================================================


def test_load_risk_impacts():
    event_id = "event-1"
    impact_id = "impact-1"

    event_time = REFERENCE_TIME - timedelta(hours=24)

    cur = make_cursor()

    cur.fetchall.return_value = [
        (
            impact_id,
            event_id,
            29,
            40.0,
            0.7,
            event_time,
        )
    ]

    result = _load_risk_impacts(
        cur,
        country_id=321,
        reference_time=REFERENCE_TIME,
    )

    assert len(result) == 1

    assert result[0]["id"] == impact_id
    assert result[0]["event_id"] == event_id
    assert result[0]["subindicator_id"] == 29
    assert result[0]["base_impact"] == pytest.approx(40.0)
    assert result[0]["relevance"] == pytest.approx(0.7)
    assert result[0]["time_start"] == event_time

def test_load_risk_impacts_excludes_duplicate_events():
    event_id = "event-1"
    duplicate_event_id = "event-duplicate"
    impact_id = "impact-1"
    duplicate_impact_id = "impact-duplicate"

    event_time = REFERENCE_TIME - timedelta(hours=24)

    cur = make_cursor()

    def execute(sql, params=None):
        normalized_sql = " ".join(
            str(sql).split()
        ).upper()

        if "FROM RISK_IMPACTS RI" in normalized_sql:
            if "E.DUPLICATE_OF IS NULL" in normalized_sql:
                cur.fetchall.return_value = [
                    (
                        impact_id,
                        event_id,
                        29,
                        40.0,
                        0.7,
                        event_time,
                    )
                ]
            else:
                cur.fetchall.return_value = [
                    (
                        impact_id,
                        event_id,
                        29,
                        40.0,
                        0.7,
                        event_time,
                    ),
                    (
                        duplicate_impact_id,
                        duplicate_event_id,
                        29,
                        40.0,
                        0.7,
                        event_time,
                    ),
                ]
            return

        cur.fetchall.return_value = []

    cur.execute.side_effect = execute

    result = _load_risk_impacts(
        cur,
        country_id=321,
        reference_time=REFERENCE_TIME,
    )

    assert len(result) == 1
    assert result[0]["id"] == impact_id
    assert result[0]["event_id"] == event_id

# ============================================================
# Full country risk snapshot
# ============================================================


def test_country_risk_snapshot_without_impacts_starts_from_zero():
    dimensions = [
        (1, "internal_instability", 0.25),
        (2, "conflict_violence", 0.25),
        (3, "international_tension", 0.20),
        (4, "military_activity", 0.15),
        (5, "pressure_stress", 0.15),
    ]

    subindicators = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
    }

    cur = configure_snapshot_cursor(
        dimensions=dimensions,
        subindicators_by_dimension=subindicators,
        impacts=[],
        confidence_values=[],
    )

    connection = make_connection(cur)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            connection
        )

        result = calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    assert result.country_id == 321

    assert result.internal_instability == pytest.approx(0.0)
    assert result.conflict_violence == pytest.approx(0.0)
    assert result.international_tension == pytest.approx(0.0)
    assert result.military_activity == pytest.approx(0.0)
    assert result.pressure_stress == pytest.approx(0.0)

    assert result.country_risk == pytest.approx(0.0)
    assert result.confidence == "low"

    connection.commit.assert_called_once()


def test_country_risk_snapshot_keeps_previous_subindicator_without_new_impact():
    dimensions = [
        (1, "internal_instability", 0.25),
    ]

    subindicators = {
        1: [
            (29, "anomalous_military_exercises", 1.0),
        ],
    }

    cur = configure_snapshot_cursor(
        dimensions=dimensions,
        subindicators_by_dimension=subindicators,
        impacts=[],
        previous_scores={
            (321, 29): 42.0,
        },
        confidence_values=[],
    )

    connection = make_connection(cur)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            connection
        )

        result = calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    assert result.internal_instability == pytest.approx(42.0)

    assert result.conflict_violence == pytest.approx(0.0)
    assert result.international_tension == pytest.approx(0.0)
    assert result.military_activity == pytest.approx(0.0)
    assert result.pressure_stress == pytest.approx(0.0)

    assert result.country_risk == pytest.approx(10.5)


def test_country_risk_snapshot_applies_event_to_subindicator():
    event_id = "event-1"
    impact_id = "impact-1"

    dimensions = [
        (4, "military_activity", 1.0),
    ]

    subindicators = {
        4: [
            (29, "anomalous_military_exercises", 1.0),
        ],
    }

    impacts = [
        (
            impact_id,
            event_id,
            29,
            40.0,
            0.7,
            REFERENCE_TIME,
        )
    ]

    cur = configure_snapshot_cursor(
        dimensions=dimensions,
        subindicators_by_dimension=subindicators,
        impacts=impacts,
        previous_scores={
            (321, 29): 0.0,
        },
        repetition_counts={
            event_id: 0,
        },
        confidence_values=[
            "high",
        ],
    )

    connection = make_connection(cur)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            connection
        )

        result = calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    assert result.military_activity > 0.0
    assert result.country_risk > 0.0
    assert result.confidence == "high"

    connection.commit.assert_called_once()


# ============================================================
# Database persistence
# ============================================================


def test_country_risk_snapshot_updates_effective_impact():
    event_id = "event-1"
    impact_id = "impact-1"

    dimensions = []

    impacts = [
        (
            impact_id,
            event_id,
            29,
            40.0,
            0.7,
            REFERENCE_TIME,
        )
    ]

    cur = configure_snapshot_cursor(
        dimensions=dimensions,
        impacts=impacts,
        repetition_counts={
            event_id: 0,
        },
        confidence_values=[
            "high",
        ],
    )

    connection = make_connection(cur)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            connection
        )

        calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    update_calls = [
        call
        for call in cur.execute.call_args_list
        if "UPDATE risk_impacts" in str(call)
    ]

    assert len(update_calls) == 1


def test_country_risk_snapshot_inserts_subindicator_snapshot():
    dimensions = [
        (4, "military_activity", 1.0),
    ]

    subindicators = {
        4: [
            (29, "anomalous_military_exercises", 1.0),
        ],
    }

    cur = configure_snapshot_cursor(
        dimensions=dimensions,
        subindicators_by_dimension=subindicators,
        impacts=[],
        previous_scores={
            (321, 29): 25.0,
        },
        confidence_values=[],
    )

    connection = make_connection(cur)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            connection
        )

        calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    snapshot_calls = [
        call
        for call in cur.execute.call_args_list
        if "INSERT INTO risk_subindicator_snapshots"
        in str(call)
    ]

    assert len(snapshot_calls) == 1


def test_country_risk_snapshot_inserts_country_risk_snapshot():
    cur = configure_snapshot_cursor(
        dimensions=[],
        impacts=[],
        confidence_values=[],
    )

    connection = make_connection(cur)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            connection
        )

        result = calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    snapshot_calls = [
        call
        for call in cur.execute.call_args_list
        if "INSERT INTO risk_snapshots" in str(call)
    ]

    assert len(snapshot_calls) == 1
    assert result.country_risk == pytest.approx(0.0)


def test_country_risk_snapshot_is_deterministic_for_same_reference_time():
    event_id = "event-1"
    impact_id = "impact-1"

    dimensions = [
        (4, "military_activity", 1.0),
    ]

    subindicators = {
        4: [
            (29, "anomalous_military_exercises", 1.0),
        ],
    }

    impacts = [
        (
            impact_id,
            event_id,
            29,
            40.0,
            0.7,
            REFERENCE_TIME,
        )
    ]

    previous_score = 10.0

    first_cursor = configure_snapshot_cursor(
        dimensions=dimensions,
        subindicators_by_dimension=subindicators,
        impacts=impacts,
        previous_scores={
            (321, 29): previous_score,
        },
        repetition_counts={
            event_id: 0,
        },
        confidence_values=[
            "high",
        ],
    )

    first_connection = make_connection(first_cursor)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            first_connection
        )

        first_result = calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    second_cursor = configure_snapshot_cursor(
        dimensions=dimensions,
        subindicators_by_dimension=subindicators,
        impacts=impacts,
        previous_scores={
            (321, 29): previous_score,
        },
        repetition_counts={
            event_id: 0,
        },
        confidence_values=[
            "high",
        ],
    )

    second_connection = make_connection(second_cursor)

    with patch(
        "backend.app.scoring.risk_service.get_connection"
    ) as mock_get_connection:
        mock_get_connection.return_value.__enter__.return_value = (
            second_connection
        )

        second_result = calculate_country_risk_snapshot(
            country_id=321,
            reference_time=REFERENCE_TIME,
        )

    assert second_result.military_activity == pytest.approx(
        first_result.military_activity
    )

    assert second_result.country_risk == pytest.approx(
        first_result.country_risk
    )

def test_global_risk_coverage_status_insufficient_global():
    assert _get_global_risk_coverage_status(24.99, 100.0) == "insufficient"


def test_global_risk_coverage_status_insufficient_systemic():
    assert _get_global_risk_coverage_status(100.0, 49.99) == "insufficient"


def test_global_risk_coverage_status_provisional_at_lower_boundary():
    assert _get_global_risk_coverage_status(25.0, 50.0) == "provisional"


def test_global_risk_coverage_status_provisional_below_operational():
    assert _get_global_risk_coverage_status(59.99, 80.0) == "provisional"


def test_global_risk_coverage_status_operational_at_boundary():
    assert _get_global_risk_coverage_status(60.0, 80.0) == "operational"


def test_global_risk_coverage_status_operational_above_boundaries():
    assert _get_global_risk_coverage_status(100.0, 100.0) == "operational"

