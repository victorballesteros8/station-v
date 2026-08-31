from unittest.mock import patch

from backend.app.osint.gdacs.ingestor import (
    ingest_gdacs,
)


def _sample_payload():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
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
                    "name": "Earthquake in China",
                    "description": "Earthquake in China",
                    "alertlevel": "Orange",
                    "alertscore": 2,
                    "country": "China",
                    "iso3": "CHN",
                    "fromdate": "2026-08-28T05:13:35",
                    "datemodified": "2026-08-28T07:04:27",
                    "source": "NEIC",
                    "url": {
                        "geometry": (
                            "https://www.gdacs.org/"
                            "gdacsapi/api/polygons/getgeometry"
                        ),
                        "report": (
                            "https://www.gdacs.org/"
                            "report.aspx?eventid=1562260"
                        ),
                        "details": (
                            "https://www.gdacs.org/"
                            "gdacsapi/api/events/geteventdata"
                        ),
                    },
                    "severitydata": {
                        "severity": 5.0,
                        "severitytext": (
                            "Magnitude 5M, Depth:10km"
                        ),
                        "severityunit": "M",
                    },
                },
            }
        ],
    }


def test_ingest_gdacs_creates_source_evidence_and_claim():
    payload = _sample_payload()

    with patch(
        "backend.app.osint.gdacs.ingestor.get_connection"
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
            None,
            ("source-id",),
            ("evidence-id",),
            ("claim-id",),
        ]

        result = ingest_gdacs(payload)

    assert result == 1

    assert cursor.execute.call_count == 4

    calls = cursor.execute.call_args_list

    source_select_sql = calls[0].args[0]
    source_insert_sql = calls[1].args[0]
    evidence_sql = calls[2].args[0]
    claim_sql = calls[3].args[0]

    assert "SELECT id" in source_select_sql
    assert "FROM sources" in source_select_sql

    assert "INSERT INTO sources" in source_insert_sql
    assert "INSERT INTO evidence" in evidence_sql
    assert "INSERT INTO claims" in claim_sql

    evidence_params = calls[2].args[1]

    assert (
        evidence_params["external_id"]
        == "1562260:1729706"
    )

    assert (
        evidence_params["evidence_type"]
        == "alert"
    )

    assert (
        evidence_params["source_role"]
        == "observation"
    )

    claim_params = calls[3].args[1]

    assert (
        claim_params["claim_type"]
        == "earthquake_alert"
    )

    assert (
        claim_params["assertion_status"]
        == "reported"
    )

    assert (
        claim_params["confidence"]
        == "high"
    )

    connection.commit.assert_called_once()


def test_ingest_gdacs_uses_existing_source():
    payload = _sample_payload()

    with patch(
        "backend.app.osint.gdacs.ingestor.get_connection"
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
            ("existing-source-id",),
            ("evidence-id",),
            ("claim-id",),
        ]

        result = ingest_gdacs(payload)

    assert result == 1

    assert cursor.execute.call_count == 3

    first_sql = (
        cursor.execute.call_args_list[0]
        .args[0]
    )

    assert "SELECT id" in first_sql
    assert "FROM sources" in first_sql


def test_ingest_gdacs_does_not_fetch_when_payload_is_provided():
    payload = _sample_payload()

    with patch(
        "backend.app.osint.gdacs.ingestor.fetch_gdacs_events"
    ) as mock_fetch:

        with patch(
            "backend.app.osint.gdacs.ingestor.get_connection"
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

            ingest_gdacs(payload)

    mock_fetch.assert_not_called()


def test_ingest_gdacs_requires_dates_without_payload():
    with patch(
        "backend.app.osint.gdacs.ingestor.get_connection"
    ) as mock_connection:

        try:
            ingest_gdacs()
        except ValueError as exc:
            assert (
                "from_date and to_date are required"
                in str(exc)
            )
        else:
            raise AssertionError(
                "Expected ValueError"
            )

        mock_connection.assert_not_called()


def test_ingest_gdacs_fetches_when_payload_is_missing():
    payload = _sample_payload()

    with patch(
        "backend.app.osint.gdacs.ingestor.fetch_gdacs_events",
        return_value=payload,
    ) as mock_fetch:

        with patch(
            "backend.app.osint.gdacs.ingestor.get_connection"
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

            result = ingest_gdacs(
                from_date="2026-08-01",
                to_date="2026-08-31",
                event_type="EQ",
            )

    assert result == 1

    mock_fetch.assert_called_once_with(
        from_date="2026-08-01",
        to_date="2026-08-31",
        event_type="EQ",
    )