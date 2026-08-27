BEGIN;

-- Event classification and lifecycle values are constrained in the database
-- rather than represented as PostgreSQL ENUM types.

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL CHECK (category IN (
        'conflict_violence',
        'protests_unrest',
        'military_activity',
        'border_tension',
        'political_crisis',
        'disaster',
        'critical_infrastructure',
        'security_terrorism'
    )),
    subtype TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    analyst_summary TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    location GEOMETRY(POINT, 4326),
    status TEXT NOT NULL DEFAULT 'emerging' CHECK (status IN (
        'emerging',
        'active',
        'stable',
        'decreasing',
        'finished'
    )),
    severity TEXT NOT NULL DEFAULT 'info' CHECK (severity IN (
        'info',
        'low',
        'medium',
        'high',
        'critical'
    )),
    escalation_score NUMERIC(4,2) CHECK (
        escalation_score IS NULL
        OR (escalation_score >= 0 AND escalation_score <= 10)
    ),
    confidence TEXT NOT NULL DEFAULT 'medium' CHECK (confidence IN (
        'low',
        'medium',
        'high'
    )),
    first_detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_evidence_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT events_escalation_requires_high_severity CHECK (
        severity IN ('high', 'critical') OR escalation_score IS NULL
    ),
    CONSTRAINT events_time_order CHECK (
        end_time IS NULL OR start_time IS NULL OR end_time >= start_time
    )
);

CREATE INDEX idx_events_category ON events (category);
CREATE INDEX idx_events_status ON events (status);
CREATE INDEX idx_events_severity ON events (severity);
CREATE INDEX idx_events_escalation_score ON events (escalation_score DESC);
CREATE INDEX idx_events_start_time ON events (start_time DESC);
CREATE INDEX idx_events_location ON events USING GIST (location);

CREATE TABLE event_countries (
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    country_id SMALLINT NOT NULL REFERENCES countries(id) ON DELETE RESTRICT,
    relation_type TEXT NOT NULL DEFAULT 'affected' CHECK (relation_type IN (
        'affected',
        'origin',
        'target',
        'location',
        'transit'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (event_id, country_id, relation_type)
);

CREATE INDEX idx_event_countries_country ON event_countries (country_id);

CREATE TABLE event_actors (
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    actor_id UUID NOT NULL REFERENCES actors(id) ON DELETE RESTRICT,
    role TEXT NOT NULL CHECK (role IN (
        'participant',
        'target',
        'authority',
        'observer',
        'alleged_actor'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (event_id, actor_id, role)
);

CREATE INDEX idx_event_actors_actor ON event_actors (actor_id);

CREATE TABLE event_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    title TEXT,
    summary TEXT,
    status TEXT CHECK (status IS NULL OR status IN (
        'emerging',
        'active',
        'stable',
        'decreasing',
        'finished'
    )),
    severity TEXT CHECK (severity IS NULL OR severity IN (
        'info',
        'low',
        'medium',
        'high',
        'critical'
    )),
    escalation_score NUMERIC(4,2) CHECK (
        escalation_score IS NULL
        OR (escalation_score >= 0 AND escalation_score <= 10)
    ),
    confidence TEXT CHECK (confidence IS NULL OR confidence IN (
        'low',
        'medium',
        'high'
    )),
    change_summary TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (event_id, version_number),
    CONSTRAINT event_versions_escalation_requires_high_severity CHECK (
        severity IS NULL
        OR severity IN ('high', 'critical')
        OR escalation_score IS NULL
    )
);

CREATE INDEX idx_event_versions_event ON event_versions (event_id, version_number DESC);
CREATE INDEX idx_event_versions_recorded_at ON event_versions (recorded_at DESC);

CREATE TABLE event_relations (
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    related_event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL CHECK (relation_type IN (
        'related',
        'preceded_by',
        'followed_by',
        'escalation_of',
        'continuation_of',
        'duplicate_of'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (event_id, related_event_id, relation_type),
    CONSTRAINT event_relations_no_self CHECK (event_id <> related_event_id)
);

CREATE INDEX idx_event_relations_related ON event_relations (related_event_id);

CREATE TABLE event_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    occurred_at TIMESTAMPTZ NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_event_timeline_event ON event_timeline (event_id, occurred_at DESC);

COMMIT;
