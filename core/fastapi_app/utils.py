import logging

import datetime

from pydantic import BaseModel, ValidationError
from starlette.websockets import WebSocket

from core import WrongBodyFormatException

from core.fastapi_app.auth.database import User

from core import ActionDTOOut, ErrorDTO

from httpx import HTTPStatusError

from core.fastapi_app.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


def get_list_of_pydantic_objects(base_model: BaseModel, list_of_elements: list) -> list[BaseModel]:
    try:
        return [base_model.model_validate(chat) for chat in list_of_elements]
    except ValidationError as e:
        logger.error("Ошибка при преобразовании списка элементов в pydantic модель")
        return []


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


def get_json_string_of_an_array(list_of_objects: list) -> str:
    return f'{[item.model_dump() for item in list_of_objects]}'


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
            except:
                action = ActionDTOOut(
                    name=name,
                    body={},
                    status_code=500,
                    error=ErrorDTO(error_type="server", error_description="Неизвестная ошибка")
                )
                await websocket_manager.send_personal_response(action, websocket)

        return inner

    return wrapper
