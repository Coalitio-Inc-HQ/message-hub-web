from starlette.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from fastapi import HTTPException

from core.fastapi_app.main_client_requests import get_waiting_chats
from core.fastapi_app.main_client_requests import get_chats_by_user
from core.fastapi_app.main_client_requests import get_messages_by_chat
from core.fastapi_app.main_client_requests import send_a_message_to_chat

from core.fastapi_app.app import app
from core import websocket_manager
from core import app_config
from core import ActionDTO, MessageDTO, ActionsMapTypedDict
from core import WrongBodyFormatException


@app.websocket(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}")
async def websocket_endpoint(websocket: WebSocket):  # в будущем авторизация по токену
    """
    :param websocket: Websocket
    :return:
    """
    await websocket_manager.connect(websocket)
    try:
        actions_map = get_websocket_actions()
        while True:
            # Получаем данные от фронта в формате ActionDTO
            data = await websocket.receive_json()
            action = ActionDTO.model_validate(data)

            if actions_map.__contains__(action.name):
                await actions_map[action.name](action.body, websocket)
            else:
                raise HTTPException(status_code=400,
                                    detail=f'Неверный заголовок запроса')
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


def get_websocket_actions() -> ActionsMapTypedDict:
    return ActionsMapTypedDict(
        get_waiting_chats=answer_front_waiting_chats,
        get_chats_by_user=answer_front_chats_by_user,
        get_messages_by_chat=answer_front_messages_from_chat,
        send_message_to_chat=process_front_message_to_chat
        # будут ещё
    )


def check_body_format(keys: list[str]):
    def wrapper(func):
        def inner(body: dict, websocket: WebSocket | None):
            if not all(key in body.keys() for key in keys):
                raise WrongBodyFormatException(
                    f"Неверный формат body в запросе. Не достает одного из ключей: {','.join(keys)}")
            result = func(body, websocket)
            return result

        return inner

    return wrapper


def get_json_string_of_an_array(list_of_objects: list) -> str:
    return f'{[item.model_dump() for item in list_of_objects]}'


@check_body_format(['count'])
async def answer_front_waiting_chats(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении ожидающих чатов от фронта

    :param body: Dict[count: int]
    :param websocket:
    :return:
    """
    count = body.get('count')
    try:
        chats = await get_waiting_chats(
            int(count)
        )  # Получаем ChatDTO с главного сервера, который мы потом отправим во фронт
    except ValueError:
        raise WrongBodyFormatException("Неверный формат данных в Body")

    await websocket.send_json(
        ActionDTO(name="get_waiting_chats", body={"chats": get_json_string_of_an_array(chats)}).model_dump()
    )


@check_body_format(['user_id'])
async def answer_front_chats_by_user(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении чатов пользователя от фронта.

    "TODO: убери дублирование кода, связанное со схожестью первых двух методов"
    :param body: Dict[user_id: int]
    :param websocket:
    :return:
    """
    user_id = body.get('user_id')  # Получаем user_id от фронта
    chats = await get_chats_by_user(user_id)

    await websocket.send_json(
        ActionDTO(name="get_chats_by_user", body={"chats": get_json_string_of_an_array(chats)}).model_dump()
    )


@check_body_format(['chat_id', 'count'])
async def answer_front_messages_from_chat(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении сообщений в чате от фронта.

    :param body: Dict[chat_id: int, count: int = 50, offset_message_id: int = -1]
    :param websocket:
    :return:
    """
    chat_id = body.get('chat_id')
    count = body.get('count')
    offset_message_id = body.get('offset_message_id')
    messages = await get_messages_by_chat(chat_id, count, offset_message_id)

    await websocket.send_json(
        ActionDTO(name="get_messages_by_chat", body={"messages": get_json_string_of_an_array(messages)})
        .model_dump()
    )


@check_body_format(['message'])
async def process_front_message_to_chat(body: dict, websocket: WebSocket | None):
    """
    Обработчик отправки сообщения в чат из фронта

    :param body: Dict[message: Message]
    :param websocket:
    :return:
    """
    message = body.get('message')
    print(message)
    message = MessageDTO(**message)
    await send_a_message_to_chat(message)
    await websocket.send_json({"status": 'ok'})
