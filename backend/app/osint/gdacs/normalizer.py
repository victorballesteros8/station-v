from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


class GDACSNormalizationError(ValueError):
    """Error al normalizar un registro de GDACS."""


@dataclass(frozen=True)
class GDACSEarthquake:
    event_id: str
    episode_id: str | None

    event_type: str
    alert_level: str | None
    alert_score: float | None

    event_name: str | None
    country: str | None
    country_iso3: str | None

    latitude: float | None
    longitude: float | None
    magnitude: float | None
    depth: float | None

    event_time: datetime | None
    update_time: datetime | None

    source: str | None

    geometry_url: str | None
    report_url: str | None
    details_url: str | None


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise GDACSNormalizationError(
            "GDACS string value must be a string"
        )

    return value or None


def _number_or_none(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, bool):
        raise GDACSNormalizationError(
            "GDACS numeric value cannot be boolean"
        )

    if not isinstance(value, (int, float)):
        raise GDACSNormalizationError(
            "GDACS numeric value must be numeric"
        )

    return float(value)


def _datetime_or_none(value: Any) -> datetime | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise GDACSNormalizationError(
            "GDACS datetime value must be a string"
        )

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise GDACSNormalizationError(
            f"Invalid GDACS datetime: {value}"
        ) from exc


def _properties(
    feature: dict[str, Any],
) -> dict[str, Any]:
    properties = feature.get("properties")

    if not isinstance(properties, dict):
        raise GDACSNormalizationError(
            "GDACS feature has no valid properties object"
        )

    return properties


def _get_value(
    properties: dict[str, Any],
    *names: str,
) -> Any:
    for name in names:
        if name in properties:
            return properties[name]

    return None


def _extract_coordinates(
    feature: dict[str, Any],
) -> tuple[float | None, float | None]:
    geometry = feature.get("geometry")

    if geometry is None:
        return None, None

    if not isinstance(geometry, dict):
        raise GDACSNormalizationError(
            "GDACS geometry must be an object"
        )

    coordinates = geometry.get("coordinates")

    if coordinates is None:
        return None, None

    if (
        not isinstance(coordinates, list)
        or len(coordinates) < 2
    ):
        raise GDACSNormalizationError(
            "GDACS geometry coordinates are invalid"
        )

    longitude = _number_or_none(coordinates[0])
    latitude = _number_or_none(coordinates[1])

    return latitude, longitude


def _extract_urls(
    properties: dict[str, Any],
) -> tuple[str | None, str | None, str | None]:
    urls = properties.get("url")

    if urls is None:
        return None, None, None

    if not isinstance(urls, dict):
        raise GDACSNormalizationError(
            "GDACS url field must be an object"
        )

    return (
        _string_or_none(urls.get("geometry")),
        _string_or_none(urls.get("report")),
        _string_or_none(urls.get("details")),
    )


def _extract_depth(
    properties: dict[str, Any],
) -> float | None:
    severitydata = properties.get("severitydata")

    if isinstance(severitydata, dict):
        depth = severitydata.get("depth")

        if depth is not None:
            return _number_or_none(depth)

        severity_text = severitydata.get("severitytext")

        if isinstance(severity_text, str):
            marker = "Depth:"

            if marker in severity_text:
                value = severity_text.split(
                    marker,
                    1,
                )[1].split(",", 1)[0].strip()

                value = value.removesuffix("km").strip()

                try:
                    return float(value)
                except ValueError:
                    pass

    return _number_or_none(
        properties.get("depth")
    )


def _extract_magnitude(
    properties: dict[str, Any],
) -> float | None:
    severitydata = properties.get("severitydata")

    if isinstance(severitydata, dict):
        severity = severitydata.get("severity")

        if severity is not None:
            return _number_or_none(severity)

    return _number_or_none(
        _get_value(
            properties,
            "magnitude",
            "mag",
        )
    )


def normalize_gdacs_feature(
    feature: dict[str, Any],
) -> GDACSEarthquake:
    if not isinstance(feature, dict):
        raise GDACSNormalizationError(
            "GDACS feature must be an object"
        )

    properties = _properties(feature)

    event_id = _get_value(
        properties,
        "eventid",
        "event_id",
    )

    if event_id is None:
        raise GDACSNormalizationError(
            "GDACS feature has no valid event id"
        )

    if isinstance(event_id, bool) or not isinstance(
        event_id,
        (int, str),
    ):
        raise GDACSNormalizationError(
            "GDACS event id must be numeric or string"
        )

    event_id = str(event_id)

    episode_id = _get_value(
        properties,
        "episodeid",
        "episode_id",
    )

    if episode_id is not None:
        if isinstance(episode_id, bool) or not isinstance(
            episode_id,
            (int, str),
        ):
            raise GDACSNormalizationError(
                "GDACS episode id must be numeric or string"
            )

        episode_id = str(episode_id)

    event_type = _string_or_none(
        _get_value(
            properties,
            "eventtype",
            "event_type",
        )
    )

    if event_type is None:
        raise GDACSNormalizationError(
            "GDACS feature has no valid event type"
        )

    if event_type != "EQ":
        raise GDACSNormalizationError(
            f"Unsupported GDACS event type: {event_type}"
        )

    latitude, longitude = _extract_coordinates(
        feature
    )

    geometry_url, report_url, details_url = (
        _extract_urls(properties)
    )

    event_name = _string_or_none(
        properties.get("eventname")
    )

    if event_name is None:
        event_name = _string_or_none(
            properties.get("name")
        )

    if event_name is None:
        event_name = _string_or_none(
            properties.get("description")
        )

    country = _string_or_none(
        properties.get("country")
    )

    country_iso3 = _string_or_none(
        properties.get("iso3")
    )

    return GDACSEarthquake(
        event_id=event_id,
        episode_id=episode_id,
        event_type=event_type,
        alert_level=_string_or_none(
            properties.get("alertlevel")
        ),
        alert_score=_number_or_none(
            properties.get("alertscore")
        ),
        event_name=event_name,
        country=country,
        country_iso3=country_iso3,
        latitude=latitude,
        longitude=longitude,
        magnitude=_extract_magnitude(
            properties
        ),
        depth=_extract_depth(
            properties
        ),
        event_time=_datetime_or_none(
            _get_value(
                properties,
                "fromdate",
                "event_time",
                "eventtime",
            )
        ),
        update_time=_datetime_or_none(
            _get_value(
                properties,
                "datemodified",
                "update_time",
                "updatetime",
                "updated",
            )
        ),
        source=_string_or_none(
            properties.get("source")
        ),
        geometry_url=geometry_url,
        report_url=report_url,
        details_url=details_url,
    )


def normalize_gdacs_feed(
    payload: dict[str, Any],
) -> list[GDACSEarthquake]:
    if not isinstance(payload, dict):
        raise GDACSNormalizationError(
            "GDACS response must be an object"
        )

    features = payload.get("features")

    if not isinstance(features, list):
        raise GDACSNormalizationError(
            "GDACS response has no valid features list"
        )

    earthquakes: list[GDACSEarthquake] = []

    for feature in features:
        earthquakes.append(
            normalize_gdacs_feature(feature)
        )

    return earthquakes