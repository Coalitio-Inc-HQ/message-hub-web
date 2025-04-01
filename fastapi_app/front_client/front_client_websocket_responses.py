import datetime
import logging

from starlette.websockets import WebSocket

from fastapi_app.main_client.main_client_requests import get_chats_in_which_user_is_not_member
from fastapi_app.main_client.main_client_requests import get_chats_by_user
from fastapi_app.main_client.main_client_requests import get_users_by_chat
from fastapi_app.main_client.main_client_requests import get_messages_by_chat
from fastapi_app.main_client.main_client_requests import add_user_to_chat
from fastapi_app.main_client.main_client_requests import send_a_message_to_chat, remove_to_archive, set_last_read_message_id, get_platforms, delete_message
from fastapi_app.utils import check_body_format, error_catcher

from fastapi_app.websocket_manager import websocket_manager

from core import MessageDTO, UserInfoDTO, ActionDTO,MessageDTOFront
from core.schemes import ActionRequestDTO, ActionResponseDTO, RequestDTO, ResponseDTO

from fastapi_app.auth.auth_schemes import ExtUserDTO

from database.database_engine import session_factory
from sqlalchemy import update
from database.database_schemes import UserORM

import uuid

from fastapi_app.event_buffer import get_event_after_event_id, get_last_event_id

logger = logging.getLogger(__name__)


def get_websocket_response_actions() -> dict:
    return {
        # get_user_info=answer_front_user_info,
        # set_is_completed_tutorial=answer_front_set_is_completed_tutorial,
        # get_chats_in_which_user_is_not_member=answer_front_get_chats_in_which_user_is_not_member,
        "chat.list": answer_chat_list,
        "chat.user.list": answer_chat_user_list,
        "chat.message.list": answer_chat_message_list,
        "chat.user.add": answer_chat_user_add,
        "chat.message.send": answer_chat_message_send,
        # "get_chats": answer_get_chats,
        "chat.archive": answer_chat_archive,
        "chat.message.last_read_message_id": answer_chat_message_last_read_message_id,
        "platform.list": answer_platform_list,
        "chat.message.delete": answer_chat_message_delete,
        "events.sinc": answer_events_sinc,
    }


# @error_catcher("get_user_info")
# @check_body_format([])
# async def answer_front_user_info(id: uuid.UUID, body: dict, websocket: WebSocket | None, user: ExtUserDTO):
#     """
#     Ответ на запрос о получении информации о текущем пользователе

#     :param body: Dict[]
#     :param websocket: Websocket
#     :param user: User
#     :return:
#     """
#     action = ActionDTO(
#         id=id,
#         name="get_user_info",
#         body={
#             "user_info": UserInfoDTO.model_validate(user, from_attributes=True)
#         },
#         status_code=200,
#         error=None
#     )
#     # await websocket.send_json(action.model_dump())
#     await websocket_manager.send_personal_response(action, websocket)


# @error_catcher("is_completed_tutorial")
# @check_body_format([])
# async def answer_front_set_is_completed_tutorial(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
#     """
#     Ответ на запрос об установлении флага прохождения руководства пользователя.

#     :param body: Dict[]
#     :param websocket: Websocket
#     :param user: User
#     :return:
#     """

#     is_completed_tutorial = bool(body.get('is_completed_tutorial'))

#     async with session_factory() as conn:
#         await conn.execute(update(UserORM).where(UserORM.id==user.id).values(is_completed_tutorial=is_completed_tutorial))
#         await conn.commit()

#     action = ActionDTO(
#         id=id,
#         name="is_completed_tutorial",
#         body={
            
#         },
#         status_code=200,
#         error=None
#     )
#     # await websocket.send_json(action.model_dump())
#     await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.list")
@check_body_format([])
async def answer_chat_list(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос о получении чатов пользователя от фронта.

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chats = await get_chats_by_user(user.id)

    await websocket_manager.connect_user_to_chats(user.id, [chat['id'] for chat in chats])

    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.list",
            status_code=200,
            body={"chats": chats},
            error=None
        )
    )
    await websocket_manager.send_personal_response(action, websocket)


# @error_catcher("get_chats")
# @check_body_format([])
# async def answer_get_chats(id: uuid.UUID, body: dict, websocket: WebSocket | None, user: ExtUserDTO):
#     """
#     Ответ на запрос о получении чатов пользователя от фронта.

#     :param body: Dict[]
#     :param websocket: Websocket
#     :param user: User
#     :return:
#     """
#     chats = await get_chats_by_user(user.id)

#     await websocket_manager.connect_user_to_chats(user.id, [chat['id'] for chat in chats])

#     action = ActionDTO(
#         id=id,
#         name="get_chats",
#         body={
#             "chats": chats
#         },
#         status_code=200,
#         error=None
#     )
#     await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.user.list")
@check_body_format(['chat_id'])
async def answer_chat_user_list(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос о получении пользователей чата от фронта.

    :param body: Dict[chat_id: int]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = request.obj.body.get('chat_id')
    users = await get_users_by_chat(chat_id)

    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.user.list",
            status_code=200,
            body={
                "chat_id": chat_id,
                "users": users
            },
            error=None
        )
    )
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.message.list")
@check_body_format(['chat_id', 'count', 'offset_message_id','include_messege','mode'])
async def answer_chat_message_list(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос о получении сообщений в чате от фронта.

    :param body: Dict[chat_id: int, count: int = 50, offset_message_id: int = -1]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = request.obj.body.get('chat_id')
    count = request.obj.body.get('count')
    offset_message_id = request.obj.body.get('offset_message_id')
    include_messege = request.obj.body.get('include_messege')
    mode = request.obj.body.get('mode')
    messages = await get_messages_by_chat(chat_id, count, offset_message_id, include_messege, mode)

    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.message.list",
            status_code=200,
            body={
                "chat_id":chat_id,
                "messages": messages,
                "offset_message_id":offset_message_id,
                "include_messege": include_messege,
                "mode": mode,
            },
            error=None
        )
    )

    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.user.add")
@check_body_format(['chat_id', 'user_id', 'event_id'])
async def answer_chat_user_add(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Добавление пользователя к чату

    :param body: Dict[chat_id: int, user_id: int]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = request.obj.body.get('chat_id')
    user_id = request.obj.body.get('user_id')
    event_id = uuid.UUID(request.obj.body.get('event_id'))

    chat_users = await add_user_to_chat(
        chat_id,
        user_id,
        event_id,
    )

    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.user.add",
            status_code=200,
            body={
                "chat_users": chat_users,
                "event_id": str(event_id),
            },
            error=None
        )
    )

    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.message.send")
@check_body_format(['message', 'event_id'])
async def answer_chat_message_send(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Обработчик отправки сообщения в чат из фронта

    :param body: Dict[message: Message]
    :param websocket: Websocket
    :param user: User
    :return:
    """

    event_id = uuid.UUID(request.obj.body.get('event_id'))
    message = request.obj.body.get('message')
    message = MessageDTOFront(**message)
    message.sender_id = user.id
    message.sended_at = datetime.datetime.now().isoformat()

    res = await send_a_message_to_chat(MessageDTO.model_validate(message,from_attributes=True), event_id)

    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.message.send",
            status_code=200,
            body={
                "message_id": res["message_id"],
                "front_message_id": message.front_message_id,
                "chat_id": message.chat_id,
                "event_id": str(event_id),
            },
            error=None
        )
    )

    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.archive")
@check_body_format(['chat_id'])
async def answer_chat_archive(request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос об отправке чата в архив.

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = request.obj.body.get('chat_id')
    event_id = uuid.UUID(request.obj.body.get('event_id'))

    await remove_to_archive(chat_id, event_id)


    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.archive",
            status_code=200,
            body={
                "chat_id": chat_id,
                "event_id": str(event_id),
            },
            error=None
        )
    )

    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.message.last_read_message_id")
@check_body_format(['chat_id','last_read_message_id','event_id'])
async def answer_chat_message_last_read_message_id (request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос на установку последнего прочитанного сообщения.

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = request.obj.body.get('chat_id')
    event_id = uuid.UUID(request.obj.body.get('event_id'))
    last_read_message_id = request.obj.body.get('last_read_message_id')

    await set_last_read_message_id(chat_id, user.id, last_read_message_id, event_id)


    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.message.last_read_message_id",
            status_code=200,
            body={
                "chat_id": chat_id,
                "last_read_message_id": last_read_message_id,
                "event_id": str(event_id),
            },
            error=None
        )
    )

    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("platform.list")
@check_body_format([])
async def answer_platform_list (request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос получения платформ.

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """

    platforms = await get_platforms()


    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="platform.list",
            status_code=200,
            body={
                "platforms": platforms,
            },
            error=None
        )
    )

    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("chat.message.delete")
@check_body_format(["message_id","event_id"])
async def answer_chat_message_delete (request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос удаления сообщения.

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    message_id = int(request.obj.body.get('message_id'))
    event_id = uuid.UUID(request.obj.body.get('event_id'))

    platforms = await delete_message(user.id, message_id, event_id)


    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="chat.message.delete",
            status_code=200,
            body={
                "message_id":message_id,
                "event_id": event_id,
            },
            error=None
        )
    )

    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("events.sinc")
@check_body_format(["last_event_id"])
async def answer_events_sinc (request: ActionRequestDTO, websocket: WebSocket | None, user: ExtUserDTO):
    """
    Ответ на запрос получения последних событий.

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    last_event_id = request.obj.body.get('last_event_id')


    serch_info = get_event_after_event_id(last_event_id)

    action = ActionResponseDTO(
        id=request.id,
        obj=ResponseDTO(
            name="events.sinc",
            status_code=200,
            body={
                "last_event_id": get_last_event_id(),
                "events": serch_info["events"],
                "find_event": serch_info["find_event"],
            },
            error=None
        )
    )

    await websocket_manager.send_personal_response(action, websocket)
