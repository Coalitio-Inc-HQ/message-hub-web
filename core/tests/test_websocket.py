from core.tests import *


def test_front_websocket_waiting_chats_by_user():
    client = TestClient(app)
    with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
        send_action = ActionDTO(name="get_waiting_chats", body={"count": 1})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


def test_front_websocket_get_chats_by_user():
    client = TestClient(app)
    with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
        send_action = ActionDTO(name="get_chats_by_user", body={"user_id": 12})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


def test_front_websocket_get_messages_by_chat():
    client = TestClient(app)
    with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
        send_action = ActionDTO(name="get_messages_by_chat",
                                body={"chat_id": 1, 'count': 2, 'offset_message_id': -1})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


def test_front_websocket_send_message_to_chat():
    client = TestClient(app)
    with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
        send_action = ActionDTO(name="send_message_to_chat",
                                body={
                                    "message":
                                        {"id": 0,
                                         "chat_id": 1,
                                         "sender_id": 1,
                                         "sended_at": "2024-06-26T06:37:17.454Z",
                                         "text": "test_string"}
                                })
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


test_front_websocket_waiting_chats_by_user()
