from collections import deque
from core import ActionDTO

EVENT_BUFFER_SIZE = 200
event_buffer = deque(maxlen=EVENT_BUFFER_SIZE)

def push(message: ActionDTO):
    """Добовляет событие в очередь"""
    event_buffer.append(message)

def get_event_after_event_id(event_id: str):
    """Возвращает список событий, которые идут после события с указанным event_id."""
    for i, event in enumerate(event_buffer):
        if getattr(event, "event_id", None) == event_id:
            return list(event_buffer)[i + 1:]

    return []
