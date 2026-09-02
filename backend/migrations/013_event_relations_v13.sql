BEGIN;

-- Align persisted EVENT relations with Event Model V1.3.
-- Existing legacy values are normalized before the constraint is replaced.
-- continuation_of is represented as same_series in V1.3 because continuity
-- belongs to the same event sequence unless the relation is explicitly an
-- escalation or a part-of relationship.

UPDATE event_relations
SET relation_type = 'related_to'
WHERE relation_type = 'related';

UPDATE event_relations
SET relation_type = 'escalates'
WHERE relation_type = 'escalation_of';

UPDATE event_relations
SET relation_type = 'same_series'
WHERE relation_type = 'continuation_of';

ALTER TABLE event_relations
    DROP CONSTRAINT IF EXISTS event_relations_type_valid;

ALTER TABLE event_relations
    ADD CONSTRAINT event_relations_type_valid
    CHECK (
        relation_type IN (
            'preceded_by',
            'followed_by',
            'escalates',
            'part_of',
            'caused_by',
            'related_to',
            'same_series',
            'duplicate_of'
        )
    );

COMMIT;
