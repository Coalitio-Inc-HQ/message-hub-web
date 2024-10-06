import logging

from core import ActionDTO, MessageDTO, ChatDTO, UserDTO, Event
from fastapi_app.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


def get_websocket_event_handlers():
    return {
        "chat.update":handler_from_main_chat_update,
    }

async def handler_from_main_chat_update(event: Event):
    """
    Обновлено состояние чата
    """
    action = ActionDTO(
        name="chat.update",
        body={
            "chat": event.data
        })
    await websocket_manager.broadcast(action)




async def trigger_front_new_chat(chat: ChatDTO):
    """
    Отдача информации о добавлении новых ожидающих чатов фронту

    :param chat: ChatDTO
    :return:
    """
    action = ActionDTO(
        name="new_chat",
        body={
            "chat": chat.model_dump()
        })
    await websocket_manager.broadcast(action)


async def trigger_front_new_message_in_chat(message: MessageDTO):
    """
    Отдача информации о новом сообщении в чате

    :param message: MessageDTO
    :return:
    """
    action = ActionDTO(
        name="new_message",
        body={
            "message": message.model_dump()
        })
    await websocket_manager.broadcast(action)

async def trigger_front_new_message_in_chat_personal(message: MessageDTO):
    """
    Отдача информации о новом сообщении в чате

    :param message: MessageDTO
    :return:
    """
    action = ActionDTO(
        name="new_message",
        body={
            "message": message.model_dump()
        })
    await websocket_manager.send_to_chat(action, message.chat_id)


async def trigger_front_new_user_in_chat(chat: ChatDTO, user: UserDTO):
    """
    Отдача информации о добавлении пользователя в новый чат

    :param chat: ChatDTO
    :param user: UserDTO
    :return:
    """
    action = ActionDTO(
        name="new_user_in_chat",
        body={
            'chat': chat.model_dump(),
            'user': user.model_dump()
        })
    await websocket_manager.broadcast(action)