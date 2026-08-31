BEGIN;

CREATE UNIQUE INDEX idx_claims_evidence_type
    ON claims (evidence_id, claim_type);

COMMIT;