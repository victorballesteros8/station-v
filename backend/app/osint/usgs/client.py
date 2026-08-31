from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USGS_FEED_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "summary/all_day.geojson"
)


class USGSClientError(RuntimeError):
    """Error al consultar la API pública de USGS."""


def fetch_usgs_feed(
    url: str = USGS_FEED_URL,
    timeout: float = 15.0,
) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "STATION-V/1.0",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()

    except HTTPError as exc:
        raise USGSClientError(
            f"USGS HTTP error: {exc.code}"
        ) from exc

    except URLError as exc:
        raise USGSClientError(
            f"USGS connection error: {exc.reason}"
        ) from exc

    except TimeoutError as exc:
        raise USGSClientError(
            "USGS request timed out"
        ) from exc

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise USGSClientError(
            "USGS returned invalid JSON"
        ) from exc

    if not isinstance(payload, dict):
        raise USGSClientError(
            "USGS response is not a JSON object"
        )

    return payload