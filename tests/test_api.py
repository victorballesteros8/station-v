from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


# ============================================================
# Health
# ============================================================


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "station-v-api"


def test_db_health():
    response = client.get("/api/db-health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] is True


# ============================================================
# Countries
# ============================================================


def test_countries_list_returns_data():
    response = client.get("/api/countries")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data

    assert isinstance(data["items"], list)
    assert data["total"] == len(data["items"])
    assert data["total"] > 0


def test_country_detail_returns_existing_country():
    response = client.get("/api/v1/countries/313")

    assert response.status_code == 200

    data = response.json()

    assert data["country"]["id"] == 313
    assert data["country"]["iso2"] == "IN"
    assert data["country"]["name"] == "India"

    assert "risk" in data
    assert "events" in data


def test_country_detail_returns_404_for_unknown_country():
    response = client.get("/api/v1/countries/999999999")

    assert response.status_code == 404


# ============================================================
# Events
# ============================================================


def test_events_list_returns_data():
    response = client.get("/api/events")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_event_detail_returns_existing_event():
    events_response = client.get("/api/events")

    assert events_response.status_code == 200

    events = events_response.json()

    assert len(events) > 0

    event_id = events[0]["id"]

    response = client.get(
        f"/api/events/{event_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == event_id


def test_event_detail_returns_404_for_unknown_event():
    response = client.get(
        "/api/events/"
        "00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


# ============================================================
# Situation
# ============================================================


def test_situation_returns_expected_structure():
    response = client.get("/api/v1/situation")

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "top_risk",
        "deterioration_24h",
        "improvement_24h",
        "relevant_events",
    }


def test_situation_country_lists_are_lists():
    response = client.get("/api/v1/situation")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["top_risk"], list)
    assert isinstance(data["deterioration_24h"], list)
    assert isinstance(data["improvement_24h"], list)
    assert isinstance(data["relevant_events"], list)


def test_situation_top_risk_has_expected_fields():
    response = client.get("/api/v1/situation")

    assert response.status_code == 200

    data = response.json()

    if not data["top_risk"]:
        return

    country = data["top_risk"][0]

    assert "country_id" in country
    assert "iso2" in country
    assert "name" in country
    assert "timestamp" in country
    assert "country_risk" in country
    assert "confidence" in country
    assert "trend" in country

    assert isinstance(country["country_id"], int)
    assert isinstance(country["iso2"], str)
    assert isinstance(country["name"], str)
    assert isinstance(country["country_risk"], (int, float))


def test_situation_relevant_events_have_expected_fields():
    response = client.get("/api/v1/situation")

    assert response.status_code == 200

    data = response.json()

    if not data["relevant_events"]:
        return

    event = data["relevant_events"][0]

    assert "id" in event
    assert "title" in event
    assert "status" in event
    assert "severity" in event
    assert "escalation_score" in event
    assert "time_start" in event
    assert "confidence" in event

    assert isinstance(event["id"], str)
    assert isinstance(event["title"], str)
    assert isinstance(event["status"], str)
    assert isinstance(event["severity"], str)


# ============================================================
# Search
# ============================================================


def test_search_returns_expected_structure():
    response = client.get(
        "/api/v1/search",
        params={"q": "India"},
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "query",
        "countries",
        "events",
    }

    assert data["query"] == "India"
    assert isinstance(data["countries"], list)
    assert isinstance(data["events"], list)


def test_search_finds_country_by_english_name():
    response = client.get(
        "/api/v1/search",
        params={"q": "India"},
    )

    assert response.status_code == 200

    data = response.json()

    assert any(
        country["iso2"] == "IN"
        for country in data["countries"]
    )


def test_search_finds_country_by_iso2():
    response = client.get(
        "/api/v1/search",
        params={"q": "IN"},
    )

    assert response.status_code == 200

    data = response.json()

    assert any(
        country["iso2"] == "IN"
        for country in data["countries"]
    )


def test_search_finds_event():
    response = client.get(
        "/api/v1/search",
        params={"q": "fronterizos"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["events"], list)

    assert any(
        "fronterizos" in event["title"].lower()
        for event in data["events"]
    )


def test_search_rejects_empty_query():
    response = client.get(
        "/api/v1/search",
        params={"q": ""},
    )

    assert response.status_code == 422


# ============================================================
# Risk recalculation
# ============================================================


def test_risk_recalculate_existing_country():
    response = client.post(
        "/api/risk/recalculate/313"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["country_id"] == 313

    assert "country_risk" in data
    assert "confidence" in data

    assert isinstance(
        data["country_risk"],
        (int, float),
    )


def test_risk_recalculate_unknown_country():
    response = client.post(
        "/api/risk/recalculate/999999999"
    )

    assert response.status_code == 404