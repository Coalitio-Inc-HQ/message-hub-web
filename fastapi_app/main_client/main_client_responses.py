import logging

from fastapi import APIRouter, Depends

from core import app_config, MessageDTO, ChatDTO, UserDTO, Event
from fastapi_app.front_client.front_client_websocket_requests import trigger_front_new_message_in_chat, \
    trigger_front_new_user_in_chat, trigger_front_new_chat, trigger_front_new_message_in_chat_personal

from  fastapi_app.front_client.front_client_websocket_requests import get_websocket_event_handlers

webhooks_router = APIRouter(prefix=app_config.INTERNAL_GET_MESSAGE_PREFIX)

from core.auth import verify_api_key

logger = logging.getLogger(__name__)


# @webhooks_router.post("/send_message")
# async def receive_new_message_from_main(message: MessageDTO):
#     await trigger_front_new_message_in_chat(message)
#     return {"ok": True}


# @webhooks_router.post("/notification_added_chat")
# async def receive_new_waiting_chat_from_main(chat: ChatDTO):
#     await trigger_front_new_chat(chat)
#     return {"ok": True}


# @webhooks_router.post("/notification_user_added_to_chat")
# async def receive_new_user_in_chat_from_main(chat: ChatDTO, user: UserDTO):
#     await trigger_front_new_user_in_chat(chat, user)
#     return {"ok": True}


# @webhooks_router.post("/send_personal_message")
# async def receive_new_message_from_main_personal(message: MessageDTO):
#     await trigger_front_new_message_in_chat_personal(message)
#     return {"ok": True}


@webhooks_router.post("/event")
async def receive_event(event: Event, api_key: str = Depends(verify_api_key)):
    await get_websocket_event_handlers()[event.name](event)
    return {"ok": True}


