from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Monitor
from app.schemas import MonitorCreate
from pydantic import HttpUrl


router = APIRouter(prefix="/monitors", tags=["Monitors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_monitor(
    monitor: MonitorCreate,
    db: Session = Depends(get_db)
):
    new_monitor = Monitor(
        name=monitor.name,
        url=str(monitor.url),
    )

    db.add(new_monitor)
    db.commit()
    db.refresh(new_monitor)

    return new_monitor

@router.get("/")
def get_monitors(db: Session = Depends(get_db)):
    monitors = db.query(Monitor).all()
    return monitors

@router.delete("/{monitor_id}")
def delete_monitor(
    monitor_id: int,
    db: Session = Depends(get_db)
):
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id)
        .first()
    )

    if not monitor:
        return {
            "message": "Monitor not found"
        }

    db.delete(monitor)
    db.commit()

    return {
        "message": "Monitor deleted successfully"
    }

@router.put("/{monitor_id}")
def update_monitor(
    monitor_id: int,
    name: str,
    url: HttpUrl,
    db: Session = Depends(get_db)
):
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id)
        .first()
    )

    if not monitor:
        return {
            "message": "Monitor not found"
        }

    monitor.name = name
    monitor.url = str(url)

    db.commit()
    db.refresh(monitor)

    return monitor