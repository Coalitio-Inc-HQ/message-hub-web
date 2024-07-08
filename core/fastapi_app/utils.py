import logging

from pydantic import BaseModel, ValidationError
from starlette.websockets import WebSocket

from core import WrongBodyFormatException

from core.fastapi_app.auth.database import User

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
            result = func(body, websocket,user)
            return result

        return inner

    return wrapper


def get_json_string_of_an_array(list_of_objects: list) -> str:
    return f'{[item.model_dump() for item in list_of_objects]}'
