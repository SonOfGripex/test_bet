import grpc
import asyncio
from sqlalchemy.future import select
from concurrent import futures
from sqlalchemy.sql import exists
from database import AsyncSessionLocal
import google.protobuf.timestamp_pb2 as timestamp_pb2
from events.models import Event, EventStatusEnum
from . import service_pb2
from . import service_pb2_grpc
from config import settings
from datetime import datetime


def sqlalchemy_event_to_protobuf_event(event):
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(event.deadline)

    return service_pb2.Event(
        id=event.id,
        coefficient=float(event.coefficient),
        deadline=timestamp,
        status=event.status.value.upper(),
    )


class EventExistenceServicer(service_pb2_grpc.EventExistenceServiceServicer):
    async def CheckEventExists(self, request, context):
        event_id = request.event_id
        db = AsyncSessionLocal()
        try:
            stmt = select(exists().where(
                Event.id == event_id,
                Event.deadline > datetime.utcnow(),
                Event.status.in_([EventStatusEnum.start_waiting, EventStatusEnum.in_process])
            ))
            result = await db.execute(stmt)
            is_exist = result.scalar()
            return service_pb2.EventExistenceReply(exists=is_exist)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(e)
            return service_pb2.EventExistenceReply(exists=False)
        finally:
            await db.close()

    async def GetEvent(self, request, context):
        event_id = request.event_id
        db = AsyncSessionLocal()
        try:
            event = await db.execute(select(Event).filter(Event.id == event_id))
            event = event.scalars().first()
            if event:
                return sqlalchemy_event_to_protobuf_event(event)
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return service_pb2.Event()
        except Exception as e:
            print(f"Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.Event()
        finally:
            await db.close()

    async def GetAllEvents(self, request, context):
        page_size = request.page_size or 100
        page_token = request.page_token or ""
        db = AsyncSessionLocal()
        try:
            query = select(Event)
            if page_token:
                try:
                    offset = int(page_token)
                    query = query.offset(offset)
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    return service_pb2.GetAllEventsResponse()

            query = query.limit(page_size)
            result = await db.execute(query)
            events = result.scalars().all()
            events_pb = [sqlalchemy_event_to_protobuf_event(event) for event in events]
            next_page_token = (
                str(int(page_token or 0) + page_size) if len(events) == page_size else ""
            )

            return service_pb2.GetAllEventsResponse(events=events_pb, next_page_token=next_page_token)
        except Exception as e:
            print(f"Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return service_pb2.GetAllEventsResponse()
        finally:
            await db.close()


class GRPCServer:
    def __init__(self):
        self.server = grpc.aio.server()
        service_pb2_grpc.add_EventExistenceServiceServicer_to_server(
            EventExistenceServicer(), self.server
        )
        self.server.add_insecure_port("line_provider:50051")

    async def serve(self):
        await self.server.start()
        print(f"gRPC listening line_provider:50051")
        await self.server.wait_for_termination()

    async def stop(self):
        await self.server.stop(0)


grpc_server_instance = GRPCServer()