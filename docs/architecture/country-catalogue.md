# Country catalogue V1

The `countries` table is the authoritative STATION V analytical universe for V1.

Natural Earth is used as a cartographic source only. It does not determine which entities are included in the STATION V country universe.

## V1 rules

- ISO 3166-1 alpha-2 and alpha-3 are used as identifiers where officially assigned.
- Palestine is included as an active analytical country entity.
- Kosovo is included as a `special` analytical entity using the internal convention `XK` / `XKX`; this is not an official ISO 3166-1 assignment.
- Taiwan is included as a `special` analytical entity using `TW` / `TWN`.
- Territorial features, military bases, buffer zones, reefs, banks and other non-country cartographic units are not automatically promoted to `countries`.

## Geometry source

Country geometry is supplied separately by Natural Earth Admin 0 Countries 10m. Where Natural Earth does not provide an ISO code for a country of the STATION V analytical universe, the importer matches the geometry by its Natural Earth name mapping.

## Known special mappings

- France → `FR` / `FRA`
- Norway → `NO` / `NOR`
- Palestine → `PS` / `PSE`
- Kosovo → `XK` / `XKX` (STATION V internal convention)
- Taiwan → `TW` / `TWN`
