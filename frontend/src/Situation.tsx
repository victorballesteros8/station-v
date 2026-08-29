import { useEffect, useState } from "react"

import CountryIdentity from "./components/CountryIdentity"

import {
  getSituation,
  type SituationCountry,
  type SituationEvent,
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
    emerging: "✨",
    active: "⚿",
    stable: "≡",
    decreasing: "↘",
    finished: "✓",
  }

  return icons[status] ?? "•"
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

  return (
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

      <strong>
        {showTrend ? (
          <>
            {formatScore(previousRisk)}{" "}
            <span
              style={{
                fontSize: "0.8em",
                fontWeight: 500,
                color:
                  country.trend !== null &&
                  country.trend > 0
                    ? "#d94a4a"
                    : "#5fa87a",
              }}
            >
              {formatTrend(country.trend)}
            </span>
          </>
        ) : (
          formatScore(country.country_risk)
        )}
      </strong>
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

  useEffect(() => {
    async function loadSituation() {
      try {
        const data = await getSituation()

        setTopRisk(data.top_risk)
        setDeterioration(data.deterioration_24h)
        setImprovement(data.improvement_24h)
        setEvents(data.relevant_events)
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
            <strong>—</strong>
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