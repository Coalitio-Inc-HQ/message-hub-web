from starlette.websockets import WebSocket

from core import *


class TestData:
    def __init__(self):
        self.test_waiting_chats = [
            ChatDTO(id=1, name="1"),
            ChatDTO(id=2, name="2"),
            ChatDTO(id=3, name="3"),
            ChatDTO(id=4, name="4")
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


@check_body_format(['user_id'])
async def answer_front_waiting_chats_by_user(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении ожидающих чатов от фронта
    :param body: Dict[user_id: int]
    :param websocket:
    :return:
    """
    user_id = body.get('user_id')  # Получаем user_id от фронта
    chats = ChatDTO  # Получаем ChatDTO с главного сервера, который мы потом отправим во фронт

    ...  # здесь логика общения с copper main, получаем ОЖИДАЮЩИЕ ЧАТЫ

    "Ниже код для тестирования"
    chats = TestData().test_waiting_chats

    await websocket.send_json(
        ActionDTO(name="get_waiting_chats", body={"chats": get_json_string_of_an_array(chats)}).model_dump()
    )


@check_body_format(['user_id'])
async def answer_front_chats_by_user(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении чатов пользователя от фронта.

    "TODO: убери дублирование кода, связанное со схожестью первых двух методов"
    :param body: Dict[]
    :param websocket:
    :return:
    """
    user_id = body.get('user_id')  # Получаем user_id от фронта
    chats = ChatDTO  # Получаем ChatDTO с главного сервера, который мы потом отправим во фронт

    ...  # здесь логика общения с copper main, получаем ОЖИДАЮЩИЕ ЧАТЫ

    "Ниже код для тестирования"
    chats = TestData().test_user_chats

    await websocket.send_json(
        ActionDTO(name="get_chats_by_user", body={"chats": get_json_string_of_an_array(chats)}).model_dump()
    )
