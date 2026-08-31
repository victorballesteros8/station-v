from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from backend.app.osint.gdacs.client import (
    GDACSClientError,
    fetch_gdacs_events,
)
from backend.app.osint.gdacs.normalizer import (
    GDACSNormalizationError,
    normalize_gdacs_feature,
    normalize_gdacs_feed,
)


def _sample_feature():
    return {
        "type": "Feature",
        "bbox": [
            105.229,
            29.2752,
            105.229,
            29.2752,
        ],
        "geometry": {
            "type": "Point",
            "coordinates": [
                105.229,
                29.2752,
            ],
        },
        "properties": {
            "eventtype": "EQ",
            "eventid": 1562260,
            "episodeid": 1729706,
            "eventname": "",
            "glide": "EQ-2026-000168-CHN",
            "name": "Earthquake in China",
            "description": "Earthquake in China",
            "htmldescription": (
                "Orange M 5 Earthquake in China at: "
                "28 Aug 2026 05:13:35."
            ),
            "alertlevel": "Orange",
            "alertscore": 2,
            "episodealertlevel": "Orange",
            "episodealertscore": 1.02196166728945,
            "istemporary": "false",
            "iscurrent": "true",
            "country": "China",
            "fromdate": "2026-08-28T05:13:35",
            "todate": "2026-08-28T05:13:35",
            "datemodified": "2026-08-28T07:04:27",
            "iso3": "CHN",
            "source": "NEIC",
            "sourceid": "",
            "polygonlabel": "Centroid",
            "Class": "Point_Centroid",
            "url": {
                "geometry": (
                    "https://www.gdacs.org/"
                    "gdacsapi/api/polygons/getgeometry"
                    "?eventtype=EQ&eventid=1562260"
                    "&episodeid=1729706"
                ),
                "report": (
                    "https://www.gdacs.org/"
                    "report.aspx?eventid=1562260"
                    "&episodeid=1729706"
                    "&eventtype=EQ"
                ),
                "details": (
                    "https://www.gdacs.org/"
                    "gdacsapi/api/events/geteventdata"
                    "?eventtype=EQ&eventid=1562260"
                ),
            },
            "affectedcountries": [
                {
                    "iso2": "CN",
                    "iso3": "CHN",
                    "countryname": "China",
                }
            ],
            "severitydata": {
                "severity": 5.0,
                "severitytext": "Magnitude 5M, Depth:10km",
                "severityunit": "M",
            },
        },
    }


def test_normalize_gdacs_feature():
    result = normalize_gdacs_feature(
        _sample_feature()
    )

    assert result.event_id == "1562260"
    assert result.episode_id == "1729706"

    assert result.event_type == "EQ"
    assert result.alert_level == "Orange"
    assert result.alert_score == 2.0

    assert result.event_name == "Earthquake in China"
    assert result.country == "China"
    assert result.country_iso3 == "CHN"

    assert result.latitude == pytest.approx(
        29.2752
    )
    assert result.longitude == pytest.approx(
        105.229
    )

    assert result.magnitude == 5.0
    assert result.depth == 10.0

    assert result.event_time == datetime(
        2026,
        8,
        28,
        5,
        13,
        35,
    )

    assert result.update_time == datetime(
        2026,
        8,
        28,
        7,
        4,
        27,
    )

    assert result.source == "NEIC"

    assert result.geometry_url is not None
    assert result.report_url is not None
    assert result.details_url is not None


def test_normalize_gdacs_feed():
    payload = {
        "type": "FeatureCollection",
        "features": [
            _sample_feature(),
        ],
    }

    result = normalize_gdacs_feed(payload)

    assert len(result) == 1
    assert result[0].event_id == "1562260"


def test_normalize_gdacs_empty_feed():
    payload = {
        "type": "FeatureCollection",
        "features": [],
    }

    result = normalize_gdacs_feed(payload)

    assert result == []


def test_normalize_gdacs_requires_features():
    with pytest.raises(GDACSNormalizationError):
        normalize_gdacs_feed({})


def test_normalize_gdacs_requires_event_id():
    feature = _sample_feature()
    del feature["properties"]["eventid"]

    with pytest.raises(GDACSNormalizationError):
        normalize_gdacs_feature(feature)


def test_normalize_gdacs_requires_event_type():
    feature = _sample_feature()
    del feature["properties"]["eventtype"]

    with pytest.raises(GDACSNormalizationError):
        normalize_gdacs_feature(feature)


def test_normalize_gdacs_rejects_non_earthquake():
    feature = _sample_feature()
    feature["properties"]["eventtype"] = "TC"

    with pytest.raises(GDACSNormalizationError):
        normalize_gdacs_feature(feature)


def test_normalize_gdacs_allows_missing_geometry():
    feature = _sample_feature()
    feature["geometry"] = None

    result = normalize_gdacs_feature(feature)

    assert result.latitude is None
    assert result.longitude is None


def test_normalize_gdacs_allows_missing_optional_urls():
    feature = _sample_feature()
    feature["properties"]["url"] = None

    result = normalize_gdacs_feature(feature)

    assert result.geometry_url is None
    assert result.report_url is None
    assert result.details_url is None


def test_normalize_gdacs_uses_description_when_event_name_empty():
    feature = _sample_feature()
    feature["properties"]["eventname"] = ""

    result = normalize_gdacs_feature(feature)

    assert result.event_name == "Earthquake in China"


def test_normalize_gdacs_rejects_invalid_coordinates():
    feature = _sample_feature()
    feature["geometry"]["coordinates"] = [105.229]

    with pytest.raises(GDACSNormalizationError):
        normalize_gdacs_feature(feature)


def test_normalize_gdacs_rejects_invalid_datetime():
    feature = _sample_feature()
    feature["properties"]["fromdate"] = "not-a-date"

    with pytest.raises(GDACSNormalizationError):
        normalize_gdacs_feature(feature)


def test_normalize_gdacs_extracts_depth_from_severity_text():
    feature = _sample_feature()

    feature["properties"]["severitydata"] = {
        "severity": 5.0,
        "severitytext": "Magnitude 5M, Depth:10km",
        "severityunit": "M",
    }

    result = normalize_gdacs_feature(feature)

    assert result.depth == 10.0


def test_gdacs_client_returns_empty_feature_collection_on_204():
    class FakeResponse:
        status = 204

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            return b""

    with patch(
        "backend.app.osint.gdacs.client.urlopen",
        return_value=FakeResponse(),
    ):
        result = fetch_gdacs_events(
            from_date=datetime(
                2026,
                8,
                31,
            ).date(),
            to_date=datetime(
                2026,
                8,
                31,
            ).date(),
        )

    assert result == {
        "type": "FeatureCollection",
        "features": [],
    }


def test_gdacs_client_rejects_invalid_json():
    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            return b"not-json"

    with patch(
        "backend.app.osint.gdacs.client.urlopen",
        return_value=FakeResponse(),
    ):
        with pytest.raises(GDACSClientError):
            fetch_gdacs_events(
                from_date=datetime(
                    2026,
                    8,
                    31,
                ).date(),
                to_date=datetime(
                    2026,
                    8,
                    31,
                ).date(),
            )

def test_gdacs_client_paginates_until_partial_page():
    pages = [
        {
            "type": "FeatureCollection",
            "features": [{"id": "event-1"}],
        },
        {
            "type": "FeatureCollection",
            "features": [{"id": "event-2"}],
        },
        {
            "type": "FeatureCollection",
            "features": [],
        },
    ]

    with patch(
        "backend.app.osint.gdacs.client._fetch_gdacs_page",
        side_effect=pages,
    ) as mock_fetch:
        result = fetch_gdacs_events(
            from_date=datetime(
                2026,
                8,
                1,
            ).date(),
            to_date=datetime(
                2026,
                8,
                31,
            ).date(),
            page_size=1,
        )

    assert result["type"] == "FeatureCollection"
    assert result["features"] == [
        {"id": "event-1"},
        {"id": "event-2"},
    ]

    assert mock_fetch.call_count == 3

    assert mock_fetch.call_args_list[0].kwargs[
        "page_number"
    ] == 1

    assert mock_fetch.call_args_list[1].kwargs[
        "page_number"
    ] == 2

    assert mock_fetch.call_args_list[2].kwargs[
        "page_number"
    ] == 3


def test_gdacs_client_stops_on_partial_page():
    pages = [
        {
            "type": "FeatureCollection",
            "features": [
                {"id": "event-1"},
            ],
        },
    ]

    with patch(
        "backend.app.osint.gdacs.client._fetch_gdacs_page",
        side_effect=pages,
    ) as mock_fetch:
        result = fetch_gdacs_events(
            from_date=datetime(
                2026,
                8,
                1,
            ).date(),
            to_date=datetime(
                2026,
                8,
                31,
            ).date(),
            page_size=2,
        )

    assert result["features"] == [
        {"id": "event-1"},
    ]

    assert mock_fetch.call_count == 1


def test_gdacs_client_rejects_invalid_page_size():
    with pytest.raises(ValueError):
        fetch_gdacs_events(
            from_date=datetime(
                2026,
                8,
                1,
            ).date(),
            to_date=datetime(
                2026,
                8,
                31,
            ).date(),
            page_size=0,
        )