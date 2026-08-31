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

def test_event_detail_returns_timeline():
    event_id = "34a5118f-8b83-435e-948e-66bb69f13526"

    response = client.get(
        f"/api/events/{event_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert "timeline" in data
    assert isinstance(data["timeline"], list)
    assert len(data["timeline"]) >= 1

    first_entry = data["timeline"][0]

    assert "timestamp" in first_entry
    assert "update_type" in first_entry
    assert "description" in first_entry
    assert "version" in first_entry

def test_event_detail_timeline_is_ordered():
    event_id = "34a5118f-8b83-435e-948e-66bb69f13526"

    response = client.get(
        f"/api/events/{event_id}"
    )

    assert response.status_code == 200

    timeline = response.json()["timeline"]

    timestamps = [
        entry["timestamp"]
        for entry in timeline
    ]

    assert timestamps == sorted(timestamps)

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
        "global_risk",
    }

def test_situation_global_risk_has_expected_fields():
    response = client.get("/api/v1/situation")

    assert response.status_code == 200

    data = response.json()
    global_risk = data["global_risk"]

    assert set(global_risk.keys()) == {
        "value",
        "coverage_global",
        "coverage_systemic",
        "coverage_status",
    }

    assert isinstance(
        global_risk["value"],
        (int, float),
    )

    assert isinstance(
        global_risk["coverage_global"],
        (int, float),
    )

    assert isinstance(
        global_risk["coverage_systemic"],
        (int, float),
    )

    assert global_risk["coverage_status"] in {
        "insufficient",
        "provisional",
        "operational",
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

def test_event_patch_creates_new_version(test_event_id):
    event_id = str(test_event_id)

    before = client.get(
        f"/api/events/{event_id}"
    )

    assert before.status_code == 200

    previous_version = before.json()["version"]

    response = client.patch(
        f"/api/events/{event_id}",
        json={
            "title": "Evento de prueba — API",
            "update_type": "general_update",
            "description": "Actualización realizada mediante la API.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["event_id"] == event_id
    assert data["version"] == previous_version + 1
    assert data["update_type"] == "general_update"
    assert data["description"] == (
        "Actualización realizada mediante la API."
    )

    after = client.get(
        f"/api/events/{event_id}"
    )

    assert after.status_code == 200

    after_data = after.json()

    assert after_data["version"] == previous_version + 1
    assert after_data["title"] == "Evento de prueba — API"

def test_event_patch_returns_404_for_unknown_event():
    response = client.patch(
        "/api/events/00000000-0000-0000-0000-000000000000",
        json={
            "update_type": "general_update",
            "description": "Evento inexistente.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_event_patch_rejects_invalid_update_type():
    event_id = "34a5118f-8b83-435e-948e-66bb69f13526"

    response = client.patch(
        f"/api/events/{event_id}",
        json={
            "update_type": "invalid_type",
            "description": "Tipo inválido.",
        },
    )

    assert response.status_code == 422
    assert "Invalid update_type" in response.json()["detail"]


def test_event_patch_preserves_unchanged_fields(test_event_id):
    event_id = str(test_event_id)

    before = client.get(
        f"/api/events/{event_id}"
    )

    assert before.status_code == 200

    before_data = before.json()

    response = client.patch(
        f"/api/events/{event_id}",
        json={
            "title": "Evento de prueba — actualizado",
            "update_type": "general_update",
            "description": "Actualización informativa.",
        },
    )

    assert response.status_code == 200

    after = client.get(
        f"/api/events/{event_id}"
    )

    assert after.status_code == 200

    after_data = after.json()

    assert after_data["version"] == before_data["version"] + 1

    assert after_data["title"] == (
        "Evento de prueba — actualizado"
    )

    assert after_data["category"] == before_data["category"]
    assert after_data["subtype"] == before_data["subtype"]
    assert after_data["status"] == before_data["status"]
    assert after_data["severity"] == before_data["severity"]
    assert after_data["confidence"] == before_data["confidence"]
    assert after_data["escalation_score"] == (
        before_data["escalation_score"]
    )

def test_global_risk_returns_expected_structure():
    response = client.get(
        "/api/risk/global"
    )

    assert response.status_code == 200

    data = response.json()

    assert set(data.keys()) == {
        "global_risk",
        "tier1_pressure",
        "tier1_intensity",
        "tier1_average",
        "tier1_breadth",
        "tier2_pressure",
        "tier3_pressure",
        "coverage_global",
        "coverage_systemic",
        "coverage_status",
    }

    assert isinstance(
        data["global_risk"],
        (int, float),
    )

    assert isinstance(
        data["coverage_global"],
        (int, float),
    )

    assert isinstance(
        data["coverage_systemic"],
        (int, float),
    )

    assert data["coverage_status"] in {
        "insufficient",
        "provisional",
        "operational",
    }
