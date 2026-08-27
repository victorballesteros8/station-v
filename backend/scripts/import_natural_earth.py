"""Import Natural Earth Admin 0 Countries into STATION V.

The raw Natural Earth ZIP is intentionally kept outside Git. This script reads
it locally and loads the selected fields and geometries into PostgreSQL/PostGIS.

Expected input:
    data/raw/natural-earth/ne_10m_admin_0_countries.zip

Requirements:
    geopandas
    psycopg[binary]
    shapely
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import geopandas as gpd
import psycopg
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ZIP = ROOT / "data" / "raw" / "natural-earth" / "ne_10m_admin_0_countries.zip"


def normalize_geometry(geometry):
    """Return a valid MultiPolygon geometry where possible."""
    if geometry is None or geometry.is_empty:
        return None

    geometry = make_valid(geometry)

    if geometry.geom_type == "Polygon":
        return MultiPolygon([geometry])
    if geometry.geom_type == "MultiPolygon":
        return geometry
    if isinstance(geometry, GeometryCollection):
        polygons = [g for g in geometry.geoms if isinstance(g, Polygon)]
        if polygons:
            return MultiPolygon(polygons)

    raise ValueError(f"Unsupported geometry type after validation: {geometry.geom_type}")


def main() -> int:
    zip_path = Path(os.getenv("NATURAL_EARTH_ZIP", DEFAULT_ZIP))

    if not zip_path.exists():
        print(f"ERROR: Natural Earth ZIP not found: {zip_path}")
        return 1

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://station_v:station_v@localhost:5432/station_v",
    )

    print(f"Reading: {zip_path}")
    gdf = gpd.read_file(f"zip://{zip_path}")

    required = {"ISO_A2", "ISO_A3", "NAME", "geometry"}
    missing = required - set(gdf.columns)
    if missing:
        print(f"ERROR: Missing required Natural Earth fields: {sorted(missing)}")
        return 1

    if gdf.crs is None:
        print("ERROR: Natural Earth dataset has no CRS.")
        return 1

    gdf = gdf.to_crs("EPSG:4326")

    rows = []
    skipped = []

    for _, row in gdf.iterrows():
        iso2 = str(row["ISO_A2"]).strip().upper()
        iso3 = str(row["ISO_A3"]).strip().upper()
        name = str(row["NAME"]).strip()

        # Natural Earth uses -99 for some non-standard ISO fields. Those
        # records are not suitable for the countries table's ISO constraints.
        if len(iso2) != 2 or iso2 == "-9" or len(iso3) != 3 or iso3 == "-99":
            skipped.append(name)
            continue

        geometry = normalize_geometry(row.geometry)
        if geometry is None:
            skipped.append(name)
            continue

        rows.append((iso2, iso3, name, geometry.wkb_hex))

    print(f"Prepared {len(rows)} countries; skipped {len(skipped)} records.")
    if skipped:
        print("Skipped records:", ", ".join(skipped))

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            for iso2, iso3, name, geometry_wkb in rows:
                cur.execute(
                    """
                    INSERT INTO countries (iso2, iso3, name, geometry)
                    VALUES (%s, %s, %s, ST_GeomFromWKB(%s, 4326))
                    ON CONFLICT (iso2) DO UPDATE SET
                        iso3 = EXCLUDED.iso3,
                        name = EXCLUDED.name,
                        geometry = EXCLUDED.geometry,
                        updated_at = now()
                    """,
                    (iso2, iso3, name, bytes.fromhex(geometry_wkb)),
                )

        conn.commit()

    print(f"Imported/updated {len(rows)} countries successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
