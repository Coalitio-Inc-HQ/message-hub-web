import logging

from httpx import AsyncClient, ConnectError, HTTPStatusError
from pydantic import ValidationError

from fastapi import APIRouter,HTTPException

from core import app_config
from core import ChatDTO, MessageDTO, UserDTO, ChatUsersDTO
from core import WrongResponseFormatFromMainException, MainServerWrongUrlException, MainServerWrongJsonFormat, \
    MainServerOfflineException

from fastapi_app.utils import get_list_of_pydantic_objects

internal_router = APIRouter(prefix=app_config.INTERNAL_ROUTER_PREFIX)

logger = logging.getLogger(__name__)


@internal_router.post("/register_platform")
async def register_platform(url: str = app_config.INTERNAL_BASE_DOMAIN):
    """
    Регистрация платформы на главном сервере

    :param url: str
    :return:
    """
    logger.info(app_config.EXTERNAL_MAIN_BASE_URL + "/message_service/platform_registration/web")
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/platform_registration/web",
                                         json={
                                             "platform_name": "web",
                                             "url": url
                                         })
            logger.info(response.text)
        except ConnectError:
            raise MainServerOfflineException("Главный сервер не в сети")
        if response.status_code == 404:
            raise MainServerWrongUrlException("Неверный url главного сервера")
        elif response.status_code == 422:
            raise MainServerWrongJsonFormat("Неверный запрос на регистрацию платформы")


@internal_router.post('/register_user')
async def register_user(name: str, platform_name: str = "web") -> dict:
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/user_registration/web",
                                         json={"platform_name": platform_name, "name": name})
            response.raise_for_status()
            return response.json()
        except HTTPException as e:
            logger.error(f"Error:{e}")
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Ошибка регистрации пользователя на основном сервере")


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

            return get_list_of_pydantic_objects(ChatDTO, response.json())
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e


@internal_router.post("/connect_to_waiting_chat")
async def connect_to_waiting_chat(user_id: int, chat_id: int):
    """
    Добавляет пользователя в ожидающий чат

    :param user_id: int
    :param chat_id: int
    :return:
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/connect_to_a_waiting_chat",
                                         json={
                                             'user_id': user_id,
                                             'chat_id': chat_id
                                         })
            logger.info(response.text)
        except Exception as e:
            logger.error(e)


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

            return get_list_of_pydantic_objects(ChatDTO, response.json())
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e


@internal_router.post("/get_users_by_chat", response_model=list[UserDTO])
async def get_users_by_chat(user_id: int, chat_id: int) -> list[UserDTO]:
    """
    Получает пользователей чата с главного сервера

    :param user_id: int
    :param chat_id: int
    :return: list[UserDTO]
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_users_by_chat_id",
                                         json={'user_id': user_id,
                                               'chat_id': chat_id
                                               })
            response.raise_for_status()

            return get_list_of_pydantic_objects(UserDTO, response.json())
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e


@internal_router.post("/get_messages_by_chat", response_model=list[MessageDTO])
async def get_messages_by_chat(
        user_id: int,
        chat_id: int,
        count: int = 50,
        offset_message_id: int = -1) -> list[MessageDTO]:
    """
    Получает сообщения из чата с главного сервера

    :param user_id: int
    :param chat_id: int
    :param count: int
    :param offset_message_id: int
    :return: list[MessageDTO]
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_messages_from_chat",
                                         json={
                                             'user_id': user_id,
                                             'chat_id': chat_id,
                                             'count': count,
                                             'offset_message_id': offset_message_id
                                         })
            response.raise_for_status()

            return get_list_of_pydantic_objects(MessageDTO, response.json())
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e


@internal_router.post("/get_messages_from_wating_chat", response_model=list[MessageDTO])
async def get_messages_by_waiting_chat(
        chat_id: int,
        count: int = 50,
        offset_message_id: int = -1) -> list[MessageDTO]:
    """
    Получает сообщения из ожидающего чата с главного сервера

    :param chat_id: int
    :param count: int
    :param offset_message_id: int
    :return: list[MessageDTO]
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_messages_from_wating_chat",
                                         json={
                                             'chat_id': chat_id,
                                             'count': count,
                                             'offset_message_id': offset_message_id
                                         })
            response.raise_for_status()

            return get_list_of_pydantic_objects(MessageDTO, response.json())
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e


@internal_router.post("/add_user_to_chat", response_model=ChatUsersDTO)
async def add_user_to_chat(chat_id: int, user_id: int) -> ChatUsersDTO:
    """
    Подключает пользователя к ожидающему чату

    :param user_id: int
    :param chat_id: int
    :return: ChatUsersDTO
    """
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/connect_user_to_chat",
                                         json={'user_id': user_id, 'chat_id': chat_id})
            response.raise_for_status()
            return ChatUsersDTO.model_validate(response.json())
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e


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
            response.raise_for_status()
            return response.json()
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except HTTPStatusError as e:
            print(f"http Error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e
