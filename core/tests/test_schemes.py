from json import dumps

from core.tests import *
from core.fastapi_app.front_client import TestData

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
    chats = TestData().test_chats
    print([chat.model_dump() for chat in chats])



if __name__ == '__main__':
    # test_calling_from_base_model(ActionDTO(name='get_waiting_chats', body={"test": "test"}))
    test_chats_list()