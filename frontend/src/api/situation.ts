export interface SituationCountry {
  country_id: number
  iso2: string
  name: string
  timestamp: string
  country_risk: number
  confidence: string
  trend: number | null
}

export interface SituationEvent {
  id: string
  title: string
  status: string
  countries: {
    iso2: string
    name: string
  }[]
  severity: string
  escalation_score: number | null
  time_start: string | null
  confidence: string
}

export interface SituationResponse {
  top_risk: SituationCountry[]
  deterioration_24h: SituationCountry[]
  improvement_24h: SituationCountry[]
  relevant_events: SituationEvent[]
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL

export async function getSituation(): Promise<SituationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/situation`,
  )

  if (!response.ok) {
    throw new Error(
      `Error loading situation: ${response.status}`,
    )
  }

  return response.json()
}