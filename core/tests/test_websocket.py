from core.tests import *


def test_front_websocket_get_waiting_chats():
    client = TestClient(app)
    with client.websocket_connect(f"{app_config.WS_LISTENER_URL}") as websocket:
        send_action = ActionDTO(name="get_waiting_chats", body={"user_id": 12})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


if __name__ == "__main__":
    test_front_websocket_get_waiting_chats()
