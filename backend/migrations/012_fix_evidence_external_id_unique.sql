BEGIN;

DROP INDEX IF EXISTS idx_evidence_source_external_id;

CREATE UNIQUE INDEX idx_evidence_source_external_id
    ON evidence (source_id, external_id);

COMMIT;