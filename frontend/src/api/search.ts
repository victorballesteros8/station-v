export interface SearchCountry {
  id: number
  iso2: string
  name: string
}

export interface SearchEvent {
  id: string
  title: string
  category: string
  severity: string
  escalation_score: number | null
}

export interface SearchResponse {
  query: string
  countries: SearchCountry[]
  events: SearchEvent[]
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL

export async function searchStationV(
  query: string,
): Promise<SearchResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/search?q=${encodeURIComponent(query)}`,
  )

  if (!response.ok) {
    throw new Error(
      `Error en la búsqueda: ${response.status}`,
    )
  }

  return response.json()
}