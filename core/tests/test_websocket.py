import unittest

from core.tests import *


class WebsocketTest(unittest.TestCase):
    def test_front_websocket_get_waiting_chats(self):
        client = TestClient(app)
        with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
            send_action = ActionDTO(name="get_waiting_chats", body={"count": 1})
            websocket.send_json(send_action.dict())
            data = websocket.receive_json()
            print(data)

    def test_front_websocket_get_chats_by_user(self):
        client = TestClient(app)
        with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
            send_action = ActionDTO(name="get_chats_by_user", body={"user_id": 12})
            websocket.send_json(send_action.dict())
            data = websocket.receive_json()
            print(data)

    def test_front_websocket_get_messages_by_chat(self):
        client = TestClient(app)
        with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
            send_action = ActionDTO(name="get_messages_by_chat",
                                    body={"chat_id": 1, 'count': 2, 'offset_message_id': -1})
            websocket.send_json(send_action.dict())
            data = websocket.receive_json()
            print(data)

    def test_front_websocket_get_messages_by_chat(self):
        client = TestClient(app)
        with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
            send_action = ActionDTO(name="send_a_message_to_chat",
                                    body={
                                        "id": 0,
                                        "chat_id": 1,
                                        "sender_id": 1,
                                        "sended_at": "2024-06-26T06:37:17.454Z",
                                        "text": "test_string"
                                    })
            websocket.send_json(send_action.dict())
            data = websocket.receive_json()
            print(data)


if __name__ == "__main__":
    unittest.main()
