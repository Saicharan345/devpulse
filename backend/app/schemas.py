from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class MonitorCreate(BaseModel):
    name: str
    url: HttpUrl


class MonitorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    status: str
    response_time: Optional[float]
    last_checked: Optional[datetime]
    created_at: Optional[datetime]


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: int
    started_at: Optional[datetime]
    resolved_at: Optional[datetime]
    status: str
    error_message: Optional[str]