import logging

from core import ActionDTO, MessageDTO, ChatDTO, UserDTO
from fastapi_app.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


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