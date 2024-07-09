import datetime
from typing import Callable, TypedDict, List

from fastapi import WebSocket

from pydantic import BaseModel

user_id = int
chat_id = int
message_id = int
count = int
name = str
body = dict
websocket = WebSocket


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
    name: str


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
    text: str | None


class UserDTO(BaseModel):
    id: user_id
    name: str


class ChatUsersDTO(BaseModel):
    user_id: int
    chat_id: int


class ActionsMapTypedDict(TypedDict):
    get_user_info: Callable[[], None] | None
    get_waiting_chats: Callable[[count], List[ChatDTO]] | None
    read_chat_by_user: Callable[[user_id, chat_id], ChatDTO] | None
    get_chats_by_user: Callable[[user_id], List[ChatDTO]] | None
    get_users_by_chat: Callable[[chat_id], List[UserDTO]] | None
    get_messages_by_chat: Callable[[chat_id, count], List[MessageDTO]] | None
    get_messages_by_waiting_chat: Callable[[chat_id, count], List[MessageDTO]] | None
    connect_to_waiting_chat: Callable[[chat_id], ChatDTO] | None
    add_user_to_chat: Callable[[chat_id, user_id], ChatDTO] | None
    send_message_to_chat: Callable[[MessageDTO], None] | None


class UserInfoDTO(BaseModel):
    """
    Экземпляр информации о пользователе (в локальной бд)
    """
    name: str
    user_id: int
