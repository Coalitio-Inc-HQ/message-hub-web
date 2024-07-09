import logging

from core import ActionDTO, MessageDTO, ChatDTO, UserDTO
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
    await websocket_manager.send_to_chat(action, message.chat_id)


async def trigger_front_new_broadcast_message_in_chat(message: MessageDTO):
    """
    Отдача информации о новом сообщении в ожидаюшем чате

    :param message: MessageDTO
    :return:
    """
    action = ActionDTO(
        name="new_broadcast_message",
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
    await websocket_manager.send_to_chat(action, chat.id)
    await websocket_manager.connect_user_to_chat(user.id, chat.id)
    await websocket_manager.send_to_user_by_user_id(action, user.id)


async def trigger_front_delite_waiting_chat(chat: ChatDTO):
    """
    Отдача информации о удалении ожидающих чатов фронту

    :param chat: ChatDTO
    :return:
    """
    action = ActionDTO(
        name="delite_waiting_chats",
        body={
            "chat": chat.model_dump()
        })
    await websocket_manager.broadcast(action)
