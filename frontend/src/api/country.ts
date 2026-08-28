export interface CountryData {
  country: {
    id: number
    iso2: string
    iso3: string
    name: string
    status: string
  }

  risk: {
    timestamp: string
    internal_instability: number
    conflict_violence: number
    international_tension: number
    military_activity: number
    pressure_stress: number
    country_risk: number
    confidence: string
  } | null

  subindicators: {
    id: number
    code: string
    name: string
    score: number
    timestamp: string
  }[]

  events: {
    id: string
    title: string
    category: string
    severity: string
    escalation_score: number | null
    time_start: string | null
    confidence: string
  }[]
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL

export async function getCountry(
  countryId: number,
): Promise<CountryData> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/countries/${countryId}`,
  )

  if (!response.ok) {
    throw new Error(
      `Error al cargar el país: ${response.status}`,
    )
  }

  return response.json()
}