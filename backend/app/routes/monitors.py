from datetime import datetime, timezone
import time
import httpx

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import HttpUrl

from app.database import SessionLocal
from app.models import Monitor, Incident
from app.schemas import MonitorCreate, MonitorRead

router = APIRouter(prefix="/monitors", tags=["Monitors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_monitor(monitor: Monitor, db: Session):
    """Check whether a website is reachable and handle incidents."""
    start_time = time.perf_counter()
    status = "down"
    error_message = None
    response_time = None

    try:
        response = httpx.get(
            monitor.url,
            timeout=10.0,
            headers={"User-Agent": "DevPulse-Monitor/1.0"},
            follow_redirects=True,
        )
        elapsed = time.perf_counter() - start_time
        response_time = round(elapsed * 1000, 2)

        if 200 <= response.status_code < 400:
            status = "up"
        else:
            status = "down"
            error_message = f"HTTP {response.status_code}"

    except httpx.HTTPError as exc:
        elapsed = time.perf_counter() - start_time
        response_time = round(elapsed * 1000, 2)
        status = "down"
        error_message = str(exc) or exc.__class__.__name__
    except Exception as exc:
        elapsed = time.perf_counter() - start_time
        response_time = round(elapsed * 1000, 2)
        status = "down"
        error_message = str(exc) or exc.__class__.__name__

    monitor.status = status
    monitor.response_time = response_time
    monitor.last_checked = datetime.now(timezone.utc)

    # --- Incident handling ---
    if status == "down":
        # Only create a new incident if there isn't already an open one
        existing = (
            db.query(Incident)
            .filter(Incident.monitor_id == monitor.id, Incident.status == "open")
            .first()
        )
        if not existing:
            db.add(
                Incident(
                    monitor_id=monitor.id,
                    started_at=datetime.now(timezone.utc),
                    status="open",
                    error_message=error_message or "Unknown failure",
                )
            )
    else:  # status == "up"
        # Resolve every open incident for this monitor
        open_incidents = (
            db.query(Incident)
            .filter(Incident.monitor_id == monitor.id, Incident.status == "open")
            .all()
        )
        for incident in open_incidents:
            incident.resolved_at = datetime.now(timezone.utc)
            incident.status = "resolved"


@router.post("/", response_model=MonitorRead)
def create_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
    new_monitor = Monitor(
        name=monitor.name,
        url=str(monitor.url),
        status="unknown",
    )
    db.add(new_monitor)
    db.commit()
    db.refresh(new_monitor)

    check_monitor(new_monitor, db)
    db.commit()
    db.refresh(new_monitor)

    return new_monitor


@router.get("/", response_model=list[MonitorRead])
def get_monitors(db: Session = Depends(get_db)):
    monitors = db.query(Monitor).all()
    for monitor in monitors:
        check_monitor(monitor, db)
    db.commit()
    return monitors


@router.delete("/{monitor_id}")
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        return {"message": "Monitor not found"}
    db.delete(monitor)
    db.commit()
    return {"message": "Monitor deleted successfully"}


@router.put("/{monitor_id}", response_model=MonitorRead)
def update_monitor(
    monitor_id: int,
    name: str,
    url: HttpUrl,
    db: Session = Depends(get_db),
):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    monitor.name = name
    monitor.url = str(url)

    check_monitor(monitor, db)
    db.commit()
    db.refresh(monitor)

    return monitor


@router.post("/{monitor_id}/check", response_model=MonitorRead)
def check_monitor_endpoint(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    check_monitor(monitor, db)
    db.commit()
    db.refresh(monitor)

    return monitor