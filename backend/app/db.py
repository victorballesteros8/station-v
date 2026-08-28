import os

import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://station_v:station_v_dev@localhost:5432/station_v",
)


def get_connection():
    return psycopg.connect(DATABASE_URL)