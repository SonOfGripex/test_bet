from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class BetStatusEnum(enum.Enum):
    waiting = 'waiting'
    win = 'win'
    lose = 'lose'


class Bet(Base):
    __tablename__ = 'bets'

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    event_id = Column(Integer, nullable=False)
    status = Column(Enum(BetStatusEnum), default=BetStatusEnum.waiting)
