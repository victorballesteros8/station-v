import { useEffect, useRef, useState } from "react"
import L from "leaflet"

import type { EventMapItem } from "./api/events"
import "./MapView.css"

interface MapViewProps {
  events: EventMapItem[]
  onEventSelect: (eventId: string) => void
}

const categoryLabels: Record<string, string> = {
  conflict_violence: "Conflicto / violencia",
  protests_unrest: "Protestas / disturbios",
  military_activity: "Actividad militar",
  border_tension: "Tensión fronteriza",
  political_crisis: "Crisis política",
  disaster: "Desastre",
  critical_infrastructure: "Infraestructura crítica",
  security_terrorism: "Seguridad / terrorismo",
}

function getEscalationColor(
  escalationScore: number | null,
): string {
  if (escalationScore === null) {
    return "#7f8a96"
  }

  if (escalationScore <= 3) {
    return "#5fa87a"
  }

  if (escalationScore <= 6) {
    return "#d8b94a"
  }

  if (escalationScore <= 8) {
    return "#e58b3a"
  }

  return "#d94a4a"
}

function getCategoryIcon(category: string): string {
  switch (category) {
    case "conflict_violence":
      return "⚔"

    case "protests_unrest":
      return "✊"

    case "military_activity":
      return "🪖"

    case "border_tension":
      return "⚑"

    case "political_crisis":
      return "⚖"

    case "disaster":
      return "◈"

    case "critical_infrastructure":
      return "⚡"

    case "security_terrorism":
      return "🚨"

    default:
      return "○"
  }
}

function createEventIcon(
  category: string,
  escalationScore: number | null,
): L.DivIcon {
  const color = getEscalationColor(escalationScore)
  const icon = getCategoryIcon(category)

  return L.divIcon({
    className: "event-map-icon-wrapper",
    html: `
      <div
        class="event-map-icon"
        style="--event-color: ${color};"
      >
        <span>${icon}</span>
      </div>
    `,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -17],
  })
}

function MapLegend({
  visibleEvents,
}: {
  visibleEvents: EventMapItem[]
}) {
  const [open, setOpen] = useState(false)

  const categories = Array.from(
    new Set(visibleEvents.map((event) => event.category)),
  )

  return (
    <>
      <button
        type="button"
        className={`map-legend-toggle ${open ? "open" : ""}`}
        onClick={() => setOpen((current) => !current)}
        aria-expanded={open}
        aria-label="Mostrar u ocultar leyenda"
      >
        {open ? "OCULTAR LEYENDA" : "LEYENDA"}
      </button>

      <div
        className={`map-legend ${open ? "map-legend-open" : ""}`}
      >
        <div className="map-legend-section">
          <h3>Escalada</h3>

          <div className="map-legend-escalation">
            <div className="map-legend-item">
              <span
                className="map-legend-dot"
                style={{ backgroundColor: "#5fa87a" }}
              />
              <span>Baja</span>
              <span className="map-legend-range">0–3</span>
            </div>

            <div className="map-legend-item">
              <span
                className="map-legend-dot"
                style={{ backgroundColor: "#d8b94a" }}
              />
              <span>Moderada</span>
              <span className="map-legend-range">&gt;3–6</span>
            </div>

            <div className="map-legend-item">
              <span
                className="map-legend-dot"
                style={{ backgroundColor: "#e58b3a" }}
              />
              <span>Alta</span>
              <span className="map-legend-range">&gt;6–8</span>
            </div>

            <div className="map-legend-item">
              <span
                className="map-legend-dot"
                style={{ backgroundColor: "#d94a4a" }}
              />
              <span>Crítica</span>
              <span className="map-legend-range">&gt;8–10</span>
            </div>
          </div>
        </div>

        {categories.length > 0 && (
          <div className="map-legend-section">
            <h3>Categorías</h3>

            <div className="map-legend-categories">
              {categories.map((category) => (
                <div
                  className="map-legend-category"
                  key={category}
                >
                  <span className="map-legend-category-icon">
                    {getCategoryIcon(category)}
                  </span>

                  <span>
                    {categoryLabels[category] ?? category}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  )
}

function MapView({
  events,
  onEventSelect,
}: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<L.Map | null>(null)

  const visibleEvents = events.filter(
    (event) =>
      event.location &&
      (event.severity === "high" ||
        event.severity === "critical"),
  )

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) {
      return
    }

    const map = L.map(mapContainerRef.current, {
      center: [25, 10],
      zoom: 2,
      minZoom: 2,
      worldCopyJump: true,
    })

    L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      },
    ).addTo(map)

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current

    if (!map) {
      return
    }

    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer)
      }
    })

    for (const event of visibleEvents) {
      if (!event.location) {
        continue
      }

      const marker = L.marker(
        [
          event.location.lat,
          event.location.lon,
        ],
        {
          icon: createEventIcon(
            event.category,
            event.escalation_score,
          ),
        },
      )

      marker.on("click", () => {
        onEventSelect(event.id)
      })

      const escalationText =
        event.escalation_score !== null
          ? `Escalada: ${event.escalation_score.toFixed(1)} / 10`
          : "Escalada: no disponible"

      marker.bindPopup(`
        <strong>${event.title}</strong>
        <br>
        ${escalationText}
        <br>
        ${event.countries
          .map((country) => country.name)
          .join(" · ")}
      `)

      marker.bindTooltip(event.title)

      marker.addTo(map)
    }
  }, [visibleEvents, onEventSelect])

  return (
    <div className="map-container">
      <div
        ref={mapContainerRef}
        className="map-view"
      />

      <MapLegend visibleEvents={visibleEvents} />
    </div>
  )
}

export default MapView