from datetime import datetime, timedelta, timezone

import pytest

from backend.app.scoring.risk_engine import (
    RiskImpactInput,
    calculate_country_risk,
    calculate_dimension_score,
    calculate_effective_impact,
    calculate_event_pressure,
    calculate_risk_impact,
    calculate_subindicator_score,
    calculate_temporal_weight,
    calculate_repetition_weight,
    calculate_trend,
)


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
# Temporal weight
# ============================================================


def test_temporal_weight_is_one_for_current_event():
    result = calculate_temporal_weight(
        REFERENCE_TIME,
        reference_time=REFERENCE_TIME,
    )

    assert result == pytest.approx(1.0)


def test_temporal_weight_is_half_after_48_hours():
    event_time = REFERENCE_TIME - timedelta(hours=48)

    result = calculate_temporal_weight(
        event_time,
        reference_time=REFERENCE_TIME,
    )

    assert result == pytest.approx(0.5, abs=0.0001)


def test_temporal_weight_is_quarter_after_96_hours():
    event_time = REFERENCE_TIME - timedelta(hours=96)

    result = calculate_temporal_weight(
        event_time,
        reference_time=REFERENCE_TIME,
    )

    assert result == pytest.approx(0.25, abs=0.0001)


def test_temporal_weight_at_seven_days():
    event_time = REFERENCE_TIME - timedelta(hours=168)

    result = calculate_temporal_weight(
        event_time,
        reference_time=REFERENCE_TIME,
    )

    assert result == pytest.approx(
        2 ** (-168 / 48),
        abs=0.0001,
    )


def test_temporal_weight_is_zero_after_calculation_window():
    event_time = REFERENCE_TIME - timedelta(hours=169)

    result = calculate_temporal_weight(
        event_time,
        reference_time=REFERENCE_TIME,
    )

    assert result == pytest.approx(0.0)


def test_temporal_weight_is_one_for_future_event():
    event_time = REFERENCE_TIME + timedelta(hours=24)

    result = calculate_temporal_weight(
        event_time,
        reference_time=REFERENCE_TIME,
    )

    assert result == pytest.approx(1.0)


# ============================================================
# Repetition weight
# ============================================================


@pytest.mark.parametrize(
    "repetition_count, expected",
    [
        (1, 1.00),
        (2, 0.60),
        (3, 0.35),
        (4, 0.20),
        (5, 0.10),
        (6, 0.10),
        (10, 0.10),
    ],
)
def test_repetition_weight(
    repetition_count,
    expected,
):
    result = calculate_repetition_weight(
        repetition_count
    )

    assert result == pytest.approx(expected)


def test_zero_repetitions_are_treated_as_one():
    result = calculate_repetition_weight(0)

    assert result == pytest.approx(1.0)


# ============================================================
# Effective impact
# ============================================================


def test_effective_impact_formula():
    result = calculate_effective_impact(
        base_impact=80.0,
        relevance=0.75,
        temporal_weight=0.5,
        repetition_weight=0.6,
    )

    assert result == pytest.approx(18.0)


def test_effective_impact_clamps_inputs():
    result = calculate_effective_impact(
        base_impact=150.0,
        relevance=2.0,
        temporal_weight=2.0,
        repetition_weight=2.0,
    )

    assert result == pytest.approx(100.0)


def test_negative_effective_impact_inputs_are_clamped():
    result = calculate_effective_impact(
        base_impact=-20.0,
        relevance=-1.0,
        temporal_weight=-1.0,
        repetition_weight=-1.0,
    )

    assert result == pytest.approx(0.0)


# ============================================================
# Risk impact
# ============================================================


def test_calculate_risk_impact_combines_components():
    impact = RiskImpactInput(
        base_impact=80.0,
        relevance=0.75,
        time_start=REFERENCE_TIME
        - timedelta(hours=48),
        repetition_count=2,
    )

    result = calculate_risk_impact(
        impact,
        reference_time=REFERENCE_TIME,
    )

    assert result.temporal_weight == pytest.approx(
        0.5,
        abs=0.0001,
    )

    assert result.repetition_weight == pytest.approx(
        0.6
    )

    assert result.effective_impact == pytest.approx(
        18.0
    )


# ============================================================
# Event pressure
# ============================================================


def test_event_pressure_is_zero_without_impacts():
    result = calculate_event_pressure([])

    assert result == pytest.approx(0.0)


def test_event_pressure_for_single_impact():
    result = calculate_event_pressure([3.0])

    expected = 100.0 * (
        1.0 - __import__("math").exp(-3.0 / 3.0)
    )

    assert result == pytest.approx(expected)


def test_event_pressure_saturates():
    result = calculate_event_pressure(
        [100.0, 100.0, 100.0]
    )

    assert result > 99.0
    assert result <= 100.0


def test_event_pressure_ignores_negative_impacts():
    result = calculate_event_pressure(
        [-10.0, 10.0]
    )

    expected = 100.0 * (
        1.0 - __import__("math").exp(-10.0 / 3.0)
    )

    assert result == pytest.approx(expected)


# ============================================================
# Subindicator score
# ============================================================


def test_subindicator_score_uses_65_35_weights():
    result = calculate_subindicator_score(
        previous_score=20.0,
        event_pressure=80.0,
    )

    assert result == pytest.approx(41.0)


def test_subindicator_score_clamps_inputs():
    result = calculate_subindicator_score(
        previous_score=150.0,
        event_pressure=150.0,
    )

    assert result == pytest.approx(100.0)


# ============================================================
# Dimension score
# ============================================================


def test_dimension_score_calculates_weighted_average():
    result = calculate_dimension_score(
        [
            (20.0, 0.25),
            (80.0, 0.75),
        ]
    )

    assert result == pytest.approx(65.0)


def test_dimension_score_normalizes_weights():
    result = calculate_dimension_score(
        [
            (20.0, 1.0),
            (80.0, 3.0),
        ]
    )

    assert result == pytest.approx(65.0)


def test_dimension_score_returns_zero_without_active_weights():
    result = calculate_dimension_score(
        [
            (20.0, 0.0),
            (80.0, 0.0),
        ]
    )

    assert result == pytest.approx(0.0)


def test_dimension_score_clamps_scores():
    result = calculate_dimension_score(
        [
            (150.0, 1.0),
            (-50.0, 1.0),
        ]
    )

    assert result == pytest.approx(50.0)


# ============================================================
# Country Risk
# ============================================================


def test_country_risk_uses_v11_dimension_weights():
    result = calculate_country_risk(
        internal_instability=100.0,
        conflict_violence=100.0,
        international_tension=100.0,
        military_activity=100.0,
        pressure_stress=100.0,
    )

    assert result == pytest.approx(100.0)


def test_country_risk_with_only_internal_instability():
    result = calculate_country_risk(
        internal_instability=100.0,
        conflict_violence=0.0,
        international_tension=0.0,
        military_activity=0.0,
        pressure_stress=0.0,
    )

    assert result == pytest.approx(25.0)


def test_country_risk_with_only_conflict_violence():
    result = calculate_country_risk(
        internal_instability=0.0,
        conflict_violence=100.0,
        international_tension=0.0,
        military_activity=0.0,
        pressure_stress=0.0,
    )

    assert result == pytest.approx(25.0)


def test_country_risk_with_only_international_tension():
    result = calculate_country_risk(
        internal_instability=0.0,
        conflict_violence=0.0,
        international_tension=100.0,
        military_activity=0.0,
        pressure_stress=0.0,
    )

    assert result == pytest.approx(20.0)


def test_country_risk_with_only_military_activity():
    result = calculate_country_risk(
        internal_instability=0.0,
        conflict_violence=0.0,
        international_tension=0.0,
        military_activity=100.0,
        pressure_stress=0.0,
    )

    assert result == pytest.approx(15.0)


def test_country_risk_with_only_pressure_stress():
    result = calculate_country_risk(
        internal_instability=0.0,
        conflict_violence=0.0,
        international_tension=0.0,
        military_activity=0.0,
        pressure_stress=100.0,
    )

    assert result == pytest.approx(15.0)


def test_country_risk_clamps_inputs():
    result = calculate_country_risk(
        internal_instability=200.0,
        conflict_violence=-100.0,
        international_tension=0.0,
        military_activity=0.0,
        pressure_stress=0.0,
    )

    assert result == pytest.approx(25.0)


# ============================================================
# Trend
# ============================================================


def test_trend_is_positive_when_risk_increases():
    result = calculate_trend(
        current_country_risk=60.0,
        previous_country_risk=40.0,
    )

    assert result == pytest.approx(20.0)


def test_trend_is_negative_when_risk_decreases():
    result = calculate_trend(
        current_country_risk=40.0,
        previous_country_risk=60.0,
    )

    assert result == pytest.approx(-20.0)


def test_trend_is_zero_when_risk_is_unchanged():
    result = calculate_trend(
        current_country_risk=50.0,
        previous_country_risk=50.0,
    )

    assert result == pytest.approx(0.0)


def test_trend_clamps_inputs():
    result = calculate_trend(
        current_country_risk=150.0,
        previous_country_risk=-50.0,
    )

    assert result == pytest.approx(100.0)