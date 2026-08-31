import pytest

from backend.app.scoring.global_risk_engine import (
    calculate_global_risk,
    calculate_tier_1_components,
    calculate_tier_2_pressure,
    calculate_tier_3_pressure,
)


def test_tier_1_components_all_low():
    result = calculate_tier_1_components(
        [10, 10, 10, 10, 10, 10, 10, 10]
    )

    assert result.intensity == pytest.approx(10.0)
    assert result.average == pytest.approx(10.0)
    assert result.breadth == pytest.approx(0.0)
    assert result.pressure == pytest.approx(8.0)


def test_tier_1_components_one_extreme_power():
    result = calculate_tier_1_components(
        [100, 0, 0, 0, 0, 0, 0, 0]
    )

    assert result.intensity == pytest.approx(70.0)
    assert result.average == pytest.approx(12.5)
    assert result.breadth == pytest.approx(12.5)
    assert result.pressure == pytest.approx(41.25)


def test_tier_1_components_multiple_systemic_powers():
    result = calculate_tier_1_components(
        [90, 90, 90, 90, 10, 10, 10, 10]
    )

    assert result.intensity == pytest.approx(90.0)
    assert result.average == pytest.approx(50.0)
    assert result.breadth == pytest.approx(50.0)
    assert result.pressure == pytest.approx(70.0)


def test_tier_1_breadth_threshold_is_inclusive():
    result = calculate_tier_1_components(
        [50, 49, 49, 49, 49, 49, 49, 49]
    )

    assert result.breadth == pytest.approx(12.5)


def test_tier_2_uses_top_eight():
    result = calculate_tier_2_pressure(
        [100, 90, 80, 70, 60, 50, 40, 30, 0, 0]
    )

    assert result == pytest.approx(65.0)


def test_tier_3_uses_top_ten():
    result = calculate_tier_3_pressure(
        [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0, 0]
    )

    assert result == pytest.approx(55.0)


def test_global_risk_all_low():
    result = calculate_global_risk(
        tier_1_risks=[10] * 8,
        tier_2_risks=[10] * 27,
        tier_3_risks=[10] * 161,
    )

    assert result == pytest.approx(8.7)


def test_global_risk_systemic_crisis():
    result = calculate_global_risk(
        tier_1_risks=[90, 90, 90, 90, 80, 70, 60, 50],
        tier_2_risks=[30] * 27,
        tier_3_risks=[10] * 161,
    )

    assert result == pytest.approx(65.8625)


def test_global_risk_tier_3_alone_cannot_dominate():
    result = calculate_global_risk(
        tier_1_risks=[10] * 8,
        tier_2_risks=[10] * 27,
        tier_3_risks=[100] * 161,
    )

    assert result == pytest.approx(17.7)


def test_global_risk_is_more_sensitive_to_tier_1_than_tier_3():
    systemic = calculate_global_risk(
        tier_1_risks=[80] * 8,
        tier_2_risks=[10] * 27,
        tier_3_risks=[10] * 161,
    )

    peripheral = calculate_global_risk(
        tier_1_risks=[10] * 8,
        tier_2_risks=[10] * 27,
        tier_3_risks=[80] * 161,
    )

    assert systemic > peripheral


def test_global_risk_zero():
    result = calculate_global_risk(
        tier_1_risks=[],
        tier_2_risks=[],
        tier_3_risks=[],
    )

    assert result == pytest.approx(0.0)


@pytest.mark.parametrize(
    "value",
    [-1, 100.1],
)
def test_invalid_country_risk_is_rejected(value):
    with pytest.raises(ValueError):
        calculate_global_risk(
            tier_1_risks=[value],
            tier_2_risks=[],
            tier_3_risks=[],
        )