import grpc
from fastapi import HTTPException
from config import settings
from . import service_pb2
from . import service_pb2_grpc


async def check_event_existence_grpc(event_id: int):
    async with grpc.aio.insecure_channel("line_provider:50051") as channel:
        stub = service_pb2_grpc.EventExistenceServiceStub(channel)
        request = service_pb2.EventExistenceRequest(event_id=event_id)
        try:
            response = await stub.CheckEventExists(request)
            return response.exists
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail={'error': e})


async def get_event_by_id(event_id):
    async with grpc.aio.insecure_channel("line_provider:50051") as channel:
        stub = service_pb2_grpc.EventExistenceServiceStub(channel)
        request = service_pb2.GetEventRequest(event_id=event_id)
        try:
            response = await stub.GetEvent(request)
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None


async def get_all_events():
    async with grpc.aio.insecure_channel("line_provider:50051") as channel:
        stub = service_pb2_grpc.EventExistenceServiceStub(channel)
        next_page_token = ""
        all_events = []
        while True:
            request = service_pb2.GetAllEventsRequest(page_size=20, page_token=next_page_token)
            try:
                response = await stub.GetAllEvents(request)
                all_events.extend(response.events)
                if not response.next_page_token:
                    break

                next_page_token = response.next_page_token
            except Exception as e:
                print(f"Error: {e}")
                break

        return all_events
