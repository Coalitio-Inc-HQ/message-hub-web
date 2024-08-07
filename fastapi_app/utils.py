import logging

from pydantic import BaseModel, ValidationError
from starlette.websockets import WebSocket

from core import WrongBodyFormatException

from database.database_schemes import User

from core import ActionDTOOut, ErrorDTO

from httpx import HTTPStatusError

from fastapi_app.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


def check_body_format(keys: list[str]):
    def wrapper(func):
        def inner(body: dict, websocket: WebSocket | None, user: User):
            if not all(key in body.keys() for key in keys):
                raise WrongBodyFormatException(
                    f"Неверный формат body в запросе. Не достает одного из ключей: {','.join(keys)}")
            result = func(body, websocket, user)
            return result

        return inner

    return wrapper


def error_catcher(name: str):
    def wrapper(func):
        async def inner(body: dict, websocket: WebSocket | None, user: User):
            try:
                result = await func(body, websocket, user)
                return result
            except ValueError:
                action = ActionDTOOut(
                    name=name,
                    body={},
                    status_code=500,
                    error=ErrorDTO(error_type="server", error_description="Неверный формат ответа главного сервера")
                )
                await websocket_manager.send_personal_response(action, websocket)
            except HTTPStatusError as err:
                if 400 <= err.response.status_code < 500:
                    action = ActionDTOOut(
                        name=name,
                        body={},
                        status_code=422,
                        error=ErrorDTO(error_type="client", error_description=err.response.text)
                    )
                    await websocket_manager.send_personal_response(action, websocket)
                else:
                    action = ActionDTOOut(
                        name=name,
                        body={},
                        status_code=500,
                        error=ErrorDTO(error_type="server", error_description="Неизвестная ошибка")
                    )
                    await websocket_manager.send_personal_response(action, websocket)
            except WrongBodyFormatException as err:
                action = ActionDTOOut(
                    name=name,
                    body={},
                    status_code=422,
                    error=ErrorDTO(error_type="client", error_description=str(err))
                )
                await websocket_manager.send_personal_response(action, websocket)
            except Exception as e:
                action = ActionDTOOut(
                    name=name,
                    body={},
                    status_code=500,
                    error=ErrorDTO(error_type="server", error_description="Неизвестная ошибка")
                )
                logger.error("Unknown error: ", e, "body", body)
                await websocket_manager.send_personal_response(action, websocket)

        return inner

    return wrapper
