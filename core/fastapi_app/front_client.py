import asyncio

from starlette.websockets import WebSocket

from core import *


class TestData:
    def __init__(self):
        self.test_chats = [
            ChatDTO(id=1, name="1"),
            ChatDTO(id=2, name="2"),
            ChatDTO(id=3, name="3"),
            ChatDTO(id=4, name="4")
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
async def send_front_waiting_chats_by_user(body: dict, websocket: WebSocket | None):
    """
    Ответ на запрос о получении ожидающих чатов от фронта
    :param body: Dict[user_id: int]
    :param websocket:
    :return:
    """
    user_id = body.get('user_id')  # Получаем user_id от фронта
    chats = ChatDTO  # Получаем ChatDTO с главного сервера, который мы потом отправим во фронт

    ...  # здесь логика общения с copper main

    "Ниже код для тестирования"
    chats = TestData().test_chats

    await websocket.send_json(
        ActionDTO(name="get_waiting_chats", body={"chats": get_json_string_of_an_array(chats)}).model_dump()
    )


@check_body_format(keys=['chats'])
async def send_waiting_chats_to_front(body: dict, websocket: WebSocket | None):
    """
    :param body: Dict[chats: ChatDTO]
    :param websocket: WebSocket
    :return:
    """
    try:
        chats = body.get('chats')
        # await websocket.send_json(ActionDTO(name="get_waiting_chats", body={"chats": chats}))
        ...
    except Exception as e:
        print(e)


@check_body_format(keys=[''])
async def send_chats_by_user_to_front(body: dict, websocket: WebSocket | None):
    ...


if __name__ == "__main__":
    asyncio.run(send_waiting_chats_to_front({"chats": 1}, None))
