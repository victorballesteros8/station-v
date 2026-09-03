from __future__ import annotations

import time

from backend.app.db import get_connection
from backend.app.scoring.risk_service import (
    calculate_scheduled_country_risk_updates,
)


UPDATE_INTERVAL_SECONDS = 6 * 60 * 60
COUNTRY_RISK_LOCK_KEY = 3141592653


def run_country_risk_cycle() -> None:
    """
    Execute one scheduled Country Risk update cycle.

    PostgreSQL advisory locking guarantees that only one worker
    instance can execute the cycle at a time.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_try_advisory_lock(%s)",
                (COUNTRY_RISK_LOCK_KEY,),
            )

            acquired = cur.fetchone()[0]

            if not acquired:
                return

            try:
                calculate_scheduled_country_risk_updates()
            finally:
                cur.execute(
                    "SELECT pg_advisory_unlock(%s)",
                    (COUNTRY_RISK_LOCK_KEY,),
                )


def main() -> None:
    """
    Run the Country Risk worker indefinitely.

    A cycle is executed immediately on startup and then every
    six hours.
    """

    while True:
        run_country_risk_cycle()
        time.sleep(UPDATE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()