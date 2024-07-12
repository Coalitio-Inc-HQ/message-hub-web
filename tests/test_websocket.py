from fastapi.testclient import TestClient

from fastapi_app.app import app

from core import app_config, ActionDTO

from httpx import AsyncClient


async def test_front_websocket_get_user_info(ac: AsyncClient):
    await ac.post("/auth/register", json={"name": "test", "email": "tes1t@test.py","password":"1234567890"})
    response = await ac.post("/auth/jwt/login", data={"username": "test1@test.py","password":"1234567890"})
    client = TestClient(app, cookies={"fastapiusersauth":response.cookies.get("fastapiusersauth")})
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
        send_action = ActionDTO(name="get_user_info", body={})
        print(send_action.dict())
        websocket.send_json(send_action.dict())
        print(send_action.dict())
        data = websocket.receive_json()
        print(data)


async def test_front_websocket_waiting_chats_by_user(ac: AsyncClient):
    await ac.post("/auth/register", json={"name": "test", "email": "test@test.py","password":"1234567890"})
    response = await ac.post("/auth/jwt/login", data={"username": "test@test.py","password":"1234567890"})
    client = TestClient(app, cookies={"fastapiusersauth":response.cookies.get("fastapiusersauth")})
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
        send_action = ActionDTO(name="get_waiting_chats", body={"count": 12})
        print(send_action.dict())
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


async def test_front_websocket_get_chats_by_user(ac: AsyncClient):
    response = await ac.post("/auth/jwt/login", data={"username": "test@test.py", "password": "1234567890"})
    client = TestClient(app, cookies={"fastapiusersauth": response.cookies.get("fastapiusersauth")})
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
        send_action = ActionDTO(name="get_chats_by_user", body={})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


async def test_front_websocket_get_users_by_chat(ac: AsyncClient):
    response = await ac.post("/auth/jwt/login", data={"username": "test@test.py", "password": "1234567890"})
    client = TestClient(app, cookies={"fastapiusersauth": response.cookies.get("fastapiusersauth")})
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
        send_action = ActionDTO(name="get_users_by_chat", body={"chat_id":1})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


async def test_front_websocket_get_messages_by_chat(ac: AsyncClient):
    response = await ac.post("/auth/jwt/login", data={"username": "test@test.py", "password": "1234567890"})
    client = TestClient(app, cookies={"fastapiusersauth": response.cookies.get("fastapiusersauth")})
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
        send_action = ActionDTO(name="get_messages_by_chat",
                                body={"chat_id": 1, 'count': 2, 'offset_message_id': -1})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


async def test_front_websocket_get_messages_by_waiting_chat(ac: AsyncClient):
    response = await ac.post("/auth/jwt/login", data={"username": "test@test.py", "password": "1234567890"})
    client = TestClient(app, cookies={"fastapiusersauth": response.cookies.get("fastapiusersauth")})
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
        send_action = ActionDTO(name="get_messages_by_waiting_chat",
                                body={"chat_id": 1, 'count': 2, 'offset_message_id': -1})
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)


async def test_front_websocket_send_message_to_chat(ac: AsyncClient):
    response = await ac.post("/auth/jwt/login", data={"username": "test@test.py", "password": "1234567890"})
    client = TestClient(app, cookies={"fastapiusersauth": response.cookies.get("fastapiusersauth")})
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
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


def test_front_websocket_connect_to_waiting_chat():
    client = TestClient(app)
    with client.websocket_connect(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}") as websocket:
        send_action = ActionDTO(name="read_chat_by_user",
                                body={
                                    "chat_id": 1
                                })
        websocket.send_json(send_action.dict())
        data = websocket.receive_json()
        print(data)
