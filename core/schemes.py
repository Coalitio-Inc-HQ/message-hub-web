import datetime
from typing import Callable, TypedDict, List

from fastapi import WebSocket

from pydantic import BaseModel, Field
from typing import  Any, Literal

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
    id: uuid.UUID
    type: Literal["Request", "Response", "Event"]
    obj: Any

class RequestDTO(BaseModel):
    name: str
    body: Any

class ActionRequestDTO(ActionDTO):
    type: Literal["Request"] = "Request"
    obj: RequestDTO

class ResponseDTO(BaseModel):
    name: str
    status_code: int
    body: Any
    error: None | Any
    permisions: None | Any = None

class ActionResponseDTO(ActionDTO):
    type: Literal["Response"] = "Response"
    obj: ResponseDTO

class EventDTO(BaseModel):
    event_id: uuid.UUID
    name: str
    body: Any

class ActionEventDTO(ActionDTO):
    type: Literal["Event"] = "Event"
    obj: EventDTO

action_dto_map = {
    "Request": ActionRequestDTO.model_validate,
    "Response": ActionResponseDTO.model_validate,
    "Event": ActionEventDTO.model_validate,
}

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