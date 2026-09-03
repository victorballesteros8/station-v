from __future__ import annotations

import json
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GDACS_API_URL = (
    "https://www.gdacs.org/"
    "gdacsapi/api/events/geteventlist/SEARCH"
)
GDACS_EVENT_DATA_URL = (
    "https://www.gdacs.org/"
    "gdacsapi/api/events/geteventdata"
)

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_DETAIL_TIMEOUT_SECONDS = 60
DEFAULT_PAGE_SIZE = 100


class GDACSClientError(RuntimeError):
    """Error al consultar la API de GDACS."""


def _fetch_json(
    *,
    url: str,
    timeout: int,
) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "STATION-V/1.0",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status == 204:
                return {}

            raw_payload = response.read()

    except HTTPError as exc:
        raise GDACSClientError(
            f"GDACS API returned HTTP {exc.code}"
        ) from exc

    except URLError as exc:
        raise GDACSClientError(
            f"GDACS API request failed: {exc.reason}"
        ) from exc

    except TimeoutError as exc:
        raise GDACSClientError(
            "GDACS API request timed out"
        ) from exc

    try:
        payload = json.loads(raw_payload.decode("utf-8"))
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise GDACSClientError(
            "GDACS API returned invalid JSON"
        ) from exc

    if not isinstance(payload, dict):
        raise GDACSClientError(
            "GDACS API response must be a JSON object"
        )

    return payload


def _fetch_gdacs_page(
    *,
    from_date: date,
    to_date: date,
    event_type: str,
    alert_levels: tuple[str, ...] | None,
    page_number: int,
    page_size: int,
) -> dict[str, Any]:
    params: dict[str, str] = {
        "eventlist": event_type,
        "fromdate": from_date.isoformat(),
        "todate": to_date.isoformat(),
        "pagenumber": str(page_number),
        "pagesize": str(page_size),
    }

    if alert_levels:
        params["alertlevel"] = ";".join(alert_levels)

    url = f"{GDACS_API_URL}?{urlencode(params)}"
    return _fetch_json(
        url=url,
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )


def fetch_gdacs_event(
    *,
    event_id: str,
    event_type: str = "EQ",
) -> dict[str, Any]:
    """Fetch one complete GDACS event by its stable event identifier."""
    if not event_id:
        raise ValueError("event_id is required")

    params = {
        "eventtype": event_type,
        "eventid": event_id,
    }
    url = f"{GDACS_EVENT_DATA_URL}?{urlencode(params)}"

    payload = _fetch_json(
        url=url,
        timeout=DEFAULT_DETAIL_TIMEOUT_SECONDS,
    )

    if "properties" not in payload:
        raise GDACSClientError(
            "GDACS event detail response has no properties object"
        )

    return payload


def fetch_gdacs_events(
    *,
    from_date: date,
    to_date: date,
    event_type: str = "EQ",
    alert_levels: tuple[str, ...] | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict[str, Any]:
    if page_size <= 0:
        raise ValueError(
            "page_size must be greater than zero"
        )

    features: list[Any] = []
    page_number = 1

    while True:
        payload = _fetch_gdacs_page(
            from_date=from_date,
            to_date=to_date,
            event_type=event_type,
            alert_levels=alert_levels,
            page_number=page_number,
            page_size=page_size,
        )

        page_features = payload.get("features")

        if not isinstance(page_features, list):
            raise GDACSClientError(
                "GDACS response has no valid features list"
            )

        features.extend(page_features)

        if len(page_features) < page_size:
            break

        page_number += 1

    result: dict[str, Any] = {
        "type": payload.get(
            "type",
            "FeatureCollection",
        ),
        "features": features,
    }

    if "bbox" in payload:
        result["bbox"] = payload["bbox"]

    return result
