BEGIN;

ALTER TABLE evidence
    ADD COLUMN event_id UUID
    REFERENCES events(id)
    ON DELETE CASCADE;

CREATE INDEX idx_evidence_event
    ON evidence(event_id);

COMMIT;