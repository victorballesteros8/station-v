from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EventLocation(BaseModel):
    lat: float
    lon: float


class EventCountry(BaseModel):
    id: int
    iso2: str
    name: str


class EventClaim(BaseModel):
    claim_type: str
    statement: str
    assertion_status: str
    confidence: str | None = None


class EventSource(BaseModel):
    id: UUID
    name: str
    tier: str
    source_class: str
    source_type: str
    reliability: float | None = None


class EventEvidence(BaseModel):
    id: UUID
    title: str | None = None
    url: str | None = None
    published_at: datetime | None = None
    evidence_type: str
    source_role: str
    relationship_to_event: str | None = None
    evidence_quality: float | None = None
    source: EventSource
    claims: list[EventClaim] = []

class EventUpdate(BaseModel):
    category: str | None = None
    subtype: str | None = None
    title: str | None = None
    summary: str | None = None
    analyst_summary: str | None = None
    status: str | None = None
    severity: str | None = None
    escalation_score: float | None = None
    confidence: str | None = None

    update_type: str
    description: str | None = None

class EventMapItem(BaseModel):
    id: UUID
    version: int
    category: str
    subtype: str
    title: str
    status: str
    severity: str
    escalation_score: float | None = None
    confidence: str
    location: EventLocation | None = None
    countries: list[EventCountry]
    updated_at: datetime

class EventDetail(BaseModel):
    id: UUID
    version: int
    category: str
    subtype: str
    title: str
    status: str
    severity: str
    escalation_score: float | None = None
    confidence: str
    location: EventLocation | None = None
    countries: list[EventCountry]
    updated_at: datetime
    evidence: list[EventEvidence] = []