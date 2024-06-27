import asyncio

from pydantic import ValidationError

from core.tests import *
from core.fastapi_app.front_client import TestData
from core.fastapi_app.main_client import get_waiting_chats


def test_json_dumps():
    action = ActionDTO(name='123', body={"json": True})
    print(action.__dict__)
    assert action.model_dump_json() == '{"name":"123","body":{"json":true}}'


def test_calling_from_base_model(action: ActionDTO):
    def call():
        return 'ok'

    actions_map = ActionsMapTypedDict(get_waiting_chats=call)
    if actions_map.__contains__(action.name):
        assert actions_map[action.name]() == "ok"


def test_chats_list():
    chats = TestData().test_user_chats
    print([chat.model_validate(chat) for chat in chats])


async def test_get_waiting_chats() -> list[ChatDTO]:
    print(type(await get_waiting_chats()))
    # assert type(await get_waiting_chats()) is list[ChatDTO]
    print(TestData().test_waiting_chats_dict)
    print([ChatDTO.model_validate(chat) for chat in TestData().test_waiting_chats])
    try:
        assert print(
            [ChatDTO.model_validate(chat) for chat in TestData().wrong_type_test_waiting_chats_dict]) is ValidationError
    except ValidationError:
        print('ok')


def test_default_error():
    message = {'id': 0, 'chat_id': 1, 'sender_id': 1, 'sended_at': '2024-06-26T06:37:17.454Z', 'text': 'test_string'}
    print(MessageDTO(**message))

    from core.fastapi_app.app import actions_map
    print(actions_map.items())


if __name__ == '__main__':
    test_default_error()
    # test_default_error()
    # test_calling_from_base_model(ActionDTO(name='get_waiting_chats', body={"test": "test"}))
    # asyncio.run(test_get_waiting_chats())
