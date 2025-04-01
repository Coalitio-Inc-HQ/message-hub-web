from collections import deque
from core.schemes import ActionEventDTO, EventDTO

EVENT_BUFFER_SIZE = 200
event_buffer = deque(maxlen=EVENT_BUFFER_SIZE)
last_event_id = None

def push(event: ActionEventDTO):
    """Добовляет событие в очередь"""
    last_event_id = event.obj.event_id
    event_buffer.append(event)

def get_event_after_event_id(event_id):
    """Возвращает список событий, которые идут после события с указанным event_id."""
    for i, event in enumerate(event_buffer):
        if event.obj.event_id == event_id:
            return {
                "events": list(event_buffer)[i + 1:],
                "find_event": True,
            }

    return {
                "events": [],
                "find_event": False,
            }

def get_last_event_id():
    """Возращяет id последнего известного события серверу"""
    return last_event_id