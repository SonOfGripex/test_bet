from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from .schemas import EventUpdate, EventCreate, Event
from .models import EventStatusEnum
from .services import get_event_by_id, get_all_events, add_event, change_event

router = APIRouter()


@router.get("/", response_model=List[Event])
async def get_events(
    db: Session = Depends(get_db),
    status: Optional[EventStatusEnum] = Query(None),
    deadline: Optional[datetime] = Query(None),
):
    return await get_all_events(db, status, deadline)


@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    return await get_event_by_id(db, event_id)


@router.post("/", response_model=Event)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    try:
        return await add_event(db, event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{event_id}", response_model=Event)
async def update_event(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    try:
        return await change_event(db, event_id, event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))