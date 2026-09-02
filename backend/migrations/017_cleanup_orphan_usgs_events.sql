-- Cleanup of two historical orphan USGS events.
-- These events have no evidence, risk impacts, relations, actors or countries.
-- Their event_versions and event_timeline rows are removed through FK CASCADE.

DELETE FROM events
WHERE id IN (
    '232dc3a4-02a8-4162-84c7-4d46731e5cc3',
    '5e68dd44-e37e-4b63-be4d-da2ae38fbd1a'
);