ALTER TABLE risk_impacts
    ADD COLUMN IF NOT EXISTS temporal_weight NUMERIC(6,4),
    ADD COLUMN IF NOT EXISTS repetition_weight NUMERIC(6,4),
    ADD COLUMN IF NOT EXISTS effective_impact NUMERIC(8,4);

ALTER TABLE risk_impacts
    ADD CONSTRAINT risk_impacts_temporal_weight_range
        CHECK (
            temporal_weight IS NULL
            OR (temporal_weight >= 0 AND temporal_weight <= 1)
        );

ALTER TABLE risk_impacts
    ADD CONSTRAINT risk_impacts_repetition_weight_range
        CHECK (
            repetition_weight IS NULL
            OR (repetition_weight >= 0 AND repetition_weight <= 1)
        );

ALTER TABLE risk_impacts
    ADD CONSTRAINT risk_impacts_effective_impact_range
        CHECK (
            effective_impact IS NULL
            OR (effective_impact >= 0 AND effective_impact <= 100)
        );