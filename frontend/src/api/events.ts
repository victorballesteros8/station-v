export interface EventLocation {
  lat: number
  lon: number
}

export interface EventCountry {
  id: number
  iso2: string
  name: string
}

export interface EventSource {
  id: string
  name: string
  tier: string
  source_class: string
  source_type: string
  reliability: number | null
}

export interface EventClaim {
  claim_type: string
  statement: string
  assertion_status: string
  confidence: string | null
}

export interface EventEvidence {
  id: string
  title: string | null
  url: string | null
  published_at: string | null
  evidence_type: string
  source_role: string
  relationship_to_event: string | null
  evidence_quality: number | null
  source: EventSource
  claims: EventClaim[]
}

export interface EventTimelineEntry {
  timestamp: string
  update_type: string
  description: string | null
  version: number | null
}

export interface EventMapItem {
  id: string
  category: string
  subtype: string
  title: string
  status: string
  severity: string
  escalation_score: number | null
  confidence: string
  location: EventLocation | null
  countries: EventCountry[]
  updated_at: string
}

export interface EventDetail extends EventMapItem {
  timeline: EventTimelineEntry[]
  evidence: EventEvidence[]
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL

export async function getEvents(): Promise<EventMapItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/events`)

  if (!response.ok) {
    throw new Error(`Error loading events: ${response.status}`)
  }

  return response.json()
}

export async function getEvent(eventId: string): Promise<EventDetail> {
  const response = await fetch(`${API_BASE_URL}/api/events/${eventId}`)

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Evento no encontrado")
    }

    throw new Error(`Error loading event: ${response.status}`)
  }

  return response.json()
}