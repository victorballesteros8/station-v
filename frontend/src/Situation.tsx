import { useEffect, useState } from "react"

import CountryIdentity from "./components/CountryIdentity"

import {
  getSituation,
  type SituationCountry,
  type SituationEvent,
  type SituationResponse,
} from "./api/situation"

import { formatSeverity } from "./utils/labels"

import "./Situation.css"

interface SituationProps {
  onCountrySelect: (countryId: number) => void
  onEventSelect: (eventId: string) => void
}

function formatScore(value: number): string {
  return value.toFixed(1)
}

function formatTrend(value: number | null): string {
  if (value === null) {
    return "—"
  }

  return `${value > 0 ? "+" : ""}${value.toFixed(1)}`
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    emerging: "📈",
    active: "🔔",
    stable: "⏳",
    decreasing: "📉",
    finished: "✅",
  }

  return icons[status] ?? "•"
}

function getRiskLevel(value: number): string {
  if (value < 20) {
    return "low"
  }

  if (value < 40) {
    return "moderate"
  }

  if (value < 60) {
    return "elevated"
  }

  if (value < 80) {
    return "high"
  }

  return "critical"
}

function CountryRow({
  country,
  showTrend = false,
  onSelect,
}: {
  country: SituationCountry
  showTrend?: boolean
  onSelect: (countryId: number) => void
}) {
  const previousRisk =
    country.trend !== null
      ? country.country_risk - country.trend
      : country.country_risk

  const riskLevel = getRiskLevel(country.country_risk)

  return (
    <div className="situation-country-row">
      <div className="situation-row">
        <button
          type="button"
          className="situation-country"
          onClick={() => onSelect(country.country_id)}
        >
          <CountryIdentity
            iso2={country.iso2}
            name={country.name}
          />
        </button>

        <strong className="situation-country-score">
          {showTrend ? (
            <>
              {formatScore(previousRisk)}{" "}
              <span
                className={
                  country.trend !== null &&
                  country.trend > 0
                    ? "situation-trend-positive"
                    : "situation-trend-negative"
                }
              >
                {formatTrend(country.trend)}
              </span>
            </>
          ) : (
            <>
              <span
                className={`situation-risk-dot ${riskLevel}`}
                aria-hidden="true"
              />
              {formatScore(country.country_risk)}
            </>
          )}
        </strong>
      </div>

      {!showTrend && (
        <div
          className="situation-risk-bar"
          aria-hidden="true"
        >
          <div
            className={`situation-risk-bar-fill ${riskLevel}`}
            style={{
              width: `${Math.min(
                Math.max(country.country_risk, 0),
                100,
              )}%`,
            }}
          />
        </div>
      )}
    </div>
  )
}

function EventRow({
  event,
  onEventSelect,
}: {
  event: SituationEvent
  onEventSelect: (eventId: string) => void
}) {
  const severityClass = event.severity
  const statusIcon = getStatusIcon(event.status)

  return (
    <button
      type="button"
      className="situation-event-row"
      onClick={() => onEventSelect(event.id)}
    >
      <span className="situation-event">
        <span
          className={`situation-event-status-icon ${event.status}`}
          aria-hidden="true"
        >
          {statusIcon}
        </span>

        <span>{event.title}</span>
      </span>

      <span className="situation-event-countries">
        {event.countries.map((country) => (
          <span
            className="situation-event-country"
            key={country.iso2}
          >
            <CountryIdentity
              iso2={country.iso2}
              name={country.name}
            />
          </span>
        ))}
      </span>

      <span
        className={`situation-event-severity ${severityClass}`}
      >
        {formatSeverity(event.severity)}
      </span>

      <strong className={severityClass}>
        {event.escalation_score !== null
          ? event.escalation_score.toFixed(1)
          : "—"}
      </strong>
    </button>
  )
}

function Situation({
  onCountrySelect,
  onEventSelect,
}: SituationProps) {
  const [topRisk, setTopRisk] = useState<
    SituationCountry[]
  >([])

  const [deterioration, setDeterioration] =
    useState<SituationCountry[]>([])

  const [improvement, setImprovement] =
    useState<SituationCountry[]>([])

  const [events, setEvents] =
    useState<SituationEvent[]>([])

  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)

  const [globalRisk, setGlobalRisk] =
    useState<SituationResponse["global_risk"] | null>(null)

  useEffect(() => {
    async function loadSituation() {
      try {
        const data = await getSituation()

        setTopRisk(data.top_risk)
        setDeterioration(data.deterioration_24h)
        setImprovement(data.improvement_24h)
        setEvents(data.relevant_events)
        setGlobalRisk(data.global_risk)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudo cargar la situación",
        )
      } finally {
        setLoading(false)
      }
    }

    loadSituation()
  }, [])

  if (loading) {
    return (
      <section className="situation">
        <p>Cargando situación...</p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="situation">
        <p>Error: {error}</p>
      </section>
    )
  }

  return (
    <section className="situation">
      <div className="situation-header">
        <h2>SITUACIÓN</h2>
      </div>

      <div className="situation-grid">
        <section className="situation-card">
          <h3>Riesgo global</h3>

          <div className="situation-global-risk">
            {globalRisk && (
              <>
                {globalRisk.coverage_status !== "operational" && (
                  <span
                    className={`situation-global-risk-status ${globalRisk.coverage_status}`}
                    title={
                      globalRisk.coverage_status === "insufficient"
                        ? "Datos insuficientes"
                        : "Datos incompletos"
                    }
                    aria-label={
                      globalRisk.coverage_status === "insufficient"
                        ? "Datos insuficientes"
                        : "Datos incompletos"
                    }
                  />
                )}

                <strong>
                  {formatScore(globalRisk.value)}
                </strong>
              </>
            )}
          </div>
        </section>

        <section className="situation-card">
          <h3>Países con mayor riesgo</h3>

          <div className="situation-table-header">
            <span>País</span>
            <span>Country Risk</span>
          </div>

          <div className="situation-list">
            {topRisk.map((country) => (
              <CountryRow
                key={country.country_id}
                country={country}
                onSelect={onCountrySelect}
              />
            ))}
          </div>
        </section>

        <section className="situation-card">
          <h3>Mayor deterioro · 24 h</h3>

          <div className="situation-table-header">
            <span>País</span>
            <span>Variación 24 h</span>
          </div>

          <div className="situation-list">
            {deterioration.length === 0 ? (
              <p className="empty-state">
                Sin cambios disponibles
              </p>
            ) : (
              deterioration.map((country) => (
                <CountryRow
                  key={country.country_id}
                  country={country}
                  showTrend
                  onSelect={onCountrySelect}
                />
              ))
            )}
          </div>
        </section>

        <section className="situation-card">
          <h3>Mayor mejora · 24 h</h3>

          <div className="situation-table-header">
            <span>País</span>
            <span>Variación 24 h</span>
          </div>

          <div className="situation-list">
            {improvement.length === 0 ? (
              <p className="empty-state">
                Sin cambios disponibles
              </p>
            ) : (
              improvement.map((country) => (
                <CountryRow
                  key={country.country_id}
                  country={country}
                  showTrend
                  onSelect={onCountrySelect}
                />
              ))
            )}
          </div>
        </section>

        <section className="situation-card situation-card-wide">
          <h3>Eventos más relevantes</h3>

          <div className="situation-event-header">
            <span>Evento</span>
            <span>Países</span>
            <span>Severidad</span>
            <span>Escalada</span>
          </div>

          <div className="situation-list">
            {events.map((event) => (
              <EventRow
                key={event.id}
                event={event}
                onEventSelect={onEventSelect}
              />
            ))}
          </div>
        </section>
      </div>
    </section>
  )
}

export default Situation