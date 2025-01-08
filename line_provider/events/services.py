import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Event as EventModel, EventStatusEnum
from .schemas import EventCreate, EventUpdate
from fastapi import HTTPException
from rabbit.connector import publish_message, RabbitMQConnection
from config import settings


async def get_event_by_id(db: AsyncSession, event_id: int) -> EventModel:
    result = await db.execute(select(EventModel).filter(EventModel.id == event_id))
    event = result.scalars().first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


async def get_all_events(
    db: AsyncSession,
    status: Optional[EventStatusEnum] = None,
    deadline: Optional[datetime] = None,
) -> List[EventModel]:
    query = select(EventModel)
    filters = []

    if status:
        filters.append(EventModel.status == status)
    if deadline:
        filters.append(EventModel.deadline <= deadline)

    if filters:
        query = query.filter(and_(*filters))

    result = await db.execute(query)
    return result.scalars().all()


async def add_event(db: AsyncSession, event: EventCreate) -> EventModel:
    db_event = EventModel(**event.dict())
    try:
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def change_event(db: AsyncSession, event_id: int, data: EventUpdate) -> EventModel:
    try:
        result = await db.execute(select(EventModel).filter(EventModel.id == event_id))
        db_event = result.scalars().first()

        original_coefficient = db_event.coefficient
        original_status = db_event.status

        if db_event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        for field, value in data.dict(exclude_unset=True).items():
            setattr(db_event, field, value)

        await db.commit()
        await db.refresh(db_event)

        if original_coefficient != db_event.coefficient or original_status != db_event.status:
            async with RabbitMQConnection() as connection:
                if connection:
                    message_dict = {
                        'event_id': db_event.id,
                        'status': db_event.status.value,
                        'coefficient': float(db_event.coefficient)
                    }
                    message_json = json.dumps(message_dict)
                    await publish_message(connection, settings.EVENTS_QUEUE, message_json)

        return db_event

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


