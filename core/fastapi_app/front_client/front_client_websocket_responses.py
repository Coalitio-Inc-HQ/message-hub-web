import logging

from starlette.websockets import WebSocket

from core.fastapi_app.main_client.main_client_requests import get_waiting_chats
from core.fastapi_app.main_client.main_client_requests import get_chats_by_user
from core.fastapi_app.main_client.main_client_requests import get_users_by_chat
from core.fastapi_app.main_client.main_client_requests import get_messages_by_chat
from core.fastapi_app.main_client.main_client_requests import get_messages_by_waiting_chat
from core.fastapi_app.main_client.main_client_requests import send_a_message_to_chat
from core.fastapi_app.utils import check_body_format
from core.fastapi_app.utils import get_json_string_of_an_array

from core.fastapi_app.websocket_manager import websocket_manager

from core import ActionDTO, MessageDTO, ActionsMapTypedDict,UserInfoDTO
from core import WrongBodyFormatException

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
        send_message_to_chat=process_front_message_to_chat
        # будут ещё
    )

@check_body_format([])
async  def answer_front_user_info(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении информаци о текущем пользователе

    :param body: Dict[]
    :param websocket: Websocket
    :return:
    """

    action = ActionDTO(
        name="get_waiting_chats",
        body={
            "user_info": UserInfoDTO.model_validate(user, from_attributes=True)
        })
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format(['count'])
async def answer_front_waiting_chats(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении ожидающих чатов от фронта

    :param body: Dict[count: int]
    :param websocket: Websocket
    :return:
    """
    count = body.get('count')
    try:
        chats = await get_waiting_chats(
            int(count)
        )  # Получаем ChatDTO с главного сервера, который мы потом отправим во фронт
    except ValueError:
        raise WrongBodyFormatException("Неверный формат данных в Body")

    action = ActionDTO(
        name="get_waiting_chats",
        body={
            "chats": get_json_string_of_an_array(chats)
        })
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format([])
async def answer_front_chats_by_user(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении чатов пользователя от фронта.

    "TODO: убери дублирование кода, связанное со схожестью первых двух методов"
    :param body: Dict[]
    :param websocket: Websocket
    :return:
    """
    chats = await get_chats_by_user(user.user_id)

    action = ActionDTO(
        name="get_chats_by_user",
        body={
            "chats": get_json_string_of_an_array(chats)
        })
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format(['chat_id'])
async def answer_front_users_by_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении пользователей чата от фронта.

    :param body: Dict[chat_id: int]
    :param websocket: Websocket
    :return:
    """
    chat_id = body.get('chat_id')
    chats = await get_users_by_chat(user.user_id, chat_id)

    action = ActionDTO(
        name="get_users_by_chat",
        body={
            "chat_id": chat_id,
            "users": get_json_string_of_an_array(chats)
        })

    await websocket_manager.send_personal_response(action, websocket)




@check_body_format(['chat_id', 'count', 'offset_message_id'])
async def answer_front_messages_from_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении сообщений в чате от фронта.

    :param body: Dict[chat_id: int, count: int = 50, offset_message_id: int = -1]
    :param websocket: Websocket
    :return:
    """
    chat_id = body.get('chat_id')
    count = body.get('count')
    offset_message_id = body.get('offset_message_id')
    messages = await get_messages_by_chat(user.user_id, chat_id, count, offset_message_id)

    print(messages)

    action = ActionDTO(
        name="get_messages_by_chat",
        body={
            "messages": get_json_string_of_an_array(messages)
        })
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format(['chat_id', 'count', 'offset_message_id'])
async def answer_front_messages_from_waiting_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Ответ на запрос о получении сообщений из ожидающего чата от фронта.

    :param body: Dict[chat_id: int, count: int = 50, offset_message_id: int = -1]
    :param websocket: Websocket
    :return:
    """
    chat_id = body.get('chat_id')
    count = body.get('count')
    offset_message_id = body.get('offset_message_id')
    messages = await get_messages_by_waiting_chat(chat_id, count, offset_message_id)

    print(messages)

    action = ActionDTO(
        name="get_messages_by_waiting_chat",
        body={
            "messages": get_json_string_of_an_array(messages)
        })
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format(['message'])
async def process_front_message_to_chat(body: dict, websocket: WebSocket | None, user: User):
    """
    Обработчик отправки сообщения в чат из фронта

    :param body: Dict[message: Message]
    :param websocket: Websocket
    :return:
    """
    message = body.get('message')
    print(message)
    message = MessageDTO(**message)
    message.sender_id = user.user_id
    try:
        await send_a_message_to_chat(message)
        action = ActionDTO(
            name="status",
            body={
                "ok": True
            }
        )
    except Exception as e:
        action = ActionDTO(
            name="status",
            body={
                "ok": False
            }
        )
        logger.error("Ошибка при отправки сообщения на главный сервер\n" + e)
    # await websocket.send_json(action.model_dump())
    await websocket_manager.send_personal_response(action, websocket)
