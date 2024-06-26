from fastapi import APIRouter
from httpx import AsyncClient
from pydantic import ValidationError

from core import app_config, ChatDTO, WrongResponseFormatFromMainException, MessageDTO

router = APIRouter(prefix=app_config.ROUTER_PREFIX)


# @router.get("/get_waiting_chats")
async def get_waiting_chats(count: int = 50) -> list[ChatDTO]:
    print(app_config.COPPER_MAIN_URL + "/message_service/get_list_of_waiting_chats")
    async with AsyncClient(base_url=app_config.COPPER_MAIN_URL) as client:
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


# @router.get("/get_chats_by_user")
async def get_chats_by_user(user_id: int) -> list[ChatDTO]:
    async with AsyncClient(base_url=app_config.COPPER_MAIN_URL) as client:
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


@router.post("/get_messages_by_chat")
async def get_messages_by_chat(chat_id: int, count: int | None = 50, offset_message_id: int | None = -1) -> list[
    MessageDTO]:
    async with AsyncClient(base_url=app_config.COPPER_MAIN_URL) as client:
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


@router.post("/send_a_message_to_chat")
async def send_a_message_to_chat(message: MessageDTO):
    async with AsyncClient(base_url=app_config.COPPER_MAIN_URL) as client:
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
