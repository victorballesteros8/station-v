from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db import get_connection
from backend.app.api.countries import router as countries_router
from backend.app.api.events import router as events_router

from backend.app.api.risk import router as risk_router
from backend.app.api.situation import router as situation_router

from backend.app.api.search import router as search_router

from backend.app.api.country import router as country_router

app = FastAPI(
    title="STATION V API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.62:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(countries_router)
app.include_router(events_router)
app.include_router(risk_router)
app.include_router(situation_router)
app.include_router(search_router)
app.include_router(country_router)

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "station-v-api",
    }


@app.get("/api/db-health")
def db_health():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()

    return {
        "status": "ok",
        "database": result[0] == 1,
    }