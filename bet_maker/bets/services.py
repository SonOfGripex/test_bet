from typing import List
from database import AsyncSession, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from .models import Bet as BetModel
from .schemas import BetCreate
from fastapi import HTTPException


async def get_bet_by_id(db: AsyncSession, bet_id: int) -> BetModel:
    result = await db.execute(select(BetModel).filter(BetModel.id == bet_id))
    bet = result.scalars().first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    return bet


async def get_all_bets(db: AsyncSession) -> List[BetModel]:
    result = await db.execute(select(BetModel))
    return result.scalars().all()


async def add_bet(db: AsyncSession, bet: BetCreate) -> BetModel:
    db_bet = BetModel(**bet.dict())
    try:
        db.add(db_bet)
        await db.commit()
        await db.refresh(db_bet)
        return db_bet
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error: " + str(e))


async def update_bet_status(bet_data: dict) -> None:
    status = bet_data["status"]
    if status in ['win_1', 'win_2']:
        status = 'win' if status == 'win_1' else 'lose'
        db = AsyncSessionLocal()
        try:
            event_id = bet_data["event_id"]
            await db.execute(
                update(BetModel)
                .where(BetModel.event_id == event_id)
                .values(status=status)
            )
            await db.commit()
        finally:
            await db.close()
