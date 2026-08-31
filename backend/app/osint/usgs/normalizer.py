from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class USGSEarthquake:
    external_id: str
    source_url: str | None

    time: datetime | None
    updated: datetime | None

    magnitude: float | None
    place: str | None

    latitude: float | None
    longitude: float | None
    depth: float | None

    alert: str | None
    significance: int | None
    tsunami: int | None

    felt: int | None
    mmi: float | None
    cdi: float | None


class USGSNormalizationError(ValueError):
    """Error al normalizar un registro de USGS."""


def _timestamp_from_milliseconds(
    value: Any,
) -> datetime | None:
    if value is None:
        return None

    if not isinstance(value, (int, float)):
        raise USGSNormalizationError(
            "USGS timestamp must be numeric"
        )

    return datetime.fromtimestamp(
        value / 1000,
        tz=timezone.utc,
    )


def _number_or_none(
    value: Any,
) -> float | None:
    if value is None:
        return None

    if isinstance(value, bool):
        raise USGSNormalizationError(
            "USGS numeric value cannot be boolean"
        )

    if not isinstance(value, (int, float)):
        raise USGSNormalizationError(
            "USGS numeric value must be numeric"
        )

    return float(value)


def normalize_usgs_feature(
    feature: dict[str, Any],
) -> USGSEarthquake:
    if not isinstance(feature, dict):
        raise USGSNormalizationError(
            "USGS feature must be an object"
        )

    external_id = feature.get("id")

    if not isinstance(external_id, str) or not external_id:
        raise USGSNormalizationError(
            "USGS feature has no valid external id"
        )

    properties = feature.get("properties")

    if not isinstance(properties, dict):
        raise USGSNormalizationError(
            "USGS feature has no valid properties object"
        )

    geometry = feature.get("geometry")

    coordinates = (
        geometry.get("coordinates")
        if isinstance(geometry, dict)
        else None
    )

    latitude = None
    longitude = None
    depth = None

    if coordinates is not None:
        if (
            not isinstance(coordinates, list)
            or len(coordinates) < 3
        ):
            raise USGSNormalizationError(
                "USGS geometry coordinates are invalid"
            )

        longitude = _number_or_none(coordinates[0])
        latitude = _number_or_none(coordinates[1])
        depth = _number_or_none(coordinates[2])

    return USGSEarthquake(
        external_id=external_id,
        source_url=(
            properties.get("url")
            if isinstance(properties.get("url"), str)
            else None
        ),
        time=_timestamp_from_milliseconds(
            properties.get("time")
        ),
        updated=_timestamp_from_milliseconds(
            properties.get("updated")
        ),
        magnitude=_number_or_none(
            properties.get("mag")
        ),
        place=(
            properties.get("place")
            if isinstance(properties.get("place"), str)
            else None
        ),
        latitude=latitude,
        longitude=longitude,
        depth=depth,
        alert=(
            properties.get("alert")
            if isinstance(properties.get("alert"), str)
            else None
        ),
        significance=(
            int(properties["sig"])
            if isinstance(properties.get("sig"), (int, float))
            and not isinstance(properties.get("sig"), bool)
            else None
        ),
        tsunami=(
            int(properties["tsunami"])
            if isinstance(properties.get("tsunami"), (int, float))
            and not isinstance(properties.get("tsunami"), bool)
            else None
        ),
        felt=(
            int(properties["felt"])
            if isinstance(properties.get("felt"), (int, float))
            and not isinstance(properties.get("felt"), bool)
            else None
        ),
        mmi=_number_or_none(
            properties.get("mmi")
        ),
        cdi=_number_or_none(
            properties.get("cdi")
        ),
    )


def normalize_usgs_feed(
    payload: dict[str, Any],
) -> list[USGSEarthquake]:
    features = payload.get("features")

    if not isinstance(features, list):
        raise USGSNormalizationError(
            "USGS feed has no valid features list"
        )

    earthquakes: list[USGSEarthquake] = []

    for feature in features:
        earthquakes.append(
            normalize_usgs_feature(feature)
        )

    return earthquakes