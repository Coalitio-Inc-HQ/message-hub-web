import logging

from core import ActionDTO, MessageDTO, ChatDTO
from core.fastapi_app.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


async def trigger_front_new_waiting_chat(chat: ChatDTO):
    """
    Отдача информации о добавлении новых ожидающих чатов фронту

    :param chat: ChatDTO
    :return:
    """
    action = ActionDTO(
        name="new_waiting_chats",
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


async def trigger_front_new_user_in_chat(chat: ChatDTO, user_id: int):
    """
    Отдача информации о добавлении пользователя в новый чат
    TODO: Непонятно. Уточню.

    :param chat: ChatDTO
    :param user_id: int
    :return:
    """
    action = ActionDTO(
        name="new_user_in_chat",
        body={
            'chat': chat.model_dump(),
            'user_id': user_id
        })
    await websocket_manager.broadcast(action)
