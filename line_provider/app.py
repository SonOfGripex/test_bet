from fastapi import FastAPI
import asyncio
from grpc_server.services import grpc_server_instance
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from events.routers import router as events_router


app = FastAPI()
shutdown_event = asyncio.Event()

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
    grpc_task = asyncio.create_task(grpc_server_instance.serve())

@app.on_event("shutdown")
async def shutdown():
    shutdown_event.set()
    await grpc_server_instance.stop()

app.include_router(events_router, prefix="/events", tags=["events"])