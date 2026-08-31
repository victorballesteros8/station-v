from datetime import datetime, timezone

import pytest

from backend.app.osint.usgs.normalizer import (
    USGSNormalizationError,
    normalize_usgs_feature,
    normalize_usgs_feed,
)

from backend.app.osint.usgs.claim_builder import (
    USGSClaim,
    build_usgs_claim,
)

from unittest.mock import patch
from unittest.mock import MagicMock

def _sample_feature() -> dict:
    return {
        "type": "Feature",
        "properties": {
            "mag": 5.6,
            "place": "10 km NW of Example",
            "time": 1725000000000,
            "updated": 1725000060000,
            "url": "https://example.usgs.gov/event/abc123",
            "alert": "green",
            "sig": 482,
            "tsunami": 0,
            "felt": 12,
            "cdi": 3.2,
            "mmi": 4.1,
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
                139.6917,
                35.6895,
                35.0,
            ],
        },
        "id": "abc123",
    }


def test_normalize_usgs_feature():
    result = normalize_usgs_feature(
        _sample_feature()
    )

    assert result.external_id == "abc123"
    assert result.source_url == (
        "https://example.usgs.gov/event/abc123"
    )

    assert result.magnitude == pytest.approx(5.6)
    assert result.place == "10 km NW of Example"

    assert result.longitude == pytest.approx(139.6917)
    assert result.latitude == pytest.approx(35.6895)
    assert result.depth == pytest.approx(35.0)

    assert result.alert == "green"
    assert result.significance == 482
    assert result.tsunami == 0
    assert result.felt == 12

    assert result.mmi == pytest.approx(4.1)
    assert result.cdi == pytest.approx(3.2)


def test_normalize_usgs_timestamps():
    result = normalize_usgs_feature(
        _sample_feature()
    )

    assert result.time == datetime.fromtimestamp(
        1725000000000 / 1000,
        tz=timezone.utc,
    )

    assert result.updated == datetime.fromtimestamp(
        1725000060000 / 1000,
        tz=timezone.utc,
    )


def test_normalize_usgs_feed():
    payload = {
        "type": "FeatureCollection",
        "features": [
            _sample_feature(),
            {
                **_sample_feature(),
                "id": "def456",
            },
        ],
    }

    result = normalize_usgs_feed(payload)

    assert len(result) == 2
    assert result[0].external_id == "abc123"
    assert result[1].external_id == "def456"


def test_normalize_usgs_feature_requires_external_id():
    feature = _sample_feature()
    del feature["id"]

    with pytest.raises(USGSNormalizationError):
        normalize_usgs_feature(feature)


def test_normalize_usgs_feature_requires_properties():
    feature = _sample_feature()
    feature["properties"] = None

    with pytest.raises(USGSNormalizationError):
        normalize_usgs_feature(feature)


def test_normalize_usgs_feature_rejects_invalid_geometry():
    feature = _sample_feature()
    feature["geometry"]["coordinates"] = [139.0]

    with pytest.raises(USGSNormalizationError):
        normalize_usgs_feature(feature)


def test_normalize_usgs_feed_requires_features():
    with pytest.raises(USGSNormalizationError):
        normalize_usgs_feed({})


def test_ingest_usgs_creates_source_and_evidence():
    payload = {
        "type": "FeatureCollection",
        "features": [
            _sample_feature(),
        ],
    }

    with patch(
        "backend.app.osint.usgs.ingestor.get_connection"
    ) as mock_connection:

        connection = mock_connection.return_value.__enter__.return_value
        cursor = connection.cursor.return_value.__enter__.return_value

        cursor.fetchone.side_effect = [
            None,
            ("source-id",),
            ("evidence-id",),
            ("claim-id",),
        ]

        from backend.app.osint.usgs.ingestor import ingest_usgs

        result = ingest_usgs(payload)

    assert result == 1
    mock_connection.assert_called_once()
    connection.commit.assert_called_once()


def test_ingest_usgs_does_not_fetch_when_payload_is_provided():
    payload = {
        "type": "FeatureCollection",
        "features": [
            _sample_feature(),
        ],
    }

    with patch(
        "backend.app.osint.usgs.ingestor.fetch_usgs_feed"
    ) as mock_fetch:
        with patch(
            "backend.app.osint.usgs.ingestor.get_connection"
        ) as mock_connection:

            connection = (
                mock_connection
                .return_value
                .__enter__
                .return_value
            )

            cursor = (
                connection
                .cursor
                .return_value
                .__enter__
                .return_value
            )

            cursor.fetchone.side_effect = [
                ("source-id",),
                ("evidence-id",),
                ("claim-id",),
            ]

            from backend.app.osint.usgs.ingestor import ingest_usgs

            result = ingest_usgs(payload)

    assert result == 1
    mock_fetch.assert_not_called()


def test_ingest_usgs_empty_feed():
    payload = {
        "type": "FeatureCollection",
        "features": [],
    }

    with patch(
        "backend.app.osint.usgs.ingestor.get_connection"
    ) as mock_connection:

        connection = mock_connection.return_value.__enter__.return_value
        cursor = connection.cursor.return_value.__enter__.return_value

        cursor.fetchone.return_value = ("source-id",)

        from backend.app.osint.usgs.ingestor import ingest_usgs

        result = ingest_usgs(payload)

    assert result == 0
    connection.commit.assert_called_once()


def test_build_usgs_claim():
    earthquake = normalize_usgs_feature(
        _sample_feature()
    )

    claim = build_usgs_claim(earthquake)

    assert isinstance(claim, USGSClaim)
    assert claim.claim_type == "earthquake"
    assert claim.assertion_status == "confirmed"
    assert claim.confidence == "high"

    assert (
        claim.statement
        == "Earthquake detected by USGS: "
        "magnitude 5.6, 10 km NW of Example."
    )


def test_build_usgs_claim_without_magnitude():
    feature = _sample_feature()
    feature["properties"]["mag"] = None

    earthquake = normalize_usgs_feature(feature)
    claim = build_usgs_claim(earthquake)

    assert claim.statement == (
        "Earthquake detected by USGS: "
        "magnitude unknown, 10 km NW of Example."
    )


def test_build_usgs_claim_without_place():
    feature = _sample_feature()
    feature["properties"]["place"] = None

    earthquake = normalize_usgs_feature(feature)
    claim = build_usgs_claim(earthquake)

    assert claim.statement == (
        "Earthquake detected by USGS: "
        "magnitude 5.6, unknown location."
    )


def test_persist_usgs_claim():
    claim = USGSClaim(
        claim_type="earthquake",
        statement=(
            "Earthquake detected by USGS: "
            "magnitude 5.6, 10 km NW of Example."
        ),
        assertion_status="confirmed",
        confidence="high",
    )

    with patch(
        "backend.app.osint.usgs.claim_persistence.get_connection"
    ) as mock_connection:
        connection = (
            mock_connection
            .return_value
            .__enter__
            .return_value
        )

        cursor = (
            connection
            .cursor
            .return_value
            .__enter__
            .return_value
        )

        cursor.fetchone.return_value = (
            "claim-id",
        )

        from backend.app.osint.usgs.claim_persistence import (
            persist_usgs_claim,
        )

        result = persist_usgs_claim(
            "evidence-id",
            claim,
        )

    assert result == "claim-id"
    connection.commit.assert_called_once()
    cursor.execute.assert_called_once()


def test_persist_usgs_claim_is_idempotent():
    claim = USGSClaim(
        claim_type="earthquake",
        statement=(
            "Earthquake detected by USGS: "
            "magnitude 5.6, 10 km NW of Example."
        ),
        assertion_status="confirmed",
        confidence="high",
    )

    with patch(
        "backend.app.osint.usgs.claim_persistence.get_connection"
    ) as mock_connection:
        connection = (
            mock_connection
            .return_value
            .__enter__
            .return_value
        )

        cursor = (
            connection
            .cursor
            .return_value
            .__enter__
            .return_value
        )

        cursor.fetchone.return_value = (
            "same-claim-id",
        )

        from backend.app.osint.usgs.claim_persistence import (
            persist_usgs_claim,
        )

        first = persist_usgs_claim(
            "evidence-id",
            claim,
        )

        second = persist_usgs_claim(
            "evidence-id",
            claim,
        )

    assert first == "same-claim-id"
    assert second == "same-claim-id"

def test_persist_usgs_claim_with_existing_cursor():
    claim = USGSClaim(
        claim_type="earthquake",
        statement=(
            "Earthquake detected by USGS: "
            "magnitude 5.6, 10 km NW of Example."
        ),
        assertion_status="confirmed",
        confidence="high",
    )

    cursor = MagicMock()
    cursor.fetchone.return_value = (
        "claim-id",
    )

    from backend.app.osint.usgs.claim_persistence import (
        _persist_usgs_claim,
    )

    result = _persist_usgs_claim(
        cursor,
        "evidence-id",
        claim,
    )

    assert result == "claim-id"
    cursor.execute.assert_called_once()

def test_earthquake_from_evidence():
    from backend.app.osint.usgs.claim_backfill import (
        _earthquake_from_evidence,
    )

    earthquake = _earthquake_from_evidence(
        (
            "test-id",
            "https://example.com/usgs",
            {
                "provider": "USGS",
                "magnitude": 5.6,
                "place": "10 km NW of Example",
                "latitude": 40.0,
                "longitude": -120.0,
                "depth": 12.5,
                "alert": "green",
                "significance": 100,
                "tsunami": 0,
                "felt": 2,
                "mmi": 3.5,
                "cdi": 4.2,
                "event_time": "2026-08-31T12:00:00+00:00",
                "updated_time": "2026-08-31T12:05:00+00:00",
            },
        )
    )

    assert earthquake.external_id == "test-id"
    assert earthquake.magnitude == 5.6
    assert earthquake.place == "10 km NW of Example"
    assert earthquake.latitude == 40.0
    assert earthquake.longitude == -120.0
    assert earthquake.depth == 12.5
    assert earthquake.alert == "green"
    assert earthquake.significance == 100
    assert earthquake.tsunami == 0
    assert earthquake.felt == 2
    assert earthquake.mmi == 3.5
    assert earthquake.cdi == 4.2
    assert earthquake.time is not None
    assert earthquake.updated is not None

def test_earthquake_from_evidence_handles_missing_optional_values():
    from backend.app.osint.usgs.claim_backfill import (
        _earthquake_from_evidence,
    )

    earthquake = _earthquake_from_evidence(
        (
            "test-id",
            None,
            {
                "provider": "USGS",
                "magnitude": None,
                "place": None,
                "latitude": None,
                "longitude": None,
                "depth": None,
                "alert": None,
                "significance": None,
                "tsunami": None,
                "felt": None,
                "mmi": None,
                "cdi": None,
                "event_time": None,
                "updated_time": None,
            },
        )
    )

    assert earthquake.external_id == "test-id"
    assert earthquake.magnitude is None
    assert earthquake.place is None
    assert earthquake.latitude is None
    assert earthquake.longitude is None
    assert earthquake.depth is None
    assert earthquake.time is None
    assert earthquake.updated is None