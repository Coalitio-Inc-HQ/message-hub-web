import logging

from core import ActionDTO, MessageDTO, ChatDTO, UserDTO, Event, ActionEventDTO, EventDTO
from fastapi_app.websocket_manager import websocket_manager

from fastapi_app.event_buffer import push

import uuid

logger = logging.getLogger(__name__)


def get_websocket_event_handlers():
    return {
        "chat.update":handler_from_main_chat_update,
        "chat.new_message": handler_from_main_new_message_in_chat,
        "chat.delete_message": handler_from_main_delete_message,
        "chat.add.user": handler_from_main_new_user_in_chat,
        "chat.set.last_read_message_id": handler_from_main_set_last_read_message_id,
    }

async def handler_from_main_chat_update(event: Event):
    """
    Обновлено состояние чата
    """
    event_front = ActionEventDTO(
        id=uuid.uuid4(),
        obj=EventDTO(
            event_id = str(event.id),
            name="chat.update",
            body={
                "chat": event.data["chat"],
            }
        )
    )

    # action = ActionDTO(
    #     id=uuid.uuid4(),
    #     name="chat.update",
    #     body={
    #         "chat": event.data["chat"],
    #     })
    push(event_front)
    await websocket_manager.broadcast(event_front)

async def handler_from_main_new_message_in_chat(event: Event):
    """
    Отдача информации о новом сообщении в чате
    """
    message = MessageDTO.model_validate(event.data["message"])

    event_front = ActionEventDTO(
        id=uuid.uuid4(),
        obj=EventDTO(
            event_id = str(event.id),
            name="chat.new_message",
            body={
                "message": message.model_dump(),
            }
        )
    )

    # action = ActionDTO(
    #     id=uuid.uuid4(),
    #     name="chat.new_message",
    #     body={
    #         "message": message.model_dump(),
    #         "event_id": str(event.id),
    #     })
    push(event_front)
    await websocket_manager.broadcast(event_front)

async def handler_from_main_delete_message(event: Event):
    """
    Отдача информации о удалении собщения
    """
    message = MessageDTO.model_validate(event.data["message"])

    event_front = ActionEventDTO(
        id=uuid.uuid4(),
        obj=EventDTO(
            event_id = str(event.id),
            name="chat.delete_message",
            body={
                "message": message.model_dump(),
            }
        )
    )

    # action = ActionDTO(
    #     id=uuid.uuid4(),
    #     name="chat.delete_message",
    #     body={
    #         "message": message.model_dump(),
    #         "event_id": str(event.id),
    #     })
    
    push(event_front)
    await websocket_manager.broadcast(event_front)

async def handler_from_main_new_user_in_chat(event: Event):
    """
    Отдача информации о добавлении пользователя в новый чат
    """
    chat = ChatDTO.model_validate(event.data["chat"])
    user = UserDTO.model_validate(event.data["user"])

    event_front = ActionEventDTO(
        id=uuid.uuid4(),
        obj=EventDTO(
            event_id = str(event.id),
            name="chat.add.user",
            body={
                'chat': chat.model_dump(),
                'user': user.model_dump(),
            }
        )
    )

    # action = ActionDTO(
    #     id=uuid.uuid4(),
    #     name="chat.add.user",
    #     body={
    #         'chat': chat.model_dump(),
    #         'user': user.model_dump(),
    #         "event_id": str(event.id),
    #     })
    
    push(event_front)
    await websocket_manager.broadcast(event_front)

async def handler_from_main_set_last_read_message_id(event: Event):
    """
    Отдача информации об установленом последнем прочитанном сообщенеии
    """

    event_front = ActionEventDTO(
        id=uuid.uuid4(),
        obj=EventDTO(
            event_id = str(event.id),
            name="chat.set.last_read_message_id",
            body={
                "chat_id": event.data["chat_id"],
                "user_id": event.data["user_id"],
                "last_read_message_id": event.data["last_read_message_id"],
                "count": event.data["count"],
            }
        )
    )

    # action = ActionDTO(
    #     id=uuid.uuid4(),
    #     name="chat.set.last_read_message_id",
    #     body={
    #         "chat_id": event.data["chat_id"],
    #         "user_id": event.data["user_id"],
    #         "last_read_message_id": event.data["last_read_message_id"],
    #         "count": event.data["count"],
    #         "event_id": str(event.id),
    #     })
    
    push(event_front)
    await websocket_manager.send_to_user_by_user_id(event_front, event.data["user_id"])









# async def trigger_front_new_chat(chat: ChatDTO):
#     """
#     Отдача информации о добавлении новых ожидающих чатов фронту

#     :param chat: ChatDTO
#     :return:
#     """
#     action = ActionDTO(
#         name="new_chat",
#         body={
#             "chat": chat.model_dump()
#         })
#     await websocket_manager.broadcast(action)


# async def trigger_front_new_message_in_chat(message: MessageDTO):
#     """
#     Отдача информации о новом сообщении в чате

#     :param message: MessageDTO
#     :return:
#     """
#     action = ActionDTO(
#         name="new_message",
#         body={
#             "message": message.model_dump()
#         })
#     await websocket_manager.broadcast(action)

# async def trigger_front_new_message_in_chat_personal(message: MessageDTO):
#     """
#     Отдача информации о новом сообщении в чате

#     :param message: MessageDTO
#     :return:
#     """
#     action = ActionDTO(
#         name="new_message",
#         body={
#             "message": message.model_dump()
#         })
#     await websocket_manager.send_to_chat(action, message.chat_id)


# async def trigger_front_new_user_in_chat(chat: ChatDTO, user: UserDTO):
#     """
#     Отдача информации о добавлении пользователя в новый чат

#     :param chat: ChatDTO
#     :param user: UserDTO
#     :return:
#     """
#     action = ActionDTO(
#         name="new_user_in_chat",
#         body={
#             'chat': chat.model_dump(),
#             'user': user.model_dump()
#         })
#     await websocket_manager.broadcast(action)