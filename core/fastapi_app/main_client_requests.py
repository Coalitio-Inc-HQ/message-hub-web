from httpx import AsyncClient
from pydantic import ValidationError

from fastapi import APIRouter

from core import app_config
from core import ChatDTO, MessageDTO
from core import WrongResponseFormatFromMainException

internal_router = APIRouter(prefix=app_config.INTERNAL_ROUTER_PREFIX)

@internal_router.post("/get_waiting_chats", response_model=list[ChatDTO])
async def get_waiting_chats(count: int = 50) -> list[ChatDTO]:
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_list_of_waiting_chats",
                                         json=count)
            response.raise_for_status()
            print(response)
            try:
                return [ChatDTO.model_validate(chat) for chat in response.json()]
            except ValidationError:
                raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except Exception as e:
            print(f"Error: {e}")


@internal_router.post("/get_chats_by_user", response_model=list[ChatDTO])
async def get_chats_by_user(user_id: int) -> list[ChatDTO]:
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        try:
            response = await client.post("/message_service/get_chats_by_user",
                                         json=user_id)
            response.raise_for_status()
            try:
                return [ChatDTO.model_validate(chat) for chat in response.json()]
            except ValidationError:
                raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except Exception as e:
            print(f"Error: {e}")


@internal_router.post("/get_messages_by_chat", response_model=list[MessageDTO])
async def get_messages_by_chat(chat_id: int, count: int | None = 50, offset_message_id: int | None = -1) -> list[
    MessageDTO]:
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
                return [MessageDTO.model_validate(message) for message in response.json()]
            except ValidationError:
                raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
        except Exception as e:
            print(f"Error: {e}")


@internal_router.post("/send_a_message_to_chat")
async def send_a_message_to_chat(message: MessageDTO):
    async with AsyncClient(base_url=app_config.EXTERNAL_MAIN_BASE_URL) as client:
        response = await client.post(
            url="/message_service/send_a_message_to_chat",
            json=message.model_dump(),
            timeout=3000
        )
        print(response.text)
        response.raise_for_status()
        print(response.json())
        try:
            return response.json()
        except ValidationError:
            raise WrongResponseFormatFromMainException("Пришел неверный формат данных с главного сервера")
