from pydantic import BaseModel
from .models import BetStatusEnum


class BetBase(BaseModel):
    amount: int
    event_id: int


class BetCreate(BetBase):
    pass


class Bet(BetBase):
    id: int
    status: BetStatusEnum

    class Config:
        orm_mode = True