import datetime
from typing import Callable, TypedDict, List

from fastapi import WebSocket

from pydantic import BaseModel, Field
from typing import  Any

import uuid

user_id = int
chat_id = int
message_id = int
count = int
name = str
body = dict
websocket = WebSocket

class OutPlatformDTO(BaseModel):
    id: int
    platform_name: str = Field(max_length=30)


class ErrorDTO(BaseModel):
    """
    Сообщение об ошибке
    """
    error_type: str
    error_description: str


class ActionDTO(BaseModel):
    """
    Экземпляр действия, совершаемого при взаимодействии
    с приложением через вебсокет

    Формат: {name: str, {...тело}}
    """
    name: name
    body: dict
    id: uuid.UUID


class ActionDTOOut(ActionDTO):
    """
    Экземпляр действия, совершаемого при взаимодействии
    с приложением через вебсокет

    Формат: {name: str, {...тело}}
    """
    status_code: int
    error: ErrorDTO | None


class ChatDTO(BaseModel):
    """
    Экземпляр чата, пришедшего с главного сервера
    """
    id: chat_id
    name: str = Field(max_length=256)
    is_waiting_answer: bool
    is_archive: bool
    icon_url: str | None = Field(max_length=256)
    last_message_send_at: datetime.datetime| None = None
    platform_id: int|None = None


class ExtChatDTO(ChatDTO):
    last_read_message_id: int | None = None
    count_unredeble_messgaes: int | None = None
    user_in_chat: bool = False
    platform_name: str|None = None


class MessageDTO(BaseModel):
    """
    Экземпляр сообщения, в данном формате они хранятся
    на главном сервере
    """
    id: message_id
    chat_id: chat_id
    sender_id: user_id
    # sent_at: datetime.datetime | str
    sended_at: datetime.datetime | str
    text: str | None = None
    attachments: dict

class MessageDTOFront(MessageDTO):
    front_message_id:int

class UserDTO(BaseModel):
    id: user_id
    name: str
    icon_url: str | None = Field(max_length=256)


class ChatUsersDTO(BaseModel):
    user_id: int
    chat_id: int


class ActionsMapTypedDict(TypedDict):
    get_user_info: Callable[[], None] | None
    get_chats_in_which_user_is_not_member: Callable[[count], List[ChatDTO]] | None
    read_chat_by_user: Callable[[user_id, chat_id], ChatDTO] | None
    get_chats_by_user: Callable[[user_id], List[ChatDTO]] | None
    get_users_by_chat: Callable[[chat_id], List[UserDTO]] | None
    get_messages_by_chat: Callable[[chat_id, count], List[MessageDTO]] | None
    add_user_to_chat: Callable[[chat_id, user_id], ChatDTO] | None
    send_message_to_chat: Callable[[MessageDTO], None] | None


class UserInfoDTO(BaseModel):
    """
    Экземпляр информации о пользователе (в локальной бд)
    """
    name: str
    id: int
    is_completed_tutorial: bool

class Event(BaseModel):
    """
    Событие
    """
    name: str
    data: Any
    id: uuid.UUID