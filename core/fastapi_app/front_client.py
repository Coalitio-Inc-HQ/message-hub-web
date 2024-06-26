from starlette.websockets import WebSocket

from core.fastapi_app.main_client import get_waiting_chats, get_chats_by_user, get_messages_by_chat, \
    send_a_message_to_chat

from core import ChatDTO, WrongBodyFormatException, ActionDTO, MessageDTO


class TestData:
    def __init__(self):
        self.test_waiting_chats = [
            ChatDTO(id=1, name="1"),
            ChatDTO(id=2, name="2"),
            ChatDTO(id=3, name="3"),
            ChatDTO(id=4, name="4")
        ]
        self.test_waiting_chats_dict = [
            chat.model_dump() for chat in self.test_waiting_chats
        ]
        self.wrong_type_test_waiting_chats_dict = [
            {'chat_id': 1, 'chat_name': '1'},
            {'chat_id': 2, 'chat_name': '2'},
            {'chat_id': 3, 'chat_name': '3'},
            {'chat_id': 4, 'chat_name': '4'}
        ]
        self.test_user_chats = [
            ChatDTO(id=55, name="fff"),
            ChatDTO(id=6, name="fgsdfg")
        ]


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


async def answer_front_waiting_chats_by_user(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении ожидающих чатов от фронта
    :param body: Dict[user_id: int]
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

    # "Ниже код для тестирования"
    # chats = TestData().test_waiting_chats

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

    # "Ниже код для тестирования"
    # chats = TestData().test_user_chats

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
    try:
        message = MessageDTO.model_dump(message)
        await send_a_message_to_chat(message)

        await websocket.send_json({"status": 'ok'})

    except AttributeError:
        raise WrongBodyFormatException('Неверный формат данных в Body')
