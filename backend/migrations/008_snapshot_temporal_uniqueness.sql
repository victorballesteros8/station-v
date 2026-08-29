CREATE UNIQUE INDEX IF NOT EXISTS
    uq_risk_subindicator_snapshots_country_subindicator_timestamp
ON risk_subindicator_snapshots (
    country_id,
    subindicator_id,
    timestamp
);

CREATE UNIQUE INDEX IF NOT EXISTS
    uq_risk_snapshots_country_timestamp
ON risk_snapshots (
    country_id,
    timestamp
);