from datetime import datetime


async def event_to_dict(event):
    if event.deadline:
        deadline_seconds = event.deadline.seconds
        deadline_nanos = event.deadline.nanos
        deadline_datetime = datetime.utcfromtimestamp(deadline_seconds + deadline_nanos / 1e9)
        deadline_str = deadline_datetime.isoformat()
    else:
        deadline_str = None
    status_dict = {
        1: "START_WAITING",
        2: "IN_PROCESS",
        3: "WIN_1",
        4: "WIN_2"
    }

    status = status_dict.get(event.status)

    return {
        "id": event.id,
        "coefficient": event.coefficient,
        "deadline": deadline_str,
        "status": status,
    }