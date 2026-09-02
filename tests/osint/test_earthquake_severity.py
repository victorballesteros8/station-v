import pytest

from backend.app.osint.earthquake_severity import (
    resolve_gdacs_earthquake_severity,
    resolve_usgs_earthquake_severity,
    severity_from_magnitude,
)


@pytest.mark.parametrize(
    ("magnitude", "expected"),
    [
        (4.9, "info"),
        (5.0, "low"),
        (5.9, "low"),
        (6.0, "medium"),
        (6.9, "medium"),
        (7.0, "high"),
        (7.9, "high"),
        (8.0, "critical"),
        (None, "info"),
    ],
)
def test_severity_from_magnitude(magnitude, expected):
    assert severity_from_magnitude(magnitude) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"magnitude": 5.0, "alert": "yellow"}, "low"),
        ({"magnitude": 5.0, "alert": "orange"}, "medium"),
        ({"magnitude": 5.0, "alert": "red"}, "high"),
        ({"magnitude": 5.0, "alert": "green"}, "low"),
        ({"magnitude": 5.0, "mmi": 7.0}, "medium"),
        ({"magnitude": 5.0, "mmi": 8.0}, "high"),
        ({"magnitude": 5.0, "mmi": 9.0}, "high"),
        ({"magnitude": 5.0, "tsunami": 1}, "medium"),
        ({"magnitude": 8.0, "mmi": 9.0, "tsunami": 1}, "critical"),
    ],
)
def test_resolve_usgs_earthquake_severity(data, expected):
    assert resolve_usgs_earthquake_severity(data) == expected


def test_usgs_does_not_use_felt_or_significance_for_elevation():
    base = {"magnitude": 5.0}
    with_context = {"magnitude": 5.0, "felt": 5000, "significance": 2000}

    assert resolve_usgs_earthquake_severity(base) == "low"
    assert resolve_usgs_earthquake_severity(with_context) == "low"


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"magnitude": 5.0, "alert_level": "green"}, "low"),
        ({"magnitude": 5.0, "alert_level": "orange"}, "medium"),
        ({"magnitude": 5.0, "alert_level": "red"}, "high"),
        ({"magnitude": 8.0, "alert_level": "green"}, "critical"),
    ],
)
def test_resolve_gdacs_earthquake_severity(data, expected):
    assert resolve_gdacs_earthquake_severity(data) == expected
