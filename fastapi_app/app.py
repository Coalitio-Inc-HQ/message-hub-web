from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from fastapi_app.main_client.main_client_requests import internal_router, register_platform
from fastapi_app.main_client.main_client_responses import webhooks_router
from core import logger, app_config, ActionDTO, PlatformRegistrationException, ActionDTOOut, ErrorDTO
from fastapi_app.websocket_manager import websocket_manager
from fastapi_app.front_client.front_client_websocket_responses import get_websocket_response_actions
from fastapi.middleware.cors import CORSMiddleware

from fastapi_users import FastAPIUsers

from fastapi import Depends

from database.database_schemes import User
from fastapi_app.auth.auth import auth_backend
from fastapi_app.auth.auth_schemes import UserRead, UserCreate
from fastapi_app.auth.user_manager import get_user_manager

from fastapi_app.auth.websocket_auth import websocket_auth_active

from database.create_db import init_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(internal_router)
    app.include_router(webhooks_router, tags=["webhook"])

    fastapi_users = FastAPIUsers[User, int](
        get_user_manager,
        [auth_backend],
    )

    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )

    try:
        await init_models()
        logger.info("База данных готова")
        await register_platform()
        logger.info("Регистрация платформы прошла успешно")
    except PlatformRegistrationException as e:
        logger.error(e)
    logger.info("Приложение успешно запущено")
    yield
    logger.info("Приложение успешно остановлено")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}")
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(websocket_auth_active)):
    """
    :param user:
    :param websocket: Websocket
    :return:
    """
    await websocket_manager.connect(websocket, user.id)
    try:
        # Получаем карту методов для ответов фронту
        response_actions_map = get_websocket_response_actions()

        while True:
            try:
                # Получаем данные от фронта в формате ActionDTO
                data = await websocket.receive_json()
                print(data)
                action = ActionDTO(**data)
                if response_actions_map.__contains__(action.name):
                    await response_actions_map[action.name](action.body, websocket, user)
                else:
                    err_action = ActionDTOOut(
                        name=action.name,
                        body={},
                        status_code=422,
                        error=ErrorDTO(error_type="client", error_description=f"Запроса {action.name} не существует")
                    )
                    await websocket_manager.send_personal_response(err_action, websocket)
            except ValidationError:
                action = ActionDTOOut(
                    name="undefined",
                    body={},
                    status_code=422,
                    error=ErrorDTO(error_type="client", error_description="Ошибка чтения запроса")
                )
                await websocket_manager.send_personal_response(action, websocket)
            except Exception:
                action = ActionDTOOut(
                    name="undefined",
                    body={},
                    status_code=500,
                    error=ErrorDTO(error_type="server", error_description="Внутренняя ошибка сервера")
                )
                await websocket_manager.send_personal_response(action, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user.id)
