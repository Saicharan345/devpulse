import time
from datetime import datetime, timezone

import httpx

from app.database import SessionLocal
from app.models import Monitor, Incident


CHECK_INTERVAL = 60


def check_monitor(monitor_id: int):
    db = SessionLocal()

    try:
        monitor = (
            db.query(Monitor)
            .filter(Monitor.id == monitor_id)
            .first()
        )

        if not monitor:
            print(f"Monitor {monitor_id} not found.")
            return

        print(f"Checking: {monitor.name} - {monitor.url}")

        start_time = time.perf_counter()

        try:
            response = httpx.get(
                monitor.url,
                timeout=10.0,
                follow_redirects=True
            )

            end_time = time.perf_counter()

            response_time = (end_time - start_time) * 1000

            monitor.response_time = round(response_time, 2)
            monitor.last_checked = datetime.now(timezone.utc)

            if response.is_success:
                monitor.status = "up"

                print(
                    f"UP - {response.status_code} - "
                    f"{response_time:.2f} ms"
                )

                # Check whether an incident is currently open
                incident = (
                    db.query(Incident)
                    .filter(
                        Incident.monitor_id == monitor.id,
                        Incident.status == "open"
                    )
                    .first()
                )

                if incident:
                    incident.status = "resolved"
                    incident.resolved_at = datetime.now(timezone.utc)

                    print(
                        f"INCIDENT RESOLVED - {monitor.name}"
                    )

            else:
                monitor.status = "down"

                print(
                    f"DOWN - HTTP {response.status_code}"
                )

                create_incident_if_needed(
                    db,
                    monitor,
                    f"HTTP {response.status_code}"
                )

        except httpx.RequestError as error:
            monitor.status = "down"
            monitor.response_time = None
            monitor.last_checked = datetime.now(timezone.utc)

            print(f"DOWN - {error}")

            create_incident_if_needed(
                db,
                monitor,
                str(error)
            )

        db.commit()

    finally:
        db.close()


def create_incident_if_needed(db, monitor, error_message):
    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.monitor_id == monitor.id,
            Incident.status == "open"
        )
        .first()
    )

    if existing_incident:
        print(
            f"Incident already open for {monitor.name}"
        )
        return

    incident = Incident(
        monitor_id=monitor.id,
        status="open",
        error_message=error_message,
        started_at=datetime.now(timezone.utc)
    )

    db.add(incident)

    print(
        f"INCIDENT CREATED - {monitor.name}"
    )


def check_all_monitors():
    db = SessionLocal()

    try:
        monitors = db.query(Monitor).all()

        if not monitors:
            print("No monitors found.")
            return

        monitor_ids = [monitor.id for monitor in monitors]

    finally:
        db.close()

    for monitor_id in monitor_ids:
        check_monitor(monitor_id)


def run_worker():
    print("===================================")
    print("DevPulse Monitoring Worker Started")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("===================================")

    while True:
        print("\nStarting monitoring cycle...\n")

        try:
            check_all_monitors()
        except Exception as error:
            print(f"Worker error: {error}")

        print(
            f"\nNext check in {CHECK_INTERVAL} seconds..."
        )

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_worker()