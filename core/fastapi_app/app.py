from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.websockets import WebSocketDisconnect, WebSocket

from pydantic import parse_obj_as

from core.fastapi_app.front_client import answer_front_waiting_chats_by_user

from core import *

actions_map = ActionsMapTypedDict(get_waiting_chats=answer_front_waiting_chats_by_user)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.websocket(f"{app_config.WS_LISTENER_URL}")
async def websocket_endpoint(websocket: WebSocket):  # в будущем авторизация по токену
    """
    :param websocket:
    :return:
    """
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Получаем данные от фронта в формате ActionDTO
            data = await websocket.receive_json()
            action = parse_obj_as(ActionDTO, data)
            if actions_map.__contains__(action.name):
                await actions_map[action.name](action.body, websocket)
            return
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('app:app', host="localhost", port=8000, reload=True)
