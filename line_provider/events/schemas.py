from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from .models import EventStatusEnum


class EventBase(BaseModel):
    coefficient: Decimal


class EventCreate(EventBase):
    deadline: datetime


class EventUpdate(BaseModel):
    status: Optional[EventStatusEnum] = None
    coefficient: Optional[Decimal] = None


class Event(EventBase):
    id: int
    status: EventStatusEnum

    class Config:
        orm_mode = True