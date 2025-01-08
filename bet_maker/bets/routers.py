from typing import List
from fastapi import APIRouter, Depends, HTTPException
from dependencies import verify_event_existence
from sqlalchemy.orm import Session
from database import get_db
from .schemas import BetCreate, Bet
from .services import get_bet_by_id, get_all_bets, add_bet

router = APIRouter()


@router.get("/", response_model=List[Bet])
async def get_bets(db: Session = Depends(get_db)):
    return await get_all_bets(db)


@router.get("/{bet_id}", response_model=Bet)
async def get_bet(bet_id: int, db: Session = Depends(get_db)):
    return await get_bet_by_id(db, bet_id)


@router.post("/", response_model=Bet)
async def create_bet(bet: BetCreate, db: Session = Depends(get_db)):
    try:
        await verify_event_existence(bet.event_id)
        return await add_bet(db, bet)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))