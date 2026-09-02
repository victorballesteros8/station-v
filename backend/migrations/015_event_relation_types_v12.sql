BEGIN;

-- V1.2: distinguish event relations that can establish repetition
-- from relations that only provide temporal/contextual linkage.

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'event_relations_type_valid'
          AND conrelid = 'event_relations'::regclass
    ) THEN
        ALTER TABLE event_relations
            DROP CONSTRAINT event_relations_type_valid;
    END IF;
END $$;

ALTER TABLE event_relations
    ADD CONSTRAINT event_relations_type_valid
    CHECK (
        relation_type IN (
            'related',
            'preceded_by',
            'followed_by',
            'escalation_of',
            'continuation_of',
            'same_series',
            'part_of',
            'duplicate_of'
        )
    );

CREATE INDEX IF NOT EXISTS idx_event_relations_type
    ON event_relations (relation_type);

COMMIT;
