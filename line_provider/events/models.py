import enum
from sqlalchemy import Column, Numeric, DateTime, Enum, Integer
from database import Base
from datetime import datetime


class EventStatusEnum(enum.Enum):
    start_waiting = "start_waiting"
    in_process = "in_process"
    win_1 = 'win_1'
    win_2 = 'win_2'


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coefficient = Column(Numeric(10, 2), default=0.00)
    deadline = Column(DateTime(timezone=True), default=datetime.utcnow)
    status = Column(Enum(EventStatusEnum), default=EventStatusEnum.start_waiting)
