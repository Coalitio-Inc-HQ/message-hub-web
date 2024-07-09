import logging

from fastapi import APIRouter

from core import app_config, MessageDTO, ChatDTO,UserDTO
from core.fastapi_app.front_client.front_client_websocket_requests import trigger_front_new_message_in_chat, \
    trigger_front_new_user_in_chat, trigger_front_new_waiting_chat,trigger_front_new_broadcast_message_in_chat,\
    trigger_front_delete_waiting_chat

webhooks_router = APIRouter(prefix=app_config.INTERNAL_GET_MESSAGE_PREFIX)


logger = logging.getLogger(__name__)


@webhooks_router.post("/send_message")
async def receive_new_message_from_main(message: MessageDTO):
    await trigger_front_new_message_in_chat(message)
    return {"ok": True}


@webhooks_router.post("/send_message_broadcast")
async def receive_new_broadcast_message_from_main(message: MessageDTO):
    await trigger_front_new_broadcast_message_in_chat(message)
    return {"ok": True}


@webhooks_router.post("/notification_added_waiting_chat")
async def receive_new_waiting_chat_from_main(chat: ChatDTO):
    await trigger_front_new_waiting_chat(chat)
    return {"ok": True}


@webhooks_router.post("/notification_user_added_to_chat")
async def receive_new_user_in_chat_from_main(chat: ChatDTO, user: UserDTO):
    await trigger_front_new_user_in_chat(chat, user)
    return {"ok": True}


@webhooks_router.post("/notification_delited_waiting_chat")
async def receive_delite_waiting_chat_from_main(chat: ChatDTO):
    await trigger_front_delete_waiting_chat(chat)
    return {"ok": True}
