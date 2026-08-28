import { useEffect, useState } from "react"

import {
  getCountry,
  type CountryData,
} from "./api/country"

import CountryIdentity from "./components/CountryIdentity"

import "./CountryPanel.css"

import {
  formatSeverity,
} from "./utils/labels"

interface CountryPanelProps {
  countryId: number
  onClose: () => void
  onEventSelect?: (eventId: string) => void
}

const DIMENSIONS = [
  {
    key: "internal_instability",
    label: "Inestabilidad interna",
  },
  {
    key: "conflict_violence",
    label: "Conflicto y violencia",
  },
  {
    key: "international_tension",
    label: "Tensión internacional",
  },
  {
    key: "military_activity",
    label: "Actividad militar",
  },
  {
    key: "pressure_stress",
    label: "Presión / estrés",
  },
] as const

function CountryPanel({
  countryId,
  onClose,
  onEventSelect,
}: CountryPanelProps) {
  const [data, setData] =
    useState<CountryData | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadCountry() {
      setLoading(true)
      setError(null)

      try {
        const result = await getCountry(countryId)

        if (!cancelled) {
          setData(result)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "No se pudo cargar el país",
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadCountry()

    return () => {
      cancelled = true
    }
  }, [countryId])

  if (loading) {
    return (
      <aside className="country-panel">
        <button
          className="country-panel-close"
          onClick={onClose}
          aria-label="Cerrar"
        >
          ×
        </button>

        <p className="country-panel-status">
          Cargando...
        </p>
      </aside>
    )
  }

  if (error || !data) {
    return (
      <aside className="country-panel">
        <button
          className="country-panel-close"
          onClick={onClose}
          aria-label="Cerrar"
        >
          ×
        </button>

        <p className="country-panel-error">
          {error ?? "No se pudo cargar el país"}
        </p>
      </aside>
    )
  }

  const { country, risk, events } = data

  return (
    <aside className="country-panel">
      <button
        className="country-panel-close"
        onClick={onClose}
        aria-label="Cerrar"
      >
        ×
      </button>

      <div className="country-panel-header">
        <CountryIdentity
          iso2={country.iso2}
          name={country.name}
        />

        <span className="country-code">
          {country.iso3}
        </span>
      </div>

      {risk && (
        <>
          <section className="country-risk">
            <div>
              <span className="country-label">
                COUNTRY RISK
              </span>

              <strong className="country-risk-score">
                {risk.country_risk.toFixed(2)}
              </strong>
            </div>

            <div className="country-confidence">
              <span>Confianza</span>
              <strong>
                {risk.confidence.toUpperCase()}
              </strong>
            </div>
          </section>

          <section className="country-section">
            <h3>DIMENSIONES</h3>

            <div className="country-dimensions">
              {DIMENSIONS.map((dimension) => (
                <div
                  className="country-dimension"
                  key={dimension.key}
                >
                  <span>{dimension.label}</span>

                  <strong>
                    {risk[
                      dimension.key
                    ].toFixed(2)}
                  </strong>
                </div>
              ))}
            </div>
          </section>
        </>
      )}

      <section className="country-section">
        <h3>ACONTECIMIENTOS</h3>

        {events.length === 0 ? (
          <p className="country-muted">
            Sin acontecimientos asociados.
          </p>
        ) : (
          <div className="country-events">
            {events.map((event) => (
              <button
                className="country-event"
                key={event.id}
                onClick={() =>
                  onEventSelect?.(event.id)
                }
              >
                <div>
                  <strong>{event.title}</strong>

                  <span>
                    {event.category}
                  </span>
                </div>

                <div className="country-event-meta">
                  <span>
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
              </button>
            ))}
          </div>
        )}
      </section>
    </aside>
  )
}

export default CountryPanel