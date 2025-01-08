from grpc_server.services import check_event_existence_grpc
from fastapi import HTTPException


async def verify_event_existence(event_id: int):
    exists = await check_event_existence_grpc(event_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Event not found or already finished")
    return event_id