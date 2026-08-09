from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Incident
from app.schemas import IncidentRead


router = APIRouter(prefix="/incidents", tags=["Incidents"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[IncidentRead])
def get_incidents(db: Session = Depends(get_db)):
    incidents = (
        db.query(Incident)
        .order_by(Incident.started_at.desc())
        .all()
    )
    return incidents