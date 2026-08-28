import type { EventDetail } from "./api/events"
import "./EventDetailPanel.css"

interface EventDetailPanelProps {
  event: EventDetail
  onClose: () => void
  onCountrySelect: (countryId: number) => void
}

function formatSeverity(severity: string): string {
  const labels: Record<string, string> = {
    critical: "Crítica",
    high: "Alta",
    medium: "Media",
    low: "Baja",
    info: "Información",
  }

  return labels[severity] ?? severity
}

function formatStatus(status: string): string {
  const labels: Record<string, string> = {
    emerging: "Emergente",
    active: "Activo",
    stable: "Estable",
    decreasing: "En descenso",
    finished: "Finalizado",
  }

  return labels[status] ?? status
}

function formatConfidence(confidence: string | null): string {
  if (!confidence) {
    return "No disponible"
  }

  const labels: Record<string, string> = {
    high: "Alta",
    medium: "Media",
    low: "Baja",
  }

  return labels[confidence] ?? confidence
}

function formatAssertionStatus(status: string): string {
  const labels: Record<string, string> = {
    confirmed: "Confirmado",
    reported: "Reportado",
    claimed: "Afirmado",
    disputed: "Disputado",
    inferred: "Inferido",
  }

  return labels[status] ?? status
}

function getCountryFlag(iso2: string): string {
  if (!/^[A-Za-z]{2}$/.test(iso2)) {
    return ""
  }

  return iso2
    .toUpperCase()
    .split("")
    .map((letter) =>
      String.fromCodePoint(127397 + letter.charCodeAt(0)),
    )
    .join("")
}

function formatCountryName(iso2: string, name: string): string {
  const names: Record<string, string> = {
    ES: "España",
    FR: "Francia",
    DE: "Alemania",
    GB: "Reino Unido",
    US: "Estados Unidos",
    UA: "Ucrania",
    IN: "India",
    PK: "Pakistán",
    EG: "Egipto",
    JP: "Japón",
    CN: "China",
    RU: "Rusia",
    IR: "Irán",
    IL: "Israel",
    TR: "Turquía",
  }

  return names[iso2.toUpperCase()] ?? name
}

function EventDetailPanel({
  event,
  onClose,
  onCountrySelect,
}: EventDetailPanelProps) {
  return (
    <aside className="event-detail-panel">
      <div className="event-detail-header">
        <div>
          <span
            className={`event-detail-severity severity-${event.severity}`}
          >
            {formatSeverity(event.severity)}
          </span>

          <h2>{event.title}</h2>
        </div>

        <button
          type="button"
          className="event-detail-close"
          onClick={onClose}
          aria-label="Cerrar detalle"
        >
          ×
        </button>
      </div>

      <div className="event-detail-meta">
        <div>
          <span>Estado</span>
          <strong>{formatStatus(event.status)}</strong>
        </div>

        <div>
          <span>Confianza</span>
          <strong>{formatConfidence(event.confidence)}</strong>
        </div>

        {event.escalation_score !== null && (
          <div>
            <span>Escalada</span>
            <strong>
              {event.escalation_score.toFixed(1)} / 10
            </strong>
          </div>
        )}
      </div>

      <section className="event-detail-section">
        <h3>Países afectados</h3>

        <div className="event-detail-countries">
          {event.countries.map((country) => (
            <button
              type="button"
              key={country.iso2}
              className="event-detail-country"
              onClick={() => onCountrySelect(country.id)}
            >
              <span aria-hidden="true">
                {getCountryFlag(country.iso2)}
              </span>

              {formatCountryName(country.iso2, country.name)}
            </button>
          ))}
        </div>
      </section>

      <section className="event-detail-section">
        <h3>Evidencia</h3>

        {event.evidence.length === 0 ? (
          <p className="event-detail-empty">
            No hay evidencia asociada.
          </p>
        ) : (
          <div className="event-detail-evidence">
            {event.evidence.map((evidence) => (
              <article
                className="event-evidence-card"
                key={evidence.id}
              >
                <h4>
                  {evidence.title ?? "Evidencia sin título"}
                </h4>

                <div className="event-evidence-source">
                  <strong>{evidence.source.name}</strong>

                  <span className="event-evidence-tier">
                    {evidence.source.tier}
                  </span>
                </div>

                <div className="event-evidence-quality">
                  Calidad de evidencia:{" "}
                  {evidence.evidence_quality !== null
                    ? `${evidence.evidence_quality}/100`
                    : "No disponible"}
                </div>

                {evidence.url && (
                  <a
                    className="event-evidence-link"
                    href={evidence.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Abrir fuente
                  </a>
                )}

                {evidence.claims.length > 0 && (
                  <div className="event-evidence-claims">
                    <h5>Afirmaciones</h5>

                    {evidence.claims.map((claim, index) => (
                      <div
                        className="event-claim"
                        key={`${evidence.id}-${index}`}
                      >
                        <p>{claim.statement}</p>

                        <span>
                          {formatAssertionStatus(
                            claim.assertion_status,
                          )}

                          {claim.confidence
                            ? ` · confianza ${formatConfidence(
                                claim.confidence,
                              )}`
                            : ""}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </aside>
  )
}

export default EventDetailPanel