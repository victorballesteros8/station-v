import { useEffect, useState } from "react"

import { getEvent, getEvents } from "./api/events"
import type { EventDetail, EventMapItem } from "./api/events"

import MapView from "./MapView"
import EventDetailPanel from "./EventDetailPanel"
import Situation from "./Situation"

import Search from "./Search"
import CountryPanel from "./CountryPanel"

import {
  formatSeverity,
} from "./utils/labels"

import "./App.css"

type Tab = "map" | "situation" | "search"

function App() {
  const [activeTab, setActiveTab] = useState<Tab>("map")

  const [events, setEvents] = useState<EventMapItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [selectedEventId, setSelectedEventId] = useState<string | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<EventDetail | null>(null)
  const [selectedCountryId, setSelectedCountryId] = useState<number | null>(null)

  useEffect(() => {
    async function loadEvents() {
      try {
        const data = await getEvents()
        setEvents(data)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "No se pudieron cargar los eventos",
        )
      } finally {
        setLoading(false)
      }
    }

    loadEvents()
  }, [])

  useEffect(() => {
    if (!selectedEventId) {
      setSelectedEvent(null)
      return
    }

    const eventId = selectedEventId

    async function loadEventDetail() {
      try {
        const data = await getEvent(eventId)
        setSelectedEvent(data)
      } catch (err) {
        console.error(err)
        setSelectedEvent(null)
      }
    }

    loadEventDetail()
  }, [selectedEventId])

  function handleTabChange(tab: Tab) {
    setActiveTab(tab)

    setSelectedEventId(null)
    setSelectedCountryId(null)
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <h1>STATION V</h1>
          <p>Inteligencia geopolítica de código abierto</p>
        </div>

        <nav className="main-nav" aria-label="Navegación principal">
          <button
            className={activeTab === "map" ? "active" : ""}
            onClick={() => handleTabChange("map")}
          >
            MAPA
          </button>

          <button
            className={activeTab === "situation" ? "active" : ""}
            onClick={() => handleTabChange("situation")}
          >
            SITUACIÓN
          </button>

          <button
            className={activeTab === "search" ? "active" : ""}
            onClick={() => handleTabChange("search")}
          >
            BUSCAR
          </button>
        </nav>
      </header>

      <main className="main">
        {activeTab === "map" && (
          <>
            <section className="map-panel">
              <MapView
                events={events}
                onEventSelect={setSelectedEventId}
              />
            </section>

            <aside className="events-panel">
              <div className="panel-header">
                <h2>Eventos</h2>
                <span>{events.length}</span>
              </div>

              {loading && (
                <div className="event-card">
                  <p>Cargando eventos...</p>
                </div>
              )}

              {error && (
                <div className="event-card">
                  <p>Error: {error}</p>
                </div>
              )}

              {!loading && !error && (
                <div className="event-list">
                  {events.map((event) => (
                    <article
                      className="event-card"
                      key={event.id}
                      onClick={() =>
                        setSelectedEventId(event.id)
                      }
                    >
                      <div
                        className={`severity severity-${event.severity}`}
                      >
                        {formatSeverity(event.severity)}
                      </div>

                      <h3>{event.title}</h3>

                      <p>
                        {event.countries
                          .map((country) => country.name)
                          .join(" · ")}
                      </p>
                    </article>
                  ))}
                </div>
              )}
            </aside>
          </>
        )}

        {activeTab === "situation" && (
          <Situation
            onCountrySelect={(countryId) => {
              setSelectedEventId(null)
              setSelectedCountryId(countryId)
            }}
            onEventSelect={(eventId) => {
              setSelectedCountryId(null)
              setSelectedEventId(eventId)
            }}
          />
        )}

        {activeTab === "search" && (
          <Search
            onEventSelect={(eventId) => {
              setSelectedCountryId(null)
              setSelectedEventId(eventId)
            }}
            onCountrySelect={(countryId) => {
              setSelectedEventId(null)
              setSelectedCountryId(countryId)
            }}
          />
        )}

        {selectedEvent && (
          <EventDetailPanel
            event={selectedEvent}
            onClose={() =>
              setSelectedEventId(null)
            }
            onCountrySelect={(countryId) => {
              setSelectedEventId(null)
              setSelectedCountryId(countryId)
            }}
          />
        )}

        {selectedCountryId !== null && (
          <CountryPanel
            countryId={selectedCountryId}
            onClose={() =>
              setSelectedCountryId(null)
            }
            onEventSelect={(eventId) => {
              setSelectedCountryId(null)
              setSelectedEventId(eventId)
            }}
          />
        )}
      </main>
    </div>
  )
}

export default App