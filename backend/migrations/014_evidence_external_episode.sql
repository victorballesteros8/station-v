BEGIN;

-- V1 keeps the source event identity separate from a source-specific
-- update/episode identity. This is required for feeds such as GDACS,
-- where several episodes belong to the same source event.

ALTER TABLE evidence
    ADD COLUMN IF NOT EXISTS external_episode_id VARCHAR(255);

-- Migration 010 made (source_id, external_id) unique. That is correct for
-- sources such as USGS, but not for GDACS where multiple episodes share the
-- same event id. Replace it with a NULL-safe uniqueness rule.
DROP INDEX IF EXISTS idx_evidence_source_external_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_evidence_source_external_event_episode
    ON evidence (
        source_id,
        external_id,
        COALESCE(external_episode_id, '')
    );

-- Normalize the GDACS records already ingested with the old eventid:episodeid
-- composite representation.
UPDATE evidence e
SET
    external_episode_id = split_part(e.external_id, ':', 2),
    external_id = split_part(e.external_id, ':', 1)
FROM sources s
WHERE e.source_id = s.id
  AND s.name = 'GDACS'
  AND e.external_id LIKE '%:%'
  AND e.external_episode_id IS NULL;

COMMIT;
