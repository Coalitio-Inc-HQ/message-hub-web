from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import ValidationError

from core.fastapi_app.main_client.main_client_requests import internal_router, register_platform
from core.fastapi_app.main_client.main_client_responses import external_receive_notification_router
from core.fastapi_app.main_client.main_client_responses import external_receive_messages_router
from core import logger, app_config, ActionDTO, PlatformRegistrationException
from core.fastapi_app.websocket_manager import websocket_manager
from core.fastapi_app.front_client.front_client_websocket_responses import get_websocket_response_actions


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(internal_router)
    app.include_router(external_receive_notification_router)
    app.include_router(external_receive_messages_router)
    try:
        await register_platform()
        logger.info("Регистрация платформы прошла успешно")
    except PlatformRegistrationException as e:
        logger.error(e)
    logger.info("Приложение успешно запущено")
    yield
    logger.info("Приложение успешно остановлено")


app = FastAPI(lifespan=lifespan)
@app.websocket(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}")
async def websocket_endpoint(websocket: WebSocket):  # в будущем авторизация по токену
    """
    :param websocket: Websocket
    :return:
    """
    await websocket_manager.connect(websocket)
    try:

        # Получаем карту методов для ответов фронту
        response_actions_map = get_websocket_response_actions()

        while True:
            # Получаем данные от фронта в формате ActionDTO
            data = await websocket.receive_json()
            try:
                action = ActionDTO(**data)
                if response_actions_map.__contains__(action.name):
                    await response_actions_map[action.name](action.body, websocket)
                else:
                    raise HTTPException(status_code=400,
                                        detail=f'Неверный заголовок запроса')
            except ValidationError:
                raise HTTPException(status_code=400,
                                    detail=f'Неверный формат запроса')
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run('app:app', host="localhost", port=8000, reload=True)
