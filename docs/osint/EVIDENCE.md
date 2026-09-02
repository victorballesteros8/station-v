# STATION V — Structured Evidence

## Purpose

`EVIDENCE` is the common STATION V representation of information received from an external source.

The relational columns of `evidence` store fields that are common across sources: provenance, timestamps, title, URL, evidence type, source role, independence, quality and deduplication metadata.

Source-specific structured data shall be stored separately from those common fields so that integrating a new source does not require adding source-specific columns to the core evidence table.

## Structured data model

The evidence model shall support a generic structured payload for source-specific information.

Conceptually:

```text
EVIDENCE
├── common relational fields
└── structured_data
    └── source-specific normalized fields
```

Examples:

```text
USGS
├── external_id
├── magnitude
├── latitude
├── longitude
├── depth
├── tsunami
└── significance
```

```text
GDACS
├── external_id
├── alert_level
├── disaster_type
├── severity
└── source-specific metadata
```

```text
GDELT
├── external_id
├── source_url
├── language
├── publisher
└── source-specific metadata
```

These examples describe the pattern and are not a complete schema for each connector.

## Principles

1. Common evidence fields remain relational and queryable.
2. Source-specific fields use structured storage and must preserve their source semantics.
3. The structured payload must not replace provenance fields such as `source_id`, `external_id`, timestamps or URL.
4. Raw/source-specific data must not be silently converted into STATION V analytical fields such as severity, Escalation Score or Country Risk.
5. Normalization must not invent precision or information that the source does not provide.
6. The structured payload must remain traceable to the originating source record.
7. A new source should normally be integrable without altering the core evidence schema.

## External identifier

The combination `(source_id, external_id)` identifies an external source record when the source provides a stable identifier.

`content_hash` has a different purpose and identifies the content representation used for deduplication or change detection. It must not be treated as a substitute for the source's external identifier when a stable identifier exists.

## Normalization boundary

Connector-specific code is responsible for converting the source payload into the normalized structured representation used by STATION V.

The generic evidence persistence layer is responsible for storing that representation and its common provenance metadata.

## Source-specific severity resolution

Source-specific structured values may participate in the resolution of STATION V `severity` when an explicit rule has been defined for that source and event type.

This resolution is distinct from evidence quality and `Confidence`: a source may provide a high-quality observation without the event necessarily having high severity, and a high-severity event does not imply high Country Risk.

For earthquake ingestion in V1.2, the detailed operational rules are defined in `docs/osint/USGS.md` and `docs/osint/GDACS.md`.

The common rule is:

- magnitude establishes a minimum severity;
- source-specific alert levels may establish a higher minimum where explicitly defined;
- objective impact signals may elevate severity;
- signals are not added together as points;
- the highest objectively supported severity prevails;
- a secondary signal never lowers a previously established minimum.

For USGS specifically:

- magnitude maps to `info`, `low`, `medium`, `high` and `critical` by the documented thresholds;
- PAGER/USGS alert maps to a minimum of `info`, `low`, `medium` or `high` for `green`, `yellow`, `orange` and `red` respectively;
- MMI VII elevates one level, while MMI VIII or IX+ elevates two levels;
- `tsunami = 1` elevates one level;
- `felt` is contextual and does not directly elevate severity in V1.2;
- `significance` is not used as an independent elevating signal to avoid double-counting a composite source metric.

For GDACS specifically:

- `green`, `orange` and `red` establish minimum severities of `info`, `medium` and `high` respectively;
- the same magnitude reference is applied;
- MMI and an explicit tsunami indicator may elevate when those fields are actually available and applicable;
- any additional objective signal requires an explicit rule before implementation.

USGS and GDACS severity values are not averaged. Independent evidence may support an update to the same EVENT through its versioning mechanism.

These rules are specific to the earthquake pipelines and must not be generalized automatically to other source types or event categories.

## Future evolution

The structured evidence model is intended to support additional sources such as GDACS, GDELT, UCDP, ReliefWeb and NASA FIRMS without redesigning the core `SOURCE → EVIDENCE → CLAIM → EVENT` chain.
