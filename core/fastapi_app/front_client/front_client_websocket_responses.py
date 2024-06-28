import logging

from starlette.websockets import WebSocket

from core.fastapi_app.main_client.main_client_requests import get_waiting_chats
from core.fastapi_app.main_client.main_client_requests import get_chats_by_user
from core.fastapi_app.main_client.main_client_requests import get_messages_by_chat
from core.fastapi_app.main_client.main_client_requests import send_a_message_to_chat
from core.fastapi_app.utils import check_body_format
from core.fastapi_app.utils import get_json_string_of_an_array

from core.fastapi_app.websocket_connection import websocket_manager

from core import ActionDTO, MessageDTO, ActionsMapTypedDict
from core import WrongBodyFormatException

logger = logging.getLogger(__name__)


def get_websocket_response_actions() -> ActionsMapTypedDict:
    return ActionsMapTypedDict(
        get_waiting_chats=answer_front_waiting_chats,
        get_chats_by_user=answer_front_chats_by_user,
        get_messages_by_chat=answer_front_messages_from_chat,
        send_message_to_chat=process_front_message_to_chat
        # будут ещё
    )


@check_body_format(['count'])
async def answer_front_waiting_chats(body: dict, websocket: WebSocket | None):
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
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format(['user_id'])
async def answer_front_chats_by_user(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении чатов пользователя от фронта.

    "TODO: убери дублирование кода, связанное со схожестью первых двух методов"
    :param body: Dict[user_id: int]
    :param websocket: Websocket
    :return:
    """
    user_id = body.get('user_id')  # Получаем user_id от фронта
    chats = await get_chats_by_user(user_id)

    action = ActionDTO(
        name="get_chats_by_user",
        body={
            "chats": get_json_string_of_an_array(chats)
        })
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format(['chat_id', 'count'])
async def answer_front_messages_from_chat(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении сообщений в чате от фронта.

    :param body: Dict[chat_id: int, count: int = 50, offset_message_id: int = -1]
    :param websocket: Websocket
    :return:
    """
    chat_id = body.get('chat_id')
    count = body.get('count')
    offset_message_id = body.get('offset_message_id')
    messages = await get_messages_by_chat(chat_id, count, offset_message_id)

    action = ActionDTO(
        name="get_messages_by_chat",
        body={
            "messages": get_json_string_of_an_array(messages)
        })
    await websocket_manager.send_personal_response(action, websocket)


@check_body_format(['message'])
async def process_front_message_to_chat(body: dict, websocket: WebSocket | None):
    """
    Обработчик отправки сообщения в чат из фронта

    :param body: Dict[message: Message]
    :param websocket: Websocket
    :return:
    """
    message = body.get('message')
    print(message)
    message = MessageDTO(**message)
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
    await websocket_manager.send_personal_response(action, websocket)
