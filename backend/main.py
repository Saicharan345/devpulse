from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routes.monitors import router as monitor_router
from app.routes.incidents import router as incident_router


Base.metadata.create_all(bind=engine)


app = FastAPI(title="DevPulse API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(monitor_router)
app.include_router(incident_router)


@app.get("/")
def home():
    return {
        "message": "DevPulse API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }