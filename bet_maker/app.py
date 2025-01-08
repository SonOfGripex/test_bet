import asyncio
from fastapi import FastAPI
from config import settings
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from rabbit.connector import consume_messages
from bets.routers import router as bets_router
from events.router import router as events_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(consume_messages(settings.EVENTS_QUEUE))


app.include_router(bets_router, prefix="/bets", tags=["bets"])
app.include_router(events_router, prefix="/events", tags=["events"])
