BEGIN;

ALTER TABLE evidence
    ADD COLUMN external_id VARCHAR(255);

CREATE UNIQUE INDEX idx_evidence_source_external_id
    ON evidence (source_id, external_id);

COMMIT;