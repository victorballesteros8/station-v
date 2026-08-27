BEGIN;

-- Migration 001 already created the event model. This migration hardens that
-- model with the V1 lifecycle/classification constraints and indexes.
-- Constraint creation is guarded so the migration is safe to rerun locally.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'event_versions_status_valid' AND conrelid = 'event_versions'::regclass) THEN
        ALTER TABLE event_versions ADD CONSTRAINT event_versions_status_valid
            CHECK (status IN ('emerging', 'active', 'stable', 'decreasing', 'finished'));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'event_versions_confidence_valid' AND conrelid = 'event_versions'::regclass) THEN
        ALTER TABLE event_versions ADD CONSTRAINT event_versions_confidence_valid
            CHECK (confidence IN ('low', 'medium', 'high'));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'event_versions_escalation_requires_high_severity' AND conrelid = 'event_versions'::regclass) THEN
        ALTER TABLE event_versions ADD CONSTRAINT event_versions_escalation_requires_high_severity
            CHECK (
                escalation_score IS NULL
                OR (severity IN ('high', 'critical') AND escalation_score >= 0 AND escalation_score <= 10)
            );
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'event_versions_time_order' AND conrelid = 'event_versions'::regclass) THEN
        ALTER TABLE event_versions ADD CONSTRAINT event_versions_time_order
            CHECK (time_end IS NULL OR time_start IS NULL OR time_end >= time_start);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'event_countries_relationship_valid' AND conrelid = 'event_countries'::regclass) THEN
        ALTER TABLE event_countries ADD CONSTRAINT event_countries_relationship_valid
            CHECK (relationship_type IN ('directly_affected', 'indirectly_affected'));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'event_actors_role_valid' AND conrelid = 'event_actors'::regclass) THEN
        ALTER TABLE event_actors ADD CONSTRAINT event_actors_role_valid
            CHECK (role IN ('participant', 'target', 'authority', 'observer', 'alleged_actor'));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'event_relations_type_valid' AND conrelid = 'event_relations'::regclass) THEN
        ALTER TABLE event_relations ADD CONSTRAINT event_relations_type_valid
            CHECK (relation_type IN ('related', 'preceded_by', 'followed_by', 'escalation_of', 'continuation_of', 'duplicate_of'));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_event_versions_recorded_at
    ON event_versions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_event_versions_escalation
    ON event_versions (escalation_score DESC);

CREATE INDEX IF NOT EXISTS idx_event_timeline_event_timestamp
    ON event_timeline (event_id, timestamp DESC);

COMMIT;
