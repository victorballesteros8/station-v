BEGIN;

ALTER TABLE evidence
    ADD COLUMN structured_data JSONB;

CREATE INDEX idx_evidence_structured_data
    ON evidence USING GIN (structured_data);

COMMIT;