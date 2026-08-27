"""Load Natural Earth Admin 0 country geometries into STATION V.

The country catalogue is authoritative in the database. Natural Earth is used
only as a cartographic geometry source. Therefore this script updates existing
country rows and never creates new countries from Natural Earth records.

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
DEFAULT_DATABASE_URL = "postgresql://station_v:station_v_dev@localhost:5432/station_v"

# Natural Earth uses -99 for France and Norway in this dataset and also has
# special/non-standard records. These aliases are deliberately explicit so
# cartographic names can be mapped to the STATION V country catalogue.
NAME_ALIASES = {
    "France": "FRA",
    "Norway": "NOR",
    "Palestine": "PSE",
    "Kosovo": "XKX",
    "Taiwan": "TWN",
}


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

    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

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

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, iso2, iso3, name FROM countries")
            catalogue = cur.fetchall()

            by_iso2 = {row[1]: row[0] for row in catalogue}
            by_iso3 = {row[2]: row[0] for row in catalogue}
            by_name = {row[3].casefold(): row[0] for row in catalogue}

            updated = set()
            unmatched = []
            invalid = []

            for _, row in gdf.iterrows():
                iso2 = str(row["ISO_A2"]).strip().upper()
                iso3 = str(row["ISO_A3"]).strip().upper()
                name = str(row["NAME"]).strip()

                country_id = None
                if len(iso2) == 2 and iso2 in by_iso2:
                    country_id = by_iso2[iso2]
                elif len(iso3) == 3 and iso3 in by_iso3:
                    country_id = by_iso3[iso3]
                elif name in NAME_ALIASES and NAME_ALIASES[name] in by_iso3:
                    country_id = by_iso3[NAME_ALIASES[name]]
                elif name.casefold() in by_name:
                    country_id = by_name[name.casefold()]

                if country_id is None:
                    continue

                geometry = normalize_geometry(row.geometry)
                if geometry is None:
                    invalid.append(name)
                    continue

                cur.execute(
                    """
                    UPDATE countries
                    SET geometry = ST_GeomFromWKB(%s, 4326),
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (bytes.fromhex(geometry.wkb_hex), country_id),
                )
                updated.add(country_id)

            cur.execute(
                """
                SELECT iso3, name
                FROM countries
                WHERE geometry IS NULL
                ORDER BY iso3
                """
            )
            unmatched = cur.fetchall()

        conn.commit()

    print(f"Updated geometries for {len(updated)} / {len(catalogue)} catalogue countries.")

    if invalid:
        print("Invalid/empty geometries:", ", ".join(invalid))

    if unmatched:
        print("Countries without geometry:")
        for iso3, name in unmatched:
            print(f"  {iso3} - {name}")
        return 1

    print("All STATION V catalogue countries have a geometry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
