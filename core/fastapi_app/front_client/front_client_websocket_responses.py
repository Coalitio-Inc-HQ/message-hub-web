import datetime
import logging

from starlette.websockets import WebSocket

from core.fastapi_app.main_client.main_client_requests import get_waiting_chats
from core.fastapi_app.main_client.main_client_requests import get_chats_by_user
from core.fastapi_app.main_client.main_client_requests import get_users_by_chat
from core.fastapi_app.main_client.main_client_requests import get_messages_by_chat
from core.fastapi_app.main_client.main_client_requests import get_messages_by_waiting_chat
from core.fastapi_app.main_client.main_client_requests import connect_to_waiting_chat
from core.fastapi_app.main_client.main_client_requests import add_user_to_chat
from core.fastapi_app.main_client.main_client_requests import send_a_message_to_chat
from core.fastapi_app.utils import check_body_format, error_catcher
from core.fastapi_app.utils import get_json_string_of_an_array

from core.fastapi_app.websocket_manager import websocket_manager

from core import MessageDTO, ActionsMapTypedDict, UserInfoDTO, ActionDTOOut

from core.fastapi_app.auth.database import User

logger = logging.getLogger(__name__)


def get_websocket_response_actions() -> ActionsMapTypedDict:
    return ActionsMapTypedDict(
        get_user_info=answer_front_user_info,
        get_waiting_chats=answer_front_waiting_chats,
        get_chats_by_user=answer_front_chats_by_user,
        get_users_by_chat=answer_front_users_by_chat,
        get_messages_by_chat=answer_front_messages_from_chat,
        get_messages_by_waiting_chat=answer_front_messages_from_waiting_chat,
        connect_to_waiting_chat=answer_front_connect_to_waiting_chat,
        add_user_to_chat=answer_front_add_user_to_chat,
        send_message_to_chat=process_front_message_to_chat
    )


@check_body_format([])
async def answer_front_user_info(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении информации о текущем пользователе

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    action = ActionDTOOut(
        name="get_user_info",
        body={
            "user_info": UserInfoDTO.model_validate(user, from_attributes=True)
        },
        status_code=200,
        error=None
    )
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("get_waiting_chats")
@check_body_format(['count'])
async def answer_front_waiting_chats(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении ожидающих чатов от фронта

    :param body: Dict[count: int]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    count = body.get('count')

    chats = await get_waiting_chats(
        int(count)
    )
    action = ActionDTOOut(
        name="get_waiting_chats",
        body={
            "chats": get_json_string_of_an_array(chats)
        },
        status_code=200,
        error=None
    )
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("get_chats_by_user")
@check_body_format([])
async def answer_front_chats_by_user(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении чатов пользователя от фронта.

    :param body: Dict[]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chats = await get_chats_by_user(user.id)

    await websocket_manager.connect_user_to_chats(user.id, [chat.id for chat in chats])

    action = ActionDTOOut(
        name="get_chats_by_user",
        body={
            "chats": get_json_string_of_an_array(chats)
        },
        status_code=200,
        error=None
    )
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("get_users_by_chat")
@check_body_format(['chat_id'])
async def answer_front_users_by_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении пользователей чата от фронта.

    :param body: Dict[chat_id: int]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = body.get('chat_id')
    chats = await get_users_by_chat(user.id, chat_id)

    action = ActionDTOOut(
        name="get_users_by_chat",
        body={
            "chat_id": chat_id,
            "users": get_json_string_of_an_array(chats)
        },
        status_code=200,
        error=None
    )

    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("get_messages_by_chat")
@check_body_format(['chat_id', 'count', 'offset_message_id'])
async def answer_front_messages_from_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении сообщений в чате от фронта.

    :param body: Dict[chat_id: int, count: int = 50, offset_message_id: int = -1]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = body.get('chat_id')
    count = body.get('count')
    offset_message_id = body.get('offset_message_id')
    messages = await get_messages_by_chat(user.id, chat_id, count, offset_message_id)

    action = ActionDTOOut(
        name="get_messages_by_chat",
        body={
            "messages": get_json_string_of_an_array(messages)
        },
        status_code=200,
        error=None
    )
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("get_messages_by_waiting_chat")
@check_body_format(['chat_id', 'count', 'offset_message_id'])
async def answer_front_messages_from_waiting_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении сообщений из ожидающего чата от фронта.

    :param body: Dict[chat_id: int, count: int = 50, offset_message_id: int = -1]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = body.get('chat_id')
    count = body.get('count')
    offset_message_id = body.get('offset_message_id')
    messages = await get_messages_by_waiting_chat(chat_id, count, offset_message_id)

    print(messages)

    action = ActionDTOOut(
        name="get_messages_by_waiting_chat",
        body={
            "messages": get_json_string_of_an_array(messages)
        },
        status_code=200,
        error=None
    )
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("connect_to_waiting_chat")
@check_body_format(['chat_id'])
async def answer_front_connect_to_waiting_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Присоединение к ожидающему чату

    :param body: Dict[chat_id: int]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = body.get('chat_id')

    chats = await connect_to_waiting_chat(
        user.id,
        chat_id
    )  # Получаем ChatDTO с главного сервера, который мы потом отправим во фронт

    action = ActionDTOOut(
        name="connect_to_waiting_chat",
        body={
            "chat": chats.model_dump_json()
        },
        status_code=200,
        error=None
    )
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("add_user_to_chat")
@check_body_format(['chat_id', 'user_id'])
async def answer_front_add_user_to_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Добавление пользователя к чату

    :param body: Dict[chat_id: int, user_id: int]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    chat_id = body.get('chat_id')
    user_id = body.get('user_id')

    chat_users = await add_user_to_chat(
        user_id,
        chat_id
    )

    action = ActionDTOOut(
        name="add_user_to_chat",
        body={
            "chat_users": chat_users.model_dump_json()
        },
        status_code=200,
        error=None
    )
    await websocket_manager.send_personal_response(action, websocket)


@error_catcher("send_message_to_chat")
@check_body_format(['message'])
async def process_front_message_to_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Обработчик отправки сообщения в чат из фронта

    :param body: Dict[message: Message]
    :param websocket: Websocket
    :param user: User
    :return:
    """
    message = body.get('message')
    message = MessageDTO(**message)
    message.sender_id = user.id
    message.sended_at = datetime.datetime.now().isoformat()

    await send_a_message_to_chat(message)
    action = ActionDTOOut(
        name="send_message_to_chat",
        body={},
        status_code=200,
        error=None
    )
    await websocket_manager.send_personal_response(action, websocket)
