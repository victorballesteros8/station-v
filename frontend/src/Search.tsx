import { useState } from "react"

import {
  searchStationV,
  type SearchCountry,
  type SearchEvent,
} from "./api/search"

import CountryIdentity from "./components/CountryIdentity"

import {
  formatSeverity,
} from "./utils/labels"

import "./Search.css"

interface SearchProps {
  onCountrySelect: (countryId: number) => void
  onEventSelect: (eventId: string) => void
}

function Search({
  onCountrySelect,
  onEventSelect,
}: SearchProps) {
  const [query, setQuery] = useState("")
  const [countries, setCountries] = useState<SearchCountry[]>([])
  const [events, setEvents] = useState<SearchEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSearch(
    event: React.FormEvent,
  ) {
    event.preventDefault()

    const trimmedQuery = query.trim()

    if (!trimmedQuery) {
      return
    }

    setLoading(true)
    setSearched(true)
    setError(null)

    try {
      const data = await searchStationV(trimmedQuery)

      setCountries(data.countries)
      setEvents(data.events)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo realizar la búsqueda",
      )

      setCountries([])
      setEvents([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="search">
      <div className="search-header">
        <h2>BUSCAR</h2>

        <p>
          Busca países y acontecimientos registrados en
          STATION V.
        </p>
      </div>

      <form
        className="search-form"
        onSubmit={handleSearch}
      >
        <input
          type="search"
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
          placeholder="Buscar país o acontecimiento..."
          aria-label="Buscar país o acontecimiento"
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading ? "BUSCANDO..." : "BUSCAR"}
        </button>
      </form>

      {error && (
        <p className="search-error">
          {error}
        </p>
      )}

      {!loading && searched && !error && (
        <div className="search-results">
          {countries.length > 0 && (
            <section className="search-section">
              <h3>PAÍSES</h3>

              <div className="search-list">
                {countries.map((country) => (
                  <button
                    type="button"
                    className="search-result search-country-result"
                    key={country.id}
                    onClick={() =>
                      onCountrySelect(country.id)
                    }
                  >
                    <CountryIdentity
                      iso2={country.iso2}
                      name={country.name}
                    />
                  </button>
                ))}
              </div>
            </section>
          )}

          {events.length > 0 && (
            <section className="search-section">
              <h3>ACONTECIMIENTOS</h3>

              <div className="search-list">
                {events.map((event) => (
                  <button
                    type="button"
                    className="search-result search-event-result"
                    key={event.id}
                    onClick={() =>
                      onEventSelect(event.id)
                    }
                  >
                    <div className="search-event">
                      <div>
                        <h4>{event.title}</h4>

                        <p>
                          {event.category}
                        </p>
                      </div>

                      <div className="search-event-meta">
                        <span
                          className={`search-severity severity-${event.severity}`}
                        >
                          {formatSeverity(event.severity)}
                        </span>

                        {event.escalation_score !==
                          null && (
                          <strong>
                            {event.escalation_score.toFixed(
                              1,
                            )}
                          </strong>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </section>
          )}

          {countries.length === 0 &&
            events.length === 0 && (
              <p className="search-empty">
                No se han encontrado resultados.
              </p>
            )}
        </div>
      )}
    </section>
  )
}

export default Search