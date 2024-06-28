import logging

from fastapi import APIRouter

from core import app_config, MessageDTO, ChatDTO
from core.fastapi_app.front_client.front_client_websocket_requests import trigger_front_new_message_in_chat, \
    trigger_front_new_user_in_chat, trigger_front_new_waiting_chat

external_receive_messages_router = APIRouter(prefix=app_config.INTERNAL_GET_MESSAGE_PREFIX)
external_receive_notification_router = APIRouter(prefix=app_config.INTERNAL_GET_NOTIFICATION_PREFIX)

logger = logging.getLogger(__name__)


@external_receive_messages_router.post("")
async def receive_new_message_from_main(message: MessageDTO):
    await trigger_front_new_message_in_chat(message)
    return {"ok": True}


@external_receive_notification_router.post("/new_waiting_chat")
async def receive_new_waiting_chat_from_main(chat: ChatDTO):
    await trigger_front_new_waiting_chat(chat)
    return {"ok": True}


@external_receive_notification_router.post("/new_user_in_chat")
async def receive_new_user_in_chat_from_main(chat: ChatDTO, user_id: int):
    await trigger_front_new_user_in_chat(chat, user_id)
    return {"ok": True}
