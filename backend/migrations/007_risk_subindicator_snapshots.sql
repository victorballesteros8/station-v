CREATE TABLE IF NOT EXISTS risk_subindicator_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id BIGINT NOT NULL,
    subindicator_id SMALLINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    score NUMERIC(5,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT risk_subindicator_snapshots_country_fk
        FOREIGN KEY (country_id)
        REFERENCES countries(id),

    CONSTRAINT risk_subindicator_snapshots_subindicator_fk
        FOREIGN KEY (subindicator_id)
        REFERENCES subindicators(id),

    CONSTRAINT risk_subindicator_snapshots_score_range
        CHECK (score >= 0 AND score <= 100)
);

CREATE INDEX IF NOT EXISTS idx_risk_subindicator_snapshots_country_subindicator_timestamp
    ON risk_subindicator_snapshots (
        country_id,
        subindicator_id,
        timestamp DESC
    );