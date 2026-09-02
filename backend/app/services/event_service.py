from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from backend.app.db import get_connection
from backend.app.schemas.events import EventUpdate


VALID_UPDATE_TYPES = {
    "general_update",
    "status_change",
    "severity_change",
    "new_evidence",
    "occurrence",
}


def _update_event_with_cursor(
    cur: Any,
    *,
    event_id: UUID,
    update: EventUpdate,
    now: datetime | None = None,
) -> dict:
    if update.update_type not in VALID_UPDATE_TYPES:
        raise ValueError(f"Invalid update_type: {update.update_type}")

    now = now or datetime.now(timezone.utc)

    cur.execute(
        """
        SELECT
            e.id,
            e.current_version_id,
            ev.version,
            ev.category,
            ev.subtype,
            ev.title,
            ev.summary,
            ev.analyst_summary,
            ev.location,
            ev.location_precision,
            ev.region,
            ev.place,
            ev.time_start,
            ev.time_end,
            ev.time_precision,
            ev.status,
            ev.severity,
            ev.escalation_score,
            ev.confidence,
            ev.confidence_score_internal,
            ev.canonical_data,
            ev.human_impact,
            ev.material_impact
        FROM events e
        JOIN event_versions ev
            ON ev.id = e.current_version_id
        WHERE e.id = %s
        FOR UPDATE
        """,
        (event_id,),
    )

    current = cur.fetchone()
    if current is None:
        raise LookupError("Event not found")

    (
        _event_id,
        _current_version_id,
        current_version,
        current_category,
        current_subtype,
        current_title,
        current_summary,
        current_analyst_summary,
        current_location,
        current_location_precision,
        current_region,
        current_place,
        current_time_start,
        current_time_end,
        current_time_precision,
        current_status,
        current_severity,
        current_escalation_score,
        current_confidence,
        current_confidence_score_internal,
        current_canonical_data,
        current_human_impact,
        current_material_impact,
    ) = current

    new_version_id = uuid4()
    new_version = current_version + 1

    category = update.category if update.category is not None else current_category
    subtype = update.subtype if update.subtype is not None else current_subtype
    title = update.title if update.title is not None else current_title
    summary = update.summary if update.summary is not None else current_summary
    analyst_summary = (
        update.analyst_summary
        if update.analyst_summary is not None
        else current_analyst_summary
    )
    status = update.status if update.status is not None else current_status
    severity = update.severity if update.severity is not None else current_severity
    escalation_score = (
        update.escalation_score
        if update.escalation_score is not None
        else current_escalation_score
    )
    confidence = update.confidence if update.confidence is not None else current_confidence

    cur.execute(
        """
        INSERT INTO event_versions (
            id,
            event_id,
            version,
            category,
            subtype,
            title,
            summary,
            analyst_summary,
            location,
            location_precision,
            region,
            place,
            time_start,
            time_end,
            time_precision,
            status,
            severity,
            escalation_score,
            confidence,
            confidence_score_internal,
            canonical_data,
            human_impact,
            material_impact,
            created_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        """,
        (
            new_version_id,
            event_id,
            new_version,
            category,
            subtype,
            title,
            summary,
            analyst_summary,
            current_location,
            current_location_precision,
            current_region,
            current_place,
            current_time_start,
            current_time_end,
            current_time_precision,
            status,
            severity,
            escalation_score,
            confidence,
            current_confidence_score_internal,
            current_canonical_data,
            current_human_impact,
            current_material_impact,
            now,
        ),
    )

    cur.execute(
        """
        UPDATE events
        SET current_version_id = %s, updated_at = %s
        WHERE id = %s
        """,
        (new_version_id, now, event_id),
    )

    cur.execute(
        """
        INSERT INTO event_timeline (
            event_id,
            timestamp,
            update_type,
            description,
            event_version_id
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (event_id, now, update.update_type, update.description, new_version_id),
    )

    return {
        "event_id": event_id,
        "version": new_version,
        "update_type": update.update_type,
        "description": update.description,
    }


def update_event(event_id: UUID, update: EventUpdate) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            result = _update_event_with_cursor(
                cur,
                event_id=event_id,
                update=update,
            )
        conn.commit()

    return result
