from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
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
from fastapi_app.auth.http_auth import http_auth_active

from database.create_db import init_models
from core.s3 import s3_client
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from core.config_reader import config

from httpx import AsyncClient

import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not config.API_KEY: app.include_router(internal_router)
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
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(websocket_auth_active)):
    """
    :param user:
    :param websocket: Websocket
    :return:
    """
    try:
        await websocket_manager.connect(websocket, user.id)
        # Получаем карту методов для ответов фронту
        response_actions_map = get_websocket_response_actions()

        # websocket.state
        while True:
            try:
                # Получаем данные от фронта в формате ActionDTO
                data = await websocket.receive_json()
                print(data)
                action = ActionDTO(**data)
                if response_actions_map.__contains__(action.name):
                    await response_actions_map[action.name](action.id, action.body, websocket, user)
                else:
                    err_action = ActionDTOOut(
                        id=action.id,
                        name=action.name,
                        body={},
                        status_code=422,
                        error=ErrorDTO(error_type="client", error_description=f"Запроса {action.name} не существует")
                    )
                    await websocket_manager.send_personal_response(err_action, websocket)
            except ValidationError:
                action = ActionDTOOut(
                    id=uuid.uuid4(),
                    name="undefined",
                    body={},
                    status_code=422,
                    error=ErrorDTO(error_type="client", error_description="Ошибка чтения запроса")
                )
                await websocket_manager.send_personal_response(action, websocket)
            except WebSocketDisconnect as e:
                raise e
            except RuntimeError as e:
                logger.error("RuntimeError: ", e)
                raise e
            except Exception as e:
                logger.error("Unknown error: ", e)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user.id)
    except Exception:
        websocket_manager.disconnect(websocket, user.id)


@app.post(app_config.INTERNAL_UPLOAD_FILE_PREFIX)
async def upload_file_to_s3(file: UploadFile = File(...), user: User = Depends(http_auth_active)):
    try:
        # Чтение содержимого файла
        file_content = await file.read()

        file_name = str(uuid.uuid4())+"."+file.filename.split(".")[-1]

        # # Загружаем файл в S3
        # s3_client.put_object(
        #     Bucket=config.S3_BUCKET_NAME,
        #     Key=file_name,  # Используем имя файла
        #     Body=file_content,
        #     ContentType=file.content_type
        # )

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