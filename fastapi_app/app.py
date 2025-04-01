from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from fastapi_app.main_client.main_client_requests import internal_router, register_platform
from fastapi_app.main_client.main_client_responses import webhooks_router
from core import logger, app_config, ActionResponseDTO, ResponseDTO, PlatformRegistrationException, ErrorDTO, action_dto_map
from fastapi_app.websocket_manager import websocket_manager
from fastapi_app.front_client.front_client_websocket_responses import get_websocket_response_actions
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends

from database.database_schemes import *
from fastapi_app.auth.auth_schemes import *
from fastapi_app.auth.auth import router as auth_router
from fastapi_app.auth.utilities import chek_jwt_and_get_user

from fastapi_app.auth.websocket_auth import websocket_auth_active, websocket_auth_base
from fastapi_app.auth.http_auth import http_auth_active

from database.database_engine import get_session, AsyncSession
from database.create_db import init_models
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from core.config_reader import config

from httpx import AsyncClient

import uuid

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not config.API_KEY: app.include_router(internal_router)

    app.include_router(webhooks_router, tags=["webhook"])

    app.include_router(
        auth_router,
        prefix="/auth",
        tags=["auth"],
    )

    try:
        await init_models()
        logger.debug("База данных готова")
        await register_platform()
        logger.debug("Регистрация платформы прошла успешно")
    except PlatformRegistrationException as e:
        logger.error(e)
    logger.debug("Приложение успешно запущено")
    yield
    logger.debug("Приложение успешно остановлено")

if not config.API_KEY:
    app = FastAPI(lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=RedirectResponse)
async def redirect():
    return f"/docs"


@app.websocket(f"{app_config.INTERNAL_WS_LISTENER_PREFIX}")
async def websocket_endpoint(websocket: WebSocket, db_session: AsyncSession=Depends(get_session)):
    """
    :param user:
    :param websocket: Websocket
    :return:
    """
    try:
        # Открытие вебсокета
        await websocket.accept()

        # Получаем карту методов для ответов фронту
        response_actions_map = get_websocket_response_actions()

        # Временное хранилище
        connetcion_data = {
            "user": None, # id пользователя
        }

        while True:
            try:
                # Получаем данные от фронта
                data = await websocket.receive_json()

                if data["type"] in action_dto_map:
                    action = action_dto_map[data["type"]](data)

                    if action.type == "Request":
                        if "token" in data:

                            try:
                                user = await chek_jwt_and_get_user(data["token"], db_session)

                                if user:
                                    if not connetcion_data["user"]:
                                        connetcion_data["user"] = user.id
                                        await websocket_manager.connect(websocket, user.id)

                                    if action.obj.name in response_actions_map:
                                        await response_actions_map[action.obj.name](action, websocket, user)
                                    else:
                                        await websocket_manager.send_personal_response(
                                                    ActionResponseDTO(
                                                        id=action.id,
                                                        obj=ResponseDTO(
                                                            name=action.obj.name,
                                                            status_code=422,
                                                            body={},
                                                            error={"description": "Метод не существует"}
                                                        )
                                                    ), websocket)    

                                else:
                                    await websocket_manager.send_personal_response(
                                                    ActionResponseDTO(
                                                        id=action.id,
                                                        obj=ResponseDTO(
                                                            name=action.obj.name,
                                                            status_code=401,
                                                            body={},
                                                            error={"description": "Пользователя не существует"}
                                                        )
                                                    ), websocket)                                   

                            except Exception as err:
                                await websocket_manager.send_personal_response(
                                                    ActionResponseDTO(
                                                        id=action.id,
                                                        obj=ResponseDTO(
                                                            name=action.obj.name,
                                                            status_code=401,
                                                            body={},
                                                            error={"description": "Токен невалиден"}
                                                        )
                                                    ), websocket)        
                        else:
                            await websocket_manager.send_personal_response(
                                                                            ActionResponseDTO(
                                                                                id=action.id,
                                                                                obj=ResponseDTO(
                                                                                    name=action.obj.name,
                                                                                    status_code=401,
                                                                                    body={},
                                                                                    error={"description": "Токен отсутсвует"}
                                                                                )
                                                                            ), websocket)
                else:
                    pass
            # except ValidationError:
            #     action = ActionResponseDTO(
            #         id=uuid.uuid4(),
            #         name="undefined",
            #         obj=
            #         body={},
            #         status_code=422,
            #         error=ErrorDTO(error_type="client", error_description="Ошибка чтения запроса")
            #     )
            #     await websocket_manager.send_personal_response(action, websocket)
            except WebSocketDisconnect as e:
                raise e
            except RuntimeError as e:
                logger.error("RuntimeError: ", e)
                raise e
            except Exception as e:
                logger.error("Unknown error: ", e)
    except WebSocketDisconnect:
        if connetcion_data["user"]:
            websocket_manager.disconnect(websocket, user.id)
    except Exception:
        if connetcion_data["user"]:
            websocket_manager.disconnect(websocket, user.id)


@app.post(app_config.INTERNAL_UPLOAD_FILE_PREFIX)
async def upload_file_to_s3(file: UploadFile = File(...), user: ExtUserDTO = Depends(http_auth_active)):
    try:
        # Чтение содержимого файла
        file_content = await file.read()

        file_name = str(uuid.uuid4())+"."+file.filename.split(".")[-1]

        async with AsyncClient() as client:
            response = await client.put(url=config.S3_BUCKET_URL+"/"+config.S3_BUCKET_NAME+"/"+file_name,data=file_content)
            response.raise_for_status()


        return {"url": config.S3_BUCKET_URL+"/"+config.S3_BUCKET_NAME+"/"+file_name}
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found")
    except PartialCredentialsError:
        raise HTTPException(status_code=500, detail="Incomplete AWS credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")