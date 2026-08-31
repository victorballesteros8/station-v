import { useEffect, useState } from "react"

import {
  getCountry,
  type CountryData,
} from "./api/country"

import {
  getSituation,
  type SituationCountry,
} from "./api/situation"

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
    id: 1,
    key: "internal_instability",
    label: "Inestabilidad interna",
    icon: "🏛️",
  },
  {
    id: 2,
    key: "conflict_violence",
    label: "Conflicto y violencia",
    icon: "⚔️",
  },
  {
    id: 3,
    key: "international_tension",
    label: "Tensión internacional",
    icon: "🌐",
  },
  {
    id: 4,
    key: "military_activity",
    label: "Actividad militar",
    icon: "🪖",
  },
  {
    id: 5,
    key: "pressure_stress",
    label: "Presión / estrés",
    icon: "⚠️",
  },
] as const

function formatDimensionScore(value: number): string {
  if (Number.isInteger(value)) {
    return value.toString()
  }

  return value.toFixed(2)
}

function formatTrend(value: number | null): string {
  if (value === null) {
    return "—"
  }

  return `${value > 0 ? "+" : ""}${value.toFixed(1)}`
}

function CountryPanel({
  countryId,
  onClose,
  onEventSelect,
}: CountryPanelProps) {
  const [data, setData] =
    useState<CountryData | null>(null)

  const [trend, setTrend] =
    useState<number | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadCountry() {
      setLoading(true)
      setError(null)

      try {
        const [countryResult, situationResult] =
          await Promise.all([
            getCountry(countryId),
            getSituation(),
          ])

        if (!cancelled) {
          setData(countryResult)

          const countrySituation =
            [
              ...situationResult.top_risk,
              ...situationResult.deterioration_24h,
              ...situationResult.improvement_24h,
            ].find(
              (country: SituationCountry) =>
                country.country_id === countryId,
            )

          setTrend(
            countrySituation?.trend ?? null,
          )
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

  const {
    country,
    risk,
    subindicators,
    events,
  } = data

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
            <div className="country-risk-block">
              <span className="country-label">
                COUNTRY RISK
              </span>

              <strong className="country-risk-score">
                {risk.country_risk.toFixed(2)}
              </strong>
            </div>

            <div className="country-risk-block country-risk-change">
              <span className="country-label">
                CAMBIO 24 H
              </span>

              <strong
                className={`country-risk-trend ${
                  trend !== null && trend > 0
                    ? "positive"
                    : trend !== null &&
                        trend < 0
                      ? "negative"
                      : ""
                }`}
              >
                {formatTrend(trend)}
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
              {DIMENSIONS.map((dimension) => {
                const activeSubindicators =
                  subindicators.filter(
                    (subindicator) =>
                      subindicator.dimension_id ===
                        dimension.id &&
                      subindicator.score > 0,
                  )

                return (
                  <div
                    className="country-dimension"
                    key={dimension.key}
                  >
                    <div className="country-dimension-main">
                      <span className="country-dimension-name">
                        <span
                          className="country-dimension-icon"
                          aria-hidden="true"
                        >
                          {dimension.icon}
                        </span>

                        <strong>
                          {dimension.label}
                        </strong>
                      </span>

                      <strong>
                        {formatDimensionScore(
                          risk[dimension.key],
                        )}
                      </strong>
                    </div>

                    {activeSubindicators.length >
                      0 && (
                      <div className="country-subindicators">
                        {activeSubindicators.map(
                          (subindicator) => (
                            <div
                              className="country-subindicator"
                              key={subindicator.id}
                            >
                              <span>
                                {
                                  subindicator.name
                                }
                              </span>

                              <span>
                                {formatDimensionScore(
                                  subindicator.score,
                                )}
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
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