import logging

from httpx import AsyncClient
from pydantic import ValidationError

from fastapi import APIRouter

from core import app_config
from core import ChatDTO, MessageDTO
from core import WrongResponseFormatFromMainException, MainServerWrongUrlException, MainServerWrongJsonFormat

from core.fastapi_app.utils import get_list_of_pydantic_objects

internal_router = APIRouter(prefix=app_config.INTERNAL_ROUTER_PREFIX)

logger = logging.getLogger(__name__)


@internal_router.post("/register_platform")
async def register_platform(url: str = app_config.FULL_WEBHOOK_URL):
    """
    Регистрация платформы на главном сервере

    :param url: str
    :return:
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        response = await client.post("/message_service/platform_registration/web",
                                     json={
                                         "platform_name": "web",
                                         "url": url
                                     })
        if response.status_code == 404:
            raise MainServerWrongUrlException("Неверный url главного сервера")
        elif response.status_code == 422:
            raise MainServerWrongJsonFormat("Неверный запрос на регистрацию платформы")


@internal_router.post("/get_waiting_chats", response_model=list[ChatDTO])
async def get_waiting_chats(count: int = 50) -> list[ChatDTO]:
    """
    Получает ожидающие чаты с главного сервера

    :param count: int
    :return: list[ChatDTO]
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_list_of_waiting_chats",
                                         json=count)
            response.raise_for_status()
            print(response)
            try:
                # return [ChatDTO.model_validate(chat) for chat in response.json()]
                return get_list_of_pydantic_objects(ChatDTO, response.json())
            except ValidationError:
                raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except Exception as e:
            print(f"Error: {e}")


@internal_router.post("/get_chats_by_user", response_model=list[ChatDTO])
async def get_chats_by_user(user_id: int) -> list[ChatDTO]:
    """
    Получает чаты пользователя с главного сервера

    :param user_id: int
    :return: list[ChatDTO]
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_chats_by_user",
                                         json=user_id)
            response.raise_for_status()
            try:
                # return [ChatDTO.model_validate(chat) for chat in response.json()]
                return get_list_of_pydantic_objects(ChatDTO, response.json())
            except ValidationError:
                raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except Exception as e:
            print(f"Error: {e}")


@internal_router.post("/get_messages_by_chat", response_model=list[MessageDTO])
async def get_messages_by_chat(
        chat_id: int,
        count: int = 50,
        offset_message_id: int = -1) -> list[MessageDTO]:
    """
    Получает сообщения из чата с главного сервера

    :param chat_id: int
    :param count: int
    :param offset_message_id: int
    :return: list[MessageDTO]
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_messages_from_chat",
                                         json={
                                             'chat_id': chat_id,
                                             'count': count,
                                             'offset_message_id': offset_message_id
                                         })
            response.raise_for_status()
            print(response)
            try:
                # return [MessageDTO.model_validate(message) for message in response.json()]
                return get_list_of_pydantic_objects(MessageDTO, response.json())
            except ValidationError:
                raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except Exception as e:
            logger.error(f"Error: {e}")


@internal_router.post("/send_a_message_to_chat")
async def send_a_message_to_chat(message: MessageDTO):
    """
    Отправляет сообщение на главный сервер

    :param message: MessageDTO
    :return: None
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post(
                url="/message_service/send_a_message_to_chat",
                json=message.model_dump(),
                timeout=3000
            )
            return response.json()
        except Exception as e:
            logger.error(e)
