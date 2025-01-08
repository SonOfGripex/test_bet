from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from grpc_server.services import get_event_by_id, get_all_events
from .services import event_to_dict

router = APIRouter()


@router.get("/")
async def get_events():
    try:
        events = await get_all_events()
        events_json = [await event_to_dict(event) for event in events]
        return JSONResponse(content=events_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.get("/{event_id}")
async def get_event(event_id):
    try:
        event = await get_event_by_id(int(event_id))
        if not event:
            raise HTTPException(status_code=400, detail="Event not found")
        events_json = await event_to_dict(event)
        return JSONResponse(content=events_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
